"""A pretend company backend: customers, orders and refunds, in memory.

You do not need to change this file. It stands in for the real systems your
agent's tools would call, and it can be told to fail on purpose so you can
see how your agent copes (``backend.fail_next("lookup_order", "timeout")``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


class BackendTimeout(Exception):
    """The backend took too long. Trying again may work."""


class BackendDenied(Exception):
    """The caller is not allowed to do this."""


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    verified: bool = True


@dataclass
class Order:
    order_id: str
    customer_id: str
    item: str
    amount: float
    status: str
    ordered_on: date
    delivered_on: date | None
    # Fields a support agent rarely needs; they make raw results long on purpose.
    warehouse: str = "NJ-04"
    carrier: str = "UPS"
    tracking_number: str = "1Z999AA10123456784"
    tax: float = 0.0
    sku: str = ""
    gift_wrap: bool = False
    internal_notes: str = ""


@dataclass
class Backend:
    customers: dict[str, Customer] = field(default_factory=dict)
    orders: dict[str, Order] = field(default_factory=dict)
    refunds: list[dict] = field(default_factory=list)
    escalations: list[dict] = field(default_factory=list)
    _failures: dict[str, list[str]] = field(default_factory=dict)

    # --- test helpers -------------------------------------------------------
    def fail_next(self, operation: str, kind: str = "timeout", times: int = 1) -> None:
        """Make the next call(s) to ``operation`` fail with ``timeout`` or ``denied``."""
        self._failures.setdefault(operation, []).extend([kind] * times)

    def _maybe_fail(self, operation: str) -> None:
        queue = self._failures.get(operation)
        if queue:
            kind = queue.pop(0)
            if kind == "timeout":
                raise BackendTimeout(f"{operation} timed out")
            if kind == "denied":
                raise BackendDenied(f"{operation} is not allowed for this account")

    # --- the operations your tools call ----------------------------------
    def find_customers(self, *, email: str | None = None, customer_id: str | None = None, name: str | None = None) -> list[Customer]:
        self._maybe_fail("get_customer")
        if customer_id:
            c = self.customers.get(customer_id)
            return [c] if c else []
        if email:
            return [c for c in self.customers.values() if c.email.lower() == email.lower()]
        if name:
            return [c for c in self.customers.values() if c.name.lower() == name.lower()]
        return []

    def get_order(self, order_id: str) -> Order | None:
        self._maybe_fail("lookup_order")
        return self.orders.get(order_id)

    def orders_for(self, customer_id: str) -> list[Order]:
        self._maybe_fail("lookup_order")
        return [o for o in self.orders.values() if o.customer_id == customer_id]

    def refund(self, *, customer_id: str, order_id: str, amount: float, reason: str) -> dict:
        self._maybe_fail("process_refund")
        record = {"customer_id": customer_id, "order_id": order_id, "amount": amount, "reason": reason}
        self.refunds.append(record)
        return {"refund_id": f"R-{len(self.refunds):04d}", **record}

    def escalate(self, handoff: dict) -> dict:
        self._maybe_fail("escalate_to_human")
        self.escalations.append(handoff)
        return {"ticket_id": f"T-{len(self.escalations):04d}", "queue": "tier-2"}


def demo_backend() -> Backend:
    """The data every step's tests start from."""
    b = Backend()
    for c in [
        Customer("C-1001", "Dana Ortiz", "dana@example.com"),
        Customer("C-1002", "Sam Okafor", "sam@example.com"),
        Customer("C-1003", "Dana Ortiz", "dana.o@example.org"),
        Customer("C-1004", "Priya Nair", "priya@example.com"),
    ]:
        b.customers[c.customer_id] = c
    for o in [
        Order("O-5001", "C-1001", "Wireless headphones", 120.00, "delivered", date(2026, 9, 28), date(2026, 10, 2), sku="HD-220"),
        Order("O-5002", "C-1001", "Laptop", 640.00, "delivered", date(2026, 10, 1), date(2026, 10, 6), sku="LP-14"),
        Order("O-5003", "C-1002", "Phone case", 35.00, "shipped", date(2026, 10, 20), None, sku="PC-9"),
        Order("O-5004", "C-1002", "Desk lamp", 58.00, "delivered", date(2026, 7, 1), date(2026, 7, 5), sku="DL-3"),
    ]:
        b.orders[o.order_id] = o
    return b
