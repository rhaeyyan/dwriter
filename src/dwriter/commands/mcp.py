"""MCP command for launching the Model Context Protocol server."""

from __future__ import annotations

import click
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import AppContext


@click.command()
@click.pass_obj
def mcp(ctx: AppContext) -> None:
    """Launch the Model Context Protocol (MCP) server.

    Exposes dwriter's core functionality as tools for AI assistants
    (like Claude, ChatGPT, etc.) that support the MCP standard.

    The server runs over STDIO, making it suitable for use as a local
    plugin in MCP-compatible clients.

    Examples:
      dwriter mcp
    """
    from ..mcp_server import main as mcp_main

    # MCP servers communicate over stdout. Status messages MUST go to stderr.
    import sys
    ctx.console.file = sys.stderr
    
    mcp_main()
