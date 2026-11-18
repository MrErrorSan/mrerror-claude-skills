"""Provenance for Anvil files adapted from Superpowers (design §8.1).

Usage: python -I upstream/superpowers/tools/provenance.py [<superpowers dir>]

Reads the "adapted from superpowers@<v>: <path>" source lines in plugins/anvil/
(HTML, '#' or 'REM' comments), merges upstream/superpowers/manual-sources.json
for copied files that carry no source line, then writes source-map.json and
provenance/diffs/*.diff and prints each mapped file's status. The Superpowers
dir defaults to the plugin cache copy of the version in baseline.json.
"""
import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_RE = re.compile(
    r"^\s*(?:<!--|#|REM\b)\s*adapted from superpowers@[\w.+-]+:\s*(.*?)\s*(?:-->)?\s*$",
    re.IGNORECASE)
UPSTREAM = Path("upstream") / "superpowers"


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_sources(repo: Path) -> dict[str, list[str]]:
    """Anvil path -> Superpowers paths (relative to the Superpowers repo root)."""
    repo = Path(repo)
    found: dict[str, list[str]] = {}
    for path in sorted((repo / "plugins" / "anvil").rglob("*")):
        if not path.is_file():
            continue
        sources = []
        for line in _norm(path.read_text(encoding="utf-8", errors="ignore")).split("\n"):
            m = SOURCE_RE.match(line)
            if m:
                for part in m.group(1).split(","):
                    src = part.split()[0].rstrip(".") if part.split() else ""
                    if src and src not in sources:
                        sources.append(src)
        if sources:
            found[path.relative_to(repo).as_posix()] = sources
    manual = repo / UPSTREAM / "manual-sources.json"
    if manual.exists():
        for anvil_path, sources in json.loads(manual.read_text(encoding="utf-8")).items():
            merged = found.setdefault(anvil_path, [])
            merged.extend(s for s in sources if s not in merged)
    return dict(sorted(found.items()))


def classify(src_text: str, dst_text: str) -> str:
    """verbatim | lightly edited (word-level ratio >= 0.85) | adapted."""
    def clean(text):
        return "\n".join(l for l in _norm(text).split("\n") if not SOURCE_RE.match(l))
    src, dst = clean(src_text), clean(dst_text)
    if src == dst:
        return "verbatim"
    ratio = difflib.SequenceMatcher(None, src.split(), dst.split(), autojunk=False).ratio()
    return "lightly edited" if ratio >= 0.85 else "adapted"


def write_source_map(repo) -> None:
    out = Path(repo) / UPSTREAM / "source-map.json"
    out.write_text(json.dumps(read_sources(repo), indent=2) + "\n", encoding="utf-8", newline="\n")


def _diff(src: Path, dst: Path, src_name: str, dst_name: str) -> str:
    """git diff --no-index on line-ending-normalised copies, headers renamed."""
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        for copy, original in ((a, src), (b, dst)):
            copy.write_bytes(_norm(original.read_text(encoding="utf-8", errors="replace")).encode("utf-8"))
        out = subprocess.run(
            ["git", "diff", "--no-index", "--no-color", "--no-ext-diff", "--no-prefix", "a", "b"],
            cwd=tmp, capture_output=True, text=True, encoding="utf-8").stdout
    lines = out.split("\n")
    for i, line in enumerate(lines[:4]):
        if line.startswith("diff --git "):
            lines[i] = f"diff --git a/{src_name} b/{dst_name}"
        elif line == "--- a":
            lines[i] = f"--- a/{src_name}"
        elif line == "+++ b":
            lines[i] = f"+++ b/{dst_name}"
    return "\n".join(lines)


def write_diffs(repo, sp_root: Path) -> list[Path]:
    """One diff per mapped Anvil file (all its sources), skipping empty ones."""
    repo, sp_root = Path(repo), Path(sp_root)
    out_dir = repo / UPSTREAM / "provenance" / "diffs"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.diff"):
        old.unlink()
    written = []
    for anvil_path, sources in read_sources(repo).items():
        parts = []
        for src in sources:
            if not (sp_root / src).is_file():
                print(f"provenance: missing Superpowers file {src} (for {anvil_path})", file=sys.stderr)
                continue
            parts.append(_diff(sp_root / src, repo / anvil_path, f"superpowers/{src}", anvil_path))
        text = "".join(p for p in parts if p.strip())
        if text:
            path = out_dir / (anvil_path.replace("/", "__") + ".diff")
            path.write_text(text, encoding="utf-8", newline="\n")
            written.append(path)
    return written


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    repo = Path(__file__).resolve().parents[3]
    if argv:
        sp_root = Path(argv[0])
    else:
        version = json.loads((repo / UPSTREAM / "baseline.json").read_text(encoding="utf-8"))["version"]
        sp_root = Path.home() / ".claude/plugins/cache/claude-plugins-official/superpowers" / version
    if not sp_root.is_dir():
        print(f"provenance: no Superpowers copy at {sp_root}", file=sys.stderr)
        return 1
    write_source_map(repo)
    diffs = write_diffs(repo, sp_root)
    print("| Anvil file | Superpowers source | Status |\n|---|---|---|")
    for anvil_path, sources in read_sources(repo).items():
        dst = (repo / anvil_path).read_text(encoding="utf-8", errors="replace")
        for src in sources:
            sp_file = sp_root / src
            status = classify(sp_file.read_text(encoding="utf-8", errors="replace"), dst) \
                if sp_file.is_file() else "missing upstream"
            print(f"| `{anvil_path}` | `{src}` | {status} |")
    print(f"\n{len(diffs)} diffs written to {UPSTREAM.as_posix()}/provenance/diffs/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
