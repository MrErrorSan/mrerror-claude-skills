# Anvil 1.0: design

- **Date:** 2026-11-18
- **Status:** draft for Saad's review. The builder check is done (2026-11-18); its questions are answered here.
- **Branch:** `anvil-rebuild`
- **Inputs:**
  - [brainstorm notes](2026-11-18-brainstorm-notes.md): the conversation record. Labels there mark what Saad said or decided and what Claude proposed.
  - [research/](research/): nine reports dated 2026-11-18.

This document says **what** gets built and **why**. The plan that follows says how, file by file.

Labels used below:
- **Claude's call** marks a decision Claude made that Saad hasn't explicitly confirmed. Those calls are also listed in §12 for review.
- **Saad's decision** marks a decision Saad made.

---

## 1. Intent

Anvil is **Saad's own take on Superpowers: how he wants Claude Code to do development work.** It stops being an override layer on top of Superpowers and becomes the workflow itself.

It contains everything the workflow depends on, even where that repeats Superpowers or another skill. Saad doesn't maintain those, they change underneath him, and his flow must stay **consistent and predictable.**

### Why the current setup fails

The detailed evidence is in notes §2 and the research reports.

1. **Two instruction sets contradict each other.** Anvil overrules Superpowers rule by rule.
   - Three of those overrides argue with Superpowers behavior that no longer exists: full-code plans, checkpoints between tasks, and reviewers rerunning tests. ([inventory](research/2026-11-18-superpowers-inventory.md))
   - Every session, the model weighs both sets and ends up half-following each.
2. **The per-task check against the spec was lost.**
   - Anvil's "verify" means "the commands pass", never "we built what was asked". The cycle that follows is: rebuild, checks pass, the same complaint comes back. That cycle is the déjà vu.
   - In 9 build sessions, the per-task review ran properly in 2.
3. **Changes don't flow back.** The plan says A, the code says A1, and the reviews disagree. Superpowers deletes its own ruling log at the end and never updates the spec or the plan.
4. **Time is wasted on repeats, not on verification itself.**
   - A slow suite runs 7 to 10 times per 3-task plan, 3 to 6 of them on unchanged code. ([test-run reuse](research/2026-11-18-test-run-reuse.md))
   - Tasks also run one at a time even when they're independent.
5. **The model can't be seen working.** There were about 30 "done?" messages across the sessions. The todo tools Superpowers relies on were removed from Claude Code on 2026-08-14.
6. **Decisions are hidden.** Decisions get made silently, with no pushback when requirements change.
7. **Tests:** suites of thousands of tests, nobody knows why each exists, and a failure gets fixed by editing either the test or the code without saying which.
8. **Over-building.** On redesigns there's also the opposite problem: anchoring on old code, caused by Anvil's "preserve and reuse" framing. ([simple-code rules](research/2026-11-18-simple-code-rules.md))
9. **The repo version has never run.** Every session loaded an old React-specific copy from `~/.claude/skills`.

## 2. Goals

1. **One predictable flow:** brainstorm → spec → **stop** → plan → **stop** → build and verify → finish.
   - The same request gets the same workflow every time.
2. **Faster than Superpowers, without losing correctness.** There are two levers:
   - test results stay valid until the code changes;
   - parallel build in waves of up to 3 or 4 isolated agents, where the plan shows the work splits.
   - The realistic target is about 1.5 to 2.5 times faster on a feature that splits well, plus the time saved on test runs. ([parallel build](research/2026-11-18-parallel-build.md))
3. **The spec and plan always match the code.** A change mid-build updates them, and anything that relied on the old version is flagged.
4. **"Did we build what was asked" is checked twice:**
   - per task, against the spec lines the task covers;
   - at the end, against every live spec line.
5. **Progress can be seen at any time** in one file.
6. **Every decision can be seen,** with its reason.
7. **Tests guard the core and say why they exist.** Scaffold tests used only during the build are deleted before finishing.
8. **Code is simple and clean.**
9. **Variations instead of interrogation** when Saad doesn't have the full picture yet: researched options and mocks he can react to.
10. **The other skills work as one system:** tickets, mocks, UX audit, cross-model review and AFK.
11. **It's maintainable:**
    - an eval suite, rerun when models change;
    - a watch on Superpowers releases;
    - releases that actually reach Saad's other machine.

## 3. Non-goals

- Not a general-purpose public framework. It's personal and opinionated, and Saad's preferences win.
- Not a replacement for Superpowers' `writing-skills` or `diagnosing-superpowers`. Those stay usable from Superpowers.
- No support for agent tools other than Claude Code (Gemini CLI, Codex and so on).
- No external task database or MCP server. Plain markdown files only.
- The stand-up skill is a separate design (`docs/superpowers/specs/2026-11-18-standup-design.md`). It's out of scope here.

## 4. Anti-goals: failure even if it technically works

- **Ceremony on a one-line change.** Plans, subagents and three test runs for a wording fix.
- **Bloat.** Collecting every good idea makes a skill too long for the model to follow, and it gets cut off after compaction.
- **Forceful wording** (MUST, IMPORTANT, ALL-CAPS). Current models over-apply it.
- **Self-approval.** The model must never pass a stop on its own say-so. Every approval has to trace back to words Saad actually typed.
  - **Saad's pre-approvals are respected.** Examples: "approve the spec yourself", "go straight to the build", or "AFK" in the original request. A stop pre-approved this way is passed, and that stage runs with **AFK decision-making**: each choice is made on Saad's behalf and logged with its reason and confidence. **Saad's decision.**
- **A parallel build that's slower end to end** once reconciling and fixing is counted, or one that silently damages lockfiles or migrations.
- **Silent decisions,** or decisions buried in a log nobody reads.
- **Asking questions the repo could answer.**
- **Repeating today's bug.** A rebuild that passes its own evals while the flow in real sessions differs from session to session.

## 5. Constraints

- **Claude Code.**
  - The machine has 2.1.268. Plugin evals need ≥ 2.1.269 and `/doctor prompt-audit` needs ≥ 2.1.283, so **update before the eval phase.**
  - The todo tools are not available.
- **Platforms.** Windows 11 with Git Bash is primary; Linux and macOS are secondary. Hooks need the same Windows wrapper Superpowers uses (`run-hook.cmd`).
- **Size.** Each `SKILL.md` stays under about 20k characters, because longer files get cut off after compaction. Detail goes into `references/`.
- **Wording.** Plain statements. Startup hook text is phrased as facts, not commands, so it doesn't trip prompt-injection defences. ([Anthropic guidance](research/2026-11-18-anthropic-guidance.md) §2.2)
- **The repo is public.** No client names or quotes go into committed files. Private evidence lives in `docs/**/private/`, which is gitignored.
- **License.** Superpowers is MIT. Ship its notice for the parts copied, and credit it in the README. Leave out its logo and the visual companion's telemetry.
- **Multi-machine.**
  - The remote is the source of truth.
  - Third-party marketplaces don't auto-update by default, and a pinned `version` blocks updates until it changes.
- **Project rules win.** `CLAUDE.md`, `.claude/rules/*` and project doc-location rules override Anvil's defaults.

## 6. Approaches considered

| | Approach | Trade-off | Verdict |
|---|---|---|---|
| **A** | **One skill per stage, plus small hooks and one script.** Each stage starts from Superpowers' prompts, rewritten plainly. | More files, and hand-offs between stages must be exact. Each stage can be invoked and evaluated on its own, and hooks enforce what prompts can't. | **Chosen**, kept close to Superpowers (Saad: "I like the superpowers and how it does things, I just want it fast") |
| B | One big skill, with stages as reference files | One trigger. But the description has to cover everything (the over-triggering shape), stages can't be invoked directly, and the size budget gets tight. | Rejected |
| C | Fork Superpowers 7.0.2 wholesale and patch it | Fastest start. It inherits forceful wording, dead todo-tool instructions and the ruling log that gets deleted (the drift cause), and it becomes a fork to rebase forever. | Rejected |

## 7. The design

### 7.1 Package layout

```
plugins/anvil/
  .claude-plugin/plugin.json      no Superpowers dependency; version bumped every release
  hooks/
    hooks.json                    SessionStart (startup, /clear, compact), PreToolUse, Stop
    run-hook.cmd                  Windows wrapper (adapted from Superpowers)
    session-start                 injects the short factual bootstrap
  bin/anvil                       one small script, see §7.9
  skills/
    anvil/        entry and router: what Anvil is, the flow, which stage skill to use
    brainstorm/   questions, variations, exploration loop  →  spec
    spec/         spec format, S-lines, approval record (may merge into brainstorm, see §11)
    plan/         plan format, task table, parallel-safe check, test strategy
    build/        build loop, waves, per-task review, change flow-back
    verify/       converge check, behavior evidence, result reuse
    finish/       commit/push per project rule, scaffold cleanup, tickets, branch safety
    debug/        systematic debugging (adapted from Superpowers)
    afk/          existing, revised to the new flow
    ui-mockup/    rewritten around the exploration loop
    ux-audit/     rewritten per the audit doc
    cross-model/  existing, plus the machine tooling folded in
    ticket-update/ existing (uncommitted today)
  references/     shared formats: spec, plan, progress file, test policy, reviewer prompts
  evals/          plugin eval cases (see §9)
  NOTICE          Superpowers MIT notice for the adapted parts
```

How the skills are invoked:
- Stage skills can be called directly, for example `/anvil:plan`.
- `afk` and `finish` get `disable-model-invocation: true` where side effects warrant it. **Claude's call.**
- Skills that only Anvil calls can get `user-invocable: false`.

### 7.2 The flow and its stops

```
request
  │
  ├─ trivial? ──► do it, one check, report  (Anvil states this path in one line; Saad can correct it)
  │
  ▼
Brainstorm ─► Spec ─[STOP 1: approve spec]─► Plan ─[STOP 2: approve plan]─► Build ─► Verify ─► Finish
```

- **The size is decided on the fly,** from how Saad describes the work. Anvil states the size it picked in its first line, so Saad can correct it. **Saad's decision** (builder check Q2).

  | Size | When | Documents and stops |
  |---|---|---|
  | **Trivial** | a single-file change with no new behavior, or "just do it" | none: do it, one check, report |
  | **Direct** | a concrete instruction about the code ("go and do this in the code"), a bug fix, or a small change, with no open questions and about 5 tasks or fewer | **one merged spec-and-plan document, one stop.** This is a plan-level requirement, not a spec requirement. A bug-fix spec part is a few lines: the bug, the expected behavior as S-lines, and the reproduction, which becomes a keep test. |
  | **Full** | a new feature, a high-level change to an already-built feature, or anything with open questions | separate spec and plan, **two stops** |

  If the work grows mid-way, Anvil says so and steps up a size.
- **The trivial path** applies to a single-file change with no new behavior, or when Saad says "just do it".
  - Anvil states the path it's taking in its first line, so it's visible and can be corrected. The model doesn't silently pick its own effort level. ([sentiment](research/2026-11-18-practitioner-sentiment.md) §3)
- **Stops are recorded on disk, and only Saad can pass them.**
  - A `UserPromptSubmit` hook records the time and text of each message Saad sends, appending it to `.anvil/prompts.log` (gitignored).
  - `bin/anvil approve spec|plan` writes `Approved: <date>` only if a message from Saad arrived **after the document was last changed**. So the model can't approve its own document.
  - Starting a stage checks for the approval:
    - the plan stage needs an approved spec;
    - the build stage needs an approved plan;
    - a PreToolUse hook blocks agent dispatch, and edits outside `docs/`, while the plan is unapproved.
  - **Claude's call** (builder check Q1).
- **Skipping stops:**
  - "AFK" skips all stops.
  - "Skip it", said at one stop, skips that stop.
  - **A pre-approval in Saad's own words** works the same way, including when it was given in the original request before the document existed. Examples: "approve the spec yourself", "go straight to the build", "don't stop for the plan". **Saad's decision.**
  - A skipped or pre-approved stop is recorded with the quote that authorised it, for example `Approved: pre-approved by Saad 2026-11-18 ("approve the spec yourself")`. That stage then runs with AFK decision-making: decisions go into the decision log, ordered by what deserves review first.
  - `bin/anvil approve --pre "<quote>"` accepts only a quote that appears verbatim in a recorded message from Saad, so the model can't invent one.
  - **AFK is turned on from Saad's own message.** `bin/anvil afk on` works only if the last recorded message contains an AFK phrase ("AFK", "I'm going to bed", "don't ask me", …). `afk` stays a skill the model can invoke, so plain chat starts it. **Claude's call.**
- **Checkpoints** happen only when Saad asks for one, at a named point in the plan or build. **Saad's decision.**
- **Fresh context for the build.** At stop 2, Anvil offers to start the build in a fresh session (`/clear`, then `/anvil:build <plan>`). This keeps old context from pulling the build back toward old code, and Anthropic's own flow recommends it. In AFK the build runs in subagents, which already have fresh context. **Claude's call.**

### 7.3 Brainstorm

This stage starts from Superpowers 7.0.2 brainstorming, plus Matt Pocock's grill-me mechanics. ([market scan](research/2026-11-18-market-scan.md) §3)

- **Look first.** Read the repo, the docs and the earlier conversation before asking. Anything the repo can answer gets looked up, by a subagent if it's broad, never asked.
- **Brainstorming ends when no question is left open.** **Saad's decision.**
- **Ask only what changes what gets built,** in **one batched round**.
  - Each question carries a **recommended answer**, worded so "yes" accepts it.
  - Everything else becomes a decision in the spec, where Saad actually reviews. **Saad's decision.**
- **Variations instead of interrogation.** When the information is thin, show 2 or 3 worked options with a recommendation, researched on the web where that helps. **Saad's decision.**
- **The exploration loop**, for UI or any "I don't know what it should look like" problem. This is the `ui-mockup` skill, and it follows the pattern from a past website redesign (notes §8):
  1. research;
  2. a shared `BRIEF.md`;
  3. 2 to 4 variants built **in parallel**, one file per agent;
  4. a comparison `index.html` and screenshots;
  5. Saad's reaction;
  6. if the round misses, a measured critique (`FLAWS.md`).
  - Rounds are numbered (`-r2`, `-r3`, …). **Each round changes only what Saad reacted to.** Mocks are throwaway. The chosen one becomes the spec's visual reference.
- **Research and architecture questions** end in a document Saad reviews. There's no plan or build stage.
- **Demos and POCs are pre-production work.** They go through the full flow, sized to the work. **Saad's decision.**

### 7.4 Spec

The spec is written in plain words for a human. It lives at `docs/<topic>/spec.md`, unless the project's doc rule says otherwise (see §7.10).

Sections, in this order:
1. **Header:** status, dates, `Approved:` line, mode (**normal change** or **redesign**), and a link to the mock or reference.
2. **Waiting on you:** at most 3 open questions, each with a recommended answer. Everything else has been decided.
3. **Intent and why.**
4. **Goals, non-goals, anti-goals.**
5. **Spec lines:** numbered `S1`, `S2`, …, one behavior each, in a list a script can parse.
   - Lines are never edited in place. A change gets a **new number**, and the old line is marked `RETIRED → S7 (2026-11-20, CR: <reason>)`. ([community frameworks](research/2026-11-18-community-frameworks.md) P1)
6. **Shared surface:** the exact names of the types, routes, contracts, files and resources that more than one part touches. This is what makes a parallel plan possible later. **Saad's requirement.**
7. **Replaces / stays** (redesign mode only): what gets replaced, and what existing code stays. "Reuse existing" applies only to what's listed under stays.
8. **Decisions:** each one with the call, the reason, the alternatives not taken, and whether it was *decided* or is *waiting on Saad*.
9. **Change log:** dated entries. Each says whether it's a **change request** or a **new feature**, and what it conflicts with that was decided before.

A **builder check** runs before stop 1: a fresh subagent reads the spec as the person who'll build it. Its questions are sorted into three piles: answered already, minor (Claude decides), and Saad's. This is Superpowers' prompt, adapted.

### 7.5 Plan

The plan is for the model: how each spec line becomes code. It lives at `docs/<topic>/plan.md`. It starts from Superpowers 7.0.2 writing-plans: signatures and test names, no code bodies, plus a self-check that it isn't a transcript of the code.

- **Header:**
  - a pointer to the spec;
  - global constraints;
  - interfaces per task;
  - the likely failures no test covers;
  - the `Approved:` line.
- **Task table:** id | spec lines covered | write set (files) | shared resources (ports, DB, lockfile, migrations) | depends on | wave.
  - Every new file, abstraction or option names the **spec line that needs it**. Anything with no spec line is over-building.
- **A foundations task** comes first and runs alone. It holds the shared types, routes and contracts from the spec's shared surface.
- **The parallel-safe check** is run by `bin/anvil plan-check`, not eyeballed:
  - write sets don't overlap;
  - no two tasks in a wave share a resource;
  - lockfiles, generated files and migrations belong only to the integrator;
  - dependencies only point at earlier waves;
  - (and the rest of the 9 points from [parallel build](research/2026-11-18-parallel-build.md)).
  - If the check fails, the plan runs sequentially and says why.
- **Execution mode,** proposed at stop 2 with numbers ("4 tasks in wave 2, estimated time saved …"):
  - parallel, 3 lanes by default and 4 at most, opted into at the stop;
  - or sequential.
- **Test strategy:**
  - every test is listed as **keep** (guards core behavior, names its S-line, says what breaks if it fails) or **scaffold** (used during the build, deleted in finish);
  - which tests are targeted per task;
  - the full-suite command and how long it takes.
- **Verification commands.**
- **Commit points (C1, C2, …).** Each one names:
  - the tasks or waves it closes;
  - its commit message;
  - whether it pushes.

  Commit points sit only at wave boundaries. A small plan has one, at the end.
- **The synced branch,** chosen at the plan stop. It's one of:
  - local only;
  - a branch made from an existing remote branch;
  - a new remote branch.

  `main` and `master` need Saad's explicit consent. **Saad's decision.**
- **Checkpoints,** only where Saad asked for them.

### 7.6 Build

This stage starts from Superpowers 7.0.2 subagent-driven-development, which runs continuously and stops for only four named reasons.

- **Two branches.** **Saad's decision:**
  - **The synced branch** tracks origin (or stays local, if Saad chose that). It only ever receives **one squashed commit per commit point.**
  - **The work branch** `anvil/<topic>/work` is local. It's branched from the synced branch, and holds every task commit, lane merge and fix. Lane worktrees branch from its HEAD.
- **At each commit point:**
  1. Reuse the recorded checks, rerunning only what changed.
  2. Squash the work branch into the synced branch as one commit, with the plan's message.
  3. Push, if the plan says so.
  4. Reset the work branch to the synced branch's new tip, so the next squash doesn't re-apply commits that already landed.
- **Pushes in AFK.** Approving the plan (or pre-approving it) authorises its pushes, so in AFK Anvil pushes at each commit point and Saad can follow along from another device.
  - If a push fails, Anvil says so plainly, keeps working locally and retries at the next commit point.
  - It never force-pushes the synced branch.
- **The progress file** `docs/<topic>/progress.md` is the single place for status. It travels inside each squashed commit.
  - Task markers: `[ ]` → `[~]` → `[x] C2`, naming the commit point that landed the task. Local commit IDs disappear when the work branch is reset, so they can't be the record. The commit point itself records the pushed commit ID.
  - It also holds: the current wave, blockers, the **decision log** (append-only, newest at top; each entry has choice, reason, confidence and "changes if"), and links to the spec's change log.
  - It replaces the todo tools.
- **Waves.**
  - Foundations first.
  - Then each wave dispatches up to 3 (or 4) implementer agents in one turn. Each uses Agent-tool `isolation: "worktree"`, based on **current HEAD**, not the default branch.
  - The builder verifies the `worktree.baseRef` setting. This was the "stale base" problem, hit 11 times in one past session.
  - The orchestrator merges lanes one at a time, in dependency order, and regenerates lockfiles and generated files itself.
- **Implementer brief.** This is Superpowers' implementer prompt, changed to:
  - run only the plan's **targeted** tests for its task, plus type-check;
  - never run the full suite;
  - commit in its worktree, with the project's pre-commit hook allowed to run on the targeted scope;
  - report what it changed and which S-lines it covers.
- **Per-task review.** Superpowers' single reviewer returns two verdicts: spec compliance against the task's S-lines first, then code quality. It **never reruns tests.**
  - It doesn't trust the implementer's report.
  - Fix rounds are capped at 5.
  - The quality checklist includes the **over-building item**: abstractions nobody asked for, speculative options, helpers that duplicate existing ones, code with no S-line.
  - **A review is required for every task that changes behavior.** Only tasks whose content the plan fully specifies (config, renames) skip it. The rule is fixed, not the model's call. ([sentiment](research/2026-11-18-practitioner-sentiment.md) §3)
- **A check after each merged wave.** After a wave's lanes are merged, before the next wave starts:
  - type-check;
  - the targeted tests of every task in the wave, run on the merged tree;
  - one short review of the merged diff, looking for clean merges that are wrong together (semantic conflicts).
  - The full suite also runs per wave only if it takes under about 2 minutes. Otherwise it waits for the final run.
  - Results are recorded, so nothing reruns on an unchanged tree.
  - **Claude's call** (builder check Q4). This follows Saad's principle: verification is fine, repeats on unchanged code are waste.
- **Diff stays inside its write set.** After each lane, `bin/anvil lane-check` confirms the lane's diff touched only its declared files.
- **Change flow-back,** when Saad changes direction mid-build or a task finds the spec wrong:
  1. Classify the change as a **change request or a new feature,** and name what it conflicts with. This is the pushback: "Earlier you decided X (S3, 2026-11-18). This replaces it. Cost: tasks T4 and T6 redo. Proceed?" In AFK, the choice is recorded instead of asked.
  2. Retire the old S-line and add the new one.
  3. `bin/anvil stale` lists every task, test and review that points at the retired line, and they're reopened.
  4. Update the plan and the progress file in the same step as the code.
- **Debugging.** On a failure the cause isn't obvious from, the `debug` skill runs: Superpowers' systematic debugging, adapted.
- **Editing a test** to make it pass requires a changed S-line referenced in the commit or progress entry. Otherwise the code gets fixed. A PreToolUse hook **warns** when a `keep` test file is edited without one. It starts as a warning and gets measured before it ever blocks. **Claude's call.**

### 7.7 Verify

1. **Result reuse.** Every test or verify run is recorded by `bin/anvil` against a key:
   - the git tree from a temporary index (which covers untracked files);
   - the command;
   - an environment fingerprint (lockfile and dependency hash, toolchain versions, allowlisted env vars).
   - Later steps reuse a **passing** result on an identical key: the reviewer, the commit step and finish.
   - Runs that used live services or the network, or ran no tests, are never reused.
   - A PreToolUse hook on test commands answers "fresh green result exists for this tree" instead of rerunning. ([test-run reuse](research/2026-11-18-test-run-reuse.md))
2. **The full suite runs once, on the final merged state.** This is the only full run, unless the suite is fast enough to also run per wave (see §7.6).
3. **The converge check** sorts every **live** S-line into **met / missing / partial / contradicts**, plus an **unrequested** list (code with no S-line).
   - "Met" needs **behavior evidence**: browser (chrome-devtools-mcp, then playwright-core), curl, or CLI output. "Tests pass" isn't enough on its own.
   - It loops through fixes until it's clean, or reports what's left.
4. **UI work.** `ux-audit` compares the built UI against the chosen mock.
5. **Before calling it done,** `cross-model` gives a second opinion on the diff. The trigger is a large or expensive-to-reverse change. **Claude's call.**

### 7.8 Finish

**Git workflow (Saad's decision, builder check Q3, refined 2026-11-18):**

- The two-branch flow and the plan's commit points (§7.5, §7.6) do the committing and pushing while the build runs.
- **Finish handles only what's left:**
  - the last commit point, if the build hasn't landed it yet;
  - offering to make a local-only synced branch live, by pushing it to a new or existing remote branch;
  - how to merge the synced branch into Saad's other branches.
- **Where a project rule exists, it wins.** This repo's CLAUDE.md, for example, says to commit and push after every unit of work; commit points are those units.
- **Cleanup:**
  - After the last push is confirmed on the remote, Anvil deletes its own local work branch and worktrees.
  - It also lists other stale local `anvil/*` branches, and remote ones whose work is already merged, then deletes them **after Saad confirms.**
  - Remote deletion always needs confirmation. **Claude's call.**
- **Commit messages** follow Saad's global rule: no Claude co-author trailer.

**The rest of finish:**

- **Scaffold tests** are deleted, and their deletion is listed in the report.
- **The spec and plan are marked done.** The progress file is kept as the record, not deleted (unlike Superpowers' logs).
- **Tickets.** `ticket-update` posts a completion comment with evidence and the stand-up line, if the repo has a tracker.
- **Branch safety.** No work on main or master without consent. Never force-push the synced branch. Resetting Anvil's own local work branch is allowed.
- **The report** covers: what shipped, the verification evidence (real output), the decision log (most review-worthy first), the weakest part, and what wasn't done.

### 7.9 `bin/anvil`, the one script

A small CLI using only the language's standard library. The language is **Python 3, called through a bash wrapper plus `.cmd`**, the same pattern as the hooks. **Claude's call.**
- On this machine, `python3` is the broken Microsoft Store stub, while `python` (3.13) and Node 26 both work.
- The wrapper tries `python`, then `py -3`, then `python3`.
- The builder confirms the other machine.

| Command | Does |
|---|---|
| `spec-lines` | parse S-lines; list the live and retired ones |
| `stale` | list tasks, tests and reviews that point at a retired S-line, or whose recorded result no longer matches the tree |
| `approve spec\|plan` | write the `Approved:` line; `check` refuses a stage without it |
| `plan-check` | the 9-point parallel-safe check over the task table |
| `lane-check <lane>` | the diff stays inside the lane's write set |
| `run <cmd>` / `fresh <cmd>` | record a test or verify result by key; answer whether a fresh green result exists |
| `progress` | print the status summary from `progress.md` |

### 7.10 Where files go

- **Default:** `docs/<topic>/` holds `spec.md`, `plan.md` and `progress.md`. Mocks go in `docs/<topic>/mocks/` (rounds `-r2`, …). Research goes in `docs/research/YYYY-MM-DD-<topic>.md`.
- **The project's doc rule wins** when it exists.
- **Existing repos** with `docs/superpowers/specs|plans` keep working: Anvil reads those paths, and writes new work to the default unless the project rule says otherwise.
- **Claude's call.**

### 7.11 The other skills in the flow

| Stage | Skill | Change needed |
|---|---|---|
| Brainstorm | `ui-mockup` runs the exploration loop. `cross-model` does research on big questions. | **Rewrite** `ui-mockup`: local files (no Artifacts), rounds, comparison page, critique, "change only what was reacted to" |
| Spec | `cross-model` reviews decisions that are expensive to undo | none |
| Plan approved | `ticket-update` splits plan tasks into tickets, if a tracker is set up | **Map** its fields to the task table |
| Build | `ticket-update` comments at real stops; `debug` | none |
| Verify | `ux-audit` checks the build against the mock; `cross-model` before done | **Rewrite** `ux-audit` per the audit doc: P0/P1/P2, tested vs code-only labels, owner decisions before fixes, chrome-devtools-mcp then playwright-core |
| Finish | `ticket-update` completion comment | none |
| Any | `afk` removes stops and logs decisions; a Stop hook keeps the run going until `progress.md` has no open tasks | **Revise** to the new flow; add the Stop hook |

### 7.12 The simplicity rules

Three plain always-on lines in the `anvil` skill replace today's five "anti-slop" rules. Wording is drafted in [simple-code rules](research/2026-11-18-simple-code-rules.md) and must be tested before adoption:

- **Normal change:** the smallest diff that meets the spec lines, using existing patterns.
- **Redesign:** build what the spec describes. Existing code is reused only where the spec's *stays* list names it.
- **No piece without a spec line:** no abstraction, option or helper that no S-line needs.

**Not adopted:** the viral Karpathy-style "4 rules" file, "prefer one-liners", and stop-and-ask rules. There's no evidence for them on current models.

### 7.13 Coexistence with Superpowers

Decided in notes §7, and revised after research.

| Setup | How |
|---|---|
| **Anvil only** (target) | Turn Superpowers off with `enabledPlugins` (`false`), per project or for the user |
| **Both installed** (while building trust) | One line in Saad's global `~/.claude/CLAUDE.md`, plus Anvil's startup facts, plus distinct skill names. This works through wording only, so it's **measured with evals** |
| **Superpowers only** (escape hatch) | `/plugin disable anvil` |

## 8. Maintenance

- **Upstream watch.** Each copied file records its source (`superpowers@7.0.2 skills/…`). On each Superpowers release, Anvil runs a diff against those sources, and each change is adopted or rejected deliberately, with a note.
  - The trigger is manual: a `/anvil:upstream` command or a checklist item. A schedule is possible later.
- **Releases.** Bump `plugin.json` `version` every release, otherwise other machines never update. Turn on auto-update for this marketplace on each machine.
- **Evals.** These are rerun when the default model changes, and before each release.

## 9. How we know it's better: no-regression checks

1. **Plugin evals** (`claude plugin eval`), building on `ticket-update`'s eval layout:
   - the trivial path is taken for a one-line change, with no plan and one check;
   - brainstorm looks things up instead of asking, and batches its questions with recommended answers;
   - the spec has parseable S-lines and ≤3 open questions;
   - the plan-check rejects an overlapping write set;
   - a mid-build change retires an S-line, and `stale` flags the dependents;
   - the reviewer catches a spec miss and an over-built helper;
   - a test isn't rerun on an unchanged tree;
   - AFK runs to completion without asking;
   - with Superpowers installed, Anvil leads.
2. **Replays.** Re-run 2 or 3 past real requests (one normal change, one redesign, one multi-task feature) from the private evidence, comparing old and new. Compare wall-clock time, full-suite runs, review coverage, and whether the result matched the request.
3. **Pilot parallel build** on one real feature, against a sequential run of the same plan, before parallel becomes the recommended option.

## 10. Rollout

1. **Core flow and the script:**
   - `anvil`, brainstorm, spec, plan, build, verify, finish, debug;
   - `bin/anvil`;
   - the hooks;
   - the references;
   - the revised `afk`.
   - The evals in §9.1 come at the end of this phase.
2. **Packaging:**
   - drop the Superpowers, claude-session-driver and episodic-memory dependencies;
   - the NOTICE file;
   - the version bump;
   - the README;
   - install on this machine;
   - remove the loose `~/.claude/skills/{anvil,afk,cross-model-review}` copies;
   - turn on auto-update.
3. **Sibling rewrites:** `ui-mockup` and `ux-audit`.
4. **`cross-model` tooling:** fold in the machine's commands and scripts, and fix the broken model names (audit doc §1).
5. **Replays and the parallel pilot.**

Each phase is verified before the next starts.

## 11. Left to the builder

- Whether `spec` is a separate skill or part of `brainstorm`, judged by size and evals.
- The exact hook matchers, and the PreToolUse logic for test-command reuse.
- The `bin/anvil` internals, and the exact 9-point check list (from the research).
- Eval case wording.
- How much of each Superpowers prompt survives verbatim. The default is to keep its structure and rewrite the forceful wording.

## 12. Claude's calls, for Saad to check

1. Approvals are recorded on disk, and the build refuses to start without them. A pre-approval must quote Saad's message verbatim, and the script checks that quote against the prompt log.
2. Fresh session offered at stop 2.
3. Only Saad can pass a stop or turn on AFK, enforced by the UserPromptSubmit hook. `finish` has `disable-model-invocation`; `afk` stays model-invocable so plain chat starts it.
4. The test-edit guard starts as a warning, not a block.
5. `cross-model` runs before done only on large or expensive-to-reverse changes.
6. After a confirmed push, Anvil deletes its own local branch automatically. Remote branches and other stale branches are deleted only after Saad confirms.
7. `bin/anvil` is in Python 3.
8. Default file location is `docs/<topic>/`. Old `docs/superpowers/` paths are read but not used for new work.
9. Upstream watch is triggered manually.
10. Parallel is opted into at stop 2 (default 3 lanes), not on by default.
12. Commit points sit only at wave boundaries. After each squash, the work branch is reset to the synced branch's tip, and progress markers record commit points, not local commit IDs.
11. A cheap check runs after each merged wave. The full suite runs per wave only when it takes under about 2 minutes.
