"""CLI commands for dwriter."""

from .add import add
from .config import config
from .delete import delete
from .edit import edit
from .examples import examples
from .help import help_cmd
from .mcp import mcp
from .review import review
from .search import search
from .standup import standup
from .stats import stats
from .timer import timer
from .today import today
from .todo import done, todo
from .undo import undo

__all__ = [
    "add",
    "config",
    "delete",
    "done",
    "edit",
    "examples",
    "timer",
    "help_cmd",
    "mcp",
    "review",
    "search",
    "standup",
    "stats",
    "today",
    "todo",
    "undo",
]
