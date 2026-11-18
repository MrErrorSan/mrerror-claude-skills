import argparse
import csv
from pathlib import Path

from . import model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ledger")
    parser.add_argument("--data", default="data/invoices.json")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    exp = sub.add_parser("export")
    exp.add_argument("--csv", type=Path, required=True)
    args = parser.parse_args(argv)

    invoices = sorted(model.load(Path(args.data)), key=lambda i: i.issued)
    if args.cmd == "export":
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";", lineterminator="\n")
            w.writerow(["id", "customer", "total", "issued"])
            for inv in invoices:
                w.writerow([inv.id, inv.customer, model.money(inv.total_cents).replace(".", ","),
                            inv.issued.isoformat()])
        return 0
    for inv in invoices:
        print(f"{inv.id}  {inv.issued.isoformat()}  {inv.customer:<20} {model.money(inv.total_cents):>10}")
    return 0
