import argparse
import re
from collections import Counter
from pathlib import Path


def count_words(text: str) -> list[tuple[str, int]]:
    """(word, count) pairs, most frequent first, ties in alphabetical order."""
    counts = Counter(re.findall(r"[a-z']+", text.lower()))
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wordfreq")
    parser.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    for word, n in count_words(args.file.read_text(encoding="utf-8")):
        print(f"{n} {word}")
    return 0
