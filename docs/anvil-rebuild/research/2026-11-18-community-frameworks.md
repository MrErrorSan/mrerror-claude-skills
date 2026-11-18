# Community workflow frameworks: survey for the Anvil rebuild

- **Date:** 2026-11-18
- **Scope:** open-source frameworks and skill collections for structured agentic development (Claude Code and similar agents), as of late 2026.
- **Feeds:** [brainstorm notes §6.5, research phase](../2026-11-18-brainstorm-notes.md).
- **Method:** GitHub API (`gh api`, `gh search`) for stars, push dates, releases, issues and skill files, all read on 2026-11-18. Web search and fetch for docs, comparison articles and one public benchmark.

**How to read this.** Plain statements are **facts**, and each one comes from a source listed at the end (a repo file, a release note, an issue or a doc page). Lines marked **Inference:** are my reading of those facts. Star counts and dates come from the GitHub API on 2026-11-18 unless the line says otherwise. "Pushed" means the date of the last push to the repo.

The user's problems are labelled like this throughout:

| Tag | Problem |
|---|---|
| **P1** | Plan, spec and code drift apart mid-build |
| **P2** | No live progress tracking |
| **P3** | End-only verification misses "did we build what was asked" |
| **P4** | Test bloat |
| **P5** | Over-engineering |
| **P6** | Too many questions, or decisions made silently |

---

## 1. Comparison table

The table is split in two because it is too wide for one.

### 1a. Health, flow and document shape

| Framework | Stars · pushed · latest release | Trend | Flow stages | Spec / plan shape |
|---|---|---|---|---|
| **obra/superpowers** | 319,650 · 2026-11-03 · v7.0.2 (2026-11-03) | Growing fast, from about 171K in Apr 2026 according to one comparison article. The v7 brainstorm rework got a strong backlash. | brainstorming → worktree → writing-plans → subagent-driven-development or executing-plans → review → finishing | Design doc, plus a plan of "Task N" steps holding signatures, files and test assertions. Full code was dropped in v6.4.2. Interfaces blocks between tasks. |
| **github/spec-kit** | 150,375 · 2026-11-17 · v1.4.2 (2026-11-17) | Growing, from about 91K in Apr 2026. Ships several releases a week. | constitution → specify → (clarify) → plan → tasks → (analyze, checklist) → implement → **converge** (loop) | `spec.md` with user stories P1/P2/P3, `FR-###`, `SC-###` and edge cases. `plan.md`. `tasks.md` with `T###`, `[P]` and `[US1]` tags, and checkpoints. |
| **Fission-AI/OpenSpec** | 75,136 · 2026-11-18 · v2.1.0 (2026-11-17) | Growing. v2.0 (2026-11-11) dropped slash commands for skills. | explore → propose → apply → (verify) → archive | Per-change folder: `proposal.md` (why), delta `specs/` (`ADDED/MODIFIED/REMOVED Requirements` with WHEN/THEN scenarios), `design.md`, `tasks.md`. Archiving merges the deltas into the living `openspec/specs/`. |
| **BMAD-METHOD** | 55,500 · 2026-11-18 · v6.12.4 (2026-10-14). v7 is in preview alpha, ETA mid-Nov 2026. | Active. Being restructured: v7 retires many v6 workflows. | Clarify → Plan → Build and verify → Learn and adjust. `bmad-build` sizes the work *after* investigating it. | Brief/PRD, then initiative, epics, and stories in `tickets.toml`. Each story has a build plan file. Architecture and UX "References" sit beside it. A two-section spec for simple changes (v6.12). |
| **Kiro specs** (AWS, closed-source IDE/CLI) | Issues repo kirodotdev/Kiro: 4,481 · 2026-11-05. Docs page updated 2026-09-25. | Active. Quick Spec arrived in May 2026 (secondary source). | requirements → design → tasks (or design-first), then run tasks | `.kiro/specs/<f>/requirements.md` (EARS: WHEN … THE SYSTEM SHALL), `design.md`, `tasks.md`. Bugfix specs use `bugfix.md` (current, expected and unchanged behavior). |
| **gotalab/cc-sdd** (open Kiro clone) | 3,771 · 2026-10-22 · v3.1.0 (2026-09-23) | Small, steady | discovery → spec-init → requirements → design → tasks → `kiro-impl` → `kiro-validate-impl` | Kiro format, plus a **File Structure Plan** in design.md. Tasks carry `_Boundary:_` and `_Depends:_`. `spec.json` holds per-phase `approved` flags. |
| **GSD → GSD Core** (open-gsd/gsd-core) | Original 64,131, **archived** (last push 2026-05-31). GSD Core 11,660 · 2026-11-18 · v1.21.0 (2026-11-13). | Original abandoned. Its fork, GSD Core, is very active. | discuss → plan → execute (waves) → verify (UAT) → ship | `.planning/`: `ROADMAP.md`, `STATE.md`, per-phase `CONTEXT.md`, `PLAN.md` (XML-ish tasks), `SUMMARY.md`, `VERIFICATION.md`, `UAT.md`. Requirement IDs (`REQ-`). |
| **buildermethods/agent-os** | 5,617 · 2026-10-07 · v3.0.0 (2026-01-20) | Flat. Narrowed itself to standards only. | discover/inject standards → shape-spec (inside Claude plan mode) | `agent-os/product/{mission,roadmap,tech-stack}.md`. Spec folders. Standards with an `index.yml`. |
| **eyaltoledano/claude-task-master** | 28,371 · last commit 2026-04-23 · 0.43.1 (2026-03-31) | **Dormant**. Security bugs from Jun 2026 have no reply. The project points to "Hamster" (commercial). | PRD → parse → tasks.json → next/expand → set-status | `tasks.json` with id, deps, priority, details, `testStrategy` and subtasks. A complexity report. |
| **ruvnet/claude-flow → ruflo** | 82,004 · 2026-11-18 · v3.77.2 (2026-11-17) | Very active, very high release churn, low trust (see §2.9) | "swarms", hive-mind, memory, MCP tools | Not a spec/plan methodology |
| **wshobson/agents** (+ commands) | 42,645 · 2026-11-16. `wshobson/commands` **archived**, superseded. | Active | Catalog: 94 plugins, 202 agents, 185 skills. The `conductor` plugin is context → spec and plan → implement. | Conductor: `product.md`, `tech-stack.md`, `workflow.md`, `tracks/<id>/{spec,plan}.md` |
| **anthropics/skills** + **claude-plugins-official** | 196,962 · 2026-11-16. Official plugins: 47,612 · 2026-11-18. | Growing | `skills` has no dev-workflow skill (docs, art, mcp-builder, skill-creator…). Official plugins: `feature-dev` (7 phases), `ralph-loop`, `code-simplifier`, `pr-review-toolkit`, `project-artifact` | feature-dev: discovery → explore → clarify → architecture → implement → review → summary |
| **garrytan/gstack** (added) | 141,963 · 2026-11-18 | Growing | Think → Plan → Build → Review → Test → Ship → Reflect, with role skills | `/office-hours` design doc, then plan reviews (CEO, eng, design, DX), then `/review`, `/qa`, `/ship` |
| **EveryInc/compound-engineering** (added) | 26,143 · 2026-11-18 · v3.38.2 (2026-11-18) | Growing | brainstorm → plan → work → simplify → review → **compound** (capture learnings) | **One plan artifact** that grows from requirements into an implementation plan. Learnings go in `docs/solutions/`. |
| **affaan-m/ECC** (everything-claude-code, added) | 305,972 · 2026-11-17 | Growing (kitchen sink) | `/plan`, TDD, "instincts", continuous learning | 72 agents, 327 skills, 98 legacy command shims |
| Awesome lists and marketplaces | awesome-claude-code 58,266 (2026-11-18). ComposioHQ/awesome-claude-skills 79,771 (2026-09-18). travisvn/awesome-claude-skills 15,857 (2026-04-28, fading). vercel-labs/skills (`npx skills`) 39,908. | Lists keep growing. Several have gone stale. | n/a | n/a |

### 1b. Mechanics

| Framework | Keeping spec, plan and code in sync on change (P1) | Progress tracking (P2) | Parallel agents / worktrees | Testing stance (P4) | Review and verification (P3) |
|---|---|---|---|---|---|
| **Superpowers** | Weak by design. Mid-build "Rulings" go into a git-ignored ledger. On a clean final review they are copied into the final chat message and the workspace is `rm -rf`'d. The spec and plan are never updated. | `.superpowers/sdd/<plan>/progress.md` ledger. Helper scripts `task-done` and `task-brief`. Todos are "the lossy half". | One implementer at a time ("never dispatch multiple implementation subagents in parallel"). Worktree per plan. A parallel DAG path is proposed in #2599 (2026-10-22), not shipped. | **Mandatory TDD**: deletes code written before its test | One task reviewer per task (spec plus quality, merged in v6.0). Small same-shape tasks are batched (v6.3.0). A broad final review. |
| **spec-kit** | `converge` checks the code against the spec, plan and tasks, and only **appends** tasks. It never edits the spec. Changing requirements has **no core command**: `/speckit.revise` (#4156) and "living spec" extensions (#4944) are still proposals, now stale. Community `reconcile` extension. | Checkboxes in `tasks.md`. Converge treats "completion claims are not evidence". | `[P]` marker for tasks that can run in parallel. A worktree issue (#1476) is closed. | Tests are **optional**, written only if the spec asks for them. When present, they are written first. | `analyze` (cross-artifact consistency), `checklist` ("unit tests for English"), `converge` loop with gap types |
| **OpenSpec** | Best in class for *post-delivery*: delta specs are merged into living specs at archive. Any artifact can be edited at any time, with no gates. Gap: forward-generated artifacts don't propagate back (#783, open). | `tasks.md` per change | Worktree-aware `view`/`list` (#2254, 2026-11-16). No orchestration. | No opinion | `validate --strict` (structure only). `/verify` against the change (since about 2026-04-11). |
| **BMAD v6.12 / v7** | v7: "Learn and adjust" sends changes back to Plan. Out-of-scope goals are split off to `deferred-work.md`. `correct-course` was **retired** in v7. | Ticket tree, with a build plan file per story. Stops at `built`. A human marks it `done`. `sprint-status` was **retired**. | `party-mode` for multi-agent discussion of a draft. One build session per story. | "Done when" per story. Separate Test Architect module. E2E generation skill. | Review depth `none`/`quick`/`thorough`, **default quick**. Thorough uses 4 lenses (diff, edge cases, test gaps, **intent alignment**). `bmad-walkthrough` for human review. |
| **Kiro** | Edit requirements → ask Kiro to update design → **Sync Files** on tasks.md, which creates new tasks mapped to the new requirements and auto-marks finished ones. **Analyze Requirements** checks for ambiguity and conflict. | tasks.md status. Sync re-derives completion from the code. | A dependency graph, with independent tasks run in concurrent waves | Property-based tests for bugfix specs, covering the fix *and* preserved behavior. Optional tasks. | Requirement analysis before design |
| **cc-sdd** | Code is the source of truth. Specs are boundary contracts. `kiro-validate-gap` for brownfield work. | `tasks.md`, plus an `## Implementation Notes` section fed into later implementers. On-disk approvals in `spec.json`. | `kiro-spec-batch` builds specs in dependency waves, with a cross-spec review for contradictions and interface mismatches | TDD RED → GREEN "behind feature flags" | A fresh independent reviewer per task (git diff, TODO grep, tests, **boundary compliance**). Debugger after 2 rejected rounds. `validate-impl` returns GO/NO-GO/MANUAL_VERIFY_REQUIRED. |
| **GSD Core** | Executor "deviation rules" 1–4. Deviations are logged in SUMMARY.md. **VERIFICATION.md goes `stale` automatically** when any covered plan, summary, requirement or implementation file changes (content fingerprint). | `STATE.md`, `ROADMAP.md`, per-plan SUMMARY, `UAT.md` that survives `/clear`. Statusline freshness marker. | Wave-based. Each executor gets a fresh context and an isolated worktree. Parallel reviewer lanes. | Nyquist auditor writes "tests that can fail" for requirement gaps. Implementation files are read-only to it. | **Goal-backward verifier** ("SUMMARY claims are not evidence"). UAT walk-through with the user. Code review with a **necessity** category. |
| **Agent OS v3** | Standards synced back to profiles. Specs come from plan mode. | Deferred to the native todo list. Those todos were later removed (see §4). | Deferred to the model | Standards only | None of its own |
| **Task Master** | `update`/`update-task` re-write tasks from a prompt | `tasks.json` status, `next` | None | `testStrategy` field per task | None |
| **ruflo** | n/a | Memory DB | "Swarms" | Claims only | Ongoing "[verification] HIGH" issues |
| **wshobson conductor** | Deviations from the tech stack: **stop, update `tech-stack.md` with a dated note**, then resume | `plan.md` markers `[ ]` → `[~]` → `[x]` **plus a commit SHA**. Plan updates are committed. Git notes per task. | No | TDD, >80% coverage target | Phase checkpoint with a manual verification plan |
| **gstack** | `/document-release` audits docs against changed behavior on each ship | n/a | n/a | **`/test-audit`** finds tests that cost more than they protect. `/review` sends every weakened test, timeout or suppression to a human. | `/review`, `/qa` (real browser or API), `/ship` gate, outside-model review |
| **Compound Eng.** | One growing plan doc. Learnings in `docs/solutions/` read by the next plan. | n/a | `ce-worktree` | **`ce-simplify-code` prunes useless tests and comments** before review | Report-only multi-agent review against the plan |

---

## 2. Framework notes

### 2.1 obra/superpowers: v7.0.2 (2026-11-03), 319,650 stars

**Facts**
- The flow and TDD stance are in the README (2026-11-03): "TDD … Deletes code written before tests", "Mandatory workflows, not suggestions".
- **v7.0.0 (2026-10-10)** rebuilt brainstorming and replaced the spec-document reviewer with a **builder check**: a fresh subagent reads the design as its builder and lists what it would still ask. This is the same "builder check" the brainstorm notes want to keep.
- v7.0.0 also asks which technology choices the user wants to own. This was added after a session designed an iOS app, never asked about the platform, and built a web app.
- **Backlash.** Issue #2530 ("v7's brainstorm questions are rather annoying", 2026-10-16, 46 comments) says the opener was formulaic and asked what the code already answered. One user counted it in 9 of 12 sessions. Fixes followed in v7.0.1 (2026-10-21) and v7.0.2 (2026-11-03): "ask a question only when the answer would change what gets built and nothing already answers it… otherwise state the call as a proposal", give options with a recommendation, and ask "why" first. In blind-graded evals, filler questions fell from 41 to 23. Users on 2026-10-28 still called it a regression from 6.4.2.
- **v6.4.2 (2026-09-25):** plans record decisions (signature, file, spec values, test assertions), not full code. There is a proportion self-check, plan length against spec length. Plans "took a quarter of the time and about a third of the tokens". This settled #895 ("plans over-specify implementation", 24 comments).
- **SDD skill (main, read 2026-11-18):**
  - "Rulings, not stalls". Decisions are recorded as `Ruling: <what> — <why> — <what it costs if wrong>`.
  - Only four things stop a run: irreversible actions, security-sensitive actions, external side effects, and a hopelessly broken plan.
  - The ledger is `progress.md` in a git-ignored workspace.
  - At the end, rulings are copied into the final message and the workspace is deleted. The final-review reference says: "the git history is the record now".
- **Speed and cost complaints:**
  - #743 (2026-03, 27 comments): "35 minute session… plain claude code 2 minutes".
  - #1152 (2026-04): a full 5-hour budget on a simple plan.
  - #2017 (2026-07-22): requests for a "Slim" version. The maintainer says v6.0 halved spend. A commenter measured Opus 5 alone at +67% turns and +49% cost on fixed tasks.
  - #1251: per-task review overhead on small tasks. The maintainers' answer was batching (v6.3.0) and merging the two reviewers into one (v6.0).
  - #1803: adversarial plan review was in 5.0 and was removed after "a lot of hate… about the additional performance hit".
- **#2177 (2026-08-19):** Claude Code **2.1.233 (2026-08-14)** removed TodoWrite and TaskCreate/Get/Update/List on Opus 4.8+, Sonnet 5, Fable 5, Mythos 5 and newer. They come back only with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` or a server flag. Four Superpowers skills still told the model to "create a todo".
- **#2599 (2026-10-22),** filed by Claude for Jesse Vincent: a parallel plan-and-build path.
  - Naive fan-out over about 26 packages produced 24 interface mismatches, 13 shared-file overlaps and about 200 contract change requests.
  - The fix:
    - a lead-written master plan;
    - a **contract registry** in which every entry names its producer and consumer packages, with an append-only "Registry fixes" log;
    - a **foundations package built first and alone**;
    - disjoint `Owns` paths;
    - DAG scheduling instead of wave barriers;
    - an append-only `02-decisions.md` (`merge=union`), with entries marked `[decided]` or `[pending human]`, and pre-authorized recommendations kept marked as pending for a morning audit.
- v7.0.1: Claude Code re-attaches skills cut off at **20,000 characters** after compaction. One session lost SDD's five-round limit this way and ran 18 fix rounds. Superpowers now fails CI on any SKILL.md of 20,000 bytes or more.

**Inference**
- The user's P1 is structural in Superpowers, not an Anvil bug. Mid-build decisions are kept in a scratch ledger and then deleted, and nothing writes them back to the spec.
- Superpowers is converging on the user's own ideas (builder check, lean plans, rulings with costs, fewer questions). The rebuild is going the same way as upstream, not against it.

### 2.2 github/spec-kit: v1.4.2 (2026-11-17), 150,375 stars

**Facts**
- Spec template: mandatory User Scenarios (P1, P2, P3 stories, each "independently testable"), `FR-###`, `SC-###`, Edge Cases and Assumptions.
- `/speckit-specify` makes **informed guesses** and allows **at most 3 `[NEEDS CLARIFICATION]` markers**. Everything else becomes a documented default in an Assumptions section.
- Tasks template: "Tests are OPTIONAL — only include them if explicitly requested". When included, they are written first and must fail. `[P]` marks tasks that can run in parallel. There are phase checkpoints.
- **`/speckit-converge`** (added 2026-06-17):
  - It reads spec, plan and tasks as "the sole source of intent".
  - It builds an inventory keyed by FR/SC/US-AC.
  - It classifies gaps as **missing / partial / contradicts / unrequested**, assigns severity, and appends a `## Phase N: Convergence` task block.
  - Re-run implement and converge until "Converged". It never edits the spec or plan. "Completion claims are not evidence."
- Change handling is the open sore:
  - #620 (2025-09, still referenced in 2026): specs go stale feature by feature.
  - #4156 (2026-08-16) proposes `/speckit.revise`: never rewrite; mark old lines **SUPERSEDED by {new-id}** or **RETIRED**; add a new ID instead of editing the meaning of an old line; append only, including **remove-code tasks**. It is stale as of 2026-11-17.
  - #4164 (2026-08-17): agents find related requirements **by grepping prose**, miss reworded lines, and create duplicate or contradictory live requirements. It proposes a script-owned ID inventory. The maintainer said to ship it as an extension.
  - #4944 (2026-10-13): "flow-back / flow-forward / living" persistence models, as exploration only.
- Complaints: #75 "SpecKit creates the illusion of work" (2025-09, 26 comments): overengineering, "hundreds of unnecessary tests". The Oct 2026 benchmark measured 690 spec lines and 473 s / $2.84 on a 24-line ledger task.

**Inference**
- Spec-kit's `converge` is the strongest public answer to P3.
- Its lack of a revise flow is a live, documented example of P1. Anvil should take the #4156 semantics, which are designed but not shipped, rather than wait for them upstream.

### 2.3 Fission-AI/OpenSpec: v2.1.0 (2026-11-17), 75,136 stars

**Facts**
- Philosophy: "fluid not rigid… iterative not waterfall… brownfield".
- Each change is a folder with `proposal.md` (why and what changes), **delta specs** (`## ADDED / MODIFIED / REMOVED Requirements`, with scenarios), `design.md` and `tasks.md`. `archive` merges the deltas into the living `openspec/specs/`.
- There are no phase gates. Any artifact can be updated at any time.
- `/verify` was added after #381 (closed 2026-04-11).
- #783 (open since 2026-03-01): artifacts generated in one forward pass contradict each other (a scope item in the proposal turns up as a design non-goal). A community "refine" skill needed an explicit "**cross-artifact propagation (MUST)**" rule before Sonnet would propagate design edits to specs and tasks.
- Rename problems with deltas: #1697 (a renamed scenario reads as dropped) and #1112.
- Many users pair OpenSpec (the "what") with Superpowers (the "how"): #780, #973. Comparison articles warn that without a bridge you get duplicate design docs and two task lists.

**Inference**
- The delta-spec plus archive pattern is the cleanest public answer to "the spec must reflect what was actually built".
- #783 shows that propagation has to be an explicit, mandatory step. The model will not do it on its own.

### 2.4 BMAD-METHOD: v6.12.4 stable, v7 alpha (Nov 2026), 55,500 stars

**Facts**
- v7 retires a long list of v6 skills, including `bmad-correct-course`, `bmad-sprint-planning`, `bmad-sprint-status`, `bmad-create-epics-and-stories`, `bmad-check-implementation-readiness` and `bmad-spec` (`retired.toml`).
- v6.12: "Build decides how much ceremony a change needs after investigating it, not before. Simple changes now get a two-section spec."
- Review:
  - depth `none`/`quick`/`thorough`, **default quick** (one reviewer: acceptance criteria, repo rules, bugs);
  - thorough uses four lenses, one of them **intent alignment**;
  - triage **rejects disproved findings and low findings whose fix would add complexity**;
  - surviving findings become patch / defer / **decision needed**.
- "Real findings on a third pass point outside the change: a weak spec or unclear repo rules."
- A reviewer without the ticket or plan "can only judge the diff against itself".
- Code is done only after review, a commit, and a human marking it done.
- v6.12 release note: "Review triage logs a verdict and evidence for every finding, so nothing gets dropped silently."
- Benchmark (2026-10-13): BMAD 6.12.2 was the cheapest of the spec tools (217 s, $1.89, 13/13). But "one sentence of pre-approval skipped both stops."

**Inference**
- BMAD's large persona-and-sprint machinery (PM, PO, SM, sprint status, correct-course) is being thrown out in favour of one build skill that sizes itself. That is the clearest sign that phase-per-persona ceremony did not survive contact with stronger models.

### 2.5 Kiro specs (and cc-sdd, the open clone)

**Facts (Kiro)**
- Three files under `.kiro/specs/`: requirements in EARS notation, design, tasks.
- When requirements change, update requirements, then design, then press **Sync Files** on tasks.md. It "will create new tasks that map to the new requirements" and "automatically mark completed tasks" by analyzing the code.
- **Analyze Requirements** looks for inconsistency, ambiguity and gaps before design (docs updated 2026-09-25).
- Bugfix specs record *current, expected and unchanged* behavior and generate property-based tests for "the fix and the preservation of existing behavior".
- Independent tasks run in dependency waves.
- Quick Spec (May 2026, per a secondary source) runs all three phases in one go with no approval gates.

**Facts (cc-sdd v3.1.0, 2026-09-23)**
- "Code remains the source of truth. Specs make the boundaries between parts of the code explicit."
- design.md has a **File Structure Plan** that drives task boundaries. Tasks are annotated `_Boundary:_` and `_Depends:_`.
- The reviewer checks **boundary compliance**. A debugger subagent is triggered after 2 rejected rounds.
- Approvals are recorded on disk in `spec.json` (`approvals.requirements.approved`…).
- Cross-cutting discoveries go into `## Implementation Notes` in tasks.md and are injected into later implementer prompts.
- "If the discipline feels like overhead, your specs are probably too big."

**Inference**
- Kiro's Sync Files and cc-sdd's Implementation Notes are both "flow-forward" mechanisms.
- Approval in `spec.json` is the only gate among these tools that lives on disk, not only in the prompt. The benchmark author's main conclusion was "if the gate matters, enforce it on disk".

### 2.6 GSD, now GSD Core (open-gsd/gsd-core v1.21.0, 2026-11-13)

**Facts**
- The original `gsd-build/get-shit-done` (64,131 stars) is **archived**. Its last push was 2026-05-31, and secondary sources say it was archived about 2026-06-26.
  - On 2026-05-22 a notice said the repo "appeared compromised". Core contributors forked it as GSD Redux, renamed to GSD Core on 2026-05-31.
  - The old npm package `get-shit-done-cc` 1.42.3 is unsupported but still on the registry.
  - `gsd-2` is archived as well and continues as `gsd-pi`.
- Executor **deviation rules**:
  1. auto-fix bugs;
  2. auto-add missing critical functionality;
  3. auto-fix blockers (package installs excepted: a human checks those);
  4. **stop and ask about architectural changes**, giving what was found, the proposed change, why, impact and alternatives.

  "When in doubt: does it affect correctness, security, or ability to complete the task? YES → Rules 1–3. MAYBE → Rule 4." All deviations are logged in SUMMARY.md.
- `gsd-verifier`: **goal-backward** verification. "SUMMARY.md claims are not evidence". FORCE stance ("starting hypothesis: tasks completed, goal missed"). Every truth ends as VERIFIED, FAILED or UNCERTAIN.
- `/gsd-verify-work`: a UAT walk-through, one deliverable at a time, with severity inferred from the user's words. Failures spawn parallel debuggers and gap-closure plans.
- **VERIFICATION.md turns `stale`** when any file its verdict covers changes (content digest).
- **Necessity review**: flags code that guards against states that cannot occur. Keep, simplify or delete, with cited evidence. Inputs crossing a trust boundary are always kept. The fixer will not delete without `--all`.
- `gsd-nyquist-auditor`: writes behavioral tests for requirement gaps that "can fail". Implementation files are read-only to it.
- Scale: about 6,200 issue/PR numbers in 6 months, about 100 how-to docs, a contract-drift linter for its own agents, CI conformance shards.

**Inference**
- GSD Core has the best *verification semantics* in this survey: goal-backward checking, staleness by fingerprint, necessity review.
- It is also a warning about complexity creep. A "light-weight" framework now ships a contract registry linter for its own prompts.
- Its archive episode is a supply-chain warning for any skill installed from a third party.

### 2.7 buildermethods/agent-os: v3.0.0 (2026-01-20), 5,617 stars

**Facts**
- v3 dropped spec writing ("now best handled using Plan mode"), task breakdown ("Claude Code… automatically create[s] and track[s] todo lists") and orchestration ("frontier models manage and delegate tasks on their own now"). It now covers only standards: discover, inject (via `index.yml`) and sync.

**Inference**
- This is the clearest "framework retreat" in the survey. Seven months later, Claude Code removed the todo tools that v3 relied on (§2.1, #2177). Handing tracking to harness features that can disappear is fragile.

### 2.8 eyaltoledano/claude-task-master: 28,371 stars, dormant

**Facts**
- Last release 0.43.1 on 2026-03-31. Last commit 2026-04-23 (README links moved to tryhamster.com).
- Issues since June 2026 have no maintainer replies, including path traversal (#1711, #1714, #1715) and "You fucked up my entire `.claude.json`" (#1709, 2026-06-11).
- Model: a PRD is parsed into `tasks.json` (deps, priority, `testStrategy`, subtasks) and driven through an MCP server.

**Inference**
- Abandoned in favour of a commercial product. Its pattern, an external task database behind MCP, has been overtaken by plain markdown task files that the agent edits directly.

### 2.9 claude-flow → ruvnet/ruflo: 82,004 stars

**Facts**
- `ruvnet/claude-flow` redirects to `ruvnet/ruflo`. v3.77.2 shipped on 2026-11-17, with a very high release cadence.
- Long-running issues question whether it works:
  - #653 (2025-08) "85% of MCP Tools Are Mock/Stub Implementations";
  - #640 "Verification & Truth Enforcement System Failure";
  - #1425 (2026-03) "Nothing is working";
  - a series of "[verification] HIGH: witness manifests report every entry missing" issues (#3189, open since 2026-09-05, 103 comments).

**Inference**
- High stars and "swarm" marketing do not show that it works. It has no spec, plan or verification method worth copying. Avoid.

### 2.10 wshobson/agents (and the archived wshobson/commands)

**Facts**
- `wshobson/commands` is archived: "replaced by the plugin marketplace at wshobson/agents".
- The catalog has 94 plugins, 202 agents, 185 skills and 105 commands, generated for 7 harnesses.
- The `conductor` plugin, which mirrors Google's gemini-cli Conductor (3,796 stars, pushed 2026-09-01):
  - task markers `[ ]` → `[~]` → `[x]`, with the **short commit SHA appended to the task line**, and the plan update committed;
  - git notes per task;
  - **if the implementation deviates from the tech stack: stop, update `tech-stack.md` with a dated note, then resume**;
  - TDD with a >80% coverage target;
  - phase checkpoints with a manual verification plan.

**Inference**
- Conductor's SHA-on-task-line is the cheapest robust progress tracker in the survey. It is human-readable, it is in git, and the claim can be checked against `git show`.

### 2.11 Anthropic: anthropics/skills and claude-plugins-official

**Facts**
- `anthropics/skills` (196,962 stars) contains no development-workflow skill: no brainstorm, plan or TDD skill.
- The official marketplace (47,612 stars) ships:
  - `feature-dev`: 7 phases (discovery, codebase exploration, clarifying questions, architecture design, implementation, quality review, summary);
  - `ralph-loop`: a Stop-hook loop with a completion promise and max iterations;
  - `code-simplifier`, `pr-review-toolkit`;
  - `project-artifact`: a "living status page" (published as an Artifact, which this user does not want).
- Superpowers has been in the official marketplace since 2026-01-15, per a secondary source.

**Inference**
- Anthropic's own structured flow is a light 7-phase command with no spec file and no traceability. Anvil cannot copy rigour from it, only the phase shape. (Anthropic's guidance is covered in the sibling report `2026-11-18-anthropic-guidance.md`.)

### 2.12 Additions: more popular or newer than some of the list

- **garrytan/gstack** (141,963 stars):
  - role skills, with a rule that every skill's output feeds the next;
  - **`/test-audit`**: tests that "cost more than they protect" (source greps, duplicates, assertion-free probes, test-only exports), each with an evidence card, report-only;
  - `/review` sends "every weakened test, timeout, snapshot or suppression" to a human ("gate integrity");
  - `/plan-ceo-review` has modes Expansion / Selective Expansion / **Hold Scope / Reduction**;
  - **`/design-shotgun`** generates 4–6 mockup variants on a comparison board.
- **EveryInc/compound-engineering** (26,143 stars):
  - **one plan artifact that grows from requirements into an implementation plan**;
  - **`ce-simplify-code`** "prunes useless tests and comments before review";
  - `ce-compound` writes learnings to `docs/solutions/`, which the next plan reads;
  - `/lfg` runs the whole loop hands-off.
- **affaan-m/ECC** (305,972 stars): 72 agents, 327 skills, a move from commands to skills, "instinct" learning. **Inference:** a kitchen sink. The star count measures discovery, not workflow quality.
- **gastownhall/beads** (28,815 stars, formerly steveyegge/beads): a git- and Dolt-backed dependency graph of issues (`bd ready`, `--claim`, `close`), meant to replace "messy markdown plans".
- **automazeio/ccpm** (8,452 stars): PRD → epic → GitHub issues, with worktrees for parallel streams and traceability to issues.
- **Public benchmark** (felipefontoura.com, run on 2026-10-13, n=1, claude-opus-5-5):

  | Tool | Time | Cost | Acceptance checks passed |
  |---|---|---|---|
  | Superpowers 7.0.0 | 40 s | $0.33 | 13/13 |
  | BMAD | 217 s | $1.89 | 13/13 |
  | OpenSpec | 277 s | $2.16 | 12/13 |
  | Spec Kit | 473 s | $2.84 | 13/13 |

  Superpowers got there because brainstorming never ran: it decided the key design question silently. Author: "in all four tools, approval lived in the prompt."

---

## 3. Ideas worth stealing

Each idea is tied to one of the user's problems. **Where it beats the current Anvil proposal** says where a framework solved the problem better than the brainstorm notes (§5 proposals).

### P1: spec, plan and code drift

1. **Supersede, don't edit** (spec-kit #4156 proposal).
   - A change from A to A1 gets a **new ID**. The old line is marked `SUPERSEDED by S3b (2026-11-18, reason)` and is never reworded. A line that no longer applies is marked `RETIRED`.
   - Tasks are append-only: open tasks for a dead ID are cancelled, finished tasks stay, and **remove-code tasks** are added when the old behavior already shipped.
   - *Where it beats the current Anvil proposal:* the notes propose "a dated edit to S3". With an edit, everything that cites S3 still looks valid. With a new ID, every stale reference is mechanically detectable, because it points at a dead ID.
2. **Staleness by fingerprint** (GSD Core VERIFICATION.md). Each review or verification records the spec lines and files it covered. If any of them changes afterwards, the verdict reads as `stale`. This is how "everything pointing at S3 gets flagged for a re-check" can work without the model remembering to do it.
3. **A script-owned ID inventory, not prose grep** (spec-kit #4164). Models miss reworded requirements and create duplicates. *Inference:* keep S-lines in a parseable table, or have a tiny script list the live, superseded and retired IDs, so that the per-task review and the change flow-back read one list.
4. **Mandatory cross-artifact propagation** (OpenSpec #783 refine skill). Sonnet propagated design edits only after an explicit "Cross-artifact propagation (MUST)" step. Make "update spec and plan" a checklist step inside the change flow, not something the model is trusted to do.
5. **Stop, write it down, resume, on deviation** (Conductor). When a build deviates from a decision, the record is updated *before* coding continues, with a dated note.
6. **Fold the delta back at the end** (OpenSpec archive). At "done", the spec describes what was built, and the change history stays in the dated SUPERSEDED lines.
7. **Avoid Superpowers' ledger lifecycle.** Rulings in a git-ignored file that is deleted at the end are exactly how the plan comes to say A while the code says A1. Commit the record.
8. *Optional:* **one artifact that grows** (Compound Engineering). Fewer files means fewer places to disagree. *Inference:* a single document with a "Spec (approved 2026-…)" section and a "Plan (approved 2026-…)" section keeps both of the user's stops and halves the drift surface.

### P2: no live progress tracking

1. **Do not rely on TodoWrite or Task\*.** Claude Code 2.1.233 (2026-08-14) removed them on current models (#2177). Progress has to live in a file.
2. **Conductor's markers:** `[ ]` → `[~]` → `[x] a1b2c3d`. Every finished item carries the commit SHA, the file is committed, and anyone can open it mid-run. That answers the user's 30 or so "done?" messages.
3. **"Completion claims are not evidence"** (spec-kit converge, GSD verifier, Kiro Sync Files). The progress file says what was claimed. The end check re-derives what is true from the code.
4. **Implementation Notes carried forward** (cc-sdd). Cross-cutting discoveries go in a section of the progress or plan file and are injected into later briefs. This also covers compaction: Superpowers found that losing its place after compaction was "the single most expensive failure observed".
5. **A stop state before "done"** (BMAD): the build stops at `built`, and done needs review plus the user. This maps onto the open "finishing" question (§6.1 of the notes).

### P3: did we build what was asked

1. **A converge loop with gap types** (spec-kit). At the end, inventory every live S-line and classify each as **missing / partial / contradicts / unrequested**. Add tasks and loop until clean. This is the "did we build what was asked" check that the notes say is missing.
2. **Goal-backward, adversarial stance** (GSD verifier). Start from "tasks completed, goal missed" and try to disprove it. Each truth ends VERIFIED, FAILED or UNCERTAIN, and UNCERTAIN goes to the user.
3. **A human walk-through for the user-visible parts** (GSD `/gsd-verify-work`, BMAD `bmad-walkthrough`). One deliverable at a time, "should do X, does it?" This directly targets the cycle of "rebuild, pass checks, same complaint again".
4. **Reviewers always get the intent** (BMAD): "without it the reviewers can only judge the diff against itself". The per-task review brief must contain the S-lines, not only the diff.
5. **A third-pass heuristic** (BMAD): if a third review still finds real issues, the spec is weak. Stop fixing code and fix the spec.
6. *Where it beats the current Anvil proposal:* the notes propose a per-task spec review plus one end verification. The frameworks add the missing piece: an **end-of-build intent inventory** that also catches *unrequested* work.

### P4: test bloat

1. **Tests are opt-in, tied to a requirement** (spec-kit: "only if explicitly requested"). The test plan names the S-line each test protects.
2. **A test audit with evidence cards** (gstack `/test-audit`): find source-grep tests, duplicates, assertion-free probes and test-only exports. It reports only, and the user decides. This is the "audit an existing bloated suite" request in §4 of the notes, done through the normal flow.
3. **Gate integrity** (gstack `/review`): every weakened test, raised timeout, updated snapshot or added suppression goes to the user. This is a ready-made form of "editing a test to make it pass requires a changed spec line".
4. **Prune before review** (Compound Engineering `ce-simplify-code`). This is the closest existing practice to the user's "scaffold tests deleted before finishing". *Inference:* make the deletion a converge check ("scaffold tests still present"), not a step the model is trusted to remember.
5. **Tests that can fail, for core behavior** (GSD Nyquist auditor; Kiro's preserved-behavior property tests). Test the gap's hard edge, with implementation files read-only to the test writer. Kiro's "unchanged behavior" section is a neat way to state what core behavior must not move.
6. **Evidence against blanket TDD.** Superpowers' mandatory TDD is its most complained-about cost (#743, #2017). The benchmark found spec-kit's analyze step catching tests "that would pass before the feature existed", which is test theatre.

### P5: over-engineering

1. **"Unrequested" as a gap type** (spec-kit converge). Code that no S-line asks for gets a task to justify it or remove it.
2. **Necessity review** (GSD Core): guards against impossible states. Keep, simplify or delete, citing the proof. Trust-boundary inputs are always kept. Deletion is the user's scope call.
3. **Triage rejects fixes that add complexity** (BMAD): low-severity findings whose fix would add complexity are dropped and logged.
4. **A proportion check on plans** (Superpowers v6.4.2): compare plan length to spec length. A plan several times longer is a transcript.
5. **Scope modes** (gstack): Hold Scope and Reduction as explicit plan-review modes, so cutting scope is a normal option.

### P6: too many questions vs silent decisions

1. **A hard cap plus documented guesses** (spec-kit: at most 3 `[NEEDS CLARIFICATION]`, the rest become Assumptions). This fits the user's "decisions go *into* the spec, where Saad reviews them".
2. **Ask only when the answer changes what gets built** (Superpowers v7.0.2). Otherwise state the call as a proposal. When there's a choice, show options with a recommendation. v7.0.0's formulaic opener is the cautionary tale (#2530).
3. **A ruling format with cost** (Superpowers SDD): `Ruling: what — why — cost if wrong`. *Where it beats the current Anvil proposal:* the notes propose "call, reason, alternatives". Adding "cost if wrong" tells the user which silent decisions are worth checking.
4. **Decisions marked `[decided]` or `[pending human]`** (Superpowers #2599). Under AFK, adopted recommendations *stay marked pending* so they can be audited the next morning. This fits the user's AFK mode exactly.
5. **Deviation rules 1–4** (GSD): a crisp line between what the builder fixes silently (bugs, critical gaps, blockers) and what it must raise (architecture). Also usable to classify mid-build requirement changes for the pushback rule.
6. **Variations, not interrogation** (gstack `/design-shotgun`, 4–6 variants on a comparison board; Superpowers' visual companion). This supports the user's "2 or 3 worked variations with mocks".

### Parallel split (supports the plan's execution strategy)

1. **Foundations first, alone** (#2599). One package creates every shared file, import line, manifest entry, route and fixture before the fan-out. Then disjoint `Owns` paths, plus "a package needing anything outside its Owns stops and reports". This is the scaled-up version of "pin the shared contracts before splitting work".
2. **Producer and consumer per contract entry, with an append-only fix log** naming the affected packages.
3. **Boundary annotations** (cc-sdd `_Boundary:_` / `_Depends:_`, a File Structure Plan) checked by the reviewer.
4. **DAG, not wave barriers** (#2599): with barriers, finished packages sat idle for about 2.5 h.

---

## 4. Patterns that failed or got abandoned, and why

| Pattern | Who | When | What happened / why (fact) | Lesson (inference) |
|---|---|---|---|---|
| Relying on the harness's todo tools for tracking | Agent OS v3, Superpowers | v3 2026-01-20; removal 2026-08-14 | Agent OS v3 handed task tracking to Claude Code's todos. Claude Code 2.1.233 removed TodoWrite and Task\* on current models. Superpowers' todo instructions became impossible to follow (#2177). | Track progress in a committed file you own. |
| Per-persona, per-phase ceremony (PM, PO, SM, sprint status, correct-course) | BMAD | v7 alpha, 2026 | v7 `retired.toml` drops correct-course, sprint-planning, sprint-status, epics-and-stories and others, for one `bmad-build` that sizes the process after investigating. | Size the ceremony after reading the code, not before. |
| Full-code plans | Superpowers | Fixed 2026-09-25 (v6.4.2) | Plans were transcripts of code. Executors copy-pasted. Planning cost 4× time and 3× tokens (#895). | Plans hold decisions and interfaces. |
| Two reviewers per task (spec, then quality), every task | Superpowers | Merged in v6.0; batching in v6.3.0 (2026-08) | Overhead on small tasks (#1251: 75 subagent tasks, 1,573 tool calls in one session). | Keep a per-task review, but one cheap reviewer, batched for mechanical tasks. |
| Adversarial plan review on by default | Superpowers | Removed after 5.0 | "a lot of hate from end users about the additional performance hit and token spend" (#1803). The maintainer wants it back as an option. | Make heavy checks opt-in. The user's "extra checkpoints only when asked" matches this. |
| Formulaic opening questions | Superpowers | v7.0.0 (2026-10-10), tuned twice by 2026-11-03 | #2530: generic "why" questions that the code already answered. Users disabled the skill or forked it (superpowers-remix). | Read the context first, then ask only questions that change the build. |
| Gates enforced only in the prompt | All four in the benchmark | 2026-10-13 | Superpowers skipped brainstorming. BMAD's stops were skipped by one pre-approval sentence. Spec-kit's script lets an empty `plan.md` through. | Record the approval on disk (cc-sdd `spec.json`) and check it before building. |
| Per-feature specs that never consolidate | spec-kit | #620 (2025-09) to #4944 (stale 2026-11-17) | Old feature specs go stale as later features change behavior. Living-spec support is still only an extension or proposal. | Fold changes back into one living spec at done (OpenSpec archive). |
| Prose-grep requirement alignment | spec-kit | #4164 (2026-08-17) | Reworded requirements are missed, creating duplicate or contradictory live lines. "analyze… only reports what the model loaded." | IDs in a parseable list. |
| External task DB behind MCP | claude-task-master | Dormant since 2026-04 | No releases since 2026-03-31. Security bugs unanswered. Pivot to a commercial product. | Plain markdown task files the agent edits directly. |
| Swarm or "hive-mind" orchestration as a product | claude-flow / ruflo | 2025–2026 | Repeated issues saying the tools are mocks or verification is broken (#653, #640, #3189). | Parallelism needs contracts and ownership (#2599), not more agents. |
| Naive parallel fan-out of package plans | Superpowers (real build, #2599) | 2026-10 | 24 interface mismatches, 13 shared-file overlaps, about 200 contract change requests. | Freeze the shared surface first and build foundations alone. |
| Single-maintainer framework with unpinned installs | GSD | Archived about 2026-06 | Compromise concerns, a fork took over, the old npm package is still live. | Vendor and pin what you depend on. Anvil copying Superpowers' MIT skills, rather than depending on it, is the right call. |
| Slash commands as the primary surface | OpenSpec v2.0 (2026-11-11), cc-sdd v3, ECC, BMAD v7 | 2026 | Commands were removed or deprecated in favour of skills ("Each command already has a matching skill"). | Ship Anvil as skills only. |
| Long SKILL.md files | Superpowers | v7.0.1 (2026-10-21) | After compaction, skills over 20,000 characters are re-attached cut off. One session lost its round cap and ran 18 fix rounds. | Keep each SKILL.md under 20 KB and move details into `references/`. |
| Weight of the framework itself | GSD Core | 2026-06 to 11 | About 6,200 issues and PRs, about 100 how-to docs, a linter for its own prompt contracts. | A "light-weight" label does not stop complexity creep. Anvil's own bar is simplicity. |
| Sibling list repos going stale | travisvn/awesome-claude-skills, Pimzino/claude-code-spec-workflow | Last pushes 2026-04-28 and 2025-09-07 | Superseded by larger lists or MCP versions | Don't depend on lists. Cite the primary repos. |

---

## 5. Where the user's plan already matches the field, and where it is alone

- **Matches the field (keep):**
  - numbered requirement IDs: spec-kit FR/SC, Kiro EARS, GSD REQ, BMAD AC;
  - a fresh builder check: Superpowers v7;
  - pinning contracts before a split: #2599, cc-sdd boundaries;
  - labelled decisions: Superpowers rulings, #2599 decision log;
  - review sized to the change: BMAD quick by default;
  - a spec stop before building: every spec tool.
- **Alone, so there is no prior art to copy:**
  - asking "change request or new feature?" when requirements change, and naming the cost of the change. *Inference:* OpenSpec gets this for free, because every change is a folder with a `proposal.md` "why". GSD Rule 4 and BMAD's split to `deferred-work.md` are the nearest equivalents;
  - "scaffold tests deleted before finishing". The nearest are CE's pruning and gstack's audit, and neither tracks the build-only versus keep distinction.
- **The field disagrees with the user's plan:**
  - Kiro Quick Spec (May 2026) and the benchmark both suggest that a separate *plan* approval stop costs a lot on small work. The user's AFK and "skip it" options already cover this.
  - Make sure the default flow sizes itself the way BMAD v7 does, so that a one-line change never meets two stops.

---

## Sources (all read 2026-11-18 unless dated otherwise)

- obra/superpowers: [README](https://github.com/obra/superpowers), releases [v7.0.0](https://github.com/obra/superpowers/releases/tag/v7.0.0), [v7.0.1](https://github.com/obra/superpowers/releases/tag/v7.0.1), [v7.0.2](https://github.com/obra/superpowers/releases/tag/v7.0.2), [v6.4.2](https://github.com/obra/superpowers/releases/tag/v6.4.2). [SDD SKILL.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md), [final-review.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/references/final-review.md). Issues [#2530](https://github.com/obra/superpowers/issues/2530), [#2177](https://github.com/obra/superpowers/issues/2177), [#2599](https://github.com/obra/superpowers/issues/2599), [#2017](https://github.com/obra/superpowers/issues/2017), [#743](https://github.com/obra/superpowers/issues/743), [#895](https://github.com/obra/superpowers/issues/895), [#1251](https://github.com/obra/superpowers/issues/1251), [#1803](https://github.com/obra/superpowers/issues/1803), [#1152](https://github.com/obra/superpowers/issues/1152)
- github/spec-kit: [README](https://github.com/github/spec-kit), [converge.md](https://github.com/github/spec-kit/blob/main/templates/commands/converge.md), [specify.md](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md), [tasks-template.md](https://github.com/github/spec-kit/blob/main/templates/tasks-template.md), [spec-template.md](https://github.com/github/spec-kit/blob/main/templates/spec-template.md). Issues [#4156](https://github.com/github/spec-kit/issues/4156), [#4164](https://github.com/github/spec-kit/issues/4164), [#4944](https://github.com/github/spec-kit/issues/4944), [#620](https://github.com/github/spec-kit/issues/620), [#75](https://github.com/github/spec-kit/issues/75)
- Fission-AI/OpenSpec: [README](https://github.com/Fission-AI/OpenSpec), [v2.0.0](https://github.com/Fission-AI/OpenSpec/releases/tag/v2.0.0). Issues [#783](https://github.com/Fission-AI/OpenSpec/issues/783), [#780](https://github.com/Fission-AI/OpenSpec/issues/780), [#381](https://github.com/Fission-AI/OpenSpec/issues/381)
- BMAD-METHOD: [README](https://github.com/bmad-code-org/BMAD-METHOD), [retired.toml](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/method/bmod-method/retired.toml), [review-choices.md](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/skills/method/bmod-method/help/review-choices.md), [How BMad works](https://docs.bmad-method.org/start/how-bmad-works/)
- Kiro: [Specs best practices](https://kiro.dev/docs/specs/best-practices/) (updated 2026-09-25). Secondary: [kirotutorial.com](https://kirotutorial.com/concepts/specs/), [verdent.ai guide](https://www.verdent.ai/guides/agents/kiro-spec-driven-development)
- gotalab/cc-sdd: [README](https://github.com/gotalab/cc-sdd), [v3.1.0](https://github.com/gotalab/cc-sdd/releases/tag/v3.1.0), [skill-reference.md](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/skill-reference.md), [why-cc-sdd.md](https://github.com/gotalab/cc-sdd/blob/main/docs/guides/why-cc-sdd.md)
- GSD: [gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done) (archived), [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core), [verify-and-ship.md](https://github.com/open-gsd/gsd-core/blob/main/docs/how-to/verify-and-ship.md), [resolve-necessity-findings.md](https://github.com/open-gsd/gsd-core/blob/main/docs/how-to/resolve-necessity-findings.md), [gsd-executor.md](https://github.com/open-gsd/gsd-core/blob/main/agents/gsd-executor.md), [gsd-verifier.md](https://github.com/open-gsd/gsd-core/blob/main/agents/gsd-verifier.md). Archive story (secondary): [skillstested.com](https://skillstested.com/skills/get-shit-done/), [mehmetkuru.dev](https://mehmetkuru.dev/en/kaynaklar/gsd-core/)
- [buildermethods/agent-os v3.0.0](https://github.com/buildermethods/agent-os/releases/tag/v3.0.0). [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master). [ruvnet/ruflo](https://github.com/ruvnet/ruflo) issues [#653](https://github.com/ruvnet/ruflo/issues/653), [#640](https://github.com/ruvnet/ruflo/issues/640), [#3189](https://github.com/ruvnet/ruflo/issues/3189)
- [wshobson/agents](https://github.com/wshobson/agents), [conductor plugin](https://github.com/wshobson/agents/tree/main/plugins/conductor), [wshobson/commands](https://github.com/wshobson/commands) (archived), [gemini-cli-extensions/conductor workflow.md](https://github.com/gemini-cli-extensions/conductor/blob/main/skills/conductor-setup/assets/workflow.md)
- [anthropics/skills](https://github.com/anthropics/skills), [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (feature-dev, ralph-loop, project-artifact READMEs)
- [garrytan/gstack](https://github.com/garrytan/gstack), [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin), [affaan-m/ECC](https://github.com/affaan-m/ECC), [gastownhall/beads](https://github.com/gastownhall/beads), [automazeio/ccpm](https://github.com/automazeio/ccpm)
- Lists: [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code), [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills), [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills), [vercel-labs/skills](https://github.com/vercel-labs/skills)
- Comparisons and benchmark: [felipefontoura.com, "OpenSpec vs Superpowers vs Spec Kit"](https://felipefontoura.com/articles/spec-driven-development-tools-compared/) (published 2026-07-11, updated 2026-10-29, benchmark run 2026-10-13). [spec-coding.dev](https://spec-coding.dev/blog/spec-driven-development-tools-openspec-spec-kit-superpowers), [specroot.io](https://specroot.io/notes/spec-kit-vs-openspec-vs-bmad/), [developertoolkit.ai](https://developertoolkit.ai/en/ecosystem/frameworks/spec-driven-frameworks/), [Pulumi blog](https://www.pulumi.com/blog/claude-code-orchestration-frameworks/)
