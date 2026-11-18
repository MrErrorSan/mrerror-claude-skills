---
type: llm
focus: trace
weight: 1
---

PASS if the first text Claude writes to the user states a size from Anvil's three (trivial, direct or full; here full or direct is expected) with a short reason, for example "Size: full. A new feature with open questions."
FAIL if no size line is stated near the start, or the session follows a different process (a design document under docs/designs/, or "one question at a time") instead of Anvil's.
