# Report filters: spec

- **Status:** draft
- **Approved:** 2026-11-16 by Saad ("spec looks right, approved")
- **Mode:** normal
- **Size:** full
- **Created:** 2026-11-16

## Waiting on you

None.

## Spec lines

- **S1** `--region <name>` limits every report to orders from that region.
- **S2** `--since <YYYY-MM-DD>` limits every report to orders on or after that date.
- **S3** A `weekly` report prints revenue per ISO week (`2026-W45`), oldest first.
- **S4** A `by-product` report prints revenue per product, highest first.
- **S5** Filters are applied before a report runs, so a new report gets them without code of its own.
- **S6** A `by-region` report prints revenue per region, highest first.

## Goals

Saad wants to answer "how did the north region do since the 1st" without a spreadsheet.

- **Constraints:** Python 3.10+, standard library only. Output format of `daily` stays as it is.

## Shared surface

- `tally/filters.py`: `apply(orders, region: str | None, since: date | None) -> list[Order]`.
- `tally/registry.py`: `REPORTS` maps a report name to `run(orders) -> list[tuple[str, int]]`. Every new report adds one entry.

## Decisions

- **Filters live in one function the CLI calls before the report** (S5). Decided by Saad, 2026-11-16. Alternative not taken: a filter argument on each report.
- **Week labels use ISO weeks** (S3). Claude's call: matches `date.isocalendar()`, no extra code.

## Left to the builder

Column widths in the printed output.

## Change log

- 2026-11-16 Created.
