"""Company policy the agent works under. You do not need to change this file."""

from datetime import date

# Refunds above this amount need a person (step 4 enforces it in code).
REFUND_LIMIT = 500.00
# Delivered orders can be refunded for this many days.
RETURN_WINDOW_DAYS = 30
# "Today" for the demo data and the tests, so results do not change with the calendar.
TODAY = date(2026, 10, 25)
