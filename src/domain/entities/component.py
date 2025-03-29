import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

from ..exceptions import UnitMismatchError
from ..value_objects import DeviceStatus, DeviceType, Unit


@dataclass
class Value:
    value: int
    unit: Unit
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))


@dataclass
class Range:
    min: int
    max: int
    unit: Unit


class Component:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        type: DeviceType,
        config_rules: list[Callable],
        unit: Unit,
        range: Range,
        buffer_size: int = 100,
        time_before_disconnect: int = 1000 * 60 * 5,
    ):
        self.__id = id
        self.__name = name
        self.__unit = unit
        self.set_ranges(range)
        self.__range = range
        self.__description = description
        self.__type = type
        self.__values = deque(maxlen=buffer_size)
        self.__time_before_disconnect = time_before_disconnect

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description

    @property
    def unit(self) -> Unit:
        return self.__unit

    @property
    def range(self) -> Range:
        return self.__range

    @property
    def type(self) -> DeviceType:
        return self.__type

    def set_ranges(self, range: Range):
        if range.unit != self.__unit:
            raise UnitMismatchError()
        self.__range = range

    def add_value(self, value: Value):
        if value.unit != self.__unit:
            raise UnitMismatchError()
        if value.value < self.__range.min or value.value > self.__range.max:
            raise ValueError("Value must be in the range")
        self.__values.append(value)

    def get_last_value(self) -> Value:
        if len(self.__values) == 0:
            raise ValueError("No values")
        return self.__values[-1]

    def get_values(self) -> list[Value]:
        return list(self.__values)

    def get_average(self) -> float:
        return sum(self.__values) / len(self.__values)

    def get_min(self) -> float:
        return min(self.__values)

    def get_max(self) -> float:
        return max(self.__values)

    def get_status(self) -> DeviceStatus:
        if len(self.get_values()) == 0:
            self.__status = DeviceStatus.OFFLINE
        elif (
            self.get_last_value().timestamp
            < time.time() * 1000 - self.__time_before_disconnect
        ):
            self.__status = DeviceStatus.OFFLINE
        else:
            self.__status = DeviceStatus.ONLINE
        return self.__status
