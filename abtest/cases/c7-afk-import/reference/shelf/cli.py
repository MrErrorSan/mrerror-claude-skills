import argparse
import json
import os
import sys
from html.parser import HTMLParser
from pathlib import Path

from . import messages


def _store() -> Path:
    return Path(os.environ.get("SHELF_FILE", Path.home() / ".shelf.json"))


def _load() -> list[dict]:
    path = _store()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


class _Bookmarks(HTMLParser):
    """Netscape bookmark export: <H3> names a folder, the next <DL> holds its contents."""

    def __init__(self):
        super().__init__()
        self.folders, self.pending, self.found, self._in_h3 = [], None, [], False

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self._in_h3, self.pending = True, ""
        elif tag == "dl":
            self.folders.append(self.pending)
            self.pending = None
        elif tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.found.append({"url": href, "tags": [f for f in self.folders if f]})

    def handle_endtag(self, tag):
        if tag == "h3":
            self._in_h3 = False
        elif tag == "dl" and self.folders:
            self.folders.pop()

    def handle_data(self, data):
        if self._in_h3:
            self.pending += data.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="shelf")
    sub = parser.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("url")
    add.add_argument("--tag", action="append", default=[])
    sub.add_parser("list")
    imp = sub.add_parser("import")
    imp.add_argument("file", type=Path)
    args = parser.parse_args(argv)

    items = _load()
    if args.cmd == "import":
        try:
            html = args.file.read_text(encoding="utf-8")
        except OSError as e:
            print(f"cannot read {args.file}: {e.strerror}", file=sys.stderr)
            return 1
        p = _Bookmarks()
        p.feed(html)
        known = {i["url"] for i in items}
        new = [b for b in p.found if b["url"] not in known and not known.add(b["url"])]
        items = new[::-1] + items
        _store().write_text(json.dumps(items, indent=2), encoding="utf-8")
        print(f"Imported {len(new)} bookmark(s).")
    elif args.cmd == "add":
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
