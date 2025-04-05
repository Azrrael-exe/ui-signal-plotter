from dataclasses import dataclass
from enum import Enum


class Unit(str, Enum):
    CELSIUS = "C"
    RPM = "RPM"
    KW = "KW"

    @staticmethod
    def get_unit_from_string(value: str) -> "Unit":
        try:
            return Unit(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid Unit value")


class DeviceType(str, Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
