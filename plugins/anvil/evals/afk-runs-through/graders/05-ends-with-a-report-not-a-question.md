---
type: llm
weight: 2
---

PASS if the final message is a hand-back report that asks Saad nothing and waits on nothing: it says what shipped (the --top option) and its state, quotes real verification output (a test summary line), and lists the decisions made for him or points to the decision log in progress.md.
FAIL if the final message asks Saad a question, asks for approval or a choice before continuing, stops at the plan or spec without building, or claims the tests pass without any output.
