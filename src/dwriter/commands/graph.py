"""Graph index management commands."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import click
from rich.console import Console

if TYPE_CHECKING:
    from ..cli import AppContext


@click.group()
def graph() -> None:
    """Manage the LadybugDB graph index."""


@graph.command()
@click.option("--full", "-f", is_flag=True, help="Wipe and rebuild from scratch.")
@click.pass_obj
def rebuild(ctx: AppContext, full: bool) -> None:
    """Sync the graph index. Defaults to incremental; use --full to wipe and rebuild."""
    console = Console()
    try:
        from ..graph import GraphProjector
        projector = GraphProjector()
        if full:
            console.print("[blue]Rebuilding graph index (full)...[/blue]")
            projector.build_index(ctx.db)
            ctx.db.set_graph_watermark(datetime.now(timezone.utc).replace(tzinfo=None))
        else:
            console.print("[blue]Syncing graph index...[/blue]")
            projector.build_index_incremental(ctx.db)
        console.print("[green]Graph index synced successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Graph sync failed: {e}[/red]")
        raise SystemExit(1) from e
