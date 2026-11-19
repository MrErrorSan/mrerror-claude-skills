# Progress: Anvil V2

- **Stage:** measure (the A/B suite `v2` is running)
- **Plan:** [2026-11-19-v2-plan.md](2026-11-19-v2-plan.md)
- **V1 baseline:** tag `anvil-v1.0`; results in [../anvil-ab/2026-11-18-ab-results.md](../anvil-ab/2026-11-18-ab-results.md)

## Tasks
- [x] Tag V1 (`anvil-v1.0`) and branch `anvil-v2` from `anvil-rebuild`
- [x] CLI: `approve --amended`, auto-park a topic at `finish`, native paths in `anvil run`/`fresh`, docs not held (74 unit tests green)
- [x] Skills: inline small builds, fewer review rounds, verify lands the work, AFK keeps going, approve-with-edits, calls list, plain reports, line endings, no heredoc edits (lint green)
- [x] Version 2.0.0 and README notes
- [x] Harness fixes found in review: agent turns via stdin, an EOL-rewrite metric, compare plus 4-way judge
- [~] Rerun the 6 c2 Superpowers and no-plugin runs that the harness bug hit
- [~] A/B suite `v2` (arm A, 21 runs), 4-way blind judge, results doc
- [ ] Iterate on any target V2 misses

## Decision log
- 2026-11-19 **Superseded the 6 c2 S/V runs and reran them, instead of keeping them.** Should a harness bug that hurt only two arms stay in the record? Replies starting with `--top` crashed `claude -p` argument parsing in all 6 Superpowers and no-plugin c2 runs and in no Anvil run. Their records sit in `abtest/results/full/superseded/` for audit. Confidence: high. Changes if: you prefer the original numbers. They're kept, so the old report can be regenerated.
- 2026-11-19 **Verify points the work branch at the landed commit (`git branch -f`) instead of deleting it.** Should it delete the work branch? Finish's own rule asks you before deleting a work branch whose synced branch is local-only, so deleting in verify would contradict it (P5). Confidence: high. Changes if: you want verify to delete it.
- 2026-11-19 **Kept `finish` as user-invoked (`disable-model-invocation`), but made it optional.** Should the model be able to run it? Verify now runs finish's landing sections itself. What's left in finish (pushes and merges beyond the plan, a PR, branch deletion) are exactly the choices that should be yours. Confidence: medium. Changes if: you want it fully automatic.
- 2026-11-19 **Inline mode is the default for 3 tasks or fewer in sequence.** Is 3 the right cut-off? The V1 data: all 7 cases were 1–3 tasks, with 7 subagents per topic, and per-task review found little that one end review wouldn't. Plans with 4+ tasks keep the subagent loop. Confidence: medium. Changes if: V2's judge scores on "tests" or "match" drop below V1's.
- 2026-11-19 **A fix that stays inside its findings' lines gets no re-review.** Should every fix be re-reviewed? The orchestrator checks the fix against each finding and reruns the covering tests instead. V1 spent 40–75 s re-reviewing one-token fixes. Confidence: medium. Changes if: V2 ships a regression from an unreviewed fix.
- 2026-11-19 **Approve-with-dictated-edits approves first, then applies the edits.** The alternative was a second stop. This mirrors what stop 1 already did in V1. `approve --amended` covers the case where the edits were made before approving. The quote rule is unchanged: his words, sent after the version he read. Confidence: high. Changes if: you want every edit re-shown.
- 2026-11-19 **Markdown under `docs/` is never held before approval.** Should the hold be narrowed to the files a project rule names? Detecting which docs a project rule requires isn't reliable, and docs aren't code. Code under `docs/` (e.g. `gen.py`) is still held. Confidence: medium. Changes if: something under `docs/` turns out to be build input.
- 2026-11-19 **Didn't add Bash-redirect detection to the edit hold.** Parsing shell writes reliably is hard and would slow every Bash call. The skills now say to edit with Edit or Write only. Confidence: medium. Changes if: V2 runs show Bash writes before approval.
- 2026-11-19 **Kept the "Size:" first line on trivial work.** The judge called it noise. But it's your design rule (the size is stated so you can correct it), and the cost is one line. Confidence: high. Changes if: you drop that rule.
- 2026-11-19 **The V2 A/B rerun is arm A only.** Should Superpowers and no-plugin be rerun too? Their 63 stored runs are the baseline, and only the 6 c2 runs the harness bug hit are redone. That keeps the cost at about 21 runs. Confidence: high. Changes if: Superpowers updates past 7.0.2.
