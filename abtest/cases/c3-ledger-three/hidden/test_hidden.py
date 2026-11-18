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
ROWS = [["INV-1001", "Blue Harbor Cafe", "19.99", "2026-09-30"],
        ["INV-1002", "Acme, Ltd.", "1250.50", "2026-10-02"],
        ["INV-1003", "Northwind Traders", "420.00", "2026-10-14"]]


class Hidden(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.data = self.dir / "inv.json"
        self.data.write_text(json.dumps(SAMPLE), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def ledger(self, *args, data=None):
        return run("-m", "ledger", "--data", str(data or self.data), *args)

    def test_core_csv_header_rows_order_and_quoting(self):
        out = self.dir / "out.csv"
        r = self.ledger("export", "--csv", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = out.read_text(encoding="utf-8")
        self.assertEqual(text.splitlines()[0], "id,customer,total,issued")
        self.assertEqual(list(csv.reader(text.splitlines()))[1:], ROWS)
        self.assertIn('"Acme, Ltd."', text)

    def test_core_json_rows(self):
        out = self.dir / "out.json"
        r = self.ledger("export", "--json", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual([[o["id"], o["customer"], o["total"], o["issued"]] for o in rows], ROWS)
        self.assertEqual(set(rows[0]), {"id", "customer", "total", "issued"})

    def test_core_list_since_is_inclusive(self):
        r = self.ledger("list", "--since", "2026-10-02")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([l.split()[0] for l in r.stdout.splitlines() if l.strip()], ["INV-1002", "INV-1003"])

    def test_core_list_without_since_unchanged(self):
        r = self.ledger("list")
        self.assertEqual([l.split()[0] for l in r.stdout.splitlines() if l.strip()],
                         ["INV-1001", "INV-1002", "INV-1003"])

    def test_edge_since_bad_date_is_rejected(self):
        r = self.ledger("list", "--since", "14/10/2026")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)

    def test_edge_since_after_everything_prints_nothing(self):
        r = self.ledger("list", "--since", "2030-01-01")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "")

    def test_edge_csv_with_no_invoices_is_header_only(self):
        empty = self.dir / "empty.json"
        empty.write_text("[]", encoding="utf-8")
        out = self.dir / "e.csv"
        r = self.ledger("export", "--csv", str(out), data=empty)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(out.read_text(encoding="utf-8").splitlines(), ["id,customer,total,issued"])

    def test_brief_export_without_a_format_is_an_error(self):
        r = self.ledger("export")
        self.assertNotEqual(r.returncode, 0)

    def test_brief_export_both_formats_at_once(self):
        c, j = self.dir / "b.csv", self.dir / "b.json"
        r = self.ledger("export", "--csv", str(c), "--json", str(j))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(c.exists() and j.exists())
