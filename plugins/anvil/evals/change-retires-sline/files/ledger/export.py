"""CSV export of invoices."""
import csv
from pathlib import Path

from .model import Invoice, money

HEADER = ["id", "customer", "total", "issued"]


def write_csv(invoices: list[Invoice], path: Path) -> int:
    """Write invoices to path, oldest first, with a header row. Returns the row count."""
    rows = sorted(invoices, key=lambda i: i.issued)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for inv in rows:
            writer.writerow([inv.id, inv.customer, money(inv.total_cents), inv.issued.isoformat()])
    return len(rows)
