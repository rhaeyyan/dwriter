"""AI Engine for dwriter.

This module provides an interface for interacting with the AI provider
using instructor and the OpenAI-compatible API.
"""

import json
import re
from typing import Any

import instructor
from openai import OpenAI

from dwriter.ai.compression import SummaryCompressor
from dwriter.ai.permissions import PermissionEnforcer, permission_mode_from_str
from dwriter.ai.tools import (
    fetch_recent_commits,
    get_daily_standup,
    search_journal,
    search_todos,
)
from dwriter.config import AIConfig
from dwriter.tui.messages import AIToolEvent

AVAILABLE_TOOLS = {
    "get_daily_standup": get_daily_standup,
    "search_journal": search_journal,
    "search_todos": search_todos,
    "fetch_recent_commits": fetch_recent_commits,
}



def _sanitize_agent_output(text: str) -> str:
    if not text:
        return ""

    # 1. Strip Llama 3 special control tokens
    clean_text = re.sub(r'<\|.*?\|>', '', text)
    clean_text = re.sub(r'<tool_call>.*?</tool_call>', '', clean_text, flags=re.DOTALL)

    # 2. Strip hallucinated JSON blocks
    clean_text = re.sub(
        r'```(?:json)?\s*{\s*"(?:name|arguments|parameters)":.*?}\s*```',
        '', clean_text, flags=re.DOTALL | re.IGNORECASE
    )
    clean_text = re.sub(
        r'{\s*"(?:name|arguments|parameters)":\s*".*?}.*?}',
        '', clean_text, flags=re.DOTALL | re.IGNORECASE
    )

    # 2.5 Strip common LLM preambles/postambles surrounding tool calls
    clean_text = re.sub(
        r"(?im)^(?:here is|here's)\s+(?:the\s+|a\s+)?(?:json|function call|tool call|function|tool).*?$",
        '', clean_text
    )
    clean_text = re.sub(r'(?im)^\(note:.*?\)$', '', clean_text)

    # 3. Aggressive Markdown Closing (fixes Textual/Rich crashes)
    # Fix unclosed backticks
    if clean_text.count('`') % 2 != 0:
        clean_text += '`'

    # Fix unclosed bold/italic markers
    for marker in ['**', '__', '*', '_']:
        if clean_text.count(marker) % 2 != 0:
            clean_text += marker

    return clean_text.strip()


def ask_second_brain_agentic(
    prompt: str, config: AIConfig, context_data: str = "", app_context: Any = None
) -> str:
    """Conversational AI with tool-calling capabilities (ReAct loop).

    Args:
        prompt (str): The user's natural language query.
        config (AIConfig): AI configuration settings.
        context_data (str): Static context from history and activity logs.
        app_context (Any): Textual App or Screen for posting messages.

    Returns:
        str: The final AI response.
    """
    client = OpenAI(base_url=config.base_url, api_key="ollama")

    # Extract a shared db instance from the caller's app context so tool
    # functions can reuse the existing connection instead of opening new ones.
    db = None
    if app_context is not None:
        ctx_obj = getattr(app_context, "ctx", None)
        if ctx_obj is not None:
            db = getattr(ctx_obj, "db", None)

    # Enforce the context budget at the engine boundary regardless of what
    # the caller provides.  SummaryCompressor is the single enforcement point.
    compressor = SummaryCompressor()
    safe_context = compressor.compress(context_data) if context_data else ""

    messages = [
        {
            "role": "system",
            "content": (
                "You are dwriter 2nd-Brain, a professional productivity assistant. "
                "Your goal is to help the user reflect on their work and plan ahead. "
                "\n\nOUTPUT RULES:\n"
                "1. BE CONCISE. Avoid long preambles or repeating global state "
                "(like full TODO lists) unless explicitly asked.\n"
                "2. ALWAYS provide a natural language response. NEVER output raw "
                "JSON tool calls to the user.\n"
                "3. If the user asks for a 'standup' or 'report', use the "
                "'get_daily_standup' tool to fetch a formatted report.\n"
                "4. Use Markdown for formatting. Use emojis to keep it engaging "
                "but professional.\n"
                "5. You have access to tools to search journal entries, todos, "
                "and git commits. Use them to provide grounded, data-driven answers."
                f"\n\nSTATIC CONTEXT (PAST 72H & RECENT SUMMARIES):\n{safe_context}"
            ),
        },
        {"role": "user", "content": prompt},
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_journal",
                "description": (
                    "Searches the user's journal entries and time logs using fuzzy "
                    "matching. Use this whenever the user asks about past work, "
                    "specific notes, or history that may not be in the static context "
                    "— e.g. 'what did I work on last week?', 'find my notes about X', "
                    "'how much time did I spend on Y?'. Returns up to 10 entries with "
                    "timestamps, tags, project, mood, and energy level."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query describing what to find.",
                        },
                        "project": {
                            "type": "string",
                            "description": "Optional: filter by project name (without the & prefix).",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_daily_standup",
                "description": (
                    "Generates a formatted Daily Standup report summarizing what was "
                    "done and what is planned. Use this when the user explicitly asks "
                    "for a 'standup', 'daily report', 'what did I do yesterday', or "
                    "wants a structured summary of a specific date's activity."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date_str": {
                            "type": "string",
                            "description": "The date in YYYY-MM-DD format. Omit for yesterday.",
                        },
                        "project": {
                            "type": "string",
                            "description": "Optional: filter by project name (without the & prefix).",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_todos",
                "description": (
                    "Searches the user's tasks and todo items by content, priority, "
                    "or deadline. Use this when the user asks about specific tasks, "
                    "what is pending, what is overdue, or anything about their "
                    "task list beyond what the static context shows."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query for tasks.",
                        },
                        "project": {
                            "type": "string",
                            "description": "Optional: filter by project name (without the & prefix).",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_recent_commits",
                "description": (
                    "Fetches recent git commit messages from the user's current "
                    "repository. Returns short hash, subject line, and relative time "
                    "(e.g. '2 hours ago'). Use this when the user asks about recent "
                    "code changes, what was shipped, or git activity."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of commits to fetch (default 10).",
                        },
                    },
                },
            },
        },
    ]

    full_response_parts = []
    enforcer = PermissionEnforcer(mode=permission_mode_from_str(config.features.permission_mode))

    while True:
        response = client.chat.completions.create(
            model=config.chat_model,
            messages=messages,  # type: ignore
            tools=tools,  # type: ignore
        )

        message = response.choices[0].message
        messages.append(message)  # type: ignore

        if message.content:
            sanitized = _sanitize_agent_output(message.content)
            if sanitized:
                full_response_parts.append(sanitized)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # Security check before execution
            permission = enforcer.check(function_name)
            if not permission.allowed:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": f"System Error: Permission Denied - {permission.reason}",
                    }
                )
                continue

            if app_context:
                app_context.post_message(AIToolEvent(tool_name=function_name))

            if function_name in AVAILABLE_TOOLS:
                tool_func = AVAILABLE_TOOLS[function_name]
                result = tool_func(db=db, **arguments)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(result),
                    }
                )
            else:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": f"Error: Tool {function_name} not found.",
                    }
                )

    return "\n\n".join(full_response_parts)


def generate_targeted_briefing(
    briefing_type: str,
    config: AIConfig,
    context_data: str = "",
    extra_data: dict[str, Any] | None = None,
) -> str:
    """Generates a highly targeted AI briefing based on specific analytics data.

    Args:
        briefing_type: One of 'weekly_retro', 'burnout_check', 'catch_up'.
        config: AI configuration.
        context_data: Static context (history).
        extra_data: Specific data for the briefing (e.g., filtered entries for Catch Up).

    Returns:
        str: The AI-generated briefing in Markdown. Returns clean Markdown
             suitable for display or file export. Callers are responsible
             for any Rich/terminal rendering transformation. Do not apply
             Rich markup before passing this output to file writers.
    """
    client = OpenAI(base_url=config.base_url, api_key="ollama")

    system_prompts = {
        "weekly_retro": (
            "You are the dwriter 2nd-Brain. Generate a 'Weekly Retrospective' briefing. "
            "Focus on: 1. Biggest Wins, 2. Velocity Trends, 3. Project Momentum, "
            "4. Areas for improvement next week. "
            "Use a professional yet encouraging tone. Use clean Markdown formatting. "
            "Limit to 4-5 concise paragraphs or bullet groups."
        ),
        "burnout_check": (
            "You are the dwriter 2nd-Brain. Generate a 'Burnout & Productivity' assessment. "
            "Analyze after-hours work, context switching, and say-do ratios. "
            "Provide actionable advice to reduce stress and improve focus. "
            "Be direct and supportive. Use Markdown highlights."
        ),
        "catch_up": (
            "You are the dwriter 2nd-Brain. Generate a 'Catch Up' briefing for the "
            "requested criteria (project/tags/dates). "
            "Summarize: 1. Key Accomplishments, 2. Blockers encountered, "
            "3. Progress on specific goals, 4. The 'Next Move' for this work stream. "
            "Be highly concise and high-signal. Use bolding for emphasis."
        ),
    }

    prompt = system_prompts.get(briefing_type, "Provide a general productivity briefing.")

    user_content = f"### ANALYTICS & CONTEXT:\n{context_data}\n"
    if extra_data:
        # Convert objects to serializable format (strings for datetimes)
        serialized_extra = json.dumps(extra_data, default=str)
        user_content += f"\n### TARGETED DATA FOR BRIEFING:\n{serialized_extra}"

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]

    response = client.chat.completions.create(
        model=config.chat_model,
        messages=messages,  # type: ignore
    )

    return _sanitize_agent_output(response.choices[0].message.content or "")


def get_ai_client(config: AIConfig) -> Any:
    """Initializes and returns an instructor-wrapped OpenAI client.

    Args:
        config (AIConfig): The AI configuration settings.

    Returns:
        Any: The instructor-wrapped client.
    """
    # MD_JSON mode is used to enhance robustness for local models,
    # such as Llama 3.1, which perform better with Markdown-wrapped JSON outputs.
    return instructor.from_openai(
        OpenAI(base_url=config.base_url, api_key="ollama"),
        mode=instructor.Mode.MD_JSON,
    )


def get_raw_ai_client(config: AIConfig) -> OpenAI:
    """Initializes and returns a standard OpenAI client.

    This client is intended for unstructured chat or text completion where
    Pydantic response models are not required.

    Args:
        config (AIConfig): The AI configuration settings.

    Returns:
        OpenAI: The standard OpenAI client.
    """
    return OpenAI(base_url=config.base_url, api_key="ollama")


def get_embedding(text: str, config: AIConfig) -> list[float]:
    """Generates a vector embedding for the given text using the Ollama API.

    Args:
        text (str): The source text to embed.
        config (AIConfig): The AI configuration settings.

    Returns:
        list[float]: The generated embedding vector.
    """
    client = OpenAI(base_url=config.base_url, api_key="ollama")
    response = client.embeddings.create(model="nomic-embed-text", input=text)
    return response.data[0].embedding


def get_semantic_recommendation(
    content: str,
    similar_entries: list[Any],
    config: AIConfig
) -> Any:
    """Generates a proactive recommendation for project and tags.

    Args:
        content (str): The new entry content.
        similar_entries (list[Entry]): A list of semantically similar past entries.
        config (AIConfig): The AI configuration settings.

    Returns:
        SemanticRecommendation: The AI-generated recommendations.
    """
    from .schemas.extraction import SemanticRecommendation

    client = get_ai_client(config)

    # Prepare context from similar entries
    context_parts = []
    for entry in similar_entries:
        meta = []
        if entry.project:
            meta.append(f"&{entry.project}")
        if entry.tag_names:
            meta.extend([f"#{t}" for t in entry.tag_names])
        meta_str = " ".join(meta)
        context_parts.append(f"Entry: {entry.content}\nTags/Project: {meta_str}")

    context_str = "\n\n".join(context_parts)

    system_msg = get_system_prompt(
        "You are a proactive assistant for a terminal-based journal. "
        "Based on the following past entries and their tags/projects, "
        "recommend 1 Project (&name) and up to 2 Tags (#tag) for the new entry. "
        "Only suggest if there is a strong semantic relationship. "
        "Ensure projects start with '&' and tags start with '#'."
    )

    user_msg = (
        f"### PAST CONTEXT:\n{context_str}\n\n"
        f"### NEW ENTRY:\n{content}"
    )

    return client.chat.completions.create(
        model=config.daemon_model,
        response_model=SemanticRecommendation,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )


def get_system_prompt(base_prompt: str) -> str:
    """Wraps a base prompt with instructions for strict data output.

    Appends instructions to the base prompt to ensure the model returns
    only a valid JSON instance without schema definitions or explanatory text.

    Args:
        base_prompt (str): The primary system instruction.

    Returns:
        str: The combined system prompt.
    """
    return (
        f"{base_prompt}\n\n"
        "Return ONLY a valid JSON instance. "
        "Do NOT return a JSON schema. Do NOT include '$defs'. "
        "Do NOT include the field names like 'properties' or 'type' "
        "in your root object. "
        "Just the raw data values matching the requested structure."
    )
