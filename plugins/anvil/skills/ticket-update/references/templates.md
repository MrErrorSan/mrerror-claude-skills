# Ticket and comment templates

Replace everything in `<angle brackets>`. Delete a section only when it
genuinely doesn't apply. Never write "N/A" in its place. Use the tracker's
collapsible syntax for Agent notes (see trackers.md); `+++` below is Linear's.

## Contents
1. Short ticket
2. Implementation ticket
3. Feature or stream parent
4. Research or decision ticket
5. Comments
6. Before and after

---

## 1. Short ticket (small tasks, fixes and backlog)

Use it when the work is small or not planned yet, and an agent doesn't need a
scope fence.

```markdown
**Done when:** <one specific, checkable sentence>

<One or two lines of context: why this matters now.>
Source: <spec §, review item, audit id, root-cause id, or the issue it came from>

Blocked by <ID>. Blocks <ID>.

+++ Agent notes
<File paths, a reproduction, log excerpts. Only when needed.>
+++
```

## 2. Implementation ticket (code an agent will build)

Title: `<Feature> <n>: <outcome>`, for example
`Decision Engine 2: schema and catalogue`.

```markdown
**Done when:** <one-line summary of the finish line>

## Goal
<One or two sentences: the state after this ticket, not the activity. Spec reference.>

## In scope
- <Thing to build>, per `<doc path> §<section>`
- <Name the exact routes, functions, CLI commands, flags, config keys and error names. No code.>

## Not in scope
- <Item a builder might reasonably add>: owned by <sibling ticket, e.g. "child 9" or ID>
- <Another item>: <owner, or "not planned">

## Done when
- <Test scenario as a case: input → expected result>
- <Test scenario: e.g. "two concurrent number requests on one prefix get consecutive, different numbers">
- `<gate command>` green (e.g. `make check`, `uv run poe check`)
- <Measured bar, if any: e.g. "eval recall ≥ 0.85 on the 40-question set">

## Dependencies
Blocked by <child N / ID>. Blocks <child M / ID>.

+++ Agent notes
<Files to touch, code to reuse, traps found while planning.>
+++
```

## 3. Feature or stream parent

There is no estimate. The due date equals the last child's. When a new module
is introduced, add a `## Placement` section that says where the code lives and
cites the rule that decides it.

```markdown
**Done when:** <one observable end-to-end outcome>, and children <ID-a> to <ID-b> are done (<N> points).

## Goal
<One paragraph: what the user gets when this exists, and why.>

## Read first
1. `<spec file>` (source of truth), especially §<x>
2. `<decision record>`
3. `<repo rule file> §<y>`

## Phases
- Phase 1, <name>: children 1–3
- Phase 2, <name>: children 4–6. Phases 1 and 2 never depend on phase 3.

## Children, in order
1. <ID>: <title>
2. <ID>: <title> (2 and 4 can run side by side once 1 is done)
3. ...
Outside this feature, blocking it: <ID>

## Not in scope
- <Item>: <where it lives instead>

## Done when
<The end-to-end scenario someone could demonstrate: real roles, real data, and the result. Not only "all children done".>
```

## 4. Research or decision ticket

```markdown
**Done when:** <the decision is made, or the document exists at <path>>

## Objective
## Deliverables
## Results
## Limitations and risks
## Next steps
## Decisions needed
- [ ] <Decision>: options A and B, recommendation <A> because <reason>
```

---

## 5. Comments

**Approval** (on the parent for feature-level decisions, before building):
```
Spec approved (2026-11-19) by <name>: <what, with the doc version or section>.
```
```
Placement approved (2026-11-19), per `ENGINEERING.md` §2: <module> goes in <package>, because <reason>.
```

**Progress** (at a stop point):
```
2026-11-19: <what is done, concretely>. Next: <next step>. Blocker: <none | what, and who can clear it, with a mention>.
```

**Completion** (before moving to Done):
```
Done (2026-11-19).
- Built: <what>, in <PR #N / commit sha / branch>. Migration: <name, if any>.
- Change from spec: <none | what changed and why>. The spec was updated in the same change.
- Checks: <command> green; <N> tests pass, including <named scenario>; <measured figure>.
- Left: <none | what is still open, and where it is tracked>.
```

**Feature closing** (on the parent):
```
Merged as PR #<N>, deployed to <env> on 2026-11-19. Hand test: <real scenario with real names> gave <result>. Still switched on: <flags or none>.
```

**Deferred or cancelled:**
```
Cancelled (2026-11-19): <reason>. The work was folded into <ID / child N>.
```

---

## 6. Before and after

**Before** (a common pattern on boards. Don't copy it):
> **Title:** Access control improvements (wave 2)
> No estimate, no due date, no labels, unassigned. The body is three screens
> that restate the design. The last line is "Done when it works".

**After:**
> **Title:** `Access control 3: route-level access checks`, estimate 2, due
> 2026-11-20, labels `Backend` and `Security`, priority High, parent the
> Access control feature.
>
> **Done when:** all 9 project routes refuse a user without the project role,
> and `make check` is green.
>
> **Goal:** every project route checks the caller's role before running, per
> `access_control/architecture.md § Core's access hook`.
> **In scope:** the `require_project_role()` dependency on the 9 routes listed
> in the spec, and the `ACCESS_DENIED` error code.
> **Not in scope:** filtering lists and totals by role (child 4), and the admin
> screens (child 6).
> **Done when:** a viewer calling `POST /projects/{id}/letters` gets a 403
> `ACCESS_DENIED`. An owner gets a 201. One test per route. `make check` and
> `make test` are green.
> **Dependencies:** blocked by child 2, blocks child 4. Both links are set.
