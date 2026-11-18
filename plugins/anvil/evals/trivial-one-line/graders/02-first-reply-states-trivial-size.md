---
type: llm
focus: trace
weight: 1
---

PASS if the first text Claude writes to the user in the session (before or alongside its first edit) states the size as trivial, for example "Size: trivial", together with a short reason.
FAIL if no size is stated, the size is stated only at the end, or the size given is direct or full.
