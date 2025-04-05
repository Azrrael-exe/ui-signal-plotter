from abc import ABC, abstractmethod

from src.domain.entities.component import Component, Range
from src.domain.value_objects import DeviceType, Unit


class ComponentRepository(ABC):
    @abstractmethod
    def get_component_by_id(self, id: str) -> Component:
        pass

    @abstractmethod
    def get_component_by_name(self, name: str) -> Component:
        pass

    @abstractmethod
    def get_components(self) -> list[Component]:
        pass

    @abstractmethod
    def _get_index(self) -> int:
        pass

    @abstractmethod
    def _save(self, component: Component) -> None:
        pass

    def update_component(self, component: Component):
        if self.get_component_by_id(component.id):
            self._save(component)
        else:
            raise KeyError("Component not found")

    def create_component(
        self,
        name: str,
        description: str,
        type: DeviceType,
        unit: Unit,
        range: Range,
        buffer_size: int = 100,
        time_before_disconnect: int = 1000 * 60 * 5,
    ) -> Component:
        component = Component(
            id=self._get_index(),
            name=name,
            description=description,
            type=type,
            unit=unit,
            range=range,
            buffer_size=buffer_size,
            time_before_disconnect=time_before_disconnect,
        )
        self._save(component)
        return component

    @abstractmethod
    def delete_component(self, id: str) -> Component:
        pass
