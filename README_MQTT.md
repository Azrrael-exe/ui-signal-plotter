# MQTT Listener for Signal Plotter

This document explains how to use the MQTT listener component to receive sensor data and control signals for the Signal Plotter application.

## Overview

The MQTT listener allows the application to:
- Subscribe to MQTT topics that publish sensor/component values
- Map topics to specific components in the system
- Automatically add received values to components using the `add_value_to_component_use_case`

## Requirements

- Python 3.8+
- Paho MQTT client: `pip install paho-mqtt`
- An MQTT broker (e.g., Mosquitto, HiveMQ, etc.)

## Basic Usage

### 1. Import the necessary modules

```python
from src.infrastructure.mqtt import MQTTHandler
from src.infrastructure.repositories.memory import MemoryComponentRepository
```

### 2. Create a component repository and components

```python
# Create a repository
repository = MemoryComponentRepository()

# Create a component (for example, a temperature sensor)
temp_sensor = repository.create_component(
    name="Temperature Sensor",
    description="DHT22 temperature sensor",
    type=DeviceType.SENSOR,
    unit=Unit.CELSIUS,
    range=Range(min=-40, max=80, unit=Unit.CELSIUS),
    buffer_size=100,
)
```

### 3. Configure and start the MQTT handler

```python
# Create the MQTT handler
mqtt_handler = MQTTHandler(
    host="localhost",
    port=1883,
    repository=repository,
    client_id="signal-plotter",
)

# Map MQTT topics to component IDs
mqtt_handler.configure_topic_mapping({
    "sensors/temperature": temp_sensor.id,
    "devices/+/temperature": temp_sensor.id,  # Using wildcards
})

# Connect to the MQTT broker and start listening
mqtt_handler.connect()
```

### 4. Publishing data (from external devices)

The MQTT listener accepts data in several formats:

1. Direct values: 
   ```
   mosquitto_pub -t "sensors/temperature" -m "25.5"
   ```

2. JSON objects with a "value" field:
   ```
   mosquitto_pub -t "sensors/temperature" -m '{"value": 25.5}'
   ```

3. JSON arrays of values:
   ```
   mosquitto_pub -t "sensors/temperature" -m '[24.5, 25.0, 25.5]'
   ```

### 5. Stopping the listener

```python
mqtt_handler.disconnect()
```

## Advanced Configuration

### Topic Wildcards

The MQTT handler supports simple wildcards in topic patterns:
- The `+` wildcard matches a single level in the topic hierarchy
- Example: `devices/+/temperature` matches `devices/living_room/temperature` and `devices/kitchen/temperature`

### Authentication

For brokers requiring authentication:

```python
mqtt_handler = MQTTHandler(
    host="localhost",
    port=1883,
    username="your_username",
    password="your_password",
    repository=repository,
)
```

## Example Script

See the full example in `examples/mqtt_listener_example.py`:

```bash
# Run the example
python examples/mqtt_listener_example.py

# In another terminal, publish test messages
mosquitto_pub -t sensors/temperature -m "25.5"
mosquitto_pub -t devices/living_room/temperature -m "22.5"
```

## Integration with Web Applications

When integrating with a web application:

```python
# In your FastAPI/Flask/etc. application startup:
repository = get_repository()  # your repository factory
mqtt_handler = MQTTHandler(repository=repository)
mqtt_handler.configure_topic_mapping({...})
mqtt_handler.connect()

# In your application shutdown:
mqtt_handler.disconnect()
```

## Troubleshooting

- Ensure your MQTT broker is running and accessible
- Check that topic mappings are correctly configured
- Verify that component IDs in the mapping exist in the repository
- Ensure published data is in one of the supported formats
- Check that the values are within the component's acceptable range 