# Parallel build for Anvil: consequences, whether, how

- **Date:** 2026-11-18 (research round 2)
- **Question:** Superpowers 7.0.2 builds one task at a time. Saad wants 3 to 4 isolated implementers running in parallel, to get roughly 3 to 4 times the speed. What goes wrong, when does it pay, how do others do it, and what must the spec and plan contain?
- **Read first:** [brainstorm notes §9](../2026-11-18-brainstorm-notes.md#9-reframe-after-the-research-2026-11-18), the four round-1 reports in this folder, Superpowers 7.0.2 `subagent-driven-development` and `writing-plans`, and the private session evidence (summarized here without client names or quotes).
- **Labels:** **Fact** is something a source says or shows. **Inference** is my reading. Every source is dated in [§8](#8-sources-all-dated).

---

## 0. Bottom line

1. **Parallel build is workable, but only with four things in place.** These are a foundations task that runs first and alone, declared write sets that don't overlap, worktree isolation from the right base, and a serial merge step that runs the tests once on the merged result. Every tool that ships parallel build in late 2026 has ended up with these same four: GSD Core, Kiro, spec-kit, ccpm, the Superpowers #2599 build brief, and the parallel Superpowers forks. Fan-out without them fails in a measurable way. The #2599 build found 24 interface mismatches and 13 shared-file overlaps across 26 packages.
2. **3 to 4 times faster is unlikely for one typical feature.** Inference from the model in §3: a well-split feature in 3 or 4 lanes gets about **1.5 to 2.5 times** on the build phase. Spec-coupled or chain-shaped work gets about 1 times, or worse. Brainstorm, spec and plan don't speed up at all. Kiro advertises "up to 4x", but only as a ceiling for "4+ independent tasks", and it publishes no data behind it.
3. **On a subscription, parallel spends the usage window faster without spending much more in total.** SDD already gives every task a fresh subagent, so running lanes side by side adds mainly the integration and drift-fix overhead (inference: about 10 to 30% more tokens). But it burns the 5-hour window about N times faster. If a build doesn't fit in one window, parallel lanes just reach the limit sooner and then wait. Saad's real sessions hit the limit 13 times.
4. **The cheaper speed win sits next to parallelism, not inside it.** In one public SDD report, 53 full-suite runs took 165 minutes. Saad's §9 rule ("a test result stays valid until the code changes") goes after that waste directly, and it carries no merge risk. Do both.
5. **Recommendation:** make parallel build an **opt-in execution strategy, chosen at the plan stop**. A mechanical parallel-safe check gates it, it runs 3 lanes by default on this laptop (4 at most), and every SDD per-task review stays. The default stays sequential whenever the check fails or the dependency graph is too narrow. Confidence is in §7.

---

## 1. Why Superpowers serializes (its stated reasons)

| What | Where | Date |
|---|---|---|
| **Fact:** "Never dispatch multiple implementation subagents in parallel (conflicts)." That one word is the whole stated reason in the skill. | SDD `SKILL.md`, dispatch section | v7.0.2, 2026-11-03 |
| **Fact:** obra: "superpowers prefers iterative implementation over parallel implementation. Parallel work is more likely to lead to conflicts and we value correctness over raw speed." | [#945](https://github.com/obra/superpowers/issues/945) | 2026-03-27 |
| **Fact:** obra, on swarm/teams mode: "it trades time for significantly increased token consumption without actually improving correctness." | [#464](https://github.com/obra/superpowers/issues/464) | 2026-03-17 |
| **Fact:** the prohibition became explicit after a report where SDD ran frontend tasks in parallel on interdependent EJS/JS/CSS files. That produced ID mismatches (`importSelectCount` vs `tmImportCountLabel`), class collisions, and bugs that "a 30-second page load after each individual task" would have caught. The triage note says "since v6.2.0 the skill forbids dispatching multiple implementation subagents in parallel — tasks run sequentially, each starting from the prior task's committed output". | [#995](https://github.com/obra/superpowers/issues/995) | filed 2026-03-29, triaged 2026-08-18 |
| **Fact:** the mechanics assume one line of commits. BASE is recorded before each dispatch, the review package is `BASE..HEAD`, and the implementer commits into the one worktree and runs "the full suite once before committing". | SDD `SKILL.md`, `implementer-prompt.md` | v7.0.2 |
| **Fact:** PRs that loosened the rule were all closed. The reasons given were "SDD stays serial by design for now" and that wording changes "need eval evidence". This covers [#1213](https://github.com/obra/superpowers/pull/1213) (worktree-per-implementer, serial `--ff-only` merges), [#1534](https://github.com/obra/superpowers/pull/1534) (allow parallel with `isolation: "worktree"`), [#1117](https://github.com/obra/superpowers/pull/1117) (dependency-aware orchestration) and [#1524](https://github.com/obra/superpowers/pull/1524) (parallel tracks by default). | PRs | closed 2026-09-26/27 |
| **Fact:** even overlapping task N's review with task N+1's implementation was declined: "This is not something that can be relied upon to be consistent. It is true in some cases, but not in all of them." | [#2674](https://github.com/obra/superpowers/issues/2674) | 2026-11-06, reply 2026-11-10 |
| **Fact:** the maintainer's own team has since written the most complete parallel design: a build brief "filed by Claude for Jesse Vincent". It is still open as an *opt-in alternate path*, not as a change to SDD. | [#2599](https://github.com/obra/superpowers/issues/2599) | 2026-10-22 |

**Inference.** Superpowers' position is not "parallel is wrong". It is "parallel without frozen contracts and isolation is wrong, and we haven't measured the version with them". The #2599 brief is the upstream answer, and Anvil should build on it rather than on the bare prohibition.

---

## 2. Consequences table

"How often" is the evidence-backed frequency in a Superpowers-style build. "Cost" is what it costs when it hits.

| # | Risk | How often | Cost when it hits | Mitigation | Source |
|---|---|---|---|---|---|
| 1 | **Shared-file collisions.** Barrels and `index` re-exports, route trees, `lib.rs`/`mod` lines, DI registration, manifests, i18n files, changelogs. | **Very common.** #2599: 13 overlaps across 26 packages. Foremerge: "Almost every task touches one of them, and almost no plan mentions them." Saad's evidence: frequent but cheap (router-list conflicts). | Low per incident, but it repeats every wave. | A **foundations task** pre-creates every module file, import line, route placeholder and manifest entry. Non-leaf modules hold only declarations, so leaf files can be owned. | #2599; Foremerge (dev.to, Oct 2026); private evidence |
| 2 | **Lockfiles and generated artifacts** (lockfiles, OpenAPI snapshots, generated clients). | Common whenever two tasks add dependencies. | **High, and silent.** Automatic lockfile resolution can drop dependencies. | Only the integrator touches them. It regenerates them per merge, and lanes never commit them. | #2599; Foremerge comment thread |
| 3 | **Migrations and the shared dev DB.** Number collisions; one agent's migration breaks another's schema; agents edit unshipped migrations in place, and the dev DB then rejects the checksum. | Common in DB-backed apps. Saad's evidence includes a migration applied from a draft branch's lane. | **High.** Confusing failures "because both agents blame their code" (matrix-os). | Reserve a migration number per task in the plan. Give each lane its own DB, named from the worktree path, with a reset recipe. Or keep schema work in the foundations task. | #2599; [#597](https://github.com/obra/superpowers/issues/597); [#2691](https://github.com/obra/superpowers/issues/2691); GSD planner-coupling rule |
| 4 | **Interface and contract drift.** Each lane invents its own field names and wire types. | **Common without a registry.** #2599: 24 interface mismatches and about 200 contract change requests. Saad's evidence has 2 cases: a field named `payment_status` against `status`, and a request type named two different ways. | **Medium to high.** It shows up only at reconcile or at runtime. | Commit the contracts as **code** (types, schema, endpoint table) in the foundations task. Keep a registry where each entry names its producer and consumers. Lanes never edit contracts; they file a change request. A lane that "needs anything outside its Owns stops and reports". | #2599; #995; private evidence |
| 5 | **Semantic conflicts:** a clean merge with a wrong result, such as one lane replacing a class while another extends it. | Less common, but invisible. Foremerge's replay of 76 intents found 1 textual conflict, plus 5 same-file pairs that merged cleanly. | **High.** Each branch passes its own tests. | Name the operation in each task (add, extend, replace, remove). Run the tests and a short integration review **on the merged result**, not per branch. | Foremerge; practitioner report §5 |
| 6 | **Stale worktree base.** Lanes fork from `origin/main` instead of the integration branch, so a lane misses the foundations or the previous wave. | **Very common with Claude Code defaults.** Saad's 66-agent session logged "stale base" 11 times. #2245: 4 worktrees forked 3 commits behind. | **Medium.** Rework, or merges of code built on the wrong base. | Set `worktree.baseRef: "head"`, or have the orchestrator create worktrees from the integration branch. Check `git rev-parse HEAD` at lane start and stop if it's wrong. **Fact:** Claude Code subagent worktrees "branch from your repository's default branch unless `worktree.baseRef` is set to `"head"`". | CC worktrees docs; [#2245](https://github.com/obra/superpowers/issues/2245); GSD wave guard; private evidence |
| 7 | **Parallel lanes in one checkout.** These cause git index races, `commit -a` sweeping up a sibling's half-done edits, relative-path `cp` into a sibling worktree, and a reviewer's build going red on a sibling's unfinished files. | Common whenever there's no worktree. Saad's evidence includes a `commit -a` incident. | **Medium to high.** | Use worktrees. If a project forbids extra folders (one of Saad's projects has that rule), **run sequentially**. #2245 got four lanes through one checkout with explicit-pathspec commits, but tests there can't be trusted. Use absolute paths in every lane command. | #2245 (item 4); #2674; private evidence |
| 8 | **The orchestrator becomes the serial bottleneck.** One controller handles 3 or 4 report streams, fix loops and merges. | Structural: every parallel run. | It caps speedup (Amdahl). It also bloats context: in one 15-task serial SDD run, coordinator context grew to 830k tokens. | Report files plus 15-line returns (SDD already does this). Hold the DAG state in a file, or in a workflow script. One integrator merges the queued branches together. | [#2612](https://github.com/obra/superpowers/issues/2612); CC workflows docs |
| 9 | **Review as the bottleneck.** | **Agent review: moderate.** Reviews took 5 to 20 minutes against 30 to 80 for implementers in an 8-task run, and agent reviews can run in parallel too. One fork measured that "reviews cost about twice what implementation did" (cost, not time). **Human review: high.** "The natural bottleneck on all of this is how fast I can review the results" (Willison). At 718 firms, agents added 30% more code, finished work didn't measurably rise, and review took 49% longer. | Late review shifts rework to the end. Saad's 66-agent run had 1 end audit, then about 20 fix agents, with 17 spec items still open. | **Keep the per-task review in each lane.** Add one integration review per merged batch. Saad's best session had per-task review, and the session without it had the late fix waves. | #2674; superpowers-fast README; Willison (Oct 2025); Chen and Stratton (coverage 2026-10); private evidence |
| 10 | **Test and dev-server contention:** ports, a shared DB, Docker Compose project names, a browser profile. | Common once lanes start servers or e2e. | **Medium.** A server dies on startup, or a flaky failure gets blamed on the code. | Lanes run **focused tests only**, with no dev server unless a setup script gives that lane its own port and DB. Browser and e2e checks run per merged batch. | #597; trigger.dev (2026-04-16); matrix-os; Conductor docs |
| 11 | **CPU and RAM on a Windows laptop.** | **Common at 4+ lanes.** Saad's evidence: "hitting my CPU and RAM like crazy" with 6 heavy jobs, one of them a test run spread over 12 worker processes. | **High.** The machine stalls, and so does everything on it. | Cap lanes at 3 by default. Cap test workers per lane (for example `-n 2` or `--maxWorkers=2`). Run one full suite at a time, never one per lane. **Facts:** a Windows CLI session is about 212 MB median (#96299); about 540 MB on macOS (#105268); **tsserver is about 2.3 GB per worktree, not shared** (#105268); about 20 sessions use about 20 GB. Inference: 3 lanes of Claude plus tsserver plus one test runner need about 8 to 12 GB free. | CC [#96299](https://github.com/anthropics/claude-code/issues/96299), [#105268](https://github.com/anthropics/claude-code/issues/105268), [#107433](https://github.com/anthropics/claude-code/issues/107433); private evidence |
| 12 | **Disk, install time and Windows paths.** | Every lane. | **Medium.** Two worktrees of a 2 GB repo took 9.82 GB. Each worktree needs its own install. Windows `Filename too long` makes `git worktree remove` fail and strand folders. | Use pnpm's shared store, `.worktreeinclude` for `.env`, `core.longpaths=true`, and a short worktree root. Clean up after each merge. | trigger.dev; [t3code #14917](https://github.com/pingdotgg/t3code/pull/14917) (2026-10-02); CC worktrees docs |
| 13 | **Tokens and usage limits.** | **Every run.** Saad: 13 limit hits; a 6-hit build happened both with and without per-task review. | The total rises modestly (inference: about 10 to 30% for integration and drift fixes), but the **burn rate is about N times**. When a build exceeds one window, the wall-clock gain is lost to waiting. The quoted 7x (agent teams in plan mode) and 15x (multi-agent vs chat) are against a *single chat*, not against SDD, which is already multi-agent. | State a budget in the plan. Use a cheaper model for mechanical lanes (SDD already does). Check that the plan fits the window before choosing parallel. Prefer runs that pause at the limit (workflows do). | CC costs docs; Anthropic multi-agent post; [#2612](https://github.com/obra/superpowers/issues/2612) ($154.83, 18.1 h, 5 limit stops); private evidence |
| 14 | **The orchestrator loses its place:** compaction, a "rejected" launch that actually ran, a lane that re-delegates and returns a promise, task status lag. | Occasional, but expensive. SDD calls re-dispatching completed tasks after compaction "the single most expensive failure observed". | **High.** Duplicate work stacked on unreviewed edits. | A state file is the only memory; write it after every transition. Inspect every worktree before you relaunch. Add a "terminal agent, don't delegate" line to every brief. | SDD `SKILL.md`; [#2691](https://github.com/obra/superpowers/issues/2691); [#2202](https://github.com/obra/superpowers/issues/2202); CC agent-teams limitations |
| 15 | **A usage limit kills lanes mid-flight**, leaving partial commits and no summary. | Seen in GSD and in Saad's session (it ended mid-wave with 2 lanes running). | **Medium.** Recovering from a stranded half-wave. | Use per-unit commits plus a "summary exists?" check before marking anything done. Never trust a `completed` status alone. Workflows pause at the limit (v2.1.271+). | [GSD #3095](https://github.com/gsd-build/get-shit-done/issues/3095); [#2696](https://github.com/obra/superpowers/issues/2696); CC workflows docs |
| 16 | **Shared tracking files overwritten:** progress, state or roadmap files that every lane updates. | Was the default bug in GSD's first worktree version. | **Medium.** Progress files drift from reality, which is exactly Saad's "can't see progress" complaint. | Only the orchestrator writes the ledger and progress file. Append-only decision logs use `merge=union`. | [GSD #1571](https://github.com/gsd-build/get-shit-done/issues/1571); #2599 |
| 17 | **Quality is lower than sequential where tasks interact.** A later sequential task sees earlier tasks' *real code*, while a parallel lane sees only the contract. A per-task reviewer sees one diff and can't spot cross-task contradictions. | Structural. | Shows up as items 4 and 5, plus later e2e defects. | Contracts as code, an integration review per batch, and the foundations audit. #2599's audit of the merged foundations found a privilege escalation "that two per-package reviews had missed". | #995; #2599; Cognition 2025-06-12 and 2026-04-22 |
| 18 | **Idle lanes behind barriers, and lane imbalance.** | Common with fixed waves. | #2599: "With wave barriers, finished packages sat idle for about 2.5h waiting on the slowest." The largest task sets the wall clock. | **DAG scheduling:** start a task the moment its dependencies have merged. Split big tasks. | #2599 |

---

## 3. When it pays, and when sequential is faster

### 3.1 A simple timing model (inference, with stated assumptions)

```
Sequential:  T_seq = Σ (I + R + F) over tasks  +  T_final
Parallel:    T_par = T_foundation
                   + Σ over batches of max(I + R + F) in the batch   ← slowest lane sets the pace
                   + Σ over batches of T_merge_and_full_suite        ← serial integrator
                   + T_drift_fix + T_final
I = implement, R = per-task review, F = fix loop
```

Worked example. Assume 12 tasks averaging I=40, R=10, F=10 minutes (in line with #2674's reported 30–80 / 5–20 ranges, scaled down), 3 lanes, a 20-minute merge and full suite per batch, and a 30-minute final review.

| Scenario | T_seq | T_par | Speed-up |
|---|---|---|---|
| Ideal: 12 equal, fully independent tasks, no foundation, no drift | 750 min | 4 batches × 60 + 4 × 20 + 30 = 350 | **2.1x** |
| Realistic: 1 foundation task, 11 in DAG, slowest lane 1.4× average, one drift-fix round of 30 | 750 | 60 + 4 × 84 + 4 × 20 + 30 + 30 = 536 | **1.4x** |
| Same, 4 lanes, DAG scheduling, merges overlapped with lane work | 750 | about 60 + 3 × 75 + 3 × 15 + 30 + 30 = 390 | **1.9x** |
| Chain-shaped plan (DAG width 1–2) | 750 | about 700 to 800 (overhead, no overlap) | **about 1x or worse** |

**Inference.** Getting 3 to 4 times needs at least 4 truly independent, similarly sized tasks in *every* batch, a small foundation and cheap merges. That shape is typical of multi-module greenfield work (the #2599 build: 26 packages overnight) or mechanical migrations (`/batch` targets 5 to 30 units). It isn't typical of one feature in an existing app. Kiro's "up to 4x" for "4+ independent tasks" is the same ceiling, stated as a promise.

### 3.2 It pays when

- **The dependency graph is wide.** At least 6 to 8 tasks, at least 3 of them ready at once after the foundations task (spec-kit: "Once Foundational phase completes, all user stories can start in parallel"). This assumes the shared surface is frozen first.
- **The shared surface is known before the build.** Contracts can be written as code in the foundations task. Brainstorm and spec already settled the names and shapes.
- **Implementation time dominates each task.** Long implementers (30 to 80 minutes) against short reviews (5 to 20 minutes) and a cheap merge. For 5-minute tasks, worktree setup, install, review and merge outweigh the gain; batch them instead (SDD `batching.md`).
- **Tasks are balanced.** The largest task sets the wall clock (#2599: "Split the big packages").
- **Per-lane environments are cheap:** no per-lane Postgres, Redis or ClickHouse, a fast install, focused tests that run in seconds.
- **The build fits one usage window**, or Saad accepts waiting for the reset.
- **The machine has headroom** for N lanes (row 11).
- **The workstreams are separate.** Practitioners agree that parallel pays most on "completely different tasks" and less on one feature split N ways (practitioner report §5).

### 3.3 Sequential is faster end to end when

- **The plan is a chain:** refactors where each step builds on the last, or redesigns that change contracts as they go.
- **Contracts are still uncertain**, so every lane would file change requests (#2599: about 200 of them before the fix).
- **The work is tightly coupled UI** (one view's markup, styles and script): the #995 failure.
- **The plan is small** (4 tasks or fewer), or its tasks are small.
- **Most of the work is in shared files**, so the foundations task absorbs most of it.
- **Per-lane environments are heavy.** Trigger.dev gave up on worktrees because each needed "its own PostgreSQL, Redis, ClickHouse, and Electric instance".
- **The build will hit a usage limit anyway.** Parallel only reaches the wait sooner.
- **The project forbids extra folders or worktrees** (one of Saad's projects has that rule).
- **A human must review every change before the next starts.** "Run only as many agents as you can review" ("You are the queue", Oct 2026).

### 3.4 Evidence against parallel build (consolidated)

- obra twice, in 2026-03, said it trades tokens for time "without actually improving correctness". He declined even review/implement overlap on 2026-11-10.
- Cognition (2025-06-12): "Actions carry implicit decisions, and conflicting decisions carry bad results." Their 2026-04-22 follow-up still holds that "parallel-writer swarms" don't see meaningful adoption. What works for them is **single-threaded writes plus parallel readers and reviewers**.
- Anthropic (old, 2025): "Most coding tasks involve fewer truly parallelizable tasks than research." Opus 5 guidance (2026) tells the model to delegate *less*.
- Carlini's 16-agent C compiler (2026-02-05) worked on thousands of independent failing tests. On one monolithic task (the kernel build), though, "every agent would hit the same bug, fix that bug, and then overwrite each other's changes", and the cost was about $20,000.
- Practitioners: "if I try doing 3+ things in parallel, I usually … don't see any improvement compared to just running two." Another: "four agents editing the same file and a merge disaster that eats every minute you 'saved'". Several dev.to reports from 2026 say the same.
- Saad's own evidence: the 66-agent run with one end audit produced the late fix waves and the "déjà vu". The per-task-review session didn't. Both hit the usage limit 6 times.

---

## 4. How others do it (late 2026)

### 4.1 Summary table

| Tool | How it plans for parallel | How it isolates | How it reviews | How it merges | What users report |
|---|---|---|---|---|---|
| **spec-kit** v1.4.2 | `[P]` = "different files, no dependencies on incomplete tasks". The Setup → Foundational ("BLOCKS all user stories") → per-story phases. "Tasks affecting the same files must run sequentially." | **None in core:** one working tree. The MAQA extension adds a worktree per feature. | `converge` checks the code against spec, plan and tasks after the build. There's no per-task gate. | Not covered in core. | #3068 (2026-06-19): the list is "mostly linear", and the maintainer said "use a preset". #4128 (2026-08-14): concurrent agents race on `.specify/feature.json`. |
| **Kiro** IDE 0.12+ | "Run all Tasks" builds a dependency graph and runs waves. The blog says tasks that touch the same files never run together, and tests run after the code they test. | "each running in its own isolated context". Workspace isolation isn't documented. | Property-based tests per task, LSP diagnostics, dev-server checks. | Not documented. | Claims "up to 4x" for 4+ independent tasks; anecdotal "a quarter of the time". Run-all was held back for months because the agent "would mess up". |
| **GSD Core** v1.21.0 | `depends_on` per plan, with wave = max(deps)+1. A `files_modified` overlap check. **Dimension 3b** flags same-wave pairs that share mutable state (a config key, DB table, migration, env var) unless the planner declares the edge, re-waves, or writes `coupling_justified`. | A git worktree per plan in the wave. A base check before each wave **auto-degrades to sequential** when the fork base is stale. Executors exit 42 on a base mismatch and never self-repair. | `gsd-verifier` after all waves, plus VERIFICATION.md, which goes stale on change. No per-plan review by default; parallel reviewer lanes are opt-in. | The orchestrator merges each wave. Executors commit `--no-verify`, and the pre-commit hook runs **once per wave** to avoid build-lock fights. `STATE.md` is written under an `O_EXCL` lock. | Bugs filed: same-wave write-set conflicts (#2892, 2026-04-30), shared planning files overwritten (#1571, 2026-04-03), a usage limit killing a wave (#3095, 2026-05-04), merges landing on the wrong branch (#3425, 2026-05-12), shared requirements never marked complete (gsd-core #6102, 2026-11-09). |
| **ccpm** | Per-issue "stream analysis": files per stream, `depends_on`, `parallel`, `conflicts_with`, shared files, a risk assessment. | **One worktree per epic.** Streams share it and are scoped by file patterns: "Work ONLY in your assigned files". | Through GitHub issue comments; no reviewer agent. | One epic merge at the end. | The README says 5 streams take "1x" wall time (marketing, not measured). It admits agents in one worktree "share one database unless you give each writer its own". |
| **Superpowers #2599** (build brief) | The lead writes the master plan alone. A contract registry where every entry names producer and consumers. A **foundations package first and alone**, then an adversarial audit. Disjoint `Owns`. DAG, not barriers. | A worktree plus its own services per package. | Two competing reviewers per package (spec+contracts, correctness+security), **capped at 2 rounds**. A gate critic compares the build to the spec. | **Merge train:** one integrator merges the queue in DAG order, regenerates lockfiles, and runs the full check **once per batch**, bisecting only when it's red. | It converged on a 26-package, about 100k-line overnight build. Full CI after every merge would have cost over an hour on an 8-package wave. |
| **Superpowers forks**: taylorelley/superagent, sampocs/superpowers-fast, omp-superpowers, nbl-superpowers, schlenks/superpowers-bd | A dependency table in the plan. Waves. A "one-writer-per-file rule": an overlap counts as a plan defect. | A worktree and branch per task, forked from the feature branch after its dependency waves merge. | **SDD's per-task review is kept** and runs on the exact range `base..<plan>/t<N>`. A 5-round fix breaker. | `merge --no-ff` after a clean review. "A merge conflict means the plan's claim of disjoint files was wrong". Waves become stacked PRs. nbl caps at 2 worktrees per batch. | All small (0 to 4 stars). No published measurements. superpowers-fast found reviews cost about 2x implementation. |
| **Claude Code `Agent` + `isolation: "worktree"`** | None; the caller plans. | A temporary worktree under `.claude/worktrees/`, branched from the **default branch** unless `worktree.baseRef: "head"`. Bash `cd` and git redirects into the main checkout are blocked; `cp` and shell redirects are not. Kept if changed, auto-removed if clean. | None built in. | Up to the caller. | Up to 20 concurrent subagents by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`). Background is the default. |
| **Claude Code agent teams** (experimental) | A shared task list with dependencies; file locking on *claims*. | **No worktree isolation:** "partition the work so each teammate owns a different set of files". | `TaskCompleted` hooks can gate completion. | Up to the lead. | "Start with 3-5 teammates." About 7x tokens in plan mode. No resume with in-process teammates. "Task status can lag". Issue #429: several forks adapt SDD to teams. |
| **Claude Code `/batch`** | Researches the codebase and splits **mechanical** changes into 5 to 30 units; the plan needs approval. | A background subagent per unit, each in its own worktree. | Each unit runs its own tests. | **One PR per unit.** | Built for migrations, not features. |
| **Claude Code dynamic workflows** | A script holds the DAG (`agent`, `parallel`, `pipeline`). | Per agent, if the script asks for isolated copies. | Cross-checking and adversarial patterns as code. | Up to the script. | Up to 16 concurrent agents by default, fewer on fewer CPUs. Resumable. **Pauses at the usage limit** (v2.1.271+). A "Large workflow" warning above 25 agents or 1.5M tokens. #2599 ran on this. |
| **Conductor** | None; per-task workspaces. | A worktree per workspace, tracked files only, a setup script. | A diff viewer plus a Checks tab. | A PR per workspace. | **macOS only**, so not an option on Saad's Windows machine. Reviewers note branches still conflict at merge. |
| **claude-squad** | None. | tmux plus a worktree per session. | Diff preview. | Commit and push per branch. | Terminal-only; needs tmux (WSL on Windows). |
| **Crystal → Nimbalyst** | None. | A worktree per session. | Compare sessions. | Per branch. | Crystal was deprecated in Feb 2026. |
| **GitButler** (trigger.dev's choice) | None. | **One directory with virtual branches**, no worktrees. | — | Per virtual branch. | "can definitely lead to problems related to races and interference" when files overlap. |

### 4.2 What they converge on (inference)

1. **Planning carries the parallelism.** Every tool that runs parallel safely gets independence from **declared metadata** written at plan time: `[P]`, `depends_on`, `files_modified`, `Owns`, `conflicts_with`. None infers it at run time. Tools that infer late (spec-kit's issue, Kiro's undocumented graph) show the gaps.
2. **Foundations first.** spec-kit's "Foundational phase BLOCKS all user stories", GSD's wave 1, and #2599's foundations package are the same idea.
3. **Isolation is a worktree per task.** The exceptions are ccpm (shared worktree, scoped by file), agent teams (no isolation) and GitButler. Each of them warns about races.
4. **Merging is serial even when building isn't.** This is the GSD per-wave hook, the #2599 merge train, the forks' `--no-ff` after review, and the practitioners' "merge one branch at a time".
5. **Review is where they differ.** Only the Superpowers lineage (#2599, the forks) keeps a review **per task**. GSD, Kiro and spec-kit verify per wave or at the end. Saad's evidence favours per-task review.

---

## 5. What the spec and plan must contain

Saad's point holds: **parallelism is decided at spec time.** A spec that doesn't name the shared surface can't be split safely later, because the plan has nothing to freeze.

### 5.1 In the spec

| Spec element | Why parallel needs it | Prior art |
|---|---|---|
| **Slices that can be tested independently** (user stories or modules), each with numbered lines (S1…) | Each slice becomes a lane candidate | spec-kit "independently testable" stories; `writing-plans` "break into sub-project specs" |
| **A shared-surface section:** every data shape, endpoint, event, route, config key, table and env var that more than one slice touches, with *exact names* | This is what goes stale fastest (row 4). Names chosen at spec time can't drift between lanes. | #2599 frozen core contracts; Saad's two field-name mismatches |
| **Operation per change:** add, extend, replace or remove | Prevents replace-vs-extend semantic conflicts | Foremerge |
| **Cross-cutting acceptance scenarios** that only work when the slices combine | Gives the integration test and review a target | #2599 §6 |
| **Global constraints** every lane must obey | Lanes don't share context, so it has to be stated | SDD Global Constraints |

### 5.2 In the plan

1. **Execution strategy, with a reason.** Parallel or sequential, lane count, expected speed-up and critical path, and *why* parallel ("separate modules, contracts pinned in T0"). Old Anvil's rule still applies: "Describing parallelism you never execute is the thing Anvil exists to prevent."
2. **Task 0, foundations.** It pre-creates every shared file: barrels, route registry entries, module declarations, DI registrations, manifest entries (with the lockfile updated once), migration files or reserved numbers, shared fixtures, and **the contracts as code**. It is reviewed, with an adversarial contract audit, before anything fans out.
3. **A task table**, one row per task:

   | Field | Example |
   |---|---|
   | ID, spec lines | T3 · S4, S7 |
   | Depends on | T0 |
   | **Owns (write set):** exact paths or globs, split into create, modify and delete | `src/billing/invoice/**`, `tests/billing/invoice/**` |
   | Reads | `src/contracts/billing.ts` |
   | Produces / Consumes (registry names) | produces `InvoiceService.create`, consumes `Money`, `CustomerId` |
   | **Shared resources touched**, with read or write | table `invoices` (W), config `billing.currency` (R) |
   | Operation | add |
   | Focused test command | `pnpm vitest run tests/billing/invoice` |
   | Size | M |

4. **Shared-file ownership.** List which files only T0 or the integrator may write: lockfiles, codegen, snapshots, route registry, changelog, ledger and progress files. Append-only logs get `merge=union`.
5. **A DAG with a lane cap**, not fixed waves. A task starts when its dependencies have *merged and been reviewed* (#2368's rule).
6. **An environment per lane:** base ref, setup script (install, `.env` via `.worktreeinclude`), port and DB name derived from the lane, test-worker cap.
7. **An integration plan:** merge order, who merges, the full suite once per batch on the merged tree (recorded against the tree hash under the §9 rule), an integration review, and the rule that a conflict means a plan defect.
8. **The stop rule:** "a file outside Owns means stop, report BLOCKED, don't reach across." Contract changes go through the orchestrator, which re-checks every consumer.
9. **A budget:** an expected token and usage estimate, and a fallback to sequential if it won't fit.

### 5.3 The mechanical "parallel-safe" check

All of this can be scripted over the task table. Inference: it should be a small deterministic script, not model judgement, per Anthropic's "prefer scripts for deterministic operations" and #2309's call for "a standalone deterministic linter".

| # | Check | Fails when | Source of the rule |
|---|---|---|---|
| C1 | The DAG is acyclic, and every `Depends on` ID exists | Cycle or dangling ID | GSD plan-checker |
| C2 | **Closure:** every consumed name is produced by T0 or by an ancestor task, never by a same-batch sibling | A consumer can run before its producer | #2309; #2599 registry |
| C3 | **Write sets are disjoint** across any two tasks that can run at once (not ancestor and descendant) | Owns globs intersect | spec-kit, GSD, forks |
| C4 | **No reserved files** in any lane's Owns (lockfiles, barrels, route registry, codegen, ledger) | A lane writes a reserved file | #2599 shared-file policy |
| C5 | **Shared mutable resources:** no two concurrent tasks touch the same table, migration, config key or env var with at least one writer, unless an edge or `coupling_justified` is declared | Undeclared state coupling | GSD Dimension 3b |
| C6 | A concurrent task doesn't **read** a file another concurrent task writes | A hidden dependency | inference |
| C7 | Every spec line is covered, and every task cites spec lines | A gap or untraced task | Anvil proposal §5 |
| C8 | Width is at most the lane cap, and the largest task is no more than about 2x the median | Imbalance warning (not a failure) | #2599 |
| C9 | Every task has a focused test command | A lane would need the full suite | §9 rule |
| **Post** | After each lane, `git diff --name-only base..branch` must be inside Owns | The lane reached outside its scope, so review rejects it | cc-sdd boundary compliance; superagent |

If C1 to C7 pass and the width allows at least 3 lanes, offer parallel at the plan stop. Otherwise the plan says "sequential" and names the reason.

---

## 6. Recommendation for Anvil

**Do it, as an opt-in strategy decided per plan, and keep Superpowers' quality loop intact inside every lane.**

1. **Execution strategy is chosen at the plan stop.** The plan runs §5.3. Parallel is offered only when C1 to C7 pass, there are at least 6 tasks, and at least 3 lanes can run at once. Otherwise the plan says sequential and names the failed check. Saad approves the choice at the plan stop he already has.
2. **Lane cap: 3 by default, 4 at most** on this Windows laptop. This follows rows 9 and 11, the 3–5 range in Anthropic's own docs, and the practitioners' "about 2–4".
3. **T0 foundations runs alone first.** Then comes an adversarial contract audit: a cheap reviewer checks the committed contracts against the spec's shared-surface section.
4. **Each lane is SDD as it is today:** an implementer, then the per-task spec and quality review on the exact range `base..branch`, then fix rounds resuming the same implementer, with the 5-round breaker. **Nothing is removed from the review**, because the evidence says that review is where the quality came from.
5. **Isolation is a worktree plus a branch per task, forked from the integration branch.** Either set `worktree.baseRef: "head"` or have the orchestrator create worktrees with `git worktree add` from the integration branch. Verify the base at lane start. If a project rule forbids extra folders, run sequentially. Don't try same-checkout parallel.
6. **Lanes run focused tests only**, with workers capped and no dev servers unless the lane's setup assigns a port and DB. Lanes never commit lockfiles or codegen.
7. **Merge train.** The orchestrator, or one integrator subagent, merges reviewed branches in DAG order with `--no-ff`, regenerates lockfiles and codegen, and runs the **full suite once per batch**. The result is recorded against the tree hash, so finishing reuses it under §9. A conflict counts as a plan defect and gets a ruling.
8. **An integration review per batch.** One cheap reviewer reads the merged batch diff against the contracts and the cross-cutting scenarios. It catches semantic conflicts, which per-task reviewers can't see. Browser and e2e checks run here, once.
9. **DAG scheduling:** a task starts when its dependencies have merged and been reviewed. No fixed wave barriers.
10. **The orchestrator's memory is a state file** written after every transition. Report files keep 15-line returns. Every brief says "terminal agent: never delegate". Inspect every worktree before relaunching anything. This maps onto Anvil's proposed live progress file (§5 of the notes).
11. **Budget line in the plan.** Estimate the build's usage. If it clearly won't fit one window, say so at the plan stop: parallel only reaches the limit sooner.
12. **Which Claude Code feature to use.** Start with **Agent tool dispatches with `isolation: "worktree"` in the background**, the primitive SDD already uses. Consider a **dynamic workflow** for the build phase later. It holds the DAG outside the orchestrator's context, it's resumable, and it pauses at usage limits, but it needs Claude Code v2.1.269 to v2.1.271+, and Saad is on 2.1.268 (notes §7). **Don't use agent teams**: they're experimental, give no worktree isolation, can't resume, and cost about 7x in plan mode.
13. **Pair it with the cheaper win.** The §9 "test result valid until the code changes" rule, plus SDD's existing batching of small same-shape tasks.
14. **Pilot before trusting it.** Run one real plan both ways, sequential and parallel, and record wall clock, tokens, limit hits, fix rounds, drift findings and final-review findings. Keep parallel as the offered option only if it is at least 1.5x faster on the build phase with **no rise in final-review or gate findings**. This is the same eval discipline Superpowers demands before changing SDD.

### Confidence

| Claim | Confidence | Why |
|---|---|---|
| Parallel build can be made safe enough with T0, disjoint Owns, worktrees from the right base, per-task review and a merge train | **Medium-high** | Six or more independent tools converge on the same design, and #2599 converged on a large real build. But Superpowers itself hasn't measured or adopted it, and no tool publishes a controlled comparison. |
| Anvil gets 3 to 4 times on the build phase for typical features | **Low** | Arithmetic (§3.1) plus reports point to 1.5 to 2.5x on suitable plans and about 1x on coupled ones. 3 to 4x needs wide, balanced graphs. |
| Parallel will reduce usage-limit hits | **Low (likely the opposite)** | Same total tokens or slightly more, burned faster. |
| Spec and plan must be written for parallel from the start (shared-surface section, Owns, T0) | **High** | Every working tool relies on plan-time metadata. Late inference produced the #2599 mismatches and the #995 failure. |
| Removing repeated full-suite runs is a bigger and cheaper speed win than going from 3 lanes to 4 | **Medium** | #2612: 53 suite runs, 165 minutes. Saad's own 20 → 40 → 60-minute example. But that is one public report plus Saad's own estimate. |

---

## 7. Open questions for Saad

1. Should a merged-batch browser and e2e check be part of every parallel build by default, or only when the spec has UI lines?
2. The project rule forbidding extra folders makes parallel impossible there. Keep it, and accept sequential for that project?
3. Should the pilot (item 14) run on a real client repo or on a fixture in this repo?

---

## 8. Sources (all dated)

**Superpowers (obra/superpowers)**
- Local v7.0.2 (2026-11-03): `skills/subagent-driven-development/SKILL.md`, `implementer-prompt.md`, `references/{preflight,batching}.md`, `skills/writing-plans/SKILL.md`, `skills/dispatching-parallel-agents/SKILL.md`, `RELEASE-NOTES.md`
- [#464](https://github.com/obra/superpowers/issues/464) swarm mode, obra's reply 2026-03-17
- [#945](https://github.com/obra/superpowers/issues/945) parallel not automatic, obra's reply 2026-03-27
- [#995](https://github.com/obra/superpowers/issues/995) parallel coupled frontend tasks, 2026-03-29 (triage 2026-08-18)
- [#597](https://github.com/obra/superpowers/issues/597) per-worktree environment isolation, 2026-03-02
- [#429](https://github.com/obra/superpowers/issues/429) agent teams support and forks, 2026-02-05 onward
- [PR #1117](https://github.com/obra/superpowers/pull/1117) (2026-04-10), [PR #1213](https://github.com/obra/superpowers/pull/1213) (2026-04-18), [PR #1524](https://github.com/obra/superpowers/pull/1524) (2026-05-12), [PR #1534](https://github.com/obra/superpowers/pull/1534) (2026-05-13); all closed 2026-09-26/27
- [#2202](https://github.com/obra/superpowers/issues/2202) re-delegating lane, 2026-08-25
- [#2245](https://github.com/obra/superpowers/issues/2245) four dispatch checks (base commit, pathspec commits), 2026-09-02
- [#2309](https://github.com/obra/superpowers/issues/2309) DAG closure in plans, 2026-09-17
- [#2368](https://github.com/obra/superpowers/issues/2368) opt-in DAG/wave SDD, 2026-09-22
- [#2599](https://github.com/obra/superpowers/issues/2599) parallel plan-and-build brief, 2026-10-22
- [#2612](https://github.com/obra/superpowers/issues/2612) 15-task SDD, 830k coordinator context, 53 suite runs, 2026-10-23
- [#2674](https://github.com/obra/superpowers/issues/2674) review/implement overlap, 2026-11-06 (reply 2026-11-10)
- [#2691](https://github.com/obra/superpowers/issues/2691) rejected launch already ran, 2026-11-12
- [#2696](https://github.com/obra/superpowers/issues/2696) per-unit commits, 2026-11-13

**Superpowers forks**
- [taylorelley/superagent](https://github.com/taylorelley/superagent): created 2026-08-13, pushed 2026-11-05
- [sampocs/superpowers-fast](https://github.com/sampocs/superpowers-fast): 2026-07-22 to 2026-09-17
- [schlenks/superpowers-bd](https://github.com/schlenks/superpowers-bd): pushed 2026-11-13
- [omp-superpowers](https://pi.dev/packages/@loneexile/omp-superpowers), [nbl-superpowers](https://skills.lc/icefrag/nbl-superpowers/icefrag-nbl-superpowers-skills-nbl-parallel-subagent-driven-development-skill-md): read 2026-11-18, publish dates not shown

**Claude Code docs** (live, read 2026-11-18)
- [Agent teams](https://code.claude.com/docs/en/agent-teams), [Subagents](https://code.claude.com/docs/en/sub-agents), [Worktrees](https://code.claude.com/docs/en/worktrees), [Run agents in parallel](https://code.claude.com/docs/en/agents), [Dynamic workflows](https://code.claude.com/docs/en/workflows), [Costs](https://code.claude.com/docs/en/costs), [Commands (`/batch`, `/simplify`, `/verify`)](https://code.claude.com/docs/en/commands)

**Claude Code issues**
- [#22427](https://github.com/anthropics/claude-code/issues/22427) (2026-02-01), [#63318](https://github.com/anthropics/claude-code/issues/63318) (2026-05-28), [#96299](https://github.com/anthropics/claude-code/issues/96299) Windows (2026-09-23), [#105268](https://github.com/anthropics/claude-code/issues/105268) (2026-10-26), [#107433](https://github.com/anthropics/claude-code/issues/107433) (2026-11-05)

**Other frameworks**
- spec-kit: `templates/tasks-template.md` and `templates/commands/{tasks,implement}.md` (main, v1.4.2 2026-11-17, read 2026-11-18); [#3068](https://github.com/github/spec-kit/issues/3068) (2026-06-19); [#4128](https://github.com/github/spec-kit/issues/4128) (2026-08-14); [MAQA #4233](https://github.com/github/spec-kit/issues/4233) (2026-08-20)
- Kiro: [IDE 0.12 changelog](https://kiro.dev/changelog/ide/0-12/) (2026-05-06); [Run all tasks blog](https://kiro.dev/blog/run-all-tasks/) (2026-01-16); [Specs docs](https://kiro.dev/docs/specs/) (read 2026-11-18)
- GSD Core (open-gsd/gsd-core, v1.21.0 2026-11-13): `docs/how-to/execute-a-phase.md`, `docs/explanation/multi-agent-orchestration.md`, `gsd-core/references/{planner-coupling,execute-phase-wave-guard}.md`, `agents/gsd-plan-checker.md`, `.out-of-scope/executor-self-repair-worktree-base.md` (2026-09-07); [#6102](https://github.com/open-gsd/gsd-core/issues/6102) (2026-11-09)
- GSD original (archived): [#1571](https://github.com/gsd-build/get-shit-done/issues/1571) (2026-04-03), [#2892](https://github.com/gsd-build/get-shit-done/issues/2892) (2026-04-30), [#3095](https://github.com/gsd-build/get-shit-done/issues/3095) (2026-05-04), [#3425](https://github.com/gsd-build/get-shit-done/issues/3425) (2026-05-12)
- ccpm: [README](https://github.com/automazeio/ccpm) and `skill/ccpm/references/execute.md` (pushed 2026-11-04)
- [claude-squad](https://github.com/smtg-ai/claude-squad) README (pushed 2026-11-13); [Crystal → Nimbalyst](https://github.com/stravu/crystal) (deprecated 2026-02)
- [Conductor docs](https://www.conductor.build/docs/concepts/parallel-agents) (read 2026-11-18); macOS-only per [vibecoding.app review](https://vibecoding.app/blog/conductor-review) (2026, exact date not shown)

**Reports and analysis**
- Anthropic, [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) (2026-02-05)
- Anthropic, multi-agent research system (2025, marked OLD in the round-1 guidance report)
- Cognition, [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) (2025-06-12) and "Multi-Agents: What's Actually Working" (2026-04-22, seen through search snippets, not fetched)
- Trigger.dev, [We ditched worktrees](https://trigger.dev/blog/parallel-agents-gitbutler) (2026-04-16)
- Foremerge / N. Woodhead, [What worktrees cannot see](https://dev.to/naw103/running-multiple-claude-code-agents-in-parallel-what-worktrees-cannot-see-4le7) (Oct 18; 2026 inferred; vendor)
- G. Anhaia, [You are the queue](https://dev.to/gabrielanhaia/five-parallel-coding-agents-wont-make-you-5x-faster-you-are-the-queue-4peo) (Oct 14; 2026 inferred)
- A. Osmani, [The Code Agent Orchestra](https://addyosmani.com/blog/code-agent-orchestra/) (2026-03-26; its numbers are unsourced)
- S. Willison, "Embracing the parallel coding agent lifestyle" ([HN](https://news.ycombinator.com/item?id=45489884), Oct 2025)
- Chen and Stratton (Harvard), "Artificial Intelligence in the Firm: Bottlenecks in Software Production". Seen through secondary coverage (for example [ComplexDiscovery](https://complexdiscovery.com/harvard-researchers-find-ai-coding-agents-shifted-the-bottleneck-to-code-review/), about 2026-10-10/12); the paper itself was not read.
- dev.to parallel-agent practitioner posts (2026; [4 agents without chaos](https://dev.to/yureki_lab/how-i-run-4-claude-code-agents-in-parallel-on-one-repo-without-chaos-5ejc)); matrix-os ports/DB guide (2026, date not shown)
- [t3code PR #14917](https://github.com/pingdotgg/t3code/pull/14917) Windows worktree long paths (2026-10-02)

**Round-1 reports in this folder** (2026-11-18): `2026-11-18-superpowers-inventory.md`, `2026-11-18-community-frameworks.md`, `2026-11-18-practitioner-sentiment.md`, `2026-11-18-anthropic-guidance.md`

**Private evidence** (`../private/2026-11-18-session-evidence.md`, gitignored), summarized generically here: a 66-agent build with 1 end audit, about 20 fix agents and 17 spec items still open; "stale base" 11 times; a `commit -a` that swept up sibling edits; a CPU and RAM overload with 6 heavy jobs and 12 test workers; 13 usage-limit hits across sessions; two field-name drift cases; a parallel-safe check that "turned up three file clashes" before the build; contract pinning that worked.
