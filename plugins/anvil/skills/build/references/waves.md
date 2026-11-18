<!-- adapted from superpowers@7.0.2: skills/dispatching-parallel-agents/SKILL.md -->
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/SKILL.md -->

# Waves

How a parallel build runs. Each lane is the task loop from SKILL.md, in its own worktree. What this file adds: how lanes start, how they merge, and the check after each merged wave.

Parallel is safe here only because the plan did the work first: a foundations task that ran alone, write sets that don't overlap (`anvil plan-check` passed), and contracts pinned before dispatch. If any of those is missing for a wave, run that wave in sequence and log why.

## Contents
- Before a wave
- Creating the lanes
- Dispatching
- While lanes run
- As each lane reports
- Merging
- The wave check
- Batched fixes
- Closing the wave

## Before a wave

- The previous wave is closed: every task `[x]`, the wave check clean, its fixes merged. A task starts only when its dependencies have merged and come back clean from review.
- `- **Wave:** <n> of <m>` is set in `progress.md`.
- **Pin shared contracts.** Every contract this wave's lanes share (a field name, a record shape, a function signature, a route, a file path) is written into the lane brief before dispatch, with its exact spelling and its producer and consumers. Lanes see each other's contracts, never each other's code; an unpinned field name is how two lanes end up with `payment_status` and `status`. If this wave needs a contract an earlier wave changed, update the brief first. A contract you can't pin yet means those tasks aren't parallel-safe: run them in sequence and log why.
- **Commit the topic docs.** Any change to the spec, plan or progress file since the last commit is committed on the work branch before you create this wave's lanes, so the lanes and `anvil lane-check` read the current plan.

## Creating the lanes

You create each lane's worktree yourself, from the work branch, and brief the agent with its absolute path:

```bash
git worktree add ../<repo>-lane-T3 -b anvil/<topic>/T3 anvil/<topic>/work
```

- Don't rely on the Agent tool's `isolation: "worktree"`: its base defaults to the repo's default branch, not the work branch, and lanes built on the wrong base miss the foundations and the previous wave ("stale base").
- Confirm the base: `git -C ../<repo>-lane-T3 rev-parse HEAD` equals `git rev-parse anvil/<topic>/work`.
- A short root next to the repo keeps Windows paths under the length limit. If `git worktree remove` later fails with `Filename too long`, set `git config core.longpaths true` and retry.
- If the project forbids extra folders or worktrees, run the build sequentially and log why. Lanes sharing one checkout race on the index and sweep up each other's half-done edits.
- If lanes need installed dependencies, the lane brief says how to install them (or reuse a shared store). Lanes never commit lockfiles or generated files.

## Dispatching

- Send up to the plan's lane count (4 at most) implementer dispatches **in one message**: several dispatches in one message run at the same time; one per message runs them one after another. Run them in the background.
- Each dispatch is the short per-task message from [../prompts/implementer.md](../prompts/implementer.md): its task, its absolute lane path, the lane brief path, its report file. Shared rules live in the brief file, not pasted into every dispatch.
- Mark each task `[~] T3 <title> (lane anvil/<topic>/T3)` in `progress.md` in the same step.
- Lanes run focused tests only. If the test runner spreads across cores, the brief caps workers per lane; one full suite at a time, never one per lane. No dev server in a lane unless the brief gives that lane its own port and database.

## While lanes run

- Keep working on local things: review packages, progress entries, the next wave's brief. Results arrive on their own; don't poll.
- Per-task reviews of lanes that have reported can run while you dispatch the next independent lanes. A reviewer reads the lane's worktree and its review package, so merging that lane meanwhile doesn't disturb it.
- When you are idle, wait in bounded stretches. Between them, list your live agents and chase any that finished without reporting.

## As each lane reports

In the order the reports arrive:

1. Handle the report (SKILL.md, step 2).
2. `anvil lane-check T3 --base anvil/<topic>/work`, run in the lane. Files outside the write set go back to the implementer.
3. Write the review package from the lane, before merging it: `BASE` is the work branch tip the lane was created from.
4. Dispatch the task reviewer, unless the row says `skip (fully specified)`: that task goes straight to `[x]` after a clean lane-check.

## Merging

Merge lanes one at a time, **in task order**, into the work branch in the main checkout:

```bash
git merge --no-ff anvil/<topic>/T3 -m "merge T3: <task name>"
```

- A textual conflict means the plan was wrong about independence. Resolve it by ruling which side the spec supports, log the ruling, and check that the losing lane's S-lines are still met.
- Lockfiles and generated files are regenerated by you after the merges, never merged from lanes.
- A lane merged before its review returned is still under review: its task isn't `[x]`, and nothing that depends on it starts.
- Fix commits made later in a lane worktree are merged the same way, again in task order.

## The wave check

After every lane of the wave has merged (and lockfiles and generated files are regenerated), on the merged tree:

1. **Type-check**, with the plan's command.
2. **The targeted tests of every task in the wave**: `anvil fresh --scope targeted -- <cmd>` first, then `anvil run --scope targeted -- <cmd>` for whatever isn't fresh.
3. **The wave's smoke paths**, if it has any: `anvil run --scope smoke [--external] -- <cmd>`.
4. **The full suite**, only if the plan records it at under about 2 minutes: `anvil fresh --scope full -- <cmd>`, else `anvil run --scope full -- <cmd>`. Otherwise it waits for verify.
5. **The wave review**: a package of the merged diff (work branch tip before the wave's first merge, to HEAD), and [../prompts/wave-review.md](../prompts/wave-review.md), looking for clean merges that are wrong together. A wave with a single lane skips it (nothing to conflict with); log the skip in the decision log.

A failure whose cause isn't obvious goes to `anvil:debug`. Findings go to the batched fixes below.

## Batched fixes

After a wave's reviews (the per-task reviews and the wave review) are in, fix in batches rather than one agent per finding: per-finding fixers each rebuild context and rerun tests.

1. Triage every finding first, per [receiving-review.md](receiving-review.md).
2. Group the open findings by the files they touch. Findings whose files overlap join one group, so the groups are disjoint.
3. One fixer per group, each with the **full findings list for its group**. A group that lies inside one lane's write set goes to that lane's own implementer (resumed, in its worktree; that's the fix round for each of its tasks). A group that spans lanes (usually a wave-review finding) gets one fixer in a fresh worktree from the work branch, with the union of those write sets.
4. Disjoint groups run at the same time, dispatched in one message.
5. Each group gets one scoped re-review, then its commits merge in task order. Each round counts toward the 5-round cap of every task it touches.

## Closing the wave

1. Every task in the wave is clean, or its residual findings are parked with rulings. Mark them `[x]` (plus ` C<k>` if a commit point closes here).
2. Remove the lane worktrees and branches: `git worktree remove ../<repo>-lane-T3`, then `git branch -d anvil/<topic>/T3`.
3. If a commit point closes here, land it (SKILL.md, "Commit points"): `anvil fresh --scope <the scope it ran with> -- <same cmd>` finds the wave check's results. The commit point that closes the last wave is the exception: it is left for `finish`.
4. Then the next wave.
