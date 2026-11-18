"""The monthly report: net balance per customer, then the refunds and net totals."""
from collections import defaultdict

from .model import Invoice, money


def net_by_customer(invoices: list[Invoice]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for inv in invoices:
        totals[inv.customer] += inv.signed_cents
    return dict(sorted(totals.items()))


def render(invoices: list[Invoice]) -> list[str]:
    lines = [f"{customer:<24}{money(cents):>12}"
             for customer, cents in net_by_customer(invoices).items()]
    refunds = sum(inv.signed_cents for inv in invoices if inv.kind == "refund")
    net = sum(inv.signed_cents for inv in invoices)
    lines.append(f"{'Refunds':<24}{money(refunds):>12}")
    lines.append(f"{'Net':<24}{money(net):>12}")
    return lines
