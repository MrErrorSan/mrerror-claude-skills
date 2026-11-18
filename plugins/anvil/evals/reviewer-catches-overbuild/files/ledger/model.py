"""Invoices and how they are loaded."""
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


def load(path: Path) -> list[Invoice]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Invoice(r["id"], r["customer"], r["total_cents"], date.fromisoformat(r["issued"]))
            for r in raw]


def money(cents: int) -> str:
    """1234 -> '12.34'."""
    return f"{cents // 100}.{cents % 100:02d}"
