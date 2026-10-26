"""Step 4 · A refund limit in code (exam tasks 1.5 and 1.4).

Hooks run before every tool call (toolbox.py, _guarded) and can stop it.
A rule in the prompt is followed most of the time; a hook every time.

TODO (step 4):
  verified_customer_first: block lookup_order and process_refund until
    get_customer has verified a customer (box.verified); a refund, or a
    lookup by customer ID, needs that particular customer verified.
  refund_limit: block process_refund above REFUND_LIMIT and redirect it to
    escalate_to_human with a full handoff (customer, root cause, amount,
    recommended action, summary), plus a customer_message to pass on.

Done when: pytest tests/test_step4_hooks.py passes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .calls import ToolCall
from .policy import REFUND_LIMIT  # noqa: F401  (used once step 4 is done)

if TYPE_CHECKING:
    from .toolbox import ToolBox


@dataclass
class HookDecision:
    allow: bool = True
    reason: str = ""
    category: str = "business"
    customer_message: str | None = None
    # A call to run instead of the blocked one (e.g. escalate_to_human).
    redirect: ToolCall | None = None


ALLOW = HookDecision()


def verified_customer_first(call: ToolCall, box: "ToolBox") -> HookDecision:
    """TODO (step 4)."""
    return ALLOW


def refund_limit(call: ToolCall, box: "ToolBox") -> HookDecision:
    """TODO (step 4)."""
    return ALLOW


# Order matters: verify first, then the limit.
DEFAULT_HOOKS = [verified_customer_first, refund_limit]
