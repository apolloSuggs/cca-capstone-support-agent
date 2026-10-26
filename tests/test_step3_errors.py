"""Step 3 · Errors the agent can act on (exam task 2.2). Run: pytest tests/test_step3_errors.py"""

import json

from support_agent.calls import ToolCall
from support_agent.toolbox import ToolBox


def run(box, tool, **input):
    return box.run(ToolCall(id="t", name=tool, input=input))


def err(outcome):
    assert outcome.is_error, f"Expected an error, got {outcome.content}"
    data = json.loads(outcome.content)
    for key in ("errorCategory", "isRetryable", "message"):
        assert key in data, f"Every error needs {key}."
    return data


def test_a_badly_formed_order_id_is_a_validation_error(backend):
    data = err(run(ToolBox(backend, hooks=[]), "lookup_order", order_id="12345"))
    assert data["errorCategory"] == "validation" and data["isRetryable"] is False


def test_a_timeout_is_retried_before_giving_up(backend):
    backend.fail_next("lookup_order", "timeout", times=1)
    outcome = run(ToolBox(backend, hooks=[]), "lookup_order", order_id="O-5001")
    assert not outcome.is_error, "One timeout should be retried and then succeed."
    assert json.loads(outcome.content)["order"]["order_id"] == "O-5001"


def test_a_timeout_that_keeps_happening_is_transient_and_retryable(backend):
    backend.fail_next("lookup_order", "timeout", times=10)
    data = err(run(ToolBox(backend, hooks=[]), "lookup_order", order_id="O-5001"))
    assert data["errorCategory"] == "transient" and data["isRetryable"] is True


def test_a_policy_refusal_is_a_business_error_with_words_for_the_customer(backend):
    box = ToolBox(backend, hooks=[])
    data = err(run(box, "process_refund", customer_id="C-1002", order_id="O-5004", amount=58.0, reason="broken"))
    assert data["errorCategory"] == "business" and data["isRetryable"] is False
    assert data.get("customerMessage"), "Give the agent a sentence it can pass on to the customer."
    assert backend.refunds == []


def test_permission_errors_are_not_retried(backend):
    backend.fail_next("lookup_order", "denied")
    data = err(run(ToolBox(backend, hooks=[]), "lookup_order", order_id="O-5001"))
    assert data["errorCategory"] == "permission" and data["isRetryable"] is False


def test_no_orders_is_an_answer_not_an_error(backend):
    outcome = run(ToolBox(backend, hooks=[]), "lookup_order", customer_id="C-1004")
    assert not outcome.is_error
    assert json.loads(outcome.content)["orders"] == []


def test_several_matching_customers_are_all_returned(backend):
    outcome = run(ToolBox(backend, hooks=[]), "get_customer", name="Dana Ortiz")
    assert not outcome.is_error
    assert len(json.loads(outcome.content)["matches"]) == 2, "Return every match so the agent asks; never pick one."


def test_a_good_refund_works(backend):
    box = ToolBox(backend, hooks=[])
    outcome = run(box, "process_refund", customer_id="C-1001", order_id="O-5001", amount=120.0, reason="broken")
    assert not outcome.is_error and backend.refunds[0]["order_id"] == "O-5001"
