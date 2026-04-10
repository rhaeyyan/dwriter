"""Git utilities for workspace awareness."""

import subprocess
from pathlib import Path
from typing import TypedDict


class GitInfo(TypedDict):
    """Git repository information."""
    repo_name: str
    branch: str
    toplevel: str


def get_git_info() -> GitInfo | None:
    """Retrieves information about the current git repository.

    Returns:
        GitInfo: A dictionary with repo_name, branch, and toplevel path,
                 or None if not in a git repository.
    """
    try:
        toplevel = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        repo_name = Path(toplevel).name

        # Respect .dwriter-ignore at the repository root
        ignore_file = Path(toplevel) / ".dwriter-ignore"
        if ignore_file.exists():
            try:
                with open(ignore_file) as f:
                    if "disable_auto_tag=true" in f.read():
                        return None
            except Exception:
                pass

        return {"repo_name": repo_name, "branch": branch, "toplevel": toplevel}

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
