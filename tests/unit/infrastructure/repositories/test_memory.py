import pytest

from src.domain.entities.component import Component, Range, Value
from src.domain.value_objects import Unit
from src.infrastructure.repositories.memory import MemoryComponentRepository


@pytest.fixture
def dummy_component():
    return {
        "name": "LM35",
        "description": "Sensor de temperatura basado en el integrado LM35",
        "type": "sensor",
        "unit": Unit.CELSIUS,
        "range": Range(min=-276, max=150, unit=Unit.CELSIUS),
        "buffer_size": 100,
        "time_before_disconnect": 1000 * 60 * 5,
    }


def dummy_repository_with_component(dummy_component):
    repository = MemoryComponentRepository()
    repository.create_component(**dummy_component())
    return repository


def test_create_component(dummy_component):
    repository = MemoryComponentRepository()

    n_components = 10
    for _ in range(n_components):
        repository.create_component(**dummy_component)

    assert len(repository.get_components()) == n_components
    assert repository.get_component_by_id(0).id == 0
    assert repository.get_component_by_id(0).name == dummy_component["name"]
    assert (
        repository.get_component_by_id(0).description == dummy_component["description"]
    )
    assert repository.get_component_by_id(0).type == dummy_component["type"]
    assert repository.get_component_by_id(0).unit == dummy_component["unit"]
    assert repository.get_component_by_id(0).range == dummy_component["range"]

    assert repository.get_component_by_id(
        n_components - 1
    ) != repository.get_component_by_id(n_components - 2)

    repository.create_component(
        name="DifferentComponent",
        description="Sensor de temperatura basado en el integrado LM35",
        type="sensor",
        unit=Unit.CELSIUS,
        range=Range(min=-276, max=150, unit=Unit.CELSIUS),
    )

    assert repository.get_component_by_name("DifferentComponent").id == n_components

    impostor_component = Component(
        id=n_components + 2,
        name="DifferentComponent",
        description="Sensor de temperatura basado en el integrado LM35",
        type="sensor",
        unit=Unit.CELSIUS,
        range=Range(min=-276, max=150, unit=Unit.CELSIUS),
        buffer_size=100,
        time_before_disconnect=1000 * 60 * 5,
    )

    with pytest.raises(KeyError):
        repository.update_component(impostor_component)

    assert repository.get_component_by_id(0) != repository.components[0]

    component_to_update = repository.get_component_by_id(0)
    component_to_update.add_value(Value(value=10, unit=Unit.CELSIUS))
    repository.update_component(component_to_update)
