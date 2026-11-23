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
  new date when one is known.
- Tickets moved because today's focus changed go here, with their new date.
- No tracker and no due date: carry over the days the user gave last time,
  count them down, and mark them as guesses until confirmed.

**Blocked**
- `<what> — <who needs to act>` per blocker, or just **No**.
- Waiting for a scheduled approval is not a blocker.

**Other**
- Only reviews (with PR numbers), mentoring or meetings not already reported
  under Yesterday, each with its duration.
- Admin work with no ticket is left out when the team tracks work in tickets.
- Unknown duration: ask. Nothing left: **No**.

## Style

- Bold question headers, `•` bullets, one line per bullet, about four lines
  per answer at most.
- Plain words. No file paths, branch names, internal jargon or tool names.
- Use concrete specifics: "compared four vendors and picked two to test",
  not "did research".
- Write in the user's voice, about the user's work. Don't make someone else
  the subject of a line, or credit them with the user's decisions. Name a
  person only when they need to act (Blocked), when the work waits on them,
  or when the user named them.
- Use ticket ids when the team's stand-up asks for them.
- Never invent an id, date or duration. Write `XXX-___` and say so.

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

---

## Sources checked
- The user's account: ACME-41 merged, today is ACME-44 then ACME-47.
- Sessions on 2026-03-09: billing-service (invoice export, 2 h), webhooks (retry logic, 1 h).
- Git: 3 commits in billing-service; PR #91 open in webhooks.
- Tracker (read 2026-03-10): ACME-41 Done, ACME-44 In Review due 10 Mar, ACME-47 To Do due 13 Mar.
```

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
    {"id": "ACME-47", "status": "To Do", "due": "2026-03-13", "days_left": 3, "state": "at risk"}
  ],
  "today": ["ACME-44: answer review comments and merge", "ACME-47: audit-log filters"],
  "blockers": [],
  "posted_edits": []
}
```

`covered_until` is when the report was approved. The next report's window starts there.
