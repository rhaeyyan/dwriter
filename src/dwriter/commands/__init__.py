"""CLI commands for Day Writer."""

from .add import add
from .config import config
from .delete import delete
from .edit import edit
from .examples import examples
from .review import review
from .standup import standup
from .stats import stats
from .today import today
from .undo import undo

__all__ = [
    "add",
    "config",
    "delete",
    "edit",
    "examples",
    "review",
    "stats",
    "standup",
    "today",
    "undo",
]
