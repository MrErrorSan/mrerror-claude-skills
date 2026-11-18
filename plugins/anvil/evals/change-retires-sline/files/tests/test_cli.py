import json
import tempfile
import unittest
from pathlib import Path

from ledger import cli


class ExportCommandTest(unittest.TestCase):
    def test_export_writes_every_invoice(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "invoices.json"
            data.write_text(json.dumps([
                {"id": "INV-1", "customer": "Blue Harbor", "total_cents": 1999, "issued": "2026-09-30"},
                {"id": "INV-2", "customer": "Northwind", "total_cents": 42000, "issued": "2026-10-14"}]))
            out = Path(tmp) / "out.csv"
            self.assertEqual(cli.main(["--data", str(data), "export", "--csv", str(out)]), 0)
            self.assertEqual(len(out.read_text(encoding="utf-8").splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
