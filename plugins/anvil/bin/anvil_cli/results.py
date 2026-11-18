"""Test-result reuse: record runs against a key of the code state, reuse fresh greens.

The key covers the working tree (via a temp index, so untracked files count and the
real index is untouched), lockfiles at the repo root, python/node/go versions on
PATH, the env vars named in ANVIL_KEY_ENV, and the directory the command runs in.
Records go to results.jsonl in the state directory, which every worktree of the
repo shares.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from . import state

LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock",
             "uv.lock", "Cargo.lock", "go.sum")
TOOLS = (("python", "--version"), ("node", "--version"), ("go", "version"))


def _git(cwd, *args, env=None, input=None) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env=env, input=input, check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()


def tree_key(cwd: Path) -> str:
    """The code-state key of the repo cwd is in. Submodules are unsupported: the
    superproject records the submodule commit, not edits inside a submodule."""
    # --git-path index is the right index in linked worktrees too.
    root, index = map(Path, _git(cwd, "rev-parse", "--path-format=absolute", "--show-toplevel",
                                 "--git-path", "index").splitlines())
    with tempfile.TemporaryDirectory() as tmp:
        tmp_index = Path(tmp) / "index"
        if index.exists():
            shutil.copy2(index, tmp_index)  # keeps the mtime git's racy-clean check relies on
        env = {**os.environ, "GIT_INDEX_FILE": str(tmp_index)}
        # In the temp index only, clear assume-unchanged (lowercase tag) and skip-worktree
        # (S) so add -A sees edits to those files. update-index takes one flag per call.
        tagged = [e.split(" ", 1) for e in _git(root, "ls-files", "-v", "-z", env=env).split("\0")
                  if e]
        for flag, hit in (("--no-assume-unchanged", str.islower),
                          ("--no-skip-worktree", lambda tag: tag in "Ss")):
            paths = [p for tag, p in tagged if hit(tag)]
            if paths:
                _git(root, "update-index", flag, "-z", "--stdin", env=env,
                     input="\0".join(paths) + "\0")
        _git(root, "-c", "core.safecrlf=false", "add", "-A", env=env)
        # The active topic's progress.md is status, not code: editing it must not
        # make recorded results stale.
        topic_dir = state.topic_dir(cwd)
        if topic_dir is not None:
            progress = (topic_dir / "progress.md").resolve()
            if progress.is_relative_to(root.resolve()):
                _git(root, "rm", "--cached", "-q", "--ignore-unmatch", "--",
                     progress.relative_to(root.resolve()).as_posix(), env=env)
        lines = ["tree " + _git(root, "write-tree", env=env)]
    for f in sorted([*(root / n for n in LOCKFILES), *root.glob("requirements*.txt")]):
        if f.is_file():
            lines.append(f"lock {f.name} {hashlib.sha256(f.read_bytes()).hexdigest()}")
    for tool, flag in TOOLS:
        exe = shutil.which(tool)
        if not exe or "WindowsApps" in exe:  # the Microsoft Store stub isn't a toolchain
            continue
        try:
            r = subprocess.run([exe, flag], capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            continue
        lines.append(f"tool {tool} {(r.stdout + r.stderr).strip()}")
    for name in sorted(set(re.split(r"[\s,]+", os.environ.get("ANVIL_KEY_ENV", ""))) - {""}):
        value = os.environ.get(name)
        digest = "unset" if value is None else hashlib.sha256(value.encode()).hexdigest()
        lines.append(f"env {name} {digest}")
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _key_parts(cwd, cmd, scope) -> tuple[str, str, str]:
    """(key, tree, prefix); prefix is cwd relative to the repo root, "" at the root."""
    tree, prefix = tree_key(cwd), _git(cwd, "rev-parse", "--show-prefix")
    raw = "\0".join([tree, prefix, json.dumps(cmd), scope])
    return hashlib.sha256(raw.encode()).hexdigest(), tree, prefix


def result_key(cwd, cmd: list[str], scope: str) -> str:
    return _key_parts(cwd, cmd, scope)[0]


def _key_or_none(cwd, cmd, scope):
    try:
        return _key_parts(cwd, cmd, scope)
    except (subprocess.CalledProcessError, OSError, ValueError):
        return None  # not a git repo, git missing, or odd git output: nothing to key on


def _run(cwd, cmd, scope, external, out):
    """Run cmd, streaming its output to out. Returns (exit code, record or None)."""
    before = _key_or_none(cwd, cmd, scope)
    exe = shutil.which(cmd[0]) or cmd[0]  # finds npm.cmd and friends on Windows
    lines = []
    try:
        proc = subprocess.Popen([exe, *cmd[1:]], cwd=cwd, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except OSError as e:
        print(f"anvil run: cannot start {cmd[0]}: {e}", file=sys.stderr)
        return 127, None
    with proc:
        for raw in proc.stdout:
            line = raw.decode("utf-8", errors="replace")
            out.write(line)
            out.flush()
            lines.append(line.rstrip("\r\n"))
    code = proc.returncode
    if before is None:
        print("anvil run: could not compute the code-state key; result not recorded",
              file=sys.stderr)
        return code, None
    if _key_or_none(cwd, cmd, scope) != before:
        print("anvil run: the code changed during the run; result not recorded", file=sys.stderr)
        return code, None
    output = "\n".join(lines)
    key, tree, prefix = before
    rec = {"key": key, "tree": tree, "prefix": prefix, "cmd": cmd, "scope": scope, "exit": code,
           "tests_ran": count_tests(output),
           "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "summary": "\n".join(lines[-40:])}
    if external:
        rec["external"] = True
    state.append_jsonl(cwd, "results.jsonl", rec, keep=500)
    return code, rec


def run(cwd, cmd, scope="targeted", external=False) -> int:
    return _run(cwd, cmd, scope, external, sys.stdout)[0]


def fresh(cwd, cmd, scope="targeted") -> dict | None:
    """The newest record for this key, if it is a green run that ran tests and isn't external.

    The newest record decides: a failure after a green on the same tree means the
    green is not reused.
    """
    parts = _key_or_none(cwd, cmd, scope)
    if parts is None:
        return None
    for rec in reversed(state.read_jsonl(cwd, "results.jsonl")):
        if rec.get("key") == parts[0]:
            ok = rec.get("exit") == 0 and rec.get("tests_ran", 0) > 0 and not rec.get("external")
            return rec if ok else None
    return None


def count_tests(output: str) -> int:
    """Tests that passed per the summary; 0 if the output shows a failure, or is unknown."""
    if (any(int(n) for n in re.findall(r"\b(\d+) failed\b", output))  # pytest, vitest, jest
            or re.search(r"^FAILED \(", output, re.M)                    # unittest
            or re.search(r"^FAIL\b", output, re.M)):                     # go test
        return 0
    ran = re.findall(r"^Ran (\d+) tests?\b", output, re.M)  # unittest
    if ran:
        skipped = re.findall(r"\bskipped=(\d+)", output)
        return max(0, sum(map(int, ran)) - sum(map(int, skipped)))
    # vitest "Tests  3 passed (3)", jest "Tests:  3 passed, 3 total"; not "Test Files"/"Test Suites"
    js = re.findall(r"^\s*Tests:?\s+(.*)$", output, re.M)
    if js:
        return sum(int(n) for n in re.findall(r"(\d+) passed", js[-1]))
    py = [l for l in output.splitlines() if re.search(r"\d+ passed\b", l)]  # pytest
    if py:
        return sum(int(n) for n in re.findall(r"(\d+) passed\b", py[-1]))
    # go test: packages that passed
    return len(re.findall(r"^ok\s+\S+\s+(?:[\d.]+s|\(cached\))", output, re.M))


def cmd_run(args) -> int:
    out = sys.stderr if args.json else sys.stdout  # keep stdout pure JSON with --json
    code, rec = _run(Path.cwd(), args.cmd, args.scope, args.external, out)
    if args.json:
        print(json.dumps({"exit": code, "record": rec}, ensure_ascii=False))
    return code


def cmd_fresh(args) -> int:
    rec = fresh(Path.cwd(), args.cmd, args.scope)
    if args.json:
        print(json.dumps(rec, ensure_ascii=False))
    elif rec:
        print(f"Fresh green result: {rec['tests_ran']} tests passed at {rec['ts']} "
              f"(scope {rec['scope']}) on this code state.")
        print(rec["summary"])
    if not rec:
        print(f"anvil fresh: no fresh green result for this code state (scope {args.scope}).",
              file=sys.stderr)
        return 1
    return 0
