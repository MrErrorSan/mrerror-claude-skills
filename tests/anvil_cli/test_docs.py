import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from anvil_cli import docs, state

from .helpers import make_repo, write

SPEC = """# Spec: demo

- **Approved:** no
- **Mode:** normal
- **Size:** full

## Spec lines

- ~~**S1** Old behavior.~~ RETIRED → S7 (2026-11-20, CR: reason)
- **S2** Second behavior.
- **S7** New behavior.

## Decisions
- not an S-line
"""

PLAN = """# Plan: demo

- **Spec:** [spec](spec.md)
- **Approved:** no
- **Size:** full
- **Synced branch:** demo (local)

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S2 | `src/types.ts`, `src/api/*.ts` | - | - | 0 | yes |
| T2 | S2, S7 | `src/a/{x,y}.ts` | port:3000, db | T1 | 1 | skip (fully specified) |

## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `tests/a.test.ts` | keep | S2, S7 | the login flow \\| the session | T2 |
| smoke: app starts | smoke | - | everything | T1 |

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | wave 0 (T1) | `feat: types` | no |
| C2 | wave 1 (T2) | `feat: a` | yes |
"""

DIRECT_PLAN = """# Plan: fix-login

- **Approved:** no
- **Size:** direct

## Spec lines

- **S1** Login works with a trailing space in the email.

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1 | `src/login.ts` | - | - | 0 | yes |
"""


class DocsTests(unittest.TestCase):
    def test_parse_live_and_retired_slines(self):
        lines = docs.parse_slines(SPEC)
        self.assertEqual([s.num for s in lines], [1, 2, 7])
        old = lines[0]
        self.assertTrue(old.retired)
        self.assertEqual(old.replaced_by, 7)
        self.assertEqual(old.text, "Old behavior.")
        self.assertEqual(lines[1], docs.SLine(2, "Second behavior.", False, None))
        self.assertFalse(lines[2].retired)
        # S-lines quoted inside a fenced code block are examples, not S-lines.
        fenced = SPEC + "\n```markdown\n- **S9** An example.\n- ~~**S8** Old.~~ RETIRED\n```\n"
        self.assertEqual(docs.parse_slines(fenced), lines)
        after = docs.parse_slines(fenced + "- **S10** After the fence.\n")
        self.assertEqual([s.num for s in after], [1, 2, 7, 10])

    def test_parse_crlf(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = write(Path(tmp) / "spec.md", SPEC, crlf=True)
            plan = write(Path(tmp) / "plan.md", PLAN, crlf=True)
            self.assertIn(b"\r\n", spec.read_bytes())
            text = docs.read_text(spec)
            self.assertNotIn("\r", text)
            self.assertEqual(docs.parse_slines(text), docs.parse_slines(SPEC))
            raw = spec.read_bytes().decode("utf-8")  # parsers take CRLF text too
            self.assertEqual(docs.parse_slines(raw), docs.parse_slines(SPEC))
            self.assertEqual(docs.parse_header(raw)["Approved"], "no")
            self.assertEqual(docs.parse_tasks(plan.read_bytes().decode("utf-8")),
                             docs.parse_tasks(PLAN))
            updated = docs.set_header(raw, "Approved", '2026-11-18 by Saad ("ok go")')
            self.assertIn('- **Approved:** 2026-11-18 by Saad ("ok go")\r\n', updated)
            self.assertNotIn("\n", updated.replace("\r\n", ""))
            self.assertEqual(docs.parse_header(updated)["Mode"], "normal")

    def test_task_table_and_commit_points(self):
        header = docs.parse_header(PLAN)
        self.assertEqual(header["Synced branch"], "demo (local)")
        self.assertEqual(header["Size"], "full")
        t1, t2 = docs.parse_tasks(PLAN)
        self.assertEqual(t1, docs.Task("T1", ["S2"], ["src/types.ts", "src/api/*.ts"],
                                       [], [], 0, "yes"))
        self.assertEqual(t2.spec, ["S2", "S7"])
        self.assertEqual(t2.writes, ["src/a/{x,y}.ts"])
        self.assertEqual(t2.shared, ["port:3000", "db"])
        self.assertEqual(t2.depends, ["T1"])
        self.assertEqual(t2.wave, 1)
        self.assertEqual(t2.review, "skip (fully specified)")
        c1, c2 = docs.parse_commit_points(PLAN)
        self.assertEqual(c1, docs.CommitPoint("C1", "wave 0 (T1)", "feat: types", False))
        self.assertTrue(c2.push)

    def test_test_list_table(self):
        keep, smoke = docs.parse_tests(PLAN)
        self.assertEqual(keep, docs.TestEntry("tests/a.test.ts", "keep", ["S2", "S7"],
                                              "the login flow | the session", "T2"))
        self.assertEqual(smoke.type, "smoke")
        self.assertEqual(smoke.spec, [])

    def test_direct_size_reads_slines_from_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            topic = Path(tmp) / "docs" / "fix-login"
            write(topic / "plan.md", DIRECT_PLAN)
            spec, plan = docs.topic_docs(topic)
            self.assertIsNone(spec)
            self.assertEqual(plan, topic / "plan.md")
            text = docs.read_text(plan)
            self.assertEqual(docs.parse_header(text)["Size"], "direct")
            self.assertEqual([s.num for s in docs.parse_slines(text)], [1])
            self.assertEqual(docs.parse_tasks(text)[0].spec, ["S1"])
            write(topic / "spec.md", SPEC)
            self.assertEqual(docs.topic_docs(topic), (topic / "spec.md", topic / "plan.md"))

    def test_spec_lines_from_subdirectory(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            write(repo / "docs" / "demo" / "spec.md", SPEC)
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "spec"})
            sub = repo / "src" / "deep"
            sub.mkdir(parents=True)
            out = io.StringIO()
            args = argparse.Namespace(live=True, retired=False, json=True)
            with contextlib.chdir(sub), contextlib.redirect_stdout(out):
                self.assertEqual(docs.cmd_spec_lines(args), 0)
            self.assertEqual([s["num"] for s in json.loads(out.getvalue())], [2, 7])


if __name__ == "__main__":
    unittest.main()
