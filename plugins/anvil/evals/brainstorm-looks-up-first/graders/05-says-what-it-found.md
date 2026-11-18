---
type: llm
weight: 1
---

PASS if, before its questions, the final message restates the request in two or three lines and says what it looked up, naming at least one fixture file or fact it found (for example notes/store.py, the ?archived=1 filter, or the private-notes decision).
FAIL if it goes straight to questions with no restatement, or never mentions anything it found in the repo.
