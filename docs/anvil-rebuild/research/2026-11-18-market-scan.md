# Market scan: Anthropic's plugins, Anthropic people, Matt Pocock, and the rest of the field

- **Date:** 2026-11-18
- **Question:** is Superpowers falling behind, and is there something faster or better for Saad's brainstorm → spec → plan → parallel build → review → finish flow?
- **Fills gaps left by:** [community-frameworks](2026-11-18-community-frameworks.md), [practitioner-sentiment](2026-11-18-practitioner-sentiment.md), [anthropic-guidance](2026-11-18-anthropic-guidance.md). Requirements: [brainstorm notes §9](../2026-11-18-brainstorm-notes.md).
- **Method:**
  - `gh api` on the repos, commit histories and marketplace manifests.
  - The local official-marketplace clone at `~/.claude/plugins/marketplaces/claude-plugins-official/`, synced 2026-11-18 09:00 UTC.
  - This machine's `installed_plugins.json`, `known_marketplaces.json`, settings files and `claude plugin` CLI. Claude Code here is **2.1.268**.
  - The official docs on code.claude.com, fetched 2026-11-18.
  - Web search for affiliations, posts and benchmarks.

**How to read this.** Plain statements are **facts**, each tied to a dated source. Lines starting **Inference:** are my reading of those facts. **Thin:** marks weak evidence. Star counts come from the GitHub API on 2026-11-18.

---

## 1. Anthropic's own development plugins

### 1.1 Where they live now (facts)

- **They moved.** On 2026-10-26, `anthropics/claude-code/plugins/` was reduced to a README. It says: "Anthropic's plugins are developed in claude-plugins-official." The old `claude-code-plugins` marketplace still lists them, but installs them from there.
- **Explicit versions.** Also on 2026-10-26, commit `30202c7` gave ten plugins explicit versions. Its message: "Without a version, every commit to this repository counts as a new version of a plugin, so users get no-op updates … From now on, a change to these plugins reaches existing installs only when its version is bumped."
- **Size.** `anthropics/claude-plugins-official` (47,611 stars, pushed 2026-11-18) lists **317 plugins**. 43 are first-party, under `plugins/`. The rest are third-party, pinned by git SHA. Superpowers and `mattpocock-skills` are both third-party entries there.
- **`anthropics/skills` has no development-workflow skill.** It has 196,968 stars and was pushed 2026-11-16. Its skills are Office files, art, mcp-builder, skill-creator, webapp-testing and similar.

### 1.2 Plugin by plugin

The original author is the first committer of the plugin in `anthropics/claude-code`, from git history. **Inference:** committers to that repo are Anthropic staff. I did not verify that separately, except for David Dworken, whose `plugin.json` gives an `@anthropic.com` email.

| Plugin (version) | Original author · first commit · last content change | Flow and key prompt ideas | Parallel agents | Review approach | Speed and cost (facts; there are no measurements) |
|---|---|---|---|---|---|
| **feature-dev** (1.0.1) | Sid Bidasaria · 2025-10-09 · content essentially unchanged since 2025. Only 5 commits; the 2026-10-26 change was the version stamp. | 7 phases: discovery → exploration → **clarifying questions ("CRITICAL … DO NOT SKIP")** → architecture → implementation ("DO NOT START WITHOUT USER APPROVAL") → quality review → summary. If the user says "whatever you think is best", it gives a recommendation and still asks for explicit confirmation. | 2–3 `code-explorer`, then 2–3 `code-architect` in **three framings: minimal changes, clean architecture, pragmatic balance**, then 3 `code-reviewer`. All on `model: sonnet`. **Implementation is single-threaded in the main agent.** | 3 parallel reviewers (simplicity/DRY, bugs, conventions). The reviewer reports only issues it rates **≥80 on a 0–100 confidence scale**. The user then chooses "fix now, fix later, or proceed". | About 7–9 subagents and **4 user stops** (questions, architecture choice, approval, review triage). |
| **code-review** (1.0.1) | Wanghong Yuan · 2025-10-24 | PR review: (1) a Haiku gate (closed, draft, trivial, already reviewed); (2) Haiku lists the CLAUDE.md files; (3) Sonnet summarises the PR; (4) **4 parallel reviewers**; (5) **one validator subagent per flagged issue**; (6) unvalidated issues are dropped. A "Do NOT flag" list covers pre-existing issues, linter-catchable issues and nitpicks. | 4 reviewers: 2 Sonnet on CLAUDE.md compliance, 2 Opus on bugs. Then N validators: Opus for bugs, Sonnet for rules. | "Find, then validate each finding" is the core idea. "False positives erode trust." | Roughly 8 + N agents per PR. Models are mixed to keep cost down. |
| **pr-review-toolkit** (1.0.1) | Ashwin Bhat · 2025-10-09 | `/review-pr [aspects]` picks agents by what changed. | 6 specialists: code-reviewer, code-simplifier, comment-analyzer, pr-test-analyzer, **silent-failure-hunter**, type-design-analyzer. **Sequential by default, parallel only when asked** ("all parallel"). | Results are aggregated as Critical / Important / Suggestions / Strengths. | Up to 6 agents. |
| **code-simplifier** (1.0.0) | **Boris Cherny** · 2026-01-09 · unchanged since 2026-02-20 | One `model: opus` agent. "Preserve Functionality", "Choose clarity over brevity", no nested ternaries, refine only recently touched code. | None | Not a reviewer. It edits. | 1 Opus agent. **Superseded** by the bundled `/simplify` (§4.3). |
| **ralph-loop** (1.0.1) | Daisy Hollman · 2025-11-16 as `ralph-wiggum` · renamed 2026-01-06 "per legal guidance" | A Stop hook blocks exit and feeds the same prompt back until `--completion-promise` appears or `--max-iterations` is hit. A state file `.claude/ralph-loop.local.md` is scoped to one session. | None | Self-review through test output | **Unbounded by default** (max-iterations defaults to unlimited). **Inference:** native `/goal` (§4.3) now covers this. |
| **commit-commands** (1.0.1) | Ashwin Bhat · 2025-10-09 | `/commit`, `/commit-push-pr`, `/clean_gone`. It injects `git status` and `git diff HEAD`, then: "You MUST do all of the above in a single message." | None | None | One turn |
| **hookify** (0.1.1) | Daisy Hollman · 2025-11-17 | Turns "don't do X" into regex rules in `.claude/hookify.*.local.md`, enforced by Python hooks on PreToolUse, PostToolUse, Stop and UserPromptSubmit. A `conversation-analyzer` agent mines past turns for unwanted behaviour. | None | None | Python on every tool call |
| **plugin-dev** (0.1.2) | Daisy Hollman · 2025-11-17 · last change 2026-11-10 | 7 skills (agents, commands, hooks, MCP, structure…), a `plugin-validator` agent and a `skill-reviewer` agent | None | None | n/a |
| **security-guidance** (2.0.20) | **David Dworken (dworken@anthropic.com)** · 2025-10-09 · **changed 2026-11-18**, the most active of these | Three layers: (1) regex warnings on Edit/Write for about 25 patterns; (2) an **LLM diff review on Stop**, newest Opus by default, with high-severity findings fed back before the user sees the reply; (3) an **agentic commit/push reviewer** that traces data flow across files. | Background LLM calls | Review gates at **turn end and at commit, not per step**. Up to 20 commit reviews per hour by default. | One LLM call per turn, plus one agentic review per commit |
| **frontend-design** (1.1.1) | **Thariq Shihipar** · 2025-11-12 | A design-direction skill ("distinctive, intentional", avoid templated defaults) | None | None | n/a |
| **claude-security** (0.12.0) and **code-modernization** (1.0.0) | Both 2026-09-25 | claude-security: a vulnerability scan where "every finding [is] challenged before it is reported and the verification tally computed in code". It writes patches, and **a panel of agents** verifies each one. code-modernization: assess → map → business rules → approved plan → rewrite, "with independent proof that the new code behaves like the old". | Agent panels | Adversarial verification, with the tally done in code | Heavy by design |
| `session-report`, `receipts`, `project-artifact`, `claude-md-management`, `claude-code-setup`, `playground`, `champion-kit` | 2026 | Usage reports, CLAUDE.md upkeep, automation recommender, HTML playgrounds | n/a | n/a | n/a |

### 1.3 What it adds up to

- **Fact:** none of Anthropic's plugins writes a spec file, keeps a plan file, tracks progress on disk or builds in parallel.
- **Fact:** feature-dev still tells the model to "Use TodoWrite". Its agents list the `TodoWrite`, `KillShell` and `BashOutput` tools.
- **Fact:** round 1 found that Claude Code 2.1.233 (2026-08-14) removed TodoWrite on current models unless a flag is set ([community-frameworks §2.1](2026-11-18-community-frameworks.md), Superpowers #2177).
- **Inference:** feature-dev is a 2025 artifact that is not maintained for current models.
- **Fact:** Anthropic's active development energy has gone into **bundled skills** instead: `/code-review`, `/simplify`, `/verify`, `/batch`, workflows (§4.3).
- **Inference:** the ideas worth taking from the plugins:
  - **architecture variations under fixed framings** (minimal / clean / pragmatic), with a recommendation (feature-dev);
  - **validate every finding with a fresh agent before reporting it** (code-review, claude-security);
  - **gate on turn end and commit, not per step** (security-guidance);
  - a **silent-failure** lens for review (pr-review-toolkit).

---

## 2. Anthropic employees: affiliation checked, and what they published

| Person | Affiliation (verified 2026-11-18) | What they published that matters here |
|---|---|---|
| **Boris Cherny** | **At Anthropic.** He created Claude Code. Quartz (2026-11-16) calls him "head of applications"; older pieces say "Head of Claude Code". | Authored the `code-simplifier` plugin (commit 2026-01-09). Announced `/simplify` and `/batch` (X, 2026-02-27). Tips threads (2026-01-02, 2026-04-16). His **`/go` skill** (test end to end, then `/simplify`, then open a PR) **has never been published**. Only community re-creations exist (howborisusesclaudecode.com). |
| **Cat Wu** | **Left Anthropic.** Her last day was 2026-10-30, announced 2026-11-03. She now leads product management for OpenAI's Core Products team (Business Insider, TNW, OfficeChai 2026-11-05). | No skills or plugins. Interviews only (round 1, S7). |
| **Thariq Shihipar** | **Left Anthropic.** Announced on X 2026-10-24 ("I've left Anthropic after more than a year of working on Claude Code"). Joined about 2025-06. | (a) The **"interview me" spec prompt**, X 2025-12-28: "read this @SPEC.md and interview me in detail using the AskUserQuestionTool … continue interviewing me continually until it's complete, then write the spec to the file", followed by a new session to execute it. (b) The `frontend-design` plugin (2025-11-12). (c) "Lessons from building Claude Code: How we use skills" (X 2026-03-17, claude.dev 2026-06-03). (d) **"A Field Guide to Fable: Finding your unknowns"** (X 2026-07-03, Claude blog 2026-07-06). It gives 8 techniques: blind-spot pass, brainstorms and prototypes, interviews, references, plans that lead with the decisions you're most likely to change, a **deviation log (`implementation-notes.md`)**, pitches and explainers, quizzes. (e) The `ThariqS/html-effectiveness` repo (685 stars, 2026-07-03). He has **no skill repo of his own**. |
| **Addy Osmani** | **At Anthropic, Claude Code team, since September 2026.** Announced on X 2026-09-08. His bio says Member of Technical Staff. Before that he spent 14 years at Google. | (a) **`addyosmani/agent-skills`**: 118,803 stars, v0.6.16 (2026-11-14), **created 2026-02-15, before he joined.** It is his personal project, not Anthropic's. (b) Co-author, with Morgan Westlee Lunt and Qing Wang, of **"How the Claude Code team does code review"** (2026-10-15). (c) Author of **"How the Claude Code team thinks about verification"** (claude.dev, 2026-11-16). §2.2 summarises both posts. |
| **Erik Schluntz** | **At Anthropic** (Member of Technical Staff). Co-author of "Building effective agents" (Dec 2024). | "Vibe coding in prod" talk (May 2025): he spends **15–20 minutes exploring and planning before any code**, starts with leaf nodes, and writes minimal end-to-end tests. He has no skill repo. **Thin:** one aggregator calls him "Head of Claude Code"; no other source agrees. |
| **Alex Albert** | **At Anthropic.** He leads Claude Relations; his X bio now reads "Research @AnthropicAI". | Nothing on development workflows. |
| **Andrej Karpathy** | **At Anthropic since 2026-05-19, on the pre-training team** (TechCrunch, VentureBeat). | The popular **"Karpathy skills" CLAUDE.md** (`multica-ai/andrej-karpathy-skills`, 234,129 stars, created 2026-01-27) is **not by Karpathy and not by Anthropic**. Jiayuan wrote it, deriving it from a Karpathy X post. It sets 4 principles: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution. **Inference:** this is probably the "4 rules for simple code" that Saad asked about in §9. Round 2 is testing those claims. |
| Daisy Hollman, Sid Bidasaria, Ashwin Bhat, Wanghong Yuan, David Dworken | Original committers of the official plugins (§1.2). Affiliation is inferred, except Dworken (fact). | See §1.2. |

### 2.1 "Grill me": who wrote it

**Saad's belief is wrong. Round 1 was right.**

- **`grill-me` is Matt Pocock's skill.** He is not and never was an Anthropic employee. He is an independent educator (Total TypeScript, AI Hero) and a former Vercel developer advocate (his X bio; Pragmatic Engineer, 2026-09-17).
- **First commit of grill-me:** 2026-02-25 in `mattpocock/skills`. The text was: "Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one."
- **The Anthropic idea Saad is probably remembering is Thariq's "interview me" prompt** from 2025-12-28, two months earlier. It is the same move: the agent interviews you to build the spec. It used Claude Code's AskUserQuestion tool.
- **Not found:** any statement from Matt Pocock saying he was inspired by Thariq. So I do not claim a lineage.

### 2.2 The two Claude Code team posts (facts)

**Verification post** (2026-11-16):
- "Verification loops are the building block that lets you delegate more work… With them, you can run dozens or hundreds in parallel."
- A **`verify` skill** lives in `.claude/skills/`. "Claude knows to use the verify skill before committing."
- A **3-round cap**, then a human.
- A diff-triggered reliability checklist: "checks only the items whose trigger matches – usually 3 to 10".
- "We point each pass at context from earlier rounds and past failures rather than re-checking everything from scratch. It's cheaper and finds more."
- "A passing review on an out-of-date commit means nothing."
- "Changes can't modify their own checks."
- Flaky tests: "Claude can't skip them, add sleeps or retry… it deletes the test and writes down why."
- A **commit gate** with off / observe / enforce modes. Enforce blocks a commit unless the session ran `/code-review` or `/verify`.

**Code-review post** (2026-10-15, summarised by InfoQ 2026-11-15):
- Claude verifies its work before the PR. Then come CI, AI review and a blocking security review. Human approval is **scaled by risk tier**: low needs no human, medium one, high two, CI files always.
- "Review cycles are capped at three rounds before the author is asked to reconsider the implementation."
- PRs passing after one review-and-fix round rose from 65% to 78%. PRs needing 5+ rounds fell from 8.9% to 1.5%. Reverts fell by more than 40%.

**Inference:** these two posts are the strongest public support for §9's rule that "a test result stays valid until the code changes":
- re-verify only the current commit;
- build on earlier rounds rather than rechecking everything;
- cap rounds at 3;
- one primary reviewer, not stacked reviewers;
- heavy tests once, before commit.

---

## 3. Matt Pocock's skills in depth

- **Repo:** `mattpocock/skills`, **327,096 stars, more than Superpowers' 319,661.**
- **Activity:** created 2026-02-03, pushed 2026-11-18 (near-daily). v1.3.2 released 2026-10-29.
- **License and install:** MIT. It is also listed in the official marketplace as `mattpocock-skills`, but **pinned to `49dd158`** (bumped 2026-10-16). So marketplace users run a copy about a month behind the repo.
- **Stated philosophy (README):** "Approaches like GSD, BMAD, and Spec-Kit try to help by owning the process. But while doing so, they take away your control… These skills are designed to be small, easy to adapt, and composable."

### 3.1 The flow

| Step | Skill | Mechanics (facts, from the SKILL.md files read 2026-11-18) |
|---|---|---|
| Route | `ask-matt` | A router across the skills. It reads a skill's SKILL.md before recommending it (1.3.2). Its `PHASE-BOUNDARIES.md` gives an ordered decision at each phase boundary: **Continue → `/clear` → `/handoff` → subagent → `/compact`**. "Grilling → implementation is the standard yes" for Continue, because "the implementation wants the reasoning verbatim, not a summary". |
| Align | `grill-me` / `grill-with-docs` → `grilling` | See §3.2. `grill-with-docs` adds `domain-modeling`: it writes `GLOSSARY.md` and ADRs as it goes. |
| Spec | `to-spec` (earlier name `to-prd`) | "Do NOT interview the user; just synthesize what you already know." It sketches **test seams** ("the highest seam possible… the ideal number is one") and checks them with the user. Template: Problem, Solution, **a LONG numbered list of user stories**, Implementation Decisions (**no file paths or code**, unless a prototype snippet encodes a decision), Testing Decisions, Out of Scope. The spec is **published to the issue tracker** with the label `ready-for-agent`. |
| Split | `to-tickets` (earlier name `to-issues`) | **Tracer-bullet vertical slices**: each one "cuts a narrow but COMPLETE path through every layer", "is demoable or verifiable on its own" and is "sized to fit in a single fresh context window". **Each ticket declares its blocking edges.** Wide refactors run as **expand → migrate in batches → contract**. It quizzes the user on granularity and edges, then publishes one ticket per file (`.scratch/<slug>/issues/NN-*.md`) or as native tracker issues. |
| Build (one ticket) | `implement` | Uses `tdd` "where possible, at pre-agreed seams". "Run typechecking regularly, single test files regularly, and **the full test suite once at the end**." Then `code-review`, then commit. |
| Build (parallel) | **`implement-spec`** (graduated in v1.3.0, 2026-10-04) | Tickets form a **task graph**, and the ready **frontier** is picked up. A **fresh implementer subagent per ticket, each in its own worktree and branch**, runs in the background "for maximum concurrency". A **merger subagent** lands each result on one **integration branch**, and the frontier is recomputed after every merge. Communication goes through "context pointers" (spec, tickets, notes, commits), not copied text. One `code-review` runs at the end, and **one fresh implementer fixes all its findings.** |
| Test | `tdd` | "**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user." Each proposed seam gets a note on what it catches and what it misses (1.3.2). Anti-patterns: implementation-coupled, **tautological**, **horizontal slicing**. "Refactoring is not part of the loop." |
| Review | `code-review` | **Two axes run as parallel fresh-context subagents:** Standards (documented repo rules plus a fixed **Fowler smell baseline**, always labelled a judgement call) and **Spec** (missing or partial, **scope creep**, implemented wrongly, each with the spec line quoted). Under 400 words each. "Do **not** merge or rerank findings." |
| After | `retro`, `pr`, `diagnosing-bugs`, `prototype`, `wayfinder`, `handoff`, `wait-what` | `retro` turns a session's misses into environment fixes (lint rule, hook, CI job, standards). `pr` writes the body with the smallest clarifying visual, before/after evidence and a merge-danger call. `wayfinder` handles efforts too big for one session. `wait-what` asks for "re-pitch that… in Simplified Technical English". |

The repo also keeps `.out-of-scope/` files that record **rejected** requests and why. Examples: no question cap, no AskUserQuestion, no recursion guards ("the harness should be responsible").

### 3.2 The exact mechanics of grilling

The current file is `skills/productivity/grilling/SKILL.md`, last changed 2026-10-29. `grill-me` itself is a 157-byte, user-invoked wrapper (`disable-model-invocation: true`): "Call the Skill tool with 'grilling'."

1. **It maps a design tree.** "Every decision branches into the decisions that hang off it."
2. **It asks in rounds.** "The **frontier** is every decision whose prerequisites are already settled… Ask the whole frontier in one round: number each question and give your recommended answer. Then wait."
3. **It uses a fixed format.** `❓ **Q1** - **<title>**: <body, may include choices>` then `➡️ <recommended answer>`, with a `---` between questions.
4. **"Word each question so 'yes' accepts your recommended answer."** Added 2026-10-07 (#706).
5. **Dependent questions wait.** "A question whose answer depends on another question still open in this round belongs to a *later* round."
6. **"Finding *facts* is your job, never the user's."** It dispatches a fresh-context subagent to look things up, without blocking: only the questions downstream of that lookup wait. "The *decisions* are the user's."
7. **It finishes when the frontier is empty.** "Every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms."

**How it evolved, from git history:**
- 2026-02-25: two sentences, "one-by-one".
- 2026-03-19: a recommended answer added.
- 2026-03-26: "one at a time".
- 2026-07-31: **round-by-round frontier**, so questions are batched.
- 2026-10-07: wording so that "yes" accepts.

**Usage guidance** (`docs/productivity/grill-me.md`):
- "Count rounds, not questions. Forty-six questions across four rounds is an ordinary session."
- The failure mode is **passivity** ("agreed, agreed, agreed" for 40 questions).
- **Ungrillable** questions ("how should this interaction feel?") mean stop and build a `prototype`.
- "Leave plan mode off. Plan mode makes the agent hurry."
- Don't start a fresh session before `to-spec`: "The value of the session is the context you just built."

### 3.3 Why people like it

**Facts:**
- Matt calls `grill-me` and `grill-with-docs` "my most popular skills".
- One marketplace counts about 1.5–1.6M skills.sh installs.
- Addy Osmani's comparison (in his own repo, 2026) calls grilling "the reference implementation" for requirements and "genuinely excellent".

**Inference, from the mechanics above:**
- it is tiny and works in any harness;
- it never asks what the code can answer;
- the recommendation makes "yes" cheap;
- rounds keep the count of stops low even when the count of questions is high;
- the user stays the owner of scope.

### 3.4 What Anvil can take, mapped to Saad's complaints

| Saad's complaint ([brainstorm notes §2](../2026-11-18-brainstorm-notes.md)) | Grilling mechanic | Inference: how Anvil uses it |
|---|---|---|
| Too many questions, too many stops | The whole frontier in one round; numbered; recommended answers | Brainstorm asks in **rounds**, not one at a time. Most rounds become a single "yes to all, except Q3" reply. |
| "Design questions are a wasted stop: I said yes to nearly all of them" | Wording where "yes" accepts the recommendation | **Accepted recommendations go straight into the spec as decisions**, each with call, reason and alternatives. Saad reviews them there, where he says he really reviews. |
| Questions skipped silently | "Nothing left silently assumed"; frontier empty = done | The brainstorm ends only when every branch is either answered or written into the spec as an **assumption**. |
| Wants 2–3 variations, not an interrogation | "Ungrillable → prototype" | Questions that can't be answered by talking ("how should it feel?") route to the **variations/mocks loop** (notes §8) instead of to more questions. |
| Spec and plan must be designed for parallel work (§9) | `to-tickets` blocking edges, vertical slices sized to a fresh context, expand–contract | The plan's task list **is a dependency graph with declared blockers**. Parallel waves come from the frontier. |
| 3–4 isolated parallel builders | `implement-spec`: worktree per ticket, merger agent, integration branch | Close to what §9 wants. **Missing from Matt:** a cap on concurrency, a per-task spec review, and a shared-contract step (see CE in §4.2 and Superpowers #2599 in round 1). |
| Slow, repeated test runs | `implement`: full suite once at the end; `tdd` at agreed seams only | Matches the §9 proposal. Matt does not cache results by git tree; Anvil would add that. |
| Reviews disagree because the plan and the code disagree | Two-axis review that quotes **spec lines** for every finding | Anvil's per-task review quotes S-lines. Keep Standards and Spec findings separate. |

**Where Matt's design conflicts with Saad's:**
- Grilling has **no cap** and is deliberately stop-and-wait. Saad wants fewer stops.
- `tdd` is red-first at every seam. Saad demoted TDD.
- Specs and tickets go to an issue tracker. Anvil has `ticket-update` for that.

**Inference:** take the round-and-frontier mechanics and the graph-shaped tickets, not the TDD stance.

---

## 4. Other notable alternatives

### 4.1 OpenSpec

Round 1 covers it ([community-frameworks §2.3](2026-11-18-community-frameworks.md)). Nothing new found. v2.1.0 shipped 2026-11-17.

### 4.2 Every's Compound Engineering: new depth on parallel builds

Round 1 had the loop and the plan shape. The new finding is in **`skills/ce-work/references/execution-strategy.md`** (read 2026-11-18; repo at 26,143 stars, v3.38.2 on 2026-11-18). It is the most worked-out public answer to "how do we run 3–4 builders safely":

- **Parallel is the default.** "Run each dependency layer's independent units together as a parallel wave of fresh workers. This is the default… a wave spends more tokens than inline work in exchange for finishing sooner, and that is the intended trade." Run serially only where the dependency graph demands it. "Blanket caution never justifies it."
- **A Parallel Safety Check before each wave:**
  - dependencies must already be committed;
  - "File overlap is necessary but not sufficient". Shared types, migrations, lockfiles, generated clients, config and schema files, and environment singletons (one dev server or port, a shared database) also count as contention;
  - estimate merge cost first;
  - "Resolve uncertainty by inspection, not by default";
  - **cap concurrency at about 3–5 workers**;
  - **weigh the cold-start cost**: a unit too small to pay for its own context ramp-up gets batched with others or done inline;
  - abort criteria.
- **Workers are isolated** in harness worktrees, given the intended base commit SHA, and must check `HEAD` matches before editing. Or they share the workspace under a strict wave contract.
- **The orchestrator owns verification and commits.** "Workers run no mutating verification (full suites, installs…)… The authoritative run happens after the wave on the integrated tree." Workers may run one focused test of their own unit.
- "**Inspect the actual tree, not reported paths**". Integrate and commit **one unit at a time in dependency order**, re-checking each remaining result against the advancing base.
- Workers get a **bounded unit packet**: goal, definition of done, the unit's section, cited requirement IDs. Never "read the whole plan". The user's own limits are passed on in the user's words.
- Workers report: files changed, verification evidence, and "whatever did not go as briefed".

**Inference:** this is very close to §9's "3–4 isolated agents, roughly 3–4× faster, verify once". It also encodes the *consequences* of parallelising that §9 asks Anvil to weigh first:
- cold-start cost;
- hidden shared surfaces;
- serial integration;
- a single authoritative test run.

### 4.3 Claude Code's native features that replace plugin workflows

Facts are from code.claude.com, read 2026-11-18. Version notes are where the docs give them. This machine runs 2.1.268, which is older than several of these.

| Feature | What it does | Replaces |
|---|---|---|
| **Plan mode / `/plan`** | Enter plan mode with a task. bcherny (round 1): "all plan mode does is add a little reminder". **`/ultraplan` is removed**: "Use plan mode instead." | Light planning |
| **`/simplify`** | "Four review agents run in parallel, covering reuse of existing helpers, simplification, efficiency, and whether the change is at the right level of abstraction." It applies the fixes. It doesn't look for bugs. | `code-simplifier` plugin, CE `ce-simplify-code` |
| **`/code-review [low…max\|ultra] [--fix] [--comment]`** | Bundled. In a terminal it runs as a background forked subagent. `low` reports only high-confidence findings; higher levels widen coverage. `ultra` runs a cloud multi-agent review that verifies each finding. It follows CLAUDE.md, not REVIEW.md. It was named `/simplify` before v2.1.147. | `code-review` and `pr-review-toolkit` plugins for local use |
| **`/verify`** | "Confirm a code change does what it should by building your project's app, running it, and observing the result, rather than relying on tests." | Boris's unpublished `/go` (partly) |
| **`/batch <instruction>`** | Researches the change, splits it into **5–30 independent units**, presents a plan for approval, then runs **one background subagent per unit in an isolated worktree**. Each implements its unit, runs tests and opens a PR. | A hand-rolled fan-out for **mechanical** changes |
| **`/goal <condition>`** | Keeps working across turns until the condition is met or judged impossible | `ralph-loop` |
| **Dynamic workflows / `ultracode`** | Claude writes a JS script (`agent()`, `pipeline()`, `parallel()`, `phase()`) that the runtime runs in the background. **Up to 16 concurrent agents**, 1,000 per run. Resumable within the session. A **"Large workflow" warning above 25 agents or 1.5M projected tokens**. Default size guideline `medium` (under 10 agents), `small` on Pro. `/deep-research` is the bundled example. Scripts can be saved to `.claude/workflows/` or **shipped in a plugin's `workflows/` directory**. "No mid-run user input." | Orchestration skills that fan out work |
| **Agent teams** | **Experimental, off by default** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). A lead plus teammates, with a shared task list and messaging. "Start with 3-5 teammates." **"Agent teams don't isolate teammates in worktrees"**, so partition files by hand. No resumption of in-process teammates. Round 1: about 7× tokens in plan mode. | Lead-and-worker builds |
| **Agent view, `/fork`, `/subtask`** | Background sessions in their own worktrees, and forked subagents | Manual parallel sessions |
| **Subagent `isolation: worktree`** | Each subagent gets its own checkout | The worktree step in Superpowers |

**Inference:**
- For a **mechanical** wide change, `/batch` already does what Anvil's parallel build would.
- For **feature** work, none of the native features holds a spec, a plan, per-task spec review or a progress file. That is the room Anvil fills.
- Anvil should **call** `/simplify`, `/code-review`, `/verify` and worktree isolation rather than re-implement them.
- A saved workflow is a possible engine for the parallel build stage. A plugin can ship one.

### 4.4 Trending in October–November 2026

- **Anthropic's own posts** on verification (2026-11-16), code review (2026-10-15) and multi-agent teams with Fable 5.2 (2026-11-09, not read in full).
- **Matt Pocock:**
  - `implement-spec` went parallel (2026-10-04);
  - a "Software Factories for Real Engineers" course started 2026-11-09;
  - an in-progress `software-factory` skill: runs triggered by ticket and PR changes, and "a run never waits for a human".
- **Addy Osmani's agent-skills** 0.6.14–0.6.16 (2026-10-29 to 2026-11-14).
- **`t3dotgg/tstack`** (Theo Browne, not Anthropic), created 2026-10-24, 4,143 stars, "the agent skills I use every day". **Not inspected.**
- **Departures from Anthropic:** Thariq (2026-10-24) and Cat Wu (2026-10-30).
- **Superpowers:** no release since v7.0.2 (2026-11-03). The parallel path #2599 is still open (last updated 2026-11-02).

### 4.5 Speed comparisons

**Thin: there is no public benchmark of parallel feature builds across frameworks.**

| Source (date) | Setup | Result | Caveat |
|---|---|---|---|
| felipefontoura.com (run 2026-10-13) | One 24-line ledger feature, claude-opus-5-5, n=1 | Superpowers 7.0.0: 40 s, $0.33. BMAD: 217 s, $1.89. OpenSpec: 277 s, $2.16. Spec Kit: 473 s, $2.84. | Superpowers was fast because brainstorming never ran. `petruseugene/full-development-cycle` #12 (2026-10-23) says the run **cannot be reproduced**: fixture and checklist unpublished, checklist written after two of the runs. |
| Chase AI (about 2026-04) | One app, three ways | Plain Claude Code: 20 min, 200K tokens. Superpowers: 60 min, 250K. GSD: 105 min, 1.2M. Quality about equal. | Secondary summary. Superpowers was pre-v6. |
| Om Mishra, cited in agent-skills `docs/comparison.md` (2026, exact date unknown) | Same model, repo and prompt | agent-skills reached code in about 8 min, Superpowers in about 12. 7 vs 5 validation passes. Tokens about equal. | One developer, one task |
| MindStudio (about 2026-05) | 12 sessions | Superpowers 9% cheaper and 14% fewer tokens than baseline | Secondary. Contradicts Chase AI. |
| Always-on context cost (search summaries, 2026) | Per-session load | Superpowers about 838 tokens; GSD Core about 10,700; ECC about 41,515. One analysis: Superpowers adds about 6,230 characters per session against Matt's 2,464. | Secondary |
| @GoSailGlobal on X (2026-04) | Startup | Matt: 3.8 s, 2,580 tokens. Superpowers: 8.7 s, 4,820 tokens. | Unverified |

**Inference:**
- On small sequential tasks, Superpowers is near plain Claude Code and far cheaper than the spec-heavy tools.
- Its slowness on real work comes from **serial execution** and per-task review rounds, not from its prompts.
- No measured evidence yet shows that Matt's or CE's parallel paths are 3–4× faster in practice. Anvil should measure that itself, for example with `claude plugin eval`.

---

## 5. Plugin update mechanics (official docs, read 2026-11-18)

### 5.1 Facts from the docs

- **Defaults** ([install: Keep plugins updated](https://code.claude.com/docs/en/plugins/install.md); [loading: Which marketplaces auto-update](https://code.claude.com/docs/en/plugins/loading.md)):
  - **On by default:** `claude-plugins-official` and the other official marketplace names (except `knowledge-work-plugins` and `first-party-plugins`), plus marketplaces added from claude.ai.
  - **Off by default:** "every other marketplace, including the community marketplace, third-party marketplaces, and local development marketplaces."
- **The `autoUpdate` setting** ([settings-reference: extraKnownMarketplaces](https://code.claude.com/docs/en/settings-reference)). It is a Boolean on an `extraKnownMarketplaces` entry: "Set `"autoUpdate": true` alongside `source`…" The order of precedence is:
  1. the settings entry;
  2. `known_marketplaces.json`, which the `/plugin` → Marketplaces → **Enable auto-update** toggle writes;
  3. the default.

  `marketplace.json` itself has **no field** to turn it on ([host-marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md)).
- **When it runs:** "after you send your first message, Claude Code waits a random delay of up to ten minutes". Then it refreshes the marketplaces that have auto-update on and updates plugins on disk. "The running session keeps the versions it loaded." The next launch, or `/reload-plugins`, picks them up.
  - `DISABLE_UPDATES`, `DISABLE_AUTOUPDATER` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` turns the pass off, unless `FORCE_AUTOUPDATE_PLUGINS=1` is set.
  - Plugins whose entry has a `headersHelper` are skipped.
- **How the version is computed** ([loading: How Claude Code computes the version](https://code.claude.com/docs/en/plugins/loading.md)):
  1. `plugin.json` `version`;
  2. else the marketplace entry's `version`;
  3. else, by source type: the commit SHA (12 characters) for `github`/`url`/`git-subdir`, and **"the commit SHA of the installed directory" for a relative path inside a git-hosted marketplace**.

  "A manifest that pins `"version": "1.0.0"` keeps every user on the cached copy until its author changes the string, however many commits they push." Don't set `version` in both places; if you do, `plugin.json` wins silently.
- **Pinning a plugin** ([host-marketplace: Hold users on one version](https://code.claude.com/docs/en/plugins/host-marketplace.md)): `ref` and `sha` on the entry. `#<ref>` on `marketplace add`. `<plugin>--v<version>` tags for dependency ranges.
- **Manual update:**
  - `/plugin` → Installed → **Update now**, or `claude plugin update <plugin>@<mkt>`.
  - Marketplaces tab → **Update marketplace** updates everything from one marketplace.
  - `claude plugin marketplace update` with no name refreshes listings only, not installed plugins.
  - "There's no command that updates every plugin at once."
  - **Local CLI help (2.1.268):** `claude plugin update` takes `-s, --scope <user|project|local|managed>`, "default: user".
- **Scopes** ([install: Choose an install scope](https://code.claude.com/docs/en/plugins/install.md)):
  - user → `~/.claude/settings.json`;
  - project → `.claude/settings.json`. Committing it "doesn't download it to their machines"; each collaborator runs `claude plugin install … --scope project` once per clone;
  - local → `.claude/settings.local.json`;
  - precedence: local over project over user.
- **On disk** ([loading: Find plugins on disk](https://code.claude.com/docs/en/plugins/loading.md)):
  - the cache is at `cache/<marketplace>/<plugin>/<version>/`;
  - an update leaves `.orphaned_at` in the old directory, which is deleted 14 days later;
  - `known_marketplaces.json` is per user, shared by every project.
- **Private repos and the second machine** ([host-marketplace: credentials](https://code.claude.com/docs/en/plugins/host-marketplace.md)):
  - git runs with prompts off;
  - GitHub `owner/repo` probes SSH first and falls back to HTTPS;
  - **"Installs from `/plugin` inside a session and plugin updates don't fall back"**, so a machine with no GitHub SSH key needs `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`;
  - a `GITHUB_TOKEN` alone does nothing; it works through a credential helper (`gh auth setup-git`).
- **Two plugins with the same manifest name** from different marketplaces "both appear as enabled… but the hooks of one of them are left out" ([loading: Hooks when two enabled plugins share a name](https://code.claude.com/docs/en/plugins/loading.md)).

### 5.2 What the official marketplace does to third-party plugins (facts from git)

- **It pins every third-party plugin to a git SHA** and bumps the pins by hand.
- **Superpowers pins:**
  - `bb92a777` (v7.0.0, released 2026-10-10) went in on **2026-10-16**;
  - `22f0b463` (v7.0.2, released 2026-11-03) went in on **2026-11-12**;
  - **v7.0.1 (2026-10-21) was never pinned.**
- **obra's own `superpowers-marketplace`** lists v7.0.2 by URL with no SHA, updated the same day as the release. But it is third-party, so it does **not** auto-update by default.
- **Inference:** "superpowers@claude-plugins-official auto-updates" means it follows **Anthropic's pin**, which here lagged 6–9 days and skipped a release.

### 5.3 This machine (facts, read 2026-11-18)

- **One shared plugin store.** `~/.claude-personal/plugins` is a **directory junction** to `~/.claude/plugins`, set up 2026-10-13. So both profiles share one `installed_plugins.json` and one cache. The 7.0.0 copy physically lives in `~/.claude/plugins/cache/claude-plugins-official/superpowers/7.0.0/`.
- **`superpowers@claude-plugins-official` has two install records:**
  - **user scope:** 7.0.2, SHA `22f0b463`, `lastUpdated` 2026-11-13 05:28 UTC. That is the day after Anthropic's pin bump, so the background auto-update worked;
  - **project scope, `projectPath: C:\Users\MrError`:** 7.0.0, SHA `bb92a777`, `lastUpdated` 2026-10-30. It was **not** moved to 7.0.2. The 7.0.0 directory has **no `.orphaned_at`**, because this record still points at it.
  - `claude plugin list` shows both as enabled.
- **The project is the home directory.** For a session started in `C:\Users\MrError`, "project settings" is `C:\Users\MrError\.claude\settings.json`, which is the **company profile's user settings file**. **Inference:** this project-scope record came from a personal-profile session (`CLAUDE_CONFIG_DIR=~/.claude-personal`) opened in the home directory, so the project scope and the other profile's user scope collide on one file.
- **The settings hard link is broken.** `~/.claude-personal/README.txt` says `settings.json` is hard-linked between the two profiles. But the two files now have **link count 1 and different contents**: 974 bytes (2026-10-30) against 1,004 bytes (2026-11-11). They have diverged. This is outside this report's scope, but worth fixing.
- **Inference, not documented:** the docs don't say whether background auto-update touches project-scope records. The evidence here suggests it updated only the record for the session it ran in, or only user scope. **Fix:** run `claude plugin update superpowers@claude-plugins-official --scope project` from `C:\Users\MrError`. **Avoid** `uninstall --scope project` there, because it would edit the company profile's user `settings.json`.

### 5.4 What this means for MrErrorSan/mrerror-claude-skills on a second machine

**Facts about the current manifests:**
- It is a third-party git marketplace, so **auto-update is off** on every machine until it is turned on.
- `plugins/anvil/.claude-plugin/plugin.json` pins **`"version": "0.2.0"`**, so **pushed commits do not reach any install until that string changes**.
- Anvil declares `dependencies` on `superpowers@superpowers-marketplace`, while this machine uses `superpowers@claude-plugins-official`.

**Inference, as a recipe:**
1. On each machine, run `claude plugin marketplace add MrErrorSan/mrerror-claude-skills`. Then turn on auto-update, either in `/plugin` → Marketplaces or in `~/.claude/settings.json`:
   ```json
   "extraKnownMarketplaces": { "mrerror-claude-skills": { "source": { "source": "github", "repo": "MrErrorSan/mrerror-claude-skills" }, "autoUpdate": true } }
   ```
   On a machine with no GitHub SSH key, also set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`.
2. Pick one release model:
   - **Omit `version`** from `plugin.json` and the entry. Every pushed commit is then a new version (the commit SHA of the plugin directory). This suits a personal tool on several machines.
   - Or **bump `version` on every push**. Never leave a pinned version unchanged across releases.
3. For the rebuild, **drop the Superpowers `dependencies`**. Otherwise a second copy of `superpowers` can install from another marketplace under the same manifest name, and one copy's hooks silently won't run.
4. Install Anvil at **user scope** on each machine. Project scope needs one install per clone, and §5.3 shows such records can go stale.
5. While developing, `claude plugin marketplace add ./` on a local checkout loads the plugin **in place**, with edits live on `/reload-plugins` and no version bump needed.

---

## 6. Market map

Dates are the last push or release as of 2026-11-18. "Speed" uses only the evidence in §4.5; "n/m" means not measured.

| Tool | Author / affiliation | Stages covered | Parallel build | Speed evidence | Activity / date | What Anvil should borrow |
|---|---|---|---|---|---|---|
| **Superpowers** 7.0.2 | Jesse Vincent (obra) / Prime Radiant. Not Anthropic. Listed in the official marketplace, SHA-pinned. | brainstorm → spec → plan → build (SDD) → review → finish | **No.** "Never dispatch multiple implementation subagents in parallel". The #2599 DAG path is open. | 40 s/$0.33 on a tiny task (brainstorm skipped). 60 vs 20 min in Chase AI. | 319,661 stars. Push and release 2026-11-03. Official pin 2026-11-12. | Builder check; rulings with cost-if-wrong; lean plans; per-task reviewer (already in notes §2) |
| **mattpocock/skills** 1.3.2 | Matt Pocock. **Independent**, ex-Vercel, **not Anthropic**. | grill → spec → tickets → implement / implement-spec → code-review → retro → pr | **Yes** (since 2026-10-04): DAG frontier, worktree per ticket, background implementers, merger agent | n/m for builds. Lightest always-on load (secondary). | **327,096 stars**, pushed 2026-11-18 (daily). Official pin 2026-10-16. | **Grilling rounds and frontier, recommended answers, "yes" accepts**; ungrillable → prototype; tickets with blocking edges; seams agreed up front; two-axis review quoting spec lines; full suite once |
| **Compound Engineering** 3.38.2 | Every (company). Not Anthropic. | brainstorm → plan → work → simplify → review → compound | **Yes, by default**: dependency-layer waves, Safety Check, **3–5 cap**, orchestrator-owned verification | n/m | 26,143 stars. Release 2026-11-18. | **Parallel Safety Check, cold-start rule, workers run no full suites, integrate one unit at a time, check base SHA** |
| **addyosmani/agent-skills** 0.6.16 | Addy Osmani, **Anthropic MTS since Sept 2026** (repo predates that, personal) | spec → plan → build → test → review → simplify → ship | `/build auto` runs a plan; `/ship` runs parallel review personas | About 8 vs 12 min to code against Superpowers (one test) | 118,803 stars. Release 2026-11-14. | Anti-rationalization tables; **routing evals in CI**; "don't run two frameworks as your active router" |
| **feature-dev** 1.0.1 | Anthropic (Sid Bidasaria) | discovery → explore → questions → architecture → implement → review → summary | Explore, architect and review in parallel; **implementation is serial** | 7–9 Sonnet subagents, 4 stops | Content from 2025. Version stamp 2026-10-26. | **Three framed architecture variations with a recommendation**; confidence ≥80 filter |
| **code-review / pr-review-toolkit** 1.0.1 | Anthropic (Wanghong Yuan / Ashwin Bhat) | Review only | 4 reviewers plus per-finding validators / 6 specialists | About 8+N agents | Version stamp 2026-10-26 | **Validate each finding**; false-positive list; silent-failure lens |
| **security-guidance** 2.0.20 | Anthropic (David Dworken) | Guard on edit, stop and commit | Background LLM review | Capped at 20 per hour | **Changed 2026-11-18** | Gate at turn end and commit, not per step |
| **ralph-loop / code-simplifier** | Anthropic (Daisy Hollman / Boris Cherny) | Loop / polish | No | n/m | Stale; superseded by `/goal` and `/simplify` | Nothing new: use the native features |
| **Claude Code native** (`/batch`, `/simplify`, `/code-review`, `/verify`, `/goal`, workflows, agent teams) | Anthropic | Pieces: review, polish, verify, mechanical fan-out, orchestration | **Yes**: `/batch` 5–30 worktree agents; workflows up to 16 concurrent; teams of 3–5 with no worktrees | n/m | Shipping continuously. This machine's 2.1.268 lags. | **Call these, don't rebuild them.** A saved workflow can serve as the parallel engine. |
| **Thariq's field guide** (and interview prompt) | Thariq Shihipar, **ex-Anthropic** (left 2026-10-24) | Brainstorm, plan, build log | n/a | n/a | 2025-12-28 / 2026-07-06 | **Deviation log `implementation-notes.md`**; plans that lead with the decisions most likely to change; blind-spot pass |
| **Claude Code team posts** | Anthropic (Addy Osmani et al.) | Verify and review | "Dozens or hundreds" in parallel, *given* verification | Review: 65 → 78% pass in one round; reverts down more than 40% | 2026-10-15 / 2026-11-16 | Re-verify only the current commit; 3-round cap; one tuned reviewer; checks a change can't edit |
| **Karpathy-skills CLAUDE.md** | Jiayuan (multica-ai). **Not Karpathy, not Anthropic.** | Coding behaviour | n/a | n/a | 234,129 stars. Push 2026-04-20. | Under test in round 2 ("4 rules") |
| **spec-kit / OpenSpec / BMAD / GSD Core / Kiro / cc-sdd / gstack** | See round 1 | See round 1 | `[P]` tags / none / none / waves / waves / batch / none | 473 s, 277 s, 217 s (spec tools) | See round 1 | See round 1 §3 (converge, delta specs, goal-backward verify, staleness by fingerprint) |
| **t3dotgg/tstack** | Theo Browne. Not Anthropic. | Unknown | Unknown | n/m | 4,143 stars, created 2026-10-24 | Watch only; not inspected |

---

## 7. Verdict

### 7.1 Is Superpowers still the leader?

It is **one of several now, and behind on the axis Saad cares about most.**

- **Facts:**
  - Matt Pocock's repo has passed Superpowers in stars: 327K against 320K on 2026-11-18. Addy Osmani's is at 119K.
  - Matt and Every both ship **parallel, worktree-isolated builds today**. Superpowers still forbids parallel implementers, and its parallel design (#2599) is an open issue.
  - Anthropic's native `/batch`, workflows and `/code-review` now cover parallel fan-out and review in the box.
  - Superpowers' brainstorming rebuild drew the backlash round 1 recorded. Matt's grilling is the reference that a neutral comparison holds up (Addy Osmani's), and Addy Osmani now works on Claude Code.
  - Through the official marketplace, Superpowers updates arrive 6–9 days late, and v7.0.1 was skipped.
- **Inference: where Superpowers still leads.**
  - **Unattended, reviewed execution.** The per-task reviewer, rulings, and "only four things stop a run" make it the best "walk away and come back to a reviewed result" pipeline.
  - Its speed problem is **serial execution**, not prompt weight. On small tasks it is as cheap as plain Claude Code.
  - It is "falling behind" on parallelism and brainstorming UX, not on discipline.
- **Is there anything faster? Thin evidence.**
  - Nobody has published a measured parallel-build benchmark.
  - CE's and Matt's designs are *built* for roughly 3–5× fewer wall-clock hours on wide plans.
  - CE itself states the trade: "a wave spends more tokens than inline work in exchange for finishing sooner".

### 7.2 What Anvil should take, and from whom

1. **Brainstorm: grilling rounds** (Matt Pocock). Ask the whole frontier per round, numbered, each with a recommended answer, worded so "yes" accepts. Facts come from subagents and never from Saad. Ungrillable questions go to variations or mocks. Accepted recommendations are written into the spec as decisions.
2. **Architecture variations under fixed framings** (feature-dev): minimal, clean, pragmatic, with a recommendation. They feed the brainstorm's 2–3 variations.
3. **A plan shaped as a dependency graph** (Matt's `to-tickets`). Vertical slices sized to one fresh context, declared blocking edges, expand–contract for wide refactors. This satisfies §9's "design for parallel from the spec stage".
4. **Parallel waves with a safety check** (Compound Engineering):
   - dependency layers, a cap of 3–4 (CE says 3–5; Saad says 3–4);
   - treat hidden shared surfaces as contention;
   - the cold-start rule;
   - workers check their base SHA;
   - **workers run only focused tests, and the orchestrator runs the suite once on the integrated tree**;
   - integrate one unit at a time.

   Add Superpowers #2599's **foundations-first package and contract registry** for the shared surface.
5. **Verification rules** (Claude Code team post, 2026-11-16):
   - a passing check on an out-of-date commit means nothing, which pairs with §9's result-per-git-tree rule;
   - each pass builds on earlier rounds;
   - a 3-round cap, then a human;
   - checks a change can't edit;
   - a project `verify` skill that Anvil calls.
6. **Review** (Matt plus Anthropic's code-review plugin):
   - a per-task review that quotes spec lines, with **Standards and Spec kept separate**;
   - each finding validated by a fresh agent before it reaches Saad;
   - at the finish, call the bundled `/simplify` and `/code-review` rather than writing new reviewers.
7. **A deviation log** (Thariq's field guide): `implementation-notes.md`, written during the build and folded back into the spec and plan. This is the cheapest fix for "changes don't flow back".
8. **Skill hygiene** (Addy Osmani, Matt):
   - routing evals for Anvil's descriptions;
   - user-invoked versus model-invoked split;
   - cross-skill calls written as "Call the Skill tool with X", which Matt found raises the hit rate (#878);
   - **pick one active router**. This supports the brainstorm decision that Anvil replaces Superpowers rather than layering on it.
9. **Distribution** (§5.4): drop the Superpowers dependency, omit or bump `version`, turn on `autoUpdate` for this marketplace on each machine, and install at user scope.

---

## Sources (all read 2026-11-18 unless dated)

**Anthropic plugins and docs**
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official): `.claude-plugin/marketplace.json`, `plugins/*` (local clone synced 2026-11-18), commit `30202c7` (2026-10-26), superpowers pin bumps (2026-10-16, 2026-11-12)
- [anthropics/claude-code `plugins/README.md`](https://github.com/anthropics/claude-code/tree/main/plugins) (2026-10-26), and the history of `plugins/*` there for original authors (2025-10-09 to 2026-01-09)
- [anthropics/skills](https://github.com/anthropics/skills) (pushed 2026-11-16)
- Docs:
  - [Install and manage plugins](https://code.claude.com/docs/en/plugins/install.md) · [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading.md) · [Host and maintain a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md) · [Create a marketplace](https://code.claude.com/docs/en/plugin-marketplaces) · [Settings reference: extraKnownMarketplaces](https://code.claude.com/docs/en/settings-reference)
  - [Run agents in parallel](https://code.claude.com/docs/en/agents.md) · [Dynamic workflows](https://code.claude.com/docs/en/workflows.md) · [Agent teams](https://code.claude.com/docs/en/agent-teams.md) · [Commands](https://code.claude.com/docs/en/commands.md) · [Review locally with /code-review](https://code.claude.com/docs/en/code-review-local.md) · [Code Review costs](https://code.claude.com/docs/en/code-review-costs.md)
- Local: `claude --version` (2.1.268), `claude plugin list`, `claude plugin update --help`, `~/.claude/plugins/installed_plugins.json`, `known_marketplaces.json`, both profiles' `settings.json`, `~/.claude-personal/README.txt`

**Anthropic people**
- Addy Osmani, "How the Claude Code team thinks about verification", [claude.dev](https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/) (2026-11-16)
- "How the Claude Code team does code review" (2026-10-15): [X article](https://x.com/addyosmani/status/2114604912520921136), [InfoQ summary](https://www.infoq.com/news/2026/11/claude-code-review/) (2026-11-15)
- Addy Osmani joins Anthropic: [bio](https://addyosmani.com/bio/), [runtimewire](https://runtimewire.com/article/addy-osmani-joins-anthropic-claude-code-developer-experience) (2026-09)
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), including [docs/comparison.md](https://github.com/addyosmani/agent-skills/blob/main/docs/comparison.md)
- Thariq: [interview prompt on X](https://x.com/trq212/status/2005315279455142243) (2025-12-28) · [Field guide on X](https://x.com/trq212/status/2073100352921215386) (2026-07-03) and its [summary](https://www.genai-playbook.com/articles/finding-your-unknowns-en.html) · [How we use skills](https://claude.dev/blog/lessons-from-building-claude-code-how-we-use-skills/) (2026-06-03) · departure: [OfficeChai](https://officechai.com/ai/thariq-shihipar-anthony-morris-announce-theyre-leaving-anthropic-weeks-before-its-ipo/) (2026-10-24)
- Cat Wu departure: [TNW](https://thenextweb.com/news/cat-wu-claude-code-anthropic-openai-core-products), [Unite.ai](https://www.unite.ai/cat-wu-steps-down-as-claude-code-product-chief-after-two-years/) (2026-11-03 to 05)
- Boris Cherny: [Quartz](https://qz.com/boris-cherny-software-engineering-jobs-disappearing-anthropic-111526) (2026-11-16), [CNN](https://www.cnn.com/2026/11/15/tech/anthropic-claude-code-boris-cherny) (2026-11-15), [howborisusesclaudecode.com](https://howborisusesclaudecode.com/) (community)
- Karpathy: [TechCrunch](https://techcrunch.com/2026/05/19/openai-co-founder-andrej-karpathy-joins-anthropics-pre-training-team/) (2026-05-19); [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)
- Erik Schluntz: [aibriefing.dev talk page](https://aibriefing.dev/library/x-2046415129684922368/), [ericjinks.com write-up](https://ericjinks.com/blog/2025/vibe-coding-in-prod/) (2025). Alex Albert: [ai.engineer](https://ai.engineer/speakers/alex-albert)

**Matt Pocock**
- [mattpocock/skills](https://github.com/mattpocock/skills): README, CHANGELOG (1.3.0 on 2026-10-04, 1.3.2 on 2026-10-29), `skills/productivity/{grill-me,grilling,wait-what}`, `skills/engineering/{to-spec,to-tickets,tdd,code-review,implement,implement-spec,ask-matt}`, `docs/productivity/grill-me.md`, `.out-of-scope/*`, git history of `grill-me/` (2026-02-25 onward) and `grilling/` (2026-06-12 to 2026-10-29)
- Affiliation: [Pragmatic Engineer](https://newsletter.pragmaticengineer.com/p/ai-skills-with-matt-pocock) (2026-09-17), [X profile](https://x.com/mattpocockuk)

**Others**
- [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) `skills/ce-work/references/execution-strategy.md`
- [obra/superpowers](https://github.com/obra/superpowers) (tags v7.0.0–v7.0.2, issue #2599), [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace)
- Benchmarks: [felipefontoura.com](https://felipefontoura.com/articles/spec-driven-development-tools-compared/) (run 2026-10-13); [petruseugene/full-development-cycle #12](https://github.com/petruseugene/full-development-cycle/issues/12) (2026-10-23); [Chase AI](https://chaseai.io/blog/gsd-vs-superpowers-vs-claude-code); [MindStudio](https://www.mindstudio.ai/blog/5-claude-code-skills-cut-token-costs-70-percent-benchmarked); [@GoSailGlobal](https://x.com/GoSailGlobal/status/2049339826877665496) (unverified)
- Comparisons: [umaranis.com](https://umaranis.com/2026/10/25/superpowers-vs-matt-pococks-skills/) (2026-10-25), [dev.to (ikramar)](https://dev.to/ikramar/superpowers-vs-compound-engineering-is-the-vs-even-real-58gc)
- [t3dotgg/tstack](https://github.com/t3dotgg/tstack) (created 2026-10-24)
