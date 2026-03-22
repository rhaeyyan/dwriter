"""Examples command - provides common usage examples."""

import click

from ..cli import AppContext


@click.command()
@click.pass_obj
def examples(ctx: AppContext) -> None:
    """Show common usage examples and workflows.

    Displays a set of common commands to get you started.
    """
    ctx.console.print("[bold blue]🚀 dwriter Examples & Workflows[/bold blue]\n")
    
    ctx.console.print("[bold cyan]1. Quick Logging[/bold cyan]")
    ctx.console.print("   dwriter add \"Finished the auth refactor #backend &api\"")
    ctx.console.print("   dwriter add \"Drafted blog post\" --date \"yesterday\"")
    
    ctx.console.print("\n[bold cyan]2. Task Management[/bold cyan]")
    ctx.console.print("   dwriter todo \"Fix race condition\" --priority urgent")
    ctx.console.print("   dwriter todo list")
    ctx.console.print("   dwriter done 1  # Mark task 1 as complete and log it")
    
    ctx.console.print("\n[bold cyan]3. Focus Sessions[/bold cyan]")
    ctx.console.print("   dwriter timer 25 -p myproject -t deepwork")
    
    ctx.console.print("\n[bold cyan]4. Review & Standup[/bold cyan]")
    ctx.console.print("   dwriter standup        # Summary of yesterday's work")
    ctx.console.print("   dwriter review --days 7 # Summary of last week")
    
    ctx.console.print("\n[bold cyan]5. Interactive TUI[/bold cyan]")
    ctx.console.print("   dwriter                # Launch the full dashboard")
    ctx.console.print("   dwriter ui --todo      # Launch directly to todo board")
    
    ctx.console.print("\n[dim]For more details, visit: https://github.com/rhaeyyan/dwriter[/dim]")
