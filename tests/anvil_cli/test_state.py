import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from anvil_cli import cli, state

from .helpers import git, make_repo


class StateTests(unittest.TestCase):
    def test_state_dir_under_git_common_dir(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            common = Path(git(repo, "rev-parse", "--path-format=absolute",
                              "--git-common-dir"))
            self.assertEqual(state.state_dir(repo).resolve(), (common / "anvil").resolve())
            sub = repo / "src"
            sub.mkdir()
            self.assertEqual(state.state_dir(sub).resolve(), (common / "anvil").resolve())

            wt = Path(tmp) / "lane"
            git(repo, "worktree", "add", "-q", str(wt), "-b", "lane")
            self.assertEqual(state.state_dir(wt).resolve(), (common / "anvil").resolve())

            state.save(repo, "active.json", {"slug": "demo"})
            self.assertEqual(state.active_topic(wt), {"slug": "demo"})
            self.assertEqual(git(repo, "status", "--porcelain"), "")

    def test_state_dir_outside_git(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            home = Path(tmp) / "home"
            work = Path(tmp) / "work" / "proj"
            home.mkdir()
            work.mkdir(parents=True)
            env = {"HOME": str(home), "USERPROFILE": str(home),
                   "GIT_CEILING_DIRECTORIES": str(Path(tmp))}
            with mock.patch.dict(os.environ, env):
                d = state.state_dir(work)
                self.assertEqual(d.parent, home / ".claude" / "anvil")
                self.assertNotIn(os.sep, d.name)
                self.assertTrue(d.name.endswith("work-proj"))
                self.assertIsNone(state.active_topic(work))
                self.assertEqual(state.load(work, "afk.json", {"on": False}), {"on": False})
                for i in range(3):
                    state.append_jsonl(work, "prompts.jsonl", {"i": i}, keep=2)
                self.assertEqual(state.read_jsonl(work, "prompts.jsonl"), [{"i": 1}, {"i": 2}])

    def test_topic_dir_resolves_against_repo_root(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            sub = repo / "src" / "deep"
            sub.mkdir(parents=True)
            self.assertIsNone(state.topic_dir(sub))
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "spec"})
            self.assertEqual(state.topic_dir(sub).resolve(), (repo / "docs" / "demo").resolve())
            self.assertEqual(state.topic_dir(repo).resolve(), (repo / "docs" / "demo").resolve())

    def topic_start(self, cwd, *argv):
        out = io.StringIO()
        with contextlib.chdir(cwd), contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["topic", "start", *argv, "--json"]), 0)
        return json.loads(out.getvalue())

    def test_topic_start_stores_repo_relative_dir(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            sub = repo / "src"
            sub.mkdir()
            topic = self.topic_start(sub, "demo")
            self.assertEqual(topic, {"slug": "demo", "dir": "docs/demo", "size": "full",
                                     "stage": "spec"})
            # --dir from a subdirectory is relative to cwd, then stored repo-relative.
            topic = self.topic_start(sub, "demo", "--dir", "notes/demo")
            self.assertEqual(topic["dir"], "src/notes/demo")
            self.assertEqual(state.active_topic(repo)["dir"], "src/notes/demo")
            self.assertEqual(self.topic_start(repo, "fix", "--size", "direct")["stage"], "plan")
            self.assertEqual(self.topic_start(repo, "typo", "--size", "trivial")["stage"], "build")

    def test_main_drops_msys_env(self):
        env = {"MSYS_NO_PATHCONV": "1", "MSYS2_ARG_CONV_EXCL": "*"}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["check"]), 2)  # a usage error still drops them
            self.assertNotIn("MSYS_NO_PATHCONV", os.environ)
            self.assertNotIn("MSYS2_ARG_CONV_EXCL", os.environ)


if __name__ == "__main__":
    unittest.main()
