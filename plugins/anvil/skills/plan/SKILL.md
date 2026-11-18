---
name: plan
description: Use when an Anvil topic reaches the plan stage - right after Saad approves the spec at stop 1, or after brainstorm has written the spec part of a direct-size plan.md - and when Saad asks to write, redo or revise the implementation plan before the build starts.
---
<!-- adapted from superpowers@7.0.2: skills/writing-plans/SKILL.md -->

# Plan

The plan turns spec lines into tasks an implementer can build without guessing. Write it for an engineer who has not seen this codebase or this spec. Assume they write idiomatic code in the project's language once they know the exact interface and the exact test, and that they make a reasonable choice wherever the plan leaves one open. What they cannot know is what you decided: which files, which names and signatures, which values from the spec, which tests prove each task. The plan records those decisions and nothing else.

Each implementer sees only its own task section, the global constraints and its S-lines, so anything a task needs from a neighbour goes in its Interfaces block.

## Entry

1. `anvil check plan`, then `anvil topic stage plan`. If either is refused, report the reason it prints in one line (the spec isn't approved, no active topic, ...) and go back to the step it points at. Don't write a plan against an unapproved spec.
2. Read the spec: `anvil spec-lines --live` for the S-lines, plus its shared surface, decisions and (in a redesign) its replaces/stays list. Then read the code the tasks will land in. Hand a broad lookup to a subagent and keep its conclusion.
3. The plan goes in the topic folder, `docs/<slug>/plan.md` by default. The project's own doc rule wins.
   - **Full size:** a new `plan.md` that points at `spec.md`.
   - **Direct size:** `plan.md` already holds the spec part, written by brainstorm. Add the plan part underneath it in the same file. There is one stop, at the plan.
4. Use [plan-template.md](references/plan-template.md) for the shape. The header lines and the three tables follow [formats.md](../../references/formats.md) exactly: `bin/anvil` parses them, and a renamed column or heading breaks the gates.

If the work is bigger than its size (a direct topic needing more than about 5 tasks, or a question the spec doesn't answer), say so, step up with `anvil topic start <slug> --size full`, move the spec part of `plan.md` into a new `spec.md`, and go back to brainstorm rather than planning around the gap.

## File structure first

If the spec covers several independent subsystems, suggest one plan per subsystem, each working and testable on its own.

Before drawing tasks, map which files get created or changed and what each one is for. This is where decomposition gets locked in.

- One clear responsibility per file, with a clear interface.
- Files that change together live together. Split by responsibility, not by technical layer.
- In an existing codebase, follow its patterns. Split a file only when one you're changing has grown unwieldy.
- Every new file, abstraction or option names the S-line that needs it. A piece with no S-line is over-building ([simplicity](../../references/simplicity.md)).

## Tasks

A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate. Fold setup, configuration, scaffolding and docs into the task whose deliverable needs them. Split only where a reviewer could reject one task while approving its neighbour. Each task ends with something testable on its own.

**The foundations task.** When the spec has a shared surface, T1 holds it: the shared types, routes, contracts, registry entries and module declarations that more than one task touches, written as code with their exact names. It is wave 0 and runs alone, so the lanes after it build against names that can't drift. A small sequential plan whose shared surface is empty has no foundations task; its tasks start at wave 1.

**The task table** is the plan's index. Per row:
- **Spec:** the S-lines it implements. A row with none is either over-building or a fully specified mechanical change (config, rename) marked `skip (fully specified)` in Review.
- **Writes:** exact repo-relative paths or globs, each in backticks. This is the lane's write set; `anvil lane-check` holds it to that.
- **Shared:** `port:<n>`, `db`, `lockfile`, `generated`, `migrations`, `devserver`, or `-`.
- **Depends** points only at earlier waves.
- Lockfiles, generated files and migrations go in no lane's Writes. The integrator (the orchestrator) regenerates them after merging; list that under **Integrator-only**.
- **Review** is `yes` for every task that changes behavior.

**Per-task sections** replace the checkbox steps: Spec, Files, Interfaces (Consumes and Produces, exact signatures), Tests (name, type, S-line, targeted command) and a short numbered step list.

For services, API calls and data hooks, Interfaces pins the DTO shape, the cache keys and their invalidation, the fallback, and the error mapping. Anything invented rather than confirmed in the code or docs is marked as an assumption, in AFK or not.

## What a step contains

A step is done when the implementer can write exactly one reasonable thing from it: unambiguous, not complete.

- **A code step:** the exact signature (name, parameters, return type), the file it lives in, and the values the spec pins. The implementer writes the body. A body appears only for an algorithm the signature and tests don't determine, or for exact copy the spec fixes.
- **A test step:** the test's name and what it asserts, with the spec's exact values.
- **A verification step:** the command, and the output that means it passed.
- **A reference to another task:** point at that task's Interfaces block; don't repeat its code.

Signatures, not bodies. A plan longer than the code it describes has written the code instead. Lines that decide nothing ("to be decided", "handle edge cases", "add appropriate validation", "write tests for the above", a type no task defines) are the opposite failure. The self-review catches both.

## Header, global constraints, review focus

- **Header lines:** as in the template, then goal, architecture and tech stack.
- **Global constraints:** the spec's project-wide requirements (version floors, dependency limits, naming and copy rules, platform needs), one line each, values copied verbatim. Lanes don't share context, so anything every task obeys is stated here once. Include the spec's mode (normal or redesign).
- **Review focus:** the inputs or failure modes the spec implies but no task's tests would exercise, most likely to bite first, at most five. Name the input and the behavior a reasonable person would expect. The spec's silence on an input isn't permission for it to break. Then add, for each line, the test that pins it to the task that owns the code. An empty section means you checked and found none.

## Test strategy

The test strategy replaces "do TDD, commit often". The rules are in [test-policy](../../references/test-policy.md); the plan applies them.

- **Name the tests that guard each task,** in the `## Test strategy` table: Test, Type (`smoke`, `keep`, `repro`, `scaffold`), Spec, what breaks if it fails, and the owning task.
- **Stay in test-policy's budget** per kind of work. Going over needs one line of reason in the plan.
- **Test-first only for repros.** A bug-fix task writes its repro before the fix. Elsewhere the steps implement, then test.
- **Each task names its targeted command,** run as `anvil run --scope targeted -- <cmd>`, so no lane needs the full suite.
- **Record the full-suite command and how long it takes, and the check commands:** `Type-check:`, `Lint:` and `Build:`, each `<command | none>`. Take the duration from a recorded run, CI timings or the project docs; don't run a long suite just to time it. If it's unknown, write "not measured", and the build treats it as over 2 minutes (full suite once, at the end).

## Commit points and the synced branch

Follow [git-flow](../../references/git-flow.md). The plan decides three things there:

- **The synced branch**, written in the header as `<branch> (local)` or `<branch> (remote <remote>/<branch>)`. It's one of: local only; a branch made from an existing remote branch; or a new remote branch. Propose one with a reason. `main` or `master` as the synced branch needs Saad's explicit consent in his own words; without it, propose a new branch and ask at the stop. A project rule about branches wins.
- **Commit points** (`## Commit points`: Commit, Closes, Message, Push). They sit only at wave boundaries; a small plan has one, at the end. Each names the waves and tasks it closes, a conventional commit message with no Claude co-author trailer, and whether it pushes. A local-only synced branch doesn't push.
- **The work branch** is `anvil/<slug>/work`, local, branched from the synced branch.

## Execution mode

Run `anvil plan-check` once the task table is written, before presenting. It checks the table's mechanics (per-wave write-set and resource collisions, wave order, integrator-only paths, tasks with no S-line, dependencies, the lane cap, ids). It doesn't check that every live S-line has a task; self-review item 1 does.

**When it reports findings,** do one of two things for each, and write it under `## Execution`:
- fix the plan (split or narrow a write set, move a task to a later wave, add the missing dependency, hand the lockfile to the integrator) and run it again; or
- run sequentially, naming the rule that failed and why the fix isn't worth it.

A finding is never left unmentioned, and parallel is never proposed over one.

**Propose a mode, with numbers.** Parallel is opted into at stop 2; it runs 3 lanes by default, 4 at most.
- **Parallel pays** when the graph is wide (around 6 or more tasks, at least 3 ready at once after the foundations), the shared surface is frozen in T1, tasks are similar in size, and implementation time dominates each task.
- **Sequential is faster** for a chain of dependent steps, 4 tasks or fewer, tightly coupled UI, contracts still in flux, mostly shared files, heavy per-lane environments, a build that will hit the usage limit anyway, or a project that forbids extra worktrees.
- **3 tasks or fewer in sequence:** `Mode: inline`. The orchestrator builds them itself and one reviewer checks the whole diff at the end ([build](../build/SKILL.md), Execution mode). One line under `## Execution` is enough. Propose subagent mode only for a reason: a task needing a different model, a large diff, or Saad asking for it.
- **4 tasks or so, in a chain:** sequential, and one line why.
- **Otherwise, give the numbers:** lanes per wave; the task count against the wave count; a rough time for each mode (sequential ≈ tasks × per-task time; parallel ≈ per wave, the slowest task plus the merge and wave check); and the saving. A well-split plan gets roughly 1.5–2.5x on the build stage, a chain about 1x. Parallel uses roughly 10–30% more tokens and drains the usage window as many times faster as it has lanes. If the build clearly won't fit one usage window, say so.

**Checkpoints** go in the plan only where Saad asked for one, at the point he named, with his words quoted. Otherwise write "Checkpoints: none". Don't add your own.

## Self-review

When the plan is written, reread the spec with fresh eyes and check the plan against it yourself, not through a subagent. Fix what you find inline.

1. **Spec coverage:** every live S-line has a task, and a test or a smoke path, or a stated reason why not. If an S-line has no task, add the task.
2. **No piece without an S-line:** every row, new file and option traces to one.
3. **Step scan:** each step lets the implementer write exactly one reasonable thing. A line that decides nothing is a gap; a body the signature and tests already determine is a transcript.
4. **Interface consistency:** names, signatures and types used in later tasks match what earlier tasks produce. `clearLayers()` in T3 against `clearFullLayers()` in T7 is a bug.
5. **Review focus:** for each failure mode the spec implies, some task's tests exercise it, or it's listed with its test added.
6. **Tables parse:** headings and columns as in the template, Writes backticked, waves integers.
7. **Proportion:** a plan several times longer than its spec, or mostly code blocks, is a transcript: replace bodies with signatures, test names and assertions, keeping each step unambiguous.

Then create `progress.md` in the topic folder, or bring its `## Tasks` list in line with the task table (format in formats.md): stage `plan`, the wave count, every task as `- [ ] T<n> <title>`. Redo this whenever the plan changes.

## Stop 2

1. `anvil plan-check` is clean, or every finding is answered under `## Execution`.
2. `anvil present plan`. It records the plan's hash; any later edit means presenting again.
3. Show Saad, briefly, in plain words (the ids stay in the document):
   - the plan's path;
   - the tasks and waves, and the proposed mode with its numbers (or the reason for sequential);
   - the test list by type, which he is approving too;
   - the synced branch and the commit points, including which ones push;
   - anything that needs his call: `main`/`master` consent, a checkpoint he mentioned, a decision the spec left waiting on him;
   - the calls you made, numbered, each with what it costs to reverse. Unstated restrictions (a rejected value, exclusive options) belong here.
4. End your turn and wait. Only Saad passes this stop.

**On his reply:**
- **He approves:** `anvil approve plan --quote "<his words>"`, quoting 3+ words of his message, or all of a shorter one. If his reply picks the mode, approve first, then write his choice under `## Execution`; otherwise the proposed mode stands.
- **He approves and dictates edits** ("approved, one fix: `--top 0` prints nothing"): approve first with his words, then make exactly those edits (the spec part's lines retire and renumber as usual), log them in the change log as his, and rerun `anvil plan-check`. No second stop. If you already edited before approving, use `anvil approve plan --amended --quote "<his words>"`.
- **He asks for changes without approving,** or the edits he asks for need new design: make them, run `anvil plan-check` again, present again, and stop again.
- **The approve is refused:** say why in one line. Never retry with words he didn't type.

**Pre-approval and AFK.** If Saad pre-approved the plan in his own words ("go straight to the build", "don't stop for the plan"), run `anvil approve plan --quote "<his words>" --pre` (3+ words of his message). If AFK is on, run `anvil approve plan --afk --quote "<his AFK words>"`. Either way, skip steps 2–4 of stop 2 (no present, no wait), and the plan stage runs with AFK decision-making: the calls he would have made at the stop (mode, synced branch, commit pushes) are made on his behalf, and each goes into the progress decision log in the formats.md entry shape (choice, reason, confidence, changes if). `main` or `master` still isn't chosen without his explicit consent; pick a new branch instead.

**Revising before the build.** To redo an approved plan before the build starts, set `- **Approved:** no`, change it, rerun `anvil plan-check` and present again. Once the build runs, changes go through its change flow-back.

## After approval

If the repo has a tracker, run `anvil:ticket-update` to split the plan's tasks into tickets.

If Saad pre-approved the plan or AFK is on, go straight on to `anvil:build`: the build runs in subagents, which already have fresh context. Otherwise offer a fresh session, because old context pulls the build back toward old code, using the plan's actual path:

> Plan approved. To build in a fresh session: `/clear`, then `/anvil:build <plan path>`. Or I can continue with the build here.

If he chooses to continue, go on to `anvil:build`.
