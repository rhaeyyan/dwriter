"""todo list subcommand."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import AppContext

import click

from ._group import todo
from ._helpers import _execute_list


@todo.command("list")
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all tasks, including completed ones",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output data in machine-readable JSON format",
)
@click.pass_obj
def todo_list(ctx: AppContext, show_all: bool, output_json: bool) -> None:
    """List pending tasks."""
    _execute_list(ctx, show_all, output_json)
