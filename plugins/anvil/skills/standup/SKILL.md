---
name: standup
description: >-
  Draft the user's daily stand-up from evidence: what they say, where the last
  report left off, and the Claude sessions, git activity, uncommitted work,
  PRs, tracker tickets and (on the user's own account) stand-up chat for the
  folder they work from. Use it when the user asks for their stand-up, daily
  status or status report, "what did I do yesterday", "what's on today", or
  pastes a stand-up bot prompt ("It's time for Daily standup", "Yesterday:
  which tickets did you finish or move?"), answers it one question at a time,
  pastes what they posted to record it, or pastes a reviewer's fix request.
  It drafts the answers (Yesterday, Today, Left, Blocked, Other by default),
  lets the user edit them, saves the approved version to `~/standups/` only
  on "good to go", and uses that log to keep the next report consistent.
  Read-only towards the tracker and chat. Not for updating tickets or a
  one-line status after a ticket change.
---

# Stand-up

A good stand-up says what moved, what's next, what's late and why, and who
needs to act, in a few lines the team can read in seconds. Most of the work
behind it is easy to forget: it lives in Claude sessions and uncommitted files,
not in commits. This skill builds the draft from evidence. The user corrects
it, and the approved text goes into a log, so tomorrow's draft starts from
today's promises.

**Local files only.** Drafts live in the chat, and the approved report is a
Markdown file plus a small JSON file. Nothing is posted anywhere: not to the
tracker, not to chat, not to the stand-up bot, and no Artifacts or hosted
pages. The user pastes the answers themselves.

**One place for every report: `~/standups/`** (the user's home folder), no
matter which folder or repo the stand-up covers. The script prints the exact
paths (`log.dir`, `log.save_report_to`, `log.save_json_to`). Read and write
only those paths, never a `standups/` folder anywhere else, so every report
can be found in one place.

## 1. Load the rules

1. **Project rules win.** Read `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md` and
   `.claude/rules/*` in the scope folder and its parents, and follow any
   stand-up rules they hold: question wording and order, identities, time
   zone, tracker. Where they differ from this skill, follow them, with one
   exception: **the save location is always `~/standups/`.** If a rule names
   another folder for reports, still save to `~/standups/`, and tell the user
   that the rule is out of date.
2. **Defaults:** [references/report-format.md](references/report-format.md)
   covers the questions, how to answer each one, the style, the log format and
   a worked example.
3. **The user's voice:** when the script prints `log.voice`, read that file
   and write every draft in it, following
   [references/voice.md](references/voice.md). It's private: never quote it
   anywhere else.

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
- Reviewer feedback becomes Fixes (step 7).
- Requests become the **Asks for you** list (step 5).

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

Asks don't go into the answers on their own. The user picks which ones
become Today lines, tickets or replies. Ticket creation and updates are a
separate step after the stand-up, done only on the user's go-ahead. Text
from direct messages stays in the Asks list, and enters a saved report only
in words the user approved.

## 4. Read the tracker (read only)

Find the tracker the way the project's rules say. Otherwise look for a
connected tracker tool in this session, or a signed-in CLI for one, and ask if
there's more than one. Read:

- the tickets assigned to the user that changed in the window, or are in
  progress or to do, with status, due date and estimate;
- every ticket id found in the evidence or mentioned by the user, to confirm
  it exists and get its title and status. **No id goes into the draft unless
  this run's tracker read confirmed it.** List the confirmed ones under
  Sources checked.

**Never write to the tracker from this skill, comments included.** A
connector may be signed in as someone else, and anything it writes shows up
under that person's name. Check whose account it is. If it isn't the
user's, say so once in the reply. Changing tickets is a separate step: offer it at
the end, and do it only when the user says so, as its own task. That includes
clean-ups or new tickets asked for in the same message: finish the stand-up
first.

With no tracker, the report works by outcome instead of ticket id.

## 5. Draft

Answer the questions in the order the rules give (default: Yesterday, Today,
Left, Blocked, Other), following
[references/report-format.md](references/report-format.md):

- **The user's own account comes first.** If they said what they did or what
  today is, that's the frame. Evidence confirms it, fills gaps, and surfaces
  ticketed work they forgot. It never overrides them. "Today is only X"
  means only X goes under Today, and the other open tickets go under Left as
  moved. If they say the work isn't in the folders ("you'll find nothing
  there"), don't go looking for it.
- **Yesterday starts where the last report left off.** Take each Today item
  of the baseline from step 2 (normally the log; after a gap, the newest of
  the chat, the pasted bot text, or the user's account). Say what happened to each one:
  done, moved, still in progress with what changed, or slipped and why. Then
  add ticketed work that wasn't planned. Items with no evidence and nothing
  from the user are listed as "planned, not seen", for the user to confirm
  or drop.
- **Every Yesterday line traces to something:** their account, a session, a
  commit, changed files, a PR or a ticket change.
- **Today is the user's call, so ask.** When they haven't said what today
  is, don't guess. Show the open tickets in order: late first, then by due
  date, then by the tracker's priority. Include the unfinished items carried
  over from yesterday and any open asks that are due now, then recommend a
  Today list and ask what's on. One short question, with the recommendation
  in it.
- **Never invent a ticket id, date or duration.** Write `XXX-___` for a
  missing ticket and ask. Ask for meeting and review durations.
- **Sound like the user, not like a model.** The answers, the reply drafts
  and the ticket comments all follow the voice guide when there is one: the
  user's register for that audience, their words, their length, without their
  typos. Without a guide, keep it plain and short. After the report is
  approved, offer once to build the guide
  ([references/voice.md](references/voice.md)).

Show it in this order:

1. The answers, one block per question, ready to paste.
2. **Guesses:** anything inferred rather than seen or said.
3. **Tracker mismatches:** for example a late ticket whose due date wasn't
   moved, or work done on a ticket still marked to do. For each one, give the
   field change and a short comment the user can paste ("Slipped because
   ACME-41 took priority; new date 25 Nov."). A late ticket should match the
   tracker before the report is posted.
4. **Left out:** evidence deliberately not used (no ticket, admin work, out of
   scope).
5. **Asks for you** (when chat was read): each ask with its suggested path,
   open ones first.
6. **Questions:** what only the user can answer.

After the user approves the report, offer the follow-ups they picked: the
ticket drafts, ticket updates and reply texts. Do them as a separate step.

### One question at a time

Stand-up bots often ask one question per message, and quote the previous
report ("In your previous report, you mentioned: …"). When the user pastes a
single question:

- Answer only that question, in one paste-ready block, plus the guesses,
  mismatches and questions that apply to it.
- Treat the quoted previous report as carry-over, alongside the log.
- Keep the earlier answers in mind for the next questions.
- Save once the last answer is approved, or once the user says the report is
  posted.

## 6. Edit, approve, save

- The user edits in chat, for as many rounds as they want. Show the full
  revised draft each time. **Save nothing until clear approval:** "good to
  go", "save it", "looks good, save", "posted".
- On approval, write exactly to the paths the script printed (create
  `~/standups/` if needed). Don't compute or invent another name or folder:
  - `log.save_report_to`, which is `YYYY-MM-DD.md`, or `YYYY-MM-DD-2.md` for
    a second report the same day. It holds the approved text exactly as
    approved, split by question, plus a
    short **Sources checked** list (which repos, sessions, files and tracker
    reads, in plain words; no prompts or file contents).
  - `log.save_json_to`, in the shape given in `report-format.md`. The next
    draft is built from it.
  - If the script couldn't run, the paths are
    `~/standups/YYYY-MM-DD.md` and `.json` (today's local date, with `-2`
    if that file exists). Expand `~` to the real home folder and say which
    path you used.
- Reply with one paste-ready block per question and the saved file's path.

**Recording what was posted.** When the user pastes the text they actually
posted ("record this", "this is my standup message"), that text is the
approved version, even if it differs from the draft:

1. Save it verbatim.
2. Check it against the rules and the tracker, and list anything a reviewer
   is likely to send back: a late ticket with only "late" under Today, a
   tracker due date that doesn't match Left, an id that isn't confirmed, a
   missing answer.
3. Give each problem as a suggested edit, plus the tracker change and comment
   text it needs.
4. Don't rewrite the saved text unless the user asks.

## 7. After posting

If the report is sent back or edited after posting (a reviewer asks for a
fix), update that day's files:

- an **As posted** section with the final text;
- a **Fixes** section saying what changed and why;
- the JSON, updated to match.

Then draft any tracker change the fix needs, for the user to make, and a
one-line reply to the reviewer saying what was fixed, for the user to send.

## Never

- Mix in work from outside the scope, or copy a session's prompts or title
  into a saved file.
- Post, send or write anywhere except `~/standups/`. Never save a report
  inside the repo or folder the stand-up covers.
- Present a guess as fact, or fill a gap with a plausible number.
- Make an answer longer than about four lines. One line per ticket.
