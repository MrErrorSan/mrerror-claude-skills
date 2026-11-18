import unittest

from .helper import run


def report_lines():
    r = run("-m", "ledger", "report")
    assert r.returncode == 0, r.stderr
    return {l[:24].strip(): l[24:].strip() for l in r.stdout.splitlines() if l.strip()}


class Hidden(unittest.TestCase):
    def test_core_blue_harbor_net_is_minus_19_99(self):
        self.assertEqual(report_lines()["Blue Harbor Cafe"], "-19.99")

    def test_core_positive_balances_unchanged(self):
        lines = report_lines()
        self.assertEqual(lines["Acme, Ltd."], "1250.50")
        self.assertEqual(lines["Northwind Traders"], "407.50")
        self.assertEqual(lines["Net"], "1638.01")

    def test_edge_refunds_total_is_minus_52_48(self):
        self.assertEqual(report_lines()["Refunds"], "-52.48")

    def test_edge_money_formats_negative_amounts(self):
        from ledger.model import money
        self.assertEqual([money(c) for c in (-1999, -5, -100, -5248)],
                         ["-19.99", "-0.05", "-1.00", "-52.48"])

    def test_edge_money_positive_and_zero_unchanged(self):
        from ledger.model import money
        self.assertEqual([money(c) for c in (1205, 7, 0, 125050)], ["12.05", "0.07", "0.00", "1250.50"])
