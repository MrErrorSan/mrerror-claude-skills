<!-- adapted from superpowers@7.0.2: skills/writing-plans/SKILL.md -->
# Plan template

The shape of `plan.md`. The header lines, S-lines and the three tables (task table, test list, commit points) are the pinned formats in [formats.md](../../../references/formats.md): `bin/anvil` parses them, so keep the column names, column order and section headings exactly as shown. Everything in `<angle brackets>` is filled in; drop any line that doesn't apply rather than writing "none" everywhere. Two exceptions stay even when empty, because they record that you checked: the `**Checkpoints:** none` line, and the `## Review focus` heading (write "None found." under it).

The examples use one language (TypeScript) and put every test file inside its owning task's Writes, so a plan copied from them passes `anvil lane-check`.

Parser facts worth knowing:
- Header lines are the `- **Key:** value` bullets above the first `## ` heading.
- Each table is the first table under its `## ` heading, so put prose for that section before or after the table, never a second table before it.
- A table cell that needs a literal `|` writes it as `\|`.
- Any line starting `- **S<number>**` outside a code fence counts as an S-line. Only the spec part writes those.

## Full size (spec in its own `spec.md`)

````markdown
# <Topic>: plan

- **Status:** draft
- **Approved:** no
- **Size:** full
- **Synced branch:** <branch> (local)
- **Spec:** [spec.md](spec.md), <its Approved value>
- **Work branch:** `anvil/<slug>/work` (local)

> **For agentic workers:**
> - Read your task's section, the S-lines it names, and the Global constraints. Nothing else in this plan is yours to change.
> - Write only the files in your task's Writes cell. A file outside it means stop and report, not reach across.
> - Run only your task's targeted tests, never the full suite.
> - Your report states, for each test you touched, whether **the test changed or the code changed**, and which S-line allows it.

**Goal:** <one sentence: what this builds>

**Architecture:** <two or three sentences: the approach, and where the pieces sit>

**Tech stack:** <languages, libraries, test runner>

## Global constraints

Each line is copied from the spec, with its exact values.

- <version floor, dependency limit, naming or copy rule, platform requirement>
- **Mode:** <normal: smallest diff using existing patterns | redesign: build what the spec describes; reuse only the spec's stays list>

## Review focus

Failure modes the spec implies but no task's tests would otherwise exercise, most likely first. Each has a test in the owning task.

1. **<input or condition>.** <what a reasonable person expects>. Covered by T<n> (`<test name>`).

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1, S4 | `<src/shared/types.ts>`, `<src/shared/types.test.ts>`, `<src/routes.ts>` | - | - | 0 | yes |
| T2 | S2 | `<src/area/**>` | - | T1 | 1 | yes |
| T3 | S3, S5 | `<src/other/**>` | port:5173 | T1 | 1 | yes |
| T4 | S6 | `<config/x.json>` | - | T1 | 1 | skip (fully specified) |

**Integrator-only** (the orchestrator, not a lane): <lockfile regeneration, codegen, migrations, merges, commit points>.

## Test strategy

Full suite: `<command>`, about <duration> (<measured from a recorded run | from CI | not measured>). <It runs once on the final state | It also runs after each wave, being under about 2 minutes.>

Type-check: <command | none>

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `<src/shared/types.test.ts>` | keep | S1 | <what a later task loses> | T1 |
| `<src/area/a.test.ts>` | keep | S2 | <what a user loses> | T2 |
| `<src/other/issue.test.ts>` | repro | S3 | <the reported bug comes back> | T3 |
| smoke: <start the app, do the main path, see the result> | smoke | S2, S3 | <the whole path> | T3 |
| `<src/area/fixtures.ts>` | scaffold | - | - | T2 |

<If a kind of work goes over its test budget, one line on why.>

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | waves 0–1 (T1, T2, T3, T4) | `<type(scope): summary>` | yes |

Each commit point squashes the work branch onto the synced branch, per [git-flow](../../../references/git-flow.md).

## Execution

`anvil plan-check`: <clean: "parallel-safe: 4 tasks in 2 waves" | findings, each with what was done about it>

| Wave | Lanes | Tasks |
|---|---|---|
| 0 | 1 | T1 (foundations, alone) |
| 1 | 3 | T2, T3, T4 |

- **Proposed mode:** <parallel, 3 lanes | sequential>, because <the reason in one sentence>.
- **Numbers:** <n> tasks in <m> waves instead of <n> one-at-a-time tasks. At about <x> min per task with review, about <a> h sequential against about <b> h parallel (roughly <a/b>x on the build stage). Parallel uses about 10–30% more tokens and drains the usage window about <lanes>x faster.
- **Sequential, if chosen:** <the failed plan-check rule or the shape that makes it slower, in one sentence>.
- **Checkpoints:** <none | after <named point> ("<Saad's words asking for it>")>

---

## T1: <foundations: shared types, routes and contracts>

- **Spec:** S1, S4
- **Files:**
  - Create: `<src/shared/types.ts>`, `<src/shared/types.test.ts>`
  - Modify: `<src/routes.ts:120-145>`
- **Interfaces:**
  - Consumes: <nothing | exact names and signatures from earlier tasks>
  - Produces: `<name(param: Type) -> Return>` in `<file>`; <every name a later task uses>
- **Tests:** `<src/shared/types.test.ts>` (keep, S1): asserts <the spec's exact values>. Targeted: `anvil run --scope targeted -- <cmd>`
- **Steps:**
  1. <Create `<file>` with `<signature>`. One line on the approach only where the signature and test leave a choice.>
  2. <Write `<test name>` asserting <values>.>
  3. <Run the targeted tests.>

## T3: <a bug fix>

- **Spec:** S3
- **Files:** Modify: `<src/other/x.ts>`; Test: `<src/other/issue.test.ts>`
- **Interfaces:** Consumes: `<name>` from T1. Produces: nothing new.
- **Tests:** `<src/other/issue.test.ts>` (repro, S3). Targeted: `anvil run --scope targeted -- <cmd>`
- **Steps:**
  1. Write `<src/other/issue.test.ts>` reproducing <the bug>; it fails for <the stated reason>.
  2. <Fix in `<function>`: one line on the approach.>
  3. Run the targeted tests; the repro passes and stays as a keep test.
````

## Direct size (spec part on top of the same `plan.md`)

Brainstorm writes the spec part, in the shape given by the direct-size section of [spec-template.md](../../brainstorm/references/spec-template.md); that file owns it. This skill adds the plan part underneath, in the same file, plus the `Synced branch` header line. There is one stop, at the plan. The skeleton below shows only where the spec part sits.

````markdown
# <Topic>: plan

- **Status:** draft
- **Approved:** no
- **Mode:** normal
- **Size:** direct
- **Synced branch:** <branch> (remote origin/<branch>)

<the rest of the spec part, as brainstorm wrote it>

## Spec lines

- **S1** <one behavior, one line>

<the rest of the spec part>

---

## Global constraints

- **Mode:** normal: smallest diff using existing patterns

## Review focus

None found.

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1 | `<src/area/a.ts>`, `<src/area/a.test.ts>` | - | - | 1 | yes |

## Test strategy

Full suite: `<command>`, about <duration>.

Type-check: <command | none>

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `<src/area/a.test.ts>` | repro | S1 | <the bug comes back> | T1 |

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | wave 1 (T1) | `<fix(scope): summary>` | yes |

## Execution

`anvil plan-check`: <result>.

- **Proposed mode:** sequential, because the plan has <n> tasks; lanes and merges cost more than they save at this size.
- **Checkpoints:** none

## T1: <title>

<Same per-task shape as the full-size template.>
````

A single-task or sequential plan with an empty shared surface has no foundations task, so its tasks start at wave 1: plan-check treats a wave-0 task with no dependents as a mistake.
