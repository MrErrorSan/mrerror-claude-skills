---
name: anvil
description: >-
  Use for any feature, bug fix, refactor, migration, POC, research, architecture
  or mock request in a codebase, or any other change to the code, however
  small, at the start of the work and before
  brainstorming, planning, dispatching agents or editing files. Also use when
  Saad picks up earlier Anvil work or asks which stage comes next. Not for
  explaining how existing code works, reviewing or summarising a diff, git and
  rebase help, build or dev-server troubleshooting, or authoring Claude skills;
  those keep their usual handling.
---
<!-- adapted from superpowers@7.0.2: skills/using-superpowers/SKILL.md -->

# Anvil

Anvil is Saad's development workflow: one flow, two stops where Saad approves the documents. A small CLI, `anvil`, keeps the gates and state on disk, so a stop passes only on words Saad typed.

If you were dispatched as a subagent to do one task, this skill doesn't apply to you: follow your brief.

## First line: the size

Pick the size from how Saad describes the work, and state it in the first line of your reply, with the reason, so he can correct it. For example: "Size: direct. A bug fix with a clear repro and no open questions."

| Size | When | Documents and stops |
|---|---|---|
| **Trivial** | a single-file change with no new behavior, or "just do it" | none: do it, run one check, report |
| **Direct** | a concrete instruction about the code, a bug fix or a small change, with no open questions and about 5 tasks or fewer | one merged spec-and-plan document (`plan.md`), one stop |
| **Full** | a new feature, a high-level change to a built feature, or anything with open questions | `spec.md` and `plan.md`, two stops |

For direct or full: `anvil topic start <slug> --size <size> [--dir <project's doc location>]`, then `anvil:brainstorm`. Pass `--dir` when the project's doc rule names a location.

**An active topic.** Check `anvil topic show` first. A message about the active topic at stage build or verify is a change request: it goes to `anvil:build`'s change flow-back, not a new `topic start`. For unrelated work, `topic start` is refused while a topic is active: tell Saad and offer to park it with `anvil topic end` (its documents stay; `topic start` with its slug resumes it). In AFK, park it and log the decision. Research needs no parking: edits under `docs/research/` are never held.

If the work grows mid-way, say so and step up: rerun `anvil topic start <slug> --size full` (the folder is kept). Going from direct to full, move the spec part of `plan.md` into a new `spec.md`. If the plan was already approved, the new `spec.md` passes stop 1 (`anvil present spec`, Saad's reply, `anvil approve spec`) before the build goes on.

Trivial's one check is the project's narrowest relevant check, run through `anvil run --scope targeted -- <cmd>` when it's a test command.

Demos and POCs go through the flow, sized like any other work; only mocks are throwaway.

**Research and architecture questions** end in a document Saad reviews, with no plan or build. Look first, ask one round of questions the way `anvil:brainstorm` does, then write `docs/research/YYYY-MM-DD-<topic>.md` and give him the path. Building on it afterwards is a new request.

## The flow

```
request ─ trivial? ─► do it, one check, report
   ▼
brainstorm ─► spec ─[stop 1]─► plan ─[stop 2]─► build ─► verify ─► finish
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
- Edit topic docs with the edit and write tools. Shell heredocs, `sed -i` and `cat >>` mangle Markdown and have emptied a spec before.

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
