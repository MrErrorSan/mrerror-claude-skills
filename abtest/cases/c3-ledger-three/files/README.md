# ledger

A small invoices CLI. Python 3.10+, standard library only.

- `python -m ledger list` prints every invoice, oldest first.
- Invoices are read from `data/invoices.json` (`--data <path>` to change it). Totals are
  stored in cents.

Tests: `python -m unittest discover -s tests`. The full suite takes about 20 s, because
`tests/test_integration.py` is slow (it stands in for the database-backed suite).
