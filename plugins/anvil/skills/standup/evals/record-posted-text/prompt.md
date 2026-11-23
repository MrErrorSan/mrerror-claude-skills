---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write]
---

record, this is my standup message:

Yesterday: which tickets did you finish or move?
• ACME-68 → Done: pricing page live; waiting for marketing's sign-off.
Today: which tickets are you working on?
• ACME-71: start the coupon rules, beginning with the validation.
• ACME-70: late (was due 3 Mar).
Left: for each ticket in progress, how many days remain, and is it on track / at risk / late?
• ACME-71: due tomorrow (1 day left), on track.
• ACME-70: late (was due 3 Mar), new date 11 Mar.

Context for this dry run (don't run any tracker tool, CLI or git command): today is Monday 2026-03-09, and the folder you were opened in is the repo /work/shop. Running the stand-up script would print log.dir = /home/me/standups and log.save_report_to = /home/me/standups/2026-03-09.md. The tracker shows ACME-68 Done, ACME-71 In Progress due 2026-03-10, and ACME-70 In Progress, still due 2026-03-03. Write what you would do and reply, including the paths you would save to, into response.md.
