from pydantic import BaseModel, field_validator

from src.domain.entities.component import Component, Range, Value
from src.domain.exceptions import UnitMismatchError
from src.domain.value_objects import DeviceType, Unit

from .interfaces import ComponentRepository
from .services import add_values_service, forecast_value_service


def fan_controller(value: Value) -> Value:
    if value.unit != Unit.CELSIUS:
        raise UnitMismatchError(value.unit)
    return Value(value=value.value * 0.5, unit=Unit.RPM)


def control_component_use_case(
    source_componet_id: str,
    target_componet_id: str,
    repository: ComponentRepository,
) -> Value:
    source_component = repository.get_component_by_id(id=source_componet_id)
    target_component = repository.get_component_by_id(id=target_componet_id)

    actual_value = forecast_value_service(component=source_component)

    output_value = fan_controller(value=actual_value)

    add_values_service(component=target_component, values=[output_value])
    return output_value


class RangeDTO(BaseModel):
    min: float
    max: float
    unit: str

    def get_range(self) -> Range:
        return Range(
            min=self.min, max=self.max, unit=Unit.get_unit_from_string(self.unit)
        )


class ComponentDTO(BaseModel):
    name: str
    description: str
    type: str
    unit: str
    range: RangeDTO
    buffer_size: int = 100
    time_before_disconnect: int = 10

    @field_validator("unit")
    def validate_unit(cls, v):
        return Unit.get_unit_from_string(v)


def create_component_use_case(
    component: ComponentDTO, repository: ComponentRepository
) -> Component:
    return repository.create_component(
        name=component.name,
        description=component.description,
        type=DeviceType(component.type),
        unit=Unit(component.unit),
        range=component.range.get_range(),
        buffer_size=component.buffer_size,
        time_before_disconnect=component.time_before_disconnect,
    )


def add_value_to_component_use_case(
    component_id: int, values: list[int], repository: ComponentRepository
) -> int:
    component = repository.get_component_by_id(id=component_id)

    updates = add_values_service(
        component=component,
        values=[Value(value=v, unit=component.unit) for v in values],
    )

    repository.update_component(component=component)

    return updates


def get_component_values_use_case(
    component_id: str,
    repository: ComponentRepository,
) -> list[Value]:
    component = repository.get_component_by_id(id=component_id)
    return [value.dump() for value in component.get_values()]


def delete_component_use_case(
    component_id: str, repository: ComponentRepository
) -> Component:
    return repository.delete_component(id=component_id)
