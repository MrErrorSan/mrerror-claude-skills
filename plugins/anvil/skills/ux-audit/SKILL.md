---
name: ux-audit
description: >-
  Use when `anvil:verify` checks a UI the topic changed, against the chosen
  mock when there is one, or when Saad asks to review the UX, audit the UI,
  check usability or the design, or polish a screen.
---

# UX Audit

A mock gets the structure right; the audit catches what only shows once the UI is real: missing states, weak hierarchy, accessibility gaps, awkward feedback. It reports findings to the caller and doesn't apply fixes: in verify, the findings go through the fix loop.

## How to run it

1. **Look at the built UI,** not the code's intentions. Use chrome-devtools-mcp (navigate, act, take a snapshot or screenshot, read the console); playwright-core if the MCP isn't available. Check real behavior and real states. Save screenshots where the caller keeps its notes.
2. **With a mock** (`<topic folder>/mocks/`), compare against it: layout, hierarchy, states, small widths. **Without one,** use the heuristics alone.
3. **Go through each heuristic:**
   - **Hierarchy:** the primary action is obvious within a second; the most important information is the most prominent.
   - **States:** empty, loading and error are handled, not blank or broken.
   - **Feedback:** interactive elements look interactive; click, submit, success and failure give feedback; no dead ends.
   - **Accessibility:** keyboard reachable, visible focus, enough contrast, labels and alt text, hit targets big enough.
   - **Small widths:** holds at phone width with no horizontal scroll or crushed content.
   - **Consistency:** spacing, type scale, colors and component patterns match the rest of the app.
   - **Content:** copy is clear; errors say what to do next.
4. **Report** to the caller, in the shape below.

## Findings

Rank each finding **P0** (broken or blocks the main path), **P1** (a real problem users will hit) or **P2** (polish). Mark each **tested** (seen in the running UI) or **code-only** (read in the code, not exercised). Name where it is and the fix you'd suggest. A finding that is a design choice the mock and spec don't settle is flagged for Saad's call.

```markdown
## UX audit: <screen>
- P0 tested: <problem>, <where>. Fix: <suggestion>.
- P1 code-only: <problem>, <where>. Fix: <suggestion>.
- Saad's call: <choice the mock and spec leave open>.
States checked: empty, loading, error (note any missing).
```

Be specific: "the submit button gives no feedback on click, so users double-submit" beats "improve the button".
