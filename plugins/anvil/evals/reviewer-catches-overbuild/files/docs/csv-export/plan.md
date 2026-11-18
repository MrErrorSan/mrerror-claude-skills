# CSV export: implementation plan

- **Spec:** [spec.md](spec.md)
- **Approved:** 2026-11-16 by Saad ("plan approved, build it")
- **Synced branch:** csv-export (local)
- **Size:** full

**Goal:** `ledger export --csv <path>`.

**Architecture:** `write_csv` in `ledger/export.py`, called by the `export` subcommand in `ledger/cli.py`.

**Tech stack:** Python 3.10+, standard library (`csv`), `unittest`.

## Global constraints

- Python 3.10+, standard library only.
- Mode: normal.

## Review focus

1. An empty invoice list (S3). Test: `tests/test_export.py` (T2).

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1 | `ledger/export.py`, `ledger/cli.py` | - | - | 0 | yes |
| T2 | S1, S2, S3, S4 | `ledger/export.py`, `tests/test_export.py` | - | T1 | 1 | yes |

Integrator-only: none.

## T1: Foundations and the export subcommand

- **Spec:** S1.
- **Interfaces (produces):** `ledger/export.py`: `HEADER = ["id", "customer", "total", "issued"]`; `write_csv(invoices: list[Invoice], path: Path) -> int` (stub). `ledger/cli.py`: `export --csv <path>` calls `write_csv`.
- **Tests:** none of its own; the smoke path covers it once T2 lands.
- **Steps:** 1. Add the stub and `HEADER`. 2. Add the subcommand.

## T2: write_csv

- **Spec:** S1, S2, S3, S4.
- **Interfaces (consumes):** `HEADER`, `write_csv` signature (T1); `model.money` (existing).
- **Tests:** `tests/test_export.py` (keep, S1, S2, S3, S4): header then rows oldest first; a customer with a comma is quoted; an empty list writes only the header. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_export`.
- **Steps:** 1. Write the body of `write_csv` with `csv.writer` and `model.money`. 2. Write the tests and run them.

## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `tests/test_export.py` | keep | S1, S2, S3, S4 | A file the spreadsheet can't import | T2 |
| smoke: `python3 -m ledger export --csv /tmp/out.csv` writes 4 lines | smoke | S1, S2 | The whole export path | T2 |

- Full suite: `python3 -m unittest discover -s tests`, about 1 second.
- Type-check: none.

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | waves 0–1 (T1, T2) | `feat(ledger): CSV export` | no |

## Execution

Sequential: two tasks in a chain.

Checkpoints: none.
