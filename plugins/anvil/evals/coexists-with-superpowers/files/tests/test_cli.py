import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

from shelf import cli, messages


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["SHELF_FILE"] = str(Path(self.tmp.name) / "shelf.json")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.main(list(argv))
        return out.getvalue()

    def test_add_confirms_with_the_url(self):
        out = self.run_cli("add", "https://example.com")
        self.assertEqual(out.strip(), messages.SAVED.format(url="https://example.com"))

    def test_list_empty(self):
        self.assertEqual(self.run_cli("list").strip(), messages.EMPTY)

    def test_list_newest_first_with_tags(self):
        self.run_cli("add", "https://a.example", "--tag", "read")
        self.run_cli("add", "https://b.example")
        lines = self.run_cli("list").splitlines()
        self.assertEqual(lines[1].strip(), "https://b.example")
        self.assertEqual(lines[2].strip(), "https://a.example  #read")


if __name__ == "__main__":
    unittest.main()
