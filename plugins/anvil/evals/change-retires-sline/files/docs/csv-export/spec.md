# CSV export: spec

- **Status:** draft
- **Approved:** 2026-11-16 by Saad ("approved, go with the recommendations")
- **Mode:** normal
- **Size:** full
- **Created:** 2026-11-16

## Waiting on you

None.

## Spec lines

- **S1** `python3 -m ledger export --csv <path>` writes every invoice to `<path>`, oldest first.
- **S2** The first row is a header naming the columns id, customer, total, issued.
- **S3** Columns are separated by commas, and a field containing a comma is quoted.
- **S4** Totals are written in currency units with two decimals (`12.50`), issued dates as ISO dates.
- **S5** After writing, `export` prints `Wrote <n> invoices to <path>`.

## Goals

The accountant opens the export in a spreadsheet without cleaning it up.

- **Constraints:** Python 3.10+, standard library only.

## Shared surface

- `ledger/export.py`: `write_csv(invoices: list[Invoice], path: Path) -> int` (rows written).

## Decisions

- **Comma-separated, quoted with the csv module** (S3). Decided by Saad, 2026-11-16: "plain CSV, commas". Alternative not taken: tabs.
- **Oldest first** (S1). Claude's call: matches `ledger list`.

## Left to the builder

Nothing.

## Change log

- 2026-11-16 Created.
