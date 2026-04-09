"""AI Routing Schemas for dwriter.

This module defines the routing logic for categorizing user intents
into functional domains.
"""

from typing import Literal

from pydantic import BaseModel


class ActionRouter(BaseModel):
    """Categorizes a user request into a specific functional domain.

    Attributes:
        category: The identified functional area of the request.
    """

    category: Literal[
        "reflection",
        "analytics",
        "context_restore",
        "unknown",
    ]
