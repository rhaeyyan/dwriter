"""Config command for managing Day Writer configuration."""

import os
import subprocess

import click

from ..config import ConfigManager


@click.group()
@click.pass_context
def config(ctx):
    """View and edit configuration.

    Day Writer stores configuration in ~/.day-writer/config.toml

    Use 'dwriter config show' to view current settings,
    'dwriter config edit' to modify them.
    """
    pass


@config.command("show")
@click.pass_context
def config_show(ctx):
    """View current configuration."""
    config_manager = ConfigManager()
    config_manager.load()
    config_dict = config_manager.to_dict()

    click.echo(click.style("Current Configuration", bold=True, fg="blue"))
    click.echo("=" * 40)
    click.echo()

    # Standup settings
    click.echo(click.style("[standup]", bold=True))
    click.echo(f"  format = \"{config_dict['standup']['format']}\"")
    click.echo(
        "  copy_to_clipboard = "
        f"{str(config_dict['standup']['copy_to_clipboard']).lower()}"
    )
    click.echo()

    # Review settings
    click.echo(click.style("[review]", bold=True))
    click.echo(f"  default_days = {config_dict['review']['default_days']}")
    click.echo(f"  format = \"{config_dict['review']['format']}\"")
    click.echo()

    # Display settings
    click.echo(click.style("[display]", bold=True))
    click.echo(
        "  show_confirmation = "
        f"{str(config_dict['display']['show_confirmation']).lower()}"
    )
    click.echo("  show_id = " f"{str(config_dict['display']['show_id']).lower()}")
    click.echo("  colors = " f"{str(config_dict['display']['colors']).lower()}")
    click.echo()

    # Defaults
    click.echo(click.style("[defaults]", bold=True))
    if config_dict["defaults"]["tags"]:
        tags_str = ", ".join(f'"{t}"' for t in config_dict["defaults"]["tags"])
        click.echo(f"  tags = [{tags_str}]")
    else:
        click.echo("  tags = []")

    if config_dict["defaults"]["project"]:
        click.echo(f"  project = \"{config_dict['defaults']['project']}\"")
    else:
        click.echo("  project = null")

    click.echo()
    click.echo(f"Config file: {config_manager.get_config_path()}")


@config.command("edit")
@click.pass_context
def config_edit(ctx):
    """Edit configuration file."""
    config_manager = ConfigManager()
    config_path = config_manager.get_config_path()

    # Ensure config file exists
    config_manager.load()

    # Get editor from environment or use default
    editor = os.environ.get("EDITOR", "nano")

    try:
        subprocess.run([editor, str(config_path)])
        # Reload config after editing
        config_manager._config = None
        config_manager.load()
        click.echo(click.style("✅", fg="green") + " Configuration updated.")
    except FileNotFoundError:
        click.echo(
            click.style("!", fg="yellow")
            + f" Could not find editor '{editor}'. "
            + "Set EDITOR environment variable or edit file directly:"
        )
        click.echo(f"  {config_path}")
    except Exception as e:
        click.echo(click.style("!", fg="red") + f" Error opening editor: {e}")
        click.echo(f"Edit file directly: {config_path}")


@config.command("reset")
@click.pass_context
def config_reset(ctx):
    """Reset configuration to defaults."""
    if click.confirm("Reset all settings to defaults?"):
        config_manager = ConfigManager()
        config_manager.reset()
        click.echo(click.style("✅", fg="green") + " Configuration reset to defaults.")
    else:
        click.echo("Cancelled.")


@config.command("path")
@click.pass_context
def config_path(ctx):
    """Show configuration file path."""
    config_manager = ConfigManager()
    click.echo(config_manager.get_config_path())
