---
type: regex
pattern: '^- \[x\] T2\b'
flags: m
match: not_contains
target: { source: file, path: docs/csv-export/progress.md }
---
