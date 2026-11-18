import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from anvil_cli import cli, plancheck, state
from anvil_cli.docs import Task

from .helpers import git, make_repo, write


def task(id, wave, writes=(), shared=(), depends=(), spec=("S1",), review="yes"):
    return Task(id, list(spec), list(writes), list(shared), list(depends), wave, review)


# A parallel-safe plan: foundations alone in wave 0, three disjoint lanes in wave 1.
CLEAN = [
    task("T1", 0, ["src/types.ts"]),
    task("T2", 1, ["src/a/**"], ["port:5173"], ["T1"]),
    task("T3", 1, ["src/b.py", "tests/test_b.py"], ["db"], ["T1"]),
    task("T4", 1, ["config/x.json"], depends=["T1"], spec=(), review="skip (fully specified)"),
]


def rules(findings):
    return sorted(f.rule for f in findings)


class PlanCheckTests(unittest.TestCase):
    def test_overlapping_write_sets_fail(self):
        self.assertEqual(plancheck.plan_check(CLEAN), [])
        for a, b in [("src/a/**", "src/a/x.py"),          # glob vs file
                     ("src\\a\\x.py", "src/a/x.py"),        # backslashes
                     ("src/a", "src/a/deep/y.py"),          # directory prefix
                     ("src/*.ts", "src/types.ts"),
                     ("src/{x,y}.ts", "src/y.ts"),          # brace form from formats.md
                     ("src/**/*.ts", "src/billing/**"),     # two globs that share files
                     ("src/*/x.py", "src/a/**"),
                     ("tests/test_*.py", "tests/test_a*.py"),
                     ("src/billing", "src/**/*.ts"),        # literal directory vs glob
                     ("src/*.ts", "src/billing/**"),        # fnmatch's * crosses /
                     ("src/A/x.py", "src/a/**"),            # case-insensitive (NTFS)
                     ("/src/a/x.py", "src/a/x.py"),         # leading slash
                     ("app/[id]/*.tsx", "app/[id]/page.tsx")]:  # [ is literal

            plan = [task("T1", 0, ["lib.py"]),
                    task("T2", 1, [a], depends=["T1"]),
                    task("T3", 1, [b], depends=["T1"])]
            found = plancheck.plan_check(plan)
            self.assertEqual(rules(found), ["write-overlap"], (a, b))
            self.assertEqual(found[0].tasks, ["T2", "T3"])
        # Same paths in different waves are fine.
        plan = [task("T1", 0, ["lib.py"]),
                task("T2", 1, ["src/a/**"], depends=["T1"]),
                task("T3", 2, ["src/a/x.py"], depends=["T1", "T2"])]
        self.assertEqual(plancheck.plan_check(plan), [])
        # A file name that only shares a prefix is not a directory prefix.
        plan = [task("T1", 0, ["lib.py"]),
                task("T2", 1, ["bin/anvil"], depends=["T1"]),
                task("T3", 1, ["bin/anvil_cli/x.py", "bin/anvil.cmd"], depends=["T1"])]
        self.assertEqual(plancheck.plan_check(plan), [])
        # Globs whose literal prefixes or suffixes can't meet share no files.
        for a, b in [("*.ts", "*.py"), ("src/**/*.ts", "src/**/*.py"),
                     ("src/a/**", "src/b/**"), ("app/[id]/*.tsx", "app/i/page.tsx")]:
            self.assertFalse(plancheck.overlaps(a, b), (a, b))

    def test_shared_resource_same_wave_fails(self):
        plan = [task("T1", 0, ["lib.py"]),
                task("T2", 1, ["a.py"], ["port:5173", "db"], ["T1"]),
                task("T3", 1, ["b.py"], ["port:5173"], ["T1"]),
                task("T4", 2, ["c.py"], ["db"], ["T1"])]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["shared-resource"])
        self.assertEqual(found[0].tasks, ["T2", "T3"])
        self.assertIn("port:5173", found[0].detail)
        # Rule 9: resource ids must be well-formed.
        plan = [task("T1", 0, ["lib.py"], ["port:abc", "redis", "devserver"]),
                task("T2", 1, ["a.py"], ["lockfile"], ["T1"])]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["shared-id", "shared-id"])
        self.assertEqual(sorted(f.detail.split()[0] for f in found), ["port:abc", "redis"])

    def test_dependency_on_same_or_later_wave_fails(self):
        plan = [task("T1", 0, ["lib.py"]),
                task("T2", 1, ["a.py"], depends=["T1", "T3"]),   # T3 is in the same wave
                task("T3", 1, ["b.py"], depends=["T1", "T4"]),   # T4 is later
                task("T4", 2, ["c.py"], depends=["T1"])]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["depends-wave", "depends-wave"])
        self.assertEqual(sorted(f.tasks for f in found), [["T2", "T3"], ["T3", "T4"]])
        # Rule 7: unknown ids in Depends.
        plan = [task("T1", 0, ["lib.py"]), task("T2", 1, ["a.py"], depends=["T1", "T9"])]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["unknown-depends"])
        self.assertIn("T9", found[0].detail)
        # Rule 6: a wave-0 task nothing depends on is not a foundation task.
        plan = [task("T1", 0, ["lib.py"]), task("T2", 0, ["x.py"]),
                task("T3", 1, ["a.py"], depends=["T1"])]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["wave-0"])
        self.assertEqual(found[0].tasks, ["T2"])
        # Rule 8: at most 4 tasks per wave.
        plan = [task("T1", 0, ["lib.py"])] + [
            task(f"T{i}", 1, [f"m{i}.py"], depends=["T1"]) for i in range(2, 7)]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["wave-width"])
        self.assertEqual(len(found[0].tasks), 5)

    def test_integrator_only_paths(self):
        for path in ["package-lock.json", "web/pnpm-lock.yaml", "go.sum",
                     "db/migrations/001_init.sql", "migrations/002.sql",
                     "src/generated/**", "src\\generated\\api.ts",
                     "db/migrations", "src/generated", "CARGO.LOCK"]:
            plan = [task("T1", 0, ["lib.py"]), task("T2", 1, ["a.py", path], depends=["T1"])]
            found = plancheck.plan_check(plan)
            self.assertEqual(rules(found), ["integrator-only"], path)
            self.assertEqual(found[0].tasks, ["T2"])
        plan = [task("T1", 0, ["lib.py"]), task("T2", 1, ["package.json", "src/migrate.py"],
                                                   depends=["T1"])]
        self.assertEqual(plancheck.plan_check(plan), [])
        # Rule 5: a task with no spec line needs review "skip (fully specified)".
        plan = [task("T1", 0, ["lib.py"]),
                task("T2", 1, ["a.py"], depends=["T1"], spec=()),
                task("T3", 1, ["b.py"], depends=["T1"], spec=("§7.5",))]
        found = plancheck.plan_check(plan)
        self.assertEqual(rules(found), ["no-spec", "no-spec"])

    def test_lane_check_flags_outside_write(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            write(repo / "docs/demo/plan.md",
                  "# Plan: demo\n\n## Task table\n\n"
                  "| Task | Spec | Writes | Shared | Depends | Wave | Review |\n"
                  "|---|---|---|---|---|---|---|\n"
                  "| T1 | S1 | `src/types.py` | - | - | 0 | yes |\n"
                  "| T2 | S1 | `src/a/**`, `tests/test_a.py` | - | T1 | 1 | yes |\n"
                  "| T3 | S1 | `src/b.py` | - | T1 | 1 | yes |\n", crlf=True)
            write(repo / "src/old.py", "old = 1\n")
            write(repo / "lib/util.py", "u = 1\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "plan")
            lane = Path(tmp) / "lane-T2"
            git(repo, "worktree", "add", "-q", str(lane), "-b", "lane-T2", "main")

            # Another lane (T3) lands on main after T2's worktree was cut.
            write(repo / "src/b.py", "b = 1\n")
            git(repo, "add", "-A")
            git(repo, "commit", "-q", "-m", "T3")

            write(lane / "src/a/x.py", "x = 1\n")
            write(lane / "tests/test_a.py", "pass\n")
            write(lane / "src/c.py", "c = 1\n")                  # outside T2's writes
            git(lane, "add", "-A")
            git(lane, "mv", "src/old.py", "src/a/old.py")        # a rename into the write set
            git(lane, "commit", "-q", "-m", "T2")

            tasks = {t.id: t for t in plancheck.docs.parse_tasks(
                plancheck.docs.read_text(lane / "docs/demo/plan.md"))}
            # Only T2's own diff, against T2's own write set: T3's src/b.py is not reported.
            # A rename reports its source path too.
            self.assertEqual(plancheck.lane_check(lane, tasks["T2"], "main"),
                             ["src/c.py", "src/old.py"])
            self.assertEqual(plancheck.lane_check(lane, tasks["T3"], "main"),
                             ["src/a/old.py", "src/a/x.py", "src/c.py", "src/old.py",
                              "tests/test_a.py"])

            # The CLI also catches uncommitted and untracked changes.
            write(lane / "src/a/y.py", "y = 1\n")
            write(lane / "notes.txt", "scratch\n")
            write(lane / "README.md", "# changed\n")
            git(lane, "mv", "lib/util.py", "src/a/util.py")      # staged rename
            write(lane / "src/a/generated/api.ts", "x\n")        # integrator-only, inside writes
            write(lane / "docs/demo/progress.md", "- [~] T2\n")  # orchestrator-owned, ignored
            state.save(lane, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "build"})
            out, old = io.StringIO(), os.getcwd()
            try:
                os.chdir(lane)
                with contextlib.redirect_stdout(out):
                    code = cli.main(["lane-check", "T2", "--base", "main"])
                with contextlib.redirect_stdout(io.StringIO()) as js:
                    cli.main(["lane-check", "T2", "--base", "main", "--json"])
            finally:
                os.chdir(old)
            self.assertEqual(code, 1)
            for path in ["src/c.py", "notes.txt", "README.md"]:
                self.assertIn(path, out.getvalue())
            self.assertNotIn("src/a/y.py", out.getvalue())
            self.assertEqual(json.loads(js.getvalue()),
                             ["README.md", "lib/util.py", "notes.txt", "src/a/generated/api.ts",
                              "src/c.py", "src/old.py"])


if __name__ == "__main__":
    unittest.main()
