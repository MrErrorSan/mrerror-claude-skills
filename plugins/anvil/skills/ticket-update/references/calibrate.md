# Calibrate: learn the team's ticket style

Use this when you first set up a repo for a team that already has tickets, or
when the user says "study the team's tickets" or "make our tickets look like
X's". The aim is to copy what already works on this team, add the team lead's
required fields on top, and write the result down once so that every later
session follows it.

## 1. Choose the sample

- Ask whose tickets or which features count as good, if the user hasn't said.
  Usually that's a strong author or two or three well-run features.
- **Watch for borrowed identities.** If the tracker connection is signed in as
  the team lead, "created by <lead>" also returns tickets the agent made for
  the user. Filter those out by title prefix, assignee or date before you count
  anything.
- Read **metadata for every ticket** in the sample: title, status, parent,
  labels, estimate, due date, priority and assignee. Page through all results.
- Read the **full text of a few tickets from each stream**: one feature
  ticket, one or two children, and one research ticket if there is one. Also
  read **the comments** on a finished feature, because the approval and
  completion habits are there.

## 2. Measure the gaps

Make one table, for example:

| | Count (of N) |
|---|---|
| Have a parent | |
| Have labels | |
| Have an estimate | |
| Have a due date | |
| Have a priority | |
| Unassigned | |
| Larger than 3 days | |
| Title styles in use | |

The numbers tell you what to fix. The full-text reading tells you what to keep.

## 3. Pull out the pattern

Check each of these points against the sample, and note an example ticket id for
each one you see:

1. One body skeleton for leaf tickets and one for features.
2. The spec is the source of truth, and the ticket points to its sections.
3. "Done when" is checkable: named tests, commands, an end-to-end scenario.
4. "Not in scope" is always there, and it names the sibling that owns each item.
5. The order is explicit: numbered titles, real blocking links, and which
   children run side by side.
6. Decisions are recorded as dated comments before building.
7. Completion comments record where the work went, any change from the spec,
   the checks run, and the deploy or hand test.
8. Deferred or cancelled work says why.

Also list **what not to copy**, usually work that predates the team lead's
rules: tickets with no estimate, oversized "wave" tickets, unassigned children,
missing labels, several title styles, and bodies that run for screens.

## 4. Write it down

- **A patterns doc**, dated: `docs/<YYYY-MM-DD>-ticket-patterns.md` (or
  `.local.md` if it names people and shouldn't be shared). It covers what was
  read, the numbers, the pattern with example ids, what not to copy, and what
  was changed.
- **The rules:** update the profile (`.claude/ticketing.md`) with anything
  specific to this team, such as the title style, label set, gate commands and
  approval habit. Or, if the repo keeps rules in `.claude/rules/`, write a rule
  file there and link it from `CLAUDE.md`. Each piece of information gets one
  home; the other file links to it.

## 5. Optionally rewrite the user's own tickets

Offer to bring the user's open tickets into the pattern. **Show the list and
get a yes first**, because this edits many tickets at once. Rewrite only the
user's tickets (SKILL.md section 4). Scheduled tickets get the full form.
Backlog tickets get an estimate and a "Done when" line until they are
scheduled. Record what you changed in the patterns doc.
