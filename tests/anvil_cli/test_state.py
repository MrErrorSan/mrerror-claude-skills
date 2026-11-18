import contextlib
import io
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from anvil_cli import cli, gate, state

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

    def topic_start(self, cwd, *argv, code=0):
        out = io.StringIO()
        with (contextlib.chdir(cwd), contextlib.redirect_stdout(out),
              contextlib.redirect_stderr(io.StringIO()) as err):
            self.assertEqual(cli.main(["topic", "start", *argv, "--json"]), code)
        self.err = err.getvalue()
        return json.loads(out.getvalue()) if code == 0 else None

    def topic(self, cwd, *argv):
        with contextlib.chdir(cwd), contextlib.redirect_stdout(io.StringIO()):
            return cli.main(["topic", *argv])

    def test_topic_start_stores_repo_relative_dir(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            sub = repo / "src"
            sub.mkdir()
            before = time.time()
            topic = self.topic_start(sub, "demo")
            self.assertGreaterEqual(topic.pop("started"), before)
            self.assertEqual(topic, {"slug": "demo", "dir": "docs/demo", "size": "full",
                                     "stage": "spec"})
            # --dir from a subdirectory is relative to cwd, then stored repo-relative.
            topic = self.topic_start(sub, "demo", "--dir", "notes/demo")
            self.assertEqual(topic["dir"], "src/notes/demo")
            self.assertEqual(state.active_topic(repo)["dir"], "src/notes/demo")
            self.assertEqual(self.topic(repo, "end"), 0)
            self.assertEqual(self.topic_start(repo, "fix", "--size", "direct")["stage"], "plan")
            self.assertEqual(self.topic(repo, "end"), 0)
            self.assertEqual(self.topic_start(repo, "typo", "--size", "trivial")["stage"], "build")

    def test_topic_start_refuses_other_slug_and_keeps_started(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            started = self.topic_start(repo, "demo", "--size", "direct")["started"]
            # The same slug is a step-up: the original start time stays.
            topic = self.topic_start(repo, "demo", "--size", "full")
            self.assertEqual((topic["size"], topic["started"]), ("full", started))
            # Another slug while demo is active is refused.
            self.assertIsNone(self.topic_start(repo, "other", code=1))
            self.assertIn("Topic demo is active (stage spec). Run `anvil topic end` first, "
                          "or continue it.", self.err)
            self.assertEqual(state.active_topic(repo)["slug"], "demo")
            # An old record without "started" counts as 0, and a step-up keeps that.
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "direct", "stage": "plan"})
            self.assertEqual(self.topic_start(repo, "demo")["started"], 0)

    def test_topic_start_parks_a_topic_at_finish(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            self.topic_start(repo, "demo", "--size", "direct")
            # At build it's refused, as before.
            self.assertEqual(self.topic(repo, "stage", "verify"), 0)
            self.assertIsNone(self.topic_start(repo, "other", code=1))
            # At finish, verify has landed the work: new work parks it.
            self.assertEqual(self.topic(repo, "stage", "finish"), 0)
            topic = self.topic_start(repo, "other", "--size", "direct")
            self.assertEqual(topic["slug"], "other")
            self.assertIn("Parked topic demo (stage finish", self.err)

    def test_topic_start_and_end_set_afk_lifetime(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            afk = lambda: gate.afk_status(repo)["on"]
            # Last week's AFK, with prompts logged since: a fresh topic start turns it off.
            state.save(repo, "afk.json", {"on": True, "ts": 1.0, "quote": "I'm AFK"})
            state.append_jsonl(repo, "prompts.jsonl", {"ts": 2.0, "prompt": "fix the login"})
            self.topic_start(repo, "login")
            self.assertFalse(afk())
            # topic end turns AFK off.
            state.append_jsonl(repo, "prompts.jsonl",
                               {"ts": time.time(), "prompt": "AFK, finish the login"})
            gate.afk_on(repo, "AFK, finish the login")
            self.assertTrue(afk())
            self.assertEqual(self.topic(repo, "end"), 0)
            self.assertFalse(afk())
            # "AFK, build X": afk on, then topic start, in the same turn: AFK stays on.
            state.append_jsonl(repo, "prompts.jsonl",
                               {"ts": time.time(), "prompt": "AFK, build the export"})
            gate.afk_on(repo, "AFK, build the export")
            self.topic_start(repo, "export")
            self.assertTrue(afk())
            self.assertEqual(self.topic(repo, "end"), 0)
            # The other order: topic start, then afk on.
            state.append_jsonl(repo, "prompts.jsonl",
                               {"ts": time.time(), "prompt": "AFK, build the import"})
            self.topic_start(repo, "import")
            gate.afk_on(repo, "AFK, build the import")
            self.assertTrue(afk())

    def test_append_jsonl_trim_replaces_file(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            for i in range(3):
                state.append_jsonl(repo, "log.jsonl", {"i": i}, keep=5)
            with mock.patch.object(state.os, "replace", wraps=os.replace) as replace:
                state.append_jsonl(repo, "log.jsonl", {"i": 3}, keep=3)
            target = state.state_dir(repo) / "log.jsonl"
            replace.assert_called_once()
            src, dst = replace.call_args[0]
            self.assertEqual(Path(dst), target)
            self.assertEqual(Path(src).parent, target.parent)
            self.assertFalse(Path(src).exists())
            self.assertEqual(state.read_jsonl(repo, "log.jsonl"), [{"i": 1}, {"i": 2}, {"i": 3}])

    def test_main_drops_msys_env(self):
        env = {"MSYS_NO_PATHCONV": "1", "MSYS2_ARG_CONV_EXCL": "*"}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["check"]), 2)  # a usage error still drops them
            self.assertNotIn("MSYS_NO_PATHCONV", os.environ)
            self.assertNotIn("MSYS2_ARG_CONV_EXCL", os.environ)


if __name__ == "__main__":
    unittest.main()
