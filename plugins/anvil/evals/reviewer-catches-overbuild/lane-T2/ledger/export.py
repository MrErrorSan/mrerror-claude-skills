"""CSV export of invoices."""
import csv
import io
from pathlib import Path

from .model import Invoice, money

HEADER = ["id", "customer", "total", "issued"]


def format_row(values, delimiter=",", quote_all=False, strip=True, upper_ids=False):
    """Format one row as a CSV line. The options cover other export targets later."""
    if upper_ids and values:
        values = [str(values[0]).upper(), *values[1:]]
    if strip:
        values = [str(v).strip() for v in values]
    buf = io.StringIO()
    quoting = csv.QUOTE_ALL if quote_all else csv.QUOTE_MINIMAL
    csv.writer(buf, delimiter=delimiter, quoting=quoting, lineterminator="\n").writerow(values)
    return buf.getvalue()


def write_csv(invoices: list[Invoice], path: Path) -> int:
    """Write invoices to path (see the csv-export spec). Returns the rows written."""
    if not invoices:
        return 0
    rows = sorted(invoices, key=lambda i: i.issued)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(format_row(HEADER))
        for inv in rows:
            f.write(format_row([inv.id, inv.customer, money(inv.total_cents),
                                inv.issued.isoformat()]))
    return len(rows)
