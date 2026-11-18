import unittest
from datetime import date

from ledger import report
from ledger.model import Invoice


class ReportTest(unittest.TestCase):
    def test_net_by_customer_subtracts_refunds(self):
        invoices = [Invoice("I1", "Ana", 5000, date(2026, 10, 1)),
                    Invoice("R1", "Ana", 1500, date(2026, 10, 2), "refund"),
                    Invoice("I2", "Ben", 700, date(2026, 10, 3))]
        self.assertEqual(report.net_by_customer(invoices), {"Ana": 3500, "Ben": 700})

    def test_render_ends_with_refunds_and_net(self):
        invoices = [Invoice("I1", "Ana", 5000, date(2026, 10, 1))]
        lines = report.render(invoices)
        self.assertTrue(lines[-2].startswith("Refunds"))
        self.assertTrue(lines[-1].startswith("Net"))
        self.assertTrue(lines[-1].endswith("50.00"))


if __name__ == "__main__":
    unittest.main()
