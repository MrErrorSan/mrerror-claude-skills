import argparse
import re
from collections import Counter
from pathlib import Path


def count_words(text: str) -> list[tuple[str, int]]:
    """(word, count) pairs, most frequent first, ties in alphabetical order."""
    counts = Counter(re.findall(r"[a-z']+", text.lower()))
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def _count(value: str) -> int:
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be a whole number, got {value!r}")
    if n < 0:
        raise argparse.ArgumentTypeError(f"must be 0 or more, got {n}")
    return n


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wordfreq")
    parser.add_argument("file", type=Path)
    parser.add_argument("--top", type=_count, metavar="N", help="print only the N most frequent words")
    args = parser.parse_args(argv)
    words = count_words(args.file.read_text(encoding="utf-8"))
    if args.top is not None:
        words = words[:args.top]
    for word, n in words:
        print(f"{n} {word}")
    return 0
