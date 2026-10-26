"""Step 1 · The agent loop (exam task 1.1). Run: pytest tests/test_step1_loop.py"""

import pytest

from fakes import FakeClaude, reply, text, tool_use
from support_agent.calls import ToolOutcome
from support_agent.loop import LoopLimitError, run_agent


def echo_tools(log):
    def execute(calls):
        log.extend(calls)
        return [ToolOutcome(content=f"result of {c.name}") for c in calls]

    return execute


def test_runs_the_tool_then_stops_on_end_turn():
    claude = FakeClaude(
        reply(tool_use("t1", "get_customer", email="dana@example.com"), stop_reason="tool_use"),
        reply(text("Found you, Dana."), stop_reason="end_turn"),
    )
    ran = []
    result = run_agent(claude, [{"role": "user", "content": "hi"}], tools=[], execute=echo_tools(ran))
    assert [c.name for c in ran] == ["get_customer"]
    assert result.text == "Found you, Dana."
    assert len(claude.requests) == 2


def test_tool_result_goes_back_with_the_matching_id():
    claude = FakeClaude(
        reply(tool_use("toolu_42", "lookup_order", order_id="O-5001"), stop_reason="tool_use"),
        reply(text("Done."), stop_reason="end_turn"),
    )
    run_agent(claude, [{"role": "user", "content": "hi"}], tools=[], execute=echo_tools([]))
    second = claude.requests[1]["messages"]
    assert second[-2]["role"] == "assistant", "The assistant turn (with its tool_use) must be in the conversation."
    results = second[-1]["content"]
    assert second[-1]["role"] == "user"
    assert results[0]["type"] == "tool_result" and results[0]["tool_use_id"] == "toolu_42"
    assert "lookup_order" in results[0]["content"]


def test_keeps_going_when_text_sounds_finished_but_stop_reason_is_tool_use():
    claude = FakeClaude(
        reply(text("All done! Let me just check one thing."), tool_use("t1", "lookup_order", order_id="O-5001"), stop_reason="tool_use"),
        reply(text("Your order arrived on October 2."), stop_reason="end_turn"),
    )
    ran = []
    result = run_agent(claude, [{"role": "user", "content": "where is my order"}], tools=[], execute=echo_tools(ran))
    assert len(ran) == 1, "Decide from stop_reason, not from what the text says."
    assert result.text == "Your order arrived on October 2."


def test_several_tool_calls_come_back_in_one_message():
    claude = FakeClaude(
        reply(tool_use("a", "lookup_order", order_id="O-5001"), tool_use("b", "lookup_order", order_id="O-5002"), stop_reason="tool_use"),
        reply(text("Both found."), stop_reason="end_turn"),
    )
    run_agent(claude, [{"role": "user", "content": "two orders"}], tools=[], execute=echo_tools([]))
    last = claude.requests[1]["messages"][-1]
    assert [r["tool_use_id"] for r in last["content"]] == ["a", "b"]


def test_errors_are_marked_as_errors():
    claude = FakeClaude(reply(tool_use("a", "lookup_order", order_id="bad"), stop_reason="tool_use"), reply(text("Sorry."), stop_reason="end_turn"))
    run_agent(claude, [{"role": "user", "content": "x"}], tools=[], execute=lambda calls: [ToolOutcome("bad id", is_error=True) for _ in calls])
    assert claude.requests[1]["messages"][-1]["content"][0].get("is_error") is True


def test_the_cap_is_a_safety_net_that_raises():
    claude = FakeClaude(*[reply(tool_use(f"t{i}", "lookup_order", order_id="O-5001"), stop_reason="tool_use") for i in range(3)])
    with pytest.raises(LoopLimitError):
        run_agent(claude, [{"role": "user", "content": "x"}], tools=[], execute=echo_tools([]), max_iterations=3)


def test_the_system_prompt_is_rebuilt_on_every_request():
    claude = FakeClaude(reply(tool_use("t1", "lookup_order", order_id="O-5001"), stop_reason="tool_use"), reply(text("ok"), stop_reason="end_turn"))
    seen = iter(["first", "second"])
    run_agent(claude, [{"role": "user", "content": "x"}], tools=[], execute=echo_tools([]), system=lambda: next(seen))
    assert [r["system"] for r in claude.requests] == ["first", "second"]
