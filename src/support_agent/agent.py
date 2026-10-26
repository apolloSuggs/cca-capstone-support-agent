"""The support agent: the loop, the tools, the hooks and the case facts, wired together."""

from __future__ import annotations

from typing import Any

from .backend import Backend, demo_backend
from .calls import ToolCall
from .context import CaseFacts, compact_history, system_with_facts
from .escalation import wants_human
from .loop import AgentResult, run_agent
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS
from .toolbox import ToolBox


class SupportAgent:
    def __init__(self, client: Any, backend: Backend | None = None, *, keep_last: int = 20):
        self.client = client
        self.backend = backend or demo_backend()
        self.facts = CaseFacts()
        self.toolbox = ToolBox(self.backend, facts=self.facts)
        self.messages: list[dict[str, Any]] = []
        self.keep_last = keep_last

    def handle(self, text: str) -> str:
        if wants_human(text):
            # Honor the request right away: no investigating first.
            ticket = self.toolbox.run(
                ToolCall(
                    id="human-request",
                    name="escalate_to_human",
                    input={
                        "customer_id": self.facts.customer_id or "unverified",
                        "root_cause": "The customer asked for a person.",
                        "amount": None,
                        "recommended_action": "Pick up the conversation with the customer.",
                        "summary": text,
                    },
                )
            )
            return f"Of course. I've passed you to a person on our team; they'll pick this up shortly. ({ticket.content})"
        self.messages = compact_history(self.messages, self.keep_last)
        self.messages.append({"role": "user", "content": text})
        result: AgentResult = run_agent(
            self.client,
            self.messages,
            tools=TOOLS,
            execute=self.toolbox.execute,
            system=lambda: system_with_facts(SYSTEM_PROMPT, self.facts),
        )
        return result.text
