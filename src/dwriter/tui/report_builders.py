"""Deterministic report builders for the Insight Hub.

Pure functions that accept an AnalyticsEngine + database and return
(title, body) Rich markup strings. No Textual imports; no AI imports.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Database


def build_report(report_type: str, db: Database) -> tuple[str, str]:
    """Return (title, body) Rich markup for the given insight report type."""
    from ..analytics import AnalyticsEngine, InsightGenerator

    engine = AnalyticsEngine(db)

    if report_type == "energy":
        return _energy(engine)
    if report_type == "momentum":
        return _momentum(engine)
    if report_type == "golden-hour":
        return _golden_hour(engine)
    if report_type == "stale":
        return _stale(engine, db)
    if report_type == "focus":
        return _focus(engine)
    if report_type == "pulse":
        return _pulse(engine, InsightGenerator(engine))
    return ("Report", "[dim]Unknown report type.[/]")


# ---------------------------------------------------------------------------
# Individual builders
# ---------------------------------------------------------------------------

def _bar(value: float, max_value: float, width: int = 16) -> str:
    filled = int((value / max(max_value, 0.01)) * width)
    return "█" * filled + "░" * (width - filled)


def _energy(engine: object) -> tuple[str, str]:
    from ..analytics import AnalyticsEngine
    assert isinstance(engine, AnalyticsEngine)

    title = "🔋 Energy Radar"
    distribution = engine.get_domain_energy_distribution()

    if not distribution:
        return title, (
            "[dim]No energy data yet. Add entries with life domain "
            "classifications to populate this report.[/]"
        )

    lines = ["[bold]Average energy level by life domain[/]\n"]
    sorted_domains = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
    for domain, avg in sorted_domains:
        bar = _bar(avg, 10, 16)
        color = "#a6e3a1" if avg >= 7 else "#f9e2af" if avg >= 5 else "#f38ba8"
        lines.append(
            f"  [bold]{domain:<14}[/] [{color}]{bar}[/]  [bold #cba6f7]{avg:.1f}[/]"
        )

    if len(sorted_domains) >= 2:
        top_domain = sorted_domains[0][0]
        low_domain = sorted_domains[-1][0]
        lines.append(
            f"\n  [dim]Peak: [bold]{top_domain}[/]  ·  "
            f"Needs attention: [bold]{low_domain}[/][/]"
        )

    return title, "\n".join(lines)


def _momentum(engine: object) -> tuple[str, str]:
    from ..analytics import AnalyticsEngine
    assert isinstance(engine, AnalyticsEngine)

    title = "⚡ Momentum Report"
    added, done = engine.get_say_do_ratio(days=7)
    current_cleared, delta = engine.get_velocity_delta()
    say_do = (done / max(added, 1)) * 100

    completion_color = (
        "#a6e3a1" if say_do >= 70 else "#f9e2af" if say_do >= 40 else "#f38ba8"
    )
    trend_color = "#a6e3a1" if delta >= 0 else "#f38ba8"
    trend_icon = "↑" if delta >= 0 else "↓"

    bar = _bar(say_do, 100, 18)

    lines = [
        "[bold]Say-Do Ratio  (last 7 days)[/]\n",
        f"  [{completion_color}]{bar}[/]  [bold #cba6f7]{say_do:.0f}%[/]",
        f"  [dim]{done} completed  /  {added} added[/]",
        "",
        "[bold]Velocity Delta[/]\n",
        f"  [{trend_color}]{trend_icon} {abs(delta)}%[/] vs. last week"
        f"  [dim]({current_cleared} tasks cleared)[/]",
    ]

    if say_do >= 70:
        assessment = "[#a6e3a1]Strong execution — you're shipping what you plan.[/]"
    elif say_do >= 40:
        assessment = (
            "[#f9e2af]Moderate execution — review blocked or carry-over tasks.[/]"
        )
    else:
        assessment = "[#f38ba8]Low execution — consider reducing planned load.[/]"
    lines.append(f"\n  {assessment}")

    return title, "\n".join(lines)


def _golden_hour(engine: object) -> tuple[str, str]:
    from ..analytics import AnalyticsEngine
    assert isinstance(engine, AnalyticsEngine)

    title = "🕒 Golden Hour"
    peak = engine.get_golden_hour()
    pulse = engine.get_weekly_pulse()

    lines = [
        "[bold]Peak Productivity Window[/]\n",
        f"  [bold #cba6f7]{peak}[/]  ← highest combined activity\n",
    ]

    if pulse:
        max_count = max(pulse.values()) or 1
        lines.append("[bold]Activity by Day of Week[/]\n")
        for day, count in pulse.items():
            bar = _bar(count, max_count, 16)
            intensity = (
                "#a6e3a1" if count >= max_count * 0.7
                else "#f9e2af" if count >= max_count * 0.4
                else "#cdd6f4"
            )
            lines.append(
                f"  [bold]{day:<4}[/] [{intensity}]{bar}[/]  [dim]{count}[/]"
            )

    return title, "\n".join(lines)


def _stale(engine: object, db: Database) -> tuple[str, str]:
    from ..analytics import AnalyticsEngine
    assert isinstance(engine, AnalyticsEngine)

    title = "⚠️ Stale Task Report"
    fresh, stale, dead = engine.get_task_staleness()
    stale_todos = db.get_stale_todos(limit=10)
    total = fresh + stale + dead

    # Health summary bar
    bar_width = 10
    f_filled = int((fresh / max(total, 1)) * bar_width)
    s_filled = int((stale / max(total, 1)) * bar_width)
    d_filled = bar_width - f_filled - s_filled

    lines = [
        "[bold]Task Health[/]\n",
        f"  [bold #a6e3a1]Fresh[/] {'█' * f_filled}  "
        f"[bold #f9e2af]Stale[/] {'█' * s_filled}  "
        f"[bold #f38ba8]Dead[/] {'█' * max(d_filled, 0)}",
        f"  [dim]{fresh} fresh  ·  {stale} stale  ·  {dead} dead  ·  {total} total[/]",
    ]

    if stale_todos:
        now = datetime.now()
        lines.append("\n[bold]Oldest Pending Tasks[/]\n")
        for t in stale_todos:
            days_old = (now - t.created_at).days
            age_color = (
                "#f38ba8" if days_old > 14 else
                "#f9e2af" if days_old > 3 else "#a6e3a1"
            )
            proj_str = f"[bold #F77F00]&{t.project}[/]  " if t.project else ""
            # Full content — no truncation
            lines.append(f"  {t.content}")
            lines.append(
                f"  {proj_str}[{age_color}]{days_old}d[/]"
                f"  {_bar(min(days_old, 21), 21, 14)}\n"
            )

    return title, "\n".join(lines)


def _focus(engine: object) -> tuple[str, str]:
    from ..analytics import AnalyticsEngine
    assert isinstance(engine, AnalyticsEngine)

    title = "🏷️ Focus Report"
    tag_velocity = engine.get_tag_velocity(days=14)
    big_rock = engine.get_big_rock(days=7)
    context_switches = engine.get_context_switches(days=7)

    lines = ["[bold]Top Tags  (last 14 days)[/]\n"]

    if tag_velocity:
        for tag, count, trend in tag_velocity[:6]:
            trend_color = (
                "#a6e3a1" if "↑" in trend or "↗" in trend
                else "#f38ba8" if "↓" in trend or "↘" in trend
                else "#cdd6f4"
            )
            lines.append(
                f"  [bold #66D0BC]#{tag:<14}[/]"
                f" {count:>3}  [{trend_color}]{trend}[/]"
            )
    else:
        lines.append("  [dim]No tag data yet.[/]")

    if big_rock:
        proj, pct = big_rock
        bar = _bar(pct, 100, 18)
        lines.append("\n[bold]Big Rock[/]\n")
        lines.append(
            f"  [bold #F77F00]&{proj}[/]  [bold #cba6f7]{pct:.0f}%[/] of bandwidth"
        )
        lines.append(f"  [#F77F00]{bar}[/]")

    lines.append("\n[bold]Context Switches[/]\n")
    switch_color = (
        "#f38ba8" if context_switches > 4
        else "#f9e2af" if context_switches > 2
        else "#a6e3a1"
    )
    switch_label = (
        "high fragmentation" if context_switches > 4
        else "moderate switching" if context_switches > 2
        else "good focus"
    )
    lines.append(
        f"  [{switch_color}]{context_switches:.1f} avg projects/day[/]"
        f"  [dim]← {switch_label}[/]"
    )

    return title, "\n".join(lines)


def _pulse(engine: object, insight_gen: object) -> tuple[str, str]:
    from ..analytics import AnalyticsEngine, InsightGenerator
    assert isinstance(engine, AnalyticsEngine)
    assert isinstance(insight_gen, InsightGenerator)

    title = "🎭 Weekly Pulse"
    wrapup = insight_gen.generate_weekly_wrapup()
    deep_work, shallow_work, deep_ratio = engine.get_deep_work_ratio(days=7)
    pulse = engine.get_weekly_pulse()

    focus_color = (
        "#a6e3a1" if deep_ratio >= 30
        else "#f9e2af" if deep_ratio >= 15
        else "#f38ba8"
    )

    lines = ["[bold]7-Day Snapshot[/]\n"]
    for insight in wrapup:
        lines.append(f"  {insight}")

    if pulse:
        max_count = max(pulse.values()) or 1
        lines.append("\n[bold]Activity This Week[/]\n")
        days_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        counts_row = "  "
        bars_row = "  "
        for day in days_abbr:
            count = pulse.get(day, 0)
            intensity = (
                "#a6e3a1" if count >= max_count * 0.7
                else "#f9e2af" if count >= max_count * 0.3
                else "#cdd6f4" if count > 0
                else "#313244"
            )
            block = "█" if count >= max_count * 0.7 else "▓" if count > 0 else "░"
            bars_row += f"[{intensity}]{block}[/]  "
            counts_row += f"[dim]{str(count):<3}[/]"
        lines.append("  Mon Tue Wed Thu Fri Sat Sun")
        lines.append(bars_row)
        lines.append(counts_row)

    lines.append("\n[bold]Deep Work Ratio[/]\n")
    bar = _bar(deep_ratio, 100, 18)
    lines.append(
        f"  [{focus_color}]{bar}[/]  [{focus_color}]{deep_ratio:.0f}%[/] deep"
    )
    lines.append(
        f"  [dim]{deep_work} deep sessions  ·  {shallow_work} shallow[/]"
    )

    return title, "\n".join(lines)
