"""Prescriptive insight generator for dwriter analytics."""

from __future__ import annotations

import re

from .engine import AnalyticsEngine


class InsightGenerator:
    """Generates prescriptive advice based on analytics data."""

    def __init__(self, engine: AnalyticsEngine) -> None:
        """Initialize with an analytics engine instance."""
        self.engine = engine

    def _colorize(self, text: str) -> str:
        """Colorize tags and projects, safely ignoring Rich formatting tags."""

        def replacer(match: re.Match[str]) -> str:
            if match.group(1):
                # Group 1 matched a Rich tag like [bold #f38ba8], leave it completely alone!  # noqa: E501
                return match.group(0)
            elif match.group(2):
                # Group 2 matched a #tag
                return f"[bold #66D0BC]#{match.group(2)}[/]"
            elif match.group(3):
                # Group 3 matched a &project
                return f"[bold #F77F00]&{match.group(3)}[/]"
            elif match.group(4):
                # Use default text color for counts in parentheses
                return f"({match.group(4)})"
            return match.group(0)

        # This regex matches: (1) Rich tags OR (2) #tags OR (3) &projects OR (4) numbers in parentheses  # noqa: E501
        pattern = r"(\[.*?\])|#(\w+)|&(\w+)|\((\d+)\)"

        return re.sub(pattern, replacer, text)

    def generate_insights(self) -> list[str]:
        """Generate a list of actionable insights."""
        raw_insights = []

        # 1. Burnout check
        burnout = self.engine.get_rolling_burnout_score(days=7)
        if burnout > 0.7:
            raw_insights.append(
                "⚠️ [bold #f38ba8]Burnout Warning:[/] "
                "[#cdd6f4]You've been burning the candle at both ends. "
                "Try to sign off earlier tonight.[/]"
            )
        elif burnout > 0.4:
            raw_insights.append(
                "⏱️ [bold #f9e2af]Watch Your Pace:[/] "
                "[#cdd6f4]Late-night sessions are adding up. "
                "Consider grouping tasks to finish faster.[/]"
            )

        # 2. Workload / Say-Do Ratio
        added, done = self.engine.get_say_do_ratio(days=7)
        if added > 0:
            completion_rate = done / added
            if completion_rate >= 0.8:
                raw_insights.append(
                    f"⚖️ [bold #a6e3a1]Great Follow-through![/] "
                    f"[#cdd6f4]You finished {done} out of {added} tasks. "
                    "Keep this momentum going![/]"
                )
            elif completion_rate < 0.4:
                raw_insights.append(
                    f"📦 [bold #f9e2af]Backlog Alert:[/] "
                    f"[#cdd6f4]You added {added} tasks but only finished {done}. "
                    "Maybe it's time to say 'no' to something new?[/]"
                )

        # 3. Context switching check
        switches = self.engine.get_context_switches(days=7)
        if switches > 4.0:
            raw_insights.append(
                f"🔄 [bold #f9e2af]Context Switcher:[/] "
                f"[#cdd6f4]You're juggling {switches:.1f} projects a day. "
                "Try focusing on just one for a few hours.[/]"
            )

        # 4. Friction Ratio (Project ROI)
        roi_data = self.engine.get_project_roi(days=45)
        if roi_data:
            highest_friction_proj, ratio, entries, todos = roi_data[0]
            if ratio > 3.0 and entries > 5:
                raw_insights.append(
                    f"🚧 [bold #fab387]Project Friction: &{highest_friction_proj}[/]. "
                    f"[#cdd6f4]Lots of notes ({entries}) but few tasks completed ({todos}). "  # noqa: E501
                    "Try breaking this down into smaller steps.[/]"
                )

        # 5. Backlog check
        fresh, stale, dead = self.engine.get_task_staleness()
        total_pending = fresh + stale + dead
        if total_pending > 0 and (dead / total_pending) > 0.3:
            raw_insights.append(
                f"🧹 [bold #f38ba8]Staleness Alert:[/] "
                f"[#cdd6f4]{dead} tasks have gone cold. "
                "Consider a cleanup or a fresh start on them.[/]"
            )

        # 6. Deep work check
        deep_count, shallow_count, deep_ratio = self.engine.get_deep_work_ratio(days=7)
        if deep_ratio < 20.0 and (deep_count + shallow_count) > 5:
            raw_insights.append(
                "🧘 [bold #a6e3a1]Focus Time Needed:[/] "
                "[#cdd6f4]Admin tasks are taking over. "
                "Schedule a deep-work session today.[/]"
            )
        elif deep_ratio > 50.0:
            raw_insights.append(
                "🔥 [bold #a6e3a1]High Focus:[/] "
                "[#cdd6f4]You are dedicating a significant portion of your time "
                "to deep work sessions.[/]"
            )

        # Tag growth insights
        tag_velocity = self.engine.get_tag_velocity(days=45)
        if tag_velocity:
            top_tags = [f"#{t[0]}({t[1]})" for t in tag_velocity[:3]]
            tags_str = ", ".join(top_tags)
            raw_insights.append(
                f"🏷️ [bold #89b4fa]Active Focus:[/] "
                f"[#cdd6f4]Recent activity is concentrated in {tags_str}.[/]"
            )

        # Default summary if no specific alerts
        if not raw_insights:
            raw_insights.append(
                "✨ [bold #a6e3a1]Current Status:[/] "
                "[#cdd6f4]Your workload distribution appears consistent "
                "across active projects.[/]"
            )

        # Apply colorization to all insights
        return [self._colorize(insight) for insight in raw_insights]

    def generate_weekly_wrapup(self) -> list[str]:
        """Generates the 7-day Weekly Pulse wrap-up."""
        raw_insights = []

        # 1. The Archetype
        archetype = self.engine.get_weekly_archetype()
        raw_insights.append(
            f"🎭 [bold #cba6f7]Your Archetype:[/] You were [bold]{archetype}[/] this week."  # noqa: E501
        )

        # 2. Peak Velocity
        golden_hour = self.engine.get_golden_hour()
        raw_insights.append(
            f"⚡ [bold #f9e2af]Peak Velocity:[/] "
            f"Your 'Golden Hour' of highest focus was at {golden_hour}."
        )

        # 3. Project Spotlight (The Big Rock)
        big_rock_data = self.engine.get_big_rock()
        if big_rock_data:
            proj, pct = big_rock_data
            raw_insights.append(
                f"⛰️ [bold #89b4fa]The Big Rock:[/] "
                f"&{proj} claimed {pct:.0f}% of your bandwidth."
            )
        else:
            raw_insights.append(
                "⛰️ [bold #89b4fa]The Big Rock:[/] No single project dominated your week."  # noqa: E501
            )

        # 4. Momentum (Velocity Delta)
        current_cleared, pct_change = self.engine.get_velocity_delta()
        trend = "more" if pct_change >= 0 else "fewer"
        raw_insights.append(
            f"🚀 [bold #a6e3a1]Momentum:[/] You cleared {current_cleared} tasks "
            f"({abs(pct_change)}% {trend} than last week)."
        )

        return [self._colorize(insight) for insight in raw_insights]
