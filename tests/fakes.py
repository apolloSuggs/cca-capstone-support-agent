"""A scripted stand-in for Claude, so the tests run without an API key and give the same result every time."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any


def text(t: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=t)


def tool_use(id: str, name: str, **input: Any) -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=id, name=name, input=input)


def reply(*blocks: SimpleNamespace, stop_reason: str) -> SimpleNamespace:
    return SimpleNamespace(content=list(blocks), stop_reason=stop_reason)


class FakeClaude:
    """Returns the scripted replies in order and records every request."""

    def __init__(self, *replies: SimpleNamespace):
        self.replies = list(replies)
        self.requests: list[dict[str, Any]] = []
        self.messages = self

    def create(self, **kwargs: Any) -> SimpleNamespace:
        # Copy the messages: the loop keeps appending to the same list.
        self.requests.append({**kwargs, "messages": list(kwargs.get("messages", []))})
        if not self.replies:
            raise AssertionError("Claude was called more times than this test scripted.")
        return self.replies.pop(0)
