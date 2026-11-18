# Skills audit: this repo against the skills on this machine

- **Date:** 2026-11-18
- **Machine:** Windows 11, user `MrError`, Claude Code with two accounts (`~/.claude`, and `~/.claude-personal`, which links to the same `skills/` and `commands/`)
- **Repo state audited:** `main` @ `46b7535`, plus the uncommitted `ticket-update` skill
- **Raw data:** [2026-11-18-skills-audit.json](2026-11-18-skills-audit.json) (every copy found, with hash, size, date and status)

## The short version

The repo is **ahead** of this machine on three of the four skills both have. But this machine doesn't run the repo: the `anvil` plugin isn't installed and the marketplace isn't added. Claude here loads older loose copies from `~/.claude/skills/` instead.

1. **Broken today: the cross-model rig.** Every machine-side piece of it names the model `gemini-3.1-pro-high`. Your `agy` plan no longer has that model, and `agy` now refuses it ("model gemini-3.1-pro-high is not recognized"). That covers the `cross-model-review` skill Claude loads, `/gemini-ask`, `/gemini-review`, `/research`, `agy-review` and `xreview`.
   - The repo's `cross-model` already uses models that exist. Test prompts to `gpt-oss-120b-medium` and `gemini-3.8-flash-medium` both answered in 6–8 s on this machine.
   - Fix this first.
2. **`anvil` on this machine is the React frontend version.** It is loaded in *every* project, Python repos included, and talks about `npm run validate`, `useResourceQuery` and "this frontend". The repo's version is the general one.
3. **The repo is missing things only this machine has:**
   - the three Gemini slash commands;
   - the "write your own findings before you read Gemini's" rule;
   - the script that runs both models side by side;
   - the reverse direction, where Gemini consults Claude;
   - the design notes behind the rig.
4. **`ui-mockup` and `ux-audit` exist only in the repo.** Both are well behind how you actually work, judging by the audits and mocks in your repos.
   - `ui-mockup` tells Claude to publish an Artifact, which your global rules forbid.
   - `ux-audit` points at a browser skill that isn't installed.
5. **Packaging would cause trouble if you installed the plugin today.**
   - It depends on a second copy of Superpowers from another marketplace.
   - It depends on a tmux-based plugin, and tmux isn't on this machine.
   - Its skills would sit alongside the loose `anvil` and `afk` copies, so both versions would load.

## What was compared

| Skill | In the repo | On this machine | Verdict |
|---|---|---|---|
| `anvil` | general version, 327 lines | `~/.claude/skills/anvil` (React frontend version, 339 lines, 2026-10-15); `Indus/frontend/.claude/skills/anvil` (336 lines, 2026-09-21) | **Repo ahead.** The machine copy is project-specific but loaded everywhere |
| `afk` | 142 lines | `~/.claude/skills/afk`, `Indus/frontend/.claude/skills/afk`, `skills.zip`: all three identical | **Same.** The repo only drops a project-specific "Rule 12" |
| `cross-model` | `cross-model` + `references/backends.md` (2026-11-03) | `cross-model-review` skill + 3 commands + 2 scripts + a Gemini-side skill + a design doc (2026-09-20) | **Repo ahead on models. Machine ahead on tooling.** The machine copy is broken |
| `ui-mockup` | 49 lines | none | **Repo only.** Behind real practice; conflicts with the no-Artifacts rule |
| `ux-audit` | 64 lines | none | **Repo only.** Well behind real practice |
| `ticket-update` | new, uncommitted | sources: `mutlashi-demo/.claude/rules/08-linear-tickets.md`, `Chunker/CLAUDE.local.md`, `Classifier/CLAUDE.local.md`, 2 pattern docs | **Up to date.** Merged from those sources today |

Out of scope:
- the Anthropic skills synced from claude.ai (docx, pdf, skill-creator and so on);
- installed plugins (Superpowers, frontend-design, chrome-devtools-mcp and so on).

Neither is yours to maintain.

---

## 1. cross-model: machine copy broken, repo copy missing tooling

### Broken on this machine

| Piece | Where | Problem |
|---|---|---|
| `cross-model-review` skill | `~/.claude/skills/cross-model-review/SKILL.md` | Says "Use `gemini-3.1-pro-high`". That model is gone |
| `/gemini-ask`, `/research` | `~/.claude/commands/` | Both hard-code `--model gemini-3.1-pro-high` |
| `/gemini-review` → `agy-review` | `~/.local/bin/agy-review` | `MODEL="gemini-3.1-pro-high"` |
| `xreview` | `~/.local/bin/xreview.cmd` → `xreview.ps1` | Same rig, same model (per the design doc) |
| Design doc | `~/.claude/docs/cross-model-review-design.md` | "Confirmed model list: `gemini-3.1-pro-high` exists". True on 2026-09-20, not now |

The models available today (`agy models`) are:
- `gemini-3.8-flash-{low,medium,high}`
- `gpt-oss-120b-medium`
- `claude-sonnet-4-6`
- `claude-opus-4-6-thinking`

The two sides also disagree on how to call `agy`:
- **Machine (Sept):** use `--mode plan`, deliver content with `--add-dir`, and never pipe it in.
- **Repo (Nov):** inline the content into the prompt, and use no `--mode plan` and no `--add-dir`. The repo says plan mode and `--add-dir` make `agy` reach for tools that headless mode denies, which gives empty output.

The repo's pattern is the newer finding. I checked it here with a test prompt only, no real diff: `gpt-oss-120b-medium` answered in 6 s and `gemini-3.8-flash-medium` in 7 s.

### What the repo is missing that the machine has

1. **The slash commands.** `/gemini-ask`, `/gemini-review` and `/research` are quick, explicit entry points. The plugin ships no `commands/`.
2. **The rule that keeps research independent.** `/research` says: "DO NOT read Gemini's output until your own findings are written. Reading it first anchors you to its framing." The repo's research mode only says to run both tracks "in parallel", and that rule is the point of having two tracks.
3. **Where research results go.** `/research` saves substantial answers to `docs/research/YYYY-MM-DD-<topic>.md`, with Gemini's raw output verbatim in an appendix. The repo has no rule for saving output.
4. **Both models side by side.** `xreview` runs Claude and Gemini on the same diff in parallel. The repo only covers one external model at a time.
5. **The reverse direction.** `~/.gemini/config/skills/cross-model-review/SKILL.md` lets Gemini, inside `agy`, consult Claude read-only with `--permission-mode plan`. The repo only covers Claude asking Gemini.
6. **Recorded test results.** The design doc and `~/.claude/docs/fixtures/xmodel-fixture/` hold the tests that proved the rig works, including a planted-bug fixture. The repo's `backends.md` says "verified working on this machine". That was the Linux machine (the README calls `cross-model` "a Linux port"), so there is no fixture to re-run here.

### Other gaps

- **Name mismatch.** Your global `~/.claude/CLAUDE.md` says the triggers "live in the `cross-model-review` skill". The repo skill is called `cross-model`. Once the plugin replaces the loose skill, that pointer leads nowhere.
- **Unverified risk on Windows: big diffs inline.** Windows caps a command line at about 32,000 characters. A large `git diff HEAD` inlined into `agy -p "<prompt>"` would fail there. The machine rig avoided this by writing the diff to a temporary folder. The repo mentions `--add-dir` plus `--sandbox` only as a fallback. It needs an explicit "over about 25 KB, use the file route" rule, and that route needs a test on this machine.

## 2. anvil: repo ahead; machine runs a project copy everywhere

The loose `~/.claude/skills/anvil` is the Indus frontend copy plus one line for Enteyoes plan paths. It's a user-level skill, so it loads in every repo, including the Python ones (Chunker, Classifier, Indus platform). Its description says "the workflow governor for **this repo** … for **this frontend**". Its commands are `npm run validate` and `npx vitest`.

**What the repo has that the machine copy lacks:**
- A rule that project rule files win over Anvil. This is the general form of the "rule 13-workflow is binding" line.
- Commands that fit any stack (type-check examples for `tsc`, `mypy`, `go build`; narrow-suite examples for `vitest` and `pytest`).
- Data-layer contracts in general terms (cache keys, invalidation, fallback, error mapping), not `useResourceQuery` and `FriendlyError`.
- "Actually executing the fan-out": dispatch with the `Agent` tool, not just describe it.
- The `graphify` tip: query the graph instead of re-reading files.

**What the machine copy has that the repo lacks:** nothing that belongs in a general skill. The Enteyoes plan path already lives in `Enteyoes/.claude/rules/planing.md`, which is the right home.

**Problems in the repo copy:**
- **Plan location doesn't match.** The repo says plans default to `docs/plans/YYYY-MM-DD-<topic>.md`. Superpowers, the machine copy and your repos (for example `Indus/docs/superpowers/plans/`) all use `docs/superpowers/plans/`. Pick one; `docs/superpowers/plans/` matches what's already on disk.
- **It points at tools that aren't here.**
  - `claude-session-driver` needs tmux, which this machine doesn't have.
  - `episodic-memory` isn't installed.
  - Both should read "if installed". The skill should fall back to the `Agent` tool without saying so.
- **The sibling skills aren't wired in.** `ux-audit` says "Anvil calls this automatically after any UI implementation". `anvil` never mentions `ui-mockup`, `ux-audit`, `cross-model` or `ticket-update`. Either add a short "what else to run, and when" table to Anvil, or remove the claim from `ux-audit`.

The Indus frontend copy from 2026-09-21 is one edit behind the user-level copy, and fine. It belongs to that project and works with its `13-workflow.md` rule.

## 3. afk: same

The user-level copy, the Indus frontend copy and `skills.zip` are byte-identical to each other. Ignoring whitespace and line wrapping, the repo copy differs from them in three lines:

- The repo drops "Rule 12 stands:" from the commit rule. That's correct, because it's general now.
- Two small wording edits.

Nothing is missing.

## 4. ui-mockup: repo only, and against your own rules

- **It conflicts with the global no-Artifacts rule.** Step 2 says to make "a low-fi wireframe / layout mock as an HTML **artifact** (use the `artifact-design` skill…)". Your `~/.claude/CLAUDE.md` forbids Artifacts and wants local files in the repo's `docs/`.
- **It's behind how you actually mock.** Your repos show a consistent habit the skill doesn't describe:
  - **Self-contained HTML mocks saved next to the feature's docs.** Examples: `Enteyoes/docs/reception-ux/2026-10-28-reception-ux-mock.html`, `Indus/docs/atom-manager-redesign/media-mocks.html`, `Indus/docs/ontology-rag/mock-ui-v2/kr-mock-v2.html`.
  - **Two or three variants side by side.** Example: `Indus/docs/collaboration-redesign/mock-a-classic-slack.html` and `mock-b-modern-slack.html`.
  - **Numbered rounds after feedback.** Example: `INDUS-Web/docs/redesign-mocks`, then `-r2`, `-r3`, `-r4`, plus an `owner-review/mocks/` folder.
  - **A note on what the chosen mock still misses.** Example: `Indus/docs/atom-manager-redesign/_archive/02-what-the-liked-mocks-miss.md`.
- **It ignores tools that are installed:**
  - the `frontend-design` plugin, for the look;
  - the Superpowers brainstorming visual companion, for showing mocks in a browser tab.
- **It doesn't say where mocks go.** It should follow the project's doc rule (for example Enteyoes: `docs/<feature>/`), with `docs/<feature>/mocks/` as the default.

## 5. ux-audit: repo only, well behind real practice

- **It names a browser tool that isn't installed.** Step 1 says "the `superpowers-chrome` skill can open it". This machine has `chrome-devtools-mcp`, which includes an `a11y-debugging` skill. The Enteyoes reception audit records that DevTools MCP failed to connect and the run fell back to `playwright-core` driving the installed Chrome. The skill should name both, in that order.
- **It applies fixes without asking.** Step 4 is "Apply the fixes". Your real audits end with decisions for the owner and a suggested order of work, not edits. Examples: `Enteyoes/docs/reception-ux/2026-10-28-reception-ux-audit.md` §5 and §7, and `Mine/redon web tv/docs/superpowers/reviews/2026-10-22-template-v2-ux-audit.md` §7 and §8.
- **Missing from the skill, present in every real audit:**
  - A header with the date, status, the exact build audited (branch @ sha, how it was served) and links to earlier reviews.
  - **How each finding was checked**: *Tested* (seen in a real browser at phone 390 px and desktop 1366–1440 px) or *Code* (file and line, not reproduced). P0 claims get re-checked by a second reader.
  - **Severity tied to user harm** (P0: lose work or see a wrong price; P1: stuck or misled; P2: polish). The skill only has "fix now" and "consider".
  - **Passes from the user's point of view** (owner, receptionist, shopper on a cheap phone), and the user's own questions answered first.
  - **Measurements saved to a sibling `.json`**: page height, word count, buttons, inputs and long text blocks per screen.
  - **Screenshots in an assets folder**, named by viewport (`d-…png`, `m-…png`).
  - **Setup notes for re-running the audit**: ports, test login and known local-only errors.
  - Where the report goes: the project's doc rule, otherwise `docs/<feature>/YYYY-MM-DD-<feature>-ux-audit.md`.
- **The description says "whenever MrError asks".** The skill can't know who MrError is. Use "the user".

## 6. ticket-update: current

It was built today from all five source files, so nothing on the machine is newer. Still open from earlier:
- it's uncommitted;
- the eval fix ("the user's own attributed report counts as evidence") hasn't been applied.

One clean-up for later: the source rule files still carry the full rules. Once the skill is installed, cut `mutlashi-demo/.claude/rules/08-linear-tickets.md` and the Linear sections of the two `CLAUDE.local.md` files down to project specifics: the team key, parent ticket, gate commands and title style. They map to a `.claude/ticketing.md` profile, so each rule lives in one place.

## 7. On the machine, not in the repo

| Item | Where | Should it go in the repo? |
|---|---|---|
| `graphify` | `~/.claude/skills/graphify` (v0.9.92), `Indus/.claude/skills/graphify` (v0.9.92), `Enteyoes/.claude/skills/graphify` (**v0.9.53**) | **No.** It's third-party and installed by the graphify tool. The Enteyoes copy is about 40 versions behind; refresh it with graphify's own installer |
| `parser-debug` skill, `pdf-parser-reviewer` agent | `Indus/platform/.claude/` | **No.** Tied to that pipeline |
| `mw2-geometry-reviewer` agent | `PBS maker/.claude/agents/` | **No.** Tied to that project |
| Gemini commands, `agy-review`, `xreview`, Gemini-side skill, design doc | `~/.claude/commands`, `~/.local/bin`, `~/.gemini/config/skills`, `~/.claude/docs` | **Yes.** Fold into `cross-model` (section 1) |
| Stand-up skill | design only: [superpowers/specs/2026-11-18-standup-design.md](superpowers/specs/2026-11-18-standup-design.md) | **Yes, once built.** It is waiting on your answers |

## 8. Packaging problems

- **Not installed here.** `~/.claude/plugins/installed_plugins.json` has no `anvil@mrerror-claude-skills`, and `known_marketplaces.json` only lists `claude-plugins-official`. Nothing in this repo is active on this machine.
- **A second copy of Superpowers.**
  - `plugin.json` depends on `superpowers@superpowers-marketplace`.
  - This machine runs `superpowers@claude-plugins-official` 7.0.2.
  - Installing the plugin as written would add a second copy from a different marketplace, so every Superpowers skill would appear twice.
  - Either depend on the official marketplace's `superpowers`, or drop the dependency and say in the README that Superpowers must be installed.
- **`claude-session-driver` needs tmux.** It's a hard dependency, but it can't run on this Windows machine. Make it optional.
- **Two copies of each skill.** After installing, `anvil` and `afk` would load twice: the loose user-level skills plus `anvil:anvil` and `anvil:afk`. Remove the loose `~/.claude/skills/{anvil,afk,cross-model-review}` once the plugin is in. Keep `skills.zip` as a backup if you want it.
- **README notes:**
  - "should list 6 skills" is right.
  - The prerequisites point at `obra/superpowers-marketplace`. That changes with the dependency fix above.

---

## What to do, in order

1. **Fix the broken rig now (minutes).**
   - Replace `gemini-3.1-pro-high` with `gpt-oss-120b-medium` (reviews) or `gemini-3.8-flash-medium` (questions and research) in `agy-review`, `xreview.ps1`, `/gemini-ask` and `/research`.
   - In `agy-review`, also drop `--mode plan`, or confirm that `--mode plan --add-dir` still works with the new model before keeping it.
   - Update the model line in the loose `cross-model-review` skill.
2. **Bring the machine's tooling into `cross-model`:**
   - add the three commands under `plugins/anvil/commands/`;
   - add the rule to write your own findings before reading Gemini's;
   - add where research results are saved;
   - add an "over about 25 KB, use the file route" rule, and test it here;
   - optionally add a "both models" mode and a note about the Gemini-side skill.
   - Then point `~/.claude/CLAUDE.md` at the new name, or keep the name `cross-model-review`.
3. **Fix packaging:** change the Superpowers dependency to the official marketplace, make `claude-session-driver` and `episodic-memory` optional, and make Anvil fall back to the `Agent` tool.
4. **Rewrite `ux-audit` and `ui-mockup` from your real audits and mocks** (sections 4 and 5): local files only, `chrome-devtools-mcp` then `playwright-core`, P0/P1/P2, *Tested* vs *Code* labels, owner decisions before fixes, and variants and rounds for mocks.
5. **Wire Anvil to its sibling skills** with a short "what else to run, and when" table. Set the plan default to `docs/superpowers/plans/`.
6. **Install the plugin on this machine,** then remove the loose `anvil`, `afk` and `cross-model-review` copies so only one version of each loads.
7. **Refresh Enteyoes' graphify** to 0.9.92.

## How this was checked

- I listed every `SKILL.md`, command and agent under `~/.claude`, `~/.claude-personal`, `~/.gemini/config/skills`, the plugin cache and every repo's `.claude/` folder under `Documents/GitHub` (searched six levels deep, skipping `node_modules` and `.git`).
- I hashed each copy, then compared same-named copies with a diff that ignores line endings, spacing, table padding and line wrapping. Without that, the repo's CRLF line endings make every line look changed.
- I ran these probes on this machine:
  - `agy models`;
  - `agy --model gemini-3.1-pro-high` (rejected);
  - `gpt-oss-120b-medium` and `gemini-3.8-flash-medium` (both returned `PROBE-OK`);
  - `--mode plan` with `gemini-3.8-flash-medium` (returned `PROBE-OK` on a trivial prompt; not tested with `--add-dir`);
  - `command -v tmux` (missing).
- I read the headings and setup notes of two real UX audits and listed the mock folders, to compare with `ux-audit` and `ui-mockup`.
