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
- **S2** The first row is a header naming the columns id, customer, total, issued; columns are comma-separated, and a field containing a comma is quoted.
- **S3** An empty invoice list still writes the file, holding only the header row.
- **S4** Totals are written in currency units with two decimals (`12.50`), issued dates as ISO dates.

## Goals

The accountant opens the export in a spreadsheet without cleaning it up.

- **Constraints:** Python 3.10+, standard library only.

## Shared surface

- `ledger/export.py`: `HEADER`, and `write_csv(invoices: list[Invoice], path: Path) -> int` (rows written, header not counted).

## Decisions

- **The standard csv module does the quoting** (S2). Claude's call: it already handles commas and quote characters.
- **An empty export still has its header** (S3). Decided by Saad, 2026-11-16: the accountant's import template needs the header row to map columns.

## Left to the builder

Nothing.

## Change log

- 2026-11-16 Created.
