from collections.abc import Callable
from threading import Lock
from typing import overload

from kash.config.logger import get_logger
from kash.errors import InvalidInput
from kash.exec_model.shell_model import ShellResult

log = get_logger(__name__)


CommandFunction = Callable[..., ShellResult] | Callable[..., None]
"""
A function that can be registered as a kash command. It can take any number
of args. It can return a `ShellResult` (for reporting exceptions or customizing
shell output) or return nothing (if it throws exceptions on errors).
"""

# Global registry of commands.
_commands: dict[str, CommandFunction] = {}
_lock = Lock()
_has_logged = False


@overload
def kash_command(func: Callable[..., ShellResult]) -> Callable[..., ShellResult]: ...


@overload
def kash_command(func: Callable[..., None]) -> Callable[..., None]: ...


def kash_command(func: CommandFunction) -> CommandFunction:
    """
    Decorator to register a command.
    """
    with _lock:
        if func.__name__ in _commands:
            log.error("Command `%s` already registered; duplicate definition?", func.__name__)
        _commands[func.__name__] = func
    return func


def register_all_commands() -> None:
    """
    Ensure all commands are registered and imported.
    """
    with _lock:
        import kash.commands  # noqa: F401

        global _has_logged
        if not _has_logged:
            log.info("Command registry: %d commands registered.", len(_commands))
            _has_logged = True


def get_all_commands() -> dict[str, CommandFunction]:
    """
    All commands, sorted by name.
    """
    register_all_commands()
    return dict(sorted(_commands.items()))


def look_up_command(name: str) -> CommandFunction:
    """
    Look up a command by name.
    """
    cmd = _commands.get(name)
    if not cmd:
        raise InvalidInput(f"Command `{name}` not found")
    return cmd
