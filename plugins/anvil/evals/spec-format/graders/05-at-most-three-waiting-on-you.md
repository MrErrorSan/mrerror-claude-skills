---
type: llm
focus: { source: file, path: docs/csv-export/spec.md }
weight: 1
---

PASS if the spec's "Waiting on you" section holds at most three questions, each with a recommended answer, or says there are none (an absent section also passes). Questions are counted as separate items, wherever they are numbered.
FAIL if it holds four or more questions, or any question has no recommended answer.
