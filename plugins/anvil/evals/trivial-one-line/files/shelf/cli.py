import argparse
import json
import os
from pathlib import Path

from . import messages


def _store() -> Path:
    return Path(os.environ.get("SHELF_FILE", Path.home() / ".shelf.json"))


def _load() -> list[dict]:
    path = _store()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="shelf")
    sub = parser.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("url")
    add.add_argument("--tag", action="append", default=[])
    sub.add_parser("list")
    args = parser.parse_args(argv)

    items = _load()
    if args.cmd == "add":
        items.insert(0, {"url": args.url, "tags": args.tag})
        _store().write_text(json.dumps(items, indent=2), encoding="utf-8")
        print(messages.SAVED.format(url=args.url))
    elif not items:
        print(messages.EMPTY)
    else:
        print(messages.LISTED.format(n=len(items)))
        for item in items:
            print(f"  {item['url']}  {' '.join('#' + t for t in item['tags'])}".rstrip())
    return 0
