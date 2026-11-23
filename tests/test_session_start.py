"""Tests for plugins/anvil/hooks/session-start (needs bash and git on PATH).

Each test names what breaks if it fails. Run: python -m unittest discover -s tests -v
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "plugins", "anvil", "hooks", "session-start")
BASH = shutil.which("bash")


def run_hook(cwd):
    r = subprocess.run([BASH, HOOK], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "CLAUDE_PROJECT_DIR": cwd}, timeout=30)
    return r, json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


def git(cwd, *args):
    subprocess.run(["git", "-C", cwd, "-c", "user.name=T", "-c", "user.email=t@example.com", *args],
                   check=True, capture_output=True)


@unittest.skipUnless(BASH and shutil.which("git"), "needs bash and git")
class SessionStartTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        self.remote = os.path.join(base, "remote.git")
        self.mine = os.path.join(base, "mine")
        self.other = os.path.join(base, "other")
        git(base, "init", "-q", "--bare", "-b", "main", self.remote)
        git(base, "clone", "-q", self.remote, self.mine)
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "first")
        git(self.mine, "push", "-q", "-u", "origin", "main")
        git(base, "clone", "-q", self.remote, self.other)
        git(self.other, "commit", "-q", "--allow-empty", "-m", "from another machine")
        git(self.other, "push", "-q", "origin", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def opt_in(self):
        os.makedirs(os.path.join(self.mine, ".claude", "rules"))
        with open(os.path.join(self.mine, ".claude", "rules", "remote-sync.md"), "w") as f:
            f.write("# Remote sync\n")

    def test_non_repo_folder_gets_rules_only(self):
        """B1/B3/B4: rules must arrive everywhere, as valid JSON, with no sync noise outside repos."""
        plain = os.path.join(self.tmp.name, "plain")
        os.makedirs(plain)
        r, ctx = run_hook(plain)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stderr, "")
        self.assertIn("local files, never Artifacts", ctx)
        self.assertIn("no Claude attribution", ctx)
        self.assertNotIn("anvil-remote-sync", ctx)

    def test_opted_in_repo_reports_behind_after_fetch(self):
        """B2: a repo one commit behind its remote must be told to pull before editing."""
        self.opt_in()
        _, ctx = run_hook(self.mine)
        self.assertIn("tracking origin/main: ahead 0, behind 1", ctx)
        self.assertIn("BEHIND the remote", ctx)
        self.assertIn("Uncommitted changes: 1", ctx)  # the untracked rule file itself

    def test_repo_without_rule_file_has_no_sync_section(self):
        """B3: repos that didn't opt in (company, client) must not get the sync rule."""
        _, ctx = run_hook(self.mine)
        self.assertNotIn("anvil-remote-sync", ctx)

    def test_diverged_repo_says_stop(self):
        """B2: a diverged repo must stop work before any code is written."""
        self.opt_in()
        git(self.mine, "commit", "-q", "--allow-empty", "-m", "local only")
        _, ctx = run_hook(self.mine)
        self.assertIn("DIVERGED", ctx)


if __name__ == "__main__":
    unittest.main()
