---
name: ui-mockup
description: >-
  Mock-first UI policy. Use this BEFORE writing any front-end implementation —
  the moment the task involves a screen, page, view, component, form, modal,
  dashboard, layout, or any visual UI. Trigger on "build the UI", "add a page",
  "create a component", "design the screen", "lay out the dashboard", or any
  request that will end in rendered interface, even if the user says "just build
  it". Produce a layout/mockup and get alignment on structure first, then
  implement — never jump straight to production UI code.
---

# UI Mockup — design the layout before you build it

Jumping straight into production UI code is where time gets wasted: you build
real components, wire real state, then discover the layout or hierarchy was
wrong and rework it. A fast mock surfaces those decisions before they cost
anything to change.

## The flow

1. **Clarify the intent** — what is this screen for, who uses it, what's the one
   primary action, what data does it show.
2. **Produce a mock FIRST.** Pick the lightest form that communicates structure:
   - A **low-fi wireframe / layout mock** as an HTML artifact (use the
     `artifact-design` skill for layout, type, spacing, and light/dark; use
     `dataviz` if it contains charts, meters, or KPI tiles). This is the default
     for anything non-trivial — it's visual and fast to react to.
   - For something simple, an **ASCII/box layout sketch** inline is enough.
   - Show real-ish content, not lorem where it matters, so hierarchy reads true.
3. **Cover the states in the mock**, not just the happy path: default, **empty**,
   **loading**, **error**, and a populated example. Show the responsive intent
   (what stacks/reflows at phone width).
4. **Align before implementing.** Present the mock and ask for a quick thumbs-up
   or changes. In `afk` mode, treat layout choices as reversible — pick the
   recommended layout, note it, and keep going, but still produce the mock so it
   lands in the review doc.
5. **Then implement** against the agreed mock, handing off to the normal build
   workflow (Anvil). After implementation, the `ux-audit` skill reviews it.

## What a good mock decides before any real code

- The layout grid and where the primary action sits.
- Visual hierarchy: what's biggest/first, what's secondary.
- The full set of states (empty/loading/error are where UIs usually fail).
- Responsive behavior at small widths.
- Component boundaries — what becomes a reusable piece.

Keep the mock cheap. Its job is to be wrong on paper instead of wrong in code.
