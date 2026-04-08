import pytest
from dwriter.ai.engine import _sanitize_agent_output

def test_sanitize_xml_tags():
    text = "Here is the answer.<tool_call>{\"name\": \"search\"}</tool_call>"
    assert _sanitize_agent_output(text) == "Here is the answer."

def test_sanitize_markdown_json():
    text = "Searching now...\n```json\n{\"name\": \"search_journal\", \"arguments\": {\"query\": \"test\"}}\n```"
    assert _sanitize_agent_output(text) == "Searching now..."

def test_sanitize_raw_json():
    text = "I found this: {\"name\": \"search_todos\", \"arguments\": {\"query\": \"task\"}}"
    assert _sanitize_agent_output(text) == "I found this:"

def test_sanitize_multiple_leaks():
    text = "<tool_call>xxx</tool_call> Thought: ```json {\"name\": \"x\"} ``` Actual answer."
    assert _sanitize_agent_output(text) == "Thought:  Actual answer."

def test_sanitize_none_or_empty():
    assert _sanitize_agent_output(None) == ""
    assert _sanitize_agent_output("") == ""

def test_sanitize_no_leak():
    text = "This is a clean response with no tools."
    assert _sanitize_agent_output(text) == text
