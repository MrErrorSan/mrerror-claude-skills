"""Claude Code hook handlers (design §7.2, §7.6, §7.7, §7.11, §7.13).

`anvil hook <event>` reads the hook JSON on stdin, calls the handler below and
prints the dict it returns as JSON. Every handler fails open: an exception gives
{} and one line on stderr. Without an active topic every hook is a no-op, except
that user-prompt-submit still logs the prompt and session-start still states the
facts.
"""
import hashlib
import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

from . import docs, gate, progress, results, state

EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
TASK_RE = re.compile(r"^- \[( |~)\] (\S+)")
FILE_RE = re.compile(r"/|\.[A-Za-z0-9]{1,4}$")  # a test name that is a path or file name
RERUN_RE = re.compile(r"^\s*ANVIL_RERUN=1\s")
SKILLS = "anvil:brainstorm, anvil:plan, anvil:build, anvil:verify, anvil:finish, anvil:debug"


def _cwd(event: dict) -> Path:
    return Path(event.get("cwd") or os.getcwd())


def _same(a, b) -> bool:
    return os.path.normcase(str(Path(a).resolve())) == os.path.normcase(str(Path(b).resolve()))


def _inside(path, folder) -> bool:
    p = os.path.normcase(str(Path(path).resolve()))
    f = os.path.normcase(str(Path(folder).resolve()))
    return p == f or p.startswith(f.rstrip("\\/") + os.sep)


def _deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                   "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def session_start(event: dict) -> dict:
    cwd = _cwd(event)
    anvil = (Path(__file__).resolve().parent.parent / "anvil").as_posix()
    facts = [
        f"Anvil is installed. Its CLI is on PATH as `anvil` ({anvil}).",
        "Anvil's flow: brainstorm → spec → stop 1 (spec approval) → plan → stop 2 (plan "
        "approval) → build → verify → finish.",
        "Sizes: trivial has no documents and no stops; direct has one spec-and-plan document "
        "and one stop; full has a separate spec and plan and two stops.",
        "A stop is passed only by Saad's own words: `anvil approve` writes the Approved line "
        "after checking his quote against his recorded messages.",
        f"When Superpowers is also installed, Anvil's skills ({SKILLS}) cover brainstorming, "
        "planning, building, review and finishing for this workflow.",
    ]
    topic = state.active_topic(cwd)
    if topic:
        s = progress.progress_summary(cwd)
        line = (f"Stage {s['stage'] or '?'}, wave {s['wave'] or '?'}. Tasks: {s['open']} open, "
                f"{s['in_progress']} in progress, {s['done']} done." if s else "No progress.md yet.")
        facts.append(f"Active topic: {topic['slug']} (size {topic['size']}, stage "
                     f"{topic['stage']}, folder {topic['dir']}). {line}")
    else:
        facts.append("No Anvil topic is active in this repo.")
    afk = gate.afk_status(cwd)
    if afk.get("on"):
        facts.append(f"AFK is on, from Saad's words \"{afk.get('quote')}\": decisions go to the "
                     "decision log instead of questions, and the Stop hook holds the run while "
                     "tasks are open.")
    return {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                   "additionalContext": "\n".join(facts)}}


def user_prompt_submit(event: dict) -> dict:
    state.append_jsonl(_cwd(event), "prompts.jsonl",
                       {"ts": time.time(), "prompt": event.get("prompt", "")}, keep=500)
    return {}


def pre_tool_use(event: dict) -> dict:
    cwd = _cwd(event)
    topic = state.active_topic(cwd)
    if not topic:
        return {}
    tool, inp = event.get("tool_name", ""), event.get("tool_input") or {}
    if tool == "Bash":
        return _fresh_result(cwd, str(inp.get("command", "")))
    if tool not in EDIT_TOOLS:
        return {}  # agent dispatch is not gated: brainstorm uses subagents before stop 2
    folder = state.topic_dir(cwd)
    raw = inp.get("file_path") or inp.get("notebook_path")
    path = (cwd / raw) if raw else None
    if path and _sets_approval(folder, path, tool, inp):
        return _deny("Only `anvil approve` writes the Approved line; it checks Saad's words.")
    # PreToolUse also fires inside subagents, so this holds a build started early. Only
    # repo files are held: the scratchpad, memory and plans live outside the repo.
    root = state.repo_root(cwd)
    if (topic.get("stage") in ("spec", "plan") and path is not None
            and _inside(path, root) and not _inside(path, folder)
            and not _inside(path, root / "docs" / "research")):  # research docs have no stops
        plan_ok, plan_reason = gate.check(cwd, "build")
        if not plan_ok:
            spec_ok, spec_reason = gate.check(cwd, "plan")
            which, reason = ("plan", plan_reason) if spec_ok else ("spec", spec_reason)
            return _deny(f"{reason} Until then, edits outside {topic['dir']} are held. The "
                         f"{which} gets approved by showing it to Saad and running "
                         f"`anvil present {which}`, then Saad's reply, recorded with "
                         f"`anvil approve {which} --quote \"<his words>\"`.")
    return _keep_test(folder, path) if path else {}


def _sets_approval(folder: Path, path: Path, tool: str, inp: dict) -> bool:
    """The edit changes the Approved header of the topic's spec.md or plan.md to a value
    other than "no"."""
    if not any(_same(path, folder / n) for n in ("spec.md", "plan.md")):
        return False
    old = docs.read_text(path) if path.exists() else ""
    if tool == "Write":
        new = str(inp.get("content", "")).replace("\r\n", "\n")
    else:
        edits = inp.get("edits") if tool == "MultiEdit" else [inp]
        new = old
        for e in edits or []:
            a = str(e.get("old_string", "")).replace("\r\n", "\n")
            b = str(e.get("new_string", "")).replace("\r\n", "\n")
            if a:
                new = new.replace(a, b, -1 if e.get("replace_all") else 1)
    before = docs.parse_header(old).get("Approved")
    after = docs.parse_header(new).get("Approved")
    return after is not None and after != before and after != "no"


def _keep_test(folder: Path, path: Path) -> dict:
    plan = folder / "plan.md"
    if not plan.exists():
        return {}
    try:
        rel = path.resolve().relative_to(state.repo_root(folder).resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    specs = []
    for t in docs.parse_tests(docs.read_text(plan)):
        name = t.name.split("::")[0].strip()
        if t.type not in ("keep", "repro") or not name:  # a repro stays on as a keep test
            continue
        if FILE_RE.search(name):
            hit = rel == name or rel.endswith("/" + name) or path.name == Path(name).name
        else:  # dotted unittest id: a test module segment names this .py file
            hit = path.suffix == ".py" and any(
                seg == path.stem and seg.startswith("test") for seg in name.split("."))
        if hit:
            specs += [s for s in t.spec if s not in specs]
    if not specs:
        return {}
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": f"This file is a keep test for {', '.join(specs)}; state "
                             "test-changed vs code-changed with the S-line in your report."}}


def _test_command(argv: list[str]) -> tuple[list[str], str | None] | None:
    """(cmd, scope) for `anvil run [--scope S] -- <cmd>`, (argv, None) otherwise;
    None for `anvil run --external`. scope None means any recorded scope."""
    if len(argv) < 2 or Path(argv[0]).name not in ("anvil", "anvil.cmd") or argv[1] != "run":
        return argv, None
    scope, rest = "targeted", argv[2:]
    while rest:
        a = rest.pop(0)
        if a == "--":
            break
        if a == "--external":
            return None
        if a == "--scope" and rest:
            scope = rest.pop(0)
        elif a.startswith("--scope="):
            scope = a.split("=", 1)[1]
        elif a != "--json":
            rest.insert(0, a)
            break
    return rest, scope


def _fresh_result(cwd: Path, command: str) -> dict:
    if RERUN_RE.match(command):
        return {}
    try:
        parsed = _test_command(shlex.split(command))
    except ValueError:
        return {}
    if not parsed or not parsed[0]:
        return {}
    cmd, scope = parsed
    # Filter on cmd (and scope) first, so ordinary commands never compute a key.
    scopes = []
    for r in reversed(state.read_jsonl(cwd, "results.jsonl")):
        if r.get("cmd") == cmd and (scope is None or r.get("scope") == scope):
            if r.get("scope") not in scopes:
                scopes.append(r.get("scope"))
    for s in scopes:
        rec = results.fresh(cwd, cmd, s)
        if rec:
            summary = "\n".join(str(rec.get("summary", "")).splitlines()[-20:])
            return _deny(f"A fresh green result exists for this code state: {rec['tests_ran']} "
                         f"tests passed at {rec['ts']} (scope {rec['scope']}). Recorded "
                         f"summary:\n{summary}\nTo run it again anyway, prefix the command "
                         "with `ANVIL_RERUN=1 `.")
    return {}


def stop(event: dict) -> dict:
    cwd = _cwd(event)
    if not state.active_topic(cwd) or not gate.afk_status(cwd).get("on"):
        return {}
    path = state.topic_dir(cwd) / "progress.md"
    if not path.exists():
        return {}
    section, open_ids = None, []
    for line in docs.read_text(path).splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        m = TASK_RE.match(line)
        if section == "tasks" and m:
            open_ids.append(m.group(2))
    digest = progress.stop_note_hash(cwd)
    # `afk on` records the baseline; without one since AFK turned on, the note as it
    # stands now is the baseline.
    prev = state.load(cwd, "stop.json", None)
    fresh = prev and prev.get("ts", 0) >= (gate.afk_status(cwd).get("ts") or 0)
    prev_hash = prev["hash"] if fresh else digest
    # Recorded on every AFK stop, so a note counts as new only once.
    state.save(cwd, "stop.json", {"hash": digest, "ts": time.time()})
    if event.get("stop_hook_active") or not open_ids or digest != prev_hash:
        return {}
    return {"decision": "block",
            "reason": f"AFK: open tasks {', '.join(open_ids)}. Continue, or write a Stop note "
                      "in progress.md."}


HANDLERS = {"session-start": session_start, "user-prompt-submit": user_prompt_submit,
            "pre-tool-use": pre_tool_use, "stop": stop}


def cmd_hook(args) -> int:
    try:
        event = json.loads(sys.stdin.read() or "{}")
        out = HANDLERS[args.event](event if isinstance(event, dict) else {})
    except Exception as e:  # fail open: a broken hook never blocks work
        print(f"anvil hook {args.event}: {type(e).__name__}: {e}".replace("\n", " "),
              file=sys.stderr)
        out = {}
    print(json.dumps(out, ensure_ascii=False))
    return 0
