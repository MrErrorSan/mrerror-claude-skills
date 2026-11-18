"""Parallel-safe check over a plan's task table, and the lane write-set check.

plan-check rules (plan T3; formats in references/formats.md):
 1 write-overlap    writes don't overlap between tasks in the same wave
 2 shared-resource  no shared resource appears twice in the same wave
 3 depends-wave     each dependency points at a strictly earlier wave
 4 integrator-only  lockfiles, migrations and generated files are in no lane's writes
 5 no-spec          every task cites an S-line, or its review is "skip (fully specified)"
 6 wave-0           every wave-0 task is a foundation: some later task depends on it
 7 unknown-depends  every id in Depends is a task in the table
 8 wave-width       each wave has at most MAX_LANES tasks
 9 shared-id        shared resource ids are well-formed
"""
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
from itertools import combinations
from pathlib import Path

from . import docs, state
from .docs import Task

INTEGRATOR_ONLY = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock",
                   "uv.lock", "Cargo.lock", "go.sum", "**/migrations/**", "**/generated/**")
SHARED_RE = re.compile(r"^(port:\d+|db|lockfile|generated|migrations|devserver)$")
SPEC_RE = re.compile(r"^S\d+$")
WILD = re.compile(r"[*?]")
MAX_LANES = 4


@dataclass
class Finding:
    rule: str
    tasks: list[str]
    detail: str


def _norm(path: str) -> str:
    path = path.strip().replace("\\", "/")
    return (path[2:] if path.startswith("./") else path).lstrip("/")


def _expand(path: str) -> list[str]:
    """Expand {a,b} groups, which fnmatch doesn't know: src/{x,y}.ts -> src/x.ts, src/y.ts."""
    m = re.search(r"\{([^{}]*)\}", path)
    if not m:
        return [path]
    return [p for alt in m.group(1).split(",")
            for p in _expand(path[:m.start()] + alt + path[m.end():])]


def _dir(path: str) -> str:
    """The directory part a glob covers: dir/** -> dir, dir/ -> dir."""
    path = path.rstrip("/")
    while path.endswith(("/**", "/*")):
        path = path.rsplit("/", 1)[0]
    return path


def _match(path: str, pattern: str) -> bool:
    """fnmatch with [ taken literally, so route folders like app/[id]/ work."""
    return fnmatchcase(path, pattern.replace("[", "[[]"))


def _globs_meet(x: str, y: str) -> bool:
    """Two globs may share files: their literal prefixes (before the first wildcard) and
    suffixes (after the last) are compatible. Conservative: a false positive only makes
    the plan run sequentially."""
    (px, *_, sx), (py, *_, sy) = WILD.split(x), WILD.split(y)
    return ((px.startswith(py) or py.startswith(px))
            and (sx.endswith(sy) or sy.endswith(sx)))


def _as_dir(path: str) -> bool:
    """A literal entry that may be a directory: a trailing / or no extension."""
    return path.endswith("/") or "." not in path.rsplit("/", 1)[-1]


def _pair(x: str, y: str) -> bool:
    if x == y or y.startswith(_dir(x) + "/") or x.startswith(_dir(y) + "/"):
        return True
    wx, wy = bool(WILD.search(x)), bool(WILD.search(y))
    if wx and wy:
        return _globs_meet(x, y)
    if wx != wy:
        lit, glob = (y, x) if wx else (x, y)
        return _match(lit, glob) or (_as_dir(lit) and _globs_meet(glob, lit.rstrip("/") + "/**"))
    return False


def overlaps(a: str, b: str) -> bool:
    """Two write entries may touch the same file. Case-insensitive (NTFS)."""
    return any(_pair(x, y) for x in _expand(_norm(a).lower()) for y in _expand(_norm(b).lower()))


def _integrator_only(path: str) -> bool:
    path = _norm(path).lower()
    name = path.rsplit("/", 1)[-1]
    return any(_match(name, pat) if "/" not in pat
               else _match("/" + path, pat) or _match("/" + path + "/", pat)
               for pat in map(str.lower, INTEGRATOR_ONLY))


def _waves(tasks: list[Task]) -> dict[int, list[Task]]:
    waves: dict[int, list[Task]] = {}
    for t in tasks:
        waves.setdefault(t.wave, []).append(t)
    return waves


def _write_overlap(tasks):
    for wave in _waves(tasks).values():
        for a, b in combinations(wave, 2):
            pairs = [f"{x} / {y}" for x in a.writes for y in b.writes if overlaps(x, y)]
            if pairs:
                yield Finding("write-overlap", [a.id, b.id], "; ".join(pairs))


def _shared_resource(tasks):
    for wave in _waves(tasks).values():
        for a, b in combinations(wave, 2):
            both = sorted(set(a.shared) & set(b.shared))
            if both:
                yield Finding("shared-resource", [a.id, b.id], ", ".join(both))


def _depends_wave(tasks):
    by_id = {t.id: t for t in tasks}
    for t in tasks:
        for d in t.depends:
            if d in by_id and by_id[d].wave >= t.wave:
                yield Finding("depends-wave", [t.id, d],
                              f"{t.id} (wave {t.wave}) depends on {d} (wave {by_id[d].wave})")


def _integrator_paths(tasks):
    for t in tasks:
        bad = [w for w in t.writes if _integrator_only(w)]
        if bad:
            yield Finding("integrator-only", [t.id],
                          f"{', '.join(bad)}: only the integrator writes these")


def _no_spec(tasks):
    for t in tasks:
        if not any(SPEC_RE.match(s) for s in t.spec) and t.review != "skip (fully specified)":
            yield Finding("no-spec", [t.id],
                          "no S-line in Spec and review is not 'skip (fully specified)'")


def _wave_zero(tasks):
    needed = {d for t in tasks for d in t.depends}
    loose = [t.id for t in tasks if t.wave == 0 and t.id not in needed]
    if loose:
        yield Finding("wave-0", loose, "no later task depends on it; wave 0 is for foundations")


def _unknown_depends(tasks):
    ids = {t.id for t in tasks}
    for t in tasks:
        unknown = [d for d in t.depends if d not in ids]
        if unknown:
            yield Finding("unknown-depends", [t.id], f"unknown task {', '.join(unknown)}")


def _wave_width(tasks):
    for n, wave in sorted(_waves(tasks).items()):
        if len(wave) > MAX_LANES:
            yield Finding("wave-width", [t.id for t in wave],
                          f"wave {n} has {len(wave)} tasks; at most {MAX_LANES} lanes")


def _shared_ids(tasks):
    for t in tasks:
        for s in t.shared:
            if not SHARED_RE.match(s):
                yield Finding("shared-id", [t.id], f"{s} is not port:<n>, db, lockfile, "
                              "generated, migrations or devserver")


RULES = (_write_overlap, _shared_resource, _depends_wave, _integrator_paths, _no_spec,
         _wave_zero, _unknown_depends, _wave_width, _shared_ids)


def plan_check(tasks: list[Task]) -> list[Finding]:
    """Empty list = parallel-safe."""
    return [f for rule in RULES for f in rule(tasks)]


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=cwd,
                          check=True, capture_output=True, text=True, encoding="utf-8").stdout


def _outside(paths, writes: list[str]) -> list[str]:
    """Changed paths outside the write set, plus integrator-only ones even inside it."""
    return sorted({p for p in paths
                   if _integrator_only(p) or not any(overlaps(p, w) for w in writes)})


def lane_check(cwd: Path, task: Task, base: str) -> list[str]:
    """Paths changed on this branch since it left base that the lane may not write:
    outside task.writes, or integrator-only. A rename counts as both of its paths."""
    out = _git(cwd, "diff", "--name-only", "--no-renames", "-z", f"{base}...HEAD")
    return _outside([p for p in out.split("\0") if p], task.writes)


def _uncommitted(cwd: Path) -> list[str]:
    """Staged, unstaged and untracked paths, relative to the repo root; both sides of a rename."""
    out = _git(cwd, "-c", "status.relativePaths=false", "status", "--porcelain", "-z", "-uall")
    paths, entries = [], iter(out.split("\0"))
    for entry in entries:
        if entry:
            paths.append(entry[3:])
            if "R" in entry[:2] or "C" in entry[:2]:
                source = next(entries, "")  # the source path follows
                if "R" in entry[:2] and source:
                    paths.append(source)
    return paths


def _active_tasks(cwd: Path) -> list[Task] | None:
    topic_dir = state.topic_dir(cwd)
    if topic_dir is None:
        print("No active topic. Run: anvil topic start <slug>", file=sys.stderr)
        return None
    plan = docs.topic_docs(topic_dir)[1]
    if not plan.exists():
        print(f"{plan} not found", file=sys.stderr)
        return None
    try:
        tasks = docs.parse_tasks(docs.read_text(plan))
    except ValueError as e:
        print(f"{plan}: {e}", file=sys.stderr)
        return None
    if not tasks:
        print(f"{plan}: no rows under '## Task table'", file=sys.stderr)
        return None
    return tasks


def cmd_plan_check(args) -> int:
    tasks = _active_tasks(Path.cwd())
    if tasks is None:
        return 1
    findings = plan_check(tasks)
    if args.json:
        print(json.dumps([asdict(f) for f in findings]))
    elif findings:
        for f in findings:
            print(f"{f.rule}: {', '.join(f.tasks)}: {f.detail}")
    else:
        print(f"parallel-safe: {len(tasks)} tasks in {len(_waves(tasks))} waves")
    return 1 if findings else 0


def cmd_lane_check(args) -> int:
    cwd = Path.cwd()
    tasks = _active_tasks(cwd)
    if tasks is None:
        return 1
    task = next((t for t in tasks if t.id == args.task), None)
    if task is None:
        print(f"{args.task}: not in the task table", file=sys.stderr)
        return 1
    try:
        outside = set(lane_check(cwd, task, args.base)) \
            | set(_outside(_uncommitted(cwd), task.writes))
        # The orchestrator owns the topic's progress.md; it isn't a lane write.
        progress = (state.topic_dir(cwd) / "progress.md").resolve()
        root = state.repo_root(cwd).resolve()
        if progress.is_relative_to(root):
            outside.discard(progress.relative_to(root).as_posix())
        outside = sorted(outside)
    except subprocess.CalledProcessError as e:
        print(f"git failed: {e.stderr.strip()}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(outside))
    elif outside:
        for p in outside:
            print(f"outside-writes: {task.id}: {p}")
    else:
        print(f"{task.id}: every changed path is inside its write set")
    return 1 if outside else 0
