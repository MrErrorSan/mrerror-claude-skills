---
type: llm
focus: { source: file, path: docs/report-filters/plan.md }
weight: 2
---

The draft plan had T3, T4 and T5 in wave 1, all writing `tally/registry.py`.

PASS if the plan's "## Execution" section names that write-set overlap and does one of these: (a) the task table no longer has two tasks in the same wave writing `tally/registry.py` (for example the registry entries moved into T1, or the tasks moved to separate waves) and the section says plan-check was rerun clean; or (b) the mode is sequential and the overlap is given as the reason.
FAIL if the section proposes parallel lanes while two tasks in the same wave still write `tally/registry.py`, if the overlap is not mentioned, or if the section still reads "Not written yet".
