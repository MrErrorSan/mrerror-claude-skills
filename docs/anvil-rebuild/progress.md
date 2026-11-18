# Progress: anvil-rebuild
- **Stage:** build
- **Wave:** 2 of 4
## Tasks
- [x] T1 Foundations (formats, CLI skeleton, parser, state) C1
- [x] T2 Gates and AFK C1
- [x] T3 Parallel-safe check and lane check C1
- [x] T4 Result reuse C1
- [x] T6 Stale detection and progress C1
- [ ] T5 Hooks
- [ ] T7 anvil router and brainstorm skills
- [ ] T8 plan skill
- [ ] T9 build skill
- [ ] T10 verify and finish skills
- [ ] T11 debug skill
- [ ] T12 afk revision and ticket-update hook-in
- [ ] T13 Packaging and skill lint
- [ ] T14 Evals
- [ ] T16 Upstream watch and provenance
- [ ] T15 Integration and final verification (orchestrator)
## Commit points
- C1 (waves 0-1) squashed onto anvil-rebuild; sha recorded after push
## Blockers
## Decision log
<!-- newest first; each: - 2026-11-18 **<choice>** — <reason>. Confidence: high|medium|low. Changes if: <fact>. -->
- 2026-11-18 **Wave 1 verified: 35 tests green on the merged tree (`unittest discover`, ~40 s) plus an end-to-end CLI smoke from a subdirectory** — the smoke covered gate order, quote-after-present, stale, plan-check overlap, run/fresh reuse and invalidation, and progress. Confidence: high.
- 2026-11-18 **The suite takes ~40 s, not the plan's "under 10 s"** — each `tree_key` and `state_dir` spawns git (~0.1-0.35 s on Windows). Still well under the design's ~2 min per-wave threshold, so it runs per wave. Confidence: high. Changes if: it passes ~2 min.
- 2026-11-18 **T5 adds a guard: PreToolUse denies an Edit/Write that sets the topic's spec or plan `Approved:` line to anything but `no`** — the T2 review found that `check` reads only the header, so a hand-written header would pass a stop. Only `anvil approve` may write it. Confidence: medium. Changes if: the guard blocks legitimate edits (e.g. the change flow-back).
- 2026-11-18 **`results.jsonl` records gain `tree` and `prefix`; `result_key` includes the cwd prefix** — the T4 review found a green `npm test` in one package would be reused for another; `stale` needs the bare tree key to detect results that no longer match. Pinned in `references/formats.md`. Confidence: high.
- 2026-11-18 **Gate hardening from the T2 review: `--pre` needs 3+ words; `afk on` reads only the last logged message (design §7.2); `present plan` is refused until the spec stage passes; `approve --afk` records the quote that turned AFK on** — each closed a path where the model could pass a stop on words not meant for it. Confidence: high.
- 2026-11-18 **A quote under 3 words is accepted only when it is Saad's whole message, sent after `present`** — so "yes" works as a normal approval (this plan's own was "1 yes"); fragments and pre-approvals still need 3+ words. Confidence: medium. Changes if: Saad wants a stricter rule.
- 2026-11-18 **This plan's own task table fails `plan-check` (Spec cells hold `§` refs; Depends holds "T7–T12")** — it predates the pinned format. Expected; T15 notes it rather than rewriting an approved plan. Confidence: high.
- 2026-11-18 **T1 review runs alongside wave 1** — wave 1 consumes only T1's pinned interfaces; review fixes stay inside T1's files, so the write sets stay disjoint. Confidence: medium. Changes if: the review finds an interface defect, in which case affected lanes get a fix task.
- 2026-11-18 **`approve --pre` accepts a verbatim quote from any logged prompt, not only prompts since `topic start`** — `active.json` is pinned without a start time, and the original request (the main pre-approval case in design §7.2) is logged before `topic start` runs. The verbatim-quote check still blocks invented quotes. Confidence: medium. Changes if: Saad wants pre-approvals scoped to the current topic.
- 2026-11-18 **Hooks call `bash` explicitly (as `run-hook.cmd` does), not via `#!/usr/bin/env bash`** — T1 saw the WSL `bash.exe` launcher picked up from WindowsApps on PATH. Confidence: high. Changes if: none expected.
- 2026-11-18 **`.gitignore` gains `__pycache__/` and `*.pyc`** — test runs produced bytecode that `git add` picked up. Confidence: high.
- 2026-11-18 **Tests run via `unittest discover -s tests -t . -p <file>`, not `-m unittest tests.anvil_cli.<mod>`** — `-I` does not put the cwd on `sys.path`, so the plan's per-module command fails to import. Confidence: high. Changes if: tests stop running under `-I`.
- 2026-11-18 **The `bin/anvil` wrappers put `bin/` on `sys.path` themselves (e.g. via `-c` bootstrap) instead of setting `PYTHONPATH`** — `python -I` ignores `PYTHONPATH`, so the plan's wrapper as written cannot import `anvil_cli`. Confidence: high. Changes if: the wrappers drop `-I`.
- 2026-11-18 **Lane worktrees at `../anvil-lane-<task>`, created by the orchestrator** — as the plan states; wave 0 (T1 alone) runs in the main checkout on the work branch. Confidence: high. Changes if: a wave-0 lane needs isolation.
## Stop note
