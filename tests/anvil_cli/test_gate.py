import datetime
import tempfile
import unittest
from pathlib import Path

from anvil_cli import docs, gate, state

from .helpers import make_repo, write

DOC = """# {kind}: demo

- **Approved:** no
- **Size:** {size}

## Body
- **S1** One behavior.
"""


class GateTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.repo = make_repo(Path(self._tmp.name))
        self.today = datetime.date.today().isoformat()

    def tearDown(self):
        self._tmp.cleanup()

    def topic(self, size="full", spec=True):
        state.save(self.repo, "active.json",
                   {"slug": "demo", "dir": "docs/demo", "size": size, "stage": "spec"})
        d = self.repo / "docs" / "demo"
        if spec:
            write(d / "spec.md", DOC.format(kind="Spec", size=size))
        write(d / "plan.md", DOC.format(kind="Plan", size=size))
        return d

    def prompt(self, text, ts):
        state.append_jsonl(self.repo, "prompts.jsonl", {"ts": ts, "prompt": text})

    def presented_ts(self, which):
        return state.load(self.repo, "presented.json", {})[which]["ts"]

    def approved(self, path):
        return docs.parse_header(docs.read_text(path))["Approved"]

    def approve_spec(self):
        self.prompt("approve the spec yourself", 0.5)
        gate.approve(self.repo, "spec", "approve the spec yourself", pre=True)

    def test_approve_requires_prompt_after_present(self):
        d = self.topic()
        gate.present(self.repo, "spec")
        ts = self.presented_ts("spec")
        self.prompt("yes I approve the spec", ts - 5)
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "spec", "I approve the spec")
        self.assertEqual(self.approved(d / "spec.md"), "no")

        self.prompt("Looks good, I approve the spec.", ts + 1)
        value = gate.approve(self.repo, "spec", "I approve the spec")
        self.assertEqual(value, f'{self.today} by Saad ("I approve the spec")')
        self.assertEqual(self.approved(d / "spec.md"), value)

    def test_approve_rejects_changed_doc(self):
        d = self.topic()
        self.approve_spec()
        gate.present(self.repo, "plan")
        ts = self.presented_ts("plan")
        write(d / "plan.md", DOC.format(kind="Plan", size="full") + "- **S2** Added later.\n")
        self.prompt("ok approve the plan", ts + 1)
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "plan", "ok approve the plan")
        self.assertEqual(self.approved(d / "plan.md"), "no")

        # Same text with CRLF line endings is the same document.
        write(d / "plan.md", DOC.format(kind="Plan", size="full"), crlf=True)
        gate.present(self.repo, "plan")
        write(d / "plan.md", DOC.format(kind="Plan", size="full"))
        self.prompt("ok approve the plan", self.presented_ts("plan") + 1)
        gate.approve(self.repo, "plan", "ok approve the plan")
        self.assertTrue(self.approved(d / "plan.md").startswith(self.today))

    def test_pre_approval_quote_must_exist(self):
        d = self.topic()
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "spec", "approve the spec yourself", pre=True)
        # A pre-approval needs 3+ words, even when the short quote is a whole message.
        self.prompt("skip it", 0.5)
        with self.assertRaisesRegex(gate.GateError, "3"):
            gate.approve(self.repo, "spec", "skip it", pre=True)
        self.assertEqual(self.approved(d / "spec.md"), "no")
        # Logged before the doc existed or was presented: still a valid pre-approval.
        self.prompt("Build the thing. Approve the spec yourself.", 1.0)
        value = gate.approve(self.repo, "spec", "approve the spec yourself", pre=True)
        self.assertEqual(value, f'pre-approved by Saad {self.today} ("approve the spec yourself")')
        self.assertEqual(self.approved(d / "spec.md"), value)

    def test_invented_quote_rejected(self):
        self.topic()
        self.prompt("Build the thing and show me the spec first.", 1.0)
        gate.present(self.repo, "spec")
        self.prompt("I need to think about the spec.", self.presented_ts("spec") + 1)
        for kwargs in ({}, {"pre": True}):
            with self.assertRaises(gate.GateError):
                gate.approve(self.repo, "spec", "approve the spec yourself", **kwargs)
        # A short fragment of a longer prompt is not a quote.
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "spec", "the spec", pre=True)
        # Part of a word is not a match.
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "spec", "ink about the spec", pre=True)
        with self.assertRaises(gate.GateError):
            gate.afk_on(self.repo, "I'm going AFK now")
        self.assertFalse(gate.afk_status(self.repo)["on"])

    def test_quote_normalised(self):
        self.topic()
        self.prompt("Okay,  that’s all\r\nlooks GOOD — “go straight to the build”", 1.0)
        self.assertTrue(gate.quote_in_prompts(
            self.repo, "that's all looks good", None))
        self.assertTrue(gate.quote_in_prompts(
            self.repo, '"Go straight  to the BUILD"', None))
        self.assertFalse(gate.quote_in_prompts(self.repo, "that's all looks good", 2.0))
        value = gate.approve(self.repo, "plan", "go  straight to\nthe build", pre=True)
        self.assertEqual(value, f'pre-approved by Saad {self.today} ("go straight to the build")')
        # After present, a whole short message is a real answer, even under 3 words.
        gate.present(self.repo, "spec")
        self.prompt("1 yes", self.presented_ts("spec") + 1)
        gate.approve(self.repo, "spec", "1 yes")

    def test_check_build_needs_plan_approved(self):
        d = self.topic()
        self.assertFalse(gate.check(self.repo, "plan")[0])
        self.assertFalse(gate.check(self.repo, "build")[0])
        # The plan can't be presented before the spec is approved, so one reply
        # can't pass both stops.
        with self.assertRaises(gate.GateError):
            gate.present(self.repo, "plan")
        self.assertNotIn("plan", state.load(self.repo, "presented.json", {}))
        # A hand-edited header is not an approval.
        write(d / "plan.md", docs.set_header(docs.read_text(d / "plan.md"), "Approved", "yes"))
        self.assertFalse(gate.check(self.repo, "build")[0])

        self.prompt("approve the spec yourself and approve the plan yourself", 1.0)
        gate.approve(self.repo, "spec", "approve the spec yourself", pre=True)
        self.assertTrue(gate.check(self.repo, "plan")[0])
        self.assertFalse(gate.check(self.repo, "build")[0])
        gate.approve(self.repo, "plan", "approve the plan yourself", pre=True)
        self.assertTrue(gate.check(self.repo, "build")[0])

        # Direct size: no spec, so the plan stage is open and only the plan gates the build.
        self.topic(size="direct", spec=False)
        (d / "spec.md").unlink()
        self.assertTrue(gate.check(self.repo, "plan")[0])
        self.assertFalse(gate.check(self.repo, "build")[0])
        with self.assertRaises(gate.GateError):
            gate.present(self.repo, "spec")

    def test_afk_on_needs_afk_phrase(self):
        self.topic()
        self.prompt("Please approve the plan now.", 1.0)
        with self.assertRaises(gate.GateError):
            gate.afk_on(self.repo, "approve the plan now")
        self.assertFalse(gate.afk_status(self.repo)["on"])

        self.prompt("I'm going to bed, run with it.", 2.0)
        gate.afk_on(self.repo, "I'm going to bed")
        status = gate.afk_status(self.repo)
        self.assertTrue(status["on"])
        self.assertEqual(status["quote"], "I'm going to bed")

        # With AFK on, a stop can be skipped. It is recorded with the quote that
        # turned AFK on, whatever quote the caller passes.
        value = gate.approve(self.repo, "spec", "an invented reason", afk=True)
        self.assertEqual(value, f'skipped (AFK) {self.today} ("I\'m going to bed")')

        gate.afk_off(self.repo)
        self.assertFalse(gate.afk_status(self.repo)["on"])
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "plan", "I'm going to bed", afk=True)

        # Only the last recorded message can turn AFK on.
        self.prompt("Actually, wait for me on the plan.", 3.0)
        with self.assertRaises(gate.GateError):
            gate.afk_on(self.repo, "I'm going to bed")
        self.assertFalse(gate.afk_status(self.repo)["on"])

    def test_pre_approval_window_starts_at_topic_request(self):
        d = self.topic()
        topic = state.active_topic(self.repo)
        state.save(self.repo, "active.json", {**topic, "started": 10.0})
        self.prompt("Old topic: approve the spec yourself.", 1.0)          # last week
        self.prompt("Build the export and approve the plan yourself.", 8.0)  # started the topic
        self.prompt("Go straight to the build.", 12.0)
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "spec", "approve the spec yourself", pre=True)
        self.assertEqual(self.approved(d / "spec.md"), "no")
        # The request that started the topic still counts, and so do later messages.
        self.prompt("ok approve the spec now", 13.0)
        gate.approve(self.repo, "spec", "approve the spec now", pre=True)
        gate.approve(self.repo, "plan", "approve the plan yourself", pre=True)
        gate.approve(self.repo, "plan", "go straight to the build", pre=True)

    def test_afk_skip_needs_afk_from_this_topic(self):
        self.topic()
        topic = state.active_topic(self.repo)
        state.save(self.repo, "active.json", {**topic, "started": 10.0})
        state.save(self.repo, "afk.json", {"on": True, "ts": 5.0, "quote": "I'm AFK"})
        self.assertFalse(gate.afk_status(self.repo)["on"])
        with self.assertRaises(gate.GateError):
            gate.approve(self.repo, "spec", "x", afk=True)
        state.save(self.repo, "afk.json", {"on": True, "ts": 11.0, "quote": "I'm AFK"})
        self.assertTrue(gate.afk_status(self.repo)["on"])
        self.assertIn("skipped (AFK)", gate.approve(self.repo, "spec", "x", afk=True))

    def test_approve_keeps_crlf(self):
        d = self.topic()
        write(d / "spec.md", DOC.format(kind="Spec", size="full"), crlf=True)
        gate.present(self.repo, "spec")
        self.prompt("yes approve the spec", self.presented_ts("spec") + 1)
        value = gate.approve(self.repo, "spec", "yes approve the spec")
        raw = (d / "spec.md").read_bytes()
        self.assertIn(f"- **Approved:** {value}\r\n".encode("utf-8"), raw)
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        self.assertTrue(raw.startswith(b"# Spec: demo\r\n\r\n"))


if __name__ == "__main__":
    unittest.main()
