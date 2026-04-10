"""Background sync daemon for dwriter."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Database

from .engine import merge_jsonl_to_db, serialize_db


def _log_sync(message: str) -> None:
    """Log a message to the sync log file."""
    log_dir = Path.home() / ".dwriter" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "sync.log"
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")


def pull_sync(db: Database) -> bool:
    """Perform a non-blocking background pull sync.

    Returns:
        bool: True if remote changes were merged, False otherwise.
    """
    sync_dir = Path.home() / ".dwriter" / "sync"
    if not (sync_dir / ".git").exists():
        return False

    try:
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=sync_dir,
            capture_output=True,
            check=True,
        )

        status = subprocess.check_output(
            ["git", "status", "-uno"], cwd=sync_dir, text=True
        )

        if "Your branch is behind" in status:
            _log_sync("Remote changes detected, pulling...")
            subprocess.run(
                ["git", "merge", "origin/main"],
                cwd=sync_dir,
                capture_output=True,
                check=True,
            )
            merge_jsonl_to_db(db, sync_dir)
            _log_sync("Sync pull successful.")
            return True

        return False

    except subprocess.CalledProcessError as e:
        _log_sync(f"Sync pull failed: {e.stderr.decode()}")
        return False
    except Exception as e:
        _log_sync(f"Sync pull error: {str(e)}")
        return False


def push_sync(db: Database) -> bool:
    """Perform a background push sync.

    Returns:
        bool: True if push succeeded, False otherwise.
    """
    sync_dir = Path.home() / ".dwriter" / "sync"
    if not (sync_dir / ".git").exists():
        return False

    try:
        _log_sync("Starting background push...")
        serialize_db(db, sync_dir)

        subprocess.run(["git", "add", "."], cwd=sync_dir, check=True, capture_output=True)

        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=sync_dir
        )

        if diff.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", f"Auto-sync from {os.uname().nodename}"],
                cwd=sync_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=sync_dir,
                check=True,
                capture_output=True,
            )
            _log_sync("Auto-sync push successful.")
            return True

        _log_sync("No changes to push.")
        return False

    except subprocess.CalledProcessError as e:
        _log_sync(f"Auto-sync push failed: {e.stderr.decode()}")
        return False
    except Exception as e:
        _log_sync(f"Auto-sync push error: {str(e)}")
        return False
