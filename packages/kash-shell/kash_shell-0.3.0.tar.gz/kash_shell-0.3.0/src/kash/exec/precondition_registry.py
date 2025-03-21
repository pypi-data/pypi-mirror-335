from collections.abc import Callable
from threading import Lock

from kash.config.logger import get_logger
from kash.model.items_model import Item
from kash.model.preconditions_model import Precondition

log = get_logger(__name__)

# Global registry of preconditions.
_preconditions: dict[str, Precondition] = {}
_lock = Lock()


def kash_precondition(func: Callable[[Item], bool]) -> Precondition:
    """
    Decorator to register a function as a Precondition.
    The function should return a bool and/or raise `PreconditionFailure`.

    Example:
        @register_precondition
        def is_file(item: Item) -> bool:
            return item.is_file()
    """
    precondition = Precondition(func)

    with _lock:
        if precondition.name in _preconditions:
            log.warning(
                "Duplicate precondition name (defined twice by accident?): %s",
                precondition.name,
            )
        _preconditions[precondition.name] = precondition

    return precondition


def get_all_preconditions() -> dict[str, Precondition]:
    """
    Returns a copy of all registered preconditions.
    """
    # Return a copy for safety.
    return dict(_preconditions)
