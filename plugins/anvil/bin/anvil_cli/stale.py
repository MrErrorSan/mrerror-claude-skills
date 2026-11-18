"""anvil stale: tasks and tests whose Spec cell names a retired S-line (design §7.6)."""
import json
import re
import subprocess
import sys
from pathlib import Path

from . import docs, state


def stale(cwd) -> list[dict]:
    cwd = Path(cwd)
    out = []
    topic = state.active_topic(cwd)
    if topic:
        spec, plan = docs.topic_docs(state.topic_dir(cwd))
        if plan.exists():
            plan_text = docs.read_text(plan)
            slines = docs.parse_slines(docs.read_text(spec) if spec else plan_text)
            retired = {s.num: s.replaced_by for s in slines if s.retired}
            rows = [("task", t.id, t.spec) for t in docs.parse_tasks(plan_text)]
            rows += [("test", t.name, t.spec) for t in docs.parse_tests(plan_text)]
            for kind, ident, spec_cell in rows:
                for entry in spec_cell:
                    m = re.fullmatch(r"S(\d+)", entry)
                    if m and int(m.group(1)) in retired:
                        out.append({"kind": kind, "id": ident, "retired": entry,
                                    "replaced_by": retired[int(m.group(1))]})
    # Result staleness: no recorded run matches the current tree. Records without
    # "tree" are the old format and are ignored.
    trees = {r["tree"] for r in state.read_jsonl(cwd, "results.jsonl") if "tree" in r}
    if not trees:
        return out
    try:
        from . import results
    except ModuleNotFoundError as e:
        if e.name != "anvil_cli.results":
            raise
        return out  # result reuse not installed: skip that check
    try:
        key = results.tree_key(cwd)
    except (subprocess.CalledProcessError, OSError):
        return out  # outside git, or git missing: nothing to key on
    if key not in trees:
        out.append({"kind": "result", "key": key})
    return out


def cmd_stale(args) -> int:
    cwd = Path.cwd()
    if not state.active_topic(cwd):
        if args.json:
            print("null")
        print("No active topic. Run: anvil topic start <slug>", file=sys.stderr)
        return 1
    try:
        entries = stale(cwd)
    except ValueError as e:
        print(f"plan.md: {e}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(entries))
    else:
        for e in entries:
            if e["kind"] == "result":
                print(f"result: no recorded run for the current tree ({e['key']})")
            else:
                by = f"S{e['replaced_by']}" if e["replaced_by"] else "nothing"
                print(f"{e['kind']} {e['id']}: names {e['retired']}, retired (replaced by {by})")
    return 1 if entries else 0
