import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Order:
    day: date
    region: str
    product: str
    amount_cents: int


def load(path: Path) -> list[Order]:
    with open(path, newline="", encoding="utf-8") as f:
        return [Order(date.fromisoformat(r["date"]), r["region"], r["product"],
                      int(r["amount_cents"])) for r in csv.DictReader(f)]
