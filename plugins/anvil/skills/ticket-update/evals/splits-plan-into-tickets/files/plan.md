# Classifier export — plan (approved 2026-11-18)

Spec: docs/export/design.md

1. Export schema: define `ExportRecord` and its JSON schema (design.md §2). ~1 day.
2. CSV writer: `classifier export --format csv` writing ExportRecords, streaming, UTF-8 BOM optional flag `--bom` (design.md §3.1). ~2 days.
3. Parquet writer: `--format parquet` using pyarrow, same records (design.md §3.2). ~2 days. Can be done in parallel with CSV once the schema exists.
4. S3 upload + resumable multipart for files > 100 MB, retry with backoff, `--dest s3://...` (design.md §4). This is the big one, ~5 days.
5. Docs + CLI help text (design.md §5). ~1 day, after 2-4.

Out of scope for this plan: scheduled exports (next quarter), a UI button.
Gates: `make check` and `make test`.
