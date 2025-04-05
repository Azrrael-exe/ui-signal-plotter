from src.domain.entities.component import Component, Value
from src.domain.entities.processors import forecast_next_value
from src.domain.value_objects import DeviceStatus


def add_values_service(component: Component, values: list[Value]) -> int:
    updates = 0
    for value in values:
        try:
            component.add_value(value)
            updates += 1
        except ValueError:
            print(f"Invalid value: {value}")
    return updates


def forecast_value_service(component: Component) -> Value:
    return forecast_next_value(component.get_values())


def get_component_status_service(component: Component) -> DeviceStatus:
    return component.get_status()
