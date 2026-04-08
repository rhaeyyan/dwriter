"""AI Engine for dwriter.

This module provides an interface for interacting with the AI provider
using instructor and the OpenAI-compatible API.
"""

from typing import Any

import instructor
from openai import OpenAI

from dwriter.config import AIConfig


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
        "Do NOT include the field names like 'properties' or 'type' in your root object. "
        "Just the raw data values matching the requested structure."
    )
