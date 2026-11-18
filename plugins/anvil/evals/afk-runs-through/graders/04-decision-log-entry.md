---
type: regex
pattern: '^- \d{4}-\d{2}-\d{2} \*\*[^*]+\*\* (—|–|--?) .+Confidence: (high|medium|low)\..*Changes if: '
flags: m
target: { source: file, path: docs/top-n/progress.md }
---
