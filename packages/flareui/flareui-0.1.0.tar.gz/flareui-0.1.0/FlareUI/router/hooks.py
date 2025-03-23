from typing import Tuple, Callable
from . import Router

_router_instance = None

def get_router() -> Router:
    global _router_instance
    if not _router_instance:
        _router_instance = Router()
    return _router_instance

def use_route() -> Tuple[str, Callable[[str], None]]:
    router = get_router()
    return router._current_path, router.navigate
