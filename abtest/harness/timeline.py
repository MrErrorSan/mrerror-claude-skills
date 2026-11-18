"""Where did each run's time go? Reads Claude Code's own session transcripts.

    python abtest/harness/timeline.py --suite full           # writes results/<suite>/timeline.json + .md

Walks the main session's events in time order and attributes every gap between two
consecutive events to what was in flight: an open tool call (by category), waiting for
background subagents, or the model. Gaps while Saad (the simulator) was answering are
excluded. Each attribution also carries the phase: the last Skill the main session invoked.
Subagent transcripts give total subagent time and how much of it overlapped (parallelism).
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
PROJECTS = Path.home() / ".claude" / "projects"


def ts(e) -> float | None:
    t = e.get("timestamp")
    if not t:
        return None
    return datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp()


def load(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if ts(e) is not None and e.get("type") in ("user", "assistant", "attachment", "system"):
            out.append(e)
    return sorted(out, key=ts)


def bash_kind(cmd: str) -> str:
    if re.search(r"unittest|pytest", cmd):
        return "bash:tests"
    if re.search(r"(^|[\s/\\\"])anvil(\.cmd)?\"?\s", cmd):
        return "bash:anvil-cli"
    if re.match(r"\s*(cd [^&;]+(&&|;)\s*)?git\s", cmd):
        return "bash:git"
    return "bash:other"


def tool_kind(c: dict) -> str:
    n = c.get("name")
    if n == "Bash":
        return bash_kind(str(c.get("input", {}).get("command", "")))
    if n in ("Read", "Grep", "Glob"):
        return "read"
    if n in ("Edit", "Write", "NotebookEdit"):
        return "edit"
    if n in ("Agent", "Task"):
        return "agent:foreground" if not c.get("input", {}).get("run_in_background") else "agent:dispatch"
    return f"tool:{n}"


def is_prompt(e: dict) -> bool:
    if e.get("type") != "user" or e.get("isSidechain"):
        return False
    c = e.get("message", {}).get("content")
    return isinstance(c, str) and not c.lstrip().startswith("<")


def is_notification(e: dict) -> bool:
    """A background subagent reporting back (it arrives as a user turn or a queued command)."""
    c = e.get("message", {}).get("content")
    if e.get("type") == "user" and isinstance(c, str):
        return "<task-notification" in c
    a = e.get("attachment") or {}
    return e.get("type") == "attachment" and a.get("type") == "queued_command" \
        and "<task-notification" in str(a.get("prompt", ""))


def analyse_main(events: list[dict]) -> dict:
    open_tools: dict[str, tuple[str, str]] = {}   # tool_use_id -> (kind, phase)
    phase = "router/none"
    by_kind: dict[str, float] = {}
    by_phase: dict[str, float] = {}
    bg_pending = 0
    prev = None
    for e in events:
        t = ts(e)
        # A gap that ends in Saad's prompt is Saad's (the simulator's) time: excluded.
        if prev is not None and not is_prompt(e):
            gap = t - prev
            if open_tools:
                kind = sorted({k for k, _ in open_tools.values()})[0]
            elif is_notification(e):
                kind = "await-subagents"
            else:
                kind = "model"
            by_kind[kind] = by_kind.get(kind, 0) + gap
            by_phase[phase] = by_phase.get(phase, 0) + gap
        typ = e.get("type")
        content = e.get("message", {}).get("content")
        if typ == "assistant":
            for c in content or []:
                if c.get("type") == "tool_use":
                    k = tool_kind(c)
                    if c.get("name") == "Skill":
                        phase = str(c.get("input", {}).get("skill", "?")).split(":")[-1]
                        k = "skill-load"
                    if k == "agent:dispatch":
                        bg_pending += 1
                    open_tools[c["id"]] = (k, phase)
        elif typ == "user" and isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    open_tools.pop(c.get("tool_use_id"), None)
        prev = t
    total = sum(by_kind.values())
    return {"active_s": round(total, 1),
            "by_kind": {k: round(v, 1) for k, v in sorted(by_kind.items(), key=lambda kv: -kv[1])},
            "by_phase": {k: round(v, 1) for k, v in sorted(by_phase.items(), key=lambda kv: -kv[1])}}


def analyse_subagents(files: list[Path]) -> dict:
    spans = []
    for f in files:
        ev = load(f)
        if len(ev) >= 2:
            spans.append((ts(ev[0]), ts(ev[-1]), f.stem))
    total = sum(b - a for a, b, _ in spans)
    # union of intervals = wall time with at least one subagent running
    union, cur = 0.0, None
    for a, b, _ in sorted(spans):
        if cur is None or a > cur[1]:
            if cur:
                union += cur[1] - cur[0]
            cur = [a, b]
        else:
            cur[1] = max(cur[1], b)
    if cur:
        union += cur[1] - cur[0]
    return {"count": len(spans), "total_s": round(total, 1), "wall_s": round(union, 1),
            "parallelism": round(total / union, 2) if union else None}


def find_files(suite: str, run_id: str) -> tuple[Path | None, list[Path]]:
    pat = f"*anvil-abtest-{suite}-{run_id}-{run_id}"
    mains = [p for d in PROJECTS.glob(pat) for p in d.glob("*.jsonl")]
    main = max(mains, key=lambda p: p.stat().st_size) if mains else None
    subs = sorted({p for d in PROJECTS.glob(f"*anvil-abtest-{suite}-{run_id}*") for p in d.rglob("agent-*.jsonl")})
    return main, subs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True)
    a = ap.parse_args()
    out = {}
    for meta in sorted((RESULTS / a.suite / "runs").glob("*.json")):
        m = json.loads(meta.read_text(encoding="utf-8"))
        main_f, subs = find_files(a.suite, m["run_id"])
        if not main_f:
            continue
        out[m["run_id"]] = {"case": m["case"], "arm": m["arm"], "agent_time_s": m["agent_time_s"],
                            "main": analyse_main(load(main_f)), "subagents": analyse_subagents(subs)}
    (RESULTS / a.suite / "timeline.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    kinds = ["model", "await-subagents", "agent:foreground", "bash:tests", "bash:anvil-cli", "bash:git",
             "bash:other", "read", "edit", "skill-load"]
    lines = [f"# Where the time went: suite `{a.suite}`", "",
             "Seconds of the main session's active time (Saad's thinking time excluded), by what was in flight.", "",
             "| Run | Agent s | " + " | ".join(kinds) + " | Subagents (n / total s / parallelism) | Top phases |",
             "|---|---|" + "---|" * len(kinds) + "---|---|"]
    for rid, r in sorted(out.items(), key=lambda kv: (kv[1]["case"], kv[1]["arm"], kv[0])):
        bk = r["main"]["by_kind"]
        s = r["subagents"]
        phases = ", ".join(f"{k} {v:.0f}" for k, v in list(r["main"]["by_phase"].items())[:4])
        lines.append(f"| {rid} | {r['agent_time_s']:.0f} | " + " | ".join(f"{bk.get(k, 0):.0f}" for k in kinds)
                     + f" | {s['count']} / {s['total_s']:.0f} / {s['parallelism']} | {phases} |")
    (RESULTS / a.suite / "timeline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / a.suite / 'timeline.md'} ({len(out)} runs)")


if __name__ == "__main__":
    main()
