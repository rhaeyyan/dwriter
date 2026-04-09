from dataclasses import dataclass
from enum import Enum, auto


class PermissionMode(Enum):
    """Defines the available security levels for AI tool execution."""

    READ_ONLY = auto()
    APPEND_ONLY = auto()
    PROMPT = auto()
    DANGER_FULL_ACCESS = auto()


@dataclass(frozen=True)
class EnforcementResult:
    """The result of a permission check for a specific tool."""

    allowed: bool
    reason: str


class PermissionEnforcer:
    """Governs tool execution based on the active PermissionMode.

    This class provides architectural guards to ensure the AI remains within
    defined safety boundaries, preventing unauthorized data modification or
    system access.
    """

    def __init__(self, mode: PermissionMode = PermissionMode.APPEND_ONLY):
        self.active_mode = mode

        # Tool categories for classification
        self._read_tools = {
            "search_journal",
            "search_todos",
            "fetch_recent_commits",
            "get_daily_standup",
            "get_stats",
        }
        self._append_tools = {
            "add_entry",
            "add_todo",
            "start_timer",
        }
        self._mutating_tools = {
            "edit_todo",
            "delete_todo",
            "update_config",
            "sync_data",
        }

    def check(self, tool_name: str) -> EnforcementResult:
        """Evaluates if a tool can be executed under the current mode.

        Args:
            tool_name (str): The name of the tool attempting to execute.

        Returns:
            EnforcementResult: A dataclass containing the allow/deny status and rationale.
        """
        if self.active_mode == PermissionMode.DANGER_FULL_ACCESS:
            return EnforcementResult(True, "Full access granted by user.")

        if self.active_mode == PermissionMode.READ_ONLY:
            if tool_name in self._read_tools:
                return EnforcementResult(True, "Read-only access permitted.")
            return EnforcementResult(
                False, f"Tool '{tool_name}' denied: Read-only mode active."
            )

        if self.active_mode == PermissionMode.APPEND_ONLY:
            if tool_name in self._read_tools or tool_name in self._append_tools:
                return EnforcementResult(True, "Append-only access permitted.")
            return EnforcementResult(
                False, f"Tool '{tool_name}' denied: Append-only mode active."
            )

        if self.active_mode == PermissionMode.PROMPT:
            # In a real TUI environment, this would trigger a UI prompt.
            # At the logic layer, we flag it as requiring intervention.
            return EnforcementResult(
                False, f"Tool '{tool_name}' requires explicit user confirmation."
            )

        return EnforcementResult(False, f"Unknown tool or permission state: {tool_name}")
