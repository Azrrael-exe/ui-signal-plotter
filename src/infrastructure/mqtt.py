import json
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt
from paho.mqtt.client import Client, MQTTMessage

from src.application.interfaces import ComponentRepository
from src.application.use_cases import add_value_to_component_use_case


class MQTTHandler:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        repository: Optional[ComponentRepository] = None,
        client_id: str = "signal-plotter",
        topic_component_map: Dict[str, Callable] = {},
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.repository = repository
        self.client_id = client_id
        self.client = None
        self.topic_component_map = topic_component_map

    def _on_connect(self, client: Client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to all configured topics
        for topic in self.topic_component_map.keys():
            client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")

    def _on_message(self, client: Client, userdata, msg: MQTTMessage):
        """Handle incoming MQTT messages."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            print(f"Received message on topic {topic}: {payload}")

            if topic not in self.topic_component_map:
                print(f"No component mapping found for topic: {topic}")
                return

            self.topic_component_map[topic](**payload)

        except json.JSONDecodeError:
            print(f"Invalid JSON payload: {msg.payload}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def connect(self):
        """Connect to the MQTT broker and start listening for messages."""
        if not self.repository:
            print("Warning: Repository not configured")

        self.client = mqtt.Client(client_id=self.client_id)

        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        try:
            self.client.connect(self.host, self.port, 60)
            for topic in self.topic_component_map.keys():
                print(f"Subscribed to topic: {topic}")
            # Start the network loop
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("Disconnected from MQTT broker")


def get_mqtt_handler(
    repository: ComponentRepository,
) -> MQTTHandler:
    topic_component_map = {
        "maxwell/add_value": lambda **payload: add_value_to_component_use_case(
            component_id=payload["component_id"],
            values=payload["values"],
            repository=repository,
        )
    }
    return MQTTHandler(
        host="broker.hivemq.com",
        port=1883,
        repository=repository,
        topic_component_map=topic_component_map,
    )
