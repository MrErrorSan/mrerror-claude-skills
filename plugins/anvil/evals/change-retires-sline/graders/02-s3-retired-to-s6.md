---
type: regex
pattern: '^- ~~\*\*S3\*\* .+~~ RETIRED → S6(, S7)* \(\d{4}-\d{2}-\d{2}, CR: '
flags: m
target: { source: file, path: docs/csv-export/spec.md }
---
