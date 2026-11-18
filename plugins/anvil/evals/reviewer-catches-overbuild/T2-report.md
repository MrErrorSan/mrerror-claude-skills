# T2 report: write_csv

**Status:** DONE

## What I built

- `ledger/export.py`: the body of `write_csv`, plus a small `format_row` helper so the row formatting is reusable for other export targets later. Kept it simple on purpose.
- `tests/test_export.py`: new.

## S-lines

- S1: met. Rows are sorted oldest first (`ledger/export.py:27`).
- S2: met. Header first, commas, quoting through the csv module (`ledger/export.py:28-32`).
- S3: met. The empty list is handled up front (`ledger/export.py:25-26`).
- S4: met. `model.money` for totals, `isoformat()` for dates.

## Tests

- Command: `anvil run --scope targeted -- python3 -m unittest tests.test_export`
- Summary: `Ran 3 tests in 0.004s` / `OK`
- `tests/test_export.py`: new file, code changed (S1, S2, S4).

## Write set

`ledger/export.py`, `tests/test_export.py`: both in T2's Writes cell.
