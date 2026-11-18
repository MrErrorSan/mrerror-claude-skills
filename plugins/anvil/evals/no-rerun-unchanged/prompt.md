---
tags: [anvil]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write, Edit, Bash]
---

the slugify build is done. before I finish it, run the full suite through anvil (`anvil run --scope full -- python3 -m unittest discover -s tests`) and give me the summary line. then, right before you hand back to me, confirm once more that the suite is green on this tree. don't change any files in between.
