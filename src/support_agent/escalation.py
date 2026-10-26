"""Step 5 · Handing off to a person (exam tasks 5.2 and 1.4).

When to escalate is mostly judgment, so the rules and examples go in the
system prompt (ESCALATION_RULES). Two parts are code: a customer who asks
for a person gets one straight away (agent.py calls wants_human before
anything else), and the handoff carries everything a person needs.

TODO (step 5):
  wants_human: true for an explicit request for a person ("talk to a human",
    "get me a manager"), false for frustration alone.
  build_handoff: raise ValueError when customer_id, root_cause,
    recommended_action or summary is empty.
  ESCALATION_RULES: when to escalate and when not to, with at least two
    examples; what to do when the customer is frustrated but the issue is
    solvable; what to do when several customers match.

Done when: pytest tests/test_step5_escalation.py passes.
"""

from __future__ import annotations


def wants_human(text: str) -> bool:
    """TODO (step 5)."""
    return False


def build_handoff(*, customer_id: str, root_cause: str, amount: float | None, recommended_action: str, summary: str) -> dict:
    """The handoff a person can act on without the transcript. TODO (step 5): refuse an incomplete one."""
    return {"customer_id": customer_id, "root_cause": root_cause, "amount": amount, "recommended_action": recommended_action, "summary": summary}


ESCALATION_RULES = """\
## When to hand the case to a person
TODO (step 5)
"""
