---
tags: [anvil]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write, Edit, Bash]
---

change of direction on the csv-export build: the accounting tool this feeds wants semicolons between columns, not commas. I know that replaces what we agreed in the spec, and I'm fine with redoing whatever it touches. Update the spec, the plan and progress for it and tell me what reopens. Don't rebuild anything yet, I'll restart the build after lunch.
