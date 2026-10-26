"""Step 6 · Long, messy conversations (exam tasks 1.6 and 5.1). Run: pytest tests/test_step6_context.py"""

import json

from fakes import FakeClaude, reply, text, tool_use
from support_agent.agent import SupportAgent
from support_agent.calls import ToolCall
from support_agent.context import ISSUE_RULES, CaseFacts, compact_history, trim_order
from support_agent.toolbox import ToolBox


def test_order_results_are_trimmed_to_what_the_case_needs(backend):
    box = ToolBox(backend)
    box.execute([ToolCall("a", "get_customer", {"email": "dana@example.com"})])
    [outcome] = box.execute([ToolCall("b", "lookup_order", {"order_id": "O-5001"})])
    order = json.loads(outcome.content)["order"]
    assert "tracking_number" not in order and "internal_notes" not in order
    assert {"order_id", "amount", "status"} <= set(order)
    assert trim_order({"order_id": "O-1", "amount": 1, "warehouse": "x"}) == {"order_id": "O-1", "amount": 1}


def test_case_facts_keep_exact_numbers(backend):
    box = ToolBox(backend)
    box.execute([ToolCall("a", "get_customer", {"email": "dana@example.com"}), ToolCall("b", "lookup_order", {"customer_id": "C-1001"})])
    block = box.facts.render()
    assert "C-1001" in block and "O-5002" in block and "$640.00" in block


def test_the_facts_go_with_every_request(backend):
    claude = FakeClaude(
        reply(tool_use("a", "get_customer", email="dana@example.com"), stop_reason="tool_use"),
        reply(tool_use("b", "lookup_order", order_id="O-5002"), stop_reason="tool_use"),
        reply(text("Your laptop order O-5002 was $640."), stop_reason="end_turn"),
    )
    agent = SupportAgent(claude, backend)
    agent.handle("I'm dana@example.com, what did my laptop cost?")
    assert "O-5002" in claude.requests[2]["system"] and "$640.00" in claude.requests[2]["system"]


def test_compacting_the_history_never_starts_on_an_orphan_tool_result():
    msgs = [{"role": "user", "content": "hi"}]
    for i in range(6):
        msgs.append({"role": "assistant", "content": [{"type": "tool_use", "id": f"t{i}", "name": "x", "input": {}}]})
        msgs.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{i}", "content": "r"}]})
    short = compact_history(msgs, keep_last=5)
    assert len(short) < len(msgs)
    first_user_with_results = next(m for m in short if m["role"] == "user" and isinstance(m["content"], list))
    i = short.index(first_user_with_results)
    assert short[i - 1]["role"] == "assistant", "A tool_result must follow the assistant turn that asked for it."


def test_facts_survive_compaction(backend):
    facts = CaseFacts()
    box = ToolBox(backend, facts=facts)
    box.execute([ToolCall("a", "get_customer", {"email": "dana@example.com"}), ToolCall("b", "lookup_order", {"order_id": "O-5001"})])
    compact_history([{"role": "user", "content": str(i)} for i in range(30)], keep_last=4)
    assert "$120.00" in facts.render()


def test_the_prompt_says_how_to_handle_several_problems():
    rules = ISSUE_RULES.lower()
    assert "each" in rules and ("separately" in rules or "one by one" in rules)
    assert "together" in rules or "one reply" in rules
