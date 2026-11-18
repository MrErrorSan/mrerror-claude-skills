import argparse
from pathlib import Path

from . import model, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ledger")
    parser.add_argument("--data", default="data/invoices.json")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("report")
    args = parser.parse_args(argv)

    invoices = model.load(Path(args.data))
    if args.cmd == "report":
        print("\n".join(report.render(invoices)))
        return 0
    for inv in sorted(invoices, key=lambda i: i.issued):
        print(f"{inv.id}  {inv.issued.isoformat()}  {inv.customer:<20} {model.money(inv.total_cents):>10}  {inv.kind}")
    return 0
