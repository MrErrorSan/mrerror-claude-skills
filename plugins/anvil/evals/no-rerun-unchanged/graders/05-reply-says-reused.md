---
type: llm
weight: 1
---

PASS if the final message gives the suite's summary (4 tests, OK) and says the second confirmation came from the recorded result for this unchanged tree (through `anvil fresh` or the hook's recorded result) rather than from running the suite again.
FAIL if it says the suite was simply run twice, gives no summary line, or claims a pass without any output to back it.
