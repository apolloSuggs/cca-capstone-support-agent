"""Step 4 · A refund limit in code (exam tasks 1.5 and 1.4). Run: pytest tests/test_step4_hooks.py"""

import json

from support_agent.calls import ToolCall
from support_agent.toolbox import ToolBox


def call(name, **input):
    return ToolCall(id=f"t-{name}", name=name, input=input)


def verified_box(backend):
    box = ToolBox(backend)
    box.execute([call("get_customer", email="dana@example.com")])
    return box


def test_a_refund_over_the_limit_never_reaches_the_backend(backend):
    box = verified_box(backend)
    [outcome] = box.execute([call("process_refund", customer_id="C-1001", order_id="O-5002", amount=640.0, reason="screen cracked")])
    assert outcome.is_error
    assert backend.refunds == [], "The hook must stop the refund before it runs."


def test_a_blocked_refund_goes_to_a_person(backend):
    box = verified_box(backend)
    box.execute([call("process_refund", customer_id="C-1001", order_id="O-5002", amount=640.0, reason="screen cracked")])
    assert len(backend.escalations) == 1
    handoff = backend.escalations[0]
    assert handoff["customer_id"] == "C-1001" and handoff["amount"] == 640.0


def test_a_refund_within_the_limit_goes_through(backend):
    box = verified_box(backend)
    [outcome] = box.execute([call("process_refund", customer_id="C-1001", order_id="O-5001", amount=120.0, reason="broken")])
    assert not outcome.is_error, outcome.content
    assert len(backend.refunds) == 1


def test_no_refund_before_the_customer_is_verified(backend):
    box = ToolBox(backend)
    [outcome] = box.execute([call("process_refund", customer_id="C-1001", order_id="O-5001", amount=120.0, reason="broken")])
    assert outcome.is_error and backend.refunds == []
    assert json.loads(outcome.content)["isRetryable"] is False


def test_no_order_lookup_before_the_customer_is_verified(backend):
    box = ToolBox(backend)
    [outcome] = box.execute([call("lookup_order", order_id="O-5001")])
    assert outcome.is_error, "Verify with get_customer before any order lookup."


def test_a_refund_for_a_different_customer_is_blocked(backend):
    box = verified_box(backend)
    [outcome] = box.execute([call("process_refund", customer_id="C-1002", order_id="O-5003", amount=35.0, reason="x")])
    assert outcome.is_error and backend.refunds == []
