"""Step 2 · Tools that say what they are for (exam task 2.1).

Claude chooses a tool by reading its description, and these descriptions are
too thin: with "Retrieves customer information" and "Retrieves order details"
Claude will mix up the two look-ups.

TODO (step 2): rewrite each description to say what the tool does, what it
takes and in what format (C-1234, O-1234), what it returns, its edge cases
(several matches, no orders), and when to use it instead of the similar tool.

Done when: pytest tests/test_step2_tools.py passes.
"""

# Step 2 · Task 2.1: Claude picks a tool only from its description, so each one
# says what it does, its input formats, what it returns, edge cases, and when to
# use the similar tool instead.
TOOLS = [
    {
        "name": "get_customer",
        # Names lookup_order so Claude can tell "who is this person" from "what did they buy".
        "description": (
            "Finds a customer account and verifies who you are talking to. Use this first in every "
            "conversation, before any order look-up or refund. "
            "Input: give exactly one of email (e.g. dana@example.com, the best choice), customer_id "
            "(format C-1234, e.g. C-1001), or full name (only when the customer gives no email or ID). "
            "Returns the customer's customer_id, name and email. "
            "Edge cases: if no customer matches, you get a not-found error; ask the customer to check "
            "the details. A name can match more than one customer (multiple accounts share a name); "
            "then all matches come back and you must ask for the email or customer ID, never guess. "
            "This tool does not return orders: to see what a customer bought, or to look up an order "
            "ID like O-1234, use lookup_order instead."
        ),
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
        # Names get_customer so Claude never uses this to identify a person.
        "description": (
            "Looks up orders: one order by its ID, or every order of a customer you have already "
            "verified. Use it to check an order's item, amount, status (e.g. shipped, delivered) and "
            "dates before answering a question or refunding. "
            "Input: give order_id (format O-1234, e.g. O-5001) for one order, or customer_id "
            "(format C-1234) to list all of that customer's orders. "
            "Returns {order: {...}} for an order ID, or {orders: [...]} for a customer ID. "
            "Edge cases: an unknown order ID gives a not-found error. A customer with no orders gets "
            "an empty list; that is a real answer, not a failure, so tell the customer you see no "
            "orders. This tool does not identify or verify people: to find a customer by email, "
            "name or C- ID, use get_customer first, then pass the customer_id it returns here."
        ),
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
        # Says what must be checked first, so Claude never refunds an order it has not looked up.
        "description": (
            "Refunds money to a customer for one order. Use it only after get_customer has verified "
            "the customer and lookup_order has shown the order, so you know it is theirs and what it cost. "
            "Input: customer_id (format C-1234), order_id (format O-1234), amount in dollars (e.g. 120.00, "
            "no more than the order total) and a short reason in plain words. "
            "Returns a refund_id like R-0001 with the refunded details. "
            "Edge cases: the refund is refused if the order is not delivered yet, was delivered more than "
            "30 days ago, belongs to another customer, or the amount is above the order total; tell the "
            "customer why. Refunds above $500 need a person: use escalate_to_human instead of this tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "The verified customer's ID, e.g. C-1001."},
                "order_id": {"type": "string", "description": "The order to refund, e.g. O-5001."},
                "amount": {"type": "number", "description": "Dollars, e.g. 120.00."},
                "reason": {"type": "string", "description": "Why the customer wants the refund, e.g. 'arrived damaged'."},
            },
            "required": ["customer_id", "order_id", "amount", "reason"],
            "additionalProperties": False,
        },
    },
    {
        "name": "escalate_to_human",
        # Asks for a handoff a person can act on without reading the whole conversation.
        "description": (
            "Hands the case to a person on the tier-2 support team. Use it when the customer asks for a "
            "person, when a refund is above $500, or when policy or your tools cannot solve the issue. "
            "Do not use it just because the customer is frustrated if you can still solve the problem. "
            "Input: customer_id (format C-1234), root_cause (what actually went wrong), amount in dollars "
            "if money is involved (otherwise null), recommended_action (what the person should do next) "
            "and summary (what you already checked and told the customer). "
            "Returns a ticket_id like T-0001 and the queue it went to; tell the customer a person will "
            "follow up and give them the ticket ID."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "The verified customer's ID, e.g. C-1001."},
                "root_cause": {"type": "string", "description": "What went wrong, e.g. 'laptop arrived with a cracked screen'."},
                "amount": {"type": ["number", "null"], "description": "Dollars at stake, e.g. 640.00, or null if none."},
                "recommended_action": {"type": "string", "description": "What the person should do, e.g. 'approve a $640 refund'."},
                "summary": {"type": "string", "description": "What you checked and told the customer so far."},
            },
            "required": ["customer_id", "root_cause", "recommended_action", "summary"],
            "additionalProperties": False,
        },
    },
]
