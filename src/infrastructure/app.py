import asyncio
import json
import os
import random
from typing import List

import serial_asyncio
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(
    title="Osciloscopio WebSocket",
    description="Aplicación de osciloscopio con FastAPI y WebSocket",
    version="1.0.0",
)

templates = Jinja2Templates(directory="src/templates")
app.mount("/static", StaticFiles(directory="src/static"), name="static")

active_connections: List[WebSocket] = []


class DataPoint(BaseModel):
    value: float


class TemperatureData(BaseModel):
    temp_oven: float
    temp_ambiente: float


async def broadcast_value(value: float):
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps({"value": value}))
        except:
            # Si hay error al enviar, removemos la conexión
            active_connections.remove(connection)


async def read_serial_data(websocket: WebSocket, port="/dev/ACM0", baudrate=115200):
    """Lee datos del puerto serial y los envía a través de WebSocket."""
    try:
        reader, _ = await serial_asyncio.open_serial_connection(
            url=port, baudrate=baudrate
        )
        while True:
            try:
                data = await reader.readline()
                if data:
                    decoded_data = json.loads(data.decode("utf-8").strip())
                    print(decoded_data)
                    try:
                        value = float(decoded_data["temp_oven"])
                        await broadcast_value(value)
                    except ValueError:
                        await websocket.send_text(json.dumps({"message": decoded_data}))
                        print(f"No se pudo convertir a número: {decoded_data}")
            except Exception as e:
                print(f"Error leyendo puerto serial: {e}")
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Error al conectar al puerto serial: {e}")
        return None


@app.post("/send-value")
async def send_value(data: DataPoint):
    """Endpoint para recibir un valor y enviarlo a todos los clientes WebSocket."""
    await broadcast_value(data.value)
    return {
        "status": "success",
        "message": f"Valor {data.value} enviado a {len(active_connections)} clientes",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Hello World"}


@app.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def generate_random_data(websocket: WebSocket):
    """Genera y envía datos aleatorios cada 5 segundos."""
    while True:
        try:
            value = random.uniform(-5, 5)
            await websocket.send_text(json.dumps({"value": value}))
            await asyncio.sleep(1)
        except:
            break


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    # Uncomment either random_task or serial_task based on what you want to use
    # random_task = asyncio.create_task(generate_random_data(websocket))
    # serial_task = asyncio.create_task(read_serial_data(websocket=websocket))

    try:
        while True:
            data = await websocket.receive_text()
            try:
                value = float(data)
                await broadcast_value(value)
            except ValueError:
                await websocket.send_text(
                    json.dumps({"error": "El valor debe ser numérico"})
                )
    except:
        if websocket in active_connections:
            active_connections.remove(websocket)
        # random_task.cancel()
        # serial_task.cancel()
        await websocket.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, reload=True)
