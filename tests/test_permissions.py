"""Coverage for the AI tool PermissionEnforcer (Security Mode Guard).

These tests assert that every tool the agentic loop advertises to the model is
classified by the enforcer and resolves to the intended allow/deny per mode.
The headline gap they close: a read-only tool wired into the loop but never
added to ``_read_tools`` is silently denied in every non-danger mode.
"""

import pytest

from dwriter.ai.permissions import (
    PermissionEnforcer,
    PermissionMode,
    permission_mode_from_str,
)

# Tools advertised to the model in ask_second_brain_agentic, plus the graph
# read tools reachable via run_cypher. Keep in sync with engine.py's tool list.
READ_TOOLS = [
    "search_journal",
    "search_todos",
    "fetch_recent_commits",
    "get_daily_standup",
    "search_facts",
    "search_semantic",
    "run_cypher",
]
APPEND_TOOLS = ["add_entry", "add_todo", "start_timer"]
MUTATING_TOOLS = ["edit_todo", "delete_todo", "update_config", "sync_data"]
ALL_ADVERTISED = READ_TOOLS + APPEND_TOOLS + MUTATING_TOOLS


@pytest.mark.parametrize("tool", READ_TOOLS)
def test_read_tools_allowed_in_read_only(tool):
    enforcer = PermissionEnforcer(mode=PermissionMode.READ_ONLY)
    assert enforcer.check(tool).allowed, f"{tool} should be allowed in read-only"


@pytest.mark.parametrize("tool", READ_TOOLS + APPEND_TOOLS)
def test_read_and_append_allowed_in_append_only(tool):
    enforcer = PermissionEnforcer(mode=PermissionMode.APPEND_ONLY)
    assert enforcer.check(tool).allowed, f"{tool} should be allowed in append-only"


def test_search_semantic_allowed_in_default_mode():
    """Regression: search_semantic was denied in every mode but danger-full."""
    for mode in (PermissionMode.READ_ONLY, PermissionMode.APPEND_ONLY):
        assert PermissionEnforcer(mode=mode).check("search_semantic").allowed


@pytest.mark.parametrize("tool", APPEND_TOOLS + MUTATING_TOOLS)
def test_writes_denied_in_read_only(tool):
    enforcer = PermissionEnforcer(mode=PermissionMode.READ_ONLY)
    assert not enforcer.check(tool).allowed


@pytest.mark.parametrize("tool", MUTATING_TOOLS)
def test_mutations_denied_in_append_only(tool):
    enforcer = PermissionEnforcer(mode=PermissionMode.APPEND_ONLY)
    assert not enforcer.check(tool).allowed


@pytest.mark.parametrize("tool", ALL_ADVERTISED)
def test_danger_full_access_allows_everything(tool):
    enforcer = PermissionEnforcer(mode=PermissionMode.DANGER_FULL_ACCESS)
    assert enforcer.check(tool).allowed


@pytest.mark.parametrize("tool", ALL_ADVERTISED)
def test_prompt_mode_flags_everything(tool):
    """PROMPT mode defers to the UI, so the logic layer denies until confirmed."""
    enforcer = PermissionEnforcer(mode=PermissionMode.PROMPT)
    assert not enforcer.check(tool).allowed


@pytest.mark.parametrize("tool", ALL_ADVERTISED)
def test_every_advertised_tool_is_classified(tool):
    """Invariant: no advertised tool is unknown to the enforcer.

    An unclassified tool is allowed only in danger-full-access and denied
    everywhere else — a silent dead feature. This guards against that.
    """
    enforcer = PermissionEnforcer()
    classified = (
        enforcer._read_tools | enforcer._append_tools | enforcer._mutating_tools
    )
    assert tool in classified, f"{tool} is not classified by the enforcer"


def test_permission_mode_from_str_mapping():
    assert permission_mode_from_str("read-only") == PermissionMode.READ_ONLY
    assert permission_mode_from_str("append-only") == PermissionMode.APPEND_ONLY
    assert permission_mode_from_str("prompt") == PermissionMode.PROMPT
    assert (
        permission_mode_from_str("danger-full-access")
        == PermissionMode.DANGER_FULL_ACCESS
    )


def test_permission_mode_from_str_defaults_to_append_only():
    assert permission_mode_from_str("nonsense") == PermissionMode.APPEND_ONLY
    assert permission_mode_from_str("READ-ONLY") == PermissionMode.READ_ONLY
