from copy import deepcopy

from src.application.interfaces import Component, ComponentRepository


class MemoryComponentRepository(ComponentRepository):
    def __init__(self):
        self.components = {}

    def get_component_by_id(self, id: str) -> Component:
        return deepcopy(self.components[id])

    def get_component_by_name(self, name: str) -> Component:
        return next(
            (
                component
                for component in self.components.values()
                if component.name == name
            ),
            None,
        )

    def get_components(self) -> list[Component]:
        return deepcopy(self.components)

    def _get_index(self) -> int:
        return len(self.components.keys())

    def _save(self, component: Component):
        self.components[component.id] = component

    def delete_component(self, id: str) -> Component:
        return self.components.pop(id)
