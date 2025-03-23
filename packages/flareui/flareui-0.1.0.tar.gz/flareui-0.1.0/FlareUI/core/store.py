from typing import Any, Callable, Dict, List

class Store:
    def __init__(self, initial_state: Dict[str, Any] = None):
        self._state = initial_state or {}
        self._middlewares: List[Callable] = []
        self._subscribers: List[Callable] = []
    
    def get_state(self) -> Dict[str, Any]:
        return self._state.copy()
    
    def set_state(self, action: str, update: Dict[str, Any]) -> None:
        prev_state = self.get_state()
        self._state.update(update)
        
        for middleware in self._middlewares:
            middleware(action, prev_state, self.get_state())
            
        self._notify_subscribers()
    
    def apply_middleware(self, middleware: Callable) -> None:
        self._middlewares.append(middleware)
    
    def subscribe(self, callback: Callable) -> Callable:
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback)
    
    def _notify_subscribers(self) -> None:
        for subscriber in self._subscribers:
            subscriber(self.get_state())
