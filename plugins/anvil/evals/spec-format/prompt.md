---
tags: [anvil]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Agent, Write, Edit, Bash]
---

I want a CSV export in ledger: `python3 -m ledger export --csv <path>` writes every invoice to that file, one row per invoice, columns id, customer, total, issued, with a header row first. Totals in currency units with two decimals (12.50, not 1250), issued as an ISO date, rows oldest first. Customer names can contain commas, so quote properly. It's for our accountant to open in a spreadsheet. Use `csv-export` as the topic name. Treat it as full size, and put anything still open under "Waiting on you" in the spec rather than asking me first. Write the spec up and stop there for my review; nothing gets planned or built yet.
