from collections import defaultdict


def run(orders) -> list[tuple[str, int]]:
    totals = defaultdict(int)
    for o in orders:
        totals[o.day.isoformat()] += o.amount_cents
    return sorted(totals.items())
