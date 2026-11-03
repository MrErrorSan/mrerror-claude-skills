---
name: ux-audit
description: >-
  Post-implementation UX review-and-improve pass. Use this right AFTER a UI is
  built or changed, and whenever MrError asks to "review the UX", "audit the UI",
  "improve usability", "check the design", "make it feel better", or "polish
  this screen". It reviews the implemented interface against concrete UX
  heuristics, reports ranked findings, and then applies the improvements. Anvil
  calls this automatically after any UI implementation, so trigger it as the
  closing step of front-end work even if the user doesn't ask by name.
---

# UX Audit — review the built UI, then improve it

A mock gets the structure right; the audit catches what only shows up once the
thing is real — missing states, weak hierarchy, accessibility gaps, awkward
feedback. Do this as the closing step of UI work.

## How to run it

1. **Look at the actual built UI**, not the code's intentions. If it's an
   artifact or local page, render/inspect it (the `superpowers-chrome` skill can
   open it and read the DOM/console). Check real behavior and real states.
2. **Audit against these heuristics** — go through each, don't skim:

   - **Hierarchy & clarity:** Is the primary action obvious within a second? Is
     the most important information the most prominent?
   - **States:** Are **empty**, **loading**, and **error** states all handled and
     not ugly or blank? (Most UX failures live here.)
   - **Feedback & affordance:** Do interactive elements look interactive? Is there
     feedback on click, submit, success, failure? Any dead-ends?
   - **Accessibility:** Keyboard reachable? Visible focus? Sufficient color
     contrast? Labels/alt text? Hit targets big enough?
   - **Responsiveness:** Does it hold up at phone width with no horizontal
     scroll? Does anything overflow or crush?
   - **Consistency:** Spacing, type scale, colors, and component patterns
     consistent with the rest of the app / design system?
   - **Content:** Is copy clear and concise? Are errors actionable ("what do I do
     now") rather than codes?

3. **Report findings ranked by impact** — severity first, each with the concrete
   problem, where it is, and the fix. Separate "should fix now" from "nice to
   have".
4. **Apply the fixes.** This skill improves, it doesn't just critique. Make the
   high-impact changes, then note anything deferred. Re-check the states you
   touched.

## Output shape

```markdown
## UX Audit — <screen/component>

### Fix now (high impact)
1. <problem> — <where> — <fix>  → applied ✓ / proposed

### Consider (lower impact)
- <problem> — <fix>

### States checked
- empty ✓ / loading ✓ / error ✓  (note any still missing)
```

Keep the tone constructive and specific — "the submit button gives no feedback
on click, so users double-submit" beats "improve the button".
