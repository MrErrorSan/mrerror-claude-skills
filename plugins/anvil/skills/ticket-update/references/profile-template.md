# Ticketing profile template

Copy this to `.claude/ticketing.md` (shared with the team) or
`.claude/ticketing.local.md` (this machine only, kept out of git with
`.git/info/exclude`). Delete any line where the skill default is fine. Personal
details (name, email, account id) belong in the `.local.md` file.

```markdown
# Ticketing profile

Read by the ticket-update skill. This overrides its defaults; the project's
rule files override this.

## Where
- Tracker: <Linear | Jira | GitHub Issues | GitLab | Azure DevOps | ...>
- Access: <MCP server name | CLI, e.g. `gh`>
- Workspace / site: <...>
- Team / project key: <e.g. IND>
- Project: <e.g. DipGos>   Milestone: <e.g. AI & Workflow>
- Parent for this repo's work: <e.g. IND-214>. New work becomes sub-tickets here unless it clearly belongs elsewhere.

## Who
- Assignee ("me"): <name>, <tracker handle or email>
- The connector is signed in as: <name, if it isn't the assignee. Expected, so set the assignee explicitly.>
- Never touch tickets of: <everyone else | specific names>

## Fields
- Estimate: 1 point = 1 day, at most 3   <or the team's scale>
- Labels: area `<e.g. AI/RAG>` + one type from <Bug, Feature, Improvement, Research, Security, Performance, Database, DevOps, Frontend>
- Priority: always set
- Custom field ids: <e.g. Jira story points = customfield_10016>

## Style
- Title: `<Feature> <n>: <outcome>`   <or the team's style, e.g. `<Feature> · <n>: <outcome>`>
- Gate commands for "Done when": <e.g. `make check`, `uv run poe check`>
- Specs live in: <e.g. docs/specs/>
- Ticket-pattern study: <docs/YYYY-MM-DD-ticket-patterns.md, if one exists>

## Rhythm
- Automatic updates allowed: <yes: status, comments and fields on my own tickets | ask first>
- Week starts: <Monday>. Create that week's tickets then, not all up front.
- Stand-up: <tool/channel, time>, e.g. Geekbot, #daily-standup, 09:30 Mon–Fri
- Stand-up format: `<ID>, <what changed>, <time left>, <on track | at risk | blocked by X>`
```
