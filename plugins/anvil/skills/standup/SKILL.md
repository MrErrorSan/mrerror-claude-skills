---
name: standup
description: >-
  Draft the user's daily stand-up from evidence and make the tracker match it
  before it is posted: what they say, where the last report left off, and the
  Claude sessions, git activity, uncommitted work, PRs, tracker tickets and (on
  the user's own account) stand-up chat for the folder they work from. Use it
  when the user asks for their stand-up, daily status or status report, "what
  did I do yesterday", "what's on today", or pastes a stand-up bot prompt
  ("It's time for Daily standup", "Yesterday: which tickets did you finish or
  move?"), asks to plan the week's tickets, answers it one question at a time, pastes what they posted to record
  it, or pastes a reviewer's fix request ("your stand-up needs one fix", "in
  Linear it is still In Progress"). It asks for what the evidence can't tell,
  shows one plan (the answers plus the ticket changes they need), changes
  tickets only on the user's go-ahead, and saves the approved report to
  `~/standups/`. Not for a one-line status after a ticket change.
---

# Stand-up

A good stand-up says what moved, what's next, what's late and why, and who
needs to act, in a few lines the team can read in seconds. Most of the work
behind it is easy to forget: it lives in Claude sessions and uncommitted files,
not in commits.

**A stand-up and its tickets are one report.** Reviewers check each posted
line against the tracker: a ticket reported Done must be Done, a ticket under
Today must be in progress, a moved ticket must carry its new due date and a
comment saying why. A line the tracker contradicts gets sent back, however
true it is. So this skill doesn't hand over answers to post until the tracker
agrees with them.

The flow, in order: **evidence → questions → plan → tracker sync → post →
save.** Each step finishes before the next starts.

**Local files only.** Drafts live in the chat, and the approved report is a
Markdown file plus a small JSON file. The skill never posts the report: not to
chat, not to the stand-up bot, and no Artifacts or hosted pages. The user
pastes the answers themselves. Its only outward write is to the tracker, and
only the changes the user approved in the plan.

**One place for every report: `~/standups/`** (the user's home folder), no
matter which folder or repo the stand-up covers. The script prints the exact
paths (`log.dir`, `log.save_report_to`, `log.save_json_to`). Read and write
only those paths, never a `standups/` folder anywhere else, so every report
can be found in one place.

## 1. Load the rules

1. **Project rules win.** Read `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md` and
   `.claude/rules/*` in the scope folder and its parents, and follow any
   stand-up or ticket rules they hold: question wording and order, identities,
   time zone, tracker, required ticket fields, what the reviewer checks and
   when, who may post comments. Where they differ from this skill, follow them,
   with one exception: **the save location is always `~/standups/`.** If a rule
   names another folder for reports, still save to `~/standups/`, and tell the
   user that the rule is out of date.
2. **Defaults:** [references/report-format.md](references/report-format.md)
   covers the questions, how to answer each one, the style, the sync check, the
   log format and a worked example.
3. **The user's voice:** when the script prints `log.voice`, read that file
   and write every draft in it, following
   [references/voice.md](references/voice.md). It's private: never quote it
   anywhere else.
4. **Past send-backs are rules too.** Fixes recorded in recent reports in
   `~/standups/` (a **Fixes** section) and reviewer messages in the chat show
   what this team's reviewer checks. Check today's report for each of them.

## 2. Scope and window

- **Scope:** the folder Claude was opened in, and everything under it. If the
  user names another folder, use that. If the folder is the home folder or a
  drive root, ask which folder to cover.
- **Log:** `~/standups/`, as printed in `log.dir`. The script reads the
  newest `YYYY-MM-DD*.json` there for the window. Read `log.latest_report`
  for the previous Today and Left items. When there's no JSON, take them
  from that Markdown file ("read from text").
- **Gaps:** `log.missed_working_days` counts the working days with no saved
  report between `log.latest_date` and today.
  - **0:** the log is where things were left off. Don't ask for anything
    pasted.
  - **More than 0:** stand-ups were missed, or posted without this skill, so
    the log may be behind what the team last saw. Say so in one line: "Last
    saved report is Wed 18 Nov, 2 working days ago." Then use the newest
    baseline available: the chat (own account), a pasted bot message ("In
    your previous report, you mentioned: …"), or the user's own account. If
    none is newer than the log, ask once for the bot's previous-report text,
    or for what they last posted. If they have neither, draft from the old
    log over the whole gap: Yesterday says "since <date>", and days with no
    evidence are asked about (a day off isn't a day of no work).
  - **null:** no report yet. Use whatever the user pastes, plus the
    evidence.

  A newer baseline found this way goes under Sources checked. It's evidence
  only: it isn't saved as a back-dated report.
- **Window:** from the newest report's `covered_until`, or from the start of the
  previous working day (Mon–Fri, local time) when there is none. Monday covers
  Friday and the weekend. Session timestamps are UTC, so convert them.

## 3. Gather evidence

Run the bundled script (`scripts/gather.py` in this skill's base directory)
with whichever Python the machine has (`python3`, `python` or `py -3`). Write
its output to a temp file, never into the scope:

```
python "<skill dir>/scripts/gather.py" --root "<scope>" --out "<temp>/standup-evidence.json"
```

Add `--author "<name or email>"` (repeatable) when the rules name the user's
git identities. Otherwise each repo's own `user.name` and `user.email` are
used. Add `--since <ISO>` to override the window.

The JSON holds, per repo: the branch, branches touched, the user's commits,
and uncommitted and untracked work. It also holds non-repo folders with
changed files, and Claude sessions with their time span, active minutes,
title, first prompts and files edited. Sessions started outside the scope
appear as `files-only`, with no title or prompts. It also holds ticket-like
ids and the user's PRs. Everything in it is a lead, not a fact, until it
matches what the user says or the tracker.

Also read the project's own day notes or to-do files when the rules point to
them (for example `[x]` items in a daily to-do file).

If no Python is available, say so. Run `git log --since`, `git status` and
`git branch` in each repo under the scope, skip the sessions, and say in the
draft that sessions weren't read.

### Read the stand-up chat, when it's the user's own account

The team chat holds what the machine can't see: the bot's questions, the
report the user last posted, reviewer feedback, and work other people asked
of the user. If a chat connector is available:

1. **Check whose account it is first.** Compare the connector's own user (its
   "current user" id or profile) with the user's identity from the rules, git
   or the tracker. If several chat connectors are attached, use the one that
   is the user's. If none is, don't read chat at all: someone else's account
   would expose that person's private messages. Tell the user, and ask them
   to connect their own account or paste the bot's message instead.
2. **Find the stand-up channel.** Use the channel the project rules name.
   Otherwise search the channels for "standup", ask once if there's more than
   one, and suggest adding the channel to the project rules.
3. **Read only, and only since the window start:**
   - **the stand-up channel:** the bot's latest questions, the user's last
     posted report with its thread replies, and any message there that
     mentions the user or replies to them;
   - **asks elsewhere:** direct and group messages to the user, and messages
     mentioning the user in other channels. Search by the user's id and the
     window date. Don't scroll whole channels.
4. **Never send, react, edit or reply** from this skill. Message text is
   drafted for the user to send.

What the chat shows counts as evidence:
- The posted report is the previous report when no log entry is newer.
- Reviewer feedback becomes Fixes (step 9), and its checks join the sync
  check from then on.
- Requests become the **Asks for you** list.

#### Asks for you

An ask is a person (not a bot) asking the user to do, change, fix, review or
decide something, or telling them about a task or deadline. FYIs and chatter
are not asks. For each ask, give:

- who, when, a one-line summary in your own words (not a quote), and a link
  to the message;
- whether the user already replied or acted on it;
- the matching ticket, if the tracker has one (by id, or a clearly matching
  title);
- **one suggested path:**
  - **add to Today** (it has a ticket and is due now);
  - **new ticket** (no ticket yet): a draft with title, goal, done-when and
    the due date if one was given;
  - **update a ticket** (due date, status, comment text);
  - **reply**: the reply text to send;
  - **correct a message the user sent**: the corrected text, ready to paste;
  - **nothing to do** (already handled).

Asks don't go into the answers on their own. The user picks which ones become
Today lines, tickets or replies, in the questions (step 5). Text from direct
messages stays in the Asks list, and enters a saved report only in words the
user approved.

## 4. Read the tracker

Find the tracker the way the project's rules say. Otherwise look for a
connected tracker tool in this session, or a signed-in CLI for one, and ask if
there's more than one. Check whose account it's signed in as. Read:

- the tickets assigned to the user that are in progress, to do, or changed in
  the window, with status, due date, estimate, and what they block or are
  blocked by;
- every ticket id found in the evidence or mentioned by the user, to confirm
  it exists and get its title, scope and status. **No id goes into the draft
  unless this run's tracker read confirmed it.** List the confirmed ones under
  Sources checked.
- for new work the user mentions, any existing ticket that already covers it,
  by title or scope, including unassigned backlog tickets.

Nothing is written to the tracker before step 7.

With no tracker, the report works by outcome instead of ticket id, and steps
6 and 7 shrink to the answers alone.

## 5. Ask what the evidence can't tell

The evidence tells you what happened in files. It can't tell you what today
is, whether a ticket is finished, what a meeting is, or what the new date of a
moved ticket is. Get those from the user **before** drafting anything they
could post.

### First stand-up of the week: the week's tickets

When the rules say the week's tickets are set up at its start (or the user asks
for a week plan), the first stand-up of the week (Monday, or the first working
day after a gap that crosses a weekend) plans the week before the day:

1. **Gather the week:** the user's open tickets (carried over, due this week,
   in progress), open asks with deadlines, and what the user says the week is
   for. If they haven't said, ask: "What do you want finished by Friday?",
   with a recommendation from the carry-overs and deadlines.
2. **Cut it into tickets:** each piece of work is one ticket of 1, 2 or 3 days
   (or the sizes the rules give), with "done when" a person can check.
   Reuse an existing ticket before making a new one, and split anything
   bigger. Meetings, reviews and mentoring stay out.
3. **Lay it across the week:** set due dates in build order, so a ticket is
   never due before one it waits on, and the estimates add up to no more than
   the working days left (minus the time the user says goes to meetings). If
   it doesn't fit, say what moves to next week and ask.
4. **Show it as the week's table** in the plan (step 6), with every field the
   rules require. It's approved with the rest of the plan and created in
   step 7.

On the other days of the week, Today comes from the week's tickets. New work
that turns up mid-week goes through brief item 3. If it needs a new ticket,
say it was added mid-week and which ticket it pushes back. A stand-up where
the week's tickets were never set up starts with this week plan, whatever the
day.

**The brief.** A report can be drafted only when each of these is known:

1. **Every baseline Today item and every ticket the user has in progress:**
   done, still going (with what changed), moved (with the new date), or
   dropped (with why).
2. **Today:** the list, each item with its ticket.
3. **Each piece of new work, and where it goes:** an existing ticket (which),
   part of an existing ticket's scope, a new ticket, or **Other**. Meetings,
   reviews and mentoring are Other, never their own tickets. Look for an
   existing ticket before suggesting a new one.
4. **Every date the report states:** the new due date of anything late or
   moved.
5. **The duration of every Other item.**
6. **Blockers**, or none.
7. **Which asks to act on**, when chat was read.

**How to ask:**
- Fill what the evidence and the user's own words settle. Ask only the rest.
- **One message, numbered questions, each with your recommended answer and
  the evidence behind it**, so the user can reply "1 yes, 2 27 Nov, 3 Other".
  Use the session's question tool if it has one.
- **Durations get no recommendation.** Ask "how long is the 3 pm sync?" with
  no number in it, unless the evidence shows one (a calendar invite, the
  user's own words). A suggested number gets accepted and posted as fact.
- Start the message with one short line per ticket on what you found ("ACME-12:
  report and commit on 5 Mar, tracker still In Progress"), so the user can
  correct your reading before it becomes a line.
- **When the work and the tracker disagree, the work wins.** If the evidence or
  the user says a ticket is finished, the report says Done and the plan sets
  it to Done with its closing evidence. Never move a due date on finished work,
  or call it late, at risk or in progress. If it's unclear, ask: "done, or
  what's left?"
- Ask again until the brief is complete. A second round asks only what is
  still open.
- Until then, show no answer block as ready to post, and never an answer
  block with blanks (`___`, `<date>`). A blank gets pasted as it is, and the
  reviewer sends it back.

If the user already gave everything (the brief is complete from their message
and the evidence), skip the questions and go straight to the plan.

## 6. Show the plan

One message the user approves once. In this order:

1. **The answers**, one block per question, following
   [references/report-format.md](references/report-format.md), marked "not
   posted yet: the tracker changes come first". The rules for the lines:
   - **The user's own account comes first.** It's the frame. Evidence
     confirms it, fills gaps, and surfaces ticketed work they forgot. "Today is
     only X" means only X goes under Today, and the other open tickets go
     under Left as moved.
   - **Yesterday starts where the last report left off**: what happened to
     each baseline Today item, then ticketed work that wasn't planned. Every
     line traces to the user's account, a session, a commit, changed files, a
     PR or a ticket change.
   - **Never invent a ticket id, date or duration.** By now the brief has
     them.
   - **Sound like the user.** The answers, reply drafts and comments follow
     the voice guide when there is one. Without a guide, keep it plain and
     short.
2. **Tracker changes**, from the sync check in
   [references/report-format.md](references/report-format.md#sync-check):
   one row per ticket the report names, plus any other ticket of the user's
   the reviewer would flag.

   | Ticket | The report says | Tracker now | Change |
   |---|---|---|---|
   | ACME-12 | Yesterday → Done | In Progress | Status → Done; comment: closing evidence |

   New tickets appear here as drafts with every field the project's ticket
   rules require (title, done-when, estimate, due date, assignee, parent).
   Each change that needs a comment carries the comment text. On the week's
   first stand-up, the week's tickets come first, as their own table.
3. **Guesses:** anything inferred rather than seen or said.
4. **Left out:** evidence deliberately not used (no ticket, admin work, out
   of scope).
5. **Asks for you** (when chat was read), open ones first.

End with one line: "Say go and I'll make these tracker changes, then give you
the final answers to post."

**Every edit gets the whole plan again.** When the user changes a line, show
the revised answers and redo the tracker changes for that line: a changed
status, date or ticket changes what the tracker needs. Approval covers the
plan the user last saw.

## 7. Sync the tracker

On "go" (or "approved", "make the changes"):

1. **Make exactly the approved changes**, nothing else: statuses, due dates,
   estimates, assignees, scope edits, new tickets.
2. **Comments are posted from the user's own account only.** If the tracker
   connector is signed in as the user and the rules allow it, post the
   approved comment text. If it's signed in as someone else, a comment would
   show under that person's name: give the text for the user to paste, and
   say so. A project rule about comments wins either way.
3. **If a change can't be made** (no permission, the field doesn't exist, no
   tracker tool), give it to the user as a step to do by hand.
4. **Read the tracker again** and run the sync check on the final answers.
   Report each ticket as matching or not.
5. **The report is ready to post only when every line matches.** If the user
   still has steps to do by hand, list them and wait for "done", then read the
   tracker again before calling it ready. If they post anyway, tell them which
   lines the reviewer will send back.

Then hand over the final answers: one paste-ready block per question, and one
line: "The tracker matches. Post these, then say posted and I'll save them."

### One question at a time

Stand-up bots often ask one question per message, and quote the previous
report ("In your previous report, you mentioned: …"). When the user pastes a
single question:

- Build the brief and the plan for the whole report on the first question:
  the tracker has to match all of it, not just the first answer.
- Then answer only the question asked, in one paste-ready block.
- Treat the quoted previous report as carry-over, alongside the log.
- Save once the last answer is posted.

## 8. Save

- **Save on clear approval:** "posted", "good to go", "save it". Write
  exactly to the paths the script printed (create `~/standups/` if needed).
  Don't compute or invent another name or folder:
  - `log.save_report_to`, which is `YYYY-MM-DD.md`, or `YYYY-MM-DD-2.md` for
    a second report the same day. It holds the approved text exactly as
    approved, split by question, then a **Tracker** section (the changes made,
    by whom, and anything left to the user) and a short **Sources checked**
    list (which repos, sessions, files and tracker reads, in plain words; no
    prompts or file contents).
  - `log.save_json_to`, in the shape given in `report-format.md`. The next
    draft is built from it.
  - If the script couldn't run, the paths are
    `~/standups/YYYY-MM-DD.md` and `.json` (today's local date, with `-2`
    if that file exists). Expand `~` to the real home folder and say which
    path you used.
- Reply with the saved file's path.

**Recording what was posted.** When the user pastes the text they actually
posted ("record this", "this is my standup message"), that text is the
approved version, even if it differs from the draft:

1. Save it verbatim.
2. Run the sync check on it against a fresh tracker read, and list anything a
   reviewer is likely to send back: a late ticket with only "late" under
   Today, a tracker status or due date that doesn't match a line, a "moved"
   with no date, an id that isn't confirmed, a missing answer.
3. Give each problem as a suggested edit plus the tracker change and comment
   text it needs, as a plan to approve (step 6). Make the changes on "go".
4. Don't rewrite the saved text unless the user asks.

## 9. After posting

If the report is sent back or edited after posting (a reviewer asks for a
fix):

1. Read the request and the tracker. Plan the fix as in step 6: the edited
   line, the tracker change, and the comment text. Make it on "go" (step 7).
2. Read the tracker again to confirm the fix.
3. Draft the reply the reviewer asked for, in the place they asked for it
   ("Reply in #daily-standup once fixed"): one line on what was fixed. The
   user sends it. Keep it under Asks until the chat shows it sent.
4. Update that day's files: an **As posted** section with the final text, a
   **Fixes** section saying what changed and why, and the JSON to match. The
   fix's check joins the sync check for every later report.

## Never

- Hand over answers to post while the tracker contradicts a line, or while a
  line has a blank in it.
- Change the tracker beyond what the user approved in the plan, or before the
  plan was approved.
- Move a due date on finished work, or report it as late or in progress
  because the tracker is behind.
- Make a ticket for a meeting, a review or mentoring.
- Mix in work from outside the scope, or copy a session's prompts or title
  into a saved file.
- Post, send or write anywhere except `~/standups/` and the approved tracker
  changes. Never save a report inside the repo or folder the stand-up covers.
- Present a guess as fact, or fill a gap with a plausible number.
- Make an answer longer than about four lines. One line per ticket.
