"""Step 6 · Long, messy conversations (exam tasks 1.6 and 5.1).

Customers bring several problems at once and keep talking. The exact facts
(order numbers, amounts, dates, statuses) must not get lost as the chat
grows or is trimmed.

TODO (step 6):
  trim_order: keep only ORDER_FIELDS (raw orders carry tracking numbers,
    warehouses and notes that only cost tokens).
  CaseFacts.record: after each successful tool, keep the verified customer,
    every order seen, refunds and escalation tickets, exactly.
  CaseFacts.render: one block listing them (amounts as $640.00).
    agent.py already puts it at the top of the system prompt on every request.
  compact_history: drop older turns, keeping the last ``keep_last``, and never
    start on a tool_result whose tool_use was dropped.
  ISSUE_RULES: tell the agent to list each problem, work on each separately
    and answer them together.

Done when: pytest tests/test_step6_context.py passes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .calls import ToolCall, ToolOutcome

# The order fields a support conversation needs; the rest only costs tokens.
ORDER_FIELDS = ("order_id", "item", "amount", "status", "ordered_on", "delivered_on")


def trim_order(order: dict[str, Any]) -> dict[str, Any]:
    """TODO (step 6)."""
    return order


@dataclass
class CaseFacts:
    """Transactional facts, kept exactly as the tools returned them."""

    customer_id: str | None = None
    orders: dict[str, dict[str, Any]] = field(default_factory=dict)
    refunds: list[dict[str, Any]] = field(default_factory=list)
    escalations: list[str] = field(default_factory=list)

    def record(self, call: ToolCall, outcome: ToolOutcome) -> None:
        """TODO (step 6)."""

    def render(self) -> str:
        """TODO (step 6)."""
        return "## Case facts\n(none recorded yet)"


def system_with_facts(base: str, facts: CaseFacts) -> str:
    """Facts first, so they sit where the model reads most reliably."""
    return f"{facts.render()}\n\n{base}"


def compact_history(messages: list[dict[str, Any]], keep_last: int = 6) -> list[dict[str, Any]]:
    """TODO (step 6)."""
    return messages


ISSUE_RULES = """\
## Messages with several problems
TODO (step 6)
"""
