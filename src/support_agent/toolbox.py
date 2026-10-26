"""Runs the agent's tools against the backend.

TODO (step 3, exam task 2.2), in this file:
  - Retry a BackendTimeout here (up to ``self.retries`` times) before
    returning a transient error, so one hiccup never reaches Claude.
  - Check ID formats (ORDER_ID, CUSTOMER_ID) and return validation errors.
  - In _process_refund, refuse with a business error (and a customerMessage)
    when the order is not delivered, or was delivered more than
    RETURN_WINDOW_DAYS before today; and check the order belongs to the
    customer and the amount is within the order total.
  - A customer with no orders is an empty list, not an error.
  - When a name matches several customers, return them all with a note to
    ask for the email or ID; never pick one.
Step 4 fills in hooks.py (they already run in _guarded below).
Step 6 fills in trim_order and CaseFacts in context.py (already called here).
"""

from __future__ import annotations

import re
from dataclasses import asdict
from datetime import date
from typing import Callable

from .backend import Backend, BackendDenied, BackendTimeout
from .calls import ToolCall, ToolOutcome
from .context import CaseFacts, trim_order
from .errors import ok, tool_error
from .policy import RETURN_WINDOW_DAYS, TODAY  # noqa: F401  (used once step 3 is done)

ORDER_ID = re.compile(r"^O-\d{4}$")
CUSTOMER_ID = re.compile(r"^C-\d{4}$")


class ToolBox:
    def __init__(self, backend: Backend, *, today: date = TODAY, hooks: list[Callable] | None = None, facts: CaseFacts | None = None, retries: int = 2):
        from .hooks import DEFAULT_HOOKS

        self.backend = backend
        self.today = today
        self.hooks = DEFAULT_HOOKS if hooks is None else hooks
        self.facts = facts if facts is not None else CaseFacts()
        self.retries = retries
        self.verified: set[str] = set()

    # Called by the agent loop with every tool call in one response.
    def execute(self, calls: list[ToolCall]) -> list[ToolOutcome]:
        outcomes = []
        for call in calls:
            outcome = self._guarded(call)
            self.facts.record(call, outcome)
            outcomes.append(outcome)
        return outcomes

    def _guarded(self, call: ToolCall) -> ToolOutcome:
        """Runs every hook first (step 4); a hook that says no stops the call."""
        for hook in self.hooks:
            decision = hook(call, self)
            if not decision.allow:
                note = decision.reason
                if decision.redirect is not None:
                    ticket = self.run(decision.redirect)
                    note += f" It was sent to a person instead: {ticket.content}"
                return tool_error(decision.category, note, retryable=False, customer_message=decision.customer_message)
        return self.run(call)

    def run(self, call: ToolCall) -> ToolOutcome:
        handler = getattr(self, f"_{call.name}", None)
        if handler is None:
            return tool_error("validation", f"There is no tool called {call.name}.")
        try:
            return handler(**call.input)
        except (BackendTimeout, BackendDenied, TypeError) as e:
            # TODO (step 3): retry timeouts, and tell the kinds of failure apart.
            return tool_error("transient", str(e))

    # --- tools ---------------------------------------------------------------
    def _get_customer(self, email: str | None = None, customer_id: str | None = None, name: str | None = None) -> ToolOutcome:
        found = self.backend.find_customers(email=email, customer_id=customer_id, name=name)
        if not found:
            return tool_error("validation", "Customer not found.")
        c = found[0]  # TODO (step 3): several matches means ask, not pick.
        self.verified.add(c.customer_id)
        return ok({"customer": {"customer_id": c.customer_id, "name": c.name, "email": c.email}})

    def _lookup_order(self, order_id: str | None = None, customer_id: str | None = None) -> ToolOutcome:
        if order_id:
            order = self.backend.get_order(order_id)
            if order is None:
                return tool_error("validation", "Order not found.")
            return ok({"order": trim_order(asdict(order))})
        orders = self.backend.orders_for(customer_id or "")
        if not orders:
            return tool_error("validation", "No orders.")  # TODO (step 3): no orders is an answer.
        return ok({"orders": [trim_order(asdict(o)) for o in orders]})

    def _process_refund(self, customer_id: str, order_id: str, amount: float, reason: str) -> ToolOutcome:
        # TODO (step 3): check ownership, amount, delivery and the return window first.
        return ok(self.backend.refund(customer_id=customer_id, order_id=order_id, amount=float(amount), reason=reason))

    def _escalate_to_human(self, customer_id: str, root_cause: str, recommended_action: str, summary: str, amount: float | None = None) -> ToolOutcome:
        from .escalation import build_handoff

        handoff = build_handoff(customer_id=customer_id, root_cause=root_cause, amount=amount, recommended_action=recommended_action, summary=summary)
        return ok(self.backend.escalate(handoff))
