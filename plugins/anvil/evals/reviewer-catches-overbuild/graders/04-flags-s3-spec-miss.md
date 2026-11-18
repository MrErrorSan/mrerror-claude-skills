---
type: llm
weight: 2
---

S3 says an empty invoice list still writes the file, holding only the header row. T2's `write_csv` returns 0 early on an empty list, so no file and no header are written, and no test covers the empty case, although the implementer's report claims S3 is met.

PASS if the final message reports S3 as not met (missing or misunderstood) because the empty case writes nothing.
FAIL if it says S3 is met or doesn't mention the empty-list case.
