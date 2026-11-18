import argparse
import csv
import json
from datetime import date
from pathlib import Path

from . import model


def _iso(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}")


def _rows(invoices):
    for inv in sorted(invoices, key=lambda i: i.issued):
        yield {"id": inv.id, "customer": inv.customer, "total": model.money(inv.total_cents),
               "issued": inv.issued.isoformat()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ledger")
    parser.add_argument("--data", default="data/invoices.json")
    sub = parser.add_subparsers(dest="cmd", required=True)
    lst = sub.add_parser("list")
    lst.add_argument("--since", type=_iso)
    exp = sub.add_parser("export")
    exp.add_argument("--csv", type=Path)
    exp.add_argument("--json", type=Path)
    args = parser.parse_args(argv)

    invoices = model.load(Path(args.data))
    if args.cmd == "export":
        if not (args.csv or args.json):
            parser.error("export needs --csv and/or --json")
        rows = list(_rows(invoices))
        if args.csv:
            with args.csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["id", "customer", "total", "issued"], lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
        if args.json:
            args.json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        return 0
    for inv in sorted(invoices, key=lambda i: i.issued):
        if args.since and inv.issued < args.since:
            continue
        print(f"{inv.id}  {inv.issued.isoformat()}  {inv.customer:<20} {model.money(inv.total_cents):>10}")
    return 0
