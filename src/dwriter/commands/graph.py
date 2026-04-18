"""Graph index management commands."""

from __future__ import annotations

from typing import TYPE_CHECKING

import click
from rich.console import Console

if TYPE_CHECKING:
    from ..cli import AppContext


@click.group()
def graph() -> None:
    """Manage the LadybugDB graph index."""


@graph.command()
@click.pass_obj
def rebuild(ctx: AppContext) -> None:
    """Rebuild the graph index from SQLite (clears and reprojects all data)."""
    console = Console()
    console.print("[blue]Rebuilding graph index...[/blue]")
    try:
        from ..graph import GraphProjector
        projector = GraphProjector()
        projector.build_index(ctx.db)
        console.print("[green]Graph index rebuilt successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Rebuild failed: {e}[/red]")
        raise SystemExit(1) from e
