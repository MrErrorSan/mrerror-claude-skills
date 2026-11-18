import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from wordfreq import cli


class WordfreqTest(unittest.TestCase):
    def test_most_frequent_first_ties_alphabetical(self):
        self.assertEqual(cli.count_words("b a b c a b"), [("b", 3), ("a", 2), ("c", 1)])

    def test_case_is_ignored(self):
        self.assertEqual(cli.count_words("Frog frog FROG"), [("frog", 3)])

    def test_main_prints_count_then_word(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.txt"
            path.write_text("pond frog pond", encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                cli.main([str(path)])
        self.assertEqual(out.getvalue().splitlines(), ["2 pond", "1 frog"])


if __name__ == "__main__":
    unittest.main()
