from typing import Dict, Any, Optional, List, Callable
from .dom import VirtualNode
from .template import TemplateParser

class Component:
    """Base component class for FlareUI."""
    
    def __init__(self):
        self.children = []
        
    def __init__(self, props: Dict[str, Any] = None):
        self.props = props or {}
        self._state = {}
        self._effects = []
        self._mounted = False
        self.component_did_mount()
        
    def set_state(self, new_state: Dict[str, Any]) -> None:
        self._state.update(new_state)
        self._update()
        
    @staticmethod
    def h(tag: str, props: Dict[str, Any] = None, *children: List[Any]) -> VirtualNode:
        return TemplateParser.h(tag, props, *children)

    @staticmethod
    def if_render(condition: bool, true_component: Component, false_component: Component = None) -> VirtualNode:
        return true_component.render() if condition else (false_component.render() if false_component else None)
    
    @staticmethod
    def for_render(items: List[Any], render_fn: Callable[[Any], Component]) -> List[VirtualNode]:
        return [render_fn(item).render() for item in items]
    
    def template(self) -> str:
        """Override this method to use template syntax"""
        return None
        
    def render(self) -> VirtualNode:
        if hasattr(self, 'template_file') and self.template_file.endswith('.pya'):
            return self.load_pya(self.template_file)
        elif template := self.template():
            return TemplateParser.parse(template)
        raise NotImplementedError("Must implement render() or provide a template")
        
    def load_pya(self, file_path: str) -> VirtualNode:
        """Load and parse a PYA template file"""
        with open(file_path, 'r') as f:
            content = f.read()
        return TemplateParser.parse_pya(content)

    def _update(self) -> None:
        try:
            if self._mounted and self.should_component_update(self.props):
                derived_state = self.get_derived_state_from_props(self.props)
                self._state.update(derived_state)
                new_vdom = self.render()
                self._renderer.render(new_vdom)
        except Exception as e:
            if not self.catch_error(e):
                raise e
            
    def component_did_mount(self) -> None:
        """Called after component is mounted"""
        pass
    
    def component_will_unmount(self) -> None:
        """Called before component is unmounted"""
        pass
    
    def should_component_update(self, next_props: Dict[str, Any]) -> bool:
        """Controls if component should re-render"""
        return True
    
    def catch_error(self, error: Exception) -> bool:
        """Error boundary implementation"""
        return False
    
    def get_derived_state_from_props(self, next_props: Dict[str, Any]) -> Dict[str, Any]:
        """Called before render with new props"""
        return {}

    def navigate_to(self, target_module: str) -> None:
        """Handle navigation through target module"""
        from .router import get_router
        router = get_router()
        router.navigate(target_module)
