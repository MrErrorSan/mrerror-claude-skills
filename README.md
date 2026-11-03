# MrError Claude Skills

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace. One
bundle plugin — **anvil** — carries an opinionated engineering workflow and
auto-installs the capability plugins it builds on.

> Policy over capability: these skills encode *how work should flow* (when to
> test, parallel vs sequential, mock-first UI, cross-model review) and orchestrate
> the community capability plugins underneath instead of reinventing them.

## What's inside `anvil`

| Skill | Fires when | Does |
|---|---|---|
| **anvil** | any non-trivial build / implement / plan task | Workflow governor over [Superpowers](https://github.com/obra/superpowers): tiered decision procedure, an override table, **parallel-agent plans** (not sequential), **implement-then-test** with a single end-of-work verification pass, lean contract plans. When it conflicts with a Superpowers skill, Anvil wins. |
| **afk** | "afk", "work autonomously", "just finish it" | Runs a plan to completion unattended: turns every question into a documented assumption + decision, **hard-stops on commits / destructive / outward actions**, and hands back one decision log. |
| **ui-mockup** | before any UI / screen / component / layout | Mock + align on structure (incl. empty / loading / error states) **before** writing production UI. |
| **ux-audit** | after UI is built; "review the ux" | Audits the built UI against UX heuristics, reports ranked findings, applies fixes. |
| **cross-model** | before calling work done, expensive-to-reverse decisions, a problem that failed twice, research | Backend-agnostic **second-model review/research** with AGREE / DISAGREE / NEEDS-CHECK triage. Uses Antigravity CLI (`agy`) on a Gemini subscription by default, or a router / API key, or falls back to Claude-only. |

Progressive disclosure keeps it cheap: ~1.2k tokens always-on; each skill's full
body loads only when it triggers.

## Prerequisites

- **Claude Code** `>= 2.1.290`.
- The **superpowers-marketplace** must be added first, because `anvil` declares
  cross-marketplace dependencies on it. (Step 1 below.)

## Install

```bash
# 1. add the dependency marketplace FIRST (anvil depends on superpowers)
claude plugin marketplace add obra/superpowers-marketplace

# 2. add this marketplace
claude plugin marketplace add MrErrorSan/mrerror-claude-skills

# 3. install anvil — its dependencies install automatically
claude plugin install anvil@mrerror-claude-skills
```

Then **restart Claude Code** (or `/reload-plugins`) so the skills load.

Verify:

```bash
claude plugin details anvil@mrerror-claude-skills   # should list 5 skills
```

### What gets installed

`anvil` + its 5 skills, plus these auto-installed dependencies (from
`superpowers-marketplace`, allow-listed via `allowCrossMarketplaceDependenciesOn`):

- [`superpowers`](https://github.com/obra/superpowers) — the skills anvil reshapes
- `claude-session-driver` — real parallel execution via tmux workers
- `episodic-memory` — cross-session recall

## Optional: a second model for `cross-model`

`cross-model` is backend-agnostic and falls back to Claude-only if nothing is set
up. For a real independent second opinion, pick one (details in
[`plugins/anvil/skills/cross-model/references/backends.md`](plugins/anvil/skills/cross-model/references/backends.md)):

- **Antigravity CLI (`agy`) — recommended.** Google's terminal agent; signs in
  with a **Google AI Pro / Ultra** subscription, so no API key and no per-token
  cost. Install: `curl -fsSL https://antigravity.google/cli/install.sh | bash`,
  then `agy` to log in. The skill drives it headless with
  `agy --model gpt-oss-120b-medium -p "<prompt>"` (a different model family from
  the Claude being reviewed → a true cross-check).
- **Gemini API key** — `npm install -g @google/gemini-cli` + `GEMINI_API_KEY`
  (free tier is Flash-only).
- **A local router** (omniroute / claude-code-router) exposing an
  OpenAI-compatible endpoint, to reach many models behind one key.

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
  skills/
    anvil/SKILL.md                       # workflow governor
    afk/SKILL.md                         # unattended mode
    ui-mockup/SKILL.md                   # mock-first UI
    ux-audit/SKILL.md                    # post-build UX audit
    cross-model/SKILL.md                 # second-model review/research
    cross-model/references/backends.md   # pluggable model backends
```

## Notes

The `anvil` and `afk` skills are generalized versions of project-specific
originals — stack specifics (commands, rules, paths) are demoted to examples so
they work across any project. `cross-model` is a Linux port of a prior Gemini
cross-review rig, rebuilt to be provider-agnostic.

MIT. Personal tooling — use at your own discretion.
