"""Parsers for the shared formats in references/formats.md.

Every parser accepts text with LF or CRLF line endings.
"""
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SLINE_RE = re.compile(r"^- (~~)?\*\*S(\d+)\*\*")
HEADER_RE = re.compile(r"^- \*\*([^*]+?):\*\*\s*(.*?)\s*$")
RETIRED_RE = re.compile(r"RETIRED\s*(?:→|->)\s*S(\d+)")


@dataclass
class SLine:
    num: int
    text: str
    retired: bool
    replaced_by: int | None


@dataclass
class Task:
    id: str
    spec: list[str]
    writes: list[str]
    shared: list[str]
    depends: list[str]
    wave: int
    review: str


@dataclass
class TestEntry:
    name: str
    type: str
    spec: list[str]
    breaks: str
    task: str


@dataclass
class CommitPoint:
    id: str
    closes: str
    message: str
    push: bool


def read_text(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")


def parse_header(text: str) -> dict[str, str]:
    """Bold-key bullet lines above the first '## ' heading."""
    header = {}
    for line in text.splitlines():
        if line.startswith("## "):
            break
        m = HEADER_RE.match(line)
        if m and m.group(1) not in header:
            header[m.group(1)] = m.group(2)
    return header


def set_header(text: str, key: str, value: str) -> str:
    """Replace the header line for key, or add it after the last header line."""
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    new = f"- **{key}:** {value}"
    last = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            break
        m = HEADER_RE.match(line)
        if m and m.group(1) == key:
            lines[i] = new
            return nl.join(lines)
        if m:
            last = i
    lines.insert(1 if last is None else last + 1, new)
    return nl.join(lines)


def parse_slines(text: str) -> list[SLine]:
    """S-lines outside fenced code blocks (a quoted example is not an S-line)."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else SLINE_RE.match(line)
        if not m:
            continue
        rest = line[m.end():]
        if m.group(1):
            body, _, tail = rest.partition("~~")
            r = RETIRED_RE.search(tail)
            out.append(SLine(int(m.group(2)), body.strip(), True,
                             int(r.group(1)) if r else None))
        else:
            out.append(SLine(int(m.group(2)), rest.strip(), False, None))
    return out


def _table(text: str, heading: str) -> list[dict[str, str]]:
    """Rows of the first table under '## <heading>', keyed by header cell."""
    rows, cols, inside = [], None, False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower() == heading.lower()
            continue
        if not inside:
            continue
        s = line.strip()
        if not s.startswith("|"):
            if cols:
                break
            continue
        cells = [c.strip().replace("\\|", "|")
                 for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if cols is None:
            cols = cells
        elif not all(set(c) <= set("-: ") for c in cells):
            rows.append(dict(zip(cols, cells)))
    return rows


def _list(cell: str) -> list[str]:
    """Backticked items if any, else comma-separated; '-' means empty."""
    items = re.findall(r"`([^`]+)`", cell) or [c.strip() for c in cell.split(",")]
    return [i for i in items if i and i != "-"]


def parse_tasks(text: str) -> list[Task]:
    tasks = []
    for r in _table(text, "Task table"):
        try:
            wave = int(r.get("Wave", ""))
        except ValueError:
            raise ValueError(f"{r.get('Task')}: wave {r.get('Wave')!r} is not an integer")
        tasks.append(Task(r.get("Task", ""), _list(r.get("Spec", "")),
                          _list(r.get("Writes", "")), _list(r.get("Shared", "")),
                          _list(r.get("Depends", "")), wave, r.get("Review", "")))
    return tasks


def parse_tests(text: str) -> list[TestEntry]:
    return [TestEntry(r.get("Test", "").replace("`", ""), r.get("Type", ""),
                      _list(r.get("Spec", "")), r.get("Breaks if it fails", ""),
                      r.get("Task", ""))
            for r in _table(text, "Test strategy")]


def parse_commit_points(text: str) -> list[CommitPoint]:
    return [CommitPoint(r.get("Commit", ""), r.get("Closes", ""),
                        r.get("Message", "").replace("`", ""),
                        r.get("Push", "").lower().startswith("yes"))
            for r in _table(text, "Commit points")]


def topic_docs(topic_dir: Path) -> tuple[Path | None, Path]:
    """(spec.md, plan.md); spec is None when there is no spec.md (direct size)."""
    topic_dir = Path(topic_dir)
    spec = topic_dir / "spec.md"
    return (spec if spec.exists() else None), topic_dir / "plan.md"


def cmd_spec_lines(args) -> int:
    from . import state
    folder = state.topic_dir(Path.cwd())
    if folder is None:
        print("No active topic. Run: anvil topic start <slug>", file=sys.stderr)
        return 1
    spec, plan = topic_docs(folder)
    path = spec or plan
    if not path.exists():
        print(f"{path} not found", file=sys.stderr)
        return 1
    lines = parse_slines(read_text(path))
    if args.live:
        lines = [s for s in lines if not s.retired]
    elif args.retired:
        lines = [s for s in lines if s.retired]
    if args.json:
        print(json.dumps([asdict(s) for s in lines]))
    else:
        for s in lines:
            mark = f" (retired, replaced by S{s.replaced_by})" if s.retired else ""
            print(f"S{s.num}{mark} {s.text}")
    return 0
