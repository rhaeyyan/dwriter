"""Todo command subpackage."""

# Import submodules to trigger @todo.command() registration
from . import add, edit, list, rm  # noqa: F401
from ._group import todo
from .done import done
from .remind import remind
from .snooze import snooze

__all__ = ["done", "remind", "snooze", "todo"]
