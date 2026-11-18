import tempfile
import unittest
from datetime import date
from pathlib import Path

from ledger.export import format_row, write_csv
from ledger.model import Invoice


class ExportTest(unittest.TestCase):
    def export(self, invoices):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            write_csv(invoices, path)
            return path.read_text(encoding="utf-8").splitlines()

    def test_header_then_rows_oldest_first(self):
        lines = self.export([Invoice("INV-2", "Northwind", 42000, date(2026, 10, 14)),
                             Invoice("INV-1", "Blue Harbor", 1999, date(2026, 9, 30))])
        self.assertEqual(lines, ["id,customer,total,issued",
                                 "INV-1,Blue Harbor,19.99,2026-09-30",
                                 "INV-2,Northwind,420.00,2026-10-14"])

    def test_customer_with_comma_is_quoted(self):
        lines = self.export([Invoice("INV-3", "Acme, Ltd.", 125050, date(2026, 10, 2))])
        self.assertEqual(lines[1], 'INV-3,"Acme, Ltd.",1250.50,2026-10-02')

    def test_format_row_options(self):
        self.assertEqual(format_row(["inv-1", " a "], delimiter=";", upper_ids=True), "INV-1;a\n")
        self.assertEqual(format_row(["x"], quote_all=True), '"x"\n')


if __name__ == "__main__":
    unittest.main()
