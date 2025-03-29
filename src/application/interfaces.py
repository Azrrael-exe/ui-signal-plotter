from abc import ABC, abstractmethod

from src.domain.entities.component import Component


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
