"""todo rm subcommand."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ._group import todo
from ._helpers import _execute_rm


@todo.command("rm")
@click.argument("task_id", type=int)
@click.pass_obj
def todo_rm(ctx: AppContext, task_id: int) -> None:
    """Delete a task entirely."""
    _execute_rm(ctx, task_id)
