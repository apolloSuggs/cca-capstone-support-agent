"""Step 3 · Errors the agent can act on (exam task 2.2).

Right now every failure comes back as "Operation failed". The agent cannot
tell a timeout (try again) from a bad order number (ask for the right one)
from a policy refusal (explain it, never retry).

TODO (step 3): make tool_error return JSON with
  errorCategory     one of CATEGORIES
  isRetryable       true only for transient errors (unless told otherwise)
  message           what happened, in plain words
  customerMessage   (optional) a sentence the agent can pass on, for policy refusals
Then use it in toolbox.py (see the TODOs there).

Done when: pytest tests/test_step3_errors.py passes.
"""

from __future__ import annotations

import json
from typing import Any

from .calls import ToolOutcome

# transient: a timeout or outage; trying again may work.
# validation: the input is wrong (a badly formed ID); fix the input, do not retry it unchanged.
# business: a policy says no; explain it to the customer, never retry.
# permission: this account may not do it; do not retry.
CATEGORIES = ("transient", "validation", "business", "permission")


def ok(data: Any) -> ToolOutcome:
    """A successful result. An empty list is a successful answer too."""
    return ToolOutcome(content=json.dumps(data, default=str), is_error=False)


def tool_error(category: str, message: str, *, retryable: bool | None = None, customer_message: str | None = None) -> ToolOutcome:
    """TODO (step 3): return a structured error instead of a generic one."""
    return ToolOutcome(content="Operation failed", is_error=True)
