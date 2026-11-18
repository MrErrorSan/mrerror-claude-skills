# Report filters: implementation plan

- **Spec:** [spec.md](spec.md)
- **Approved:** no
- **Synced branch:** report-filters (local)
- **Size:** full

**Goal:** region and date filters for every report, plus three new reports.

**Architecture:** one filter function the CLI applies before the chosen report runs; each report is a module with `run(orders)`, registered by name in `tally/registry.py`.

**Tech stack:** Python 3.10+, standard library, `unittest`.

## Global constraints

- Python 3.10+, standard library only.
- The `daily` report's output format doesn't change.
- Mode: normal.

## Review focus

1. A `--since` date in the future: every report prints nothing and exits 0. Test: `tests/test_filters.py` (T1).

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1, S2, S5 | `tally/filters.py`, `tests/test_filters.py` | - | - | 0 | yes |
| T2 | S1, S2, S5 | `tally/cli.py`, `tests/test_cli.py` | - | T1 | 1 | yes |
| T3 | S3 | `tally/reports/weekly.py`, `tally/registry.py`, `tests/test_weekly.py` | - | T1 | 1 | yes |
| T4 | S4 | `tally/reports/by_product.py`, `tally/registry.py`, `tests/test_by_product.py` | - | T1 | 1 | yes |
| T5 | S6 | `tally/reports/by_region.py`, `tally/registry.py`, `tests/test_by_region.py` | - | T1 | 1 | yes |

Integrator-only: none.

## T1: Filters

- **Spec:** S1, S2, S5.
- **Interfaces (produces):** `tally/filters.py`: `apply(orders: list[Order], region: str | None, since: date | None) -> list[Order]`.
- **Tests:** `tests/test_filters.py` (keep, S1, S2): region only, since only, both, a future `since` gives `[]`. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_filters`.
- **Steps:** 1. Write `apply`. 2. Write the tests and run them.

## T2: CLI flags

- **Spec:** S1, S2, S5.
- **Interfaces (consumes):** `filters.apply` (T1).
- **Tests:** `tests/test_cli.py` (keep, S1, S2, S5): `tally daily --region north` prints only north's days. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_cli`.
- **Steps:** 1. Add `--region` and `--since` to `tally/cli.py`, and call `filters.apply` before the report. 2. Write the test and run it.

## T3: Weekly report

- **Spec:** S3.
- **Interfaces (produces):** `tally/reports/weekly.py`: `run(orders) -> list[tuple[str, int]]`; registry entry `"weekly"`.
- **Tests:** `tests/test_weekly.py` (keep, S3): two orders in week 45 and one in week 46 give two rows, oldest first. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_weekly`.
- **Steps:** 1. Write `run`. 2. Register it in `tally/registry.py`. 3. Write the test and run it.

## T4: By-product report

- **Spec:** S4.
- **Interfaces (produces):** `tally/reports/by_product.py`: `run(orders) -> list[tuple[str, int]]`; registry entry `"by-product"`.
- **Tests:** `tests/test_by_product.py` (keep, S4): highest revenue first. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_by_product`.
- **Steps:** 1. Write `run`. 2. Register it in `tally/registry.py`. 3. Write the test and run it.

## T5: By-region report

- **Spec:** S6.
- **Interfaces (produces):** `tally/reports/by_region.py`: `run(orders) -> list[tuple[str, int]]`; registry entry `"by-region"`.
- **Tests:** `tests/test_by_region.py` (keep, S6): highest revenue first. Command: `anvil run --scope targeted -- python3 -m unittest tests.test_by_region`.
- **Steps:** 1. Write `run`. 2. Register it in `tally/registry.py`. 3. Write the test and run it.

## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `tests/test_filters.py` | keep | S1, S2, S5 | Reports showing orders outside the filter | T1 |
| `tests/test_cli.py` | keep | S1, S2, S5 | The flags not reaching the reports | T2 |
| `tests/test_weekly.py` | keep | S3 | Weekly totals | T3 |
| `tests/test_by_product.py` | keep | S4 | Product ranking | T4 |
| `tests/test_by_region.py` | keep | S6 | Region ranking | T5 |
| smoke: `python3 -m tally weekly --region north --since 2026-11-01` prints rows | smoke | S1, S2, S3 | The whole filtered-report path | T2 |

- Full suite: `python3 -m unittest discover -s tests`, about 1 second.
- Type-check: none.

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | waves 0–1 (T1, T2, T3, T4, T5) | `feat(tally): report filters and three new reports` | no |

## Execution

Not written yet.

Checkpoints: none.
