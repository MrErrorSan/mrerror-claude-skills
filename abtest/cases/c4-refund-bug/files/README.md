# ledger

A small invoices CLI. Python 3.10+, standard library only.

- `python -m ledger list` prints every invoice and refund, oldest first.
- `python -m ledger report` prints the net balance per customer, then the refunds total and
  the overall net.
- Entries are read from `data/invoices.json` (`--data <path>` to change it). Totals are
  stored in cents; refunds have `"kind": "refund"` and a positive total.

Tests: `python -m unittest discover -s tests`
