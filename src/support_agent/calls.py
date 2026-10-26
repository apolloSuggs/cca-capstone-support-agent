"""Small shared types. You do not need to change this file."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """One tool Claude asked for: its id, name and input."""

    id: str
    name: str
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolOutcome:
    """What a tool returns to Claude: text (usually JSON) and whether it failed."""

    content: str
    is_error: bool = False
