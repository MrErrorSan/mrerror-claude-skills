# ledger

A small invoices CLI. Python 3.10+, standard library only.

- `python3 -m ledger list` prints every invoice, oldest first.
- Invoices are read from `data/invoices.json` (`--data <path>` to change it). Totals are
  stored in cents.

Tests: `python3 -m unittest discover -s tests`
