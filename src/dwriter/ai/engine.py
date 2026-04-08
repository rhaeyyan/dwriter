"""AI Engine for dwriter.

This module provides an interface for interacting with the AI provider
using instructor and the OpenAI-compatible API.
"""

import json
import re
from typing import Any

import instructor
from openai import OpenAI

from dwriter.ai.tools import fetch_recent_commits, search_journal, search_todos
from dwriter.config import AIConfig
from dwriter.tui.messages import AIToolEvent

AVAILABLE_TOOLS = {
    "search_journal": search_journal,
    "search_todos": search_todos,
    "fetch_recent_commits": fetch_recent_commits,
}


def _sanitize_agent_output(text: str | None) -> str:
    """Strips hallucinated tool-call syntax leaked by local models."""
    if not text:
        return ""

    # Strip stray Llama 3 XML tool tags
    clean_text = re.sub(r"<tool_call>.*?</tool_call>", "", text, flags=re.DOTALL)

    # Strip hallucinated markdown JSON tool calls
    # We look for JSON blocks that contain "name" and "arguments" or typical tool signatures
    clean_text = re.sub(
        r"```(?:json)?\s*{\s*\"name\":\s*\"[^\"]+\".*?}\s*```",
        "",
        clean_text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Also strip raw JSON-like structures that look exactly like tool calls
    clean_text = re.sub(
        r"{\s*\"name\":\s*\"[^\"]+\",\s*\"arguments\":\s*\{.*?\}.*?}",
        "",
        clean_text,
        flags=re.DOTALL | re.IGNORECASE,
    )

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

    messages = [
        {
            "role": "system",
            "content": (
                "You are dwriter 2nd-Brain, a productivity assistant. "
                "Use the provided context and tools to answer user questions. "
                "You can search journal entries, todos, and git commits. "
                f"\n\nSTATIC CONTEXT:\n{context_data}"
            ),
        },
        {"role": "user", "content": prompt},
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_journal",
                "description": "Searches journal entries for notes and thoughts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"},
                        "project": {
                            "type": "string",
                            "description": "Optional project filter (&name)",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_todos",
                "description": "Searches tasks and todo items.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query"},
                        "project": {
                            "type": "string",
                            "description": "Optional project filter (&name)",
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
                "description": "Fetches recent git commit messages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of commits to fetch",
                        }
                    },
                },
            },
        },
    ]

    while True:
        response = client.chat.completions.create(
            model=config.model,
            messages=messages,  # type: ignore
            tools=tools,  # type: ignore
        )

        message = response.choices[0].message
        messages.append(message)  # type: ignore

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if app_context:
                app_context.post_message(AIToolEvent(tool_name=function_name))

            if function_name in AVAILABLE_TOOLS:
                tool_func = AVAILABLE_TOOLS[function_name]
                result = tool_func(**arguments)

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

    return _sanitize_agent_output(message.content)


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
        model=config.model,
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
