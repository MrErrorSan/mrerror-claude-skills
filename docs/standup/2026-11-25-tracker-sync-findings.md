# Stand-up skill: why reports kept getting sent back, and the fix (0.3.3)

Date: 2026-11-25. Based on five working days of real stand-ups on a team that
posts through a stand-up bot and tracks work in a ticket tracker. The repo is
public, so people and tickets are described by role. The detailed timeline is
in `docs/standup/private/` (gitignored).

## What happened

The team lead's reviewer checks every posted stand-up against the tracker at
a fixed time each morning, 40 to 70 minutes after people post. It sent
something back on every one of the five days. The first was about format
(ticket ids, the shape of Left). The other four were the same kind of problem:
a line the tracker contradicted **at the moment of the check**.

| Day | The report said | The tracker showed |
|---|---|---|
| 1 | a ticket under Today | still To Do |
| 2 | a late ticket | the old due date, no comment; the Today line only said "late" |
| 3 | a ticket "moved" | no due date at all |
| 4 | a ticket Done | In Progress |

On days 3 and 4 the skill was in use. It saw both problems and listed them,
but only **below** the answers, as "tracker mismatches" for a later step. The
user posted the answers, and the tracker was fixed after the reviewer had
already flagged them.

## Root causes in the skill (0.3.2)

1. **The tracker sync was optional and came last.** The skill was read-only
   towards the tracker: changes were "a separate step after the stand-up,
   done only on the user's go-ahead". The answers were ready to paste before
   the tracker matched them, so the user pasted them.
2. **It drafted first and asked second.** Drafts carried blanks (`___` for
   tickets and dates) with up to six questions underneath. Blanks got pasted:
   "moved" with no date was posted on day 3.
3. **It took the tracker's state over the work.** On day 4 it read a ticket
   whose work was finished, but which the tracker still showed as open, as
   "late". It moved the due date forward and set the ticket to In Progress.
   The user had to correct it, and the tracker was put right only after the
   send-back.
4. **Its own tracker writes went stale.** Changes made early in the session
   didn't match the answers after the user's edits, and nothing re-checked
   them before posting.
5. **It didn't ask where new work belongs.** Asked for tickets for "all of
   these", it created three: one for meetings, two for work that was already
   in an existing ticket's scope. All three were canceled minutes later.
6. **Too many rounds.** Day 4 took about eight drafts in 43 minutes, because
   questions surfaced one revision at a time.

## The fix

The flow is now **evidence → questions → plan → tracker sync → post → save**,
and no step starts before the previous one is done.

- **Questions before any draft** (step 5). A "brief" lists what must be known
  before a report can be drafted: what happened to each planned and in-progress
  ticket, today's list, where each piece of new work goes (existing ticket, an
  existing ticket's scope, new ticket, or Other), every new date, every meeting
  duration, blockers. The skill asks only what the evidence can't settle, in
  one numbered message, each question with its recommended answer. No answer
  block is shown as ready to post before the brief is complete, and none ever
  contains a blank.
- **The work wins over the tracker.** Finished work is reported Done and the
  tracker catches up. Due dates on finished work are never moved.
- **One plan, approved once** (step 6): the answers plus a table of tracker
  changes, one row per ticket the report names, built from a **sync check**
  (in `references/report-format.md`). Every edit regenerates the whole plan.
- **Tracker sync before posting** (step 7): on "go", the skill makes exactly
  the approved field changes. It posts comments only from the user's own
  tracker account, and otherwise gives the text to paste. It reads the tracker
  again and calls the answers ready to post only when every line matches.
- **Past send-backs become checks.** Fixes saved in earlier reports, and the
  reviewer's messages, are added to the sync check for every later report.
- **After a send-back** the skill plans the fix, makes it on "go", re-reads the
  tracker, and drafts the "fixed" reply the reviewer asked for.
- Meetings, reviews and mentoring always go under Other, never into tickets.

The team's own stand-up rule file had the same "separate step" line, which
outranks the skill. It was updated with the reviewer's checks, in both of its
copies.

## Weekly tickets (added the same day)

The user also asked for the team lead's weekly rule to be enforced: every
ticket for the week is in the tracker at the start of the week, each 1 to 3
days, and the days then work from those tickets. When the project's rules ask
for weekly tickets, the first stand-up of the week now plans the week before
the day:
- it gathers carry-overs, deadlines and the user's goals for the week;
- it cuts the work into tickets of at most 3 days, reusing existing ones;
- it sets due dates in build order that fit the working days, or says what
  spills into next week;
- it shows all of this as its own table in the plan.

Mid-week work goes into an existing ticket where it fits, or into a new
ticket that says what it pushes back.

## How it was checked

Five new eval cases under `plugins/anvil/skills/standup/evals/`:
`interview-before-draft`, `sync-before-posting`, `done-work-tracker-behind`,
`new-work-placement` and `monday-week-plan`. They run next to the four
existing cases.

The existing graders were broken in two ways, and both are fixed. They used
`focus: trace`, which leaves out most of a long trace, so the judge never saw
the reply. And the runs couldn't write `response.md` without
`--allow-tools Write`. All graders now read `response.md` directly. Two graders
that required "for the user to post themselves" now also accept posting from
the user's own tracker account, which is the intended change.

How to run them (`claude plugin eval` won't read cases from inside `skills/`):
copy the plugin to a temp folder, move `skills/standup/evals` to
`standup-evals` beside it, then run:

```
claude plugin eval <copy> --eval-dir standup-evals --runs 2 --ablation none \
  --allow-tools Write --judge-model sonnet --no-publish --trust-plugin
```

Results, 2 runs per case, Sonnet judge:

| | Old skill (0.3.2) | New skill (0.3.3) |
|---|---|---|
| The 5 new cases | 0.81 | 0.98 |
| All 9 cases | not run | **0.95** (6 of 9 cases perfect on both runs) |
| `interview-before-draft` | 0.4 and 0.8: drafts with blanks | 1.0 and 0.8 |
| `new-work-placement` | 0.6 and 0.8: meetings proposed as tickets | 1.0 and 1.0 |

The remaining failures were checked by hand. In each one the reply did the
right thing and the judge read the grader more strictly. For example, one
reply asked for the slip reason instead of inventing it in the comment.
`sync-before-posting` and `done-work-tracker-behind` pass on the old skill
too: in a single dry-run turn, the old skill already listed the mismatches.
The real failure happened later, when the user posted before the tracker was
fixed. A one-turn eval can't show that ordering. The new skill's gate (answers
marked "not posted yet" until the tracker re-read matches) closes it.

Running the evals also turned up one more rule, now in
`references/report-format.md`: lines describe the work, never the tracker.
One reply wrote "tracker updated today", the same kind of line that drew the
day-4 send-back.
