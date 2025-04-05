from abc import ABC

import pytest

from src.application.interfaces import ComponentRepository
from src.domain.entities.component import Component, Range
from src.domain.value_objects import DeviceType, Unit


def test_component_repository_cannot_be_instantiated_directly():
    """Verifica que no se puede instanciar directamente ComponentRepository por ser abstracta"""
    with pytest.raises(TypeError):
        ComponentRepository()


def test_component_repository_abstract_methods_must_be_implemented():
    """Verifica que se lanza error si los métodos abstractos no están implementados"""

    class IncompleteRepository(ComponentRepository):
        # No implementa ningún método abstracto
        pass

    with pytest.raises(TypeError):
        IncompleteRepository()


def test_component_repository_partial_implementation():
    """Verifica que se lanza error si solo algunos métodos abstractos son implementados"""

    class PartialRepository(ComponentRepository):
        def get_component_by_id(self, id: str) -> Component:
            pass

        # Faltan otros métodos abstractos

    with pytest.raises(TypeError):
        PartialRepository()


def test_component_repository_update_component_nonexistent():
    """Verifica que update_component lanza KeyError si el componente no existe"""

    class ValidRepository(ComponentRepository):
        def get_component_by_id(self, id: str) -> Component:
            return None  # Simulamos que no existe

        def get_component_by_name(self, name: str) -> Component:
            pass

        def get_components(self) -> list[Component]:
            pass

        def _get_index(self) -> int:
            pass

        def _save(self, component: Component) -> None:
            pass

    repo = ValidRepository()
    dummy_component = Component(
        id=1,
        name="test",
        description="test component",
        type=DeviceType.SENSOR,
        unit=Unit.CELSIUS,
        range=Range(min=0, max=100, unit=Unit.CELSIUS),
    )

    with pytest.raises(KeyError):
        repo.update_component(dummy_component)


def test_component_repository_update_component_success():
    """Verifica que update_component funciona correctamente cuando el componente existe"""

    class ValidRepository(ComponentRepository):
        def __init__(self):
            self.save_called = False

        def get_component_by_id(self, id: str) -> Component:
            # Simulamos que el componente existe
            return Component(
                id=1,
                name="test",
                description="test component",
                type=DeviceType.SENSOR,
                unit=Unit.CELSIUS,
                range=Range(min=0, max=100, unit=Unit.CELSIUS),
            )

        def get_component_by_name(self, name: str) -> Component:
            pass

        def get_components(self) -> list[Component]:
            pass

        def _get_index(self) -> int:
            pass

        def _save(self, component: Component) -> None:
            self.save_called = True

    repo = ValidRepository()
    dummy_component = Component(
        id=1,
        name="test",
        description="test component",
        type=DeviceType.SENSOR,
        unit=Unit.CELSIUS,
        range=Range(min=0, max=100, unit=Unit.CELSIUS),
    )

    repo.update_component(dummy_component)
    assert repo.save_called, "_save method should have been called"


def test_component_repository_create_component():
    """Verifica que create_component crea y guarda un componente correctamente"""

    class ValidRepository(ComponentRepository):
        def __init__(self):
            self.saved_component = None

        def get_component_by_id(self, id: str) -> Component:
            pass

        def get_component_by_name(self, name: str) -> Component:
            pass

        def get_components(self) -> list[Component]:
            pass

        def _get_index(self) -> int:
            return 1

        def _save(self, component: Component) -> None:
            self.saved_component = component

    repo = ValidRepository()
    component = repo.create_component(
        name="test",
        description="test component",
        type=DeviceType.SENSOR,
        unit=Unit.CELSIUS,
        range=Range(min=0, max=100, unit=Unit.CELSIUS),
        buffer_size=200,
        time_before_disconnect=10000,
    )

    assert component.id == 1
    assert component.name == "test"
    assert component.description == "test component"
    assert component.type == DeviceType.SENSOR
    assert component.unit == Unit.CELSIUS
    assert component.range.min == 0
    assert component.range.max == 100
    assert repo.saved_component is not None, "Component should be saved"
    assert repo.saved_component.id == component.id
