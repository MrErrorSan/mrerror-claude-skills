#!/usr/bin/env python3
"""Collect stand-up evidence for one folder and print it as one JSON object.

Standard library only. Read-only: it runs git and (when signed in) gh, reads
Claude Code session files, and never writes anywhere except --out.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

SCHEMA_VERSION = 1
SKIP_DIRS = {"node_modules", ".venv", "venv", "dist", "build", "graphify-out", ".git", "standups", "__pycache__"}
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
ACTIVE_GAP = dt.timedelta(minutes=30)
TICKET_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9}-\d{1,6})\b")
TICKET_STOP = {"UTF", "ISO", "SHA", "RFC", "GPT", "AES", "TLS", "SSL", "WCAG", "HTTP", "CVE", "MD", "X"}
NOISE_PREFIXES = ("<", "Base directory for this skill", "This session is being continued",
                  "Another Claude session sent", "[Request interrupted", "Caveat:")
MAX_PROMPTS, PROMPT_CHARS, MAX_PATHS, SIZE_CAP = 5, 150, 10, 40_000
GIT_TIMEOUT = 15


# ---------- paths and time ----------

def norm(path):
    """Comparable absolute path; accepts Git Bash style /c/... paths."""
    m = re.match(r"^/([a-zA-Z])/(.*)", path or "")
    if m and os.name == "nt":
        path = f"{m.group(1)}:/{m.group(2)}"
    return os.path.normcase(os.path.abspath(path))


def inside(path, root):
    p, r = norm(path), norm(root)
    return p == r or p.startswith(r.rstrip("\\/") + os.sep)


def parse_ts(value):
    try:
        t = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.astimezone()


def previous_working_day_start(now, working_days=(0, 1, 2, 3, 4)):
    """Local midnight of the last working day before `now` (Monday -> Friday)."""
    day = now.date() - dt.timedelta(days=1)
    while day.weekday() not in working_days:
        day -= dt.timedelta(days=1)
    return dt.datetime.combine(day, dt.time(), tzinfo=now.tzinfo)


REPORT_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.(md|json)$")


def default_log_dir():
    """The one place reports live: ~/standups, whatever folder the stand-up covers."""
    return os.path.join(os.path.expanduser("~"), "standups")


def reports(log_dir, ext):
    """Report files of one extension, oldest first (2026-11-23.md before 2026-11-23-2.md)."""
    try:
        names = os.listdir(log_dir)
    except OSError:
        return []
    found = [(m.group(1), int(m.group(2) or 1), n) for n in names
             for m in [REPORT_RE.match(n)] if m and m.group(3) == ext]
    return [os.path.join(log_dir, n) for _, _, n in sorted(found)]


def next_report_paths(log_dir, today):
    """Where today's report goes: YYYY-MM-DD.md, or -2, -3 ... when one exists."""
    n = 1
    while True:
        stem = today.isoformat() + ("" if n == 1 else f"-{n}")
        md = os.path.join(log_dir, stem + ".md")
        if not os.path.exists(md):
            return md, os.path.join(log_dir, stem + ".json")
        n += 1


def missed_working_days(latest, today, working_days=(0, 1, 2, 3, 4)):
    """Working days strictly between the last report's date and today (0 = no gap)."""
    day, missed = latest + dt.timedelta(days=1), 0
    while day < today:
        missed += day.weekday() in working_days
        day += dt.timedelta(days=1)
    return missed


def window_start(log_dir, now):
    """covered_until of the newest saved report, else the previous working day."""
    for path in reversed(reports(log_dir, "json")):
        try:
            with open(path, encoding="utf-8") as f:
                t = parse_ts(json.load(f).get("covered_until"))
        except (OSError, ValueError, AttributeError):
            continue
        if t:
            return t, path
    return previous_working_day_start(now), "previous working day"


# ---------- git ----------

def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, "--no-optional-locks", *args], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise RuntimeError(f"git {args[0]}: {type(e).__name__}")
    if r.returncode != 0:
        raise RuntimeError(f"git {args[0]}: {r.stderr.strip()[:120]}")
    return r.stdout


def find_repos(root, depth):
    repos, folders = [], []
    if os.path.exists(os.path.join(root, ".git")):
        return [root], []

    def walk(d, level):
        found = False
        try:
            entries = sorted(os.scandir(d), key=lambda e: e.name.lower())
        except OSError:
            return False
        for e in entries:
            if not e.is_dir(follow_symlinks=False) or e.name in SKIP_DIRS or e.name.startswith("."):
                continue
            if os.path.exists(os.path.join(e.path, ".git")):
                repos.append(e.path)
                found = True
            elif level < depth and walk(e.path, level + 1):
                found = True
            elif level == 1:
                folders.append(e.path)
        return found

    walk(root, 1)
    # a top-level folder that holds repos deeper down is not a plain folder
    folders = [f for f in folders if not any(inside(r, f) for r in repos)]
    return repos, folders


def matches_author(name, email, authors):
    hay = f"{name} {email}".lower()
    return any(a.lower() in hay for a in authors)


def repo_evidence(repo, since, until, authors):
    out = {"path": repo}
    try:
        out["branch"] = git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
        who = authors or [x for x in (git_config(repo, "user.name"), git_config(repo, "user.email")) if x]
        touched = []
        for line in git(repo, "for-each-ref", "--format=%(refname:short)%09%(committerdate:iso-strict)",
                        "refs/heads").splitlines():
            name, _, date = line.partition("\t")
            t = parse_ts(date)
            if t and since <= t <= until:
                touched.append(name)
        out["branches_touched"] = touched
        commits = []
        for line in git(repo, "log", "--all", f"--since={since.isoformat()}", f"--until={until.isoformat()}",
                        "--format=%H%x09%aI%x09%an%x09%ae%x09%s").splitlines():
            parts = line.split("\t", 4)
            if len(parts) == 5 and (not who or matches_author(parts[2], parts[3], who)):
                commits.append({"sha": parts[0][:10], "date": parts[1], "subject": parts[4][:120]})
        out["commits"] = commits
        status = [l for l in git(repo, "status", "--porcelain").splitlines() if l.strip()]
        out["dirty"] = {
            "modified": sum(1 for l in status if not l.startswith("??")),
            "untracked": sum(1 for l in status if l.startswith("??")),
            "paths": [l[3:] for l in status[:MAX_PATHS]],
        }
        out["remotes"] = sorted({l.split()[1] for l in git(repo, "remote", "-v").splitlines() if len(l.split()) > 1})
    except RuntimeError as e:
        out["error"] = str(e)
    return out


def git_config(repo, key):
    try:
        return git(repo, "config", key).strip()
    except RuntimeError:
        return ""


def folder_evidence(folder, since, max_files=5000):
    changed, names, seen = 0, [], 0
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if dirpath[len(folder):].count(os.sep) >= 3:
            dirnames[:] = []
        for fn in filenames:
            seen += 1
            if seen > max_files:
                break
            try:
                mtime = dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(dirpath, fn)), dt.timezone.utc)
            except OSError:
                continue
            if mtime >= since:
                changed += 1
                if len(names) < 5:
                    names.append(os.path.relpath(os.path.join(dirpath, fn), folder))
    return {"path": folder, "changed": changed, "names": names} if changed else None


# ---------- Claude sessions ----------

def prompt_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def read_session(path, since, until):
    """Parse one session file; unknown or malformed lines are skipped."""
    s = {"id": os.path.basename(path)[:-6], "cwd": None, "branch": None, "title": None,
         "stamps": [], "prompts": [], "files": []}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if not isinstance(o, dict):
                continue
            if o.get("type") == "ai-title" and o.get("aiTitle"):
                s["title"] = str(o["aiTitle"])[:120]
                continue
            s["cwd"] = s["cwd"] or o.get("cwd")
            t = parse_ts(o["timestamp"]) if o.get("timestamp") else None
            if not t or not (since <= t <= until):
                continue
            s["stamps"].append(t)
            s["branch"] = o.get("gitBranch") or s["branch"]
            content = (o.get("message") or {}).get("content") if isinstance(o.get("message"), dict) else None
            if o.get("type") == "user" and not o.get("isSidechain"):
                text = prompt_text(content).strip()
                if len(text) > 3 and not text.startswith(NOISE_PREFIXES):
                    s["prompts"].append(" ".join(text.split())[:PROMPT_CHARS])
            elif o.get("type") == "assistant" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in EDIT_TOOLS:
                        inp = b.get("input") or {}
                        p = inp.get("file_path") or inp.get("notebook_path")
                        if p and p not in s["files"]:
                            s["files"].append(p)
    return s


def active_minutes(stamps):
    stamps = sorted(stamps)
    total = sum((b - a for a, b in zip(stamps, stamps[1:]) if b - a <= ACTIVE_GAP), dt.timedelta())
    return round(total.total_seconds() / 60)


def owning_repo(path, repos):
    best = None
    for r in repos:
        if inside(path, r) and (best is None or len(r) > len(best)):
            best = r
    return best


def sessions_evidence(projects_dir, root, repos, since, until):
    out = []
    try:
        dirs = [os.path.join(projects_dir, d) for d in os.listdir(projects_dir)]
    except OSError:
        return out, [f"no session folder at {projects_dir}"]
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            path = os.path.join(d, fn)
            if not fn.endswith(".jsonl"):
                continue
            try:
                if dt.datetime.fromtimestamp(os.path.getmtime(path), dt.timezone.utc) < since:
                    continue
                s = read_session(path, since, until)
            except OSError:
                continue
            if not s["stamps"]:
                continue
            files_in = [p for p in s["files"] if inside(p, root)]
            if s["cwd"] and inside(s["cwd"], root):
                scope, anchor = "inside", s["cwd"]
            elif files_in:
                scope, anchor = "files-only", files_in[0]
            else:
                continue
            repo = owning_repo(anchor, repos)
            item = {
                "id": s["id"], "scope": scope,
                "repo": os.path.relpath(repo, root) if repo else os.path.relpath(norm(anchor), norm(root)),
                "first": min(s["stamps"]).isoformat(), "last": max(s["stamps"]).isoformat(),
                "active_minutes": active_minutes(s["stamps"]),
                "files_edited": [os.path.relpath(norm(p), norm(root)) for p in files_in][:MAX_PATHS * 2],
            }
            if scope == "inside":  # titles and prompts never cross the scope boundary
                item.update(branch=s["branch"], title=s["title"], prompts=s["prompts"][:MAX_PROMPTS])
            out.append(item)
    out.sort(key=lambda x: x["first"])
    return out, []


# ---------- PRs ----------

def prs_evidence(since, repos_out):
    if not shutil.which("gh"):
        return {"status": "skipped: gh not installed", "items": []}
    try:
        if subprocess.run(["gh", "auth", "status"], capture_output=True, timeout=GIT_TIMEOUT).returncode:
            return {"status": "skipped: gh not signed in", "items": []}
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "skipped: gh did not answer", "items": []}
    remotes = " ".join(r for x in repos_out for r in x.get("remotes", [])).lower()
    items = []
    for role, flag in (("author", "--author=@me"), ("reviewer", "--reviewed-by=@me")):
        try:
            r = subprocess.run(["gh", "search", "prs", flag, f"--updated=>={since.date().isoformat()}",
                                "--json", "number,title,repository,state,url", "--limit", "30"],
                               capture_output=True, text=True, encoding="utf-8", timeout=30)
            found = json.loads(r.stdout or "[]") if r.returncode == 0 else []
        except (OSError, subprocess.TimeoutExpired, ValueError):
            found = []
        for p in found:
            name = ((p.get("repository") or {}).get("nameWithOwner") or "").lower()
            if name and name in remotes:  # only PRs of repos inside the scope
                items.append({"number": p.get("number"), "repo": name, "title": (p.get("title") or "")[:120],
                              "state": p.get("state"), "role": role})
    return {"status": "ok", "items": items}


# ---------- assembly ----------

def ticket_ids(repos_out, sessions):
    text = []
    for r in repos_out:
        text += [r.get("branch") or ""] + r.get("branches_touched", []) + [c["subject"] for c in r.get("commits", [])]
    for s in sessions:
        text += [s.get("branch") or "", s.get("title") or ""] + s.get("prompts", [])
    ids = {m for t in text for m in TICKET_RE.findall(t) if m.split("-")[0] not in TICKET_STOP}
    return sorted(ids)


def cap_size(result):
    sessions = result["sessions"]
    for s in sessions:  # oldest first
        if len(json.dumps(result)) <= SIZE_CAP:
            break
        s.pop("prompts", None)
    for s in sessions:
        if len(json.dumps(result)) <= SIZE_CAP:
            break
        s["files_edited"] = s["files_edited"][:3]
    return result


def gather(root, since=None, until=None, authors=(), projects_dir=None, depth=3, with_prs=True, log_dir=None):
    root = os.path.abspath(root)
    log_dir = os.path.abspath(log_dir or default_log_dir())
    now = dt.datetime.now().astimezone()
    until = until or now
    notes = []
    if since is None:
        since, source = window_start(log_dir, now)
        notes.append(f"window start from {source}")
    next_md, next_json = next_report_paths(log_dir, now.date())
    latest = reports(log_dir, "md")
    latest_date = dt.date.fromisoformat(REPORT_RE.match(os.path.basename(latest[-1])).group(1)) if latest else None
    log = {"dir": log_dir, "latest_report": latest[-1] if latest else None,
           "latest_date": latest_date.isoformat() if latest_date else None,
           "missed_working_days": missed_working_days(latest_date, now.date()) if latest_date else None,
           "save_report_to": next_md, "save_json_to": next_json}
    repos, folders = find_repos(root, depth)
    repos_out = [repo_evidence(r, since, until, list(authors)) for r in repos]
    folders_out = [x for x in (folder_evidence(f, since) for f in folders) if x]
    sessions, more = sessions_evidence(projects_dir or default_projects_dir(), root, repos, since, until)
    notes += more
    notes.append("sessions are from this machine only")
    for r in repos_out:
        r["path"] = os.path.relpath(r["path"], root) if r["path"] != root else "."
    result = {
        "schema_version": SCHEMA_VERSION, "root": root, "log": log,
        "window": {"since": since.isoformat(), "until": until.isoformat()},
        "repos": repos_out, "folders": [dict(f, path=os.path.relpath(f["path"], root)) for f in folders_out],
        "sessions": sessions, "ticket_ids": ticket_ids(repos_out, sessions),
        "prs": prs_evidence(since, repos_out) if with_prs else {"status": "skipped: disabled", "items": []},
        "notes": notes,
    }
    for r in repos_out:
        r.pop("remotes", None)
    return cap_size(result)


def default_projects_dir():
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "projects")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="folder the stand-up covers (default: current folder)")
    ap.add_argument("--since", help="ISO time; default: last report's covered_until, else previous working day")
    ap.add_argument("--until", help="ISO time; default: now")
    ap.add_argument("--author", action="append", default=[], help="git author name or email (repeatable)")
    ap.add_argument("--projects-dir", help="Claude session folder (default: ~/.claude/projects)")
    ap.add_argument("--depth", type=int, default=3)
    ap.add_argument("--no-prs", action="store_true")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    a = ap.parse_args(argv)
    since = parse_ts(a.since) if a.since else None
    until = parse_ts(a.until) if a.until else None
    result = gather(a.root, since, until, a.author, a.projects_dir, a.depth, not a.no_prs)
    text = json.dumps(result, indent=1, ensure_ascii=False)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(a.out)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
