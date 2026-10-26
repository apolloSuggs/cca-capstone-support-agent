"""Step 2 · Tools that say what they are for (exam task 2.1). Run: pytest tests/test_step2_tools.py

These tests check that each description carries what Claude needs to choose
well. They cannot judge your wording; read your descriptions out loud and ask
whether someone new could pick the right tool from them alone.
"""

from support_agent.tools import TOOLS

BY_NAME = {t["name"]: t for t in TOOLS}


def test_the_four_tools_exist_with_schemas():
    assert set(BY_NAME) == {"get_customer", "lookup_order", "process_refund", "escalate_to_human"}
    for t in TOOLS:
        assert t["input_schema"]["type"] == "object"


def test_descriptions_are_more_than_a_line():
    for t in TOOLS:
        assert len(t["description"]) >= 250, f"{t['name']}: say what it does, its inputs and formats, what it returns, edge cases, and when to use it."


def test_the_look_ups_point_at_each_other():
    assert "lookup_order" in BY_NAME["get_customer"]["description"], "Say when to use lookup_order instead."
    assert "get_customer" in BY_NAME["lookup_order"]["description"], "Say when to use get_customer instead."


def test_input_formats_are_described():
    assert "C-" in BY_NAME["get_customer"]["description"]
    assert "O-" in BY_NAME["lookup_order"]["description"]


def test_edge_cases_are_described():
    gc = BY_NAME["get_customer"]["description"].lower()
    assert "more than one" in gc or "multiple" in gc, "What happens when a name matches several customers?"
    lo = BY_NAME["lookup_order"]["description"].lower()
    assert "no orders" in lo or "empty" in lo, "What does a customer with no orders look like?"


def test_refund_requires_everything_it_needs():
    assert set(BY_NAME["process_refund"]["input_schema"]["required"]) >= {"customer_id", "order_id", "amount"}


def test_the_handoff_asks_for_what_a_person_needs():
    req = set(BY_NAME["escalate_to_human"]["input_schema"].get("required", []))
    assert {"customer_id", "root_cause", "recommended_action"} <= req
