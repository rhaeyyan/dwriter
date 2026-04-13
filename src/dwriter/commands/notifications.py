"""Commands for managing dwriter's push notification daemon via systemd."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ..cli import AppContext

# ─── Systemd unit templates ───────────────────────────────────────────────────

_SERVICE_TEMPLATE = """\
[Unit]
Description=dwriter reminder check
Documentation=https://github.com/yourusername/dwriter

[Service]
Type=oneshot
ExecStart={exec_path} --check-only
StandardOutput=null
StandardError=journal
"""

_TIMER_TEMPLATE = """\
[Unit]
Description=dwriter reminder timer
After=graphical-session.target
PartOf=graphical-session.target

[Timer]
OnBootSec=2min
OnUnitActiveSec={interval}min
Persistent=true

[Install]
WantedBy=timers.target
"""

SERVICE_NAME = "dwriter-remind.service"
TIMER_NAME = "dwriter-remind.timer"


def _systemd_user_dir() -> Path:
    """Return the systemd user unit directory, creating it if needed."""
    xdg_config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    unit_dir = xdg_config / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    return unit_dir


def _find_dwriter_executable() -> str | None:
    """Locate the dwriter executable on PATH."""
    import shutil

    return shutil.which("dwriter")


def _run_systemctl(*args: str) -> tuple[int, str]:
    """Run a systemctl --user command, returning (returncode, combined output)."""
    result = subprocess.run(
        ["systemctl", "--user", *args],
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


# ─── Commands ─────────────────────────────────────────────────────────────────


@click.command("install-notifications")
@click.option(
    "--interval",
    default=5,
    show_default=True,
    type=click.IntRange(1, 60),
    help="How often to check for reminders (minutes).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Print what would be installed without making changes.",
)
@click.pass_obj
def install_notifications(ctx: AppContext, interval: int, dry_run: bool) -> None:
    """Install a background reminder checker using systemd (Linux only).

    Writes two unit files to ~/.config/systemd/user/:

      dwriter-remind.service  — runs 'dwriter --check-only'
      dwriter-remind.timer    — fires every INTERVAL minutes

    After installation, desktop notifications appear automatically via
    notify-send whenever an urgent task's due time is approaching.

    Requires 'notifications_enabled = true' in your dwriter config:
      dwriter config set notifications_enabled true

    Examples:
      dwriter install-notifications
      dwriter install-notifications --interval 10
      dwriter install-notifications --dry-run
    """
    console = ctx.console

    if sys.platform != "linux":
        _show_non_linux_instructions(console)
        return

    exec_path = _find_dwriter_executable()
    if exec_path is None:
        console.print(
            "[red]Error:[/red] 'dwriter' binary not found on PATH.\n"
            "Install with [bold]uv tool install .[/bold] first."
        )
        return

    unit_dir = _systemd_user_dir()
    service_path = unit_dir / SERVICE_NAME
    timer_path = unit_dir / TIMER_NAME

    service_content = _SERVICE_TEMPLATE.format(exec_path=exec_path)
    timer_content = _TIMER_TEMPLATE.format(interval=interval)

    if dry_run:
        console.print("[bold yellow]--- DRY RUN ---[/bold yellow]\n")
        console.print(f"[dim]Would write:[/dim] {service_path}")
        console.print(service_content)
        console.print(f"[dim]Would write:[/dim] {timer_path}")
        console.print(timer_content)
        console.print(
            "[dim]Would run:[/dim] systemctl --user daemon-reload\n"
            f"[dim]Would run:[/dim] systemctl --user enable --now {TIMER_NAME}"
        )
        return

    # Write unit files
    service_path.write_text(service_content)
    timer_path.write_text(timer_content)
    console.print(f"[green]✔[/green] Wrote {service_path}")
    console.print(f"[green]✔[/green] Wrote {timer_path}")

    # Reload systemd and enable the timer
    rc, out = _run_systemctl("daemon-reload")
    if rc != 0:
        console.print(f"[yellow]Warning:[/yellow] daemon-reload failed: {out}")

    rc, out = _run_systemctl("enable", "--now", TIMER_NAME)
    if rc != 0:
        console.print(f"[red]Error:[/red] Could not enable timer: {out}")
        console.print(
            "Try enabling 'lingering' so that user units can start without login:\n"
            "  [bold]loginctl enable-linger $USER[/bold]"
        )
        return

    console.print(f"[green]✔[/green] Timer enabled: checks every {interval} minute(s)")

    # Verify timer is active
    rc, out = _run_systemctl("is-active", TIMER_NAME)
    status = out.strip()
    console.print(f"[green]✔[/green] Timer status: [bold]{status}[/bold]")

    # Friendly reminder about the config toggle
    if not ctx.config.display.notifications_enabled:
        console.print(
            "\n[yellow]Note:[/yellow] Push notifications are currently [bold]disabled[/bold] in config.\n"  # noqa: E501
            "Enable them with:\n"
            "  [bold]dwriter config set notifications_enabled true[/bold]"
        )
    else:
        console.print(
            "\n[green]All set![/green] dwriter will now send desktop notifications "
            f"every {interval} minute(s) for urgent tasks."
        )


@click.command("uninstall-notifications")
@click.pass_obj
def uninstall_notifications(ctx: AppContext) -> None:
    """Remove the dwriter background reminder checker.

    Disables and deletes the systemd user units installed by
    'install-notifications'.

    Example:
      dwriter uninstall-notifications
    """
    console = ctx.console

    if sys.platform != "linux":
        console.print(
            "[yellow]Note:[/yellow] Automated notification daemons are only "
            "managed on Linux. Remove any cron jobs or launchd plists manually."
        )
        return

    unit_dir = _systemd_user_dir()
    service_path = unit_dir / SERVICE_NAME
    timer_path = unit_dir / TIMER_NAME

    # Stop and disable the timer first
    _run_systemctl("disable", "--now", TIMER_NAME)
    console.print(f"[green]✔[/green] Disabled {TIMER_NAME}")

    removed_any = False
    for path in (timer_path, service_path):
        if path.exists():
            path.unlink()
            console.print(f"[green]✔[/green] Removed {path}")
            removed_any = True

    if not removed_any:
        console.print("[dim]No unit files found — nothing to remove.[/dim]")

    # Reload systemd
    _run_systemctl("daemon-reload")
    console.print("[green]✔[/green] Notifications daemon removed.")


def _show_non_linux_instructions(console: click.utils._DefaultTextStderr | object) -> None:  # type: ignore[name-defined]  # noqa: E501
    """Print setup instructions for non-Linux platforms."""
    import click as _click  # local to avoid circular issues

    _click.echo("")
    if sys.platform == "darwin":  # macOS
        _click.echo(
            "macOS: Use launchd to schedule periodic checks.\n\n"
            "1. Find your dwriter path:  which dwriter\n"
            "2. Create ~/Library/LaunchAgents/com.dwriter.remind.plist:\n\n"
            "   <?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "   <!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\"\n"
            "     \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
            "   <plist version=\"1.0\"><dict>\n"
            "     <key>Label</key><string>com.dwriter.remind</string>\n"
            "     <key>ProgramArguments</key>\n"
            "     <array><string>/path/to/dwriter</string>"
            "<string>--check-only</string></array>\n"
            "     <key>StartInterval</key><integer>300</integer>\n"
            "   </dict></plist>\n\n"
            "3. Load it:  launchctl load ~/Library/LaunchAgents/com.dwriter.remind.plist\n"  # noqa: E501
        )
    elif sys.platform == "win32":  # Windows
        _click.echo(
            "Windows: Use Task Scheduler to run 'dwriter --check-only' every 5 minutes.\n\n"  # noqa: E501
            "  schtasks /Create /SC MINUTE /MO 5 /TN \"dwriterRemind\" "
            "/TR \"dwriter --check-only\"\n"
        )
    else:
        _click.echo(
            "Automated installation is only supported on Linux (systemd).\n"
            "Run 'dwriter --check-only' periodically via your system's task scheduler."
        )
