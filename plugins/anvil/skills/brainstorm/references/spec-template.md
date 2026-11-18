<!-- adapted from superpowers@7.0.2: skills/brainstorming/SKILL.md -->

# Spec template

The spec is for a human: plain words, short sentences, no process jargon. The header lines and S-lines are parsed by `anvil`, so keep their exact form ([formats.md](../../../references/formats.md)):

- Header lines are `- **Key:** value` bullets **above the first `## ` heading**.
- An S-line starts its line with `- **S<n>**`. Don't start any other bullet that way (decisions use `D<n>`), and keep example S-lines out of the real spec.
- `- **Approved:** no` is the only approval value you write. `anvil approve` replaces it.

## Full size: `<topic dir>/spec.md`

```markdown
# <Topic>: spec

- **Status:** draft
- **Date:** 2026-11-18
- **Approved:** no
- **Mode:** normal
- **Size:** full
- **Reference:** [chosen mock](mocks/variant-b-r2.html)

## Waiting on you

**Q1 <short title>.** <What is open, and what the answer changes about what gets built.>
Recommended: <the answer, worded so "yes" accepts it>.

<At most three. With none open, write: "Nothing. Every other point is decided below.">

## Intent and why

<What this is, who it is for, and why now, in Saad's terms where he gave them.>

## Goals

- **Constraints:** <platform, performance, compatibility; or "none beyond the project's".>

## Non-goals

## Anti-goals

<What would make this a failure even if it technically works.>

## Spec lines

- **S1** <One observable behavior, one line.>
- **S2** <...>

## Shared surface

<The exact names more than one part touches: types, routes, API contracts,
events, files, config keys, ports, database tables. Write "none" if nothing
is shared.>

## Replaces / stays

<Redesign mode only; leave the section out in normal mode.>

- **Replaces:** <modules, files or behaviors this design replaces. They are designed from this spec; the old code is a reference only for what must keep working.>
- **Stays:** <code this design keeps and builds on. Reuse it and match its style.>
- **Must keep working:** <behaviors of the replaced code that survive, each one an S-line: S4, S5.>

## Left to the builder

<A few points you're leaving open on purpose, which the builder settles while planning: naming, internal structure, the order of work. Write "nothing" if none.>

## Decisions

- **D1 <the call>.** Why: <reason>. Not taken: <alternatives, and why not>. Status: decided by Saad.
- **D2 <the call>.** Why: <reason>. Not taken: <...>. Status: decided, Claude's call.
- **D3 <the call>.** Why: <reason>. Not taken: <...>. Status: waiting on Saad (Q1).

## Change log

- 2026-11-18 Created.
```

### Field notes

- **Mode** is `normal` or `redesign`. It decides which simplicity line applies, and whether **Replaces / stays** exists.
- **Reference** is a link to the chosen mock or other reference, or `none`.
- **Left to the builder** is what the builder check is told to skip. Keep it short; anything that changes what gets built belongs in a decision instead.
- **Spec lines** are numbered from S1 and never reused. A change gets a new number; the old line is kept, struck through:
  `- ~~**S3** Old behavior.~~ RETIRED → S7 (2026-11-20, CR: reason)`
- **Decisions** carry every point settled without Saad's explicit answer, so he reviews them here. Statuses: `decided by Saad`, `decided, Claude's call`, `decided, Claude's call (AFK)`, `waiting on Saad (Q<n>)`.
- **Change log** entries after "Created" say whether the change is a **change request** or a **new feature**, what earlier decision or S-line it conflicts with, and which S-lines were retired or added:
  `- 2026-11-20 **Change request:** the cursor moves to the end after a save. Conflicts with D2. S1 retired → S4.`

## Direct size: the spec part of `<topic dir>/plan.md`

The same sections, kept short, at the top of the plan. `anvil:plan` adds its header line (`- **Synced branch:** …`) and the plan sections below.

```markdown
# <Topic>: plan

- **Approved:** no
- **Mode:** normal
- **Size:** direct

## Spec

<Two or three sentences: what changes and why.>

## Spec lines

- **S1** <...>

## Shared surface

## Decisions

## Change log

- 2026-11-18 Created.
```

For a **bug fix**, the spec part is the bug, the expected behavior as S-lines, and the reproduction:

```markdown
## Spec

**Bug:** <what happens, where, since when if known.>
**Reproduce:** <steps or command; this becomes the repro test, written before the fix.>

## Spec lines

- **S1** <the expected behavior.>
```
