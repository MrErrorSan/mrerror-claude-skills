# Upstream decisions ledger

This ledger is append-only. It holds every Superpowers change or part that has been considered, with its verdict, the reason and the date.
- Add new rows at the bottom. Never edit or delete a row.
- To reverse a decision, add a new row that names the earlier one, with the new evidence.
- A rejection recorded here isn't reopened without new evidence (README, step 2).

**Verdicts:**
- At 7.0.2 (the initial sync), each part was given one of these:
  - **keep:** copied, with light edits for names and paths;
  - **rewrite:** the idea is kept and the rule is changed;
  - **drop:** not in Anvil.
- From the first release review on, a verdict is **adopt**, **adapt**, **reject**, **ignore** or **candidate (Saad)**. It also carries the rubric category (A–G) in the reason.

**Reasons** cite a principle (`P<n>` in [docs/anvil-principles.md](../../docs/anvil-principles.md)), a design section (`§n`), or evidence.

The 7.0.2 rows are seeded from the stage-mapping table in [the inventory](../../docs/anvil-rebuild/research/2026-11-18-superpowers-inventory.md) (§6). Where the build ended up differing from the inventory's verdict, the row records what was actually done, and the reason says so.

| Date | Version | Superpowers part | Verdict | Reason | Anvil files |
|---|---|---|---|---|---|
| 2026-11-18 | 7.0.2 | `hooks/hooks.json`, `hooks/run-hook.cmd`, `hooks/session-start` | keep | Anvil needs its own startup hook. The polyglot wrapper works on Windows and Git Bash (P1, §5, §7.13). `run-hook.cmd` was kept with only its comments changed. The hook scripts kept only the `$0` split, and call `bin/anvil` instead. | `plugins/anvil/hooks/*`, `plugins/anvil/bin/anvil` |
| 2026-11-18 | 7.0.2 | `skills/using-superpowers/SKILL.md` | rewrite | Only the structure (one router) was kept. The 1% rule, the caps, the always-brainstorm rule and the todo-per-item rule were dropped: forceful wording, and the todo tools are gone (P4, §4, §5). | `plugins/anvil/skills/anvil/SKILL.md` |
| 2026-11-18 | 7.0.2 | `skills/brainstorming/SKILL.md`: the opening check, Look Before You Ask, proposal over question, approaches, ground to cover, split projects | rewrite | One batched question round with recommended answers. Variations when information is thin. Decisions go into the spec (P8, P9, P20, §7.3). The spike section and the router-owned sizing were dropped. | `plugins/anvil/skills/brainstorm/SKILL.md` |
| 2026-11-18 | 7.0.2 | `skills/brainstorming/visual-companion.md`, `skills/brainstorming/scripts/*` | drop | The global constraints exclude the companion and its telemetry (§5). Mocks are `ui-mockup`'s job, as local files. The inventory had this as "rewrite or optional". | none |
| 2026-11-18 | 7.0.2 | `skills/dispatching-parallel-agents/SKILL.md` | keep (merged) | Parallel research and parallel lanes (P33, P35, §7.6). | `plugins/anvil/skills/build/SKILL.md`, `plugins/anvil/skills/build/references/waves.md`, `plugins/anvil/skills/build/prompts/implementer.md` |
| 2026-11-18 | 7.0.2 | The Written Design outline and the "calls marked as yours" rule | keep and extend | Adds S-lines, header lines, shared surface, replaces/stays and a change log (P9, P22, §7.4). | `plugins/anvil/skills/brainstorm/references/spec-template.md` |
| 2026-11-18 | 7.0.2 | `skills/brainstorming/builder-check-prompt.md`, plus the three-pile triage | keep | The builder check is what worked (§2 "what worked", §7.4). Adds shared-surface and S-line checks. | `plugins/anvil/skills/brainstorm/prompts/builder-check.md` |
| 2026-11-18 | 7.0.2 | Brainstorming's HARD-GATE | rewrite | It becomes the spec stop, enforced by `anvil approve` and skippable in AFK (P21, P26, §7.2). | `plugins/anvil/skills/brainstorm/SKILL.md` |
| 2026-11-18 | 7.0.2 | `skills/writing-plans/SKILL.md`: the spec pointer, Global Constraints, Interfaces, Review Focus, right-sizing, the step recipe, self-review | keep | Contracts pinned before splitting work (§2 "what worked", §7.5). | `plugins/anvil/skills/plan/SKILL.md`, `plugins/anvil/skills/plan/references/plan-template.md` |
| 2026-11-18 | 7.0.2 | The writing-plans execution handoff (SDD vs inline) | rewrite | It becomes the plan's execution mode: parallel waves or a single agent, proposed with numbers and approved at stop 2 (P24, P36, §7.5). | `plugins/anvil/skills/plan/SKILL.md` |
| 2026-11-18 | 7.0.2 | The writing-plans TDD step template and per-step "Commit" | rewrite | Replaced by the test strategy (keep / scaffold / smoke / repro, each naming its S-line) and by commit points (P10, P16, P17, §7.5). | `plugins/anvil/skills/plan/SKILL.md`, `plugins/anvil/references/test-policy.md`, `plugins/anvil/references/git-flow.md` |
| 2026-11-18 | 7.0.2 | SDD: the dispatch recipe, brief and report files, status contract, model selection, no sub-dispatch, batching, pre-flight, "Rulings, not stalls", the four stops | keep | §7.6. The ledger and `.superpowers/` paths became `progress.md` and the topic folder (P12). | `plugins/anvil/skills/build/SKILL.md`, `plugins/anvil/skills/build/references/*.md` |
| 2026-11-18 | 7.0.2 | SDD "never parallel implementers" | rewrite | Parallel waves of parallel-safe tasks, each task still reviewed (P33, P35, P36, §7.6). | `plugins/anvil/skills/build/SKILL.md`, `plugins/anvil/skills/build/references/waves.md` |
| 2026-11-18 | 7.0.2 | `skills/executing-plans/SKILL.md` | rewrite | It becomes the single-agent mode. Mandatory TDD dropped, and the per-task check kept (P10, §7.6). | `plugins/anvil/skills/build/SKILL.md` |
| 2026-11-18 | 7.0.2 | `skills/executing-plans/scripts/{task-start, task-done}`, `skills/subagent-driven-development/scripts/*` | drop | Replaced by `progress.md` and `bin/anvil` (P12, §7.6, §7.9). | none |
| 2026-11-18 | 7.0.2 | `skills/subagent-driven-development/implementer-prompt.md` | rewrite | Keeps escalation and self-review. Drops "full suite before committing" and TDD by default. Reports "test changed or code changed, and why" (P11, P18, P34, §7.6, §7.14). | `plugins/anvil/skills/build/prompts/implementer.md` |
| 2026-11-18 | 7.0.2 | `skills/test-driven-development/SKILL.md` (the Iron Law) | drop | TDD is slow and stalls unattended work. Test-first survives only for bug repros (P10, §7.14). | `plugins/anvil/references/test-policy.md` (replacement) |
| 2026-11-18 | 7.0.2 | `skills/test-driven-development/writing-good-tests.md` | drop | The inventory said "keep", but it wasn't copied: `test-policy.md` covers test quality through the test types and the "names its S-line and what breaks" rule (P16, P17, §7.5, §7.14). | none |
| 2026-11-18 | 7.0.2 | `skills/systematic-debugging/SKILL.md`, plus its references and `find-polluter.sh` | keep | Systematic debugging is what worked (§2). Phase 4 now points at Anvil's test rules. The Iron Law wording was removed. | `plugins/anvil/skills/debug/**` |
| 2026-11-18 | 7.0.2 | `skills/using-git-worktrees/SKILL.md` | drop | The inventory said "rewrite (optional)". The orchestrator creates lane worktrees itself, with no consent or baseline-suite stops (P27, §7.6). | none |
| 2026-11-18 | 7.0.2 | `skills/subagent-driven-development/task-reviewer-prompt.md` | keep and extend | The per-task spec review was the biggest loss (§2 evidence). It checks against S-lines and never reruns tests (P11, §7.6). | `plugins/anvil/skills/build/prompts/task-reviewer.md`, `plugins/anvil/skills/build/prompts/wave-review.md` |
| 2026-11-18 | 7.0.2 | `re-review-prompt.md`, `references/fix-loop.md`, `references/cannot-verify.md`, `references/handling-reports.md`, `references/resuming.md` | keep | §7.6. Re-review gains a WITHDRAWN verdict. | `plugins/anvil/skills/build/prompts/re-review.md`, `plugins/anvil/skills/build/references/receiving-review.md`, `plugins/anvil/skills/build/references/resuming.md`, `plugins/anvil/skills/build/SKILL.md` |
| 2026-11-18 | 7.0.2 | `references/final-review.md`, plus `requesting-code-review/code-reviewer.md` | keep | The vision-document clause, "Declined to judge" and "Rulings I made" (P28, §7.6). | `plugins/anvil/skills/build/prompts/final-review.md`, `plugins/anvil/skills/verify/SKILL.md` |
| 2026-11-18 | 7.0.2 | `skills/verification-before-completion/SKILL.md` | rewrite | Evidence before claims and the line-by-line requirements check are kept. It's sized to the change, run once by the main agent, and reuses fresh results (P11, P34, §7.7). | `plugins/anvil/skills/verify/SKILL.md` |
| 2026-11-18 | 7.0.2 | `skills/receiving-code-review/SKILL.md` | rewrite (merged) | Merged into review triage. The pushback rules are kept (§2 evidence, §7.6). | `plugins/anvil/skills/build/references/receiving-review.md`, `plugins/anvil/skills/build/prompts/implementer.md` |
| 2026-11-18 | 7.0.2 | `skills/requesting-code-review/SKILL.md` | drop | Its template lives on in final review and verify. Its `HEAD~1` example is a known bug. | none |
| 2026-11-18 | 7.0.2 | `skills/finishing-a-development-branch/SKILL.md` | rewrite | Keeps the safety rules: base confirmation, typed `discard`, never `--force` a worktree removal. Fresh results replace the rerun. Adds the commit-point policy, ticket-update and the report order (P11, §7.8). | `plugins/anvil/skills/finish/SKILL.md` |
| 2026-11-18 | 7.0.2 | SDD workspace deletion | rewrite | `progress.md` and the decision log stay in the topic folder. Only lane briefs, reports and worktrees are cleaned up (P12, P26, §7.8). | `plugins/anvil/skills/finish/SKILL.md`, `plugins/anvil/references/git-flow.md` |
| 2026-11-18 | 7.0.2 | `skills/writing-skills/**` | drop | Outside the workflow. Anvil skills are written with Anthropic's `skill-creator` (§8.3, Saad's requirement; notes §11). | none |
| 2026-11-18 | 7.0.2 | `skills/diagnosing-superpowers/**` | drop | Outside the workflow (notes §11). | none |
| 2026-11-18 | 7.0.2 | `skills/using-superpowers/references/*-tools.md`, other-harness folders, `hooks/hooks-cursor.json`, `GEMINI.md`, `AGENTS.md`, `gemini-extension.json`, `index.js` | drop | Anvil targets Claude Code (rubric G). | none |
| 2026-11-18 | 7.0.2 | `skills/using-superpowers/references/claude-code-tools.md` ("orchestrator one layer down") | drop | The inventory had this as "keep as an option". It wasn't taken in 1.0: the build orchestrator is the main session. It can be reconsidered for long plans. | none |
| 2026-11-18 | 7.0.2 | `assets/` (logos) | drop | No Superpowers branding (§5). | none |
| 2026-11-18 | 7.0.2 | `LICENSE` | keep | MIT requires the notice to ship with substantial portions (§5). | `plugins/anvil/NOTICE` |
