---
name: mockups
description: >-
  Use when the look of a screen, page, flow, component, form, modal, dashboard
  or layout is an open question and the user wants to see options before
  deciding: after brainstorming or a spec, when the feature is clear but its
  interface isn't, or when the user asks for a mock, mockup, wireframe, layout
  options or "show me what it could look like". Also for an interactive mock
  with realistic data that shows a hard problem to a non-technical reviewer.
  It makes 2 to 4 local HTML variants that differ in one clear idea each,
  using a frontend design skill when one is available and its own rules for
  layout, type, color and theme, compared side by side in rounds. Not for
  building the real UI, and not for a change already described exactly.
---

# Mockups

A fast mock is wrong on paper instead of wrong in code. This skill makes mocks;
it never implements the real thing. It ends by handing the chosen mock back to
the spec, or to whoever asked.

Mocks are throwaway, but the chosen one is kept as the reference. That covers
an interactive mock with realistic data, built to show a hard problem to
someone non-technical: it gets the same loop, and once approved, the feature
is built from the ground up against it.

## Where mocks go

Local, self-contained HTML files: CSS, JS and icons (as inline SVG) all inside
the file, so it opens straight from disk with no network. Put them where the
project's doc rule says. Otherwise put them in a `mocks/` folder next to the
spec, or in `docs/<feature>/mocks/` when there's no spec. Later rounds add
`-r2`, `-r3`, …. **Local files only:** no Artifact, hosted page or shared link
unless the user asks for one, and never production code.

**If a frontend or UI design skill is available in this session,** use it for
every variant without being asked: each variant agent loads it for the look.
The brief still wins on what stays the same and on the one idea each variant
tests. If no such skill is available, the design rules below are enough on
their own.

## The loop

1. **Intent.** What the screen is for, who uses it, its one primary action,
   and the data it shows. Read the spec if there is one, and look at the
   existing app's screens and styles, so the variants fit it.
2. **Research,** when the user doesn't yet know what it should look like:
   search the web for how comparable products solve the same screen, and base
   the variants on what you find. Note the sources in the brief.
3. **Brief.** A shared `BRIEF.md` in the mocks folder, so every variant starts
   from the same facts: the intent, the real-ish content, the design rules
   below, **what stays the same**, and **the one idea each variant tests**.
4. **Variants.** 3 by default (2 to 4), one HTML file each, built in parallel:
   one agent per file, each given the brief, writing only its own file and
   running no git commands.
5. **Compare.** An `index.html` that links the variants side by side, with one
   line per variant on its idea.
6. **The user's reaction.** Give the folder path, the differences in a few
   lines, and your recommendation. End the turn.
7. **Next round,** if it misses: a short critique in `FLAWS.md` of why the
   round missed, then a round that changes only what the user reacted to and
   keeps everything they didn't object to.

When the user is away, pick the variant you'd recommend, log the choice and
why, and hand back.

## How the variants differ

Each variant tests **one idea** about the screen, so the user compares ideas,
not noise. Pick the ideas from what's actually open:

- **Structure:** a table, cards, a split view (list and detail), a board or a
  timeline.
- **Navigation:** a sidebar, top tabs, or steps in a guided flow.
- **Density:** compact for power users, comfortable for occasional ones.
- **The primary action:** inline on each item, in a sticky bar, or as one
  focused flow.
- **Visual direction,** only when the look itself is open: for example quiet
  and neutral, bold and brand-led, or dense and data-first.
- **Copy,** when the wording is undecided too: vary it as well, not just the
  layout.

**What stays the same in every variant:** the data and content, the primary
action, the states, and the app's design system when it has one. Label one
variant as the safe choice, the one closest to the app's current patterns.

## Design rules for every variant

- **Start from the app.** If it has a design system (colors, type, spacing,
  components), every variant uses it, and the variants differ in structure
  and density. A new visual direction is only for apps with no settled look,
  or when the user asks for one.
- **Type.** At most two families: one for headings, one for text (one is
  fine). Use the app's fonts. Otherwise use a readable, deliberate pairing,
  as a system font stack or a web font with a full fallback stack, so the
  file works offline. Use a clear scale (for example 12, 14, 16, 20, 24 and
  32 px), body text at 14–16 px, line height 1.4–1.6, and lines no longer
  than about 70 characters. Use tabular figures for numbers in tables.
- **Color.** Define the palette once, as CSS variables at the top: background,
  surface, text, muted text, border, one accent, and success, warning and
  danger. The accent marks the primary action and the key data, not
  decoration. Body text contrast is at least 4.5:1.
- **Theme.** Light and dark from the same variables, following the system
  setting, with a toggle. Skip this only when the app has a single theme.
- **Spacing and shape.** One spacing scale in 4 or 8 px steps, aligned to a
  grid, with consistent corner radii and no more than two shadow levels.
- **Content.** Real-ish content where the hierarchy depends on it: real names,
  real lengths, realistic numbers, the longest likely value. No lorem ipsum.
- **States.** Every variant shows the default, empty, loading and error
  states and a populated example (a small state switcher is fine), and shows
  what reflows at phone width (390 px).
- **Charts,** if any: inline SVG, labelled axes and units, one palette color
  per series. No 3-D, and no pie charts for comparisons.
- **Avoid the template look:** no decorative gradients, no generic grids of
  hero cards, no emoji as icons, and not the same font and accent in every
  variant unless the app sets them.

## What a good mock settles

- The layout grid, and where the primary action sits.
- The hierarchy: what comes first, what's secondary.
- Every state: empty, loading and error are where UIs usually fail.
- What happens at small widths.
- Which parts become reusable components.

## Hand-back

Give the chosen file's path, and one line on what it decided. It becomes the
spec's visual reference: acceptance lines can point at it, the build implements
against it, and an audit of the built UI can check against it.
