# Anvil 0.2.0 release audit: `main` vs `anvil-og-next`

- **Date:** 2026-11-19
- **Compared:** `main` @ `46b7535` (plugin 0.1.0) against the working tree of `anvil-og-next` (0.2.0). The branch has no commits of its own, so every change is uncommitted.
- **Yardstick:** Anthropic's current prompting guidance for Claude Opus 5.5 and Claude Sonnet 5.5 (the Claude API skill bundled with Claude Code 2.1.322: its prompt-audit guide and the "Migrating to Claude Opus 5.5 / Sonnet 5.5" behavioural-shift sections). Also this repo's own intent: [the fix list](2026-11-19-og-grievances-and-fixes.md) (G1–G12) and [the design rule](2026-11-19-skills-review.md).
- **Target model:** Opus 5.5, which runs these skills. Sonnet 5.5 is noted where it behaves differently.
- **State:** your decisions were applied the same day (table below), and this file was then rechecked against the files. Findings marked **Resolved** are fixed; the rest still stand. Line links point to the files as they are now.

## Decisions and what was applied (2026-11-19)

| Finding | Your decision | Applied |
| --- | --- | --- |
| R1 `afk` commits | Controlling commits isn't AFK's job | `afk` description and body: commits and branches are left to the workflow, the project rules and the user. The old "Branch safety" bullet and "Never push" went (pushing is still covered by "Anything leaving the machine"). README row updated. The fix list's G11 and §4 lines are marked superseded |
| R2 stale README / marketplace | Update them | README tagline, the `afk` row and the tree comment; marketplace "Gemini research" → "two-model cross-model research" |
| R3 / G-c model for subagents | Not a sensitive matter: use whichever model is available | No model line added to Anvil. Fix list §4 annotated |
| `cross-model` cheapest model | Start cheap; if the result isn't good enough, move up a tier | The step-up rule in `SKILL.md` and `backends.md` now covers "empty, shallow or off-target", repeats if needed, and names the model used |
| Diff review | Anvil shouldn't have cross-model review at all | Unchanged (the plugin is research only). `cross-model-review` stays a loose skill; the skills review no longer lists it for removal |
| Global CLAUDE.md | Fix it | `~/.claude/CLAUDE.md`: research → `cross-model` (plugin), diff review → `cross-model-review`, provider-neutral wording |
| Stale or duplicated content | Remove it | G-a: Anvil's "No progress narration" line rewritten to apply to the report only |

## Verdict

The release is an improvement, and **no accidental data loss was found**. Every removal traces to a decision in the fix list, the design rule, or the decisions above. All of `afk`'s content from `main` survives except its own commit and branch rules, which you removed on purpose.

Still open before shipping:

- **2 gaps against the 5.5 guidance** (§4): the mockups avoid list, and the `ticket-update` trigger.
- **1 trigger overlap** (§3): the plugin's `cross-model` and the loose `cross-model-review` both answer "use cross-model".
- **Removals still to confirm** (§5). The one with the most reach: web-audit no longer checks accessibility by default.
- **The governor is unmeasured** (§6).

## 1. What changed, per skill

| Skill | `main` | `anvil-og-next` | Net |
| --- | --- | --- | --- |
| `anvil` | Tiers 0/1/2, 8-step decision procedure, parallel by default, verify once at the end, frontend test table | Three paths with stated stops, waves of at most 4 with a spec check after each, final verification that ticks off each ask, repro-first bug fixes, report shape, landing | Rewritten. Similar size (17.7k → 19.2k chars) |
| `afk` | Decide-don't-wait, never-unlocked list (with its own commit and branch rules), decision log | Same, plus "Passing a stop" (a ruling for each kind of stop) and "Ending too early". Commits and branches are left to the workflow, the project rules and the user | Additions, and its own commit and branch rules removed on purpose |
| `cross-model` | Review and research, auto-triggered, hard-wired to `agy` and named models | Research only, manual only, discovers any backend, starts with the cheapest model and moves up a tier when needed | Narrowed on purpose |
| `ui-mockup` → `mockups` | 49 lines: mock first, states, align | 130 lines: 2–4 local HTML variants, one idea each, its own design rules, rounds | Renamed, grown |
| `ux-audit` → `web-audit` | 7 heuristics by default, applies fixes | UI and UX at one size by default; other categories on request; report only | Renamed, rescoped |
| `ticket-update` | — | New: tracker detection, ticket contract, comments, 3 evals | New |
| `plugin.json` | Depends on `superpowers`, `claude-session-driver` and `episodic-memory` from `superpowers-marketplace` | No dependencies; the description says Superpowers is required | Matches §6 of the fix list |

## 2. Improvements under the 5.5 guidance

| What the guidance says | What changed | Where |
| --- | --- | --- |
| Emphasis makes current models over-apply a rule | No all-caps emphasis is left in any skill body (`main` had 5 words). What's left is `cross-model`'s "Use ONLY" trigger text, which is allowed calibrated urgency, and the prompt sent to another model's CLI, which has a recorded failure behind it | all skills |
| Lines like "don't narrate" make current models go quiet during long work | Anvil's report rule now applies to the final report only, and invites brief updates at milestones | `anvil` Report |
| Step choreography for judgment work degrades output | The 8-step "don't improvise the sequence" procedure and its mermaid flowchart are gone. The remaining numbered steps are where order matters (Just do it, final verification) | `anvil` |
| Keep the *reason* beside a rule | New rules carry their reasons. Examples: "a reviewer asked to find problems always finds something", "a big ticket hides drift", "writing to the wrong one is visible to other people" | `anvil`, `ticket-update` |
| Pinned model names rot after the next release | `gpt-oss-120b-medium`, `gemini-3.8-flash-*` and `claude-opus-4-6-thinking` are removed. Models are listed from the tool each time | `cross-model`, `backends.md` |
| Sonnet 5.5 at low effort reports changes done without a real check, and should say which check it didn't run | "Check once: … run the real command, endpoint or screen … If the suite is slow, run the targeted tests and say so." Plus the final "tick off what was asked" | `anvil` Just do it and Verification |
| Sonnet 5.5 follows tool-discouraging language literally | None present | all |
| Asking the model to reproduce its reasoning may be declined (`reasoning_extraction`) | None present. "Calls I made, each with its reason" asks for a short explanation, which is allowed | `anvil`, `afk` |
| Unattended runs end early (documented for Sonnet 5.5 at low effort: it checks in before finishing) | New "Ending too early" section names four early-stop shapes | `afk` |
| Volatile paths and tools go stale | Dead pointers removed: `claude-session-driver` (needs tmux), `episodic-memory`, `superpowers-chrome`, `artifact-design`/`dataviz`, and the Artifact instruction that broke your CLAUDE.md rule | `anvil`, `mockups`, `web-audit` |
| Facts claimed should match the machine | `agy --print-timeout` and `--effort` both exist in `agy --help`. The Linear tool names in `trackers.md` (`save_*`, `list_issue_statuses`, `addLabels`) match this session's Linear connector | `backends.md`, `trackers.md` |

## 3. Contradictions

- **R1 `afk` description vs body on commits: Resolved.** Both now say AFK leaves commits and branches to the workflow, the project rules and the user. The README row matches.
- **R2 README and marketplace describing 0.1.0: Resolved.** The tagline, the `afk` row, the tree comment and the marketplace description are updated.
- **R3 the two docs disagreeing on the speed levers: Resolved.** Your decision is in the fix list §4: only batched fixes stayed, and Anvil doesn't prescribe a model.

### R4. Two skills answer "use cross-model" (low, open)

- The plugin's [cross-model/SKILL.md:7-9](../../plugins/anvil/skills/cross-model/SKILL.md#L7-L9) triggers on "use cross-model", "research this with another model too" (research only).
- The loose `~/.claude/skills/cross-model-review` triggers on "use cross-model", "use Gemini", "ask Gemini", "research with Gemini", "get a second opinion from another model". It does review *and* research.
- The global CLAUDE.md now says which one handles what. But skill selection reads the descriptions, so "use cross-model, research X" can still land on the review skill.
- **Proposed fix:** narrow the loose skill's description to diff review ("review this diff with another model", "get a second opinion on this change"), and drop "use cross-model" and "research with Gemini" from it. This file is outside the repo and affects every project.

## 4. Gaps against the 5.5 guidance

- **G-a "No progress narration": Resolved.** It's in §2 now.
- **G-c no model guidance for subagents: Decided, no change.** Whichever model is available is used.

### G-b. The mockups "avoid" list targets older models' defaults, not Opus 5.5's (medium, open)

- [mockups/SKILL.md:114-116](../../plugins/anvil/skills/mockups/SKILL.md#L114-L116): "no decorative gradients, no generic grids of hero cards, no emoji as icons, and not the same font and accent in every variant".
- **Guidance:** asked for frontend work without design direction, Opus 5.5 falls back on a few specific defaults. A general "avoid the template look" mostly swaps one default for another. The fix that works is a list that **names** the defaults: a cream or off-white background, italic accent words in headlines, numbered "01/02/03" section labels, monospace labels, and pill-shaped buttons. Then extend the list from what the first round actually used.
- The skill's own "Visual direction: quiet and neutral" option tends to land on exactly the cream-background default.
- **Proposed addition** to that bullet:

  > Also none of the current model's defaults unless the app uses them: a cream or off-white background, italic accent words in headings, "01/02/03" section numbers, monospace labels, or pill-shaped buttons. After each round, add any default the variants still shared to `FLAWS.md` and to the next brief's avoid list.

### G-d. `ticket-update` may trigger on nearly every turn (low, open)

- [ticket-update/SKILL.md:6-8](../../plugins/anvil/skills/ticket-update/SKILL.md#L6-L8): "Use it at every stop point in a repo whose work is tracked … or you are ending a turn that changed something."
- Current models follow descriptions closely. "A repo whose work is tracked" is detected from signals as weak as `#123` in a commit, which most GitHub repos have. So in most repos the skill would load on every edit turn, and a repo without a profile would get the Setup questions.
- The outward writes are already gated ("Asking first", "Don't guess between trackers"). The cost is load and interruptions, not wrong writes.
- **Proposed narrowing:**

  > …in a repo that has a ticketing profile or a project rule about tickets, or whenever the user asks…

## 5. Removed content: deliberate, but confirm each

These all match a stated decision, but each one loses something real. Rows marked **Decided** were settled on 2026-11-19.

| Removed | From | Where it went / why | Risk |
| --- | --- | --- | --- |
| **Diff review mode**: the review prompt (`SEVERITY \| file:line \| …`, "only the + lines"), AGREE/DISAGREE/NEEDS-CHECK triage, and the auto-triggers (before calling work done, after two failed fixes, on pushback) | `cross-model` | **Decided:** Anvil has no cross-model review. Diff review stays in the loose `cross-model-review` skill, and the global CLAUDE.md routes to it | Low. See R4 for the trigger overlap |
| Its own commit rule ("never commit unless asked", "never push") and "Branch safety" (no work on `main` without consent) | `afk` | **Decided:** commits and branches are the workflow's job. Pushing is still blocked by "Anything leaving the machine", and "Finish the work is not commit the work" stays | With no workflow and no project rule in use, AFK itself no longer stops commits on `main`. Claude Code's own default (commit only when asked) still applies |
| "Use a capable model; avoid low/mini tiers. A shallow second opinion is worse than none" | `cross-model` | **Decided:** start with the cheapest model and move up a tier, again if needed, when the answer is empty, shallow or off-target | Low. The step-up rule covers the obvious failure, and the result names the model used |
| Router ports (omniroute `:20128/v1`, CCR `:3456`), the Gemini API-key route (`GEMINI_API_KEY`, the June 2026 OAuth removal) | `backends.md` | Generalised to "an OpenAI-compatible endpoint on localhost" | Without a port, "a quick request to its models endpoint" has nowhere to go. Ports are quirks, not model names, so they fit "Known backends" without breaking the design rule. Suggest keeping one line per router |
| Accessibility, responsiveness, consistency and content as default checks | `ux-audit` → `web-audit` | Opt-in categories ("UI and UX by default") | **Keyboard, focus and contrast problems are no longer caught unless asked.** The UI row doesn't mention contrast, though `mockups` requires 4.5:1. A cheap middle ground: add "body-text contrast" to the UI row |
| "Apply the fixes" | `ux-audit` → `web-audit` | Report only; the user decides | Intended. README says so |
| The "States checked" summary in the report | `ux-audit` | States moved into the UX row | Minor. A single `States: empty / loading / error` line in the template makes missing states visible at a glance |
| ASCII sketch inline "for something simple" | `ui-mockup` | Always 2–4 HTML variants; "not for a change already described exactly" | Small screens now cost a variant round. Acceptable if the description keeps routing small changes away |
| Trigger "BEFORE writing any front-end implementation" | `ui-mockup` | Fires only when the look is open | Intended; the old trigger over-fired |
| Tiers, decision procedure, flowchart, the frontend "what earns a test" table, the claim that interleaved checks "catch none this pass would miss", the "implement only, don't author tests" brief | `anvil` | Replaced per G1, G4–G6 | Intended |
| `graphify` and `episodic-memory` pointers; the `Workflow` tool mention | `anvil` | Removed per the design rule | Intended |
| Speed levers "cheapest capable model for mechanical work" and "file-based handoffs" | `anvil` | **Decided:** only batched fixes stayed; whichever model is available is used | Intended |
| `using-git-worktrees` and `finishing-a-development-branch` "kept as written" | `anvil` | Now overridden by Anvil's isolation rule and Landing | Intended (G10, G11) |
| "A review pass before merge" in the non-negotiable floor | `anvil` | The final review runs on the Full path only | Just do it and Spec first now merge with no review pass. Intended for Just do it. For Spec first, which can produce commits, confirm this |
| "No lint-disable to mask output" | `anvil` | Now "Resolve the warnings that matter. Never hide any." | The concrete example is gone. Re-add three words: "…Never hide any (no lint-disable)." |
| Two reasons: data-layer contracts are pinned "because that's where under-specification silently regresses caching and error handling"; "an invented contract presented as settled is worse than none: the pin is what everyone downstream trusts" | `anvil` | The rules survive; the reasons were cut | The guidance values a rule's "because" over the rule's length. Re-add both clauses (one line each) |
| "Tier is about coordination complexity, not counts" | `anvil` | The Full trigger is "4+ tasks in separable areas" plus risk triggers | Acceptable. V2.2's triggers routed 21/21 |
| `dependencies` on `superpowers`, `claude-session-driver`, `episodic-memory`; `allowCrossMarketplaceDependenciesOn` | manifests | Fix list §6: wrong marketplace, unused tools | Intended. Superpowers must now be installed by hand; the README says so |

## 6. Not verified yet

- **The governor is unmeasured.** The fix list's step 4 (rerun the 7 A/B cases against OG) hasn't happened. The parts that changed most (per-wave spec check, waves, reconciliation, landing) need a case with 4+ separable tasks, and the current suite has none (§7.2 of the fix list).
- **Evals exist only for `ticket-update`** (3 cases, 23 graders). They haven't been run because they cost money. `anvil`, `afk`, `mockups`, `web-audit` and `cross-model` have no evals in this branch.
- **Checked and fine:**
  - 6 `SKILL.md` files, matching the README's "should list 6 skills".
  - Every description is under the 1,536-character cut-off. The largest is `anvil` at 1,001.
  - The always-loaded descriptions total 4,974 characters (about 1.2k tokens), up from 3,633, so the README's "~1.2k tokens always-on" holds.

## 7. Public-repo check

The `.gitignore` comment says the repo is public. These would ship:

- [evals/splits-plan-into-tickets/files/.claude/ticketing.local.md:3-5](../../plugins/anvil/skills/ticket-update/evals/splits-plan-into-tickets/files/.claude/ticketing.local.md#L3-L5): "Team: IND. Project: DipGos. Milestone: AI & Workflow", plus your full name and handle.
- [references/profile-template.md:19](../../plugins/anvil/skills/ticket-update/references/profile-template.md#L19): "Project: <e.g. DipGos>".
- The eval prompts use "Saad" and the branch `saad/sql-guard`.

If DipGos or the IND team key belong to a client or employer, replace them with placeholders (for example `Team: ACME`, `Project: Ledger`). Your own first name in the evals is your call.

## 8. Skill-authoring and marketplace conformance (checked 2026-11-19)

Checked against the `skill-creator` guidance (official plugin) and with Claude Code 2.1.318's own validator.

**Validator results:**

| Command | Result |
| --- | --- |
| `claude plugin validate . --strict` (marketplace) | Passed |
| `claude plugin validate plugins/anvil --strict` | Passed |
| `claude plugin validate plugins/anvil/skills --strict` (all 6 skills) | Passed |
| `claude plugin validate plugins/anvil --strict --profile directory` | Fails on one warning: no icon (`ICON_MISSING`). This matters only if you submit to Anthropic's plugin directory; your own marketplace doesn't need one |

**Skill-creator checklist:**

| Rule | Status |
| --- | --- |
| Frontmatter has `name` and `description`; the name matches the folder | Yes, all 6 |
| The description says what the skill does and when to use it | Yes, all 6. `cross-model` is deliberately restrictive (manual only), which goes against the guide's "make it pushy" advice on purpose |
| `SKILL.md` under 500 lines | Yes. The largest are `anvil` (382 lines) and `ticket-update` (312) |
| Reference files over 300 lines have a table of contents | None is over 300 lines. `templates.md` and `trackers.md` have one anyway |
| Each reference file is linked from `SKILL.md` with when to read it | Yes (`ticket-update`'s 4, `cross-model`'s 1) |
| The reason is explained instead of all-caps MUST/NEVER | Yes (§2) |
| No surprising behaviour; outward writes are gated | Yes. Tracker writes ask first; the second-model brief carries no secrets |
| Test cases for skills with checkable output | **Partly.** Only `ticket-update` has evals. `anvil` was measured with the A/B harness, which lives on the `anvil-v2` branch, not this one. `afk`, `web-audit` and `cross-model` have checkable behaviour and no evals. `mockups` is subjective, so human review is fine |
| Trigger-accuracy check of descriptions | Not run for any skill (optional in the guide) |

**Problems found:**

1. **The `ticket-update` evals aren't found by default.** `claude plugin eval` reads `<plugin>/evals/` unless `--eval-dir` or the manifest's `experimental.evals` names another folder. The cases sit in `plugins/anvil/skills/ticket-update/evals/`, so `claude plugin eval plugins/anvil` finds none of them. Fix: move them to `plugins/anvil/evals/ticket-update/`, or run with `--eval-dir skills/ticket-update/evals`. The README's tree line also says they're plugin eval cases.
2. **The marketplace serves what's committed, and 0.2.0 isn't committed.** Installing from `MrErrorSan/mrerror-claude-skills` today gets `main`'s 0.1.0. The validator also notes that a submission uses only committed files.
3. **0.2.0 isn't what's running on this machine.** This session's skill list loads the loose `~/.claude/skills/anvil` and `afk` (the old copies tied to a React frontend). The plugin is installed at local scope as 1.0.0 (see the fix list §6). Deploying at user scope and moving the loose copies out is still open.
4. **Superpowers is required but not declared.** `plugin.json` has no `dependencies`, so installing Anvil won't pull Superpowers in. That's consistent with the README ("doesn't install it for you"). Declaring `superpowers@claude-plugins-official`, with `allowCrossMarketplaceDependenciesOn: ["claude-plugins-official"]` in the marketplace, would install it automatically. Your call.

## Still open, in suggested order

1. G-b: the mockups avoid list.
2. The accessibility default in `web-audit` (§5).
3. R4: narrow the loose `cross-model-review` description.
4. G-d: the `ticket-update` trigger.
5. The small §5 items: router ports, "no lint-disable", the two "because" clauses, and the review pass on Spec first.
6. §7, if DipGos is a client name.
7. Then run the measurement in §6 before committing.
