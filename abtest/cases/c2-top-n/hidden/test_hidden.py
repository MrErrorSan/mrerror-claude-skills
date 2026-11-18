import tempfile
import unittest
from pathlib import Path

from .helper import run


def wf(text, *args):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.txt"
        p.write_text(text, encoding="utf-8")
        return run("-m", "wordfreq", *args, str(p))


class Hidden(unittest.TestCase):
    def test_core_top_two(self):
        r = wf("b a b c a b", "--top", "2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), ["3 b", "2 a"])

    def test_core_ties_at_cutoff_stay_alphabetical(self):
        self.assertEqual(wf("c b a", "--top", "2").stdout.splitlines(), ["1 a", "1 b"])

    def test_core_n_larger_than_word_count_prints_all(self):
        self.assertEqual(wf("pond frog pond", "--top", "10").stdout.splitlines(), ["2 pond", "1 frog"])

    def test_core_without_top_unchanged(self):
        self.assertEqual(wf("pond frog pond").stdout.splitlines(), ["2 pond", "1 frog"])

    def test_edge_negative_n_is_rejected(self):
        r = wf("a b c", "--top", "-1")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_edge_non_integer_n_is_rejected(self):
        r = wf("a b c", "--top", "abc")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "")

    def test_brief_top_zero_prints_nothing_and_succeeds(self):
        r = wf("a b c", "--top", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "")

    def test_brief_error_mentions_top(self):
        self.assertIn("--top", wf("a b c", "--top", "-3").stderr)
