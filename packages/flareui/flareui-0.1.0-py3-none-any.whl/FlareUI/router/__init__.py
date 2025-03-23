from typing import Dict, Callable, Optional, Any
from importlib import import_module
from pathlib import Path
from ..core.component import Component

class Router:
    def __init__(self):
        self._routes: Dict[str, Component] = {}
        self._current_path: str = "/"
        self._subscribers: List[Callable] = []
        self._route_params: Dict[str, Any] = {}
        self._parent_routes: Dict[str, str] = {}
        self._guards: List[Callable[[str], bool]] = []
        self._middlewares: List[Callable[[str, Dict], None]] = []
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._error_handlers: Dict[str, Callable[[Exception], None]] = {}

    def add_route(self, path: str, component: Component) -> None:
        self._routes[path] = component

    def add_nested_route(self, parent_path: str, path: str, component: Component) -> None:
        """Add a nested route under a parent route"""
        full_path = f"{parent_path}/{path}"
        self._routes[full_path] = component
        self._parent_routes[path] = parent_path

    def add_guard(self, guard: Callable[[str], bool]) -> None:
        """Add a route guard that must return True to allow navigation"""
        self._guards.append(guard)

    def add_middleware(self, middleware: Callable[[str, Dict], None]) -> None:
        """Add middleware to be executed before navigation"""
        self._middlewares.append(middleware)

    def set_metadata(self, path: str, metadata: Dict[str, Any]) -> None:
        """Set metadata for a route"""
        self._metadata[path] = metadata

    def add_error_handler(self, error_type: str, handler: Callable[[Exception], None]) -> None:
        """Add handler for specific route errors"""
        self._error_handlers[error_type] = handler

    def navigate(self, module_name: str, params: Dict[str, Any] = None) -> None:
        try:
            # Check guards
            if not all(guard(module_name) for guard in self._guards):
                raise PermissionError("Navigation blocked by guard")

            # Execute middlewares
            for middleware in self._middlewares:
                middleware(module_name, params or {})

            if params:
                self._route_params = params
            
            # Handle nested routes
            parts = module_name.split('/')
            for i in range(len(parts)):
                partial_path = '/'.join(parts[:i+1])
                if (partial_path not in self._routes):
                    self._load_module(partial_path)
            
            self._current_path = module_name
            self._notify_subscribers()
        except Exception as e:
            error_type = type(e).__name__
            if error_type in self._error_handlers:
                self._error_handlers[error_type](e)
            else:
                raise e
    
    def _load_module(self, module_path: str) -> None:
        """Load a module and its component"""
        try:
            module = import_module(f"pages.{module_path}")
            component_name = module_path.split('/')[-1].capitalize()
            component_class = getattr(module, component_name)
            component = component_class({"route_params": self._route_params})
            self.add_route(module_path, component)
        except Exception as e:
            print(f"Error loading module {module_path}: {e}")

    def current_component(self) -> Optional[Component]:
        return self._routes.get(self._current_path)

    def get_params(self) -> Dict[str, Any]:
        """Get current route parameters"""
        return self._route_params.copy()

    def _notify_subscribers(self) -> None:
        for subscriber in self._subscribers:
            subscriber(self._current_path)
