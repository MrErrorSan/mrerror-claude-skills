"""anvil progress: a short status summary from the topic's progress.md (design §7.6)."""
import hashlib
import json
import sys
from pathlib import Path

from . import docs, state

MARKERS = {"[ ]": "open", "[~]": "in_progress", "[x]": "done", "[X]": "done"}


def progress_summary(cwd) -> dict | None:
    """None when there is no active topic or no progress.md."""
    folder = state.topic_dir(cwd)
    if folder is None:
        return None
    path = folder / "progress.md"
    if not path.exists():
        return None
    text = docs.read_text(path)
    header = docs.parse_header(text)
    out = {"stage": header.get("Stage", ""), "wave": header.get("Wave", ""),
           "open": 0, "in_progress": 0, "done": 0, "blockers": [], "last_decision": None}
    section = None
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        s = line.strip()
        if section == "tasks" and line.startswith("- [") and line[2:5] in MARKERS:
            out[MARKERS[line[2:5]]] += 1  # top-level only: indented sub-bullets aren't tasks
        elif section == "blockers" and s.startswith("- "):  # not "<!--" or loose text
            out["blockers"].append(s[2:])
        elif section == "decision log" and s.startswith("- ") and out["last_decision"] is None:
            out["last_decision"] = s[2:]
    return out


def stop_note_hash(cwd) -> str:
    """sha256 of the `## Stop note` section text (empty when there's no progress.md)."""
    folder = state.topic_dir(cwd)
    path = folder / "progress.md" if folder else None
    note, section = [], None
    if path and path.exists():
        for line in docs.read_text(path).splitlines():
            if line.startswith("## "):
                section = line[3:].strip().lower()
            elif section == "stop note":
                note.append(line)
    return hashlib.sha256("\n".join(note).strip().encode("utf-8")).hexdigest()


def cmd_progress(args) -> int:
    cwd = Path.cwd()
    summary = progress_summary(cwd)
    if summary is None:
        if args.json:
            print("null")
        reason = ("No active topic. Run: anvil topic start <slug>"
                  if not state.active_topic(cwd) else "progress.md not found")
        print(reason, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(summary, ensure_ascii=False))
        return 0
    s = summary
    print(f"Stage {s['stage'] or '?'}, wave {s['wave'] or '?'}. "
          f"Tasks: {s['open']} open, {s['in_progress']} in progress, {s['done']} done.")
    print("Blockers: " + ("; ".join(s["blockers"]) if s["blockers"] else "none"))
    print("Last decision: " + (s["last_decision"] or "none"))
    return 0
