from typing import Any, Dict, Optional, TypeVar
from .state import State

T = TypeVar('T')

class Context(Generic[T]):
    def __init__(self, initial_value: T):
        self._state = State(initial_value)
        self._consumers: Set[Component] = set()

    def provide(self, value: T) -> None:
        self._state.set(value)

    def consume(self) -> T:
        if _current_component:
            self._consumers.add(_current_component)
        return self._state.get()

    def _notify_consumers(self) -> None:
        for consumer in self._consumers:
            consumer._update()
