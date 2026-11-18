"""Shared test helpers: throwaway git repos and file writing."""
import subprocess
from pathlib import Path


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def make_repo(tmp: Path) -> Path:
    """git init in tmp/repo with one commit; returns the repo path."""
    repo = Path(tmp) / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "commit.gpgsign", "false")
    write(repo / "README.md", "# test repo\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "init")
    return repo


def write(path: Path, text: str, crlf: bool = False) -> Path:
    """Write text with LF line endings, or CRLF when crlf=True."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.replace("\r\n", "\n")
    if crlf:
        data = data.replace("\n", "\r\n")
    path.write_bytes(data.encode("utf-8"))
    return path
