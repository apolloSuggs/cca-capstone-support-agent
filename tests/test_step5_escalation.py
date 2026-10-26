"""Step 5 · Handing off to a person (exam tasks 5.2 and 1.4). Run: pytest tests/test_step5_escalation.py"""

import pytest

from fakes import FakeClaude
from support_agent.agent import SupportAgent
from support_agent.escalation import ESCALATION_RULES, build_handoff, wants_human


@pytest.mark.parametrize("text", ["I want to speak to a manager.", "Can I talk to a human please", "get me a real person", "Transfer me to an agent"])
def test_explicit_requests_for_a_person(text):
    assert wants_human(text)


@pytest.mark.parametrize("text", ["This is ridiculous, I've been charged twice!", "My order is late again", "I'm so frustrated with this headset"])
def test_frustration_alone_is_not_a_request_for_a_person(text):
    assert not wants_human(text)


def test_asking_for_a_person_escalates_straight_away(backend):
    agent = SupportAgent(FakeClaude(), backend)
    reply = agent.handle("I want to speak to a manager.")
    assert len(backend.escalations) == 1, "Honor it right away."
    assert agent.client.requests == [], "No investigating first: Claude is not even called."
    assert reply


def test_a_handoff_has_what_a_person_needs():
    h = build_handoff(customer_id="C-1001", root_cause="Refund of $640 is above the limit", amount=640, recommended_action="Approve the refund", summary="Laptop screen cracked on arrival")
    assert {"customer_id", "root_cause", "amount", "recommended_action", "summary"} <= set(h)
    with pytest.raises(ValueError):
        build_handoff(customer_id="C-1001", root_cause="", amount=None, recommended_action="x", summary="y")


def test_the_prompt_has_criteria_and_examples():
    rules = ESCALATION_RULES.lower()
    assert "escalate" in rules
    assert rules.count("example") >= 2, "Show at least two examples of when to escalate and when not to."
    assert "frustrat" in rules, "Say what to do when the customer is frustrated but the issue is solvable."
    assert "more than one" in rules or "multiple" in rules, "Say what to do when several customers match."
