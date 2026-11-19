# Anvil plugin skills: intent, value and fit

- **Date:** 2026-11-19
- **Branch:** `anvil-og-next` (plugin 0.2.0). Nothing committed yet.
- **Renamed 2026-11-19:** `ui-mockup` is now `mockups`, and `ux-audit` is now `web-audit` (by default it audits UI and UX at one target screen size; responsiveness, accessibility, SEO, performance, technical and content run only when asked).
- **Related:** [2026-11-19-og-grievances-and-fixes.md](2026-11-19-og-grievances-and-fixes.md) covers the governor in depth.

## The design rule (yours, 2026-11-19)

- **`anvil` has one job: guiding Superpowers.** Superpowers is its only dependency. It doesn't mention your other skills.
- **Every other skill stands alone:**
  - It names no other skill, tool or model.
  - It looks at what the machine has when it runs, and uses that.
  - When something it needs is missing, it says so, recommends the option it would pick, and installs only with approval.
  - Adding a new tool or provider later (another model subscription, a new tracker) should need at most a small edit, never a new skill.
- **A skill holds what you'd otherwise explain to Claude again and again.** Anything Claude already does by default is bloat.
- **Local files only, in every skill, Anvil included.**
  - All output is a file on this machine, in the repo.
  - No Artifacts, hosted pages or shared links unless you ask for one.
  - The only outward writes are the ones that are the skill's job: ticket content to the tracker, and the brief to the second model.
- **Use what helps when it's there.** `mockups` uses a frontend design skill automatically when one is available, and works fully on its own rules when none is.

## Intent and fit

| Skill | What you built it for | Before | Now |
|---|---|---|---|
| `anvil` | You like Superpowers, but it's slow and you dislike some parts. A governor keeps the liked parts working and getting upstream updates, and steers the rest | It fit. It had picked up a table routing to your other skills | Names only Superpowers. The routing table and the ticket line were removed. 19.2k |
| `afk` | Keep working until the work is done, through the night. Whatever stops (Superpowers or any other skill), a ruling says how to get past it. Decide on your behalf | Named Anvil's stops only; pointed at Anvil for commits | "Passing a stop": a ruling for each *kind* of stop (approve a document, choose an option, a checkpoint, stop-and-ask, a finishing menu, a never-unlocked action), whichever skill raises it. Names no other skill. Plus the early-stop list |
| `ticket-update` | Keep the tracker in step with the real work, so seniors can see progress, with whichever tracker you have | Had a section tied to Anvil's plan format, and no answer for "no tracker" | "From a written plan" works with any plan. With no tracker, it offers a local `docs/tickets.md` in the same format. Tracker names appear only as things to detect |
| `mockups` | After brainstorming or a spec, when the UI is unclear. All the instructions you used to repeat: how variants differ, layouts, how many, fonts, themes, colors | Leaned on other skills for the look | Holds its own rules: how variants differ (structure, navigation, density, primary action, visual direction, copy), what stays the same, type, color variables, light and dark theme, spacing, content, states, charts, what to avoid. 3 variants by default |
| `web-audit` | Catch mistakes and what your intent has but the mock misses, plus SEO. Find the tools on the machine; if none, recommend and ask before installing | Named specific browser and audit tools | Finds whatever browser tooling exists. If there's none, it recommends the option it would pick and asks before installing, or audits the code only. By default it audits only UI and UX at one target screen size, spec and mock first. Responsiveness, accessibility, SEO, performance, technical and content are categories it runs only when asked; naming one audits just that one |
| `cross-model` | Research only: Claude subagents plus another model family on the same question, then consolidate. Use the cheapest model available. Adapt when you add a provider | Hard-wired to one CLI and named models | Discovers model CLIs, configured API keys and local routers. Picks your stated preference or the cheapest model, listed fresh each time. Manual only. `backends.md` explains how to drive an unfamiliar CLI and keeps notes on the one met so far, with no model names |

## Value: is any of it bloat?

None of the six is pure bloat. Each holds instructions you'd otherwise repeat:

- **anvil:** the routing table and "speed levers" were removed.
- **afk:** about a third restates what plain Opus 5.5 already does. In the A/B AFK case it asked nothing, 0 of 3 runs. It's kept because the arm using it scored best. The decision-log file, the safety floor, the stop rulings and the early-stop list aren't default behaviour.
- **ticket-update:** none. Team rules are what skills are for.
- **mockups:** none. It's grown, because it now carries the design rules itself instead of depending on another skill.
- **web-audit:** kept small by scope. UI and UX by default, every other category only on request, so an audit is only as big as the question. The value is the spec comparison and the report format.
- **cross-model:** none. The CLI gotchas are what Claude can't know.

## Fit with the Opus 5.5 guidance

| Guidance | Where it's applied |
|---|---|
| Plain words; emphasis makes rules over-apply | All descriptions are plain and under the 1,536-character cut-off |
| A reviewer asked to find problems always finds something | The governor's per-wave spec check and final review skip style |
| Opus 5 delegates eagerly | Parallel agents run on the governor's Full path only, at most 4. Mock variants are independent files |
| Unattended runs end early in four named ways | AFK's "Ending too early" |
| Gotchas are the highest-value content | `cross-model`'s backend gotchas, AFK's stop rulings |

## Outside the repo

- `~/.claude/commands/research.md`: fixed after the dead model broke it.
- `~/.claude/skills/cross-model-review` and `~/.claude/CLAUDE.md`: now manual-only.
- `cross-model-review` stays as a loose skill: diff review is not part of Anvil (decided 2026-11-19). The global CLAUDE.md routes research to the plugin's `cross-model` and diff review to `cross-model-review`.
- `agy-review` and `xreview.ps1` still hard-code a model that's gone. They're review tools, outside the research-only intent.

## Still open

1. Deploy 0.2.0 at user scope, and remove the loose `~/.claude/skills/{anvil,afk}` copies. Keep `cross-model-review`.
2. Measure the governor: 7 cases × 1 run against the original (about $4).
3. Commit. Whether to add the repo `CLAUDE.md` (commit and push after every unit of work) from `anvil-v2` is your call.
