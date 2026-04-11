"""Todo command subpackage."""

from ._group import todo

# Import submodules to trigger @todo.command() registration
from . import add, edit, list, rm  # noqa: F401

from .done import done
from .remind import remind
from .snooze import snooze

__all__ = ["done", "remind", "snooze", "todo"]
