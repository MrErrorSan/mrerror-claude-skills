---
name: ticket-update
description: >-
  Keep the team's ticket tracker current while you work: Linear, Jira, GitHub
  Issues, GitLab, Azure DevOps, or whatever the project uses. It detects the
  tracker and asks when it is unsure. Use it at every stop point in a repo whose
  work is tracked: a task is finished, you are waiting on approval, review or
  input, you are blocked, or you are ending a turn that changed something. Also
  use it whenever the user asks to create, update, split, plan, close or comment
  on tickets, issues or stories ("update linear", "log this in jira", "make this
  week's tickets", "break this plan into tickets", "write my stand-up line"), or
  asks to study the team's tickets and set up ticket rules for a repo. It writes
  tickets an agent can build from (Goal, In scope, Not in scope, Done when,
  Dependencies), sets the fields the team lead requires, and records approvals,
  progress and completion evidence as comments. Skip it for a turn that only
  answers a question and changes nothing.
---

# Ticket updates

The tracker is how the team sees progress without asking. A good ticket is a
**contract**: an agent or a teammate can build from it, and a reviewer can check
it, without a meeting. A good ticket has six parts:

- **Outcome.** What the work achieves (Goal).
- **Boundary.** Where it stops (Not in scope).
- **Source.** The doc that holds the design. The ticket points into it.
- **Check.** How a reviewer knows it is done (Done when).
- **Order.** What it waits for and what waits for it (Dependencies).
- **Trail.** Comments that record decisions, progress and completion.

This skill covers how to find the tracker, when to update it, what every ticket
carries, and how to report back. Keep it light: about 30 minutes a week and a
few minutes a day. A simple, honest ticket is better than a detailed, late one.

## 1. Load the rules, in order of precedence

1. **The project's own rules win.** Look in `CLAUDE.md`, `CLAUDE.local.md`,
   `AGENTS.md`, `.claude/rules/*`, and any doc they point to about tickets.
   These often name the team, the project, the parent ticket, the assignee and
   the gate commands. Where they differ from this skill, follow them.
2. **The ticketing profile.** This is `.claude/ticketing.md` (shared with the
   team) and/or `.claude/ticketing.local.md` (this machine only: who "I" am,
   the assignee). The format is in
   [references/profile-template.md](references/profile-template.md).
3. **The defaults in this skill**, for anything the first two don't say.

If there are neither project rules nor a profile, run **Setup** (section 2) once
before the first update.

## 2. Find the tracker, and ask when you're not sure

Look for signals of which tracker the project uses. Detection details and
per-tracker mechanics are in [references/trackers.md](references/trackers.md).

- **Named in the rules or profile:** use it. You're done.
- **Tools in this session:** MCP tools for Linear, Jira/Atlassian, GitHub,
  GitLab, Azure DevOps, Shortcut, ClickUp, Asana and so on, or CLIs such as
  `gh`, `glab`, `az boards`, `jira` and `acli`.
- **Repo hints:** ticket ids in branch names and recent commits (`IND-123`,
  `PROJ-45`, `#123`, `AB#123`), the git remote host, and links in docs.

**Decide:**

- **One tracker has both a usage signal and a working tool:** use it, and say
  so in one line.
- **Anything else:** ask the user with the options you found. That covers two
  candidates, a signal but no working tool, a tool but no signal, or nothing
  at all.

Don't guess between trackers. Writing to the wrong one is visible to other
people, and it is awkward to clean up.

If the tracker's tool needs sign-in or fails, tell the user how to connect it.
Keep doing the actual work. In your reply, include the text you would have
posted so that nothing is lost.

### Setup, the first time in a repo

Collect these: the tracker; the workspace, team and project (plus milestone);
the parent feature this repo's work goes under; the assignee ("me"); the area
label and the allowed type labels; the estimate unit and the most a ticket may
be; the status names; the gate commands; and the stand-up format and channel.

Look up everything you can from the tracker first: the current user, teams,
statuses and labels. Then ask only for what's left. Write the profile from
[references/profile-template.md](references/profile-template.md). Put personal
details (name, email, account) in `ticketing.local.md`, and add that file to
`.git/info/exclude`, which keeps it out of the shared repo without editing
`.gitignore`.

If the team already has tickets, offer to study them first so that new tickets
match the house style. See [references/calibrate.md](references/calibrate.md).

## 3. When to update

| Moment | Do |
|---|---|
| Starting a ticket | Read the ticket and its "Read first" docs. Move it to In Progress. |
| A design, placement or spec is approved | Add a dated approval comment, on the parent for feature-level decisions. Do this **before** you build. |
| A task is finished and verified | Add a completion comment with evidence, then move the ticket to Done. |
| A stop point: waiting on approval, review or input; blocked; ending a turn that changed something; context about to be summarized | Add a progress comment: what is done, what's next, and any blocker. |
| New work turns up | Search first. Update a match, or create a new child (section 6). |
| The start of the week | Make sure that week's planned tickets exist and are complete (section 9). |
| The turn only answered a question | Nothing. |

**Asking first.** If the project rules or the profile allow automatic updates,
make routine updates on your own tickets without asking: status, comments, and
fields. Even then, get a yes before you create more than two tickets at once,
restructure existing ones (re-parent, renumber, rewrite bodies), or cancel
anything. Show the list first: titles, estimates, due dates and parents. Bulk
changes are visible to the whole team and tedious to undo.

## 4. Whose tickets

- **Only touch tickets that belong to the profile's user,** meaning tickets
  assigned to them or tickets you are creating for them. Don't create, edit,
  comment on, move or add relations to anyone else's ticket, even when it's
  related. Mention it in your reply and let the user decide.
- **Always set the assignee explicitly.** The connector may be signed in as
  someone else, such as the team lead. The tracker will then show them as the
  creator, which is fine, but the assignee must be the real owner.
- **Never put secrets in a ticket.** That means no `.env` contents,
  credentials, tokens, customer data, or URLs with keys in them. Tickets are
  read widely and kept forever.

## 5. The fields every ticket carries

These are the defaults. The project rules or the profile can change them.

- **Assignee:** the profile's user.
- **Estimate:** 1 point = 1 day. Use only 1, 2 or 3. **Nothing goes over 3
  days.** Split bigger work into numbered tickets. Small tickets show progress
  during the week, and a big ticket hides drift until it is too late.
- **Due date:** required on planned work. Space the dates across the week in
  build order, not all on the same day. Backlog that is in no plan gets an
  estimate and "Done when" but no date, and gets a date when it is planned. If
  the date depends on a plan that isn't written yet, set a placeholder and say
  so in the ticket.
- **Parent and project:** the feature (or stream) parent, plus the project and
  milestone.
- **Labels:** two or three. One is the area label (for example `AI/RAG`). One
  is a type: `Bug`, `Feature`, `Improvement`, `Research`, `Security`,
  `Performance`, `Database`, `DevOps` or `Frontend`, or the project's own list.
- **Priority:** always set.
- **Relations:** set "blocked by" and "blocks" as **real tracker links**, and
  also add one line in the body: `Blocked by X. Blocks Y.` The links show the
  order and which tickets can run side by side. The text line survives exports.

**Parents** (features and streams) have **no estimate of their own**, so that
nothing is counted twice. Their due date is the last child's due date.

**Readiness check.** A ticket without an estimate, a due date (if planned), a
parent, labels or a "Done when" is not ready to start. Fix the ticket before
you start the work.

## 6. Writing a ticket

**Search before you create.** Look by keyword and under the parent. Update a
matching ticket instead of making a duplicate. Create a ticket only when you
can write its Goal and its "Done when". A stub that says "details to be added"
is noise.

**Title:** `<Feature> <n>: <outcome>`. Use sentence case and no trailing
period. Number the tickets in build order, for example
`Documents 3: document type catalogue, fields and numbering`. Once a number is
assigned it stays; a new ticket takes the next free number. If the project
already uses a different separator (such as `Feature · n:`), keep the
project's. The point is one style across all its tickets.

**Choose the form.** The full templates and examples are in
[references/templates.md](references/templates.md).

- **Short ticket:** small tasks, fixes and backlog. A bold `**Done when:** …`
  first line, one or two lines of context, and the source reference.
- **Implementation ticket:** code that an agent will build. Goal, In scope, Not
  in scope, Done when, Dependencies.
- **Feature or stream parent:** Goal, Read first, Phases, Children in order,
  Not in scope, and an end-to-end Done when.
- **Research or decision ticket:** Objective, Deliverables, Results,
  Limitations and risks, Next steps, and the decisions needed.

**What makes these work.** Each of these closes a gap where an agent would
otherwise guess:

- **The first line is a checkable `**Done when:** …`.** It is what the team
  lead reads in the list, and it is the finish line. "Works well" is not
  checkable. "The 12 refusal cases in `test_guard.py` pass, and `make check` is
  green" is.
- **Point into the spec instead of restating it.** Write `design.md §6.4` or
  `ENGINEERING.md §2`. The doc is the source of truth, so nothing is invented
  and nothing goes stale in two places.
- **In scope names exact things:** modules, functions, routes, CLI commands,
  config keys and error names. Don't put code in the ticket.
- **Not in scope names the ticket that owns each excluded item**, for example
  "Setup screens (child 19)". This stops the agent from building the next
  ticket.
- **Done when lists test scenarios as cases** (input → expected result), then
  the gate commands.
- **Keep it to one screen.** If a ticket grows longer, the detail belongs in the
  doc. Keep the length in the feature ticket and the spec, not in each child.
- **Put agent detail last, in a collapsible section:** file paths, logs and
  plans. The tracker's syntax for this is in
  [references/trackers.md](references/trackers.md).

**Hierarchy.** Feature, then an optional stream when the work is large, then
the numbered tasks. The parent's "Children, in order" list must stay current:
update it whenever a child is added, and say which children can run side by
side.

**Breaking a plan into tickets.** Split the plan into tasks of 3 days or less.
Number them in build order, set the blocks and blocked-by links, space the due
dates across the week, and mark what can run in parallel. Show the list and get
a yes (section 3), then create the tickets.

## 7. Comments are the log

Use absolute dates (`2026-11-19`), never "today".

- **Approval:** `Spec approved (2026-11-19) by <name>: <what was approved>`, or
  `Placement approved (2026-11-19): <module> goes in <place>, per <rule §>`.
  Don't build past an approval point without one.
- **Progress, at a stop point:** what was done, what's next, and the blocker
  and who can clear it. Mention that person when you need their input.
- **Completion, before Done:**
  - what was built and where: PR, commit or branch, plus migration names;
  - any change from the spec, and that the spec was updated in the same change;
  - the checks run, with real results: test counts, commands, measured figures;
  - what is still left, or what is still switched on.

  A feature parent also gets the merge, deploy and hand-test comment, with the
  real scenario and its result.
- **Deferred or cancelled:** say why, and where the work went (for example
  "folded into child 4", or "blocked by IND-149").

**Never mark a ticket Done without fresh evidence** from this session. A check
that passed yesterday does not count. If a check can't run, leave the ticket In
Progress and say why.

## 8. Each update, step by step

1. Load the rules and the profile (section 1), and confirm the tracker (section 2).
2. Find the ticket: by id from the branch or the conversation, otherwise by
   searching. Check it's yours (section 4).
3. Make the change: status, missing fields, the comment. For a long body,
   patch the part that changed instead of resending the whole description.
   When you edit labels, add or remove single labels. On some trackers,
   setting the label list replaces every label on the ticket.
4. Keep the parent in sync: its children list, and its due date (which equals
   the last child's).
5. Read the ticket back once. Confirm that the fields and links actually stuck.
6. Report (below).

## 9. Report back, and the weekly rhythm

**In your reply**, list each ticket you touched, with its link and what
changed. Then give a stand-up line for each ticket you worked on, ready to
paste:

```
<ID>, <what changed, concretely>, <time left>, <on track | at risk | blocked by X (who can help)>
IND-251, RIGHT and FULL joins refused, unit_ledger scoping next, 1 day left, on track
```

Say what changed, not just that work happened. For reviews, list the PR
numbers. If the tracker update failed or was skipped, say so here. Never skip
an update silently.

**Weekly:** at the start of each week, make sure the week's planned work has
tickets with estimates and due dates spaced in order. Split upcoming work into
tickets as it enters the week, not all at once in advance. **Daily:** the
stand-up line above.

## 10. Things that look helpful but aren't

- **Stub tickets.** They clutter the board and get stale.
- **Tickets over 3 days.** Split them. Large old tickets on the board predate
  this rule, so don't copy them.
- **Restating the design in the ticket.** It drifts from the spec. Point to the
  spec instead.
- **Updating a teammate's ticket because it's related.** Mention it in your
  reply instead.
- **Marking Done on "it should work".** A ticket is done when there is evidence
  that it works.
- **Silently skipping the update** when the tracker is down. Say so, and paste
  the text you would have posted.
