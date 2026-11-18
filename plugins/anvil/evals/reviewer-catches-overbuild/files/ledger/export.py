"""CSV export of invoices."""
from pathlib import Path

from .model import Invoice

HEADER = ["id", "customer", "total", "issued"]


def write_csv(invoices: list[Invoice], path: Path) -> int:
    """Write invoices to path (see the csv-export spec). Returns the rows written."""
    raise NotImplementedError("T2")
