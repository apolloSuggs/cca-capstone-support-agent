"""Step 1 · The agent loop (exam task 1.1).

Send the conversation to Claude, run every tool it asks for, add the results
to the conversation, and go again. Stop when Claude's stop reason says the
turn is over, never because a reply sounds finished.

Done when: pytest tests/test_step1_loop.py passes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable

from .calls import ToolCall, ToolOutcome

MODEL = os.environ.get("CAPSTONE_MODEL", "claude-opus-5-5")
MAX_TOKENS = 16000


class LoopLimitError(RuntimeError):
    """The safety cap was reached. A cap is a backstop, not the way the loop ends."""


@dataclass
class AgentResult:
    text: str
    messages: list[dict[str, Any]]
    tool_calls: list[ToolCall] = field(default_factory=list)
    iterations: int = 0


def run_agent(
    client: Any,
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]],
    execute: Callable[[list[ToolCall]], list[ToolOutcome]],
    system: str | Callable[[], str] = "",
    model: str = MODEL,
    max_iterations: int = 25,
) -> AgentResult:
    """Run the conversation until Claude ends its turn.

    ``execute`` runs a batch of tool calls and returns one outcome per call,
    in order. ``system`` may be a function: call it before every request so
    it is rebuilt each time (step 6 puts the case facts there).

    TODO (step 1):
      1. Call client.messages.create(model=..., max_tokens=..., system=..., tools=..., messages=...).
      2. Append Claude's reply to ``messages`` as an assistant turn (its full content, tool_use blocks included).
      3. If response.stop_reason is not "tool_use", return an AgentResult with the reply's text.
      4. Otherwise turn every tool_use block into a ToolCall, run them all with ``execute``,
         and append ONE user message holding a tool_result per call
         ({"type": "tool_result", "tool_use_id": ..., "content": ..., "is_error": ...}).
      5. Go again. After ``max_iterations`` rounds, raise LoopLimitError.
    Do not decide to stop by reading the reply's text.
    """
    raise NotImplementedError("Step 1: write the agent loop. Run /cca-prep-studio:next-step in Claude Code for help.")
