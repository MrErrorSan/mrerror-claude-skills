# Trackers: detection and mechanics

Read this when you are choosing the tracker, or when you are about to write to
one you haven't used in this session. Tool names depend on how each server or
CLI was installed. **Check the tools you actually have.** Don't trust a name
written here.

## Contents
1. Detection signals
2. Concept map (one table)
3. Notes per tracker: Linear, Jira, GitHub Issues, GitLab, Azure DevOps, others

---

## 1. Detection signals

Collect the signals before you decide. A **usage** signal shows that the team
uses this tracker. A **tool** signal shows that you can write to it. You need
both.

| Signal | Kind | How to check |
|---|---|---|
| Rules or profile name the tracker, team, project or parent id | usage | Read `CLAUDE*.md`, `.claude/rules/*` and `.claude/ticketing*.md` |
| Ticket ids in branches or commits | usage | `git branch -a`, `git log --oneline -30`. `ABC-123` suggests Linear, Jira or YouTrack (the profile tells them apart). `#123` suggests GitHub or GitLab. `AB#123` suggests Azure Boards. |
| Links to tracker sites in docs and PRs | usage | Grep for `linear.app`, `atlassian.net`, `/issues/`, `dev.azure.com`, `app.shortcut.com`, `app.clickup.com` |
| Git remote host | weak usage | `git remote -v`. github.com and gitlab.* only suggest that the code lives there, not that tickets do. |
| MCP tools in this session | tool | Look in the tool list for names containing `linear`, `atlassian`/`jira`, `github`, `gitlab`, `azure`/`ado`, `shortcut`, `clickup`, `asana`, `notion` |
| CLIs on PATH and signed in | tool | `gh auth status`, `glab auth status`, `az account show` (plus the `azure-devops` extension), `jira me`, `acli` |

**Ask when the signals are not clean.** Use the question tool, list the trackers
you found with what you saw for each, and offer "None, don't track this repo".
If the user picks a tracker you can't reach, explain how to connect it (for
example, the claude.ai connector settings, `claude mcp`, or `gh auth login`).
Then save the choice in the profile so that you never ask again.

---

## 2. Concept map

| Concept | Linear | Jira | GitHub Issues | GitLab | Azure DevOps |
|---|---|---|---|---|---|
| Ticket | issue | issue (Story, Task, Bug, Sub-task) | issue | issue / task | work item (User Story, Task, Bug) |
| Parent | `parent` (sub-issue); feature parent issue | `parent` (epic, or the parent of a sub-task) | sub-issues | epic (Premium) or a parent issue with child tasks | `Parent` link |
| Project / milestone | project + project milestone | project + fix version or sprint | milestone, or a Projects (v2) board | milestone, iteration | area path + iteration path |
| Estimate | `estimate` (team point scale) | story points (a custom field whose id varies) | a Projects v2 number field; otherwise a `size:N` label or a line in the body | `weight` | `Microsoft.VSTS.Scheduling.StoryPoints` |
| Due date | `dueDate` | `duedate` | a Projects v2 date field, or the milestone's date | `due_date` | `Microsoft.VSTS.Scheduling.DueDate` (or the TargetDate) |
| Labels | labels (per team) | labels | labels | labels (scoped `area::x` works well) | tags (separated by `;`) |
| Priority | 0–4 (1 = urgent) | priority | a label or a Projects field | a label, or `/severity` on incidents | `Microsoft.VSTS.Common.Priority` 1–4 |
| Blocks / blocked by | relations `blocks`, `blockedBy` | issue link "Blocks" | issue dependencies, where enabled | linked issues "blocks" (Premium); otherwise "relates to" | Predecessor / Successor links |
| Status | per-team workflow states | **transitions**, not a field | open/closed plus a Projects Status field | open/closed plus labels or a board | `System.State` |
| Collapsible agent notes | `+++ Agent notes` … `+++` | the `{expand:Agent notes}` macro in wiki markup; otherwise an `## Agent notes` heading at the end | `<details><summary>Agent notes</summary>` … `</details>` | `<details>` as on GitHub | the description is HTML: `<details>` is unreliable, so use a heading |

**When a concept has no native field** (for example, an estimate on plain GitHub
Issues), put it in one line at the top of the body:
`Estimate: 2 · Due: 2026-11-20 · Priority: High`. Say once during setup which
concepts this tracker can't hold natively.

---

## 3. Notes per tracker

### Linear (MCP)
- The `save_*` tools create when you leave out `id`, and update when you pass
  it. Send only the fields that change. For a long description, send a `patch`
  instead of the full body.
- **`labels` replaces the whole label set.** Use `addLabels` and `removeLabels`
  to change one label at a time.
- Statuses and labels belong to the team. Call `list_issue_statuses` or
  `list_issue_labels` before you set an unfamiliar one.
- `get_issue` leaves out the discussion. Read comments with `list_comments`.
- The tools accept readable references (`IND-123`, a team key, `"me"`, an
  email), so you rarely need to look up ids first.
- Lists come in pages. Follow the cursor while `hasNextPage` is true before you
  conclude that no matching ticket exists.
- The connection may be signed in as someone else (for example, the team lead
  connected the workspace). Then "creator" is that person. Set the `assignee`
  explicitly. When you study "their" tickets, filter out the ones made for you
  (see calibrate.md).

### Jira (Atlassian MCP, `acli`, or `jira-cli`)
- Find the cloud id or site first. Then search with JQL, for example
  `project = ABC AND assignee = currentUser() AND statusCategory != Done`.
- **Status changes are transitions.** Get the available transitions for the
  issue, then apply one by its id. You can't set the status as a field.
- The story points field is custom, and its id differs between sites and
  between team-managed and company-managed projects. Look it up once and save
  the id in the profile.
- Assignees are account ids. Look up "me" once and save it.
- Some tools take Markdown and convert it to ADF. If tables or macros come out
  broken, simplify them to headings and bullets.
- If no tool can create issue links, write the `Blocked by` line in the body
  and tell the user that the link must be added by hand.

### GitHub Issues (`gh`, or the GitHub MCP)
- `gh issue create --title … --body-file … --assignee @me --label … --milestone …`;
  `gh issue edit`; `gh issue comment`; `gh issue close --reason completed` (or
  `--reason "not planned"` to cancel).
- **Sub-issues** and **issue dependencies** exist on github.com through the REST
  API (`gh api`). Check that they work in this repo before you rely on them.
  Otherwise, use a task list on the parent and the text line.
- Estimates and due dates live in a **Projects (v2)** board when the team uses
  one: `gh project item-add`, then `gh project item-edit` with the field ids,
  which you can find with `gh project field-list`. Without a board, use the
  line at the top of the body.
- Write the body to a temp file and pass `--body-file`. Shell quoting breaks
  Markdown in long bodies.

### GitLab (`glab`, or the GitLab MCP)
- `glab issue create/update/note/close`, with `--weight`, `--due-date`,
  `--milestone`, `--label` and `--assignee @me`.
- Quick actions in a note also work: `/weight 2`, `/due 2026-11-20`,
  `/label ~"type::bug"`, `/assign me`, `/blocked_by #12`. Blocking links and
  epics need Premium. Fall back to `/relate` plus the text line.

### Azure DevOps (`az boards`)
- `az boards work-item create --type "User Story" --title … --fields
  "Microsoft.VSTS.Scheduling.StoryPoints=2" "System.Tags=AI;Feature"`.
- `az boards work-item relation add --id N --relation-type parent
  --target-id P`. For order, use `Successor` or `Predecessor`.
- The description and comments are HTML. A comment is a write to
  `System.History`.

### Others (Shortcut, ClickUp, Asana, Notion, YouTrack, Plane, Trello)
Go through the concept map row by row. Find each concept's field through the
tool's own "describe" calls, write down in the profile what you found, and use
the body line for anything with no native field. The ticket form, the comment
log and the 3-day rule are the same in every tracker. Only the mechanics change.
