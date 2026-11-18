# Anthropic guidance relevant to the Anvil rebuild

- **Date:** 2026-11-18
- **Scope:** what Anthropic and its staff publish, as of late 2026, that should shape how Anvil's skills are written and how its workflow runs. Read alongside [the brainstorm notes](../2026-11-18-brainstorm-notes.md).
- **Method:** I fetched primary docs and posts with WebFetch and WebSearch. I also read the locally installed `claude-plugins-official` marketplace cache (skill-creator, feature-dev, superpowers 7.0.2) and ran `claude --version`.
- **Conventions:**
  - Text "in quotes" is verbatim from the source.
  - **Fact** is something the source states.
  - **For Anvil** is my inference. It is not Anthropic's claim.
  - **[OLD]** marks a source older than about 9 months (before 2026-02-18). **[SECONDARY]** marks a claim known only through third-party write-ups.
- **Local version note:** this machine runs **Claude Code 2.1.268**. Several features cited below need a newer version: `claude plugin eval` needs v2.1.269, `/doctor prompt-audit` needs v2.1.283, and `engines` in plugin.json needs v2.1.323. Update before relying on them.

---

## Sources

The docs pages (code.claude.com, platform.claude.com) show no publication date. They are living docs, fetched on 2026-11-18. They cite versions up to v2.1.323 and models up to Fable 5.2, so they are current.

| # | Title | URL | Date |
|---|---|---|---|
| D1 | Skill authoring best practices (platform docs) | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | live, fetched 2026-11-18 |
| D2 | Skills (Claude Code docs) | https://code.claude.com/docs/en/skills | live |
| D3 | Plugin manifest reference | https://code.claude.com/docs/en/plugins-reference | live |
| D4 | Plugin dependencies | https://code.claude.com/docs/en/plugins/dependencies.md | live |
| D5 | Install and manage plugins (scopes, enable/disable) | https://code.claude.com/docs/en/plugins/install.md | live |
| D6 | Hooks reference | https://code.claude.com/docs/en/hooks | live |
| D7 | Settings files and precedence | https://code.claude.com/docs/en/settings | live |
| D8 | Best practices for Claude Code | https://code.claude.com/docs/en/best-practices | live. The old Apr 2025 engineering post now 308-redirects here, so the old post is superseded |
| D9 | Extend Claude Code (features overview) | https://code.claude.com/docs/en/features-overview | live |
| D10 | Memory (CLAUDE.md, auto memory, prompt audit) | https://code.claude.com/docs/en/memory | live |
| D11 | `/goal` | https://code.claude.com/docs/en/goal | live |
| D12 | Test plugins with evals (`claude plugin eval`) | https://code.claude.com/docs/en/plugin-evals | live |
| D13 | Common workflows (plan mode, worktrees) | https://code.claude.com/docs/en/common-workflows | live |
| P1 | Prompting best practices (all current models) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | live. Covers Opus 4.6 through Fable 5.2 |
| P2 | Prompting Claude Opus 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 | live |
| P3 | Prompting Claude Opus 5.5 (the default model in Claude Code per D8) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 | live |
| P4 | Prompting Claude Fable 5.2 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 | live |
| E1 | Building effective agents | https://www.anthropic.com/engineering/building-effective-agents | 2024-12-19 **[OLD]** (not re-fetched) |
| E2 | How we built our multi-agent research system | https://www.anthropic.com/engineering/multi-agent-research-system | 2025-06-13 **[OLD]** |
| E3 | Effective context engineering for AI agents | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 2025-09-29 **[OLD]** |
| E4 | Equipping agents for the real world with Agent Skills | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | 2025-10-16 **[OLD]** |
| E5 | Effective harnesses for long-running agents (Justin Young) | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 2025-11-26 **[OLD]**, refined by E6 |
| E6 | Harness design for long-running application development (Prithvi Rajasekaran) | https://www.anthropic.com/engineering/harness-design-long-running-apps | 2026-03-24 |
| E7 | Building a C compiler with a team of parallel Claudes (Nicholas Carlini) | https://www.anthropic.com/engineering/building-c-compiler | 2026-02-05 |
| E8 | How Claude Code is used in practice (Economics team) | https://www.anthropic.com/research/claude-code-expertise | 2026-06-16 |
| E9 | The components of agent memory (Lance Martin) | original not fetched (guessed URL returned 404). Secondary: https://dev.to/gabrielanhaia/anthropics-agent-memory-study-rules-on-what-to-save-cost-claude-much-of-the-gain-3089 | 2026-11-06 **[SECONDARY]** |
| E10 | Engineering blog index | https://www.anthropic.com/engineering | fetched 2026-11-18 |
| B1 | Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents (Michael Segner) | https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more | 2026-06-18 |
| B2 | How Anthropic teams use Claude Code | https://www.anthropic.com/news/how-anthropic-teams-use-claude-code | about Jul 2025 **[OLD]**, date not confirmed on the page |
| R1 | anthropics/skills repo | https://github.com/anthropics/skills | live, last-commit date not visible |
| R2 | skill-creator SKILL.md, claude-plugins-official (local cache) | `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md` | cache synced 2026-11-18. Authoring date unknown |
| R3 | feature-dev plugin, claude-plugins-official (local cache) | `.../claude-plugins-official/plugins/feature-dev/commands/feature-dev.md` | cache synced 2026-11-18. Authoring date unknown, probably 2025 |
| S1 | Boris Cherny workflow (InfoQ write-up of his X thread) | https://www.infoq.com/news/2026/01/claude-code-creator-workflow/ | 2026-01-10. Quotes Opus 4.5-era practice |
| S2 | Boris Cherny, Opus 4.7 tips thread (tip 6, verification and `/go`) | https://x.com/bcherny/status/2044847858634064115 | 2026-04-16 (read via search summary) |
| S3 | Boris Cherny, `/simplify` and `/batch` announcement | https://x.com/bcherny/status/2027534984534544489 | 2026-02-27 |
| S4 | Thariq Shihipar, "Lessons from Building Claude Code: How We Use Skills" (gist mirror) | https://gist.github.com/Danm72/467f6d6cd193d19c0042371866d53b75 (original https://x.com/trq212/status/2033949937936085378) | 2026-03-17 **[SECONDARY mirror]** |
| S5 | Thariq, "thin prompts, thick artifacts, thin skills" | https://explainx.ai/blog/thin-prompts-thick-artifacts-thin-skills-thariq-july-2026 | 2026-07-16 **[SECONDARY]** |
| S6 | Simon Willison, live blog of Code w/ Claude 2026 | https://simonwillison.net/2026/May/6/code-w-claude-2026/ | 2026-05-06 |
| S7 | Cat Wu coverage (aggregated search; for example creatoreconomy.so, theneuron.ai) | https://creatoreconomy.so/p/inside-claude-code-how-an-ai-native-actually-works-cat-wu | 2025 to 2026, mixed **[SECONDARY]** |

---

## 1. Skill authoring

**1.1 Descriptions decide triggering. Write them in the third person, as what plus when, with the key use case first.**
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): the description "should include both what the Skill does and when to use it". "Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems." Claude chooses "from potentially 100+ available Skills".
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing." The whole listing is budgeted at 1% of the context window. When it overflows, descriptions are dropped "starting with the skills you invoke least".
- **Fact** ([D9](https://code.claude.com/docs/en/features-overview)): "If descriptions are vague or overlap, Claude may load the wrong skill or miss one that would help."
- **For Anvil:** each Anvil skill needs a description that does not overlap with any Superpowers description. Put the trigger in the first sentence. Drop narrative such as "the override layer that sits on top of Superpowers".

**1.2 Anthropic's sources disagree on how forceful a description should be.**
- **Fact** ([R2](#sources), skill-creator): "currently Claude has a tendency to 'undertrigger' skills ... please make the skill descriptions a little bit 'pushy'."
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): "If your prompts were designed to reduce undertriggering on tools or skills, these models might now overtrigger. The fix is to soften any aggressive language. Where you might have said 'CRITICAL: You MUST use this tool when...,' you can use more normal prompting such as 'Use this tool when...'". Also: "Instructions such as 'If in doubt, use [tool]' cause overtriggering."
- **Fact** ([R2](#sources)): "Claude only consults skills for tasks it can't easily handle on its own". Simple one-step queries may not trigger a skill however well the description matches.
- **For Anvil:** Anvil's problem is over-triggering, not under-triggering. The evidence shows it loaded in 64 sessions, including Python, Rust and C# repos it was not written for. Write descriptions in plain words and measure the trigger rate (see 1.8) instead of guessing.

**1.3 Length and progressive disclosure.**
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [D2](https://code.claude.com/docs/en/skills)): "Keep `SKILL.md` under 500 lines." D2 adds: "State what to do rather than narrating how or why." Only name and description load at startup. The body loads on invocation, and other files load when read.
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): "Keep references one level deep from `SKILL.md`." From nested references, Claude "might use commands such as `head -100` to preview content rather than reading entire files". Files over 100 lines need a table of contents.
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): "Default assumption: Claude is already very smart. Only add context Claude doesn't already have."
- **Secondary** ([S5](https://explainx.ai/blog/thin-prompts-thick-artifacts-thin-skills-thariq-july-2026), Thariq, Jul 2026): "Most SKILL.md files are too big." The entry point should be thin, with depth in the folder.
- **For Anvil:** each phase (brainstorm, spec, plan, build, finish) becomes a thin SKILL.md. Templates (spec format, plan format, progress file) and rules (test rules, change-flow-back rules) go in `references/`, each linked directly from SKILL.md.

**1.4 Skill content persists, and compaction cuts it.**
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): invoked skill content "stays there across later turns", and "Claude Code does not re-read the skill file". After auto-compaction, Claude Code re-attaches "the first 5,000 tokens of each", with a shared budget of 25,000 tokens filled from the most recent skill. "Older skills can be dropped entirely."
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): "put the most important instructions near the top of `SKILL.md`." Write guidance that applies to the whole task as standing instructions, for example "Run the tests after every edit" rather than "Run the tests".
- **For Anvil:** a long build session can lose the governor skill after compaction. Put the gates, the to-do rule and the verify rule in the first screen of each skill. The live progress file (see 3.6) carries state that a compaction would otherwise lose.

**1.5 Degrees of freedom: match rigidity to fragility. Don't railroad.**
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): use high freedom where "multiple approaches are valid" and low freedom where operations are "fragile and error-prone". Its analogy is a "narrow bridge with cliffs" versus an "open field".
- **Secondary** ([S4](https://gist.github.com/Danm72/467f6d6cd193d19c0042371866d53b75), Thariq, Mar 2026): "Give Claude the information it needs, but give it the flexibility to adapt to the situation." "The highest-signal content in any skill is the Gotchas section."
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): "Prefer general instructions over prescriptive steps ... Claude's reasoning frequently exceeds what a human would prescribe."
- **For Anvil:** keep the gates, the spec-line references and the test rules low-freedom. Keep the brainstorm technique, the code design and the split into agents high-freedom. Grow a "Gotchas" section from real failures, such as redesigns anchored on old code and silently skipped questions.

**1.6 Explain the why. Treat ALL-CAPS as a yellow flag.**
- **Fact** ([R2](#sources)): "Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs." "If you find yourself writing ALWAYS or NEVER in all caps ... that's a yellow flag."
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): "Claude can generalize from the explanation."
- **Counter-fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): in its iteration example, D1 still lists "using stronger language such as 'MUST filter' instead of 'always filter'" as a possible refinement. The guidance is not perfectly uniform.
- **For Anvil:** give every hard rule a one-clause reason. For example: "Edit a test only with a changed spec line, because otherwise you can't tell whether the test or the code moved."

**1.7 Scripts, checklists and feedback loops.**
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): "Prefer scripts for deterministic operations". Make clear whether Claude should run a script or read it. Give complex workflows "a checklist that Claude can copy into its response and check off". Use the loop "Run validator → fix errors → repeat". Use "plan-validate-execute" with a validated intermediate file for high-stakes batch work.
- **For Anvil:** a small script can check that every plan task and test names an existing spec line, and can flag items that point at a changed spec line. This is the "builder check" for traceability, and it is deterministic, so it fits D1's "prefer scripts" advice.

**1.8 Evaluate. Don't assume.**
- **Fact** ([D1](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)): "Create evaluations BEFORE writing extensive documentation." Build three scenarios, measure a no-skill baseline, then "Write minimal instructions". Test with Haiku, Sonnet and Opus.
- **Fact** ([D12](https://code.claude.com/docs/en/plugin-evals)): `claude plugin eval` runs cases with and without the plugin. Graders include `tool_used: Skill`, `tool_order`, `regex`, `file_exists` and `llm`. "The most common first finding is a `Δ` near zero with the case's `tool_used: Skill` grader failing". It needs v2.1.269 or later. Shell-granting suites need a sandbox, and "Native Windows has no backend, so run shell-granting suites under WSL2".
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): `skillOverrides` "doesn't apply to plugin skills". To compare against no plugin, use `claude plugin eval`.
- **For Anvil:** "better than today, with no regressions" can be measured. Write eval cases for: triggering on a feature request, not triggering on "explain this code", stopping at the spec gate, not stopping in AFK, and a one-line fix getting one check.

**1.9 The anthropics/skills repo.**
- **Fact** ([R1](https://github.com/anthropics/skills)): the frontmatter needs only `name` and `description`. The spec lives in `./spec` and at agentskills.io. A template is in `./template`. The README says the skills are "for demonstration and educational purposes only", so test them before relying on them.
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): outside Claude Code, only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` are allowed. Other keys "cause a hard error on upload".
- **For Anvil:** Claude Code-only frontmatter is fine, because Anvil targets Claude Code. Examples are `disable-model-invocation`, `context: fork` and `hooks`.

**1.10 Anthropic's own feature-dev plugin is a gate-heavy reference.**
- **Fact** ([R3](#sources)): it has 7 phases. Phase 3 says "**CRITICAL**: This is one of the most important phases. DO NOT SKIP." and "Wait for answers". Phase 4 runs 2 or 3 architect agents with different trade-offs, then asks the user to pick. Phase 5 says "DO NOT START WITHOUT USER APPROVAL". It uses TodoWrite throughout.
- **For Anvil:** this is a third reference point alongside Superpowers. Its "2 or 3 approaches with a recommendation" step matches Saad's "variations instead of an interrogation". Its ALL-CAPS gating is the style P1 and D8 now advise against. Its date is unknown, so it may be older guidance.

## 2. Plugin mechanics in Claude Code

**2.1 Declaring a SessionStart hook in a plugin.**
- **Fact** ([D6](https://code.claude.com/docs/en/hooks), [D3](https://code.claude.com/docs/en/plugins-reference)): declare it in `hooks/hooks.json` with a top-level `"hooks"` wrapper, or through `plugin.json` `hooks`, which merges with the file. "When a plugin is enabled, its hooks merge with your user and project hooks." The matchers are `startup`, `resume`, `clear`, `compact` and `fork`. `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` are available. On Windows, use exec form or quote the variable.
- **Fact** (local, superpowers 7.0.2): Superpowers' own hook uses the matcher `startup|clear|compact` and injects the whole `using-superpowers` SKILL.md.
- **For Anvil:** Anvil's startup hook should use the same matchers, so its statement is re-injected after `/clear` and compaction.

**2.2 Hook output has no special authority. It arrives as a system reminder.**
- **Fact** ([D6](https://code.claude.com/docs/en/hooks)): "Claude Code wraps the string in a system reminder and inserts it into the conversation at the point where the hook fired." For SessionStart, the placement is "at the start of the conversation, before the first prompt."
- **Fact** ([D6](https://code.claude.com/docs/en/hooks)), verbatim: "Write the text as factual statements rather than imperative system instructions. Phrasing such as 'The deployment target is production' ... reads as project information. Text framed as out-of-band system commands can trigger Claude's prompt-injection defenses, which causes Claude to surface the text to you instead of treating it as context."
- **Fact** ([D6](https://code.claude.com/docs/en/hooks)): output is capped at 10,000 characters. Above that, the output goes to a file with a 2,000-character preview, and Claude is not asked to read the file. A `<system-reminder>` tag inside the string is escaped.
- **Fact** ([D10](https://code.claude.com/docs/en/memory)): by contrast, "CLAUDE.md content is delivered as a user message after the system prompt". **Fact** ([B1](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)): output styles go into the system prompt and carry "the highest instruction-following weight of any method".
- **For Anvil:** the brainstorm's premise, "Anvil's startup hook is installed by the user, so it counts as one of those instructions", is not supported by the docs. See Contradiction C1. Phrase the hook as a fact, for example "This user runs Anvil as their development workflow; Anvil's brainstorm, spec, plan, build and finish skills cover what Superpowers' brainstorming, writing-plans, executing-plans, subagent-driven-development, requesting-code-review and finishing skills cover." If more weight is needed, the user's own `~/.claude/CLAUDE.md` is the documented channel. A plugin can also ship `outputStyles`, but that is untested (see Open items).

**2.3 Plugin dependencies exist. Conflicts do not.**
- **Fact** ([D3](https://code.claude.com/docs/en/plugins-reference), [D4](https://code.claude.com/docs/en/plugins/dependencies.md)): `dependencies` accepts `"name"`, `"name@marketplace"`, or `{name, marketplace, version}` with a semver range. Installing or enabling a plugin pulls in its dependencies. Disabling a plugin that another enabled plugin needs is refused. Cross-marketplace dependencies need `allowCrossMarketplaceDependenciesOn`. The manifest fields table has **no `conflicts` or `replaces` field**.
- **For Anvil:** Anvil must not declare Superpowers as a dependency, because the goal is independence. Nothing in the platform lets Anvil switch Superpowers off. Coexistence can only be negotiated through context.

**2.4 Enabling or disabling a plugin per project.**
- **Fact** ([D5](https://code.claude.com/docs/en/plugins/install.md)): `enabledPlugins` lives in `~/.claude/settings.json` (user scope), `.claude/settings.json` (project scope, committed) or `.claude/settings.local.json` (local scope). "the local setting overrides the project setting, and the project setting overrides the user setting." `claude plugin disable <name>@<marketplace> --scope local|project|user` changes the same settings. Without `--scope`, it acts on "the most specific scope whose settings already list the plugin".
- **Fact** (local): Saad's user settings use the form `"superpowers@claude-plugins-official": true`.
- **Fact** ([D3](https://code.claude.com/docs/en/plugins-reference)): `defaultEnabled` sets the starting state. Once a user's entry is written, it persists across plugin updates.
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): "Plugin skills are not affected by `skillOverrides`. Manage those through `/plugin` instead."
- **For Anvil:** a project can run "Anvil only" with `"superpowers@claude-plugins-official": false` in that repo's `.claude/settings.local.json`. There is **no way to hide individual Superpowers skills**, such as hiding `brainstorming` while keeping `writing-skills`. It is the whole plugin or nothing. The "both installed" row in §7 therefore depends entirely on wording (see C2).

**2.5 Namespacing.**
- **Fact** ([D2](https://code.claude.com/docs/en/skills), [D3](https://code.claude.com/docs/en/plugins-reference)): plugin skills appear as `/plugin-name:skill-name`. The frontmatter `name` replaces the directory segment. "The bare `/fancy` also invokes the skill unless another command already uses that name." Plugin names starting with `claude-` or `anthropic-` are reserved.
- **For Anvil:** `anvil:brainstorm` and `superpowers:brainstorming` will not clash by name. Their descriptions can still overlap in meaning, which is the real risk (see 1.1).

**2.6 Slash commands and skills have merged.**
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): "Custom commands have been merged into skills". `.claude/commands/*.md` still works. "If a skill and a command file share a name, the skill wins." In plugins, "Prefer `skills/` for new plugins" ([D3](https://code.claude.com/docs/en/plugins-reference)).
- **Fact** ([D2](https://code.claude.com/docs/en/skills), [D8](https://code.claude.com/docs/en/best-practices)): `disable-model-invocation: true` means only the user can start the skill, and its description stays out of context. D8 recommends this "For a workflow with side effects". `user-invocable: false` hides a skill from the `/` menu.
- **For Anvil:** `afk` and any finish, commit or ticket-push step are candidates for `disable-model-invocation: true`. Phase skills that only Anvil calls internally can use `user-invocable: false`, which shrinks the `/` menu.

**2.7 Other mechanics worth using.**
- **Fact** ([D2](https://code.claude.com/docs/en/skills)): the skill frontmatter field `hooks` registers hooks "when the skill is invoked, active for the rest of the session". `context: fork` with `agent` runs the skill in a subagent. `paths` limits automatic activation by file glob. `!`command`` injects live output when the skill loads.
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices), [D11](https://code.claude.com/docs/en/goal)): `/goal <condition>` is "a wrapper around a session-scoped prompt-based Stop hook". A small fast model checks the condition after each turn. It "doesn't run commands or read files", so the condition has to be visible in the transcript.
- **Fact** ([D10](https://code.claude.com/docs/en/memory)): `/doctor prompt-audit` (v2.1.283 or later) looks for "instructions written for older models, references to files or commands that don't exist, and files that contradict each other". It covers CLAUDE.md, rules, skills, commands and subagents.
- **For Anvil:** AFK can be enforced instead of merely requested. Inference: the `afk` skill could register a Stop hook through `hooks` frontmatter, or set a `/goal` such as "every item in progress.md is checked and the verify command exits 0". Run `/doctor prompt-audit` after updating Claude Code, to find conflicts between Anvil, Superpowers, CLAUDE.md and memory. That conflict is the "two skills contradicting" complaint.

## 3. Prompting current Claude models

The default in Claude Code is "Claude Opus 5.5 at medium effort on most plans" ([D8](https://code.claude.com/docs/en/best-practices)). For Opus 5.5, "the patterns in Prompting Claude Opus 5 remain a reasonable starting point" ([P3](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)).

**3.1 Emphasis now causes over-application.**
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices), "What you can stop doing"): "Add IMPORTANT or ALL CAPS to instructions Claude keeps missing" is listed as old advice. "Current ones follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule. If it's a rule that can't bend, turn it into a hook or a deny rule."
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "Tell Claude to keep going, loop until done, don't be lazy" is also old advice: "lines like that are more likely to cause over-work than fix a stall."
- **Fact** ([P4](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)): "The model treats an instruction that contains 'never' as absolute. For example, write 'ask for approval before deleting files' instead of 'never delete files'."
- **For Anvil:** remove every CRITICAL, MUST and ALL-CAPS line. Rewrite each "never" as a scoped rule with a reason. Example: afk's "never commit unless asked" becomes "commit only when the plan's finish step or the user says so", which also resolves the conflict with this repo's commit-and-push rule.

**3.2 Literal, precise instruction following.**
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): "Claude's latest models are trained for precise instruction following". "Can you suggest some changes" may produce only suggestions.
- **Fact** ([P2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)): "If your review prompt says 'only report high-severity issues' or 'be conservative,' the model might follow that instruction literally and report less; ask it to report everything and filter in a separate pass instead."
- **For Anvil:** reviewers should report every spec mismatch with a severity, and the main agent ranks and filters them. This matches "reports rank what's critical" without hiding findings at the source.

**3.3 Over-verification and self-checking on Opus 5 and later.**
- **Fact** ([P2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)): "Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions ('include a final verification step for any non-trivial task,' 'use a subagent to verify'), remove them: instructions like these cause over-verification ... The same applies to legacy harness scaffolding that adds separate verification steps."
- **Fact** ([P2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)): "Avoid instructing re-checks it already performs ('double-check your answer,' 're-verify before responding')".
- **For Anvil:** this explains the one-line change that got verified four times. It strongly supports "one verification run, sized to the change". The Superpowers skills `verification-before-completion` and "verify in subagent plus main agent" are exactly the scaffolding P2 says to remove.

**3.4 Subagents: Opus 5 delegates eagerly, so cap it.**
- **Fact** ([P2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)): "Claude Opus 5 delegates to subagents more readily than prior models." The sample damping prompt reads: "Delegate to a subagent only for large tasks that are genuinely independent and parallelizable ... Do not delegate work you can finish yourself in a handful of tool calls, and do not use subagents to verify or double-check your own work. If one subagent can complete the task, use one rather than several". The deterministic caps are `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`.
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "Handing the same task to a subagent doesn't make the answer any better. A fresh reviewer does help, because it hasn't seen your reasoning". Also: "a fresh subagent first has to gather context your conversation already had, so it can end up *slower*."
- **Fact** ([P4](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)): "If your system prompt, skills, or agent files tell the model to delegate, review those lines first."
- **Fact** ([E2](https://www.anthropic.com/engineering/multi-agent-research-system), **[OLD]**): "multi-agent systems use about 15× more tokens than chats". "Most coding tasks involve fewer truly parallelizable tasks than research." "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries."
- **For Anvil:** "fan out by default", which old Anvil does, is now counter-indicated. The plan should state why each split is parallel: independent files, a pinned contract, no shared state. The default is a single agent. This also bears on the 13 usage-limit hits and the 66-agent session.

**3.5 Scope control and over-engineering.**
- **Fact** ([P2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)): "Claude Opus 5 can also expand the scope of a task". Its sample: "Deliver what was asked, at the scope intended ... If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it."
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): the over-engineering prompt says "Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements."
- **Fact** ([P4](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2), measured on Fable 5.2): with no ownership statement, or with code presented as someone else's, "the model tended to add to the existing structure ... even when that duplicated existing code." With "You are the owner and long-term maintainer of this codebase", consolidation went from "under 10 percent of runs" to "about 75 percent". Output tokens rose "about 70 to 80 percent", and the model made unrequested changes.
- **For Anvil:** the "say so in a sentence and continue" pattern is a ready-made form of the "push back on requirement changes" rule. The ownership finding gives a measured mechanism for "redesigns anchored on old code". It applies to Fable 5.2 and has not been verified on Opus 5.5. Inference: when the spec says a part is being redesigned, say so explicitly ("the spec replaces X; design from the spec, not from X") rather than leaning on "reuse existing" rules.

**3.6 Long-horizon work, state files and to-do lists.**
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): "Use structured formats for state data" (JSON for test and task status). "Use unstructured text for progress notes". "Use git for state tracking". "Claude's latest models are extremely effective at discovering state from the local filesystem." The example start-up prompt is "Review progress.txt, tests.json, and the git logs."
- **Fact** ([P1](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)): "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."
- **Fact** ([P3](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)): "Treat a text-only end of turn as a report rather than as proof the task is done. Keep the task's parts in a checklist the model updates, such as a to-do tool or a file." If items are still open and no blocker is stated, send a continuation naming them, and "stop after two or three automatic continuations".
- **Fact** ([E5](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), **[OLD]**, via summary): one feature at a time, a feature list kept as JSON, `init.sh`, and progress files.
- **For Anvil:** this directly supports the proposals for "one live progress file" and "editing a test requires a changed spec line". Consider a JSON task list (id, spec lines, status) plus a Markdown progress log. This also answers the roughly 30 "done?" messages.

**3.7 Progress updates and final reports.**
- **Fact** ([P2](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)): Opus 5 "narrates readily". To shape updates: "give a brief update only when you find something important or change direction. When you finish, lead with the outcome". Files it writes "are often longer than on prior models".
- **Fact** ([P4](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)): "Write for an intelligent but low-context reader ... Put the key points in the first few sentences." It suggests "the style of ASD-STE100 Simplified Technical English".
- **For Anvil:** this matches Saad's plain-language spec requirement. Add a length calibration to spec and plan templates: "cover the substance, but do not pad".

**3.8 Unattended runs: finishing versus stopping.**
- **Fact** ([P3](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)): an unattended run ends early in four named ways. They are a summary that announces the next step, an offer to carry on, a list of decisions that block nothing, and deciding "this is a good place to report". P3 gives a paragraph to add "at the end of your system prompt from the first request of the session" and says to "leave the addition out of human-in-the-loop applications".
- **Fact** ([P4](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2)): on approvals, "say exactly what you want rather than sending a simple 'continue.'" A rule listing "sending messages to people outside this conversation" as needing approval "led the model to hold back about half of its routine requests". Under "Keep caution from piling up": "Name the steps that need no approval."
- **For Anvil:** AFK should name the steps it covers, such as answering its own design questions, choosing between variations and writing tests. It should also name the few that still stop, such as destructive git operations and pushing to main. "Skip all stops" is too vague. In attended mode, the gate prompt should ask for a specific approval, for example "Approve spec S1 to S14 as written?".

**3.9 Context engineering.**
- **Fact** ([E3](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), **[OLD]**): find the "smallest possible set of high-signal tokens". Avoid "brittle if-else hardcoded prompts" and also guidance that is too vague. Use just-in-time references and NOTES.md-style note files.
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "Running out of context is rarely the problem anymore" (1M window and auto-compaction). Even so, "/clear between tasks is still worth doing".
- **Secondary** ([E9](#sources), Nov 2026): telling the model exactly what to save backfired. When told to record only failures, "both Opus 5 and Opus 4.7 lost much of the performance boost". The stated rule is to state what memory is for without scripting how to use it.
- **For Anvil:** say what the decision log is for ("so Saad can see what was decided and why"). Don't script a rigid field list beyond the essentials.

## 4. Engineering blog and talks

**4.1 Simplicity, and strip scaffolding as models improve.**
- **Fact** ([E6](https://www.anthropic.com/engineering/harness-design-long-running-apps), Mar 2026): "Every component in a harness encodes an assumption about what the model can't do on its own." When a new model arrives, strip away "pieces that are no longer load-bearing". "Find the simplest solution possible, and only increase complexity when needed", which echoes [E1](https://www.anthropic.com/engineering/building-effective-agents) **[OLD]**.
- **Secondary** ([S6](https://simonwillison.net/2026/May/6/code-w-claude-2026/), Dianne Na Penn, May 2026, paraphrased): the teams doing best focus on "automated evals" and "simple scaffolding". She also said "design for the next model".
- **For Anvil:** this supports rebuilding Anvil as a small workflow rather than copying all of Superpowers. Each Anvil rule should name the failure it prevents, so it can be deleted when the model stops making that mistake.

**4.2 Planner, generator and evaluator. The spec stays high-level. Self-grading is lenient.**
- **Fact** ([E6](https://www.anthropic.com/engineering/harness-design-long-running-apps)): the planner focuses "on product context and high level technical design rather than detailed technical implementation", because spec errors cascade. Agents "reliably skew positive when grading their own work". "Tuning a standalone evaluator to be skeptical turns out to be far more tractable." Sprint contracts defined "what 'done' looked like for that chunk of work before any code was written."
- **Fact** ([E6](https://www.anthropic.com/engineering/harness-design-long-running-apps)): with Opus 4.6, the sprint construct was removed, and the evaluator moved "from per-sprint grading to a single pass at the end of the run". For work within the model's capability boundary, "the evaluator became unnecessary overhead."
- **For Anvil:** the plain-language spec and a separate skeptical reviewer are both supported. Per-chunk review is the open question (see C3). Saad's evidence, where per-task review caught real bugs and the 66-agent run collected 17 open spec items, is a local counter-datapoint to E6's finding.

**4.3 The verifier must be near-perfect, and test output must be compact.**
- **Fact** ([E7](https://www.anthropic.com/engineering/building-c-compiler), Feb 2026): "it's important that the task verifier is nearly perfect, otherwise Claude will solve the wrong problem." Test output should be a few lines, with details in log files, "ERROR and put the reason on the same line so grep will find it". A default `--fast` option ran "a random 1% or 10% sample". Agents "can't tell time and would spend hours on test runs." It is easy to see tests pass and assume the work is done, which is "rarely the case".
- **For Anvil:** this supports core-only tests plus a fast subset for build-time checks. It addresses the 20 to 30 minute suites. "Tests pass" is not "built what was asked", which supports adding a spec check to "verify".

**4.4 How people actually use Claude Code.**
- **Fact** ([E8](https://www.anthropic.com/research/claude-code-expertise), Jun 2026): "people make about 70% of the planning decisions but only 20% of the execution decisions." Experts get more work per instruction: about 12 actions per prompt against 5 for novices. Verified success is 28 to 33% for intermediate and above, against 15% for novices.
- **For Anvil:** human-owned planning with Claude-owned execution matches the two-gate flow. Gates belong at planning decisions, not execution decisions.

**4.5 Skills engineering post.**
- **Fact** ([E4](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), **[OLD]**): start with evaluation. "When the SKILL.md file becomes unwieldy, split its content into separate files". "Pay special attention to the name and description". Install skills "only from trusted sources".

**4.6 Steering mechanisms (staff blog).**
- **Fact** ([B1](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more), Jun 2026): it lists as mistakes "'Never' rules as instructions" and "'Always do X' as instructions", which should be hooks or permissions instead. A "30-line procedure in CLAUDE.md" belongs in a skill. Keep CLAUDE.md under 200 lines.
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "If you keep adding emphasis to a `CLAUDE.md` line and Claude still misses it, that's a sign the line belongs in a hook." "Keep the enforced set small ... If you ever find yourself at forty of them, most are probably preferences".

## 5. Workflows Anthropic staff describe publicly

**5.1 Spec first via interview, then build in a fresh session.**
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "Interview me until you could write the spec, then write it to SPEC.md." Claude asks "multiple-choice questions about the parts you haven't pinned down". "Once `SPEC.md` exists, start a fresh session to build from it, so the build begins with a clean context and a written definition of done."
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): the spec review prompt is "use a subagent to review the rate limiter diff against SPEC.md, check every requirement is implemented ... report gaps that affect correctness and skip style". It warns: "Don't drop the `skip style` part ... A reviewer that's asked to find problems will always find *something*. If you fix every finding, you end up with extra abstraction layers and tests for cases that can't happen."
- **For Anvil:** Anthropic's own reference flow is interview → SPEC.md → fresh session → build → review against SPEC.md. It is close to Anvil's flow. The fresh session between spec and build is the difference (see C5). The "skip style" warning should go into every Anvil reviewer brief.

**5.2 Plan mode, then auto-accept, then (later) auto mode.**
- **Fact** ([S1](https://www.infoq.com/news/2026/01/claude-code-creator-workflow/), Jan 2026, Boris Cherny): "If my goal is to write a Pull Request, I will use Plan mode, and go back and forth with Claude until I like its plan. From there, I switch into auto-accept edits mode and Claude can usually 1-shot it." "A good plan is really important!"
- **Secondary** (search summaries): Boris later said "I don't use that anymore. I use auto mode instead of plan mode." This is unverified.
- **Fact** ([D13](https://code.claude.com/docs/en/common-workflows)): plan mode is still documented. It is read-only until approval, and the plan can be edited in a text editor.
- **For Anvil:** Anvil's plan gate is the documented "approve the plan, then let it run" pattern. Inference: Anvil does not need Claude Code's plan mode, because its own written plan file plus the approval stop does the same job and survives across sessions.

**5.3 Verification is the top tip, and it is end-to-end.**
- **Fact** ([S2](https://x.com/bcherny/status/2044847858634064115), Apr 2026): verification "has always been a way to 2-3x what you get out of Claude, and with 4.7 it's more important than ever." His `/go` skill tests end to end (bash, browser or computer use), runs `/simplify`, and opens a PR. Its contents were not published.
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "Give Claude something it can run that comes back pass or fail." "Ask Claude for *evidence*: the command it ran and its output". `/verify` "has Claude build and run the app and look at the result."
- **Fact** ([S3](https://x.com/bcherny/status/2027534984534544489), Feb 2026): `/simplify` uses "parallel agents to improve code quality, tune code efficiency, and ensure CLAUDE.md compliance."
- **For Anvil:** Anvil's finish step could reuse the bundled `/simplify`, `/code-review` and `/verify` instead of reimplementing them. Inference: this fits "simple, not over-built". Verification should prove behaviour (run the thing) once, not repeat the same command at several levels.

**5.4 Parallel sessions and worktrees.**
- **Fact** ([S1](https://www.infoq.com/news/2026/01/claude-code-creator-workflow/)): Boris runs about 5 local sessions, each in its own checkout, plus 5 to 10 web sessions. About 10 to 20% are abandoned.
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): "give each its own checkout so the edits can't collide" (`claude -w`). `/batch` splits mechanical changes into 5 to 30 units with a plan you approve. "A second session is also the easiest independent reviewer you can get."
- **Secondary** ([S7](https://creatoreconomy.so/p/inside-claude-code-how-an-ai-native-actually-works-cat-wu), Cat Wu): her team prefers prototypes to multi-page specs ("The source of truth is the code base"). That interview is about 14 months old. She also advocates worktree-isolated agent fleets. As of 2026-11-05 she has left Anthropic.
- **For Anvil:** parallel build agents should get worktree isolation when they touch overlapping areas. For big mechanical splits, `/batch` is a built-in alternative to a hand-rolled fan-out.

**5.5 Keep it simple. Gotchas over procedures.**
- **Secondary** ([S4](https://gist.github.com/Danm72/467f6d6cd193d19c0042371866d53b75), Thariq, Mar 2026): the tips are "Don't State the Obvious", build a Gotchas section, avoid railroading, "the description field is not a summary", and on-demand hooks. "Verification skills are extremely useful".
- **Secondary** ([S5](https://explainx.ai/blog/thin-prompts-thick-artifacts-thin-skills-thariq-july-2026), Jul 2026): use a thin prompt, thick artifacts and a thin skill. Specs live in artifact files, and the prompt points at them. This is attributed to Thariq. **Unverified:** "HTML beats Markdown for specs".

**5.6 "Let Claude run without you" checklist.**
- **Fact** ([D8](https://code.claude.com/docs/en/best-practices)): before an unattended run, check five things. Does it know what done looks like? Can it check its own work? What is it allowed to touch? What stops it (`--max-turns`, budget)? Where does the result go, and who signs off? "The parts that stay with you are starting it, deciding what 'done' means this time, and approving the merge at the end."
- **For Anvil:** this maps cleanly onto AFK's preconditions. The approved spec answers "done". The plan's test strategy and verify command answer "check". Branch or worktree rules answer "touch". A continuation cap answers "stops". The decision log plus a final hand-back answers "sign-off".

---

## Contradicts or warns against the current plan

**C1. The authority the startup hook is assumed to carry (§7) is not documented.** The brainstorm says the hook "counts as one of" the user's instructions. The docs say hook output is a system reminder ([D6](https://code.claude.com/docs/en/hooks)), while CLAUDE.md arrives as a user message ([D10](https://code.claude.com/docs/en/memory)). D6 warns that imperative "out-of-band system commands" can trip prompt-injection defenses. **Implication:** write the hook as facts and test it with evals. Put the single coexistence sentence in Saad's own CLAUDE.md as well, or instead.

**C2. "Both installed" cannot be enforced, and Superpowers' hook competes directly.** Plugin skills ignore `skillOverrides` ([D2](https://code.claude.com/docs/en/skills)), and no manifest field expresses a conflict ([D3](https://code.claude.com/docs/en/plugins-reference)). Superpowers 7.0.2 injects all of `using-superpowers` on startup, clear and compact (local). Both hooks land as equal-standing system reminders. **Implication:** the "single statement settles it" claim is a hypothesis. Measure it with `claude plugin eval` on a with-Superpowers fixture. The only hard switch is disabling Superpowers per project through `enabledPlugins`.

**C3. Per-task spec review against Opus 5 guidance.** P2 says "do not use subagents to verify or double-check your own work" and to remove "legacy harness scaffolding that adds separate verification steps". E6 moved its evaluator to a single end-of-run pass on Opus 4.6. On the other side, D8 endorses a fresh reviewer ("it hasn't seen your reasoning"), and E6 found a separate skeptical evaluator works better than self-grading. **Implication:** frame the per-task check as independent review against spec lines, not as re-verification. Keep it cheap (diff plus spec lines only, "skip style"), and measure whether it beats one end-of-build review. Saad's evidence favours per-task review, but it comes from older models and an older Anvil.

**C4. Demoting TDD against Anthropic's long-run guidance.** P1 advises writing tests "before starting work" in a structured file and says "It is unacceptable to remove or edit tests". D8's model prompt says "write a failing test that reproduces it, then fix it". E7 says the verifier must be "nearly perfect". None of these require TDD everywhere. All of them warn that a no-stop build needs a reliable pass/fail check decided before the build. **Implication:** for "keep" tests, write them early against spec lines, at least for bug fixes, where a failing reproduction is Anthropic's default. Scaffold tests are fine. "Tests after the code found nothing" is consistent with this: tests written after the code tend to confirm what was built.

**C5. Anthropic's reference flow uses a fresh session between spec and build. Anvil runs straight through.** D8: "start a fresh session to build from it, so the build begins with a clean context". **Implication:** this is not fatal, since context limits are rare now ([D8](https://code.claude.com/docs/en/best-practices)). But a long brainstorm leaves rejected variations in context, which risks anchoring. Consider offering "build in a fresh session from spec.md and plan.md" as the default after the plan gate. Inference: this fits the multi-machine workflow too.

**C6. Old Anvil's "fan out by default" and "per-step checks find nothing".** P2, P4 and D8 all say current models over-delegate. Delegation multiplies cost, and E2 says coding rarely parallelizes well. **Implication:** the plan should justify each parallel split, and single-agent should be the default.

**C7. "Never" rules in afk and elsewhere.** P4: "never" is treated as absolute. B1 says never and always rules belong in hooks. **Implication:** scope each rule with its reason, or move it to a hook or permission. The commit conflict (afk "never commit" against the repo rule "commit and push every unit") is the concrete case to fix.

**C8. Forceful descriptions and the governor pattern.** Today's Anvil description says "Read Anvil FIRST, before any Superpowers process skill ...". That is the over-trigger pattern P1 describes, and the evidence (loads in unrelated repos) matches it. skill-creator's "pushy" advice (R2) points the other way, but it addresses under-triggering. **Implication:** plain descriptions, measured with evals.

**C9. Accumulated cautions.** P4 says memory and instruction files "collect cautions over time" and should be trimmed. Saad's evidence shows project rules and memory files overrode both skills. **Implication:** the rebuild should include a pass with `/doctor prompt-audit`, which needs v2.1.283 (this machine has 2.1.268), to remove stale rules that will fight the new Anvil.

**C10. Specs versus prototypes.** Cat Wu's team prefers prototypes to specs ([S7](https://creatoreconomy.so/p/inside-claude-code-how-an-ai-native-actually-works-cat-wu), secondary and old). This is a different team context, not a refutation. Saad's "2 or 3 variations with mocks" already leans toward prototypes in the brainstorm phase.

**C11. Markdown or HTML for specs (unverified).** Thariq reportedly prefers HTML specs ([S5](https://explainx.ai/blog/thin-prompts-thick-artifacts-thin-skills-thariq-july-2026), secondary). Saad's global rule defaults to Markdown. Saad's rule should win unless he chooses otherwise. Noted only for completeness.

**Guidance that supports the plan:** one verification sized to the change (P2), plain-language spec before build (D8, E6), two human gates at planning decisions (E8, D8 "approve the merge"), a live progress file and to-do list (P1, P3), "say so in a sentence and continue" pushback (P2), core-only and fast tests (E7), a "skip style" spec reviewer (D8), and simplicity (E1, E6, S6).

## Open or unverified

1. **Hook versus CLAUDE.md weight in practice.** No document compares how strongly Claude follows a plugin SessionStart reminder against a user CLAUDE.md line or a rival plugin's reminder. This needs an eval.
2. **A plugin `outputStyles` as a higher-authority channel.** B1 says output styles carry the highest weight, and D3 confirms plugins can ship `outputStyles`. Not tested: whether a plugin style can be active by default, and whether `keep-coding-instructions: true` avoids stripping the defaults. Using one may also be overkill.
3. **The full `enabledPlugins` reference entry was not retrieved,** because the settings-reference page was truncated. The scope and precedence rules come from [D5](https://code.claude.com/docs/en/plugins/install.md) and the format from Saad's own settings file.
4. **Feature availability on 2.1.268.** Not checked on 2.1.268: `/goal`, `hooks` in skill frontmatter, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, `/verify`. Confirmed to need a newer version: `claude plugin eval` (v2.1.269), `/doctor prompt-audit` (v2.1.283) and `engines` (v2.1.323).
5. **Boris dropping plan mode for auto mode** is known only from secondary summaries. **Cat Wu quotes** are secondary, and their dates are approximate.
6. **E9 (agent memory, Nov 2026):** the original page was not fetched. The claims come from secondary write-ups.
7. **Thariq's posts (S4, S5)** were read through mirrors and summaries, not the X originals.
8. **B2's date** (How Anthropic teams use Claude Code) was not confirmed on the page, and the "slot machine" quote comes only from secondary sources.
9. **Fable 5.2 findings (P4)** were measured on Fable 5.2, not on Opus 5.5, which is Saad's likely default. P1 says: "treat it as measured on that model and re-check it against your own evals before applying it to another." This covers the ownership sentence, "never" as absolute, and approval hold-back.
10. **E1, "Building effective agents",** was cited from its known thesis and not re-fetched.
11. **Not read:** "Demystifying evals for AI agents" (2026-01-09), "Trustworthy agents in practice" (2026-04-09, which discusses Plan Mode), "How we built Claude Code auto mode" (2026-03-25). They are possibly relevant to AFK safety and to Anvil's own eval design.
