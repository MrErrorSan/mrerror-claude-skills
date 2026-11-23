# MrError Claude Skills

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace. One
bundle plugin — **anvil** — carries an opinionated engineering workflow on top of
[Superpowers](https://github.com/obra/superpowers).

> Policy over capability: these skills encode *how work should flow* (when to
> test, parallel vs sequential, mock-first UI, cross-model research). Apart from
> `anvil`, which governs Superpowers, each skill stands alone and uses whatever
> tools the machine has when it runs.

## What's inside `anvil`

| Skill | Fires when | Does |
|---|---|---|
| **anvil** | any non-trivial build / implement / plan task | Workflow governor over [Superpowers](https://github.com/obra/superpowers). Picks one of three paths: **just do it** for linear work (no docs, stops or subagents), **spec first** (one short spec-and-plan, one stop) for open product questions, and **full** (spec stop, plan stop, parallel waves of at most 4 agents with a spec check after each) for large or risky work. Lean contract plans, implement-then-test (a bug fix always starts with a failing repro test), one final verification that also ticks off what was asked. When it conflicts with a Superpowers skill, Anvil wins. |
| **afk** | "afk", "I'm going to bed", "just finish it" | Keeps working until the work is done. Any skill or workflow's stop (an approval, a choice, a checkpoint) is passed with a ruling and logged. **Leaves commits to the workflow and project rules, hard-stops on destructive / outward actions**, and hands back one decision log. Works with or without any other skill. |
| **mockups** | after brainstorming or a spec, when the interface is still unclear; you ask for mocks; or an interactive mock to show a hard problem | 2–4 local HTML variants, each testing one idea (structure, navigation, density, visual direction), with built-in rules for type, color, light/dark theme, spacing and states. Web research first when the look is unknown. Compared side by side, in rounds. |
| **web-audit** | a page or UI was built or changed; "audit this page"; or you name a category ("check SEO", "responsiveness on 390 and 768") | By default audits only UI and UX at one target screen size, against the spec and mock (missing, different, extra). Responsiveness, accessibility, SEO, performance, technical and content are categories it adds only when asked. Uses whatever browser tooling the machine has, and asks before installing any. Ranks findings P0/P1/P2 by user harm and reports; fixes are your call. |
| **ticket-update** | a repo whose work is tracked; "update the tickets", "break this plan into tickets" | Detects whichever tracker the project uses (asks when unsure, offers a local `docs/tickets.md` when there's none), writes tickets an agent can build from, keeps status and evidence comments current, only touches your own tickets. |
| **standup** | "standup", "daily status", "what did I do yesterday", or a pasted stand-up bot prompt | Drafts the stand-up (Yesterday, Today, Left, Blocked, Other) for the folder you work from: what you say first, then Claude sessions, git activity, uncommitted work, PRs and tracker tickets as evidence. You edit; on "good to go" it saves the approved text to `~/standups/YYYY-MM-DD.md` (+ `.json`) in your home folder, the one place for every report whichever repo you're in, which keeps the next day consistent. Drafts follow your own writing voice from `~/standups/voice.md` (built, when you agree, from messages you sent on your own chat account) so they don't read as machine-written. Reads the tracker, never writes to it. |
| **cross-model** | only when you ask ("use cross-model", "research this with another model too"); never on its own | **Two-track research**: Claude subagents and a model from another family that this machine can reach (any CLI, API key or local router you've set up; the cheapest model it offers) research the same question independently, then Claude compares and consolidates. Falls back to Claude-only, and says so. |

Progressive disclosure keeps it cheap: ~1.2k tokens always-on; each skill's full
body loads only when it triggers.

### Session-start hook

Anvil also ships one `SessionStart` hook (about 500 tokens per session):

- **Machine rules**, in every session: reports and plans are local Markdown files
  in the repo, never Artifacts or hosted pages; no Claude co-author trailers or
  "Generated with" footers; a second model family only when you ask. Text in
  [`plugins/anvil/hooks/machine-rules.md`](plugins/anvil/hooks/machine-rules.md).
  Your own `CLAUDE.md` and requests still win.
- **Multi-machine sync**, only in repos that opt in by committing
  `.claude/rules/remote-sync.md` (the rule itself, which Claude Code also loads
  natively). The hook fetches (capped at ~5 s) and tells Claude whether the branch
  is behind, diverged, unpushed or dirty, so it pulls before editing. It never
  pulls, commits or pushes itself.

## Prerequisites

- **Claude Code** `>= 2.1.290`.
- **Superpowers** from the official marketplace
  (`superpowers@claude-plugins-official`). Anvil governs it and doesn't install
  it for you.

## Install

```bash
# 1. Superpowers, if it isn't installed yet
claude plugin install superpowers@claude-plugins-official

# 2. add this marketplace
claude plugin marketplace add MrErrorSan/mrerror-claude-skills

# 3. install anvil at user scope
claude plugin install anvil@mrerror-claude-skills
```

Then **restart Claude Code** (or `/reload-plugins`) so the skills load.

Verify:

```bash
claude plugin details anvil@mrerror-claude-skills   # should list 7 skills and 1 hook
```

### What gets installed

`anvil`, its 7 skills and its session-start hook. Nothing else is installed automatically. Parallel
work uses Claude Code's built-in `Agent` tool.

If you have loose copies in `~/.claude/skills/anvil` or `~/.claude/skills/afk`
from before the plugin, move them out: otherwise both versions load.

## Optional: a second model for `cross-model`

`cross-model` uses whatever second model family the machine can reach when you
ask for it: a model CLI signed in with your subscription, an API key in the
environment, or a local OpenAI-compatible router. It lists the backend's models
each time and picks the cheapest, so adding a new provider later needs no new
skill. With nothing set up, it runs Claude-only and says so. How it finds and
drives a backend, and the quirks already met, are in
[`plugins/anvil/skills/cross-model/references/backends.md`](plugins/anvil/skills/cross-model/references/backends.md).

## Updating

This marketplace tracks its git source. After pulling or editing:

```bash
claude plugin marketplace update mrerror-claude-skills
# or, inside Claude Code:
/reload-plugins
```

Bump `version` in `plugins/anvil/.claude-plugin/plugin.json` for meaningful changes.

## Editing the skills

Plain `SKILL.md` files under `plugins/anvil/skills/`. Each is just YAML
frontmatter (`name`, `description`) + Markdown instructions — edit, reload, done.
`cross-model` keeps backend wiring in `references/backends.md` so adding a new
provider doesn't touch the skill logic.

## Uninstall

```bash
claude plugin uninstall anvil@mrerror-claude-skills
claude plugin prune                 # remove now-unused auto-installed deps
claude plugin marketplace remove mrerror-claude-skills
```

## Layout

```
.claude-plugin/marketplace.json          # marketplace manifest + cross-marketplace allow-list
plugins/anvil/
  .claude-plugin/plugin.json             # plugin manifest + dependencies
  hooks/                                 # session-start: machine rules + repo sync check
  skills/
    anvil/SKILL.md                       # workflow governor
    afk/SKILL.md                         # unattended mode
    mockups/SKILL.md                     # mock variants, in rounds
    web-audit/SKILL.md                   # UI, UX, accessibility and SEO audit of web pages
    cross-model/SKILL.md                 # two-model research, only when asked
    cross-model/references/backends.md   # pluggable model backends
    ticket-update/SKILL.md               # tracker updates and ticket writing
    ticket-update/references/            # trackers, templates, profile, calibration
    ticket-update/evals/                 # claude plugin eval cases
    standup/SKILL.md                     # daily stand-up drafts and log
    standup/scripts/gather.py            # evidence gatherer (Python stdlib)
    standup/references/report-format.md  # questions, rules, example, log format
    standup/references/voice.md          # writing in the user's voice; building the guide
    standup/evals/                       # claude plugin eval cases
tests/                                   # unit tests for gather.py and the hook (not shipped)
```

## Notes

`anvil` is the only skill tied to another plugin: it governs Superpowers and
does nothing without it. Every other skill stands alone. It names no other
skill, tool or model, finds what the machine has when it runs, and asks before
installing anything.

MIT. Personal tooling — use at your own discretion.
