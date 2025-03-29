from dataclasses import dataclass
from enum import Enum


class Unit(str, Enum):
    CELSIUS = "C"
    RPM = "RPM"
    KW = "KW"


class DeviceType(str, Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
