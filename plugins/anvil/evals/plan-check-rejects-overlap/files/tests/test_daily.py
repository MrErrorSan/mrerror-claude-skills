import unittest
from datetime import date

from tally.orders import Order
from tally.reports import daily


class DailyTest(unittest.TestCase):
    def test_sums_per_day_in_order(self):
        orders = [Order(date(2026, 11, 3), "north", "mug", 1200),
                  Order(date(2026, 11, 2), "north", "kettle", 4500),
                  Order(date(2026, 11, 2), "south", "mug", 1200)]
        self.assertEqual(daily.run(orders), [("2026-11-02", 5700), ("2026-11-03", 1200)])


if __name__ == "__main__":
    unittest.main()
