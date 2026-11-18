# Superpowers 7.0.2 inventory: what it contains, and what Anvil keeps

- **Date:** 2026-11-18
- **Source read:** `~/.claude/plugins/cache/claude-plugins-official/superpowers/7.0.2/`. Every skill folder, including prompts, references and scripts. Also `hooks/`, `.claude-plugin/`, README, RELEASE-NOTES (v5.1 to v7.0.2 in full, older ones skimmed), AGENTS.md, `docs/testing.md`, `docs/porting-to-a-new-harness.md`, and the design specs that explain the current SDD and brainstorming shapes.
- **Compared against:** [brainstorm notes](../2026-11-18-brainstorm-notes.md) and `plugins/anvil/skills/*` on branch `anvil-rebuild`.
- **Not read in depth:** the visual-companion server code (`server.cjs`, 26 KB; skimmed for paths, auth and telemetry), `writing-skills/references/anthropic-best-practices.md` (a copy of Anthropic's skill-authoring docs), and the non-Claude harness shims (`.opencode/`, `.pi/`, `.hermes-plugin/` and others). None of these affect what Anvil keeps.

## Requirement key

Section numbers point into the brainstorm notes. The rest of this file cites these keys.

| Key | Requirement |
|---|---|
| R1 | When information is thin, offer 2 or 3 variations (researched, shown visually) instead of an interrogation (§2, §3.1) |
| R2 | Design questions are a wasted stop. Decisions go *into* the spec, where Saad actually reviews them (§2, §3.2) |
| R3 | Stop for approval after the spec and after the plan (§3.2, §3.3) |
| R4 | The plan holds the execution strategy (parallel or single), the test strategy and the to-do list (§3.3) |
| R5 | Build and verify run with no stops, and hand back a fully working result (§3.4) |
| R6 | "AFK" skips every stop, and each decision made on Saad's behalf is logged (§3.5) |
| R7 | No automatic extra checkpoints (§3.6) |
| R8 | Changes flow back: the spec, plan, code and reviews never disagree (§3.7) |
| R9 | Push back on requirement changes: change request or new feature, what it conflicts with, what it costs (§3.8) |
| R10 | Verification fits the change, runs once, and is never repeated by both subagent and main agent (§2, §4) |
| R11 | Tests only for the core. Every test can say why it exists. Keep tests vs scaffold tests (§4, §5) |
| R12 | When a fix touches a test or the code, say which one and why (§4) |
| R13 | Reports rank what's critical and what isn't (§4) |
| R14 | Simple solutions. Simplicity must not anchor a redesign on old code (§2, §5) |
| R15 | A visible to-do list and progress tracking, so Saad never has to ask "done?" (§2, §5) |
| R16 | A cheap per-task spec review comes back. It doesn't rerun tests (§2 evidence, §5) |
| R17 | The builder check survives (§2 "what worked") |
| R18 | Pin the shared contracts before splitting work. Parallel agents (§2 "what worked", §1) |
| R19 | The flow also covers non-code work: research, architecture, demos, mocks (§1, §6.3) |
| R20 | Self-contained. No Superpowers dependency. Credit kept. Anvil's own startup hook. Distinct skill names (§1, §7) |
| R21 | Reports and mocks are local files in the repo, never Artifacts (global `~/.claude/CLAUDE.md`) |
| R22 | Finishing is undecided: this repo says commit and push after every unit of work, but `afk` says never commit unless asked (§6.1) |
| R23 | Push back instead of agreeing. Don't take subagent findings on trust (§2 evidence) |

---

## 1. Package overview

### Versions and identity

- `.claude-plugin/plugin.json`: `"name": "superpowers"`, `"version": "7.0.2"`, author Jesse Vincent, `"license": "MIT"`, homepage `github.com/obra/superpowers`. The manifest has no `hooks`, `commands` or `agents` field. Claude Code auto-discovers `hooks/hooks.json`.
- **Installed here from `claude-plugins-official`**. Anvil's `plugin.json` depends on `superpowers@superpowers-marketplace` instead, which would install a second copy. The skills audit covers this.
- `RELEASE-NOTES.md` runs from v3.x (2025-10) to v7.0.2 (2026-11-03).
- **Versions that matter to Anvil:**
  - **v5.1.0** removed `commands/` (`/brainstorm`, `/write-plan`, `/execute-plan`) and `agents/code-reviewer.md`.
  - **v6.0.0** merged the two per-task reviewers into one prompt.
  - **v6.2.0** added the plan-scoped ledger and the five-round fix loop.
  - **v6.4.1** added Review Focus, the "Native" inline mode and `diagnosing-superpowers`.
  - **v6.4.2** made plans lean (signatures, not code).
  - **v7.0.0 to v7.0.2** rebuilt brainstorming and added the builder check.

### Files that ship

| Area | Files | What they are |
|---|---|---|
| Hook | `hooks/hooks.json`, `hooks/session-start`, `hooks/run-hook.cmd`, `hooks/hooks-cursor.json` | SessionStart bootstrap (§2 below) |
| Skills (15) | `skills/<name>/SKILL.md` + supporting files | See the per-skill sections |
| Brainstorming extras | `builder-check-prompt.md`, `visual-companion.md`, `scripts/{server.cjs, helper.js, frame-template.html, start-server.sh, stop-server.sh}` | Builder-check prompt, plus a zero-dependency Node server for browser mockups |
| SDD extras | `implementer-prompt.md`, `task-reviewer-prompt.md`, `re-review-prompt.md`, `references/{preflight, fix-loop, final-review, handling-reports, cannot-verify, batching, resuming}.md`, `scripts/{sdd-workspace, sdd-repo, task-brief, review-package}` | Subagent prompt templates, references loaded at the step that needs them, and bash helpers |
| executing-plans extras | `scripts/{task-start, task-done}` | Inline-mode helpers that share SDD's workspace |
| requesting-code-review extras | `code-reviewer.md` | The whole-branch reviewer prompt |
| TDD extras | `writing-good-tests.md` | Test-quality rules |
| Debugging extras | `root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md` + `.ts` example, `find-polluter.sh` | Techniques |
| diagnosing-superpowers extras | 10 analyst prompts, 4 references, 4 templates | Transcript forensics |
| writing-skills extras | `references/{discovery, bulletproofing, flowcharts, persuasion-principles, testing-skills-with-subagents, CLAUDE_MD_TESTING, anthropic-best-practices}.md`, `graphviz-conventions.dot`, `render-graphs.js` | Skill-authoring method |
| using-superpowers extras | `references/<harness>-tools.md` (7 harnesses) | Tool-name mappings |
| Other harnesses | `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `.pi/`, `.hermes-plugin/`, `.kimi-plugin/`, `.muse-plugin/`, `.antigravity-plugin/`, `.devin-plugin/`, `gemini-extension.json` + `GEMINI.md` | Not relevant to Anvil |
| Dev only | `tests/`, `docs/`, `scripts/`, `.github/` | Plugin tests and design history. `docs/superpowers/specs/` explains *why* the current shapes exist |

There is **no `commands/` and no `agents/`**. Every subagent is a `general-purpose` dispatch filled from a prompt template that sits next to its skill.

### Hard size limit worth copying

v7.0.1: "After a compaction, Claude Code re-attaches each skill cut off at 20,000 characters, so anything past that point is gone for the rest of the session." In one session, SDD lost its five-round cap and ran 18 fix rounds. `tests/skill-size/test-skill-size.sh` fails any `SKILL.md` of 20,000 bytes or more. Long material moves to `references/` and is read from disk at the step that needs it. **The current `anvil/SKILL.md` is 18,198 bytes, just under the line.**

---

## 2. How Superpowers starts itself (the SessionStart hook)

### Config: `hooks/hooks.json`

```json
{ "hooks": { "SessionStart": [ {
  "matcher": "startup|clear|compact",
  "hooks": [ {
    "type": "command",
    "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
    "powershell": "& \"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
    "shell": "bash",
    "async": false
} ] } ] } }
```

- **`matcher: startup|clear|compact`.** It re-injects after `/clear` and after compaction. There's no `resume`, because a resumed session keeps its context.
- **`"shell": "bash"`.** Claude Code 2.1.81 and later resolves this to Git for Windows. Older versions ignore the key. The `powershell` form exists for Copilot on Windows (v7.0.2).
- **`async: false`.** The context must land before the first turn.

### Wrapper: `hooks/run-hook.cmd`

A polyglot file: cmd.exe runs the batch half, and bash treats it as a no-op heredoc and runs the shell half.

- **On Windows**, it finds `bash.exe` in the standard Git paths, then `%LOCALAPPDATA%\Programs\Git`, then `where.exe $PATH:bash`. It skips the WSL launchers and anything in the current directory, which is a security fix. If it finds no bash, it **exits 0 silently**, so the plugin still works without the bootstrap.
- **On Unix**, it uses `$BASH`, then falls back to zsh.
- **Script names have no extension** (`session-start`, not `.sh`), because Claude Code on Windows prepends `bash` to anything containing `.sh`.

### Script: `hooks/session-start`

- **What it does:**
  - reads `skills/using-superpowers/SKILL.md` **in full, frontmatter included**;
  - uses only bash builtins, with no `cat`, `dirname` or subshell, because the startup `PATH` can be broken (anthropics/claude-code#43127) and each fork costs tens of milliseconds on Git Bash;
  - JSON-escapes the text;
  - prints the JSON with `printf`, with SIGPIPE ignored so the broken pipe on Windows doesn't spam errors.
- **Output on Claude Code**, chosen when `CLAUDE_PLUGIN_ROOT` is set without `COPILOT_CLI` or `MUSE_PLUGIN_ROOT`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "<EXTREMELY_IMPORTANT>\nYou have superpowers.\n\n**Below is the full content of your 'superpowers:using-superpowers' skill - your introduction to using skills. For all other skills, use the 'Skill' tool:**\n\n<full SKILL.md text>\n</EXTREMELY_IMPORTANT>"
  }
}
```

- **Only one field is emitted per platform.** The script's comment says: "Claude Code reads BOTH additional_context and hookSpecificOutput without deduplication, so we must emit only the field the current platform consumes." Cursor gets `additional_context` and Copilot gets a top-level `additionalContext`.
- **The porting guide's rule:** "**The bootstrap is the entire integration.** Without it, the skill files are inert." Its acceptance test is that "Let's make a react todo list" in a clean session triggers brainstorming before any code is written.

### What Anvil should copy

- Copy the `hooks.json` shape, `run-hook.cmd` and the builtin-only `session-start` almost verbatim, with credit.
- Inject a short Anvil bootstrap, not a long skill. This text is paid for on every startup, `/clear` and compaction. v6.1.0 compressed `using-superpowers` for exactly this reason.
- **When both plugins are installed** (notes §7), Anvil's bootstrap must say once that Anvil replaces Superpowers' brainstorming, planning, executing, review and finishing skills.
  - Superpowers' own bootstrap ends: "User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc, direct requests) take precedence over skills". Anvil's statement leans on that line.
  - **The risk:** both hooks inject at the same priority, and Superpowers' block is wrapped in `<EXTREMELY_IMPORTANT>` with "1% chance … ABSOLUTELY MUST" language. Whether a plugin hook counts as a "user instruction" is the open question the notes flag in §7. Test it on a live session before trusting it.

---

## 3. Skills, one by one

Each skill lists its trigger (the frontmatter `description`, quoted), its mechanisms, its prompt technique and tone, what must survive, what conflicts, and its stage.

### 3.1 `using-superpowers` (bootstrap / router)

- **Trigger:** "Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions".
- **Mechanisms:**
  - `<SUBAGENT-STOP>`: "If you were dispatched as a subagent to execute a specific task, ignore this skill."
  - `<EXTREMELY-IMPORTANT>`: "If you think there is even a 1% chance a skill might apply … you ABSOLUTELY MUST invoke the skill."
  - **The Rule:** invoke a skill before *any* response, including clarifying questions. "Before entering plan mode: if you haven't already brainstormed, invoke the brainstorming skill first." Announce "Using [skill] to [purpose]". "If it has a checklist, create a todo per item."
  - **Skill priority:** process skills (brainstorming, systematic-debugging) come before implementation skills.
  - A 12-row **Red Flags** table ("This is just a simple question" / "Questions are tasks. Check for skills.").
  - Platform adaptation pointers.
  - User instructions outrank skills.
  - `references/claude-code-tools.md`: an opt-in "orchestrator one layer down" mode. One mid-tier subagent runs the whole SDD loop, and its final message must carry "Rulings I made" verbatim.
- **Technique and tone:** the most forceful text in the package (caps, "not negotiable", "You cannot rationalize your way out of this"). It uses a rationalization table and a commitment device (announcing the skill).
- **Keep:**
  - `SUBAGENT-STOP`, so subagents don't load the workflow;
  - the "user instructions outrank skills" line;
  - "create a todo per checklist item" (R15);
  - the idea of process skill before implementation skill.
- **Conflicts:**
  - The 1% rule is the opposite of right-sizing (R10, R14). It's also part of why Anvil today adds a second always-on layer and the two contradict each other (notes §2).
  - "Before entering plan mode, brainstorm first" makes every plan-mode entry an interview (R1, R2).
  - The maximal tone is calibrated for older models. Superpowers' own v6.4.2 notes say Opus 5.5 "could get overzealous". The sibling research slice on current-model behavior should decide the tone.
- **Stage:** cross-cutting (startup). Rewrite as Anvil's own short bootstrap.

### 3.2 `brainstorming`

- **Trigger:** "You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning anything new, in software or out of it (a talk, a business, a renovation)."
- **Mechanisms:**
  - **Opening self-check:** "what do I know about what they want, and why?" If everything is in the request, just do it and say what you did.
  - **A mandatory order before implementing:**
    1. lay out the approaches in their own message and have the human pick one;
    2. write the design doc, short or full;
    3. get approval of the doc;
    4. invoke `writing-plans`.
  - **"Look Before You Ask":** read the referenced files and code until you can explain how things work today. "Never ask what the project or their context already answers."
  - **First-message recipes.** If the request is already specified, about 200 words: an echo, the findings, an invitation to correct, and then one question (the *why* if missing, else the biggest open fork with options and a pick). If nothing is open, the first message *is* the short design, and approval covers it. If it's under-specified, one open question with the reason. It offers to "just dive in" only when the user didn't ask for brainstorming.
  - **The conversation:**
    - "Ask a question only when the answer would change what gets built and neither the request nor the project answers it. Otherwise, state your call and your reason as a proposal they can correct."
    - "Process steps are always your calls."
    - Questions come one at a time, open until the *why* is known, then options with a recommendation.
    - Socratic, specific questions.
    - Recon: "go look … Say what you looked for and what you found."
  - **Ground to cover**, "territory, not a script": what kind of thing it is; why now; goals, non-goals and anti-goals; prior art; current state; details.
  - **"Lay out the approaches":** "Come up with several real alternatives and drop the weak ones … Sketch the two or three that remain … Recommend one and say why."
  - **Show, don't tell:** text sketches, plus the visual companion when "the look itself is theirs to decide".
  - **Spike:** a throwaway build is allowed with consent and skips plan and review. "Keeping what it produced is a new request that comes back through this gate."
  - **Play It Back:** chunks of 200 to 300 words, alternating with questions. "Only what they said goes in as theirs. Anything you filled in goes in as your proposal, with your reason."
  - **Size the Work:** small change (short doc) or project (full doc). Both have an **Approaches** part. "If it grows mid-task, stop, say so, and step up a size." Several independent projects are brainstormed one at a time.
  - **The Written Design:** intent and why; goals, non-goals and anti-goals; constraints; approaches; the parts of the how they decided; what's left to the builder.
  - **Builder check:** see §4.3 below.
  - **`<HARD-GATE>`:** "Nothing gets built until your human partner approves the design doc … Building includes writing product code, scaffolding, installing dependencies, creating projects, and invoking an implementation skill." The next skill is `writing-plans` "and no other skill".
  - **Red Flags** table: "I'll offer a menu of what they might want" / "Options steer. Ask them to describe it first." Also "They said 'sounds good' to the idea" / "Approval covers what you showed them."
  - **Visual companion:** offered just in time, in "its own message with nothing else in it", and never re-offered after a decline.
- **Files:**
  - spec: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, committed ("Your human partner's preferences override");
  - mockups: `<project>/.superpowers/brainstorm/<pid>-<ts>/content/*.html`;
  - clicks: `state/events` as JSON lines.
- **Technique and tone:** calm, positive recipes. It is the least shouty major skill, after the v7 rebuild ("filler questions dropped from 41 … to 23"). One hard gate and one red-flag table. It tells the model not to quote the skill to the user or use process jargon.
- **Keep:**
  - "Look Before You Ask";
  - "proposal they can correct beats a question", which is R2 in Superpowers' own words;
  - approaches (2 or 3, with a pick);
  - Play It Back with "theirs vs your proposal" labelling;
  - the written-design outline (it already has goals, non-goals and anti-goals, as R2 wants);
  - the builder check (R17);
  - spike-then-back-through-the-gate;
  - "If it grows mid-task, stop, say so, and step up a size";
  - splitting multi-project requests;
  - the HARD-GATE idea, as Anvil's spec stop (R3).
- **Conflicts:**
  - **R1.** The Red Flags row "I'll offer a menu … Options steer. Ask them to describe it first" and "Get them describing … open questions, with no example answers attached" are the opposite of variations-first. Saad wants 2 or 3 worked variations *when information is thin*, which is exactly when Superpowers insists on open questions. Rewrite it as: ask *why* once, then show variations.
  - **R2.** Play-back chunks and the approaches message are extra stops before the spec. Saad does his real review in the spec, so fold the approaches and the playback into the spec instead of separate conversational rounds.
  - **R21.** Mockups go to a gitignored `.superpowers/brainstorm/` behind a local server. Saad keeps mocks in `docs/<feature>/mocks/`.
  - **R20.** The spec path is `docs/superpowers/specs/` and the next skill is hard-wired to `superpowers:writing-plans`.
  - **Telemetry:** the companion page loads a logo from `primeradiant.com` with the version number, unless `SUPERPOWERS_DISABLE_TELEMETRY` or `DISABLE_TELEMETRY` is set. Strip it if the server is cloned.
  - **R9.** There's no pushback on requirement changes against an earlier decision.
- **Stage:** brainstorm and spec.

### 3.3 `writing-plans`

- **Trigger:** "Use when you have a spec or requirements for a multi-step task, before touching code".
- **Mechanisms:**
  - **Reader model:** "an engineer who has not seen this codebase or this spec … What they cannot know is what you decided." "DRY. YAGNI. TDD. Frequent commits."
  - **Save to** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`. User preference overrides.
  - **Scope check:** one plan per independent subsystem.
  - **File Structure first:** "This is where decomposition decisions get locked in."
  - **Task Right-Sizing:** "the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate … split only where a reviewer could meaningfully reject one task while approving its neighbor."
  - **A required header:**
    - an agentic-worker banner naming SDD or executing-plans;
    - Goal, Architecture and Tech Stack;
    - **`Spec:` path** ("the spec travels with it");
    - **`## Global Constraints`** ("exact values copied verbatim from the spec. Every task's requirements implicitly include this section");
    - **`## Review Focus`** ("The five input classes or failure modes the spec implies but no task's tests exercise … The spec is a vision document … its silence on an input is not permission for that input to break the program"; each line gets a test in the owning task).
  - **Task block:** `### Task N: …`, then **Files** (Create, Modify with line ranges, Test), then **Interfaces** (Consumes and Produces with exact signatures: "this block is how they learn the names and types neighboring tasks use"), then `- [ ]` steps in RED, GREEN, commit order.
  - **What a Step Contains:** a test step carries names and assertions with the spec's values; a code step carries the signature, file and pinned values ("The implementer writes the body"); a verification step carries the command and expected output. "A plan longer than the code it describes has written the code instead."
  - **Self-Review checklist:** spec coverage, a step scan for placeholders and transcripts, type consistency across tasks, Review Focus, and **proportion** against the spec.
  - **Execution Handoff:** link the plan, ask for review, and offer "Subagent-driven" or "Native" with a one-sentence recommendation. **Wait.**
- **Technique and tone:** moderate. One "MUST" (the header). A positive recipe ("What a Step Contains") replaced a banned-word list after micro-tests (see §5).
- **Keep:**
  - the Spec pointer, Global Constraints, Interfaces and Review Focus. These are R18's "pin the contracts", and the Interfaces block is what makes parallel split possible;
  - Task Right-Sizing ("worth a fresh reviewer's gate"), which ties tasks to R16;
  - the step-content recipe, and the proportion check against the spec (R14);
  - self-review for spec coverage;
  - the handoff "review the saved plan before anything runs" (R3).
- **Conflicts:**
  - **R4.** There's no execution-strategy section: no parallel vs single choice, no split. There's no test strategy (which tests, why, keep or scaffold). The to-do list is only `- [ ]` checkboxes, which nothing ticks.
  - **R11.** "TDD" is in the reader model and in every task's step template (write the failing test, watch it fail).
  - **R22.** "Commit" is a step in every task.
  - **R8.** Spec lines aren't numbered, so tasks can't name the spec lines they cover.
  - **R20.** The handoff names Superpowers skills.
  - **Overlap:** the current Anvil "lean plan template" attacks a "full code" plan that **no longer exists**. v6.4.2 already made plans signatures-only.
- **Stage:** plan.

### 3.4 `subagent-driven-development` (SDD)

- **Trigger:** "Use when executing implementation plans with independent tasks in the current session".
- **Mechanisms:**
  - **Per task:** a fresh implementer, then **one task reviewer with two verdicts** (spec compliance and code quality), then a scoped fix loop. At the end, one whole-branch review.
  - **Continuous execution:** "Do not pause to check in with your human partner between tasks."
  - **"Rulings, not stalls":** every conflict or ambiguity is decided and logged as `Ruling: <what you decided> — <why> — <what it costs if wrong>`.
  - "Four things stop you, and only these":
    1. an irreversible or destructive operation;
    2. a security-sensitive action;
    3. a side effect outside the worktree (merge, push to a shared branch, publish);
    4. "a plan so broken that every path forward is a guess".
  - **Setup:**
    - a worktree via `using-git-worktrees`, and never on main without consent;
    - a **plan-scoped workspace**: `bash scripts/sdd-workspace PLAN_FILE` prints `<repo>/.superpowers/sdd/<plan-basename>/`, which ignores itself via its own `.gitignore` (`*`) and keeps a `plan-path` marker;
    - a **ledger** at `<workspace>/progress.md` whose first line is `# SDD ledger — plan: <path>`;
    - "Track progress in a ledger file, not only in todos";
    - read the plan once, then "create a todo per task";
    - read the Spec ("the spec is the authority the plan argues from");
    - run the **pre-flight scan** (`references/preflight.md`): a table row for every pair of tasks that share a file or interface, and a row for every task checking that its own text agrees with itself, with rulings recorded in the ledger.
  - **Model selection:**
    - the cheapest model for a mechanical task, standard for integration, most capable for architecture and for the final review;
    - reviewers are "scaled to the diff's size, complexity, and risk";
    - "Always specify the model explicitly", because an omitted model inherits the expensive one;
    - "Turn count beats token price": a mid-tier model is the floor for reviewers.
  - **Dispatch recipe:**
    - record BASE first;
    - `bash scripts/task-brief PLAN N` writes `task-N-brief.md`;
    - the dispatch contains, in order: (1) one line on where the task fits; (2) the brief path, "read this first"; (3) interfaces and decisions from earlier tasks; (4) your resolution of any ambiguity; (5) the report path and the report contract;
    - "Never make a subagent read the whole plan file";
    - no pasted history (one dispatch hit 42k characters, "99% was pasted history");
    - **"Never dispatch multiple implementation subagents in parallel (conflicts)."**
  - **Reports:** the implementer writes `task-N-report.md` and returns at most 15 lines with a status: `DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT`. `references/handling-reports.md` covers each case.
  - **Review:**
    - `bash scripts/review-package PLAN BASE HEAD` writes `review-<base7>..<head7>.diff` (commit list, stat and `-U10` diff);
    - the reviewer gets the brief, the report, the package and Global Constraints copied verbatim;
    - controller rules for the reviewer prompt: no open-ended directives, no "re-run tests", and **no pre-judging**: "If the prompt you are writing contains 'do not flag,' 'don't treat X as a defect,' 'at most Minor,' or 'the plan chose' — stop";
    - "⚠️ Cannot verify from diff" items go to the controller (`references/cannot-verify.md`).
  - **Fix loop** (`references/fix-loop.md`, "Read it again before every round"):
    - Minors go to the ledger as deferred;
    - plan-mandated findings are ruled on against the spec;
    - rounds 1 to 3 resume the original implementer, and rounds 4 and 5 use a fresh, more capable implementer;
    - every round ends with a **scoped re-review** (`re-review-prompt.md`);
    - a ledger line is written after each round;
    - at the five-round cap, the controller adjudicates (park with a ruling, or rule on a load-bearing finding and carry it forward);
    - "Never fix findings yourself in the controller session".
  - **Completion:** `Task <N>: complete (commits <base7>..<head7>, review clean)`, then the todo is marked complete.
  - **Final review** (`references/final-review.md`):
    - a branch package from the merge-base, reviewed with `code-reviewer.md` on the most capable model, pointed at the deferred minors and parked lines;
    - **ONE** fix subagent with the full findings list, then one scoped re-review, and no second wave;
    - **Finish:** collect every `Ruling:` line into "Rulings I made", then delete the workspace ("the git history is the record now"), then run `finishing-a-development-branch`.
  - **Batching** (`references/batching.md`): small same-shape edits go in one dispatch.
  - **Resuming** (`references/resuming.md`): trust the ledger and `git log` over memory.
- **Technique and tone:**
  - firm and specific;
  - a positive dispatch recipe, which the micro-tests showed beats a prohibition;
  - token tripwires (the "do not flag" phrase check);
  - a 9-row rationalization table;
  - "read the reference again before every round", which survives compaction;
  - evidence-cited rules ("a real session's final-review fix wave cost more than all its tasks combined").
- **Keep:**
  - **the per-task review (R16)**: brief + report + package → one reviewer, spec verdict first, "Do Not Trust the Report", no test re-runs, ⚠️ cannot-verify;
  - the implementer status contract and report file;
  - "Rulings, not stalls" and the four stops (R5, R6);
  - the ledger as recovery memory (R15);
  - the pre-flight scan (R18);
  - explicit model per dispatch;
  - the dispatch recipe;
  - no subagent spawns its own subagents;
  - the scoped re-review, the five-round breaker and the single final fix wave;
  - batching;
  - "Rulings I made" (R6).
- **Conflicts:**
  - **R18.** "Never dispatch multiple implementation subagents in parallel" vs parallel agents. Anvil's parallel-safe test (disjoint write sets, no decision dependency) plus the Interfaces block can make a *wave* of tasks parallel, with each still getting its own review.
  - **R10.**
    - The implementer prompt says "run the full suite once before committing".
    - TDD (loaded under SDD) says to run "the project's suite" before calling the change done.
    - The final review exists, and then `finishing` re-runs the full suite, and runs it again after merge.
    - So one change runs the full suite three or four times.
  - **R11.** The implementer writes tests "following TDD if task says to", and the plan template always says so.
  - **R15.** The ledger is git-ignored scratch and **deleted at the end**. Progress isn't visible outside the session's todo list.
  - **R8.** Rulings live only in the ledger and the final message. The spec and plan aren't updated when a ruling changes them.
  - **R22.** The implementer commits every task.
  - **R20.** `.superpowers/` paths and `superpowers:` skill names are hard-coded in the scripts and prose.
- **Stage:** build and review/verify.

### 3.5 `executing-plans` ("Native", inline)

- **Trigger:** "Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or no subagent tool is available".
- **Mechanisms:**
  - the same workspace, ledger, rulings and four stops as SDD;
  - a pre-flight scan limited to the Interfaces blocks;
  - **REQUIRED SUB-SKILL:** load TDD before Task 1;
  - per task: `scripts/task-start PLAN N` prints the brief and BASE, then the work follows each step's `Expected:` line ("The code is wrong" leads to systematic-debugging; "The plan is wrong" leads to a ruling);
  - **a completion contract** (every named test ran, every `Expected:` was compared, every deviation has a `Ruling:`), with verification-before-completion governing the claim;
  - `scripts/task-done PLAN N BASE -- <test cmd>` runs the tests, keeps the log and appends the ledger line only if they pass;
  - one final reviewer on the most capable model, given the Review Focus and the rulings, with a "Declined to judge" list that the executor rules on;
  - findings are re-graded "by effect";
  - ONE fix pass, with each fix done RED to GREEN and the full suite run;
  - Minors are deferred.
- **Technique and tone:** firm. A rationalization table ("I remember what Task N says" / "You remember a summary. The brief has the exact values.").
- **Keep:**
  - a single-agent mode for small or tightly coupled work, which is R4's "parallel or single";
  - the completion contract;
  - re-grading by effect;
  - the "Declined to judge" rulings;
  - one final fresh review.
- **Conflicts:**
  - **R11.** TDD is mandatory, and the fix pass is RED to GREEN.
  - **R10.** It explicitly rejects running the suite only at the end ("Per-step runs are how you learn which step broke it").
  - **R16.** There's no per-task review, by design. Anvil's single-agent mode should still get the cheap per-task spec check.
- **Stage:** build.

### 3.6 `test-driven-development` (+ `writing-good-tests.md`)

- **Trigger:** "Use when implementing any feature or bugfix, before writing implementation code".
- **Mechanisms:**
  - **Iron Law:** `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`. "Write code before the test? Delete it. Start over."
  - RED, verify RED, GREEN, verify GREEN, refactor. "'Other tests' means the project's suite, not just your file."
  - an 11-row rationalization table, a red-flags list ending "Delete code. Start over with TDD.", a verification checklist, and "Exceptions (ask your human partner)".
  - **`writing-good-tests.md`:**
    - "Every test names the break it catches" and "Every test exercises the real thing";
    - a **gate function**: "Name the production change that would make this test fail. Cannot name one → redesign … Only intentional decisions → change detector";
    - derive expectations by hand; no mirror assertions; "Behavior, not text"; "Your code, not the framework";
    - mock at the right level, and mirror real data completely;
    - "Ship the tests the behavior needs and only those: trivial code and human prose earn none, and a test written to satisfy process costs maintenance forever";
    - the **mutation check**.
- **Technique and tone:** maximal discipline language ("Violating the letter of the rules is violating the spirit of the rules", "Delete means delete"), with good/bad code pairs.
- **Keep:**
  - **all of `writing-good-tests.md`.** "Name the break it catches" *is* R11's "every test can say why it exists", and the gate function is R11's core-only filter;
  - the mutation check;
  - "Test fails? Fix code, not test", which is the seed of R12 and §5's "editing a test to make it pass requires a changed spec line";
  - red-green as a **tool** for reproducing a reported bug, as the current Anvil floor already says.
- **Conflicts:**
  - **R11 and R5.** The Iron Law and "Delete means delete" demand TDD on everything. That's the slowness and the stopped sessions Saad reported.
  - **R10.** Run the whole suite on each change.
  - **R7.** "Exceptions (ask your human partner)" is a stop.
- **Stage:** build (test strategy belongs in plan).

### 3.7 `verification-before-completion`

- **Trigger:** "Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always".
- **Mechanisms:**
  - **Iron Law:** `NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE`;
  - **gate function:** IDENTIFY, RUN (the full command, fresh), READ, VERIFY, then claim. "Skip any step = lying";
  - a claim/requires table, including: "Agent completed → VCS diff shows changes / Agent reports 'success'" and "Requirements met → Line-by-line checklist / Tests passing";
  - red flags ("should", "probably", "Great!");
  - "ALWAYS before … Moving to next task; Delegating to agents".
- **Technique and tone:** maximal.
- **Keep:**
  - evidence before a claim;
  - "Agent reports success → check the diff" (R23);
  - **"Requirements met = line-by-line checklist, not tests passing"**. This is the "did we build what was asked" check that Anvil lost (notes §2, the déjà vu root cause) and maps to R8 and R16.
- **Conflicts:**
  - **R10.** "Execute the FULL command (fresh, complete)" before *every* claim, including "moving to next task". That's the 1-line-change-verified-4-times pattern. Rewrite it as: once, by the main agent, sized to the change.
- **Stage:** review/verify, and cross-cutting.

### 3.8 `requesting-code-review` (+ `code-reviewer.md`)

- **Trigger:** "Use when completing tasks, implementing major features, or before merging to verify work meets requirements".
- **Mechanisms:**
  - mandatory after each SDD task, after a major feature, and before merge;
  - a `general-purpose` dispatch of `code-reviewer.md` with DESCRIPTION, PLAN_OR_REQUIREMENTS, BASE_SHA and HEAD_SHA;
  - Critical gets fixed now, Important before proceeding, Minor is noted, and you push back if the reviewer is wrong.
  - **`code-reviewer.md` (the whole-branch reviewer):**
    - a "Senior Code Reviewer" persona;
    - **"The spec is a vision document … a reasonable person's expectation is a requirement, and a spec's silence is not permission"**;
    - **"Declined to judge"**: list every behavior set aside, so nothing is dropped silently;
    - read-only;
    - no sub-dispatching;
    - checks for plan alignment, code quality, architecture, testing and production readiness;
    - calibrated severity (Critical, Important, Minor);
    - a "Ready to merge? Yes/No/With fixes" verdict;
    - DO and DON'T lists.
- **Technique and tone:** medium. A persona, a structured output and a calibration block.
- **Keep:**
  - `code-reviewer.md` as the final whole-branch review;
  - the "vision document" and "Declined to judge" clauses;
  - the severity ranking (R13).
- **Conflicts:**
  - The SKILL.md example uses `HEAD~1` as BASE. SDD explicitly forbids that ("silently drops all but the last commit").
  - It overlaps the separate `cross-model` skill for the second-opinion role.
- **Stage:** review/verify.

### 3.9 `receiving-code-review`

- **Trigger:** "Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable - requires technical rigor and verification, not performative agreement or blind implementation".
- **Mechanisms:**
  - READ, UNDERSTAND, VERIFY, EVALUATE, RESPOND, IMPLEMENT;
  - forbidden phrases ("You're absolutely right!", any thanks);
  - if anything is unclear, ask about all of it before implementing any of it;
  - external feedback gets five checks before you act on it;
  - YAGNI: "grep codebase for actual usage";
  - when to push back, and how to correct your own pushback;
  - reply in GitHub threads.
- **Technique and tone:** strong prohibitions on specific phrases, which act as a tripwire.
- **Keep:**
  - verify-before-implement and push back with reasons (R23);
  - "IF conflicts with your human partner's prior decisions: Stop and discuss", which is the seed of R9;
  - the YAGNI grep (R14).
- **Conflicts:**
  - "STOP - do not implement anything yet, ASK" on unclear items is a stop under AFK (R6). It needs the same ruling route as SDD.
  - It overlaps `cross-model`'s AGREE / DISAGREE / NEEDS-CHECK triage, which is the better-structured version.
- **Stage:** review/verify.

### 3.10 `systematic-debugging`

- **Trigger:** "Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes".
- **Mechanisms:**
  - **Iron Law:** `NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST`;
  - four phases:
    1. root cause: read the errors, reproduce, check recent changes, instrument every component boundary, trace the data flow;
    2. pattern: find working examples and diff against them;
    3. hypothesis: one at a time, smallest test;
    4. implementation: a failing test, a single fix, verify;
  - **"If ≥ 3 fixes failed: STOP and question the architecture … Discuss with your human partner"**;
  - red flags, "your human partner's signals you're doing it wrong" ("Stop guessing", "We're stuck?"), and a rationalization table;
  - the references: backward root-cause tracing, four-layer defense in depth, condition-based waiting (plus a TypeScript example), and `find-polluter.sh` (bisects which test leaves state behind).
- **Technique and tone:** strong (Iron Law, "You MUST complete each phase").
- **Keep:** everything. The notes list it under "what worked". The 3-fix rule pairs with `cross-model`'s "same problem failed twice" trigger.
- **Conflicts:**
  - Phase 4 says to use `superpowers:test-driven-development` for the failing test. Point it at Anvil's test rules instead (a reproduction test is a legitimate keep test).
  - "Discuss with your human partner" after 3 fails is a stop. Under AFK it becomes a logged ruling plus a cross-model consult.
- **Stage:** cross-cutting (build and verify).

### 3.11 `dispatching-parallel-agents`

- **Trigger:** "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies".
- **Mechanisms:**
  - one agent per independent problem domain;
  - each prompt is focused, self-contained and specific about its output, with constraints ("Do NOT change production code");
  - "Multiple dispatch calls in one response = parallel execution";
  - afterwards: review the summaries, check for conflicts, run the full suite, spot-check;
  - a "When NOT to use" list.
- **Technique and tone:** soft and instructional. It's mostly a worked example.
- **Keep:**
  - the brief shape and the "one response = parallel" mechanic, for research and checking (the notes' "parallel agents for research and checking" worked);
  - conflict checking after agents return.
- **Conflicts:**
  - It's framed around debugging test failures only, not building (R18, R19).
  - It doesn't have Anvil's stronger parallel-safe test (disjoint writes, no decision dependency).
- **Stage:** cross-cutting (research, build fan-out).

### 3.12 `using-git-worktrees`

- **Trigger:** "Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated workspace exists via native tools or git worktree fallback".
- **Mechanisms:**
  - **Step 0:** detect isolation (`GIT_DIR` vs `GIT_COMMON`, with a submodule guard);
  - **ask consent** before creating a worktree;
  - prefer the native `EnterWorktree` tool, and fall back to `git worktree add` under `.worktrees/`, checking that it's ignored first;
  - project setup by stack;
  - a **baseline test run** ("If tests fail: Report failures, ask whether to proceed");
  - a rationalization table.
- **Technique and tone:** moderate.
- **Keep:**
  - detect-before-create, native tool first, and the ignore check;
  - "Never start on main without consent", already in Anvil's floor.
- **Conflicts:**
  - The consent question and the baseline-failure question are stops (R5, R7).
  - A full-suite baseline run adds another suite run (R10).
  - Saad already works on feature branches (this repo is on `anvil-rebuild`).
  - A worktree also loses untracked files, which conflicts with this repo's "never end with unpushed work" rule.
- **Stage:** build setup (optional).

### 3.13 `finishing-a-development-branch`

- **Trigger:** "Use when implementation is complete, all tests pass, and you need to decide how to integrate the work".
- **Mechanisms:**
  - Step 1: run the full suite, and stop if it's red;
  - detect the environment;
  - confirm the base branch ("Confirm before merging");
  - **an exact menu**: 1 merge locally, 2 push and open a PR, 3 keep as-is. "Wait for their answer";
  - discard only on an explicit request, with the typed word `discard`;
  - after a merge, run the tests on the merged result;
  - worktree cleanup only under `.worktrees/` or `worktrees/`, and never `--force`;
  - a rationalization table ("The push was rejected — force-push will fix it").
- **Technique and tone:** firm. An exact menu text, which acts as a commitment device.
- **Keep:**
  - the safety rules: no force-push, never `--force` a worktree removal, confirm the base, typed confirmation for discard;
  - a test run on the tree you integrate. This should be the *one* final verification (R10), not a second one.
- **Conflicts:**
  - **R22.** The menu-and-wait doesn't fit this repo's "commit and push after every unit of work", or AFK.
  - **R10.** Step 1 re-runs the full suite after SDD's final review, and Option 1 runs it again after merging.
  - It has no ticket update (`ticket-update`) and no spec or plan sync (R8).
- **Stage:** finish.

### 3.14 `writing-skills`

- **Trigger:** "Use when creating new skills, editing existing skills, or verifying skills work before deployment".
- **Mechanisms:**
  - TDD for docs: **RED** (pressure scenario without the skill, rationalizations recorded verbatim), **GREEN** (minimal skill), **REFACTOR** (close loopholes);
  - **Iron Law:** "NO SKILL WITHOUT A FAILING TEST FIRST";
  - **"Match the Form to the Failure"** (see §5);
  - micro-tests: "One fresh-context sample per call … Always include a no-guidance control … 5+ reps … Manually read every flagged match … Variance is a metric";
  - `references/discovery.md`: "Description = When to Use, NOT What the Skill Does". The evidence: "A description saying 'code review between tasks' caused an agent to do ONE review, even though the skill's flowchart clearly showed TWO reviews";
  - invoke scripts through their interpreter (`bash scripts/x`), because packagers strip exec bits;
  - a deployment checklist.
- **Technique and tone:** strong. It quotes persuasion research (Meincke et al. 2025: "33% → 72%").
- **Keep:** don't clone it. It isn't part of the flow, and the notes (§7) keep it usable from Superpowers. But **use its findings when writing Anvil** (§5).
- **Conflicts:** none. Not replaced.
- **Stage:** none (meta).

### 3.15 `diagnosing-superpowers`

- **Trigger:** "Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a skill that didn't fire, 'it took too long', 'why is it so expensive', 'what is it doing' — or wants to build a bug report …".
- **Mechanisms:**
  - problem intake (one question at a time, then a written problem statement);
  - locate the session JSONL files, and record rejected candidates;
  - a case file at `~/.superpowers/diagnosing-superpowers/<session-id>/`;
  - seven parallel analyst subagents (skill timeline, plan adherence, repeated work, stumbles, quality evidence, request conflicts, cost and time);
  - "Every finding cites `path:line`. No citation, no finding";
  - a report template;
  - optional GitHub issue and scrubbed bundle, gated on approval.
- **Technique and tone:** firm hard rules. A red-flags table.
- **Keep:** don't clone it as a skill. It's Superpowers-specific. **Its method is what produced the notes' "[evidence]" section.** The `plan-adherence.md` prompt ("steps silently changed … steps invented … drift immediately after a structural event") is a ready-made audit for R8. Consider an Anvil "what went wrong" mode later.
- **Stage:** none (meta).

---

## 4. The four mechanisms the brief asked about

### 4.1 The handoff: brainstorming → writing-plans → SDD

1. **Brainstorming** ends at the HARD-GATE. The human approves the design doc, then "invoke superpowers:writing-plans and no other skill".
   - Spec file: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, committed.
   - Format: a plain document covering intent and why; goals, non-goals and anti-goals; constraints; Approaches (2 or 3, trade-offs, which was picked and why); the how they decided; what's left to the builder; and calls marked as Claude's.
2. **Writing-plans** writes `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`.
   - Header: the agentic-worker banner, Goal, Architecture, Tech Stack, `**Spec:** <path>`, `## Global Constraints` and `## Review Focus`.
   - Each `### Task N:` carries Files, Interfaces and `- [ ]` steps.
   - It ends by asking the human to review the plan and choose **Subagent-driven** or **Native**, with a recommendation. **It waits.**
3. **SDD:**
   - `sdd-workspace` resolves the workspace, and the ledger is created or resumed;
   - it reads the plan and the spec, makes a todo per task, and runs the pre-flight scan;
   - per task, `task-brief` extracts `### Task N` (the heading must use the English word "Task" followed by an ID with a digit);
   - implementer, then report file, then `review-package`, then reviewer, then the fix loop, then the ledger line;
   - final review, the "Rulings I made" message, `rm -rf` of the workspace, then `finishing-a-development-branch`.
4. **What travels between stages:** files only. The spec path is in the plan header, and the brief, report and diff paths are in each dispatch. The controller never pastes plan text or diffs into its own context.

**Workspace files (all git-ignored, deleted at the end):** `<repo>/.superpowers/sdd/<plan-basename>/` holds:
- `plan-path`
- `progress.md` (the ledger)
- `task-N-brief.md`
- `task-N-report.md`
- `review-<base7>..<head7>.diff`
- `task-N-tests.log` (inline mode)

**Ledger line formats:**
- `Task <N>: complete (commits <a>..<b>, review clean | <K> parked | tests: <cmd> → <result>)`
- `Task <N>: minor (deferred): …`
- `Task <N>: fix round <R>/5 (…)`
- `Task <N>: parked — <finding> — Ruling: …`
- `Ruling: <what> — <why> — <cost if wrong>`
- `Final: minor (deferred): …` and `Final: fixed <finding> — <test> RED→GREEN, suite N/N`

### 4.2 The per-task review in SDD (the piece the evidence says was lost)

**History.** Until v6.0.0 there were two serial reviewers per task: `spec-reviewer-prompt.md`, then `code-quality-reviewer-prompt.md` (which delegated to the merge-review template). v6.0.0 merged them into **one** `task-reviewer-prompt.md` that returns **two verdicts**. The reason was cost: "per-dispatch overhead dominating cost", and quality reviewers had cost "4-8× what spec reviewers cost". The spec verdict stays first.

**Dispatch inputs:**
- the model (required);
- `[BRIEF_FILE]`, the same brief the implementer used;
- `[GLOBAL_CONSTRAINTS]`, copied verbatim from the plan or spec ("the reviewer's attention lens");
- `[REPORT_FILE]`;
- `[BASE_SHA]` and `[HEAD_SHA]`;
- `[DIFF_FILE]` from `review-package`.

**The reviewer prompt, summarized:**

1. **Frame:** "This is a task-scoped gate, not a merge review — a broad whole-branch review happens separately".
2. **Reading:**
   - read the diff file once ("The diff's context lines ARE the changed files");
   - don't re-run git;
   - don't crawl the codebase;
   - look outside the diff only for "a concrete risk you can name", one focused check per risk, naming both the risk and the check. Changed contracts, lock ordering and shared mutable state are legitimate reasons to check call sites.
3. **Read-only.** No mutating the working tree, index, HEAD or branch.
4. **No sub-dispatching.** "A reviewer you spawn duplicates one of them at full cost, and its verdict counts for nothing."
5. **Do Not Trust the Report.** "Treat the implementer's report as unverified claims … Design rationales in the report are claims too: 'left it per YAGNI,' 'kept it simple deliberately,' … a stated rationale never downgrades a finding's severity."
6. **Tests:** "Do not re-run the suite to confirm their report." Run a single focused test only for a specific doubt; otherwise recommend heavy validation instead of running it. Noise in reported output is a finding. "Illegibility of the evidence is not invalidation of it."
7. **Part 1, Spec Compliance:**
   - **Missing**: skipped, missed, or claimed without implementing;
   - **Extra**: unrequested features, over-engineering, "nice to haves";
   - **Misunderstood**: right feature built the wrong way, or the wrong problem solved;
   - batched briefs are checked file by file;
   - requirements in unchanged code or spanning tasks are reported as **⚠️ Cannot verify from diff**.
8. **Part 2, Code Quality:**
   - separation of concerns, error handling, DRY without premature abstraction, edge cases;
   - tests verify real behavior, not mocks, and cover the task's edge cases;
   - one responsibility per file, independent units, follows the plan's file structure, new or significantly grown files.
   - "file:line references for every finding and for any check you would otherwise answer with a bare 'yes.'"
9. **Calibration:**
   - "Important means this task cannot be trusted until it is fixed";
   - "Coverage could be broader" is Minor;
   - a plan-mandated defect is reported as Important and labelled plan-mandated ("The plan's authorship does not grade its own work; the human decides");
   - praise first.
10. **Output:**
    - `### Spec Compliance`: ✅ or ❌ with file:line, plus ⚠️ items;
    - `### Strengths`;
    - `### Issues` (Critical, Important, Minor), each with file:line, what's wrong, why it matters and the fix;
    - `### Assessment`: **Task quality: Approved | Needs fixes**.
    - "begin directly with the spec-compliance verdict … no preamble, no process narration, no closing summary."

**The scoped re-review prompt** (`re-review-prompt.md`):
- inputs: the brief, the verbatim findings, the report with fix notes appended, and the fix-range diff;
- verdict each finding **ADDRESSED | NOT ADDRESSED** with file:line ("'Attempted' is not addressed");
- report new breakage in the fix diff only;
- issues outside the fix diff go under "Out-of-Scope Observations" and are non-blocking;
- round verdict.

**Implementer prompt essentials** (`implementer-prompt.md`):
- read the brief first;
- "Ask them now" before starting;
- implement, test, verify, commit, self-review, report;
- "run the focused test … run the full suite once before committing";
- no subagents;
- file-size discipline;
- "It is always OK to stop and say 'this is too hard for me.' Bad work is worse than no work";
- self-review for completeness, quality, YAGNI and testing;
- a TDD RED/GREEN evidence block in the report;
- return at most 15 lines.

**For R16:**
- The review already doesn't rerun tests, already reads one packaged diff, and already starts with spec compliance.
- What it lacks is **numbered spec lines**. The brief carries task text, not "S3 says …", so "does this match S3" isn't possible yet.
- Anvil's version should hand the reviewer the spec lines the task names and ask for a verdict per line.
- For a cheaper seat, the spec part can run alone on small tasks, with the quality part left to the final review. That's a decision for the design, not this inventory.

### 4.3 The builder check

`brainstorming/builder-check-prompt.md`. It's dispatched to a fresh `general-purpose` subagent once a project-sized written design exists. Small changes skip it.

```
You are a talented [DOMAIN, e.g. "software engineer", "event planner",
"bakery consultant"]. You've been handed a design document and asked to
put together a plan to build what it describes. You will not be able to
talk to the person who wrote it.

Read [DOCUMENT_PATH].

Report only the questions you'd still need answered before you could plan
this well: places where you'd have to guess and a wrong guess would
matter. For each, give the question and why the answer changes the plan.
Rank them by importance.

Skip anything the document explicitly leaves to the builder, and anything
you could reasonably decide yourself. Skip nitpicks about wording.

If nothing important is left, say "nothing important left".
```

**What the controller does with the answers.** It says up front that "a reviewer will read it first and you may come back once with a few questions". It doesn't hand over the document until the check is back. Then it sorts the builder's questions into three piles:
- **Answered already**: put the answer in the doc.
- **Minor**: settle it and mark it in the doc as "your call".
- **Theirs**: one message, most important first.

The doc is then updated and handed over "with a short list of the calls you made". "That's the only round of questions the check produces." Without a subagent tool, the controller reads the document as the builder itself.

It replaced v6's `spec-document-reviewer-prompt.md` (a checklist for completeness, consistency, clarity and YAGNI, with an iterate-until-approved loop).

**For Anvil (R17, R2, R6):**
- Keep the prompt nearly verbatim.
- The "Minor, marked as your call" pile *is* "decisions go into the spec".
- The "Theirs" pile is the list "genuinely Saad's to decide at the top" (notes §5).
- Under AFK, the Theirs pile becomes logged decisions at the top of the spec instead of a message.
- Consider also running it on the **plan** (as "an implementer who can't talk to the planner") before the plan stop.

### 4.4 What Superpowers already does that Saad wants

| Saad wants | Superpowers 7.0.2 already has | Gap |
|---|---|---|
| Variations instead of questions (R1) | "A proposal they can correct, plus your reason for it, often beats a question." "Lay out the approaches": 2 or 3 with a pick. "When they say 'just guess' … propose something concrete." The visual companion offers side-by-side options (`.options`, `.cards`, `.split` classes, click events). Spikes | It insists on *open* questions until the why is known, and its red flags call menus "steering". No web research for variations. Mocks aren't saved to `docs/` |
| Decisions in the spec, not as stops (R2) | "Process steps are always your calls … Do them and say so." "Any choice you make goes in the design as your call, never as something they agreed to." The builder check's "Minor" pile | Approaches and play-back are still separate conversational rounds before the doc |
| Spec stop and plan stop (R3) | HARD-GATE on the design doc. writing-plans waits for the plan review | It also adds an "approaches" stop and an execution-method question |
| No stops during build (R5, R6) | SDD and inline: "Do not pause to check in", "Rulings, not stalls", the four named stops, and "Rulings I made" in the final message | Brainstorming, worktrees, TDD exceptions, receiving-review and finishing all still ask |
| To-do tracking (R15) | "create a todo per item" (bootstrap), "create a todo per task" (SDD and inline), `- [ ]` plan steps, the ledger `progress.md` | The ledger is git-ignored and deleted at the end. Plan checkboxes are never ticked. No user-readable progress file |
| Change flow-back (R8) | "The spec is the binding authority, the plan is its argument". Plan-mandated conflicts are ruled on against the spec. The `Spec:` pointer | Rulings never update the spec or plan. They live in the ledger, then the final message, then the ledger is deleted. **This gap causes "plan says A, code says A1".** `ticket-update` already demands "any change from the spec, and that the spec was updated in the same change" |
| Pushback on requirement changes (R9) | `receiving-code-review`: "IF conflicts with your human partner's prior decisions: Stop and discuss". Brainstorming: "If you found something they may not have considered … say so plainly" | No check against earlier decisions in the spec |
| Right-sized ceremony (R10, R14) | The brainstorming opening check ("make the icon cornflower blue": just do it), short vs full doc, task right-sizing, batching, the proportion check, and reviewers not re-running tests | TDD and verification still demand a full suite per claim |
| Tests that say why they exist (R11) | `writing-good-tests.md`: "Every test names the break it catches", the gate function, and "trivial code and human prose earn none" | No keep vs scaffold split, and no test-to-spec-line link |

---

## 5. Prompt-engineering findings worth reusing

From `writing-skills`, `docs/superpowers/specs/2026-06-10-positive-instruction-redesign-design.md` and the release notes. These are measured by Superpowers' own micro-tests, not opinion.

- **What works and what backfires** (from the 2026-06-10 micro-tests):
  - **Tripwires work:** "if the prompt you are writing contains 'do not flag' … stop".
  - **Recognition tables work:** rationalization and red-flag tables "read at decision time".
  - **Discrete-directive prohibitions work** when there's no competing incentive. "Do not ask the reviewer to re-run tests" had 0/5 violations.
  - **Composition prohibitions backfire:** "don't restate the brief" produced *more* restated values (4.4) than no guidance (3.6). A positive recipe ("your dispatch should contain (1)…(5)") gave 3.0 with zero variance.
  - **Nuance clauses dilute recipes:** "Don't X unless it matters" reopens the negotiation.
  - **Exemption clauses don't scope.**
  - **Ties go to the shorter phrasing.**
- **Descriptions say when to use the skill, never the workflow.** A workflow summary in the description gets followed *instead of* the body. The current `anvil` description is about 1,100 characters of workflow summary ("implement first and test after … fan independent work out … lean contract plans … verify once"). By Superpowers' own evidence, that is a likely reason Anvil's body rules were applied unevenly.
- **Keep skills under 20,000 bytes** and move material to `references/`, read again "before every round". This survives compaction.
- **Hand artifacts over as files.** "Everything you paste into a dispatch prompt — and everything a subagent prints back — stays resident in your context."
- **Name the model on every dispatch.**
- **Invoke bundled scripts with `bash scripts/x`** and an absolute path from the working tree. v7.0.2 fixed agents running helpers against the plugin cache.
- **The tone ranges** from the bootstrap's "1% … ABSOLUTELY MUST" through the TDD and verification Iron Laws to brainstorming's calm recipes. The v7 brainstorming rebuild deliberately moved *away* from interrogation and shouting and measured fewer filler questions. The research slice on current Claude models should set Anvil's tone. Superpowers' own trend (v6.2 "recap and persuasion prose removed across the library") points toward fewer caps.

---

## 6. Stage mapping

**Keep** means copy it, with light edits for names and paths. **Rewrite** means keep the idea and change the rule. **Drop** means not in Anvil.

| New-flow stage | Superpowers pieces feeding it | Verdict | Notes |
|---|---|---|---|
| **Startup** (cross-cutting) | `hooks/hooks.json`, `run-hook.cmd`, `session-start` | **Keep** | Swap the injected text for a short Anvil bootstrap. Add the "replaces Superpowers' X, Y, Z" line (notes §7) |
| | `using-superpowers` body | **Rewrite** | Keep `SUBAGENT-STOP`, user-instructions precedence and "todo per checklist item". Drop the 1% rule, the always-brainstorm-before-plan-mode rule and the caps |
| **Brainstorm** | `brainstorming`: opening check, Look Before You Ask, proposal over question, approaches, ground to cover, spike, split projects, "step up a size" | **Rewrite** | Variations-first when information is thin (R1). Approaches and playback fold into the spec (R2). Add pushback on changed requirements (R9) and the non-code path (R19) |
| | `visual-companion.md` + `scripts/*` | **Rewrite or optional** | Either clone the server with telemetry stripped and output to `docs/<feature>/mocks/`, or let `ui-mockup` write self-contained HTML files (R21). The click-to-select event loop is the valuable part |
| | `dispatching-parallel-agents` | **Keep** (merged) | For parallel research behind the variations |
| **Spec** | Written Design outline, the "Approaches" part, "calls marked as yours" | **Keep and extend** | Add numbered spec lines, a decision record (call, reason, alternatives) and "Saad's to decide" at the top (notes §5) |
| | `builder-check-prompt.md` + the three-pile triage | **Keep** | R17. Optionally pair it with `cross-model` |
| | HARD-GATE | **Rewrite** | Becomes the spec stop. Skippable under AFK (R6) |
| **Plan** | `writing-plans`: Spec pointer, Global Constraints, Interfaces, Review Focus, right-sizing, the step recipe, self-review, proportion | **Keep** | R18 contracts. The Interfaces block makes parallel split checkable |
| | Execution handoff (SDD vs Native) | **Rewrite** | Becomes the plan's *execution strategy* section: parallel waves vs single agent, decided in the plan, and Saad approves it at the plan stop (R4) |
| | TDD step template, "Commit" step | **Drop or rewrite** | Replace with the plan's test strategy (keep vs scaffold tests, each naming a spec line) (R11). The commit policy is decided under R22 |
| | Current Anvil lean-plan frontmatter `todos:` and the parallel-safe test | **Keep** (from Anvil) | Merge with the Superpowers header: the todo list and progress (R15) |
| **Build** | SDD: dispatch recipe, brief and report files, status contract, model selection, no sub-dispatch, batching, ledger, pre-flight, "Rulings, not stalls", four stops | **Keep** | Paths renamed off `.superpowers/` |
| | SDD "never parallel implementers" | **Rewrite** | Parallel waves of parallel-safe tasks, each task still reviewed (R18) |
| | `executing-plans` (inline) + `task-start`/`task-done` | **Rewrite** | The single-agent mode. Keep the completion contract. Drop mandatory TDD. Add the cheap per-task spec check (R16) |
| | `implementer-prompt.md` | **Rewrite** | Keep the escalation and self-review. Drop "full suite before committing" and TDD-by-default (R10, R11). Report "test changed or code changed, and why" (R12) |
| | `test-driven-development` (Iron Law) | **Drop** | Red-green survives as a tool for bug reproduction and gnarly pure logic |
| | `writing-good-tests.md` | **Keep** | The heart of R11 |
| | `systematic-debugging` + references | **Keep** | Point Phase 4 at Anvil's test rules |
| | `using-git-worktrees` | **Rewrite (optional)** | Keep detection, the native-tool preference and the ignore check. Drop the consent and baseline-suite stops by default |
| **Review/verify** | `task-reviewer-prompt.md` | **Keep and extend** | Add a per-spec-line verdict (R16, R8). Spec verdict first. No test reruns |
| | `re-review-prompt.md`, `fix-loop.md` (5-round breaker), `cannot-verify.md`, `handling-reports.md` | **Keep** | |
| | `final-review.md` + `code-reviewer.md` | **Keep** | The vision-document clause, "Declined to judge", one fix wave, "Rulings I made" (R6, R13) |
| | `verification-before-completion` | **Rewrite** | Keep evidence before claims, the "requirements met = line-by-line checklist" check and "check the diff, not the agent's word". Sized to the change, once, by the main agent (R10) |
| | `receiving-code-review` | **Rewrite** (merge) | Merge into the triage with `cross-model`'s AGREE / DISAGREE / NEEDS-CHECK. Keep the pushback rules (R23) |
| | `requesting-code-review` SKILL.md | **Drop** | Its template lives on in final review. Its `HEAD~1` example is a known bug |
| **Finish** | `finishing-a-development-branch` | **Rewrite** | Keep the safety rules (no force-push, base confirmation, never `--force` a worktree removal, typed `discard`). The one final test run goes here, not a second one. Replace the menu with the R22 decision. Add the spec and plan sync check (R8) and `ticket-update` |
| | SDD workspace deletion | **Rewrite** | Keep the progress file and decision log in `docs/<feature>/` (R15, R6). Delete only the briefs, reports and diffs |
| **Meta** | `writing-skills` | **Not cloned** | Stays a Superpowers skill (notes §7). Use its §5 findings while writing Anvil |
| | `diagnosing-superpowers` | **Not cloned** | Reuse its `plan-adherence` analyst idea for an R8 audit later |
| | `references/*-tools.md` (non-Claude harnesses), `.opencode`, `.pi`, and other harness folders | **Drop** | Anvil targets Claude Code |
| | `references/claude-code-tools.md` ("orchestrator one layer down") | **Keep as an option** | Cheaper controller for long plans. Must relay "Rulings I made" verbatim |

---

## 7. The current Anvil skills: overlaps, conflicts and plug-in points

### 7.1 `anvil` (today's governor)

- **Overlaps Superpowers 7.0.2:**
  - Lean contract plans: Superpowers v6.4.2 already made plans signatures-only.
  - Continuous execution: SDD already does it.
  - Batched fixes: SDD's single final fix wave.
  - File-based handoffs: SDD's briefs, reports and packages.
  - Cheapest capable model: SDD's model selection.
  - Escalation triggers: SDD's four stops, plus brainstorming's "step up a size".
  - Non-negotiable floor: verification-before-completion, with "a review pass before merge" matching the final review.
  - Labelled assumptions: brainstorming's "your proposal, with your reason" and SDD's `Ruling:`.
- **Conflicts:**
  - **The override table describes Superpowers as it was, not 7.0.2.**
    - It says `writing-plans` produces a "Comprehensive plan: full code". That's false since v6.4.2.
    - It says SDD/`executing-plans` is "Sequential task-by-task with checkpoints". That's false since v5.1 and v6.4.1.
    - Every session the model weighs an override against a rule that no longer exists. That's a plausible part of the "contradicting instructions" and the déjà vu (notes §2).
  - **The verification table removes the per-task review.**
    - Agents may run only the type-check, and the "Implement only" brief forbids tests.
    - Its claim that interleaved checks catch nothing "this pass would miss" is contradicted by the evidence in notes §2. SDD's task reviewer is the piece to restore (R16).
  - **"When Anvil and a Superpowers skill disagree, Anvil wins"** plus "consult Anvil first" is the two-layer setup that notes §7 replaces with a single bootstrap.
  - **The anti-slop rules** ("preserve behavior, minimize changes, reuse utilities") are the likely cause of redesigns anchoring on old code (notes §2, R14).
  - **Tiers barely gated anything** (Tier 0 was never chosen). Superpowers' own sizing (quick task, small change, project) is plainer and sits after intent, not before.
  - **The description summarizes the workflow**, which is the failure mode in §5.
  - **The dependencies** `claude-session-driver` (needs tmux) and `episodic-memory` aren't on this machine (audit §8).
- **Keep from Anvil:**
  - the **parallel-safe test** (disjoint write sets, no decision dependency, "pin the contract and the consumers become parallel-safe");
  - the plan frontmatter `todos:` with `parallel:` and `depends-on:`;
  - the "Data-tier contracts" list;
  - the "What earns a test" layer table, merged with `writing-good-tests.md` into keep vs scaffold;
  - the early-verify exception for unknown blast radius (shared theme token, router table, code generator);
  - the `## Open questions` and `## Key design decisions` sections;
  - "Describing parallelism you never execute is the thing Anvil exists to prevent."
- **Plug-in points:** Anvil becomes the flow itself, so the rest of this section is about the siblings plugging into Anvil.

### 7.2 `afk`

- **Overlaps:**
  - SDD and inline's "Rulings, not stalls", the four stops and "Rulings I made" are AFK inside the build stage.
  - AFK's "when to stop anyway" and "stop late" match SDD's four stops and its "a plan so broken that every path forward is a guess".
- **What AFK has that Superpowers lacks:**
  - a richer decision-log entry: what was ambiguous, the choice and reason, confidence, "what would change it", blast radius;
  - ordering the log by review value;
  - "Prefer reversible" and "prefer repo precedent";
  - the finish report order;
  - never commit, never leave the machine.
- **Conflicts:**
  - **R22.** AFK says "Never commit unless the user explicitly asked", but SDD and writing-plans commit every task and this repo's CLAUDE.md says commit and push after every unit. One rule has to win.
  - AFK's table maps onto *Anvil* escalation triggers that will change.
  - AFK covers only the build. Under R6 it must also cover the brainstorming HARD-GATE, the builder-check "Theirs" pile, the plan stop, worktree consent, the finishing menu, `receiving-code-review`'s "ask first" and the debugging "3 fails, discuss" stop.
- **Plug-in points:**
  - **One decision-log format** for SDD's `Ruling:` lines and AFK entries. Keep AFK's fields and SDD's "cost if wrong" (the same as blast radius).
  - Write it into the spec (decisions before the build) and the progress file (decisions during the build), not only the final message (R6, R8).
  - **Gates:** each of Anvil's stops checks one flag, "AFK on / skip this phase".

### 7.3 `ui-mockup`

- **Overlaps:**
  - brainstorming's "Show, don't tell", the visual companion (mockups, side-by-side options, click-to-select), "Lay out the approaches" (2 or 3), and spikes;
  - `writing-plans` has nothing for UI.
- **Conflicts:**
  - **R21.** It tells Claude to publish an Artifact (audit §4).
  - It asks for "a quick thumbs-up" before implementing, which is an extra stop unless it's folded into the spec stop (R7).
  - The Superpowers companion stores mocks in gitignored `.superpowers/brainstorm/`. Saad's practice is `docs/<feature>/mocks/`, with variants (`mock-a`, `mock-b`), numbered rounds (`-r2`, `-r3`) and a "what the liked mocks miss" note.
  - It names neither `frontend-design` nor the companion.
- **Plug-in points:**
  - **Brainstorm stage:** the producer of R1's visual variations. Anvil calls it when the work has a screen.
  - **Spec stage:** the spec links the chosen mock and its "still misses" list, with spec lines referencing mock states (empty, loading, error).
  - **Build:** UI tasks name the mock they implement.
  - Decide whether Anvil clones the companion server (live click selection) or just opens self-contained HTML from `docs/`.

### 7.4 `ux-audit`

- **Overlaps:** nothing in Superpowers checks a *rendered* UI. Reviews are diff-only. The closest Superpowers piece is `code-reviewer.md`'s "reasonable person … would expect".
- **Conflicts:**
  - It "applies the fixes" without asking. Saad's real audits end with owner decisions. Under the new flow, fixes must go back through the spec if they change behavior (R8).
  - It names `superpowers-chrome`, which isn't installed. `chrome-devtools-mcp` (with `a11y-debugging`) and `playwright-core` are what work here.
  - Its severity is "fix now / consider". It should be P0/P1/P2 tied to user harm (R13).
  - "whenever MrError asks".
- **Plug-in points:**
  - **Review/verify stage**, after UI tasks (or once in the final review for UI-heavy plans). Findings are ranked and checked against spec lines.
  - Fixes in scope enter the fix loop. Behavior changes become spec edits flagged for re-check (R8).
  - Output goes to `docs/<feature>/YYYY-MM-DD-<feature>-ux-audit.md` with a sibling `.json` of measurements.

### 7.5 `cross-model`

- **Overlaps:**
  - The builder check, the task reviewer and the final reviewer are all *same-family* fresh reviewers.
  - Its triage (AGREE / DISAGREE / NEEDS-CHECK, "agreement between two models is a signal, not proof") is a stronger form of `receiving-code-review`.
  - Its "same problem failed twice" trigger sits next to systematic-debugging's 3-fix rule.
- **Conflicts:**
  - Naming. The global `~/.claude/CLAUDE.md` says the `cross-model-review` skill is the source of truth, but the repo skill is `cross-model` (audit §1).
  - The machine-side tooling (commands, scripts, "write your own findings before reading Gemini's") isn't in the repo yet.
- **Plug-in points:**
  - **Spec:** an optional second-family builder check for expensive-to-reverse designs.
  - **Plan:** a review before the plan stop, when the split or contracts are risky.
  - **Final review:** a second-family review of the branch package (`review-package` output is already a single file, which suits cross-model's file route).
  - **Debugging:** after 2 failed fixes.
  - **Research:** behind R1's variations (Gemini plus a Claude subagent, adjudicated).
  - Anvil's plan should say which of these run (R4). None run automatically except where the plan or Saad says (R7).

### 7.6 `ticket-update`

- **Overlaps:**
  - **Planning:** "Breaking a plan into tickets: split into tasks of 3 days or less, number them in build order, set blocks and blocked-by, … mark what can run in parallel". That matches writing-plans' task right-sizing plus Interfaces plus Anvil's parallel annotation.
  - **Approvals:** "Spec approved (2026-11-19) by <name>" matches the brainstorming HARD-GATE.
  - **Completion:** a completion comment with evidence, "Never mark a ticket Done without fresh evidence", matches verification-before-completion and the finish stage.
  - **Flow-back:** a completion comment must list "any change from the spec, and that the spec was updated in the same change". **This is R8, already written down, and Superpowers has no equivalent.**
- **Conflicts:**
  - Its trigger is "every stop point … ending a turn that changed something". In a no-stops build (R5) that means after each task or wave, not every turn.
  - "Get a yes before you create more than two tickets" is a stop. Under AFK it becomes a decision-log entry, or it's deferred until Saad returns, since it leaves the machine (`afk`'s "anything leaving the machine" rule). Decide which.
  - The tracker isn't always present, so all hooks into it must be no-ops when the repo has no tracker.
- **Plug-in points:**
  - after the **spec stop**: an approval comment on the parent;
  - after the **plan stop**: offer to split the plan into tickets, with task Interfaces becoming blocks and blocked-by links and the plan's to-do list mapping to tickets;
  - **during the build**: a progress comment at real stop points (the four stops, a context compaction);
  - at **finish**: a completion comment with evidence and spec changes, plus the stand-up line.

### 7.7 Summary of the plug-in points in the new flow

| Stage | Plug-ins |
|---|---|
| Brainstorm | `ui-mockup` (visual variations), `cross-model` research mode, parallel research agents |
| Spec | builder check (+ optional `cross-model`), `afk` (skips the stop and logs the Theirs pile), `ticket-update` (approval comment) |
| Plan | `cross-model` (optional), `afk` (skips the stop), `ticket-update` (split into tickets) |
| Build | `afk` (rulings), `systematic-debugging`, `cross-model` (after 2 failed fixes), `ticket-update` (progress at real stops) |
| Review/verify | task reviewer, `ux-audit` (UI work), final reviewer (+ optional `cross-model`), triage rules |
| Finish | the one verification run, spec and plan sync check, `ticket-update` completion + stand-up, the R22 commit/push policy, the `afk` finish report |

---

## 8. License and credit

- **License:** MIT. "Copyright (c) 2025 Jesse Vincent". `.claude-plugin/plugin.json` says `"license": "MIT"`. The MIT condition is: "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."
- **What that means for Anvil:**
  - Ship the full Superpowers MIT notice with Anvil, for example `plugins/anvil/LICENSE-superpowers` or a `NOTICE` section, because copied hook scripts, prompt templates, reviewer prompts, helper scripts and adapted skill text are "substantial portions".
  - Credit Superpowers 7.0.2 (`github.com/obra/superpowers`) in the Anvil README, listing which files are adapted.
  - Add a one-line header to each copied or adapted file ("Adapted from Superpowers 7.0.2 by Jesse Vincent, MIT; see LICENSE-superpowers"). That makes later diffs against upstream easy.
  - Anvil's own license is Saad's choice. MIT permits relicensing the combined work, as long as the Superpowers notice stays.
- **Don't copy:**
  - the Prime Radiant / Superpowers logos in `assets/`;
  - the companion's brand-image telemetry (`server.cjs` line 106, `primeradiant.com/brand/...png?v=<version>`);
  - the "Superpowers" name in anything user-facing, so Anvil doesn't present itself as Superpowers (R20 distinct names);
  - `AGENTS.md`'s contributor rules (they're for PRs upstream).
- **Upstream etiquette:** the Superpowers AGENTS.md says the maintainers "don't generally accept contributions of new skills" and reject agent-written PRs. Anvil is a fork of the ideas, not a contribution, so this is no constraint, but don't open upstream PRs from Anvil work without Saad.
