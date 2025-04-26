import uvicorn

from src.infrastructure.api import get_app
from src.infrastructure.mqtt import get_mqtt_handler
from src.infrastructure.repositories.memory import MemoryComponentRepository

# Create a repository
repository = MemoryComponentRepository()

# Create the FastAPI application with the repository
app = get_app(repository)

# Initialize and start the MQTT handler
mqtt_handler = get_mqtt_handler(repository)
mqtt_handler.connect()


# Register shutdown event to properly disconnect MQTT handler
@app.on_event("shutdown")
async def shutdown_event():
    mqtt_handler.disconnect()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
