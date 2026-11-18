import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from anvil_cli import cli, results, state, stale

from .helpers import make_repo, write

SPEC = """# Spec: demo

- **Approved:** 2026-11-18 by Saad ("yes")
- **Size:** full

## Spec lines

- **S1** First behavior.
- ~~**S2** Old behavior.~~ RETIRED → S3 (2026-11-20, CR: reason)
- **S3** New behavior.
- ~~**S4** Dropped behavior.~~ RETIRED (2026-11-20, CR: not needed)
"""

PLAN = """# Plan: demo

- **Approved:** no
- **Size:** full

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1 | `src/a.py` | - | - | 0 | yes |
| T2 | S1, S2 | `src/b.py` | - | T1 | 1 | yes |
| T3 | S3, §7.2 | `src/c.py` | - | T1 | 1 | yes |
| T4 | S4 | `src/d.py` | - | - | 1 | yes |

## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `test_a.test_one` | keep | S1 | A | T1 |
| `test_b.test_old` | keep | S2, Review focus 1 | B | T2 |
| `test_c.test_new` | keep | §7.2 | C | T3 |
"""


class StaleTests(unittest.TestCase):
    def test_retired_sline_flags_tasks_and_tests(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            write(repo / "docs/demo/spec.md", SPEC, crlf=True)
            write(repo / "docs/demo/plan.md", PLAN, crlf=True)
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "build"})
            got = [e for e in stale.stale(repo) if e["kind"] != "result"]
            self.assertEqual(got, [
                {"kind": "task", "id": "T2", "retired": "S2", "replaced_by": 3},
                {"kind": "task", "id": "T4", "retired": "S4", "replaced_by": None},
                {"kind": "test", "id": "test_b.test_old", "retired": "S2", "replaced_by": 3},
            ])

            # Direct size: S-lines live in plan.md, there is no spec.md.
            (repo / "docs/demo/spec.md").unlink()
            write(repo / "docs/demo/plan.md", SPEC.replace("# Spec", "# Plan")
                  + PLAN.split("\n", 1)[1])
            got = [e for e in stale.stale(repo) if e["kind"] != "result"]
            self.assertEqual([e["id"] for e in got], ["T2", "T4", "test_b.test_old"])

    def test_result_stale_when_no_record_matches_tree(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "build"})
            self.assertEqual(stale.stale(repo), [])  # no records: nothing to check
            # Old-format records (no "tree") are ignored.
            state.append_jsonl(repo, "results.jsonl", {"key": "k0", "exit": 0})
            self.assertEqual(stale.stale(repo), [])

            state.append_jsonl(repo, "results.jsonl",
                               {"key": "k1", "tree": "old-tree", "prefix": "", "exit": 0})
            key = results.tree_key(repo)
            self.assertEqual(stale.stale(repo), [{"kind": "result", "key": key}])

            state.append_jsonl(repo, "results.jsonl",
                               {"key": "k2", "tree": key, "prefix": "", "exit": 0})
            self.assertEqual(stale.stale(repo), [])

            # No usable tree key (outside git, git missing): the check is skipped.
            (state.state_dir(repo) / "results.jsonl").unlink()
            state.append_jsonl(repo, "results.jsonl",
                               {"key": "k1", "tree": "old-tree", "prefix": "", "exit": 0})
            for err in (subprocess.CalledProcessError(128, ["git"]), FileNotFoundError("git")):
                with mock.patch.object(results, "tree_key", side_effect=err):
                    self.assertEqual(stale.stale(repo), [])

    def test_cmd_stale_fails_only_on_tasks_and_tests(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "build"})
            state.append_jsonl(repo, "results.jsonl",
                               {"key": "k1", "tree": "old-tree", "prefix": "", "exit": 0})

            def run():
                with contextlib.chdir(repo), contextlib.redirect_stdout(io.StringIO()) as out:
                    code = cli.main(["stale"])
                return code, out.getvalue()

            code, out = run()  # a result entry alone is informational
            self.assertEqual(code, 0)
            self.assertIn("result: no recorded run for the current tree", out)
            write(repo / "docs/demo/spec.md", SPEC)
            write(repo / "docs/demo/plan.md", PLAN)
            code, out = run()
            self.assertEqual(code, 1)
            self.assertIn("task T2: names S2", out)


if __name__ == "__main__":
    unittest.main()
