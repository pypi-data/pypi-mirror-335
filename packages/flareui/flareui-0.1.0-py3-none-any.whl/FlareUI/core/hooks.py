from typing import Any, Callable, List, Optional, Tuple
from .state import State

_current_component = None
_hooks_index = 0

def use_state(initial_value: Any) -> Tuple[Any, Callable[[Any], None]]:
    global _hooks_index
    state = State(initial_value)
    
    def set_state(new_value: Any) -> None:
        state.set(new_value)
        if _current_component:
            _current_component._update()
    
    _hooks_index += 1
    return state.get(), set_state

def use_effect(effect: Callable[[], Optional[Callable]], dependencies: List[Any] = None) -> None:
    global _hooks_index
    
    if _current_component:
        old_cleanup = _current_component._effects.get(_hooks_index, lambda: None)
        old_cleanup()
        
        def cleanup_wrapper():
            cleanup = effect()
            if cleanup and callable(cleanup):
                _current_component._effects[_hooks_index] = cleanup
        
        cleanup_wrapper()
    
    _hooks_index += 1

def use_memo(compute: Callable[[], T], dependencies: List[Any] = None) -> T:
    global _hooks_index
    hook_state = _get_hook_state(_hooks_index)
    
    if not hook_state or _dependencies_changed(hook_state.get('deps'), dependencies):
        value = compute()
        hook_state = {'value': value, 'deps': dependencies}
        _set_hook_state(_hooks_index, hook_state)
    
    _hooks_index += 1
    return hook_state['value']

def use_model(initial_value: Any) -> Tuple[Any, Callable[[Any], None]]:
    value, set_value = use_state(initial_value)
    
    def bind_input(event):
        set_value(event.target.value)
    
    return value, bind_input

def use_store(selector: Callable[[Dict], Any] = None) -> Any:
    store = get_global_store()
    state = store.get_state()
    if selector:
        return selector(state)
    return state

def _dependencies_changed(old_deps: List[Any], new_deps: List[Any]) -> bool:
    if old_deps is None or new_deps is None:
        return True
    return len(old_deps) != len(new_deps) or any(
        old != new for old, new in zip(old_deps, new_deps)
    )
