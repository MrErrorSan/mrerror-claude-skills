"""Anvil's state directory: <git common dir>/anvil, or ~/.claude/anvil/<cwd> outside git.

Never committed. Shared by every worktree of a repo.
"""
import functools
import json
import os
import re
import subprocess
from pathlib import Path


@functools.lru_cache(maxsize=None)
def _git_path(cwd: str, flag: str) -> Path:
    """The absolute path `git rev-parse <flag>` prints for cwd.

    Raises LookupError outside git or without git; lru_cache doesn't cache a
    raise, so only the git case is cached (the fallback depends on HOME).
    """
    try:
        r = subprocess.run(["git", "rev-parse", "--path-format=absolute", flag], cwd=cwd,
                           capture_output=True, text=True, encoding="utf-8")
    except OSError as e:
        raise LookupError("git not found") from e
    if r.returncode != 0 or not r.stdout.strip():
        raise LookupError("not a git repository")
    return Path(r.stdout.strip())


def state_dir(cwd: Path) -> Path:
    cwd = Path(cwd).resolve()
    try:
        return _git_path(str(cwd), "--git-common-dir") / "anvil"
    except LookupError:
        return Path.home() / ".claude" / "anvil" / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))


def repo_root(cwd: Path) -> Path:
    """The worktree's top level, or cwd itself outside git."""
    cwd = Path(cwd).resolve()
    try:
        return _git_path(str(cwd), "--show-toplevel")
    except LookupError:
        return cwd


def load(cwd: Path, name: str, default):
    path = state_dir(cwd) / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save(cwd: Path, name: str, value) -> None:
    path = state_dir(cwd) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def append_jsonl(cwd: Path, name: str, record: dict, keep: int | None = None) -> None:
    path = state_dir(cwd) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    if keep is not None:
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > keep:  # a temp file and a rename, so a crash can't truncate the log
            tmp = path.with_name(path.name + ".tmp")
            tmp.write_text("\n".join(lines[-keep:]) + "\n", encoding="utf-8")
            os.replace(tmp, path)


def read_jsonl(cwd: Path, name: str) -> list[dict]:
    path = state_dir(cwd) / name
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # blank or half-written line
    return out


def active_topic(cwd: Path) -> dict | None:
    return load(cwd, "active.json", None)


def topic_dir(cwd: Path) -> Path | None:
    """The active topic's folder: its repo-relative dir resolved against the repo root."""
    topic = active_topic(cwd)
    return repo_root(cwd) / topic["dir"] if topic else None
