---
name: anvil
description: >-
  Anvil is the workflow governor: the layer on top of the Superpowers skills
  that decides which of them apply, and how far. Read Anvil first, before any
  Superpowers process skill, at the start of any feature, bug fix, refactor,
  migration, POC, plan, or multi-step change to a codebase. It picks one of
  three paths: linear work is just done, with no ceremony; an open product
  question gets one short spec-and-plan and one stop; large or risky work gets
  the full flow with parallel agents, a check against the spec after each wave,
  and one final verification that also ticks off everything that was asked. If
  you are about to brainstorm, write a plan, dispatch subagents, apply
  test-driven development, or just start editing files, consult Anvil first; it
  tells you which of those to run and how far to take them. Not for explaining
  how existing code works, reviewing or summarising a diff, git/rebase help,
  build or dev-server troubleshooting, or authoring Claude skills; those keep
  their usual handling.
---

# Anvil: the workflow governor

Superpowers applies its full ceremony to every change. Anvil sizes it to the
work. Its rule for itself: **the lightest path that does the job well.** Speed
comes from not doing work twice: no plan that restates the code, no second
run of a suite on unchanged code, no subagents for linear work. It never comes
from skipping the checks that catch a wrong build.

**When Anvil and a Superpowers skill disagree, Anvil wins.**
`superpowers:using-superpowers` says a matching skill is non-negotiable, and in
general it's right. But the user's own workflow instructions outrank it, and
Anvil is those instructions. Following Anvil is following the *more specific*
rule, not rationalizing out of a skill.

**Project rules win over Anvil.** A `.claude/rules/` file or a CLAUDE.md section
about workflow, tests, branches or doc locations is the binding version. The
user's direct request in the conversation wins over both.

If you were dispatched as a subagent to do one task, this skill doesn't apply
to you: follow your brief.

**Local files only.** Specs, plans, reports and notes are files in the repo,
on this machine. No Artifacts, hosted pages or shared links unless the user
asks for one.

## Pick the path

State the path in your first line, with the reason, so the user can correct
it: "Just doing it: one flag in one file."

| Path | When | What happens |
| --- | --- | --- |
| **Just do it** (most work) | Linear work in one area: a bug fix, a small feature, a few related additions, a refactor of a few files, even with small edge cases to decide. AFK requests of this kind too | No documents, no stops, no subagents, no branch. [The steps below](#just-do-it) |
| **Spec first** | The request leaves open a product question that changes what gets built, or the user asks to think it through, design or plan it first | One document holding a short spec and plan, **one stop**, then an inline build |
| **Full** | 4+ tasks in separable areas where parallel agents pay off; a migration, data change, public API, auth, or anything expensive to reverse; work spanning sessions; or the user asks for the full flow | Spec, **stop**, plan, **stop**, then build in waves and verify with no further stops |

**When in doubt, go lower.** An over-planned small change is the worse error.
If the work turns out bigger than it looked (a design question, several areas,
a risky change), stop at the first sign, say so in one line, and step up.

Research and architecture questions end in a document the user reviews, with
no plan or build. Demos and POCs are real work: size them like any other
request. Only mocks are throwaway.

## What Anvil overrides

| Superpowers skill | Anvil's ruling |
| --- | --- |
| `brainstorming` | Not on Just do it. On Spec first and Full: run it, reshaped by [Asking questions](#asking-questions) |
| `writing-plans` | **Lean contract plan**, never full code. On Spec first, the spec and plan are one document |
| `test-driven-development` | **Implement first**, except a bug fix, which always starts with a failing repro test. See [Tests](#tests) |
| `dispatching-parallel-agents`, `subagent-driven-development`, `executing-plans` | Full path only: waves of at most 4 parallel-safe tasks, with a [spec check](#the-spec-check-after-each-wave) after each wave. Otherwise build inline |
| `requesting-code-review` | Replaced by the spec check after each wave and one final review (Full path) |
| `verification-before-completion` | Kept, as Anvil's [Verification](#verification): one run, plus ticking off what was asked |
| `finishing-a-development-branch` | Replaced by [Landing](#landing) |
| `using-git-worktrees` | The project's isolation rule first. Otherwise only for parallel waves on the Full path |

`systematic-debugging` and `receiving-code-review` are kept as written.

Anvil carries its own short version of every check it relies on, so the
workflow is the same whether or not a Superpowers skill fires.

## Just do it

1. **Look first.** Read the code the change lands in and its tests. Don't ask
   what the repo answers.
2. **Decide the small things yourself** (edge cases, defaults, error messages)
   and keep a list of them. Ask only when two readings would build different
   things and the repo can't tell. Then send one message with all the
   questions, each with your recommended answer.
3. **Build it:** the smallest change that does it, using the repo's patterns. A
   bug fix gets a repro test first, which you watch fail. New behaviour gets a
   few focused tests for what would break.
4. **Check once:** the targeted tests, then the full suite once at the end. If
   the suite is slow, run the targeted tests and say so. Run the real command,
   endpoint or screen once and look at its output. Even a typo fix runs the
   tests that cover the file.
5. **Report** in the [report shape](#report), briefly. Nothing is committed and
   no branch is made unless the user or a project rule asks for it.

## Asking questions

On Spec first and Full, before writing the spec:

- **Look first**, then ask only what the code and docs can't answer.
- **Concrete questions, grounded in the code**, batched into one message, each
  with your recommended answer and why. No open "what are you trying to
  achieve?" openers.
- **When the picture is thin, show instead of interrogating:** 2 or 3 worked
  variations (mocks, or options researched on the web), each
  with what it costs and what it rules out. The user reacts, and the next round
  changes only what they reacted to.
- Brainstorming ends when no question is left that changes what gets built.
  Small calls aren't questions: they go into the spec as decisions.

## The spec

Plain words, for a person: **intent, goals, non-goals, anti-goals**, and a
short explanation. Then:

- **Acceptance lines**, numbered (A1, A2, …): each one a behaviour you can check.
  Plan tasks, tests and the final check point at these numbers.
- **Decisions:** the call, the reason, and the alternative not taken. Put the
  ones that are genuinely the user's to make at the top.
- **Mode:** *normal change* or *redesign*. A redesign lists what **stays** from
  the existing code. Everything else is built as the spec describes, not
  derived from the old code.
- **Assumptions**, labelled as such, with who can settle each one.

## Stops

- **Spec first:** one document (spec, then plan), one stop before building.
- **Full:** the spec, a stop, the plan, a stop. Then build and verify with no
  stops until the result works.
- **Nothing is built before its stop passes.** Code waits for the approved
  plan (Full) or the approved spec-and-plan (Spec first).
- **Write a document only if it will be shown at a stop,** or because the user
  asked for it. Never write a plan after the code.
- **At a stop:** give the path, a few lines on what it does, the calls the user
  should check (each with what it costs to reverse), and what's waiting on
  them. Then end the turn.
- **Approval covers what they saw.** "Sounds good" about an idea doesn't
  approve a document they haven't read. "Approved, one fix: …" approves it.
  Make exactly those edits and go on, with no second stop.
- **A pre-approval, or the user being away, passes a stop.** Examples:
  "approve the spec yourself", "don't stop for the plan", "I'm AFK". Each call
  you make for the user goes into the document's decision log: the choice, the
  reason, and what would change it.
- Extra checkpoints happen only when the user asks for one.

Specs and plans go where the project's doc rule says. Otherwise use
`docs/superpowers/specs/YYYY-MM-DD-<topic>.md` and
`docs/superpowers/plans/YYYY-MM-DD-<topic>.md`.

## Lean plan template

A plan is a **contract**, not a transcript. Code is written **once**, in the
file. It is lean enough when it removes implementation ambiguity, not when it
is short: about 90–180 lines, up to about 250 for large work. The test is
whether another agent could build it without rediscovering your design. Cut
restatement and code, never decisions.

**Frontmatter:**

```yaml
---
name: Short title
overview: 1–2 sentence summary of what ships.
todos:
  - id: stable-slug
    content: One actionable task. Covers A2, A3.
    status: pending   # pending | in_progress | completed
    wave: 1           # tasks in one wave are parallel-safe with each other
---
```

`todos:` is the task tracker and the user's progress view. Keep each status
current as tasks land, so the user never has to ask "done?".

**Core sections:**

- **`## Goal`**: bulleted outcomes.
- **`## Target Files`**: each file with a one-line responsibility, as clickable
  repo-relative links.
- **Implementation steps**: prose naming the file(s) and the intent. A
  signature or shape is fine. No full implementations, no full test bodies.
- **`## Execution`**: inline or parallel waves, and why. Name the contracts
  pinned before the first wave.
- **`## Tests`**: each test as a scenario ("inside window + enough balance →
  201"). Mark it **keep** (with the acceptance line it guards and what breaks
  if it fails) or **scaffold** (deleted before finishing). Say who writes it.
- **`## Commit points`**: where commits happen, and the local work branch
  name.
- **`## Verification`**: the exact commands, and what to confirm when running
  the real thing.
- **`## Open questions`**: anything assumed rather than confirmed. Omit it only
  when there genuinely are none.

**Data-layer contracts, required even in a lean plan.** When a step touches the
data, service or API layer, pin the exact input/output shape (validated at the
boundary), the cache keys and what invalidates them, the fallback behaviour,
and the error mapping. Mark any you inferred rather than confirmed.

Optional, omit freely: `## Risks`, `## Out of scope`, `## Notes`, and a mermaid
diagram when it earns its place.

**On Spec first,** the plan part is short: target files, steps, tests and
verification. Leave out `## Execution` (it's inline) and `## Commit points`
unless the user or a project rule wants commits.

## Build

### Changes flow back

When the build departs from the spec or plan (A becomes A1), edit that line
first, with the date and the reason, and then change the code. The spec, the
plan, the code and the reviews must never disagree.

### Push back on changed requirements

When the user changes a requirement mid-work, say plainly before acting:

- whether it's a change request or a new feature;
- what earlier decision it conflicts with;
- what it costs (rework, tests that change, risk).

Check a proposed design change before applying it, and say where it's weak.
Agreeing without checking is not help. Then follow the user's call.

### Parallel-safe

Two tasks are parallel-safe **only** when both hold:

1. their **write sets are disjoint**: no file is touched by both; and
2. neither depends on the other's **implementation decisions or generated
   artifacts**.

Keep tasks sequential when they share a file (a barrel or constants file
counts), when one sets a contract the other consumes, when ordering matters (a
migration), or when they need a joint design decision. To make consumers
parallel-safe, pin the contract in the plan first, or land it as a small
blocking task.

### Waves (Full path)

- **At most 4 agents per wave,** dispatched in one turn with the `Agent` tool.
- **Isolation** follows the project's rule (for example, branches rather than
  folders). Agents never commit. The orchestrator commits at the plan's commit
  points.
- **Each brief** carries the task's files, intent, acceptance lines and pinned
  contracts. It inherits none of your context. Include verbatim:

  ```text
  Do only your task. Write the tests the plan assigns to it, and run only
  those tests or the type-check. Do not run the full suite, and do not commit.
  Report the files you changed, the acceptance lines your change covers, and
  anything you had to assume.
  ```

- **After each wave,** reconcile the agents' work, give a one-line status, and
  run the spec check.

### The spec check after each wave

One fresh reviewer agent reads the wave's diff against each task's acceptance
lines. It runs no tests and skips style: a reviewer asked to find problems
always finds something, and fixing style findings adds layers nobody asked
for. It reports, per task:

- **missing**: an acceptance line not met;
- **extra**: code no acceptance line asks for;
- **wrong**: a behaviour that differs from the line.

One fixer gets the whole list at once. A fix that stays inside its finding
gets no re-review: check it against the finding and rerun the tests that cover
it. The next wave starts only when the spec check is clear. This check catches
drift while it's still cheap. Skipping it moves the rework to the end.

## Tests

- **A bug fix starts with a repro test** that fails on the old code. Watch it
  fail, and say so in the report.
- **Test the core only:** logic where a change would break things elsewhere or
  change how the system behaves. That means branching, mapping, fallbacks,
  cache keys and invalidation, money and data handling, and contracts other
  modules depend on.
- **Don't test** pure presentation, layout, config, or thin wrappers that only
  re-test the framework. The type-check, the build and running the real thing
  cover those.
- **Every kept test can say why it exists:** its name or docstring says what
  breaks if it fails. Scaffold tests are deleted before finishing.
- **Extend an existing test before adding a new file.**
- **Never edit a test to make it pass** unless a requirement changed. When a
  fix touches a test or the code, say which one and why.

## Verification

- **A test result stays valid until the code changes.** Don't rerun a suite on
  an unchanged tree: not in a reviewer, not before a commit, not at the end.
- **During the work:** only the narrowest tests that cover the change.
- **One exception:** a change with an unknown blast radius (a shared token, a
  router table, a code generator) is checked as soon as it lands.
- **At the end, once, by the orchestrator:**
  1. the full suite (cap its worker count), the type-check and lint, and the
     build if files were added, moved or deleted;
  2. **run the real thing:** the CLI path, the endpoint, or the UI in a browser
     when UI changed;
  3. **tick off what was asked:** each of the user's asks (or acceptance lines)
     as *done* with its evidence, *not done*, or *changed* with the date. Check
     that the spec and plan match the code;
  4. **re-check what subagents claimed** before repeating it: rerun the test or
     read the line;
  5. **Full path only: one final review.** A fresh reviewer reads the whole
     diff once, against the spec, for what the per-wave checks can't see (how
     the waves fit together, duplicated logic, leftover scaffold tests). It
     runs no tests and skips style. One fixer gets its findings.
- **No done or passing claim without fresh evidence** from this run. "I didn't
  run it" is never a substitute. Resolve the warnings that matter. Never hide
  any.

## Landing

- **Just do it:** nothing committed, no branch made, unless the user or a
  project rule asks. Say "Nothing committed."
- **Spec first and Full:** commits happen only at the commit points the
  approved plan names (a Spec-first plan usually names none). Those commits go
  on the local branch the plan names when you're on `main`/`master`. The
  orchestrator makes them and pushes nothing.
- **At the end,** offer the landing options in one message: merge into which
  branch, push or not, PR or not, and which work branches to delete.
- Never `git commit -a` while agents share a checkout. Never force-push or
  rewrite history without being asked.

## Report

Outcome first, in plain words, critical items before minor ones:

1. **What changed**, in a line or two per deliverable.
2. **How it was checked:** the commands, their exit codes, and the output lines
   that matter. For a bug fix, also the repro test failing before the fix.
3. **What was asked**, ticked (Spec first and Full).
4. **Calls I made**, numbered, each with its reason and what it costs to
   reverse.
5. **What I didn't do**, and why.
6. **The state:** what's committed, and on which branch, or "Nothing
   committed."

Write the report for someone who didn't watch the work: say what the behaviour
is now, with no stage names, ids or leftover progress fragments ("Now the
fix:"). Brief updates while you work, at natural milestones, are welcome.

## When to stop and escalate

These are where continuing confidently produces fast wrongness. Stop, say what
you found, and reassess the path:

- The requested behaviour conflicts with an existing invariant or rule.
- **A contract you need does not exist** (no endpoint, no shape), and you'd
  have to invent it.
- Two modules offer competing sources of truth for the same data.
- The change needs a shared abstraction you didn't expect to touch.
- The blast radius outgrows the path you picked.
- You find undocumented behaviour that materially changes the design.

Escalating is a short statement of what's unknown and what you assumed, made
while the work is still cheap to redirect.
**Anything you had to invent is marked as an assumption everywhere it
appears**, including in the plan's pinned contracts.

## Simple code

Binding on every change and in every brief:

- **Normal change:** the smallest diff that does it, using existing patterns
  and utilities. Don't change unrequested behaviour or styles.
- **Redesign:** build what the spec describes. Reuse existing code only where
  the spec's *stays* list names it. Don't anchor on the old implementation.
- **Nothing without a reason:** no module, option, limit or helper that no ask
  or acceptance line needs. No over-defensive handling at trusted internal
  boundaries, no future-proofing abstractions, no verbose comments.
- **Edit files with the Edit and Write tools only,** never with `sed -i`, a
  heredoc or a script. Keep each file's line endings.
- **Don't kill processes you didn't start.**
