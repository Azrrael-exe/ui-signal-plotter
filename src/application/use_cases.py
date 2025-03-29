from src.domain.entities.component import Value
from src.domain.exceptions import UnitMismatchError
from src.domain.value_objects import Unit

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


def add_value_use_case(
    component_id: str, values: list[int], repository: ComponentRepository
):
    component = repository.get_component_by_id(id=component_id)
    add_values_service(
        component=component,
        values=[Value(value=v, unit=component.unit) for v in values],
    )
    return None
