"""Stops (spec and plan approval) and AFK mode. Design §4 (self-approval) and §7.2.

Every approval traces back to words Saad typed: a quote is accepted only when it
appears in prompts.jsonl, the log the UserPromptSubmit hook writes.
"""
import datetime
import hashlib
import json
import re
import sys
import time
from pathlib import Path

from . import docs, state

AFK_PHRASES = ("afk", "going to bed", "don't ask", "dont ask", "no approvals", "just finish",
               "run with it", "work through the plan", "i'll review", "make the call yourself")

APPROVED_RE = re.compile(r'^(\d{4}-\d{2}-\d{2} by Saad|pre-approved by Saad \d{4}-\d{2}-\d{2}'
                         r'|skipped \(AFK\) \d{4}-\d{2}-\d{2}) \(".*"\)$')
_QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})


# UserPromptSubmit also fires for turns Claude Code starts itself (a background subagent
# reporting back, a scheduled /loop firing, a message from another session), and the event
# carries no origin field. Those turns arrive wrapped in these markers; they are not
# Saad's words, so they never count for a gate.
INJECTED_RE = re.compile(r"<task-notification|\[SYSTEM NOTIFICATION|<agent-message|"
                         r"<scheduled-task|<cross-session|<teammate-message|<local-command-")


def is_injected(prompt: str) -> bool:
    return INJECTED_RE.search(prompt) is not None


def saad_prompts(cwd) -> list[dict]:
    """Logged prompts that came from Saad, oldest first."""
    return [r for r in state.read_jsonl(cwd, "prompts.jsonl")
            if not is_injected(str(r.get("prompt", "")))]


class GateError(Exception):
    pass


def _norm(text: str) -> str:
    return " ".join(text.translate(_QUOTES).lower().split())


def _quote_in(prompt: str, quote: str) -> bool:
    """A quote of 3+ words may be part of the prompt; a shorter one must be the whole prompt."""
    q, p = _norm(quote), _norm(prompt)
    if not q:
        return False
    return p == q or (len(q.split()) >= 3
                      and re.search(r"(?<!\w)" + re.escape(q) + r"(?!\w)", p) is not None)


def quote_in_prompts(cwd, quote: str, after_ts: float | None,
                     since: float | None = None) -> bool:
    """quote appears in a logged prompt newer than after_ts and logged at or after since
    (each only if given)."""
    for rec in saad_prompts(cwd):
        ts = float(rec.get("ts", 0))
        if (after_ts is not None and ts <= after_ts) or (since is not None and ts < since):
            continue
        if _quote_in(str(rec.get("prompt", "")), quote):
            return True
    return False


def has_afk_phrase(text: str) -> bool:
    q = _norm(text)
    return any(re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", q) for p in AFK_PHRASES)


def _last_prompt_ts(cwd, at_or_before: float) -> float | None:
    """ts of the last prompt logged at or before the given time."""
    return max((float(r.get("ts", 0)) for r in saad_prompts(cwd)
                if float(r.get("ts", 0)) <= at_or_before), default=None)


def _doc(cwd, which: str) -> Path:
    topic = state.active_topic(cwd)
    if not topic:
        raise GateError("No active topic. Run: anvil topic start <slug>")
    spec, plan = docs.topic_docs(state.topic_dir(cwd))
    if which == "spec" and spec is None:
        if topic.get("size") == "direct":
            raise GateError("This topic is direct size: it has no spec.md, only plan.md.")
        raise GateError(f"{topic['dir']}/spec.md not found.")
    path = spec if which == "spec" else plan
    if not path.exists():
        raise GateError(f"{topic['dir']}/plan.md not found.")
    return path


def _hash(path: Path) -> str:
    return hashlib.sha256(docs.read_text(path).encode("utf-8")).hexdigest()


def present(cwd: Path, which: str) -> None:
    path = _doc(cwd, which)
    if which == "plan":
        ok, reason = check(cwd, "plan")
        if not ok:  # else one reply after both are shown would pass both stops
            raise GateError(f"{reason} Present the plan once the spec is approved.")
    presented = state.load(cwd, "presented.json", {})
    presented[which] = {"hash": _hash(path), "ts": time.time()}
    state.save(cwd, "presented.json", presented)


def approve(cwd, which, quote: str, pre: bool = False, afk: bool = False) -> str:
    path = _doc(cwd, which)
    shown = " ".join(quote.split())
    today = datetime.date.today().isoformat()
    if afk:
        status = afk_status(cwd)
        if not status["on"]:
            raise GateError("AFK mode is off (or was turned on before this topic started), "
                            "so this stop can't be skipped.")
        # The quote that turned AFK on authorises the skip, not the caller's.
        value = f'skipped (AFK) {today} ("{" ".join(status["quote"].split())}")'
    elif pre:
        if len(_norm(quote).split()) < 3:
            raise GateError(f'"{shown}" is too short for a pre-approval: it needs 3+ words '
                            "of Saad's exact message.")
        # The window opens at the request that started the topic: older prompts
        # belong to earlier work.
        started = state.active_topic(cwd).get("started", 0)
        if not quote_in_prompts(cwd, quote, None, since=_last_prompt_ts(cwd, started)):
            raise GateError(f'"{shown}" is not in a message from Saad since this topic started. '
                            "A pre-approval needs his exact words (3+ words).")
        value = f'pre-approved by Saad {today} ("{shown}")'
    else:
        rec = state.load(cwd, "presented.json", {}).get(which)
        if not rec:
            raise GateError(f"The {which} was never presented. Run: anvil present {which}")
        if rec["hash"] != _hash(path):
            raise GateError(f"The {which} changed after it was presented. "
                            f"Show it again and run: anvil present {which}")
        if not quote_in_prompts(cwd, quote, rec["ts"]):
            raise GateError(f'"{shown}" is not in a message from Saad sent after the {which} '
                            "was presented (3+ words, or his whole message).")
        value = f'{today} by Saad ("{shown}")'
    raw = path.read_bytes().decode("utf-8")
    path.write_bytes(docs.set_header(raw, "Approved", value).encode("utf-8"))
    return value


def _approved(path: Path | None) -> bool:
    if path is None or not path.exists():
        return False
    return bool(APPROVED_RE.match(docs.parse_header(docs.read_text(path)).get("Approved", "")))


def check(cwd, stage: str) -> tuple[bool, str]:
    """"plan": spec approved, or size=direct. "build": plan approved."""
    topic = state.active_topic(cwd)
    if not topic:
        return False, "No active topic."
    if topic.get("size") == "trivial":
        return True, "Trivial size has no stops."
    spec, plan = docs.topic_docs(state.topic_dir(cwd))
    if stage == "plan":
        if topic.get("size") == "direct":
            return True, "Direct size has no separate spec stop."
        if _approved(spec):
            return True, "The spec is approved."
        return False, "The spec is not approved yet. Stop 1 needs Saad's approval."
    if _approved(plan):
        return True, "The plan is approved."
    return False, "The plan is not approved yet. Stop 2 needs Saad's approval."


def afk_on(cwd, quote) -> None:
    """Design §7.2: only the last recorded message can turn AFK on."""
    prompts = saad_prompts(cwd)
    if not prompts or not _quote_in(str(prompts[-1].get("prompt", "")), quote):
        raise GateError(f'"{" ".join(quote.split())}" is not in the last message from Saad. '
                        "AFK turns on only from his latest message.")
    if not has_afk_phrase(quote):
        raise GateError("The quote has no AFK phrase (for example \"AFK\", \"going to bed\", "
                        "\"don't ask\", \"just finish\").")
    state.save(cwd, "afk.json", {"on": True, "ts": time.time(), "quote": quote})
    # The Stop note as it is now is the baseline, so a note written later in this
    # same turn counts as new at the first stop.
    from . import progress
    state.save(cwd, "stop.json", {"hash": progress.stop_note_hash(cwd), "ts": time.time()})


def afk_off(cwd) -> None:
    state.save(cwd, "afk.json", {"on": False, "ts": time.time(), "quote": None})


def afk_status(cwd) -> dict:
    """afk.json, with "on" false when AFK was turned on before the active topic started."""
    status = state.load(cwd, "afk.json", {"on": False, "ts": None, "quote": None})
    topic = state.active_topic(cwd)
    if status.get("on") and topic and (status.get("ts") or 0) < topic.get("started", 0):
        status["on"] = False
    return status


def afk_at_topic_start(cwd, started: float) -> None:
    """A fresh topic start keeps AFK only when it was turned on from the latest prompt
    ("AFK, build X": afk on, then topic start, in one turn). It is then restamped, so it
    isn't older than the topic, and so is the Stop note baseline `afk on` recorded."""
    status = state.load(cwd, "afk.json", None)
    if not status or not status.get("on"):
        return
    last = _last_prompt_ts(cwd, started)
    if last is None or (status.get("ts") or 0) < last:
        afk_off(cwd)
        return
    from . import progress
    state.save(cwd, "afk.json", {**status, "ts": started})
    state.save(cwd, "stop.json", {"hash": progress.stop_note_hash(cwd), "ts": started})


def _report(args, ok: bool, message: str, **data) -> int:
    if args.json:
        print(json.dumps({"ok": ok, "message": message, **data}, ensure_ascii=False))
    if ok and not args.json:
        print(message)
    if not ok:
        print(message, file=sys.stderr)
    return 0 if ok else 1


def cmd_present(args) -> int:
    try:
        present(Path.cwd(), args.which)
    except GateError as e:
        return _report(args, False, str(e))
    return _report(args, True, f"Recorded the {args.which} as presented.",
                   **state.load(Path.cwd(), "presented.json", {})[args.which])


def cmd_approve(args) -> int:
    if args.pre and args.afk:
        print("anvil approve: use --pre or --afk, not both", file=sys.stderr)
        return 2
    try:
        value = approve(Path.cwd(), args.which, args.quote, pre=args.pre, afk=args.afk)
    except GateError as e:
        return _report(args, False, str(e))
    return _report(args, True, f"Approved: {value}", approved=value)


def cmd_check(args) -> int:
    ok, reason = check(Path.cwd(), args.stage)
    return _report(args, ok, reason)


def cmd_afk(args) -> int:
    cwd = Path.cwd()
    try:
        if args.action == "on":
            afk_on(cwd, args.quote)
        elif args.action == "off":
            afk_off(cwd)
    except GateError as e:
        return _report(args, False, str(e))
    status = afk_status(cwd)
    return _report(args, True, f"AFK is {'on' if status['on'] else 'off'}.", **status)
