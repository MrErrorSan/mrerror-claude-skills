# tally

Sales reports from a CSV of orders. Python 3.10+, standard library only.

- `python3 -m tally daily` prints revenue per day.
- Orders are read from `data/orders.csv` (columns: date, region, product, amount_cents).
- Reports are registered by name in `tally/registry.py`.

Tests: `python3 -m unittest discover -s tests` (about 1 second).
