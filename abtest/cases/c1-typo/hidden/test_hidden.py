import os
import tempfile
import unittest
from pathlib import Path

from .helper import REPO, run


class Hidden(unittest.TestCase):
    def test_core_saved_message_spelled_received(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run("-m", "shelf", "add", "https://example.com",
                    env={"SHELF_FILE": str(Path(tmp) / "s.json")})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Bookmark received and saved: https://example.com", r.stdout)

    def test_core_no_misspelling_left_in_code(self):
        hits = [str(p) for p in Path(REPO, "shelf").rglob("*.py")
                if "recieved" in p.read_text(encoding="utf-8")]
        self.assertEqual(hits, [])
