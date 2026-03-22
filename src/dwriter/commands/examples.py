"""Examples command - provides common usage examples."""

import click

from ..cli import AppContext


@click.command()
@click.pass_obj
def examples(ctx: AppContext) -> None:
    """Show common usage examples and workflows.

    Displays a set of common commands to get you started.
    """
    ctx.console.print("[bold blue]dwriter: Common Workflows[/bold blue]\n")
    
    ctx.console.print("[bold cyan]1. Headless CLI (Quick Logging)[/bold cyan]")
    ctx.console.print("   dwriter add \"Refactored auth layer #backend &engine\"")
    ctx.console.print("   dwriter add \"Drafted documentation\" --date \"yesterday\"")
    
    ctx.console.print("\n[bold cyan]2. Task Management[/bold cyan]")
    ctx.console.print("   dwriter todo \"Fix race condition\" --priority urgent")
    ctx.console.print("   dwriter todo list")
    ctx.console.print("   dwriter done 1  # Mark task 1 as complete and log it")
    
    ctx.console.print("\n[bold cyan]3. Focus Timer[/bold cyan]")
    ctx.console.print("   dwriter timer 25 -p engine -t deepwork")
    
    ctx.console.print("\n[bold cyan]4. Reports & Summaries[/bold cyan]")
    ctx.console.print("   dwriter standup        # Summary of yesterday's work")
    ctx.console.print("   dwriter review --days 7 # Summary of last 7 days")
    
    ctx.console.print("\n[bold cyan]5. Unified Dashboard (TUI)[/bold cyan]")
    ctx.console.print("   dwriter                # Launch the full interactive dashboard")
    ctx.console.print("   dwriter ui --todo      # Launch directly to the todo board")
    
    ctx.console.print("\n[dim]Visit the documentation for advanced configuration and use cases.[/dim]")
