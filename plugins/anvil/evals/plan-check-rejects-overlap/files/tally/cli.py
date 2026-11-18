import argparse
from pathlib import Path

from . import orders, registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tally")
    parser.add_argument("report", choices=sorted(registry.REPORTS))
    parser.add_argument("--data", default="data/orders.csv")
    args = parser.parse_args(argv)
    for key, cents in registry.get(args.report)(orders.load(Path(args.data))):
        print(f"{key}  {cents / 100:.2f}")
    return 0
