# Progress: anvil-rebuild
- **Stage:** build
- **Wave:** 4 of 4
## Tasks
- [x] T1 Foundations (formats, CLI skeleton, parser, state) C1
- [x] T2 Gates and AFK C1
- [x] T3 Parallel-safe check and lane check C1
- [x] T4 Result reuse C1
- [x] T6 Stale detection and progress C1
- [x] T5 Hooks C2
- [x] T7 anvil router and brainstorm skills C2
- [x] T8 plan skill C2
- [x] T9 build skill C2
- [x] T10 verify and finish skills C3
- [x] T11 debug skill C3
- [x] T12 afk revision and ticket-update hook-in C3
- [ ] T13 Packaging and skill lint
- [ ] T14 Evals
- [ ] T16 Upstream watch and provenance
- [ ] T15 Integration and final verification (orchestrator)
## Commit points
- C1 04a8360 pushed 2026-11-18
- C2 7f7d574 pushed 2026-11-18
## Blockers
## Decision log
<!-- newest first; each: - 2026-11-18 **<choice>** — <reason>. Confidence: high|medium|low. Changes if: <fact>. -->
- 2026-11-18 **No separate wave-3 semantic review** — the T10 reviewer traced build ↔ verify ↔ finish hand-offs, and the T11/T12 reviewers checked against `hooks.py`/`gate.py`; the whole-branch final review (T15) and T13's skill lint cover the rest. Confidence: medium. Changes if: the final review finds wave-3 drift.
- 2026-11-18 **Wave-3 lanes were cherry-picked, not merged** — they were cut before C2, and the work branch was reset onto the C2 squash, so a merge conflicted on every wave-2 file. Cherry-picking the six lane commits applied cleanly. The lesson is now in `references/git-flow.md` and `build/references/waves.md`. Confidence: high.
- 2026-11-18 **The last commit point is recorded as `- C<k> (this commit) <date>` before its own squash; in AFK, verify lands it** — keeps one squashed commit per commit point (design §7.6) and keeps AFK pushes flowing, since `finish` can't be model-invoked. Confidence: medium. Changes if: Saad prefers finish to always land the last commit point.
- 2026-11-18 **`afk on` records the Stop-note baseline; session-start states AFK; `repro` tests warn like `keep`; `docs/research/` is never held** — from the wave-2 and T12 reviews. Confidence: high.
- 2026-11-18 **C2 landed before the wave-2 cross-skill fixes** — wave 2's per-task reviews were clean and pushing it protected the work; the cross-skill fixes travel in C3. Confidence: high.
- 2026-11-18 **Wave 3 started before C2 landed** — T10-T12 depend only on T1/T2; their write sets don't touch wave 2's, and C2 squashes before any wave-3 lane merges. Confidence: high.
- 2026-11-18 **Wave 2 verified: 44 tests green on the merged tree; hook smokes pass (session-start JSON, empty-PATH pre-tool-use → `{}` exit 0, `.cmd` route exit 0); hook scripts LF in the index; skills within budget, no forbidden words, only pinned CLI subcommands** — plus per-task reviews and a wave review for cross-skill drift. Confidence: high.
- 2026-11-18 **The active topic's `progress.md` is left out of the result tree key and ignored by `lane-check`** — T9 found every progress edit made recorded results stale (no reuse at commit points), and sequential lanes got the orchestrator's own progress file flagged. Confidence: high. Changes if: a project keeps code-relevant data in progress.md (not expected).
- 2026-11-18 **`topic start` on the same slug keeps the stored folder unless `--dir` is given** — the T7 review found a size step-up dropped a project-rule `--dir`. Confidence: high.
- 2026-11-18 **The PreToolUse gate does not hold Agent dispatch; it holds Edit/Write inside the repo but outside the topic folder** — brainstorm needs subagents in the spec stage (lookups, builder check, mock variants), and PreToolUse fires inside subagents too (hooks docs), so the edit hold still stops an early build. Writes outside the repo (scratchpad, memory) are never held. Confidence: high. Changes if: evals show builds starting early through Bash writes.
- 2026-11-18 **skill-creator's `quick_validate.py` failing only on `disable-model-invocation` / `user-invocable` is accepted** — the validator's allowlist predates those Claude Code frontmatter keys, and the plan requires `disable-model-invocation` on `finish`. Every other validator failure is fixed. Confidence: high. Changes if: skill-creator adds the keys.
- 2026-11-18 **Added `anvil topic stage <stage>` (plan and build gated by `check`)** — the skills need to move a topic between stages and the pinned CLI had no command for it. Documented in `references/formats.md`; stage hand-offs pinned in the skill-lane brief. Confidence: high. Changes if: none expected.
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
