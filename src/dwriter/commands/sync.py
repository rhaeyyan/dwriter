"""Sync command for multi-device synchronization."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext

import click
from rich.console import Console

from ..sync.engine import merge_jsonl_to_db, serialize_db


@click.command()
@click.option("--push", is_flag=True, help="Push local changes to remote")
@click.option("--pull", is_flag=True, help="Pull remote changes and merge")
@click.option("--remote", help="Set remote Git URL")
@click.pass_obj
def sync(ctx: AppContext, push: bool, pull: bool, remote: str | None) -> None:
    """Synchronize journal data across devices using Git."""
    console = Console()
    sync_dir = Path.home() / ".dwriter" / "sync"
    sync_dir.mkdir(parents=True, exist_ok=True)

    # Initialize Git repo if not exists
    if not (sync_dir / ".git").exists():
        console.print("[yellow]Initializing sync repository...[/yellow]")
        subprocess.run(["git", "init"], cwd=sync_dir, capture_output=True)
        if remote:
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=sync_dir)

    if remote and (sync_dir / ".git").exists():
        # Update remote if provided
        subprocess.run(["git", "remote", "set-url", "origin", remote], cwd=sync_dir)

    if not push and not pull:
        # Default to both if none specified
        push = pull = True

    if pull:
        console.print("[blue]Pulling remote changes...[/blue]")
        # 1. Fetch
        subprocess.run(["git", "fetch", "origin"], cwd=sync_dir, capture_output=True)
        # 2. Merge (Git level)
        subprocess.run(["git", "merge", "origin/main"], cwd=sync_dir, capture_output=True)
        # 3. Merge into SQLite
        merge_jsonl_to_db(ctx.db, sync_dir)
        console.print("[green]Remote changes merged into local database.[/green]")

    if push:
        console.print("[blue]Pushing local changes...[/blue]")
        # 1. Dump SQLite to JSONL
        serialize_db(ctx.db, sync_dir)
        # 2. Git Commit
        subprocess.run(["git", "add", "."], cwd=sync_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Sync from {os.uname().nodename} at {click.format_filename(str(Path.cwd()))}"],
            cwd=sync_dir,
            capture_output=True
        )
        # 3. Git Push
        result = subprocess.run(["git", "push", "origin", "main"], cwd=sync_dir, capture_output=True)
        if result.returncode == 0:
            console.print("[green]Local changes pushed to remote.[/green]")
        else:
            console.print(f"[red]Push failed: {result.stderr.decode()}[/red]")
