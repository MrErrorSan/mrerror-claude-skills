import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from ledger import model


class ModelTest(unittest.TestCase):
    def test_load_reads_every_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invoices.json"
            path.write_text(json.dumps([{"id": "INV-1", "customer": "Northwind",
                                         "total_cents": 1250, "issued": "2026-10-01"}]))
            [inv] = model.load(path)
        self.assertEqual(inv, model.Invoice("INV-1", "Northwind", 1250, date(2026, 10, 1)))

    def test_money_pads_cents(self):
        self.assertEqual(model.money(1205), "12.05")
        self.assertEqual(model.money(7), "0.07")


if __name__ == "__main__":
    unittest.main()
