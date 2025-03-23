from typing import Any, Callable, Dict, TypeVar, Generic

T = TypeVar('T')

class State(Generic[T]):
    def __init__(self, initial_value: T):
        self._value = initial_value
        self._subscribers: List[Callable[[T], None]] = []

    def get(self) -> T:
        return self._value

    def set(self, new_value: T) -> None:
        if new_value != self._value:
            self._value = new_value
            self._notify()

    def subscribe(self, callback: Callable[[T], None]) -> Callable[[], None]:
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback)

    def _notify(self) -> None:
        for callback in self._subscribers:
            callback(self._value)
