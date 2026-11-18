"""CSV export after the mid-build change: semicolon separator, decimal comma."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from .helper import run

SAMPLE = [
    {"id": "INV-1003", "customer": "Northwind Traders", "total_cents": 42000, "issued": "2026-10-14"},
    {"id": "INV-1001", "customer": "Blue Harbor Cafe", "total_cents": 1999, "issued": "2026-09-30"},
    {"id": "INV-1002", "customer": "Acme, Ltd.", "total_cents": 125050, "issued": "2026-10-02"},
]


class Hidden(unittest.TestCase):
    def export(self, rows):
        with tempfile.TemporaryDirectory() as tmp:
            data, out = Path(tmp) / "i.json", Path(tmp) / "o.csv"
            data.write_text(json.dumps(rows), encoding="utf-8")
            r = run("-m", "ledger", "--data", str(data), "export", "--csv", str(out))
            self.assertEqual(r.returncode, 0, r.stderr)
            return out.read_text(encoding="utf-8-sig")

    def test_core_header_uses_semicolons(self):
        self.assertEqual(self.export(SAMPLE).splitlines()[0], "id;customer;total;issued")

    def test_core_rows_semicolon_decimal_comma_oldest_first(self):
        rows = list(csv.reader(self.export(SAMPLE).splitlines(), delimiter=";"))[1:]
        self.assertEqual(rows, [["INV-1001", "Blue Harbor Cafe", "19,99", "2026-09-30"],
                                ["INV-1002", "Acme, Ltd.", "1250,50", "2026-10-02"],
                                ["INV-1003", "Northwind Traders", "420,00", "2026-10-14"]])

    def test_core_no_comma_separated_output_left(self):
        self.assertNotIn("id,customer,total,issued", self.export(SAMPLE))

    def test_edge_customer_with_semicolon_is_quoted(self):
        rows = list(csv.reader(self.export(
            [{"id": "X1", "customer": "Semi; Colon GmbH", "total_cents": 500, "issued": "2026-10-01"}]
        ).splitlines(), delimiter=";"))
        self.assertEqual(rows[1], ["X1", "Semi; Colon GmbH", "5,00", "2026-10-01"])
