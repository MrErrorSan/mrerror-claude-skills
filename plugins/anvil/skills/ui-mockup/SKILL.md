---
name: ui-mockup
description: >-
  Use when the look of a screen, page, component, form, modal, dashboard or
  layout is an open question and Saad wants to see options before deciding:
  when `anvil:brainstorm` hands over its mock exploration loop, or when Saad
  asks for a mock, wireframe or layout options. Not for building the real UI.
---

# UI Mockup

A fast mock is wrong on paper instead of wrong in code. This skill makes mocks; it never implements the UI. It ends by handing the chosen mock back to `anvil:brainstorm`, or to whoever called it.

## Where mocks go

Mocks are local, self-contained HTML files (CSS and JS inlined, so they open straight from disk) in `<topic folder>/mocks/`. Later rounds add `-r2`, `-r3`, …. They are throwaway: never a hosted page, never production code.

## The loop

1. **Intent.** What the screen is for, who uses it, its one primary action, the data it shows.
2. **Brief.** A shared `BRIEF.md` in the mocks folder: the intent, the real-ish content to show, the states to cover.
3. **Variants.** 2 to 4 layouts, one HTML file each, built in parallel (one agent per file). Each covers the default, empty, loading and error states and a populated example, and shows what reflows at phone width. Use real-ish content where hierarchy depends on it.
4. **Compare.** An `index.html` that links the variants side by side, plus a screenshot of each.
5. **Saad's reaction.** Show him the folder path and the differences in a few lines. End the turn.
6. **Next round,** if it misses: a short critique in `FLAWS.md`, then a round that changes only what he reacted to.

In AFK, pick the variant you'd recommend, log the choice and why in the decision log, and hand back.

## What a good mock settles

- The layout grid and where the primary action sits.
- The hierarchy: what comes first, what is secondary.
- Every state, since empty, loading and error are where UIs usually fail.
- What happens at small widths.
- Which parts become reusable components.

## Hand-back

Give the caller the chosen file's path and one line on what it decided. In brainstorm it becomes the spec's visual reference; the build implements against it later, and `anvil:ux-audit` checks the built UI against it in verify.
