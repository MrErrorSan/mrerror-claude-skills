"""Invoices, refunds and how they are loaded."""
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Invoice:
    id: str
    customer: str
    total_cents: int
    issued: date
    kind: str = "invoice"  # "invoice" or "refund"; refunds store a positive total

    @property
    def signed_cents(self) -> int:
        """What this entry adds to the customer's balance: refunds count negative."""
        return -self.total_cents if self.kind == "refund" else self.total_cents


def load(path: Path) -> list[Invoice]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Invoice(r["id"], r["customer"], r["total_cents"], date.fromisoformat(r["issued"]),
                    r.get("kind", "invoice"))
            for r in raw]


def money(cents: int) -> str:
    """1234 -> '12.34'."""
    return f"{cents // 100}.{cents % 100:02d}"
