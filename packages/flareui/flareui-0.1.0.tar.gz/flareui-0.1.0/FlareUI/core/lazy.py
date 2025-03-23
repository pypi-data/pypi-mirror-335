from typing import Type, Dict, Any
from .component import Component
import importlib

class LazyComponent(Component):
    def __init__(self, module_path: str, component_name: str):
        super().__init__()
        self._module_path = module_path
        self._component_name = component_name
        self._loaded_component = None
    
    def render(self) -> Any:
        if not self._loaded_component:
            module = importlib.import_module(self._module_path)
            component_class = getattr(module, self._component_name)
            self._loaded_component = component_class(self.props)
        return self._loaded_component.render()

def lazy_load(module_path: str, component_name: str) -> Type[Component]:
    return lambda props: LazyComponent(module_path, component_name)(props)
