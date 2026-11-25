# Report format

The defaults for the stand-up. A project rule that gives other questions, wording
or order wins.

## The questions

1. **Yesterday:** which tickets did you finish or move? (ticket ID + one line on what changed)
2. **Today:** which tickets are you working on? (ticket ID + one line on what you will do)
3. **Left:** for each ticket in progress, how many days remain, and is it on track / at risk / late?
4. **Blocked:** by what, and who needs to act? (or "no")
5. **Other:** reviews (PR numbers), mentoring, meetings, and roughly how long? (or "none")

## How to answer each one

**Yesterday**
- One bullet per ticket: `ID → <status now>: <what changed>`.
- Name the outcome, not the activity: approved, done, reviewed, sent back for
  rework, handed over. "Worked on X" is not an outcome.
- A meeting that decided something (approval, rework) is that ticket's line.
- No tracker: one bullet per outcome ("Finished the importer: CSV and JSON
  both load, and bad rows are reported").

**Today**
- One bullet per ticket: `ID: <what you will do>`. Only what the user will
  actually work on.
- A late ticket still gets a line saying what will be done on it today, or
  what is left. Never just "late". Lateness belongs under Left.

**Left**
- One bullet per in-progress ticket:
  `ID: <n> day(s) left (due <date>), on track | at risk | late`, plus a few
  words of why when it isn't on track.
- Days left are working days from today to the due date. Due today = 0.
- **On track:** will finish by the due date.
- **At risk:** can still make it, but only if a named thing happens (an
  approval, a reply).
- **Late:** past the due date, or moved and can no longer be met. Give the
  new date.
- Tickets moved because today's focus changed go here, with their new date.
  "Moved" never stands alone: the line says to when, and the tracker's due
  date says the same.
- A ticket whose scope grew isn't late. Say what was added: "2 days left (due
  27 Nov), on track: paid runs added to it."
- Finished work never goes here, even when the tracker was behind on it. It's
  a Yesterday line, `→ Done`.
- No tracker and no due date: carry over the days the user gave last time,
  count them down, and mark them as guesses until confirmed.

**Blocked**
- `<what> — <who needs to act>` per blocker, or just **No**.
- Waiting for a scheduled approval is not a blocker.

**Other**
- Only reviews (with PR numbers), mentoring or meetings not already reported
  under Yesterday, each with its duration. These are never tickets of their
  own, even when the user asks for tickets for "all of it".
- Admin work with no ticket is left out when the team tracks work in tickets.
- Unknown duration: ask. Nothing left: **No**.

## Style

- Bold question headers, `•` bullets, one line per bullet, about four lines
  per answer at most.
- Plain words. No file paths, branch names, internal jargon or tool names.
- Lines are about the work, never about the tracker: no "tracker updated",
  "caught up in Linear" or "status fixed". The tracker shows that, and a line
  claiming it invites a check.
- Use concrete specifics: "compared four vendors and picked two to test",
  not "did research".
- Write in the user's voice, about the user's work. Don't make someone else
  the subject of a line, or credit them with the user's decisions. Name a
  person only when they need to act (Blocked), when the work waits on them,
  or when the user named them.
- Sound like the user: their verbs and length from the voice guide
  ([voice.md](voice.md)) when there is one. Under about 20 words per line. No
  stacked achievements, adjective triplets, em dashes or words they never use.
- Use ticket ids when the team's stand-up asks for them.
- Never invent an id, date or duration. Write `XXX-___` and say so.

## Sync check

Reviewers compare each posted line with the tracker, usually soon after the
stand-up is due. Run this check on the planned answers (step 6), again after
the tracker changes (step 7), and on any text the user says they posted. Each
failed row becomes a tracker change in the plan, or a question.

| The report says | The tracker must show |
|---|---|
| Yesterday `ID → Done` | Done, with a closing comment giving the evidence |
| Yesterday `ID → <other status>` | that status |
| A Today line | in progress (the team's started state), assigned to the user |
| Left `n days left (due D)` | due date D, and n counted from today |
| Left `late` or `moved to D` | due date D, and a comment saying why it slipped or moved |
| Anything named | the fields the project's ticket rules require (estimate, due date, assignee, parent) |

Then check the tickets the report doesn't name but a reviewer would see:

- **In progress and assigned to the user, but missing from Left** (Left asks
  for every ticket in progress): add it to Left, or change its status.
- **Past its due date and not done**: it's late. Move the date with a comment,
  or close it if the work is finished.
- **Due before a ticket it waits on**: the date can't be met. Move it, or put
  it under Left as at risk with the reason.
- **"On track" with 0 days left and clear work remaining**: ask whether it
  really finishes today.
- **A parent marked done while its children are open**, or the other way
  round.
- **When the rules plan tickets weekly:** this week's work all has tickets of
  at most 3 days (or the rules' limit), and the estimates due this week fit
  the working days left. Otherwise the week plan comes first.

A row passes only on this run's tracker read, never on what the tracker
showed earlier, or what the user said they'd change.

## Worked example (made-up team and tickets)

Saved as `~/standups/2026-03-10.md` (every report goes in the home folder's
`standups/`, whichever repo it covers):

```markdown
# Stand-up · Tuesday 2026-03-10

**Yesterday: which tickets did you finish or move?**
• ACME-41 → Done: invoice export ships CSV and PDF; reviewed and merged (PR #88).
• ACME-44 → In review: retry logic for the webhook sender is up for review (PR #91).

**Today: which tickets are you working on?**
• ACME-44: answer the review comments and merge.
• ACME-47: start the audit-log screen, beginning with the filters.

**Left: days remaining and on track / at risk / late?**
• ACME-44: 0 days left (due today), on track.
• ACME-47: 3 days left (due 13 Mar), at risk: needs the API field from the platform team by Thursday.

**Blocked: by what, and who needs to act?**
• No.

**Other: reviews, mentoring, meetings, and how long?**
• Reviewed PR #86 (30 min). Sprint planning (1 h).

## Tracker (synced 2026-03-10 09:10, before posting)
- ACME-47: To Do → In Progress (it's under Today).
- Everything else already matched.

---

## Sources checked
- The user's account: ACME-41 merged, today is ACME-44 then ACME-47.
- Sessions on 2026-03-09: billing-service (invoice export, 2 h), webhooks (retry logic, 1 h).
- Git: 3 commits in billing-service; PR #91 open in webhooks.
- Tracker (read 2026-03-10, before and after the sync): ACME-41 Done, ACME-44 In Review due 10 Mar, ACME-47 In Progress due 13 Mar.
```

## Asks for you (shown under the draft, not part of the answers)

Example, when the chat was read:

```markdown
**Asks for you** (since Mon 9 Mar)
1. Dana (lead), Mon 16:40, DM: wants the CSV export to include refunds by Thursday.
   No reply yet. No ticket. → **New ticket:** "Include refunds in invoice CSV export";
   done when refunds appear as negative rows and totals match; due 12 Mar.
2. Sam, Tue 09:05, stand-up thread: ACME-44 still shows the old due date. You replied
   "will fix". → **Update ticket:** move ACME-44's due date to 10 Mar, with the comment
   "Slipped one day for review fixes."
3. Priya, Mon 11:20, #payments: asked you to review PR #93. Approved Mon 15:02.
   → **Nothing to do.** It goes under Other as a review, if you want it listed.
```

Paraphrase, never quote direct messages. Each ask is one line of facts plus one
suggested path.

When a report is changed after posting, add these after the answers:

```markdown
## As posted
<the final text of each answer>

## Fixes (2026-03-10)
1. ACME-47 had no due date in the tracker: user set 13 Mar and added a comment.
```

## The JSON next to each report

`~/standups/YYYY-MM-DD.json` (the script prints the exact path as
`log.save_json_to`). Only these fields: no prompts, no file contents.

```json
{
  "schema_version": 1,
  "date": "2026-03-10",
  "scope": "/home/me/work/billing",
  "covered_from": "2026-03-09T00:00:00+01:00",
  "covered_until": "2026-03-10T09:15:00+01:00",
  "tickets": [
    {"id": "ACME-44", "status": "In Review", "due": "2026-03-10", "days_left": 0, "state": "on track"},
    {"id": "ACME-47", "status": "In Progress", "due": "2026-03-13", "days_left": 3, "state": "at risk"}
  ],
  "tracker_sync": {
    "checked_at": "2026-03-10T09:10:00+01:00",
    "changes": ["ACME-47: To Do -> In Progress"],
    "left_to_user": []
  },
  "today": ["ACME-44: answer review comments and merge", "ACME-47: audit-log filters"],
  "blockers": [],
  "asks": [
    {"from": "Dana", "summary": "include refunds in CSV export", "due": "2026-03-12",
     "ticket": null, "path": "new ticket", "status": "open"}
  ],
  "posted_edits": []
}
```

`asks` carries the open asks to the next report, which checks whether each one
was handled. One-line summaries only.

`covered_until` is when the report was approved. The next report's window starts there.

`tracker_sync` records the last sync check: when it ran, the changes made,
and any change left for the user to make by hand. The next report starts by
checking that `left_to_user` is empty in the tracker.
