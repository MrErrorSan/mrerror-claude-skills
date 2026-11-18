"""anvil: the Anvil CLI. Exit codes: 0 ok/yes, 1 no/refused (reason on stderr), 2 usage error.

Each subcommand maps to "module:function" in COMMANDS. The function takes the
parsed argparse.Namespace and returns an int exit code. Lanes write only the
module function; argument parsing for every subcommand lives here:

    gate.cmd_present(args) -> int       args.which: spec|plan
    gate.cmd_approve(args) -> int       args.which, args.quote, args.pre, args.afk, args.amended
    gate.cmd_check(args) -> int         args.stage: plan|build
    gate.cmd_afk(args) -> int           args.action: on|off|status; args.quote (on)
    docs.cmd_spec_lines(args) -> int    args.live, args.retired
    stale.cmd_stale(args) -> int
    plancheck.cmd_plan_check(args) -> int
    plancheck.cmd_lane_check(args) -> int   args.task, args.base
    results.cmd_run(args) -> int        args.scope, args.external, args.cmd (list)
    results.cmd_fresh(args) -> int      args.scope, args.cmd (list)
    progress.cmd_progress(args) -> int
    hooks.cmd_hook(args) -> int         args.event; reads hook JSON on stdin

Every subcommand also has args.json (bool).
"""
import argparse
import importlib
import json
import os
import sys
import time
from pathlib import Path

from . import state

COMMANDS: dict[str, str] = {
    "topic": "cli:cmd_topic",
    "present": "gate:cmd_present",
    "approve": "gate:cmd_approve",
    "check": "gate:cmd_check",
    "afk": "gate:cmd_afk",
    "spec-lines": "docs:cmd_spec_lines",
    "stale": "stale:cmd_stale",
    "plan-check": "plancheck:cmd_plan_check",
    "lane-check": "plancheck:cmd_lane_check",
    "run": "results:cmd_run",
    "fresh": "results:cmd_fresh",
    "progress": "progress:cmd_progress",
    "hook": "hooks:cmd_hook",
}

SCOPES = ("targeted", "full", "smoke", "check")  # check: type-check, lint, build
STAGES = ("spec", "plan", "build", "verify", "finish", "done")


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="print JSON")
    p = argparse.ArgumentParser(prog="anvil", description="Anvil workflow CLI.")
    sub = p.add_subparsers(dest="command", required=True, metavar="<subcommand>")

    def add(name, help_text, leaf=True):
        return sub.add_parser(name, help=help_text, parents=[common] if leaf else [])

    topic = add("topic", "start, show or end the active topic", leaf=False)
    tsub = topic.add_subparsers(dest="action", required=True)
    start = tsub.add_parser("start", parents=[common])
    start.add_argument("slug")
    start.add_argument("--size", choices=("trivial", "direct", "full"), default="full")
    start.add_argument("--dir", help="topic folder (default docs/<slug>)")
    tsub.add_parser("stage", parents=[common]).add_argument("stage", choices=STAGES)
    tsub.add_parser("show", parents=[common])
    tsub.add_parser("end", parents=[common])

    add("present", "record that a doc was shown to Saad").add_argument(
        "which", choices=("spec", "plan"))
    approve = add("approve", "write the Approved: line")
    approve.add_argument("which", choices=("spec", "plan"))
    approve.add_argument("--quote", required=True)
    approve.add_argument("--pre", action="store_true")
    approve.add_argument("--afk", action="store_true")
    approve.add_argument("--amended", action="store_true",
                         help="Saad's reply approved it and dictated the edits made since")
    add("check", "is this stage allowed to start?").add_argument(
        "stage", choices=("plan", "build"))

    afk = add("afk", "turn AFK mode on or off", leaf=False)
    asub = afk.add_subparsers(dest="action", required=True)
    asub.add_parser("on", parents=[common]).add_argument("--quote", required=True)
    asub.add_parser("off", parents=[common])
    asub.add_parser("status", parents=[common])

    sl = add("spec-lines", "list S-lines of the active topic")
    g = sl.add_mutually_exclusive_group()
    g.add_argument("--live", action="store_true")
    g.add_argument("--retired", action="store_true")
    add("stale", "tasks and tests pointing at retired S-lines")
    add("plan-check", "parallel-safe check over the task table")
    lane = add("lane-check", "a lane's diff stays inside its write set")
    lane.add_argument("task")
    lane.add_argument("--base", required=True)

    run = add("run", "run a test command and record the result")
    run.add_argument("--scope", choices=SCOPES, default="targeted")
    run.add_argument("--external", action="store_true", help="uses live services; never reused")
    run.add_argument("cmd", nargs=argparse.REMAINDER, help="-- <cmd...>")
    fresh = add("fresh", "is there a fresh green result for this command?")
    fresh.add_argument("--scope", choices=SCOPES, default="targeted")
    fresh.add_argument("cmd", nargs=argparse.REMAINDER, help="-- <cmd...>")

    add("progress", "status summary from progress.md")
    add("hook", "run a hook (reads hook JSON on stdin)").add_argument(
        "event", choices=("session-start", "user-prompt-submit", "pre-tool-use", "stop"))
    return p


def main(argv: list[str] | None = None) -> int:
    # bin/anvil sets these for its own Python call; a test command run by
    # `anvil run` must not inherit them.
    for name in ("MSYS_NO_PATHCONV", "MSYS2_ARG_CONV_EXCL"):
        os.environ.pop(name, None)
    # Spec text and hook JSON hold non-ASCII ("→", smart quotes); a cp1252 pipe
    # would crash on it or garble it.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command in ("run", "fresh"):
            if args.cmd[:1] == ["--"]:
                args.cmd = args.cmd[1:]
            if not args.cmd:
                parser.error(f"{args.command}: missing command after --")
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2
    module, func = COMMANDS[args.command].split(":")
    try:
        mod = importlib.import_module(f"anvil_cli.{module}")
    except ModuleNotFoundError as e:
        if e.name != f"anvil_cli.{module}":
            raise
        mod = None
    fn = getattr(mod, func, None)
    if fn is None:
        print(f"anvil {args.command}: not available yet", file=sys.stderr)
        return 1
    return fn(args)


def cmd_topic(args) -> int:
    cwd = Path.cwd()
    topic = state.active_topic(cwd)
    if args.action == "start":
        from . import gate
        if topic and topic.get("slug") != args.slug:
            if topic.get("stage") != "finish":
                print(f"Topic {topic['slug']} is active (stage {topic.get('stage')}). Run "
                      "`anvil topic end` first, or continue it.", file=sys.stderr)
                return 1
            # Verify already landed its work on the synced branch; only the optional
            # /anvil:finish (push, merge, clean-up) was left. Its documents stay.
            print(f"Parked topic {topic['slug']} (stage finish: its work is already landed).",
                  file=sys.stderr)
            topic = None
        # Restarting the same slug (a size step-up) keeps its folder unless --dir is
        # given, and keeps its start time.
        if topic:
            kept, started = topic["dir"], topic.get("started", 0)
        else:
            kept, started = None, time.time()
            gate.afk_at_topic_start(cwd, started)
        topic = {"slug": args.slug,
                 "dir": _topic_dir_arg(cwd, args.dir) or kept or f"docs/{args.slug}",
                 "size": args.size,
                 "stage": {"trivial": "build", "direct": "plan"}.get(args.size, "spec"),
                 "started": started}
        state.save(cwd, "active.json", topic)
    elif not topic:
        if args.json:
            print("null")
        print("No active topic.", file=sys.stderr)
        return 1
    elif args.action == "stage":
        if args.stage in ("plan", "build"):
            from . import gate
            ok, reason = gate.check(cwd, args.stage)
            if not ok:
                print(reason, file=sys.stderr)
                return 1
        topic["stage"] = args.stage
        state.save(cwd, "active.json", topic)
    elif args.action == "end":
        from . import gate
        state.save(cwd, "active.json", None)
        gate.afk_off(cwd)  # an AFK run ends with its topic
    if args.json:
        print(json.dumps(topic))
    else:
        verb = {"start": "Started", "stage": "Moved", "show": "Active", "end": "Ended"}[args.action]
        print(f"{verb} topic {topic['slug']}: size {topic['size']}, "
              f"stage {topic['stage']}, dir {topic['dir']}")
    return 0


def _topic_dir_arg(cwd: Path, given: str | None) -> str | None:
    """--dir is relative to cwd; store it relative to the repo root, with forward slashes."""
    if not given:
        return None
    path = (cwd / given).resolve()
    try:
        return path.relative_to(state.repo_root(cwd).resolve()).as_posix()
    except ValueError:
        return path.as_posix()  # outside the repo: keep it absolute


if __name__ == "__main__":
    sys.exit(main())
