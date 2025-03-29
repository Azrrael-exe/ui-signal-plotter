from src.application.interfaces import Component, ComponentRepository


class MemoryComponentRepository(ComponentRepository):
    def __init__(self):
        self.components = []

    def add_component(self, component: Component):
        self.components.append(component)

    def get_component_by_id(self, id: str) -> Component:
        return next(
            (component for component in self.components if component.id == id), None
        )

    def get_component_by_name(self, name: str) -> Component:
        return next(
            (component for component in self.components if component.name == name), None
        )

    def get_components(self) -> list[Component]:
        return self.components
