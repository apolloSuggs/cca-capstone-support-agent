"""Step 2 · Tools that say what they are for (exam task 2.1).

Claude chooses a tool by reading its description, and these descriptions are
too thin: with "Retrieves customer information" and "Retrieves order details"
Claude will mix up the two look-ups.

TODO (step 2): rewrite each description to say what the tool does, what it
takes and in what format (C-1234, O-1234), what it returns, its edge cases
(several matches, no orders), and when to use it instead of the similar tool.

Done when: pytest tests/test_step2_tools.py passes.
"""

TOOLS = [
    {
        "name": "get_customer",
        "description": "Retrieves customer information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "The customer's email address, e.g. dana@example.com."},
                "customer_id": {"type": "string", "description": "A customer ID like C-1001."},
                "name": {"type": "string", "description": "Full name, only when no email or ID is given."},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "lookup_order",
        "description": "Retrieves order details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "An order ID like O-5001."},
                "customer_id": {"type": "string", "description": "A verified customer ID like C-1001, to list their orders."},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "process_refund",
        "description": "Processes a refund.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "order_id": {"type": "string"},
                "amount": {"type": "number", "description": "Dollars, e.g. 120.00."},
                "reason": {"type": "string"},
            },
            "required": ["customer_id", "order_id", "amount", "reason"],
            "additionalProperties": False,
        },
    },
    {
        "name": "escalate_to_human",
        "description": "Escalates to a human.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "root_cause": {"type": "string"},
                "amount": {"type": ["number", "null"]},
                "recommended_action": {"type": "string"},
                "summary": {"type": "string"},
            },
            "required": ["customer_id", "root_cause", "recommended_action", "summary"],
            "additionalProperties": False,
        },
    },
]
