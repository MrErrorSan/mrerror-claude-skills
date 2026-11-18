---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

just merged the retry fix for the webhook sender, PR #45 — can you update the ticket and give me my standup line?

Context for this dry run (don't run any tracker tool or CLI, and don't touch git): this repo has no CLAUDE.md and no ticketing profile. In this session there is a Jira (Atlassian) MCP server connected, and the gh CLI is signed in. The git remote is github.com/acme/hooks. Recent commits look like: "ABC-312 add retry with backoff", "fix flaky test (#41)", "ABC-298 webhook signing". Write what you would do next, including any message you'd send me, into response.md.
