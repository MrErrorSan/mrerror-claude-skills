---
type: llm
weight: 2
---

PASS if the final message to Saad does all of these: calls the change a change request (it replaces S3, the comma rule he decided on 2026-11-16), not a new feature; says S3 is retired and replaced by a new S-line (S6); and quotes or closely reproduces the `anvil stale` output, which names task T1 and the test `tests/test_export.py` as pointing at the retired S3.
FAIL if the change is called a new feature, the retired and new S-line numbers are missing, no `anvil stale` output appears, or the message only asks Saad whether to proceed without having made the documented change.
