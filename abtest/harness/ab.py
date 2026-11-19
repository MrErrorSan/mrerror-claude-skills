"""A/B harness: the same cases under Anvil (A), Superpowers (S) and no plugin (V).

    python abtest/harness/ab.py run    --suite pilot --cases c1-typo,c2-top-n --arms A,S,V --runs 1
    python abtest/harness/ab.py judge  --suite pilot
    python abtest/harness/ab.py report --suite pilot

Each run: a fresh git repo outside this checkout, an isolated `claude -p` session
(--setting-sources project: Saad's global CLAUDE.md and the fixture's CLAUDE.md load; no
installed plugins, no loose user skills), a simulated Saad answering via --resume, then
hidden tests and metrics. Raw data goes to RUN_ROOT; summaries to abtest/results/<suite>/.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import difflib
import io
import json
import tarfile
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ABTEST = HERE.parent
REPO = ABTEST.parent
CASES = ABTEST / "cases"
RESULTS = ABTEST / "results"
RUN_ROOT = Path(os.environ.get("ABTEST_RUN_ROOT",
                               Path(os.environ.get("LOCALAPPDATA", "/tmp")) / "Temp" / "anvil-abtest"))
SP_DIR = Path(os.environ.get(
    "ABTEST_SP_DIR",
    Path.home() / ".claude/plugins/cache/claude-plugins-official/superpowers/7.0.2"))
ANVIL_DIR = REPO / "plugins" / "anvil"
# O: the original Anvil (main, 0.1.0: a text-only governor over Superpowers) loaded together
# with Superpowers, as it ran. Snapshot made with `git archive main plugins/anvil`, with
# plugin.json's marketplace dependencies removed (Superpowers is loaded directly instead).
OG_DIR = RUN_ROOT / "_plugins" / "anvil-og-46b7535" / "plugins" / "anvil"
ARMS = {"A": ANVIL_DIR, "S": SP_DIR, "V": None, "O": [OG_DIR, SP_DIR]}
AGENT_MODEL = os.environ.get("ABTEST_MODEL", "claude-opus-5-5")
AGENT_EFFORT = os.environ.get("ABTEST_EFFORT", "high")
SIM_MODEL = os.environ.get("ABTEST_SIM_MODEL", "claude-sonnet-5-5")
JUDGE_MODEL = os.environ.get("ABTEST_JUDGE_MODEL", "claude-opus-5-5")
IGNORE_DIRS = {".git", "__pycache__", "_hidden", ".pytest_cache", ".venv", "node_modules"}
CLAUDE_BIN = shutil.which("claude") or "claude"
PRINT_LOCK = threading.Lock()


def log(msg: str) -> None:
    with PRINT_LOCK:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def child_env() -> dict:
    """Environment for child claude processes: no link back to this session."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC_"))}
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def rmtree(path: Path) -> None:
    """shutil.rmtree that also removes read-only files (git objects on Windows)."""
    def onexc(func, p, _exc):
        os.chmod(p, 0o700)
        func(p)
    shutil.rmtree(path, onexc=onexc)


def sh(args, cwd=None, timeout=120, check=False, input=None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, check=check, input=input)


def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGKILL)


def run_claude(args: list[str], cwd: Path, out_path: Path | None, timeout_s: float,
               stdin_text: str | None = None) -> tuple[int, str, bool]:
    """Run claude; stream stdout to out_path (or capture). Returns (rc, stdout, timed_out)."""
    kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    fh = open(out_path, "w", encoding="utf-8") if out_path else subprocess.PIPE
    proc = subprocess.Popen([CLAUDE_BIN, *args], cwd=cwd, env=child_env(), text=True,
                            encoding="utf-8", errors="replace",
                            stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
                            stdout=fh, stderr=subprocess.PIPE, **kw)
    try:
        out, err = proc.communicate(stdin_text, timeout=max(timeout_s, 5))
        timed_out = False
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        out, err = proc.communicate()
        timed_out = True
    if out_path:
        fh.close()
        out = out_path.read_text(encoding="utf-8", errors="replace")
        if err:
            out_path.with_suffix(".err").write_text(err, encoding="utf-8")
    return proc.returncode, out or "", timed_out


# ----------------------------------------------------------------------------- traces

def parse_stream(text: str) -> dict:
    """Digest one stream-json turn: result fields, tool calls, texts, skills."""
    d = {"result": None, "texts": [], "tools": [], "init": None, "tool_errors": 0, "hooks": []}
    for line in text.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        t = e.get("type")
        if t == "system" and e.get("subtype") == "init":
            d["init"] = {"plugins": [p.get("name") for p in e.get("plugins", [])],
                         "skills": e.get("skills", []), "model": e.get("model")}
        elif t == "system" and e.get("subtype") == "hook_response":
            d["hooks"].append(e.get("hook_name"))
        elif t == "assistant":
            sub = e.get("parent_tool_use_id") is not None
            for c in e.get("message", {}).get("content", []) or []:
                if c.get("type") == "text" and not sub:
                    d["texts"].append(c.get("text", ""))
                elif c.get("type") == "tool_use":
                    d["tools"].append({"name": c.get("name"), "input": c.get("input", {}), "sub": sub})
        elif t == "user":
            for c in (e.get("message", {}).get("content") or []):
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                    d["tool_errors"] += 1
        elif t == "result":
            d["result"] = {k: e.get(k) for k in ("subtype", "is_error", "duration_ms", "duration_api_ms",
                                                  "num_turns", "total_cost_usd", "usage", "result",
                                                  "session_id", "modelUsage")}
    return d


def tool_stats(turns: list[dict], test_re: str) -> dict:
    tools = [t for d in turns for t in d["tools"]]
    names: dict[str, int] = {}
    for t in tools:
        names[t["name"]] = names.get(t["name"], 0) + 1
    bash = [str(t["input"].get("command", "")) for t in tools if t["name"] == "Bash"]
    skills = [str(t["input"].get("skill", "")) for t in tools if t["name"] == "Skill"]
    agents = [t for t in tools if t["name"] in ("Agent", "Task")]
    return {
        "tool_calls": len(tools),
        "tool_calls_subagents": sum(1 for t in tools if t["sub"]),
        "by_tool": names,
        "test_runs": sum(1 for c in bash if re.search(test_re, c)),
        "test_runs_main": sum(1 for t in tools if t["name"] == "Bash" and not t["sub"]
                              and re.search(test_re, str(t["input"].get("command", "")))),
        "skills": skills,
        "subagents": len(agents),
        "subagent_types": [str(a["input"].get("subagent_type", "")) for a in agents],
        "tool_errors": sum(d["tool_errors"] for d in turns),
        "ask_user_question": names.get("AskUserQuestion", 0),
    }


# ----------------------------------------------------------------------------- simulator

def simulate(case: dict, history: list[dict], latest: str, run_dir: Path, n: int) -> dict:
    tmpl = (HERE / "prompts" / "simulator.md").read_text(encoding="utf-8")
    hist = []
    for h in history:
        who = "AGENT" if h["role"] == "agent" else "SAAD"
        text = h["text"] if who == "SAAD" else (h["text"][:2500] + (" [...]" if len(h["text"]) > 2500 else ""))
        hist.append(f"--- {who}:\n{text}")
    prompt = (tmpl.replace("{brief}", case["brief"])
              .replace("{history}", "\n".join(hist) or "(none)")
              .replace("{latest}", latest[-14000:] or "(the agent said nothing)"))
    for attempt in range(3):
        rc, out, _ = run_claude(["-p", "--setting-sources", "", "--model", SIM_MODEL, "--tools", "",
                                 "--output-format", "json", "--no-session-persistence"],
                                cwd=run_dir, out_path=None, timeout_s=300, stdin_text=prompt)
        try:
            res = json.loads(out)
            text = res.get("result", "")
            m = re.search(r"\{.*\}", text, re.S)
            obj = json.loads(m.group(0))
            obj["_cost"] = res.get("total_cost_usd", 0)
            return obj
        except Exception:  # noqa: BLE001 - retry on any parse failure
            (run_dir / f"sim-{n}-attempt{attempt}.txt").write_text(out, encoding="utf-8")
    return {"kind": "other", "reply": "continue, your call", "done": False, "delivered_change": False,
            "_cost": 0, "_sim_failed": True}


# ----------------------------------------------------------------------------- one run

def make_repo(case_dir: Path, repo: Path) -> str:
    shutil.copytree(case_dir / "files", repo)
    g = lambda *a: sh(["git", *a], cwd=repo, check=True)  # noqa: E731
    g("init", "-q", "-b", "main")
    g("config", "user.name", "Saad Test")
    g("config", "user.email", "saad.test@example.com")
    g("config", "core.autocrlf", "false")
    g("add", "-A")
    g("commit", "-q", "-m", "initial version")
    return sh(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()


def run_one(suite: str, case: dict, arm: str, k: int) -> dict:
    run_id = f"{case['id']}-{arm}-r{k}"
    run_dir = RUN_ROOT / suite / run_id
    meta_path = RESULTS / suite / "runs" / f"{run_id}.json"
    if meta_path.exists() and json.loads(meta_path.read_text(encoding="utf-8")).get("status") == "complete":
        log(f"skip {run_id} (complete)")
        return json.loads(meta_path.read_text(encoding="utf-8"))
    if run_dir.exists():
        rmtree(run_dir)
    run_dir.mkdir(parents=True)
    repo = run_dir / run_id            # unique name: Superpowers' global worktree dirs key on it
    base = make_repo(CASES / case["id"], repo)
    sid = str(uuid.uuid4())
    plugin = ARMS[arm]
    common = ["--setting-sources", "project", "--model", AGENT_MODEL, "--effort", AGENT_EFFORT,
              "--permission-mode", "bypassPermissions", "--disallowedTools", "AskUserQuestion",
              "--output-format", "stream-json", "--verbose"]
    for pdir in (plugin if isinstance(plugin, list) else [plugin] if plugin else []):
        common += ["--plugin-dir", str(pdir)]
    deadline = time.time() + case["timeout_min"] * 60
    history, turns, sims = [], [], []
    message = case["request"]
    status, end_reason = "complete", "done"
    agent_ms = 0
    wall0 = time.time()
    log(f"start {run_id}")
    for n in range(case["max_user_turns"] + 1):
        # The message goes on stdin: as an argument, a reply starting with "--top" was parsed
        # as a CLI option and crashed the turn (c2, S and V arms, suite "full").
        args = ["-p", *(["--session-id", sid] if n == 0 else ["--resume", sid]), *common]
        t0 = time.time()
        rc, out, timed_out = run_claude(args, cwd=repo, out_path=run_dir / f"turn-{n}.jsonl",
                                        timeout_s=deadline - time.time(), stdin_text=message)
        d = parse_stream(out)
        d["wall_s"] = round(time.time() - t0, 1)
        d["rc"] = rc
        turns.append(d)
        agent_ms += (d["result"] or {}).get("duration_ms") or int(d["wall_s"] * 1000)
        history.append({"role": "user", "text": message})
        latest = "\n\n".join(d["texts"]) or ((d["result"] or {}).get("result") or "")
        history.append({"role": "agent", "text": latest})
        if timed_out:
            status, end_reason = "timeout", "timeout"
            break
        if d["result"] is None or (d["result"].get("is_error") and d["result"].get("subtype") != "success"):
            err = (run_dir / f"turn-{n}.err").read_text(encoding="utf-8") if (run_dir / f"turn-{n}.err").exists() else ""
            if re.search(r"rate.?limit|usage limit|overloaded|529|credit", out[-3000:] + err, re.I):
                status, end_reason = "infra_error", "rate_limit_or_overload"
                break
        if n == case["max_user_turns"]:
            end_reason = "max_user_turns"
            break
        sim = simulate(case, history[:-1], latest, run_dir, n)
        sim["after_turn"] = n
        sims.append(sim)
        if sim.get("done"):
            break
        message = sim.get("reply") or "continue"
    wall_s = round(time.time() - wall0, 1)
    (run_dir / "sim.json").write_text(json.dumps(sims, indent=1), encoding="utf-8")
    (run_dir / "conversation.json").write_text(json.dumps(history, indent=1), encoding="utf-8")
    log(f"graded? {run_id} end={end_reason} turns={len(turns)} agent_s={agent_ms/1000:.0f}")
    grade = grade_run(case, repo, base, run_dir)
    # total_cost_usd and modelUsage are cumulative over --resume calls and include subagents;
    # usage and num_turns are per call, main thread only. So take the last call's modelUsage.
    last = next((d["result"] for d in reversed(turns) if d["result"]), {}) or {}
    model_usage = last.get("modelUsage") or {}
    usage = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
    for mu in model_usage.values():
        usage["input"] += mu.get("inputTokens", 0) or 0
        usage["output"] += mu.get("outputTokens", 0) or 0
        usage["cache_read"] += mu.get("cacheReadInputTokens", 0) or 0
        usage["cache_write"] += mu.get("cacheCreationInputTokens", 0) or 0
    cost_by_model = {k: round(v.get("costUSD", 0) or 0, 4) for k, v in model_usage.items()}
    meta = {
        "run_id": run_id, "suite": suite, "case": case["id"], "arm": arm, "replicate": k,
        "status": status, "end_reason": end_reason,
        "plugin": [str(x) for x in plugin] if isinstance(plugin, list) else (str(plugin) if plugin else None),
        "plugin_rev": plugin_rev(arm),
        "model": AGENT_MODEL, "effort": AGENT_EFFORT,
        "loaded_plugins": (turns[0]["init"] or {}).get("plugins") if turns else None,
        "agent_time_s": round(agent_ms / 1000, 1), "wall_time_s": wall_s,
        "agent_invocations": len(turns),
        "user_turns": len(turns) - 1,
        "agent_num_turns": sum((d["result"] or {}).get("num_turns") or 0 for d in turns),
        "cost_usd": round(max([(d["result"] or {}).get("total_cost_usd") or 0 for d in turns] or [0]), 4),
        "cost_by_model": cost_by_model,
        "sim_cost_usd": round(sum(s.get("_cost", 0) or 0 for s in sims), 4),
        "tokens": usage,
        "sim_kinds": [s.get("kind") for s in sims],
        "change_delivered_after_turn": next((s["after_turn"] for s in sims if s.get("delivered_change")), None),
        "tools": tool_stats(turns, case.get("test_cmd_re", "unittest|pytest")),
        "hooks_fired": sorted({h for d in turns for h in d["hooks"] if h}),
        "grade": grade,
        "run_dir": str(run_dir),
    }
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=1), encoding="utf-8")
    cleanup_external_worktrees(repo, run_dir)
    h = grade["hidden"]
    log(f"done  {run_id} {status} agent={meta['agent_time_s']}s cost=${meta['cost_usd']} "
        f"user_turns={meta['user_turns']} hidden={h['passed']}/{h['total']}")
    return meta


_REV_CACHE: dict[str, str] = {}


def plugin_rev(arm: str) -> str | None:
    if arm == "V":
        return None
    if arm not in _REV_CACHE:
        if arm == "A":
            rev = sh(["git", "rev-parse", "--short", "HEAD"], cwd=REPO).stdout.strip()
            dirty = sh(["git", "status", "--porcelain", "--", "plugins/anvil"], cwd=REPO).stdout.strip()
            _REV_CACHE[arm] = f"anvil@{rev}{'+dirty' if dirty else ''}"
        elif arm == "O":
            _REV_CACHE[arm] = f"anvil-og@main:46b7535 (0.1.0) + superpowers@{SP_DIR.name}"
        else:
            _REV_CACHE[arm] = f"superpowers@{SP_DIR.name}"
    return _REV_CACHE[arm]


def cleanup_external_worktrees(repo: Path, run_dir: Path) -> None:
    """Remove worktrees this run registered outside its own run dir (e.g. ~/.config/superpowers)."""
    out = sh(["git", "worktree", "list", "--porcelain"], cwd=repo).stdout
    for line in out.splitlines():
        if line.startswith("worktree "):
            p = Path(line[9:].strip())
            try:
                p.resolve().relative_to(run_dir.resolve())
            except ValueError:
                if p.exists() and (p / ".git").is_file():
                    sh(["git", "worktree", "remove", "--force", str(p)], cwd=repo)


# ----------------------------------------------------------------------------- grading

def snapshot_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=lambda d, names: [n for n in names if n in IGNORE_DIRS or n.endswith(".db")])


def candidates(repo: Path, work: Path) -> list[tuple[str, Path]]:
    """Every place the result may live: worktrees (with uncommitted work) and branch heads."""
    out, seen = [], set()
    wt = sh(["git", "worktree", "list", "--porcelain"], cwd=repo).stdout
    i = 0
    for line in wt.splitlines():
        if line.startswith("worktree "):
            p = Path(line[9:].strip())
            if p.exists():
                dst = work / f"wt{i}"
                snapshot_tree(p, dst)
                out.append((f"worktree:{p.name}", dst))
                i += 1
        if line.startswith("branch "):
            seen.add(line[7:].strip().replace("refs/heads/", ""))
    for br in sh(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], cwd=repo).stdout.split():
        if br in seen:
            continue
        dst = work / f"br-{re.sub(r'[^A-Za-z0-9_.-]', '_', br)}"
        dst.mkdir(parents=True)
        arch = subprocess.run(["git", "archive", "--format=tar", br], cwd=repo, capture_output=True)
        with tarfile.open(fileobj=io.BytesIO(arch.stdout)) as tf:
            tf.extractall(dst, filter="data")
        out.append((f"branch:{br}", dst))
    return out


def run_hidden(case_dir: Path, tree: Path) -> dict:
    hid = tree / "_hidden"
    shutil.copytree(case_dir / "hidden", hid)
    reg = hid / "regression"
    reg.mkdir()
    (reg / "__init__.py").write_text("", encoding="utf-8")
    for f in (case_dir / "files" / "tests").glob("test_*.py"):
        text = f.read_text(encoding="utf-8")
        (reg / f.name).write_text(text, encoding="utf-8")
    try:
        r = sh([sys.executable, str(HERE / "hidden_runner.py")], cwd=tree, timeout=300)
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:  # noqa: BLE001
        res = {"tests": [], "ran": 0, "error": f"{type(e).__name__}: {e}"}
    by = {}
    for t in res["tests"]:
        c = by.setdefault(t["category"], {"passed": 0, "total": 0})
        c["total"] += 1
        c["passed"] += t["outcome"] == "pass"
    res["by_category"] = by
    res["passed"] = sum(c["passed"] for c in by.values())
    res["total"] = sum(c["total"] for c in by.values())
    return res


def own_suite(tree: Path) -> dict:
    if not (tree / "tests").exists():
        return {"ran": 0, "ok": None}
    t0 = time.time()
    r = sh([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=tree, timeout=600)
    m = re.search(r"Ran (\d+) tests?", r.stderr)
    return {"ran": int(m.group(1)) if m else 0, "ok": r.returncode == 0, "seconds": round(time.time() - t0, 1),
            "tail": r.stderr[-400:] if r.returncode else ""}


def kind_of(path: str) -> str:
    p = path.replace("\\", "/")
    name = p.rsplit("/", 1)[-1]
    if p.startswith("tests/") or name.startswith("test_") or "/tests/" in p:
        return "tests"
    if p.endswith(".md") or p.startswith("docs/"):
        return "docs"
    if p.endswith(".py"):
        return "code"
    return "other"


def tree_files(root: Path) -> dict[str, str]:
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and not any(part in IGNORE_DIRS for part in p.relative_to(root).parts) \
                and not p.name.endswith((".db", ".pyc")):
            try:
                out[p.relative_to(root).as_posix()] = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                out[p.relative_to(root).as_posix()] = "<binary>"
    return out


def eol_style(data: bytes) -> str | None:
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    return None if not (crlf or lf) else ("crlf" if crlf and not lf else "lf" if lf and not crlf else "mixed")


def eol_changes(fixture: Path, tree: Path) -> list[str]:
    """Files present in both whose line-ending style changed (read_text hides this)."""
    out = []
    for f in fixture.rglob("*"):
        if f.is_file() and not any(p in IGNORE_DIRS for p in f.relative_to(fixture).parts):
            g = tree / f.relative_to(fixture)
            if g.is_file():
                a, b = eol_style(f.read_bytes()), eol_style(g.read_bytes())
                if a and b and a != b:
                    out.append(f"{f.relative_to(fixture).as_posix()} {a}->{b}")
    return sorted(out)


def diff_stats(before: dict, after: dict) -> tuple[dict, str]:
    stats = {k: {"files": 0, "added": 0, "removed": 0} for k in ("code", "tests", "docs", "other")}
    chunks = []
    for path in sorted(set(before) | set(after)):
        a, b = before.get(path, ""), after.get(path, "")
        if a == b:
            continue
        lines = list(difflib.unified_diff(a.splitlines(), b.splitlines(), f"a/{path}", f"b/{path}", lineterm=""))
        k = kind_of(path)
        stats[k]["files"] += 1
        stats[k]["added"] += sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
        stats[k]["removed"] += sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
        if k in ("code", "tests"):
            chunks.append("\n".join(lines))
    return stats, "\n".join(chunks)


def grade_run(case: dict, repo: Path, base: str, run_dir: Path) -> dict:
    case_dir = CASES / case["id"]
    work = run_dir / "_grade"
    rmtree(work) if work.exists() else None
    work.mkdir()
    fixture = tree_files(case_dir / "files")
    best = None
    for name, tree in candidates(repo, work):
        if tree_files(tree) == fixture:
            continue  # untouched
        h = run_hidden(case_dir, tree)
        cand = {"name": name, "hidden": h, "tree": tree}
        if best is None or h["passed"] > best["hidden"]["passed"]:
            best = cand
    if best is None:  # nothing changed anywhere: grade the fixture as-is
        tree = work / "untouched"
        snapshot_tree(case_dir / "files", tree)
        best = {"name": "untouched", "hidden": run_hidden(case_dir, tree), "tree": tree}
    after = tree_files(best["tree"])
    stats, diff = diff_stats(fixture, after)
    (run_dir / "final.diff").write_text(diff, encoding="utf-8")
    docs = sorted(p for p in set(after) - set(fixture) if p.endswith(".md"))
    changed_docs = sorted(p for p in set(after) & set(fixture) if p.endswith(".md") and after[p] != fixture[p])
    docs_dir = run_dir / "docs"
    for p in docs + changed_docs:
        dst = docs_dir / p
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(after[p], encoding="utf-8")
    log_all = sh(["git", "log", "--all", "--format=%H%x00%B%x01", f"^{base}"], cwd=repo).stdout
    msgs = [m.split("\x00", 1)[-1] for m in log_all.split("\x01") if m.strip()]
    status = sh(["git", "status", "--porcelain"], cwd=repo).stdout
    doc_rule = None
    if case.get("doc_rule"):
        stray = [p for p in docs if not re.match(r"docs/[^/]+/.+\.md$", p) and p != "docs/decisions.md"]
        doc_rule = {"new_docs_outside_rule": stray,
                    "decisions_md_updated": after.get("docs/decisions.md") != fixture.get("docs/decisions.md")}
    anvil_state = repo / ".git" / "anvil"
    if anvil_state.exists():
        shutil.copytree(anvil_state, run_dir / "anvil-state", dirs_exist_ok=True)
    return {
        "eol_changes": eol_changes(case_dir / "files", best["tree"]),
        "result_location": best["name"],
        "hidden": {k: best["hidden"][k] for k in ("passed", "total", "by_category")},
        "hidden_failures": [t["id"].rsplit(".", 1)[-1] for t in best["hidden"]["tests"] if t["outcome"] != "pass"],
        "own_suite": own_suite(best["tree"]),
        "diff": stats,
        "new_docs": docs,
        "changed_docs": changed_docs,
        "commits": len(msgs),
        "claude_trailers": sum(1 for m in msgs if re.search(r"Co-Authored-By:.*(Claude|anthropic)", m, re.I)),
        "uncommitted_in_main": bool(status.strip()),
        "branches": sh(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"], cwd=repo).stdout.split(),
        "worktrees": sum(1 for l in sh(["git", "worktree", "list"], cwd=repo).stdout.splitlines() if l.strip()),
        "doc_rule": doc_rule,
    }


# ----------------------------------------------------------------------------- judge

SCRUB = re.compile(r"(?i)\b(anvil|superpowers|using-superpowers|brainstorming|writing-plans|executing-plans|"
                   r"subagent-driven-development|systematic-debugging|test-driven-development|"
                   r"verification-before-completion|finishing-a-development-branch|requesting-code-review|"
                   r"dispatching-parallel-agents|using-git-worktrees|afk)\b")


def scrub(text: str) -> str:
    return SCRUB.sub("[workflow]", text)


def run_bundle(meta: dict, label: str) -> str:
    rd = Path(meta["run_dir"])
    conv = json.loads((rd / "conversation.json").read_text(encoding="utf-8"))
    parts = [f"##### RUN {label}"]
    parts.append("--- Conversation (user messages and the agent's visible text; long messages shortened):")
    for h in conv:
        t = h["text"]
        if h["role"] == "agent" and len(t) > 3500:
            t = t[:1800] + "\n[...]\n" + t[-1500:]
        parts.append(f"[{'USER' if h['role'] == 'user' else 'AGENT'}] {t}")
    g = meta["grade"]
    parts.append(f"--- Facts: commits={g['commits']}, claude co-author trailers={g['claude_trailers']}, "
                 f"uncommitted changes left={g['uncommitted_in_main']}, result lives in {g['result_location']}, "
                 f"new docs={g['new_docs']}, changed docs={g['changed_docs']}, "
                 f"own test suite: {g['own_suite'].get('ran')} tests, ok={g['own_suite'].get('ok')}, "
                 f"test-suite runs during the session={meta['tools']['test_runs']}, "
                 f"subagents dispatched={meta['tools']['subagents']}")
    diff = (rd / "final.diff").read_text(encoding="utf-8")
    parts.append("--- Final code and test diff:\n" + (diff[:16000] + ("\n[diff truncated]" if len(diff) > 16000 else "")))
    for p in (g["new_docs"] + g["changed_docs"])[:4]:
        f = rd / "docs" / p
        if f.exists():
            body = f.read_text(encoding="utf-8")
            parts.append(f"--- Document {p}:\n" + body[:5000] + ("\n[truncated]" if len(body) > 5000 else ""))
    return scrub("\n".join(parts))


def judge(suite: str, metas: list[dict] | None = None, out_dir: Path | None = None) -> None:
    metas = load_metas(suite) if metas is None else metas
    out_dir = out_dir or RESULTS / suite / "judge"
    out_dir.mkdir(parents=True, exist_ok=True)
    groups: dict[tuple[str, int], list[dict]] = {}
    for m in metas:
        if m["status"] == "complete":
            groups.setdefault((m["case"], m["replicate"]), []).append(m)
    tmpl = (HERE / "prompts" / "judge.md").read_text(encoding="utf-8")
    for (cid, k), ms in sorted(groups.items()):
        dst = out_dir / f"{cid}-r{k}.json"
        if dst.exists() or len(ms) < 2:
            continue
        case = load_case(cid)
        rng = random.Random(f"{cid}-{k}")
        ms = sorted(ms, key=lambda m: m["arm"])
        rng.shuffle(ms)
        labels = (list("XYZ") if len(ms) <= 3 else list("WXYZ") if len(ms) == 4 else list("KLMNPQRT"))[:len(ms)]
        prompt = (tmpl.replace("{n}", str(len(ms))).replace("{labels}", ", ".join(labels))
                  .replace("{judge_notes}", case["judge_notes"]).replace("{request}", case["request"])
                  .replace("{brief}", case["brief"])
                  .replace("{runs}", "\n\n".join(run_bundle(m, l) for m, l in zip(ms, labels))))
        log(f"judge {cid} r{k} ({len(prompt)//1000}k chars)")
        verdict = None
        for _ in range(3):
            rc, out, _t = run_claude(["-p", "--setting-sources", "", "--model", JUDGE_MODEL, "--tools", "",
                                      "--effort", "high", "--output-format", "json", "--no-session-persistence"],
                                     cwd=RUN_ROOT, out_path=None, timeout_s=900, stdin_text=prompt)
            try:
                text = json.loads(out)["result"]
                verdict = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
                break
            except Exception:  # noqa: BLE001
                continue
        if verdict is None:
            log(f"judge failed {cid} r{k}")
            continue
        verdict["label_to_arm"] = {l: m["arm"] for m, l in zip(ms, labels)}
        dst.write_text(json.dumps(verdict, indent=1), encoding="utf-8")


# ----------------------------------------------------------------------------- report

def load_case(cid: str) -> dict:
    return json.loads((CASES / cid / "case.json").read_text(encoding="utf-8"))


def load_metas(suite: str) -> list[dict]:
    d = RESULTS / suite / "runs"
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(d.glob("*.json"))] if d.exists() else []


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else round((xs[n // 2 - 1] + xs[n // 2]) / 2, 2)


def report(suite: str, metas: list[dict] | None = None, out: Path | None = None) -> None:
    metas = load_metas(suite) if metas is None else metas
    out = out or RESULTS / suite
    jdir = out / "judge"
    verdicts = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                for p in jdir.glob("*.json")} if jdir.exists() else {}
    rows = []
    for m in metas:
        g = m["grade"]
        h = g["hidden"]["by_category"]
        jv = verdicts.get(f"{m['case']}-r{m['replicate']}")
        js = None
        if jv:
            lab = next((l for l, a in jv["label_to_arm"].items() if a == m["arm"]), None)
            js = jv["scores"].get(lab, {})
            rank = jv["ranking"].index(lab) + 1 if lab in jv.get("ranking", []) else None
        rows.append({
            "case": m["case"], "arm": m["arm"], "rep": m["replicate"], "status": m["status"],
            "end": m["end_reason"],
            "hidden": f"{g['hidden']['passed']}/{g['hidden']['total']}",
            "hidden_pct": round(100 * g["hidden"]["passed"] / g["hidden"]["total"]) if g["hidden"]["total"] else 0,
            **{f"h_{c}": f"{v['passed']}/{v['total']}" for c, v in h.items()},
            "agent_s": m["agent_time_s"], "wall_s": m["wall_time_s"], "cost": m["cost_usd"],
            "user_turns": m["user_turns"], "test_runs": m["tools"]["test_runs"],
            "subagents": m["tools"]["subagents"], "tool_calls": m["tools"]["tool_calls"],
            "code_lines": g["diff"]["code"]["added"] + g["diff"]["code"]["removed"],
            "test_lines": g["diff"]["tests"]["added"] + g["diff"]["tests"]["removed"],
            "docs": len(g["new_docs"]) + len(g["changed_docs"]),
            "own_tests": g["own_suite"].get("ran"), "own_ok": g["own_suite"].get("ok"),
            "trailers": g["claude_trailers"], "location": g["result_location"],
            "judge_overall": (js or {}).get("overall"), "judge_rank": rank if jv else None,
            "skills": m["tools"]["skills"],
            "failures": g["hidden_failures"],
            "eol_changes": len(g.get("eol_changes", [])),
        })
    (out / "summary.json").write_text(json.dumps({"rows": rows, "verdicts": verdicts}, indent=1), encoding="utf-8")
    lines = [f"# A/B results: suite `{suite}`", "",
             f"Generated {time.strftime('%Y-%m-%d %H:%M')}. Arms: A = Anvil, S = Superpowers 7.0.2, V = no plugin. "
             f"Agent model {AGENT_MODEL} at effort {AGENT_EFFORT}.", "",
             "## Per case (median over replicates)", "",
             "| Case | Arm | Hidden pass % | Agent time s | Cost $ | User turns | Suite runs | Subagents | Code lines | Test lines | Docs | EOL rewrites | Judge (1-5) | Judge rank |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    by: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by.setdefault((r["case"], r["arm"]), []).append(r)
    for (c, a), rs in sorted(by.items()):
        lines.append("| " + " | ".join(str(x) for x in [
            c, a, med([r["hidden_pct"] for r in rs]), med([r["agent_s"] for r in rs]), med([r["cost"] for r in rs]),
            med([r["user_turns"] for r in rs]), med([r["test_runs"] for r in rs]), med([r["subagents"] for r in rs]),
            med([r["code_lines"] for r in rs]), med([r["test_lines"] for r in rs]), med([r["docs"] for r in rs]),
            med([r["eol_changes"] for r in rs]),
            med([r["judge_overall"] for r in rs]), med([r["judge_rank"] for r in rs])]) + " |")
    lines += ["", "## Totals per arm", "", "| Arm | Runs | Hidden passed | Perfect runs | Agent min | Cost $ | User turns | Suite runs | EOL rewrites | Judge mean | First places |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    first = {}
    for v in verdicts.values():
        if v.get("ranking"):
            a = v["label_to_arm"].get(v["ranking"][0])
            first[a] = first.get(a, 0) + 1
    for a in sorted({r["arm"] for r in rows}):
        rs = [r for r in rows if r["arm"] == a]
        hp = sum(int(r["hidden"].split("/")[0]) for r in rs)
        ht = sum(int(r["hidden"].split("/")[1]) for r in rs)
        js = [r["judge_overall"] for r in rs if r["judge_overall"] is not None]
        lines.append("| " + " | ".join(str(x) for x in [
            a, len(rs), f"{hp}/{ht}", sum(r["hidden_pct"] == 100 for r in rs), round(sum(r["agent_s"] for r in rs) / 60),
            round(sum(r["cost"] for r in rs), 2), sum(r["user_turns"] for r in rs), sum(r["test_runs"] for r in rs),
            sum(r["eol_changes"] for r in rs), round(sum(js) / len(js), 2) if js else None, first.get(a, 0)]) + " |")
    lines += ["", "## Every run", "",
              "| Run | Status | End | Hidden | core | edge | brief | regr | Agent s | Wall s | $ | User turns | Suite runs | Own tests | Trailers | Result in | Skills |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["case"], r["rep"], r["arm"])):
        lines.append("| " + " | ".join(str(x) for x in [
            f"{r['case']} {r['arm']} r{r['rep']}", r["status"], r["end"], r["hidden"], r.get("h_core", "-"),
            r.get("h_edge", "-"), r.get("h_brief", "-"), r.get("h_regression", "-"), r["agent_s"], r["wall_s"],
            r["cost"], r["user_turns"], r["test_runs"], f"{r['own_tests']} {'ok' if r['own_ok'] else 'FAIL' if r['own_ok'] is False else ''}",
            r["trailers"], r["location"], ", ".join(sorted(set(r["skills"])))[:80]]) + " |")
    lines += ["", "## Hidden-test failures", ""]
    for r in sorted(rows, key=lambda r: (r["case"], r["rep"], r["arm"])):
        if r["failures"]:
            lines.append(f"- **{r['case']} {r['arm']} r{r['rep']}**: {', '.join(r['failures'])}")
    if verdicts:
        lines += ["", "## Judge summaries (blind; labels mapped back to arms)", ""]
        for key, v in sorted(verdicts.items()):
            m = v["label_to_arm"]
            rank = " > ".join(m.get(l, l) for l in v.get("ranking", []))
            lines.append(f"### {key}: {rank}")
            lines.append("")
            lines.append(re.sub(r"\b([XYZ])\b", lambda mm: m.get(mm.group(1), mm.group(1)), v.get("summary", "")))
            lines.append("")
            for lab, s in sorted(v["scores"].items(), key=lambda kv: m.get(kv[0], kv[0])):
                probs = "; ".join(re.sub(r"\b([XYZ])\b", lambda mm: m.get(mm.group(1), mm.group(1)), p)
                                  for p in s.get("problems", []))
                lines.append(f"- **{m.get(lab, lab)}** overall {s.get('overall')} (match {s.get('match')}, "
                             f"simplicity {s.get('simplicity')}, tests {s.get('tests')}, process {s.get('process_fit')}, "
                             f"communication {s.get('communication')}, rules {s.get('rules')}): {probs}")
            lines.append("")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"wrote {out / 'report.md'}")


# ----------------------------------------------------------------------------- main

def set_metas(sets: str) -> list[dict]:
    """--sets "full:A=A1,full:S=S,v2:A=A2": runs from several suites, arms relabelled."""
    out = []
    for spec in sets.split(","):
        src, label = spec.split("=")
        suite, arm = src.split(":")
        for m in load_metas(suite):
            if m["arm"] == arm:
                out.append({**m, "arm": label, "source_suite": suite})
    return out


def backfill_eol(suite: str) -> None:
    for p in sorted((RESULTS / suite / "runs").glob("*.json")):
        m = json.loads(p.read_text(encoding="utf-8"))
        repo = Path(m["run_dir"]) / m["run_id"]
        if "eol_changes" in m["grade"] or not repo.exists():
            continue
        m["grade"]["eol_changes"] = eol_changes(CASES / m["case"] / "files", repo)
        p.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log(f"eol backfilled for {suite}")


def selftest() -> bool:
    """Hidden tests must fail on the untouched fixture (except regression) and pass on reference/."""
    import tempfile
    ok = True
    for cdir in sorted(p for p in CASES.iterdir() if (p / "case.json").exists()):
        with tempfile.TemporaryDirectory() as tmp:
            raw, ref = Path(tmp) / "raw", Path(tmp) / "ref"
            snapshot_tree(cdir / "files", raw)
            snapshot_tree(cdir / "files", ref)
            shutil.copytree(cdir / "reference", ref, dirs_exist_ok=True)
            r0, r1 = run_hidden(cdir, raw), run_hidden(cdir, ref)
            own = own_suite(ref)
        bad_ref = [t["id"].rsplit(".", 1)[-1] + f" ({t['outcome']}: {t['detail'][-160:]!r})"
                   for t in r1["tests"] if t["outcome"] != "pass"]
        reg0 = r0["by_category"].get("regression", {})
        new0 = sum(v["passed"] for c, v in r0["by_category"].items() if c != "regression")
        good = not bad_ref and reg0.get("passed") == reg0.get("total") and own["ok"] is not False
        ok &= good
        print(f"{'OK ' if good else 'BAD'} {cdir.name}: reference {r1['passed']}/{r1['total']}, "
              f"fixture regression {reg0.get('passed')}/{reg0.get('total')}, fixture new-tests passing {new0} "
              f"(should be low), reference own suite ok={own['ok']}")
        for b in bad_ref:
            print("     ref fails:", b)
    return ok


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "judge", "report", "selftest", "compare", "eol"])
    ap.add_argument("--sets", help='compare: "suite:arm=label,..."')
    ap.add_argument("--suite", required=True)
    ap.add_argument("--cases", default="all")
    ap.add_argument("--arms", default="A,S,V")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--concurrency", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "selftest":
        raise SystemExit(0 if selftest() else 1)
    if a.cmd == "eol":
        return backfill_eol(a.suite)
    if a.cmd == "compare":
        metas, out = set_metas(a.sets), RESULTS / a.suite
        judge(a.suite, metas, out / "judge")
        return report(a.suite, metas, out)
    if a.cmd == "judge":
        return judge(a.suite)
    if a.cmd == "report":
        return report(a.suite)
    case_ids = sorted(p.name for p in CASES.iterdir() if (p / "case.json").exists()) if a.cases == "all" \
        else a.cases.split(",")
    arms = a.arms.split(",")
    jobs = [(load_case(c), arm, k) for k in range(1, a.runs + 1) for c in case_ids for arm in arms]
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    log(f"suite={a.suite} jobs={len(jobs)} concurrency={a.concurrency} run_root={RUN_ROOT} "
        f"anvil={plugin_rev('A')} sp={plugin_rev('S')}")
    with cf.ThreadPoolExecutor(a.concurrency) as ex:
        futs = {ex.submit(run_one, a.suite, c, arm, k): f"{c['id']}-{arm}-r{k}" for c, arm, k in jobs}
        for f in cf.as_completed(futs):
            try:
                f.result()
            except Exception as e:  # noqa: BLE001
                log(f"FAILED {futs[f]}: {type(e).__name__}: {e}")
    report(a.suite)


if __name__ == "__main__":
    main()
