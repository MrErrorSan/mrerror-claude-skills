# CSV export: implementation plan

- **Spec:** [spec.md](spec.md)
- **Approved:** 2026-11-16 by Saad ("plan approved, build it")
- **Synced branch:** csv-export (local)
- **Size:** full

**Goal:** `ledger export --csv <path>`.

**Architecture:** one `write_csv` function in `ledger/export.py`, called by a new `export` subcommand in `ledger/cli.py`.

**Tech stack:** Python 3.10+, standard library (`csv`), `unittest`.

## Global constraints

- Python 3.10+, standard library only.
- Mode: normal.

## Review focus

1. A customer name with a comma or a quote character in it. Test: `tests/test_export.py` (T1).

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S2, S3, S4 | `ledger/export.py`, `tests/test_export.py` | - | - | 1 | yes |
| T2 | S1 | `ledger/cli.py`, `tests/test_cli.py` | - | T1 | 2 | yes |
| T3 | S5 | `ledger/cli.py`, `tests/test_cli.py` | - | T2 | 3 | yes |

Integrator-only: none.

## T1: write_csv

- **Spec:** S2, S3, S4.
- **Interfaces (produces):** `ledger/export.py`: `write_csv(invoices: list[Invoice], path: Path) -> int`.
- **Tests:** `tests/test_export.py` (keep, S2, S3, S4): header then rows oldest first; a customer with a comma is quoted. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_export`.
- **Steps:** 1. Write `write_csv` with `csv.writer`. 2. Write the tests and run them.

## T2: export subcommand

- **Spec:** S1.
- **Interfaces (consumes):** `write_csv` (T1).
- **Tests:** `tests/test_cli.py` (keep, S1): export writes a header plus one row per invoice. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_cli`.
- **Steps:** 1. Add `export --csv <path>` to `ledger/cli.py`. 2. Write the test and run it.

## T3: confirmation line

- **Spec:** S5.
- **Interfaces (consumes):** the row count `write_csv` returns (T1).
- **Tests:** `tests/test_cli.py` (keep, S5): stdout is `Wrote 2 invoices to <path>`. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_cli`.
- **Steps:** 1. Print the line after `write_csv` returns. 2. Extend the test and run it.

## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `tests/test_export.py` | keep | S2, S3, S4 | A file the spreadsheet can't read | T1 |
| `tests/test_cli.py` | keep | S1, S5 | The command not writing the file | T2 |
| smoke: `python3 -m ledger export --csv /tmp/out.csv` writes 4 lines | smoke | S1, S2 | The whole export path | T2 |

- Full suite: `python3 -m unittest discover -s tests`, about 1 second.
- Type-check: none.

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | waves 1–3 (T1, T2, T3) | `feat(ledger): CSV export` | no |

## Execution

Sequential: three tasks in a chain (T2 needs T1, T3 needs T2).

Checkpoints: none.
