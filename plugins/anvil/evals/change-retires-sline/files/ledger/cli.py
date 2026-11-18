import argparse
from pathlib import Path

from . import export, model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ledger")
    parser.add_argument("--data", default="data/invoices.json")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    exp = sub.add_parser("export")
    exp.add_argument("--csv", required=True, type=Path)
    args = parser.parse_args(argv)

    invoices = model.load(Path(args.data))
    if args.cmd == "export":
        export.write_csv(invoices, args.csv)
        return 0
    for inv in sorted(invoices, key=lambda i: i.issued):
        print(f"{inv.id}  {inv.issued.isoformat()}  {inv.customer:<20} {model.money(inv.total_cents):>10}")
    return 0
