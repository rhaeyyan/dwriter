"""dwriter - A low-friction terminal journaling tool.

This package provides a command-line interface for tracking daily tasks
and generating standup summaries.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("dwriter")
except PackageNotFoundError:
    __version__ = "unknown"

__author__ = "dwriter Contributors"
