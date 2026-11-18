# Stand-up skill: design

Date: 2026-11-18. Status: draft, awaiting Saad's approval.
Home: the `anvil` plugin in `mrerror-claude-skills`, next to `ticket-update`.

## Intent

Saad works in several separate folders under one GitHub directory. Each folder
is a profile with its own audience. Every working day he has to answer a
stand-up for at least one of them. Today he writes the answers from memory,
and most of the real work is easy to forget, because it lives in uncommitted
files and Claude sessions rather than commits. In the week before 2026-11-18,
none of the 15 repos had a commit, yet four of them had a full week of work.

This skill turns "give me my stand-up" into a draft built from evidence. Saad
edits the draft, approves it, and it goes into a log. That log makes each day's
report consistent with the last one, and gives him a dated record of what was
done.

## Profiles and audiences (decided by Saad)

A **profile** is a top-level folder of the workspace root
(`C:\Users\MrError\Documents\GitHub`). Each profile has one audience:

| Profile | Kind | Audience | Tracker today |
|---|---|---|---|
| `Indus Technologies` | team | the team, through Geekbot in #daily-standup | Linear (team IND) |
| `Enteyoes`, and any other folder except `Mine` | client | may be shared with that client | none (may get one) |
| `Mine` | personal | Saad only. It sets today's goals. | none (may get a personal one) |

**Reports never mix profiles.** A report reads evidence only from its own
profile's folder, and its log is stored only in that profile's folder. If Saad
works in two profiles on one day, he gets two reports. This is what keeps a
client report safe to share.

## Goals

- **One request, one draft.** Saad asks ("standup", "status for Indus", or pastes
  the Geekbot prompt) and gets a draft that answers the five questions:
  - **Yesterday:** which tickets did you finish or move? (ticket ID + one line on what changed)
  - **Today:** which tickets are you working on? (ticket ID + one line on what you will do)
  - **Blocked:** by what, and who needs to act? (or "no")
  - **Left:** for each ticket in progress, how many days remain, and is it on track / at risk / late?
  - **Other:** reviews (PR numbers), mentoring, meetings, and roughly how long? (or "none")
- **Grounded in evidence.** Every Yesterday item comes from something the skill
  saw: a session, changed files, a commit, a PR or a ticket change. Anything it
  inferred is marked as a guess.
- **Ticket ids where they exist.** Linear for Indus today. Any profile that gets
  a tracker later uses it with no change to the skill.
- **Draft, edit, approve, save.** Nothing is saved until Saad says "good to go"
  (or similar). The saved version is exactly the one he approved.
- **Consistent from day to day.** The log feeds the next draft. Yesterday's
  "Today" becomes the check for the next "Yesterday", and unfinished items carry
  over with their days left.
- **Paste-ready output.** Geekbot asks the questions one at a time, so each
  answer is its own copyable block.

## Non-goals

- **No writes to the tracker.** The stand-up only reads Linear (option A, chosen
  by Saad). When it notices a mismatch, such as work done on a ticket still in
  Todo, it lists the mismatch under the draft and offers to run `ticket-update`.
- **No posting.** It does not post to Geekbot, Slack or a client. Saad pastes.
- **No team-wide reports.** It covers only Saad's own work.
- **No hooks or background journaling.** Claude's session history already
  records the work.

## Anti-goals (failure even if it "works")

- **Leaking across profiles.** An Indus stand-up that mentions Enteyoes, or a
  client report that mentions Indus or Mine.
- **Invented work.** A Yesterday line with no evidence behind it, or a guess
  presented as fact.
- **Raw session content in a saved report.** Prompts, file contents, secrets
  and internal chatter must never reach a log that may be shared. The log holds
  only the approved text and small structured fields.
- **A report too long to paste.** Each answer should be one to four lines.

## Constraints

- Windows with Git Bash, and Python 3 with the standard library only. Paths
  contain spaces (`Indus Technologies`, `Lenovo LCD`).
- Repos are not always one level deep. Claude has had sessions in
  `Indus Technologies/Indus/Mutlashi`, under a folder that is not itself a repo.
  Some work folders are not repos at all (`PBS maker`, `HikVision IOT`).
- Session files are large (one Chunker session is 13 MB of JSONL) and are not a
  public format. The useful fields seen on 2026-11-18 are `type`
  (`user`/`assistant`/`ai-title`/`last-prompt`), `timestamp`, `cwd`,
  `gitBranch` and `sessionId`, plus tool-use blocks inside `message.content`. The
  script must skip what it doesn't recognise instead of failing.
- Saad's global rules apply: reports are local files in his own folders, never
  Artifacts; no Claude co-author trailers on commits.

## Approaches considered

1. **A skill plus an evidence-gathering script (chosen).** A bundled Python
   script finds the profile's repos, collects git status, branches, commits and
   PRs, and skims session files since the last report into one compact
   summary. Claude reads that summary plus the tracker and writes the draft.
   This is fast across many repos, gives the same result each run, and is the
   only way to use session history without filling the context window.
2. **Instructions only.** Claude would run git commands in each repo every time.
   It was rejected because it is slow, varies between runs, and can't use
   session history, which is where most of the work shows up.
3. **Fold it into `ticket-update`.** It was rejected because one skill writes and
   the other only reads, which would blur when each should run. Also, the
   stand-up must work for profiles with no tracker.

The marketplace search on 2026-11-18 found no tool that covers several repos
grouped by profile, tickets and a report history together. These ideas are
borrowed:

| Source | Idea taken |
|---|---|
| ryanb `standup` | a config file, a "since last report" marker, and skipping repos with no activity |
| `git-standup` | working days, so Monday covers Friday and the weekend |
| `claude-daily` | one dated Markdown file per report, in an append-only folder |
| `herdr-standup` | report uncommitted work, and keep a versioned JSON file next to each report |
| Anthropic `engineering:standup` | keep working when no tracker is connected |

## Design

### Parts

```
plugins/anvil/skills/standup/
  SKILL.md                    # workflow: pick profile → gather → draft → edit → approve → save
  scripts/gather.py           # evidence gatherer (stdlib only), prints one JSON summary
  references/profile-template.md
  references/report-format.md # the five questions, rules per profile kind, worked example
```

### Profile settings

These live in `<profile>/.status/profile.md`, a short Markdown file with a YAML
block. The skill creates it the first time it runs in a profile and asks only for
what it can't detect.

- `kind`: `team` | `client` | `personal`. This sets the tone and what may be
  mentioned.
- `audience`: free text, for example "IND team via Geekbot, #daily-standup 09:30
  Mon to Fri".
- `tracker`: `linear` | `jira` | `github` | `none`, plus the team or project and
  the assignee ("me"). When a repo in the profile has a `ticket-update` profile
  (`.claude/ticketing*.md`), reuse its details instead of asking again.
- `authors`: the git author names and emails that count as Saad. Indus, client
  and personal work may use different emails.
- `working_days`: the default is Mon to Fri.
- `include` / `exclude`: optional repo or folder overrides.

### Evidence gathering (`gather.py`)

Input: the profile folder, the time window, and the authors. Output: one JSON
object written to the temp directory, never into the profile.

The window starts at `covered_until` in the last approved report, or at the start
of the previous working day if there is no report yet. It ends now.

| Source | What it reports | Notes |
|---|---|---|
| Repo discovery | every git repo under the profile, up to 3 levels deep | skips `node_modules`, `.venv`, `dist`, `build` and `graphify-out` |
| Git | the current branch, other branches touched in the window, commits by `authors`, and uncommitted or untracked files (counts plus up to ~10 paths per repo) | each git call has its own timeout, so a slow repo can't stall the run |
| Claude sessions | sessions whose `cwd` is inside the profile and that have activity in the window. For each: the repo, branch, first and last timestamps, active time (gaps over 30 min don't count), the AI title, the first few user prompts (cut to about 150 characters), and the files written or edited | match on the `cwd` field, not the folder names under `~/.claude/projects`, because those names are lossy |
| Non-repo folders | files changed in the window, by count and a few names | bounded depth, for folders like `PBS maker` |
| Ticket ids | `[A-Z]+-\d+` found in branch names, commits and session prompts | the tracker resolves them |
| PRs | PRs Saad opened, updated or reviewed in the window, through `gh` | runs only if the remotes are on GitHub and `gh` is signed in. If not, it says so and carries on. |

The script never sends anything outside the machine except read-only `gh` calls.
It runs in well under a minute for the current 15 repos.

### Drafting

1. **Pick the profile** from the current folder, or from the request ("for
   Enteyoes"). Ask if it's unclear, for example when run from the workspace root.
   Load `profile.md` and the last approved report.
2. **Run `gather.py`.** Read the tracker if the profile has one: tickets assigned
   to me that changed in the window or are In Progress or Todo, with estimate,
   due date and status. Also look up any ticket ids found in the evidence.
3. **Write the draft**, in the format in `report-format.md`:
   - **Yesterday:** group the evidence by ticket where there is one, and by
     outcome where there isn't ("Finished the chunker research: …"). Say what
     changed, not that work happened. If yesterday's report planned something
     that has no evidence now, list it as "planned, not seen", so Saad can
     confirm or drop it.
   - **Today:** a proposal, built from In Progress and Todo tickets, unfinished
     work (uncommitted files, open branches), and the "next" items from the
     last report. For `personal`, these are today's goals.
   - **Blocked:** blockers seen in session prompts or ticket status, plus any
     open blocker from the last report. If nothing was seen: "no (confirm)".
   - **Left:** with a tracker, the working days to the due date against the
     remaining estimate, giving on track, at risk or late. Without one, carry
     over the days Saad gave at the last approval and count them down. Mark
     these as guesses until he confirms.
   - **Other:** PR numbers reviewed, and rough active time per repo from
     session times. Meetings and mentoring can't be seen, so leave a visible
     gap: "meetings? (fill in)".
4. **Show it:**
   - the five answers;
   - a short list of what was guessed;
   - tracker mismatches, with an offer to run `ticket-update`;
   - a "not included" note for any evidence that was left out on purpose.

### Editing and approval

Saad edits in chat, as many rounds as he wants. Each round shows the full
revised draft. Saving happens only on clear approval ("good to go", "save it",
"looks good, save"). Until then nothing is written.

### The log

On approval, in `<profile>/.status/`:

- `YYYY-MM-DD.md`, the approved report exactly as approved, with the answers
  split into the five Geekbot sections. If there is a second report on the same
  day, it is saved as `YYYY-MM-DD-2.md`.
- `YYYY-MM-DD.json`, holding:
  - `covered_from` and `covered_until`;
  - the profile kind;
  - the ticket ids, each with its status and days left;
  - the Today items, with Saad's day estimates;
  - the open blockers.

  The next draft is built from this file.
- **Versioning (my call):** `.status/` is its own small local git repo, created
  on first save with no remote, and each approval is one commit. Profile folders
  are not repos, and this keeps the history versioned and offline without
  touching any project repo. Commit messages follow Saad's rules: no co-author
  trailer.

After saving, reply with the paste-ready blocks, one per question, and the path
of the saved file.

### Rules per kind

- **team:** ticket ids first, using the team's words. It's fine to name
  teammates as people who need to act.
- **client:** written as progress the client can read. No internal ticket noise
  unless the client shares the tracker, no other clients, and no internal
  people's names unless Saad adds them.
- **personal:** short and goal-shaped. Today is the list of goals. Blocked and
  Left are still useful to Saad.

### Decisions from the builder check (my calls)

- **Sessions started outside any profile.** Claude is often opened from the
  home folder or the workspace root, so a session may have a `cwd` outside every
  profile. Such a session still counts for a profile through the **files it
  edited**. But only file-level facts carry over: repo, file names and active
  time. Its title and prompts never do, because they may describe another
  profile's work. A session that edited files in two profiles adds those
  file-level facts to each profile separately. Old paths that no longer exist
  (`GitHub\Indus\…`, `GitHub\ZenTechSol\…`) are ignored.
- **Generic shipped skill.** The marketplace repo is public, so the skill files
  name no real client, team, channel or ticket. The workspace root, the kind of
  each profile, the tracker and the audience are all asked on first run and
  stored in that profile's `profile.md`. The defaults suggested on first run
  are: every top-level folder is a client, unless the user marks it personal or
  team. The worked example in `report-format.md` uses made-up names.
- **What a client sees.** Only the text Saad pastes. `.status/` is never sent.
  Even so, the saved report and JSON hold only approved text and small fields,
  so the folder stays safe if it is ever shared by mistake.

## Left to the builder

- The exact `gather.py` command-line flags and JSON field names. They should
  follow the table above, and the JSON should carry a `schema_version`.
- How to find PRs Saad reviewed (`gh search prs --reviewed-by @me`, or the
  GraphQL API). It is skipped cleanly if `gh` can't run.
- The exact on track / at risk / late rule. Default: **late** if past the due
  date; **at risk** if the remaining estimate is more than the working days
  left; otherwise **on track**. Show it as a guess.
- How many prompts to sample per session, and how to keep the summary under
  about 10k tokens for a busy week.
- The trigger wording in the skill description. It must include pasted Geekbot
  prompts ("It's time for Daily standup …") as well as "standup", "status report"
  and "what did I do yesterday".

## Open questions

None. Saad decided the profiles and audiences, that the draft is edited before
it is saved, that the tracker is read-only, and approach 1. Everything else above
is marked as my call or left to the builder.
