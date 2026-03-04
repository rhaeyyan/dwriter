"""Config command for managing Day Writer configuration."""

import os
import subprocess

import click

from ..cli import AppContext


@click.group()
def config():
    """View and edit configuration.

    Day Writer stores configuration in ~/.day-writer/config.toml

    Use 'dwriter config show' to view current settings,
    'dwriter config edit' to modify them.
    """
    pass


@config.command("show")
@click.pass_obj
def config_show(ctx: AppContext):
    """View current configuration."""
    config_dict = ctx.config_manager.to_dict()

    ctx.console.print("[bold blue]Current Configuration[/bold blue]")
    ctx.console.print("=" * 40)
    ctx.console.print()

    # Standup settings
    ctx.console.print("[bold][standup][/bold]")
    ctx.console.print(f"  format = \"{config_dict['standup']['format']}\"")
    ctx.console.print(
        "  copy_to_clipboard = "
        f"{str(config_dict['standup']['copy_to_clipboard']).lower()}"
    )
    ctx.console.print()

    # Review settings
    ctx.console.print("[bold][review][/bold]")
    ctx.console.print(f"  default_days = {config_dict['review']['default_days']}")
    ctx.console.print(f"  format = \"{config_dict['review']['format']}\"")
    ctx.console.print()

    # Display settings
    ctx.console.print("[bold][display][/bold]")
    ctx.console.print(
        "  show_confirmation = "
        f"{str(config_dict['display']['show_confirmation']).lower()}"
    )
    ctx.console.print(
        "  show_id = "
        f"{str(config_dict['display']['show_id']).lower()}"
    )
    ctx.console.print(
        "  colors = " f"{str(config_dict['display']['colors']).lower()}"
    )
    ctx.console.print()

    # Defaults
    ctx.console.print("[bold][defaults][/bold]")
    if config_dict["defaults"]["tags"]:
        tags_str = ", ".join(f'"{t}"' for t in config_dict["defaults"]["tags"])
        ctx.console.print(f"  tags = [{tags_str}]")
    else:
        ctx.console.print("  tags = []")

    if config_dict["defaults"]["project"]:
        ctx.console.print(f"  project = \"{config_dict['defaults']['project']}\"")
    else:
        ctx.console.print("  project = null")

    ctx.console.print()
    ctx.console.print(f"Config file: {ctx.config_manager.get_config_path()}")


@config.command("edit")
@click.pass_obj
def config_edit(ctx: AppContext):
    """Edit configuration file."""
    config_path = ctx.config_manager.get_config_path()

    # Ensure config file exists
    ctx.config_manager.load()

    # Get editor from environment or use default
    editor = os.environ.get("EDITOR", "nano")

    try:
        subprocess.run([editor, str(config_path)])
        # Reload config after editing
        ctx.config_manager._config = None
        ctx.config_manager.load()
        ctx.console.print("[green]✅[/green] Configuration updated.")
    except FileNotFoundError:
        ctx.console.print(
            f"[yellow]![/yellow] Could not find editor '{editor}'. "
            + "Set EDITOR environment variable or edit file directly:"
        )
        ctx.console.print(f"  {config_path}")
    except Exception as e:
        ctx.console.print(f"[red]![/red] Error opening editor: {e}")
        ctx.console.print(f"Edit file directly: {config_path}")


@config.command("reset")
@click.pass_obj
def config_reset(ctx: AppContext):
    """Reset configuration to defaults."""
    if click.confirm("Reset all settings to defaults?"):
        ctx.config_manager.reset()
        ctx.console.print("[green]✅[/green] Configuration reset to defaults.")
    else:
        ctx.console.print("Cancelled.")


@config.command("path")
@click.pass_obj
def config_path(ctx: AppContext):
    """Show configuration file path."""
    ctx.console.print(ctx.config_manager.get_config_path())
