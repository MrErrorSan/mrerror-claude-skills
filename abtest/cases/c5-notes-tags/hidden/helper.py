"""Helpers for hidden acceptance tests. The repo under test is the current directory."""
import os
import subprocess
import sys

REPO = os.getcwd()


def run(*args, env=None, input=None):
    """Run `python <args>` in the repo; returns CompletedProcess (text)."""
    full_env = dict(os.environ, PYTHONIOENCODING="utf-8")
    if env:
        full_env.update(env)
    return subprocess.run([sys.executable, *args], cwd=REPO, capture_output=True, text=True,
                          env=full_env, input=input, timeout=60, encoding="utf-8")
