"""CLI commands for dwriter."""

from .add import add
from .ask import ask
from .compress import compress
from .config import config
from .delete import delete
from .edit import edit
from .examples import examples
from .help import help_cmd
from .notifications import install_notifications, uninstall_notifications
from .review import review
from .search import search
from .standup import standup
from .stats import stats
from .sync import sync
from .timer import timer
from .today import today
from .todo import done, remind, snooze, todo
from .undo import undo

__all__ = [
    "add",
    "ask",
    "compress",
    "config",
    "delete",
    "done",
    "edit",
    "examples",
    "help_cmd",
    "install_notifications",
    "review",
    "remind",
    "search",
    "snooze",
    "standup",
    "stats",
    "sync",
    "timer",
    "today",
    "todo",
    "undo",
    "uninstall_notifications",
]
