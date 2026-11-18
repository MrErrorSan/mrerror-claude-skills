---
type: llm
weight: 2
---

The repo already answers these: notes are stored in SQLite (notes/store.py); the API is the Python standard library http.server (notes/api.py); the notes list already takes filters as query parameters (GET /notes?archived=1); notes are private to their owner, with no sharing (docs/decisions.md); tests use unittest.

PASS if the final message asks Saad none of these things (it may state them as findings).
FAIL if any question to Saad asks which database or storage is used, which web framework, how list filters are passed, whether other users can see a note, or which test framework to use.
