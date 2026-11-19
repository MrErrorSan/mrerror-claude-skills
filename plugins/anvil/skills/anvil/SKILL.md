---
name: anvil
description: >-
  Use at the start of any feature, bug fix, refactor, migration, POC, research,
  architecture or mock request in a codebase, or any other change to the code,
  to pick the path: most linear work is done directly with no Anvil ceremony;
  Anvil's spec and plan flow is for open product questions, and its full
  parallel flow for large work. Also use when Saad picks up earlier Anvil work
  or asks which stage comes next. Not for explaining how existing code works,
  reviewing or summarising a diff, git and rebase help, build or dev-server
  troubleshooting, or authoring Claude skills; those keep their usual handling.
---
<!-- adapted from superpowers@7.0.2: skills/using-superpowers/SKILL.md -->

# Anvil

Anvil is Saad's development workflow. Its rule for itself: **the lightest path that does the job well.** On linear work the model needs no workflow, and every layer added there is pure cost: a 14-line flag done plainly took 75 s, and through the full flow 330 s, with the same result. So most work takes the first path below, and Anvil stays out of the way. The stops, documents, CLI gates and parallel lanes are for the work that needs them.

If you were dispatched as a subagent to do one task, this skill doesn't apply to you: follow your brief.

## Pick the path

State it in your first line, with the reason, so Saad can correct it: "Just doing it: one flag in one file." **When in doubt, go lower.** An over-planned small change is the worse error.

| Path | When | What happens |
|---|---|---|
| **Just do it** (most work) | Linear work in one area: a bug fix, a small feature, a few related additions, a refactor of a few files, even with small edge cases to decide. Also AFK requests of this kind | No topic, no documents, no stops, no subagents. The steps below |
| **Spec first** (`--size direct`) | The request leaves open a product question that changes what gets built, or Saad asks to think it through, design, spec or plan it first | One `plan.md` holding a short spec and plan, one stop, an inline build ([brainstorm](../brainstorm/SKILL.md), fast path) |
| **Full** (`--size full`) | Large work: 4+ tasks in separable areas where parallel lanes pay; a migration, data change, public API, auth or anything expensive to reverse; work spanning sessions; or Saad asks for the full flow | `spec.md` and `plan.md`, two stops, build in waves with reviews, verify |

### Just do it

1. **Look first.** Read the code the change lands in and its tests. Don't ask what the repo answers.
2. **Decide the small things yourself** (edge cases, defaults, error messages), and keep a list of them. Ask only when two readings would build different things and the repo can't tell; then one message with all the questions, each with your recommended answer.
3. **Build it:** the smallest change that does it, using the repo's patterns. Edit with the Edit and Write tools; keep each file's line endings. A bug fix gets a repro test first, which you watch fail; new behaviour gets a few focused tests for what would break. No test bloat.
4. **Check once:** the targeted tests, then the full suite once at the end (if it's slow, the targeted tests and say so). Run the real command or CLI path once and look at its output.
5. **Report**, briefly:
   - what changed, in a line or two;
   - how it was checked: the commands, with exit codes and the output lines that matter;
   - **calls I made**, numbered, each with what it costs to reverse;
   - the state: "Nothing committed." (or what was committed, if the project's rules or Saad asked for it). No co-author trailer, ever.

If the work turns out bigger than it looked (a design question, several areas, a risky change), stop at the first sign, say so in one line, and step up to the right path.

### Spec first and Full

For either: `anvil topic start <slug> --size <direct|full> [--dir <project's doc location>]`, then `anvil:brainstorm`. Pass `--dir` when the project's doc rule names a location.

**An active topic.** Check `anvil topic show` first. A message about the active topic at stage build or verify is a change request: it goes to `anvil:build`'s change flow-back, not a new `topic start`. For unrelated work, `topic start` is refused while a topic is active: tell Saad and offer to park it with `anvil topic end` (its documents stay; `topic start` with its slug resumes it). In AFK, park it and log the decision. Research needs no parking: edits under `docs/research/` are never held.

If the work grows mid-way, say so and step up: rerun `anvil topic start <slug> --size full` (the folder is kept). Going from direct to full, move the spec part of `plan.md` into a new `spec.md`. If the plan was already approved, the new `spec.md` passes stop 1 (`anvil present spec`, Saad's reply, `anvil approve spec`) before the build goes on.

Demos and POCs go through the flow, sized like any other work; only mocks are throwaway.

**Research and architecture questions** end in a document Saad reviews, with no plan or build. Look first, ask one round of questions the way `anvil:brainstorm` does, then write `docs/research/YYYY-MM-DD-<topic>.md` and give him the path. Building on it afterwards is a new request.

## The flow

```
request ─ just do it? ─► build, check once, report
   ▼
brainstorm ─► spec ─[stop 1]─► plan ─[stop 2]─► build ─► verify ─► finish
          (spec first: one plan.md, one stop)
```

| Stage | Skill | Ends with |
|---|---|---|
| brainstorm and spec | `anvil:brainstorm` | full: stop 1; direct: hands to `anvil:plan` in the same document |
| plan | `anvil:plan` | stop 2, then a fresh session or straight on |
| build | `anvil:build` | every task `[x]` in `progress.md` |
| verify | `anvil:verify` | the converge check, the last commit point landed on the synced branch, the report |
| finish | `anvil:finish` | optional, Saad runs it: pushes or merges beyond the plan, a PR, clean-up, `anvil topic end` |
| any stage | `anvil:debug` | a failure whose cause isn't obvious; then back to the stage |

## How a stop passes

1. Write the document, then run `anvil present spec` (or `plan`). Any edit after that needs another `present`.
2. Show Saad the path, a short summary and what's waiting on him. End the turn.
3. When he approves, run `anvil approve spec --quote "<his words>"` with three or more words from his reply, or his whole message. The CLI checks the quote against his recorded messages and writes the `Approved:` line. If he approves and dictates specific edits in the same reply ("approved, one fix: …"), make exactly those edits and run `anvil approve <doc> --amended --quote "<his words>"`: no second round. If he asks for changes without approving, or your edits go beyond what he dictated, make them, present again, and stop again.

Approval covers what he saw. "Sounds good" about an idea doesn't approve a document he hasn't read. Never write the `Approved:` line by hand; if `approve` refuses, tell him why.

**Pre-approval.** When Saad's own words already pass a stop ("approve the spec yourself", "go straight to the build"), run `anvil approve <doc> --quote "<his exact words>" --pre` instead of stopping. That stage then runs with AFK decision-making: each choice you make for him goes into `progress.md`'s decision log in the formats.md entry shape (choice, reason, confidence, changes if).

**AFK.** When his message says he's away ("AFK", "I'm going to bed", "don't ask me"), use `anvil:afk`. It turns AFK on with his quote, and each skipped stop is recorded with `anvil approve <doc> --quote "<the AFK quote>" --afk`.

## Simple code

These three lines hold in every stage ([simplicity.md](../../references/simplicity.md)):

- **Normal change:** the smallest diff that meets the spec lines, using existing patterns.
- **Redesign:** build what the spec describes. Existing code is reused only where the spec's *stays* list names it.
- **No piece without a spec line:** no abstraction, option or helper that no S-line needs.

The spec's `- **Mode:**` line says which of the first two applies.

## Project rules win

The project's `CLAUDE.md`, `.claude/rules/*` and doc-location rules override Anvil's defaults. Saad's direct requests override both.

## Talking to Saad

Plain words, outcome first. Ids like S3, T1 and C1 belong in the docs; in chat, say what the behaviour is. Keep stop messages short: the path, what it does, the calls he should check (each with what it costs to reverse), what's waiting on him. In the docs, address him as "you".

## Where files go

- Topic documents: `docs/<slug>/` holds `spec.md`, `plan.md` and `progress.md` (direct size: `plan.md` and `progress.md`). Formats: [formats.md](../../references/formats.md).
- Mocks: `<topic folder>/mocks/`, rounds `-r2`, `-r3`, ….
- Research: `docs/research/YYYY-MM-DD-<topic>.md`.
- Repos with `docs/superpowers/specs|plans` keep them: read those; new work goes to the default unless a project rule names a place.
- Status lives in `progress.md`, not in todo tools. Anvil's state is never committed.
- Edit docs and code with the Edit and Write tools only: never with a script (`python - <<EOF`, a shell heredoc, `sed -i`, `cat >>`). Scripts mangle Markdown, have emptied a spec before, and each costs a round trip to debug. Several changes to one file go in one Edit or one Write.

## The other skills

| Stage | Skill | Use |
|---|---|---|
| brainstorm | `anvil:ui-mockup` | the mock exploration loop (variants in parallel, then Saad's reaction) |
| brainstorm, spec | `anvil:cross-model` | research on big questions; review of decisions that are expensive to undo |
| plan approved | `anvil:ticket-update` | split plan tasks into tickets, if the project tracks work |
| build | `anvil:ticket-update`, `anvil:debug` | comments at real stops; failures with no obvious cause |
| verify | `anvil:ux-audit`, `anvil:cross-model` | any UI change, against the mock if one exists; a second model before done on large or hard-to-reverse changes |
| finish | `anvil:ticket-update` | the completion comment |
| any | `anvil:afk` | runs without stops and logs decisions |

## Alongside Superpowers

- With both installed, Anvil's stage skills take the place of Superpowers' brainstorming, writing-plans, executing-plans, subagent-driven-development, test-driven-development, requesting-code-review, verification-before-completion, finishing-a-development-branch and systematic-debugging for work in this flow. Superpowers' writing-skills and diagnosing-superpowers stay usable.
- Anvil only: turn Superpowers off with `enabledPlugins` (`false`). Superpowers only: `/plugin disable anvil`.

## The CLI

`anvil <subcommand> [--json]`: exit 0 ok, 1 refused (reason on stderr), 2 usage. If a bare `anvil` isn't found, use the absolute path the session-start note gives. `anvil topic show` says where the topic is; the full list is in [formats.md](../../references/formats.md).
