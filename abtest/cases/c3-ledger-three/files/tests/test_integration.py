"""End-to-end check of `ledger list` against the sample data.

The sleep stands in for the real database-backed setup this suite has in production; it is
slow on purpose and must stay.
"""
import subprocess
import sys
import time
import unittest


class IntegrationTest(unittest.TestCase):
    def test_list_prints_sample_invoices_oldest_first(self):
        time.sleep(15)
        out = subprocess.run([sys.executable, "-m", "ledger", "list"], capture_output=True,
                             text=True, check=True).stdout.splitlines()
        self.assertEqual([line.split()[0] for line in out], ["INV-1001", "INV-1002", "INV-1003"])


if __name__ == "__main__":
    unittest.main()
