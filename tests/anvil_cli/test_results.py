import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from anvil_cli import cli, results, state

from .helpers import git, make_repo, write

# A fake test command: reads mode.txt (gitignored, so it never changes the key)
# and prints a unittest-style summary. mode "fail" exits 1, "zero" runs 0 tests.
FAKE = [sys.executable, "-I", "-c",
        "import sys; m = open('mode.txt').read().strip()\n"
        "print('Ran %d tests in 0.001s' % (0 if m == 'zero' else 3))\n"
        "sys.exit(1 if m == 'fail' else 0)"]
PASS = [sys.executable, "-I", "-c", "print('Ran 3 tests in 0.001s')"]


def quiet_run(*args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return results.run(*args, **kwargs)


class ResultsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)

    def tearDown(self):
        self._tmp.cleanup()

    def test_native_args_leaves_non_paths_alone(self):
        cmd = ["python", "-m", "unittest", "-v", "tests/test_x.py", "--name=demo"]
        self.assertEqual(results.native_args(cmd), cmd)

    @unittest.skipUnless(os.name == "nt" and shutil.which("cygpath"), "Git Bash on Windows only")
    def test_native_args_converts_posix_paths_on_windows(self):
        posix = subprocess.run(["cygpath", "-u", str(self.tmp)], capture_output=True,
                               text=True, check=True).stdout.strip()
        got = results.native_args(["python", "x.py", f"{posix}/out.csv", f"--out={posix}/o",
                                   "/no_such_root_zz/q"])
        self.assertEqual(Path(got[2]), self.tmp / "out.csv")
        self.assertEqual(Path(got[3].removeprefix("--out=")), self.tmp / "o")
        self.assertEqual(got[4], "/no_such_root_zz/q")  # parent missing: left as typed

    def test_key_changes_on_edit_and_untracked(self):
        k0 = results.tree_key(self.repo)
        self.assertEqual(results.tree_key(self.repo), k0)
        write(self.repo / "README.md", "# edited\n")
        self.assertNotEqual(results.tree_key(self.repo), k0)
        write(self.repo / "README.md", "# test repo\n")
        self.assertEqual(results.tree_key(self.repo), k0)
        write(self.repo / "new.py", "x = 1\n")
        k1 = results.tree_key(self.repo)
        self.assertNotEqual(k1, k0)
        write(self.repo / ".gitignore", "*.log\n")
        k2 = results.tree_key(self.repo)
        write(self.repo / "run.log", "ignored\n")
        self.assertEqual(results.tree_key(self.repo), k2)
        self.assertNotEqual(results.result_key(self.repo, PASS, "targeted"),
                            results.result_key(self.repo, PASS, "full"))
        # The same command from two subdirectories is a different run.
        (self.repo / "a").mkdir()
        (self.repo / "b").mkdir()
        self.assertNotEqual(results.result_key(self.repo / "a", PASS, "targeted"),
                            results.result_key(self.repo / "b", PASS, "targeted"))

    def test_key_ignores_topic_progress_file(self):
        state.save(self.repo, "active.json",
                   {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "build"})
        write(self.repo / "docs/demo/progress.md", "# Progress: demo\n- [ ] T1 a\n")
        k0 = results.tree_key(self.repo)
        write(self.repo / "docs/demo/progress.md", "# Progress: demo\n- [x] T1 a C1\n")
        self.assertEqual(results.tree_key(self.repo), k0)
        write(self.repo / "docs/demo/plan.md", "- **Approved:** no\n")
        self.assertNotEqual(results.tree_key(self.repo), k0)

    def test_key_sees_assume_unchanged_edit(self):
        git(self.repo, "update-index", "--assume-unchanged", "README.md")
        k0 = results.tree_key(self.repo)
        write(self.repo / "README.md", "# edited behind the flag\n")
        self.assertNotEqual(results.tree_key(self.repo), k0)
        self.assertEqual(git(self.repo, "ls-files", "-v", "README.md"), "h README.md")

    def test_key_changes_on_lockfile(self):
        # Ignored, so only the lockfile hash (not the tree) can change the key.
        write(self.repo / ".gitignore", "package-lock.json\nrequirements-dev.txt\n")
        k0 = results.tree_key(self.repo)
        write(self.repo / "package-lock.json", '{"lockfileVersion": 3}\n')
        k1 = results.tree_key(self.repo)
        self.assertNotEqual(k1, k0)
        write(self.repo / "package-lock.json", '{"lockfileVersion": 2}\n')
        self.assertNotEqual(results.tree_key(self.repo), k1)
        write(self.repo / "requirements-dev.txt", "pytest==8\n")
        k2 = results.tree_key(self.repo)
        self.assertNotIn(k2, (k0, k1))
        # The environment fingerprint: allowlisted env vars are part of the key.
        with mock.patch.dict(os.environ, {"ANVIL_KEY_ENV": "ANVIL_T_VAR", "ANVIL_T_VAR": "a"}):
            ka = results.tree_key(self.repo)
            os.environ["ANVIL_T_VAR"] = "b"
            self.assertNotEqual(results.tree_key(self.repo), ka)

    def test_fresh_only_reuses_passing_with_tests(self):
        write(self.repo / ".gitignore", "mode.txt\n")
        mode = self.repo / "mode.txt"

        write(mode, "fail")
        self.assertEqual(quiet_run(self.repo, FAKE), 1)
        self.assertIsNone(results.fresh(self.repo, FAKE))

        write(mode, "zero")
        self.assertEqual(quiet_run(self.repo, FAKE), 0)
        self.assertIsNone(results.fresh(self.repo, FAKE))

        write(mode, "pass")
        self.assertEqual(quiet_run(self.repo, FAKE), 0)
        rec = results.fresh(self.repo, FAKE)
        self.assertIsNotNone(rec)
        self.assertEqual((rec["exit"], rec["tests_ran"], rec["scope"]), (0, 3, "targeted"))
        self.assertIn("Ran 3 tests", rec["summary"])
        self.assertIsNone(results.fresh(self.repo, FAKE, scope="full"))
        src = write(self.repo / "src.py", "y = 2\n")
        self.assertIsNone(results.fresh(self.repo, FAKE))
        src.unlink()
        self.assertIsNotNone(results.fresh(self.repo, FAKE))

        # A later failure on the same tree wins over the earlier green.
        write(mode, "fail")
        quiet_run(self.repo, FAKE)
        self.assertIsNone(results.fresh(self.repo, FAKE))

        count = results.count_tests
        self.assertEqual(count("collected 5\n==== 3 passed, 2 skipped in 0.2s ===="), 3)
        self.assertEqual(count(" Test Files  1 passed (1)\n      Tests  5 passed (5)"), 5)
        self.assertEqual(count("Test Suites: 2 passed, 2 total\nTests:       6 passed, 6 total"), 6)
        self.assertEqual(count("ok  \texample.com/a\t0.01s\n?   \texample.com/b\t[no test files]\n"
                               "ok  \texample.com/c\t(cached)\n"), 2)
        self.assertEqual(count("Ran 4 tests in 0.1s\n\nOK (skipped=1)"), 3)
        self.assertEqual(count("all good\n"), 0)
        self.assertEqual(count("ok   all good\n"), 0)
        # Failures in the output count 0, whatever the exit code said.
        for out in ["collected 4\n==== 3 passed, 1 failed in 0.2s ====",
                    "      Tests  1 failed | 4 passed (5)",
                    "Tests:       1 failed, 5 passed, 6 total",
                    "Ran 3 tests in 0.1s\n\nFAILED (failures=1)",
                    "ok  \texample.com/a\t0.01s\nFAIL\texample.com/b\t0.02s\nFAIL\n",
                    "Ran 2 tests in 0.1s\n\nOK (skipped=2)"]:          # all skipped
            self.assertEqual(count(out), 0, out)

    def test_check_scope_reused_without_tests(self):
        write(self.repo / ".gitignore", "mode.txt\n")
        mode = self.repo / "mode.txt"
        lint = [sys.executable, "-I", "-c",
                "import sys; m = open('mode.txt').read().strip()\n"
                "print('Found 0 errors.')\nsys.exit(1 if m == 'fail' else 0)"]
        write(mode, "pass")
        self.assertEqual(quiet_run(self.repo, lint, scope="check"), 0)
        rec = results.fresh(self.repo, lint, scope="check")
        self.assertIsNotNone(rec)
        self.assertEqual((rec["scope"], rec["tests_ran"]), ("check", 0))
        # The tests_ran rule still holds for the test scopes.
        self.assertEqual(quiet_run(self.repo, lint, scope="smoke"), 0)
        self.assertIsNone(results.fresh(self.repo, lint, scope="smoke"))
        # A failing or external check is not reused.
        write(mode, "fail")
        self.assertEqual(quiet_run(self.repo, lint, scope="check"), 1)
        self.assertIsNone(results.fresh(self.repo, lint, scope="check"))
        write(mode, "pass")
        self.assertEqual(quiet_run(self.repo, lint, scope="check", external=True), 0)
        self.assertIsNone(results.fresh(self.repo, lint, scope="check"))
        # The CLI accepts the scope.
        self.assertEqual(quiet_run(self.repo, lint, scope="check"), 0)
        with contextlib.chdir(self.repo), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.main(["fresh", "--scope", "check", "--", *lint]), 0)
        self.assertIn("scope check", out.getvalue())

    def test_external_never_reused(self):
        self.assertEqual(quiet_run(self.repo, PASS, external=True), 0)
        rec = state.read_jsonl(self.repo, "results.jsonl")[-1]
        self.assertIs(rec.get("external"), True)
        self.assertEqual(set(rec), {"key", "tree", "prefix", "cmd", "scope", "exit", "tests_ran",
                                    "ts", "summary", "external"})
        self.assertEqual((rec["tree"], rec["prefix"]), (results.tree_key(self.repo), ""))
        self.assertEqual(rec["tests_ran"], 3)
        self.assertIsNone(results.fresh(self.repo, PASS))

    def test_run_that_writes_a_file_not_recorded(self):
        cmd = [sys.executable, "-I", "-c",
               "open('made.txt', 'w').write('x'); print('Ran 3 tests in 0.001s')"]
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(quiet_run(self.repo, cmd), 0)
        self.assertIn("code changed during the run", err.getvalue())
        self.assertEqual(state.read_jsonl(self.repo, "results.jsonl"), [])
        self.assertIsNone(results.fresh(self.repo, cmd))

    def test_state_shared_across_worktrees(self):
        lane = self.tmp / "lane"
        git(self.repo, "worktree", "add", "-q", str(lane), "-b", "lane")
        self.assertEqual(results.tree_key(lane), results.tree_key(self.repo))
        self.assertEqual(quiet_run(lane, PASS, scope="full"), 0)
        rec = results.fresh(self.repo, PASS, scope="full")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["tests_ran"], 3)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        self.assertEqual(git(lane, "status", "--porcelain"), "")

    def test_index_untouched(self):
        write(self.repo / "README.md", "# staged\n")
        git(self.repo, "add", "README.md")
        write(self.repo / "README.md", "# staged then edited\n")
        write(self.repo / "untracked.txt", "u\n")
        index = Path(git(self.repo, "rev-parse", "--path-format=absolute", "--git-path", "index"))
        before = (git(self.repo, "diff", "--cached"), git(self.repo, "status", "--porcelain"),
                  index.read_bytes())
        results.tree_key(self.repo)
        after = (git(self.repo, "diff", "--cached"), git(self.repo, "status", "--porcelain"),
                 index.read_bytes())
        self.assertEqual(after, before)

        # A repo with no index yet: starts from an empty temp index, creates none.
        bare = self.tmp / "noindex"
        bare.mkdir()
        git(bare, "init", "-q")
        write(bare / "a.txt", "a\n")
        self.assertTrue(results.tree_key(bare))
        self.assertFalse((bare / ".git" / "index").exists())


if __name__ == "__main__":
    unittest.main()
