---
name: build
description: Use when an approved Anvil plan is ready to be built, when Saad runs `/anvil:build` with a plan path, when the plan stage hands off after stop 2, or when a build that was interrupted (by `/clear`, compaction or a usage limit) needs to pick up where its `progress.md` left off.
---
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/SKILL.md -->
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/references/preflight.md -->
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/references/handling-reports.md -->
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/references/batching.md -->
<!-- adapted from superpowers@7.0.2: skills/executing-plans/SKILL.md -->
<!-- adapted from superpowers@7.0.2: skills/dispatching-parallel-agents/SKILL.md -->

# Build

Build an approved plan: a fresh implementer per task, one reviewer per task giving two verdicts (spec, then quality), a check after each merged wave, and one whole-branch review at the end. Then hand over to `anvil:verify`.

You are the orchestrator: you write `progress.md`, create worktrees, merge lanes, land commit points and make rulings. In subagent mode you don't write task code: your context is for coordination, and code you write skips review.

**Continuous execution.** Don't pause between tasks to check in: Saad approved the plan so it would run. `progress.md` is the live view (`anvil progress` prints it).

**Rulings, not stalls.** Conflicts, ambiguities, plan defects, a cap you would have asked to exceed: decide them. The spec is the binding authority, the plan is its argument, and your judgment settles what neither answers. Each ruling goes in the progress file's decision log, newest first:

```
- 2026-11-18 **<choice>** — <reason>. Confidence: high|medium|low. Changes if: <fact>.
```

The log is append-only: never edit or remove an entry. A ruling you reverse gets a new entry that names the old one. A wrong ruling costs rework Saad can see and undo; a build parked on a question costs his whole day.

**Four things stop you, in any mode:**
1. an irreversible or destructive operation (resetting Anvil's own work branch and removing its own lane worktrees are not in this group);
2. a security-sensitive action;
3. a side effect the plan doesn't authorise: a push, or a merge into any branch other than the work branch, outside the plan's commit points; a publish; a deploy. Approving the plan authorised the pushes its commit points name;
4. a plan so broken that every path forward is a guess.

Outside AFK and pre-approved builds, two more things stop you: a checkpoint Saad named in the plan, and a change that replaces one of his decisions ([references/change-flow-back.md](references/change-flow-back.md)). When AFK is on or the build stage was pre-approved, nothing asks Saad: every question becomes a ruling, change requests are logged rather than asked, and only the four stops above stop you. To stop: say why in one short message, and add the reason under `## Blockers`. In AFK, also write it under `## Stop note`, so the Stop hook lets the turn end. If the repo has a tracker, `ticket-update` comments at real stops.

**Narration:** at most one short line between tool calls.

## Preflight

1. **Sync.** `git fetch`, then `git status`. If the synced branch (the plan header's `- **Synced branch:**` line) is behind its remote, pull. If it has diverged, stop and tell Saad: that is stop 4, since any merge you pick is a guess.
2. **Gate.** `anvil topic show`. If it reports no active topic (the plan was approved on another machine, or after `topic end`), run `anvil topic start <slug> --size <the plan's Size> --dir <the plan's folder>` first. Then `anvil check build` and `anvil topic stage build`. Both refuse unless the plan is approved. Don't work around a refusal; report it.
3. **Resuming?** If `progress.md` already has `[~]` or `[x]` tasks, or `git worktree list` shows lanes for this topic, read [references/resuming.md](references/resuming.md) before anything else. Re-dispatching finished work is the costliest failure here.
4. **Read once.** The plan's header, Global constraints, Review focus, Task table, Test strategy, Commit points and execution mode, and the spec's S-lines. Note the type-check and full-suite commands and the suite's recorded duration.
5. **Work branch.** `git switch -c anvil/<topic>/work <synced branch>`, or switch to it if it exists. No work on `main` or `master` without Saad's explicit consent. Branch rules: [../../references/git-flow.md](../../references/git-flow.md).
6. **Progress file.** Create `progress.md` in the topic folder `anvil topic show` reports, if it's missing, from the task table, in the format in [../../references/formats.md](../../references/formats.md), and set `- **Stage:** build`. Only you write it; lanes never do.
7. **Build folder.** Scratch files (the lane brief, per-task messages, reports, review packages) go in `$(git rev-parse --path-format=absolute --git-common-dir)/anvil/build/<slug>/`. Never committed; every worktree reads it by absolute path; it survives `/clear`.
8. **Conflict scan.** Scan the plan once, writing down what you checked:
   - tasks that contradict each other, the spec, or the Global constraints;
   - anything the plan mandates that the review rubric treats as a defect (a test that asserts nothing, a duplicated logic block);
   - one row for every pair of tasks that share an interface: what one produces against what the other consumes.

   Rule on each conflict and log it. A clean scan gets one decision-log line saying so.
9. **Lane brief.** Write one shared brief file for the whole build from [prompts/implementer.md](prompts/implementer.md). It carries the rules every lane shares, the pinned contracts ([references/waves.md](references/waves.md), "Before a wave"), and the project's environment notes (interpreter, test runner, shell traps).

## Execution mode

Use the mode the approved plan states.

- **Parallel:** waves of up to the plan's lane count (default 3, 4 at most), one worktree per lane. Mechanics in [references/waves.md](references/waves.md); read it before the first wave.
- **Sequential:** one task at a time, in task order. The implementer works in the main checkout on the work branch. Record BASE (`git rev-parse HEAD`) before each task. A task's check is its targeted tests through `anvil run --scope targeted`, plus its smoke path where the plan lists one (`anvil run --scope smoke`); a commit point lands once every task it closes has passed its check.
- **Inline (single agent):** when Saad chose it, or no subagent tool is available. You do each task yourself, under an implementer's rules (targeted tests only, inside the write set, the test-changed vs code-changed statement). Never fabricate a dispatch. The per-task review still happens, by a fresh reviewer if you can dispatch one; otherwise do it yourself as a separate pass with [prompts/task-reviewer.md](prompts/task-reviewer.md), log `self-review (no subagent tool)` under the task, and say so at the end: Saad decides whether that's enough.

## Model selection

Use the least capable model that does each role well, and always name it in the dispatch: an omitted model inherits the session's.

- **Implementers:** cheap for 1–2 files with a complete spec; standard for multi-file integration; most capable for design judgment or broad codebase understanding. Prose-only tasks get a mid tier at least: cheap models take two or three times the turns on multi-step work.
- **Reviewers:** scaled to the diff's size and risk, mid tier as the floor. Scoped re-reviews of small fixes take a cheap-to-mid tier.
- **Wave review:** mid tier. **Final review:** most capable. **Fix rounds 4–5:** one tier above the stuck implementer.

## The task loop

Every task goes through this loop, in every mode.

### 1. Dispatch the implementer

- Mark the task `[~] T3 <title> (lane anvil/<topic>/T3)` in `progress.md` when you dispatch it (in sequential mode, leave out the lane part).
- The dispatch is short ([prompts/implementer.md](prompts/implementer.md)): the lane brief, the task's plan section, the absolute working directory, the report file path, and only what the brief can't know (interfaces and rulings from earlier tasks, your resolution of an ambiguity, a parked finding in the area).
- Don't paste the plan, other tasks' history, or prior summaries into a dispatch: everything you paste, and everything a subagent prints back, stays in your context. Hand things over as files.
- **Batch small same-shape tasks.** Several small, independent edits of the same kind (the same one-line fix or field addition across files) can go in one dispatch that lists every file and its change, reviewed as one diff. Keep one dispatch per task for work that needs its own judgment, tests or review.
- Note the implementer's agent id: fix rounds 1–3 resume this agent.

### 2. Handle the report

- **DONE:** go to the review.
- **DONE_WITH_CONCERNS:** correctness or scope concerns get addressed before the review; observations ("this file is getting large") get noted, and the review goes ahead.
- **NEEDS_CONTEXT:** give the missing context and resume it.
- **BLOCKED:** find what has to change. A context gap: more context. Needs more reasoning: a more capable model. Too big: split it and log the split. The plan is wrong: rule on the correction, log it, carry it in the re-dispatch. Never resend the same task to the same model unchanged.
- **The spec looks wrong** (the report says a requirement can't hold, or Saad changes direction): follow [references/change-flow-back.md](references/change-flow-back.md).
- **A failure whose cause isn't obvious** (on the merged tree, or a lane stuck on one): run `anvil:debug`, then come back here.

Check the report has what the prompt asks for (S-lines covered, the targeted test command and summary line, a test-changed or code-changed statement per touched test). A missing item goes back to the implementer before the review.

### 3. Check the write set

`anvil lane-check T3 --base <base>`, run in the task's working directory. The base is the work branch in parallel mode, and the recorded BASE otherwise. Files outside the write set go back to the implementer: revert them, or report BLOCKED if the task needs them; the fix is then a plan ruling, never a quiet reach across.

### 4. Review the task

Every task gets reviewed, unless its row says `skip (fully specified)`: that task goes straight to `[x]` after a clean lane-check. The rule is fixed; it isn't your call per task. An implementer's self-review never replaces it.

- Write the review package before anything else touches the branch: `git log --oneline BASE..HEAD`, `git diff --stat BASE..HEAD` and `git diff -U10 BASE..HEAD`, run in the lane, redirected into one file in the build folder. BASE is the commit the task started from, never `HEAD~1` (that drops every commit but the last). In parallel mode, write it before merging the lane.
- Dispatch [prompts/task-reviewer.md](prompts/task-reviewer.md), filling its placeholders as its notes say.
- Accept no review missing either verdict.

### 5. Act on the review

Read [references/receiving-review.md](references/receiving-review.md) when a review comes back with anything other than two clean verdicts, and again before every fix round: it holds the triage, the 5-round fix cap, the breaker, and what each round writes to `progress.md`. Your memory of it doesn't survive compaction.

### 6. Complete the task

When the review is clean, or every open finding is parked with a ruling at the cap, mark the task `[x] T3 <title>` in `progress.md`, with the report's test statements as an indented line under it (`  - tests: <file> code changed (S3)`): `finish` reports from these, since the build folder doesn't survive the build. The commit point adds ` C<k>`. Never start a task that depends on this one while it has open Critical or Important findings that are neither fixed nor parked.

## Tests in the build

The rules are in [../../references/test-policy.md](../../references/test-policy.md). Reuse needs the scope the run used: `anvil fresh --scope <the scope it ran with> -- <same cmd>`.

## Simplicity

See [../../references/simplicity.md](../../references/simplicity.md). The spec's `- **Mode:**` line says whether this is a normal change or a redesign.

## Commit points

Land one when every task it closes is `[x]` and its check is clean, per the plan's `## Commit points` table and [../../references/git-flow.md](../../references/git-flow.md):

```bash
anvil fresh --scope <scope> -- <cmd>     # each recorded check; rerun only what isn't fresh
git add <topic folder> && git commit -m "docs(<topic>): progress"   # on the work branch, if changed
git switch <synced>
git merge --squash anvil/<topic>/work
git commit -m "<the plan's message>"     # no co-author trailer or Claude attribution
git push                                 # only if the row says yes
git switch anvil/<topic>/work
git reset --hard <synced>
```

Then record it under `## Commit points`: `- C<k> <sha> pushed <date>`, `- C<k> <sha> not pushed (push failed <date>)`, or `- C<k> <sha> local <date>` for a `no` row. The record travels in the next squash. The commit point that closes the last wave is left for `finish`, so the fixes verify makes travel in it.

## Final review

When every task is `[x]`:

1. Write a package of the whole build (its range is in the placeholder notes of [prompts/final-review.md](prompts/final-review.md)) and dispatch that prompt on the most capable model, with the inputs it lists.
2. Triage per [references/receiving-review.md](references/receiving-review.md). Critical and Important findings get **one** fix wave, batched by disjoint file groups ([references/waves.md](references/waves.md), "Batched fixes"), then exactly one scoped re-review of the fix range ([prompts/re-review.md](prompts/re-review.md)). No second wave: residual findings become rulings, and the load-bearing ones are named at the end.
3. Each item on the reviewer's "Declined to judge" list is a ruling you make and log.

## Hand-off

1. Your closing message lists **Rulings I made**: every decision-log entry this build added, most review-worthy first, each with its confidence and "changes if"; then the deferred minors and anything parked. A ruling missing from it was made in secret.
2. Remove the lane worktrees still left, and this topic's build folder.
3. `anvil topic stage verify`, set `- **Stage:** verify` in `progress.md`, then run `anvil:verify`.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "Close enough on spec compliance" | A spec gap means not done. Fix it, or reach the cap and adjudicate. |
| "The fix was small, skip the re-review" | Unreviewed fixes are how regressions land. |
| "The lanes are independent, skip the wave check" | Each lane passes its own tests; clean merges can still be wrong together. |
| "I remember which tasks are done" | You remember a summary. Read `progress.md` and `git log`. |
| "Progress bookkeeping is overhead" | It's what survives compaction, and it's Saad's only live view. |
