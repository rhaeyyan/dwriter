"""todo edit subcommand."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ._group import todo
from ._helpers import _execute_edit


@todo.command("edit")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_edit(ctx: AppContext, task_id: int) -> None:
    """Edit a task's content interactively."""
    _execute_edit(ctx, task_id)
