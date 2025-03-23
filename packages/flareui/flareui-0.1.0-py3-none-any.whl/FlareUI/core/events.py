from typing import Callable, Dict, Any

class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def add_listener(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def remove_listener(self, event_type: str, callback: Callable) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].remove(callback)

    def dispatch(self, event_type: str, event_data: Any = None) -> None:
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                callback(event_data)
