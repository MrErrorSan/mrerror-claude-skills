# Test-run reuse: stop re-running a slow suite on unchanged code

- **Date:** 2026-11-18
- **Round:** research round 2, topic "avoiding repeated test runs" ([brainstorm notes §9](../2026-11-18-brainstorm-notes.md))
- **Question:** the proposed rule is *a test result stays valid until the code changes*. Where do the repeated runs come from, how do others avoid them, when is reuse unsafe, and what would a small cross-platform mechanism look like in a Claude Code plugin?
- **Method:** I read Superpowers 7.0.2 from the local plugin cache, the current Anvil `SKILL.md`, the round-1 reports and the private session evidence (counts only; nothing from client work is quoted). I used WebSearch and WebFetch for docs and posts, and `gh api` for repo, issue and release dates. I measured the proposed tree key on this repo, on this Windows machine, with Git Bash.
- **Labels:** **Fact** means it was read in a source or measured. **Inference** means it's my reading. Every web source is dated in [Sources](#sources).

## Summary

1. **Superpowers 7.0.2 already stopped its reviewers from re-running tests.** The reviewer and re-reviewer prompts forbid it. The redundant runs now come from three other places:
   - the implementer runs the **full suite before every task commit**;
   - `verification-before-completion` demands a run **"in this message"** before any claim, including "moving to next task";
   - `finishing-a-development-branch` **always** runs the full suite again, and again after a local merge, even when the tree is unchanged.
   
   None of them can know that the tree is unchanged, because nothing records which tree a run saw.
2. **Current Anvil cuts the per-agent runs on paper,** but keeps `verification-before-completion` "in full" and keeps `finishing-a-development-branch` "as written". Its own final validate is followed by Finishing's full run, then the merge run. It ships no hooks, so nothing enforces any of this. Its "implement only" brief reached only 26 of about 400 implementer briefs.
3. **Prior art for "key the result by tree" is old and simple.** mhagger/git-test and spotify/git-test both do it, from 2015 to 2017. Go and Bazel cache test results natively. In 2026, agent-focused tools converged on the same fix:
   - run targeted tests while working;
   - run the full suite once, on the final code;
   - reviewers read the recorded result and run nothing.
4. **A safe key is the tree hash plus what the tree can't see.** The tree is `git add -A` into a *temporary* index, then `git write-tree`, which covers tracked and untracked non-ignored files. Add a hash of the exact command and a small fingerprint of the environment: installed-dependency state, toolchain versions, declared gitignored inputs and an allowlist of env vars.
   - Reuse passes only. Never reuse a failure or a run during which the tree changed.
   - Measured: 0.39 s on this repo under Git Bash, and the real index is untouched.
5. **A hook can enforce part of it.**
   - Deterministic: a `PreToolUse` hook can skip a test command when a fresh green record already exists for this exact state, and it can gate `git commit` and `gh pr create`.
   - Only heuristic: claims in prose ("tests pass") can be caught only by a `Stop`, `SubagentStop` or `SubagentHandback` hook matching the text. That should be a nudge, not a wall.

---

## 1. Where the runs come from

### 1.1 Superpowers 7.0.2: every place a test run is triggered

Paths are relative to `~/.claude/plugins/cache/claude-plugins-official/superpowers/7.0.2/skills/`.

| # | Trigger | File:line | Scope | How often | Can the tree be unchanged since the previous run? |
|---|---|---|---|---|---|
| S1 | Baseline when a worktree is created: "Run tests to ensure workspace starts clean" | `using-git-worktrees/SKILL.md:121-127` | full | once per worktree | **Yes.** It's the base commit's tree, often already green in CI or a previous session |
| S2 | Implementer: "run the focused test for what you're changing; run the full suite once before committing" | `subagent-driven-development/implementer-prompt.md:47-48` (job list `:35-38`) | focused, then **full** | **every task** | No for the first run. Yes if the controller later runs again |
| S3 | TDD: "'Other tests' means the project's suite … run the project's test command … even when your task named only one test file" | `test-driven-development/SKILL.md:185-189` (added in #2110, `RELEASE-NOTES.md:188`) | **full** | every TDD cycle that ends a change | Reinforces S2 |
| S4 | Verification gate: "If you haven't run the verification command **in this message**, you cannot claim it passes"; "Execute the FULL command (fresh, complete)"; "Previous run" listed as not sufficient | `verification-before-completion/SKILL.md:20`, `:28`, `:42` | **full** | before *any* claim, including "Committing", "Moving to next task" and "Delegating to agents" (`:112-114`) | **Yes.** This is the main source of main-agent re-runs on a tree the implementer just tested |
| S5 | Fix loop: "re-runs the tests covering the amended code … a one-line fix does not need the whole suite" | `subagent-driven-development/references/fix-loop.md:36-42`, `implementer-prompt.md:121-126` | focused | every fix round | No, the code changed. But see the note on S2 |
| S6 | Task reviewer: "Do not re-run the suite to confirm their report" | `task-reviewer-prompt.md:73-82`, `:87-92`; re-review `re-review-prompt.md:64-72`; controller rule `SKILL.md:283-284` | none, or one focused test on a specific doubt | per review | n/a. **Already fixed** in 7.x (#2089, `RELEASE-NOTES.md:233`) |
| S7 | Final whole-branch reviewer checklist: "All tests passing?" | `requesting-code-review/code-reviewer.md:87` | ambiguous | once | **Yes.** A checklist item that reviewers can read as an order to run (inference; the jknofe case in §1.5 shows exactly this) |
| S8 | Final-review fix wave: ONE fix subagent, which follows the implementer contract | `references/final-review.md:18-21` | full (through S2 and S3) | once if there are findings | No, it's new code |
| S9 | Finishing Step 1: "Run the project's full test suite" | `finishing-a-development-branch/SKILL.md:14-16` | **full** | once | **Yes, almost always.** It's the same tree S2, S4 or S8 just ran on |
| S10 | Finishing Option 1: "Verify tests on merged result" | `finishing-a-development-branch/SKILL.md:98-99` | **full** | once per local merge | **Yes when the merge fast-forwards,** because the tree is identical. No for a real merge |
| S11 | `executing-plans` (the inline route): `task-done` runs the brief's test command per task; the final fix pass reruns "the whole suite" | `executing-plans/SKILL.md:226-229`, `:282`; anti-shortcut row `:314` | as briefed; full at the end | per task | Like S2 |
| S12 | `dispatching-parallel-agents`: "Run full test suite" after agents return | `dispatching-parallel-agents/SKILL.md:84`, `:166` | full | per fan-out | No, it's the integrated tree. Yes if a later step runs again |

**Fact.** Superpowers already states the principle and doesn't implement it. `finishing-a-development-branch/SKILL.md:216` says: "Run the suite on the tree you are about to integrate. A green run only proves the tree it ran on." Since no run records its tree, the only safe reading is "always run again".

**Fact.** `executing-plans/scripts/task-done:42-54` is a test-result recorder, the nearest thing Superpowers has. It runs the command, keeps the log and writes `tests: <command> → <last line>` with a commit range into the ledger. It's keyed by commit range, not tree, and nothing ever reads it back to skip a run.

**Inference: a worked count.** Take a 3-task SDD plan, a 20-minute suite, a final-review fix wave and Option 1 (merge locally). The minimum is:

| Step | Full runs |
|---|---|
| S1 baseline | 1 |
| S2 ×3 tasks | 3 |
| S8 fix wave | 1 |
| S9 finishing | 1 |
| S10 merge | 1 |
| **Total** | **7, about 2 h 20 min** |

S4 adds 0 to 3 more main-agent runs, depending on how literally the controller reads "in this message". Of those 7 to 10 runs:
- S9 is always a repeat on an unchanged tree;
- S10 is a repeat whenever the merge fast-forwards;
- S1 is a repeat when the base was already green;
- every S4 controller run is a repeat.

That's **3 to 6 runs (1 to 2 hours) spent on code that hadn't changed.** Saad's "20 → 40 → 60 minutes" is the S2 → S4 → S9 chain for a single task.

### 1.2 Current Anvil (`plugins/anvil/skills/anvil/SKILL.md`)

| Rule | Line | Effect on runs |
|---|---|---|
| `verification-before-completion`: "**Kept in full** — but as one pass at the end" | `:79` | Keeps S4's wording ("in this message", "fresh", "FULL"). "Fresh" is never defined, so the model reruns at every claim point after the end pass too. |
| "Every other Superpowers skill is kept exactly as written … `finishing-a-development-branch`" | `:83-86` | **S9 and S10 run after Anvil's own final full validate.** That's at least 2 extra full runs on a tree Anvil just verified. |
| Agents type-check only; "Agents never run a test suite"; orchestrator runs the narrowest suite, then "full validate once" | `:252-260` | Correct in intent: one full run. |
| Brief text "Implement only … do not run any test suite" | `:275-279` | **Fact** (private session evidence): it appears in only 26 of about 400 implementer briefs. Elsewhere implementers wrote and ran their own tests (8/9, 16/18 and 22/23 briefs in three sessions). In practice S2 still happens. |
| "Fresh verification evidence before any done/passing claim" | `:299-301` | "Fresh" again undefined. It reads as "rerun now". |
| Early exception for unknown blast radius | `:262-264` | Reasonable. It's one extra run where it buys something. |
| Plugin contents | `plugins/anvil/` has `skills/` only | **No hooks.** Nothing records a run, so nothing can prove a later run is redundant. |

**Fact** (private session evidence): the most frequent frustration was long, opaque waits, about 30 "done?" pings across 12 sessions. One answer was a 2,900-test final suite running 28 to 35 minutes, and another was full backend and migration suites still running when Saad wanted to merge and sleep.

**Inference.** Anvil's end-loaded single run is the right count. It became a long blocking wait because Finishing then added more runs and nothing let the end run be reused.

### 1.3 Runs added by the project: pre-commit, husky, lint-staged, pre-push

These run *outside* the agent's instructions, so no skill wording removes them.

- **Every agent `git commit` fires the project's pre-commit hook.** SDD commits at least once per task (`implementer-prompt.md:38`) and once per fix round (`fix-loop.md:54` records "commits <a7>..<b7>" per round).
  - Inference: Claude Code's built-in git guidance tells the model not to bypass hooks (`--no-verify`) unless asked, and Anvil shouldn't change that.
- **Typical husky and lint-staged setups:**
  - `jest --bail --findRelatedTests` or `vitest related` on staged files: a focused run per commit. Fact: this is the common recipe (2025 DEV guide; planar-nexus PR #1668).
  - Some projects run the full `npm test` in pre-commit. That's a full run per commit.
  - The common advice is "related tests in pre-commit, full suite in pre-push or CI". The same guide says pre-commit tests only make sense for suites under about 10 s.
- **pre-push:** Finishing Option 2 pushes. A pre-push hook that runs the full suite adds one more full run on the tree S9 just tested. Then CI runs it again, which is outside the agent's control.
- **Count formula (inference):**
  - full runs = agent runs (§1.1) + `commits × [pre-commit runs full]` + `pushes × [pre-push runs full]`;
  - focused runs = `commits × [lint-staged related tests]`.
  
  For the 3-task plan, a full-suite pre-commit adds at least 4 to 5 more full runs: 3 task commits, fix commits and the fix-wave commit.
- **The overlap:** the pre-commit hook re-tests the *staged* tree. In the agent's flow, that's usually the exact working-tree state the implementer tested seconds earlier.
- **Gotcha** (fact, kamp-us/phoenix #7995, 2026-09-05): inside a git hook, `GIT_DIR` is set. `vitest --changed` then stopped applying the root `.gitignore` and treated thousands of ignored files as changed, so every push ran everything. Affected-test commands behave differently inside hooks.

### 1.4 What other agent projects found (late 2026)

These are independent confirmations that the problem is **who runs** and **what's recorded**, not tests as such.

- **jknofe/llm-agent-framework PR #14** (merged 2026-11-11). On one task with a 4-minute suite, the worker ran the full suite 34 times and one reviewer ran it 10 times, about an hour between them. Two reviewer runs hit the 10-minute tool timeout.
  - The fix: targeted tests while iterating, then the full suite once on the final code ("a green CI run on the last push counts as that run").
  - Review "runs no test, lint, build or code". The supervisor doesn't rerun either; a missing result goes back to the worker.
  - The reviewer's checklist item "tested" had been read "as an order to rerun". Compare S7.
- **JPHutchins/code-review #315** (2026-10-24): the main agent never reran, but subagents ran the whole suite 9 times in 4 of 7 review rounds, because the "CI passed" rule reached only the main agent. Handing every subagent the same trusted result line brought it to 0 whole-suite runs.
- **aganesy/QFAI #3695** (2026-10-13): a reviewer started test files in the background while the session ran its own full gate. It cost about 200k tokens, minutes of wall time and false failures from the concurrent load, all for a copy change. The fix: reviewers read gate results and run no suites.
- **letrquan/book #236** (2026-09-23): "Agent over-verifies: reruns the full unit suite instead of targeted tests."
- **Hu et al., arXiv 2609.30725** (v1 2026-09-25): *test re-execution* is one of three cost-inefficient behaviours that together affect 79 to 98% of tasks and up to 22.75% of task cost. Developer-written skills were the most effective mitigation, cutting cost by up to 41.73%. One stated cause of reruns is "test-signal recovery": output that is truncated or poorly captured makes the agent run again to see it.
  - **Inference:** a recorded log that later steps can read removes that motive.
- **Anthropic's Opus 5 prompting guide** (round-1 report, §3.3): explicit verification instructions and "legacy harness scaffolding that adds separate verification steps" cause over-verification. S4 is exactly such scaffolding.

---

## 2. Techniques survey

| Technique | How it works | Maturity (Nov 2026) | Suits | Gives Anvil |
|---|---|---|---|---|
| **A. Result cache keyed by tree** | Hash the tested content, store pass or fail under (tree, test-id), skip when the same pair is asked again | Old and proven in small tools. git-test (mhagger, 2017, last push 2025-03); spotify/git-test (2015, archived). Agent-era versions are young or retired. | Any stack. It's runner-agnostic | **The core mechanism** |
| **B. Verdicts go stale** (GSD Core) | A verification report records a digest of the files it covered. Any change flips it to `stale` | In production in a very active repo, with a long tail of bugs (§2B) | Spec, plan and review verdicts as well as tests | The same idea one level up: reviews and spec checks |
| **C. Runner-native result caches** | The build or test tool hashes declared inputs and replays the stored result | Very mature: Go `go test`, Bazel, Gradle, Nx, Turborepo | Go, monorepos, JVM, Bazel shops | Use when present. Don't duplicate them |
| **D. Affected-test selection** | Map changed files to the tests that depend on them (import graph or coverage) | Mature, with known holes (dynamic imports, non-code files) | JS/TS (jest, vitest), Python (testmon), monorepos (Nx) | **The "rerun only what's affected" half of the rule** |
| **E. Fast and slow split** | A fast lane while working, the slow lane once at a gate | Universal practice | Everything | The plan's test strategy names both lanes |
| **F. Claude Code hooks that record or gate** | PostToolUse, Stop and PreToolUse scripts log changes, run checks and block finishing | Many blog-level implementations in 2026, no standard | Claude Code | The enforcement layer |
| **G. One owner of test execution** | Only the worker (or only the orchestrator) runs tests; everyone else reads the record | Converged practice in late-2026 agent frameworks | Multi-agent flows | **The policy half of the rule** |

### A. Result cache keyed by tree hash

- **Fact:** mhagger/git-test saves pass/fail results "permanently in the repository as Git notes". It "reports the old results instead of testing it again". Results are recorded **by tree, not commit**, so they survive rebases. It recommends running in a linked worktree, which shares results across worktrees.
- **Fact:** spotify/git-test keys the cache on (tree, test). It hashes the test command with `git hash-object` so unit and integration results don't mix, and it skips trees it has already tested.
- **Fact:** Reachpad/greentree is the most complete design, and it's **retired**. Created 2026-08-12, archived around 2026-09-27; the README says "Do not install it or configure it in agent environments", with no reason given. Linux and macOS only. Its design is still instructive:
  - key = `(tree, check, command hash, environment fingerprint)`;
  - the dirty tree is captured through a **persistent shadow index** (`git add -A`, then `git write-tree`), so the real index is never touched, and untracked non-ignored files are included;
  - `inputs:` lists gitignored files (for example `.env` or a lockfile) that are hashed into the key, so a cache miss names the file responsible;
  - "Timeouts, infrastructure errors, and runs during which the tree changed are never cached";
  - it admits that "undeclared environment (toolchain versions, system libraries) is not in the verdict key";
  - `greentree publish` exits non-zero unless the tree has a fresh green verdict for every required check.
- **Fact:** berlinguyinca/pi-engineering #149 and PR #264 (merged 2026-10-20) add a "fingerprinted test result cache":
  - fingerprint = sha256 over tree hash, lockfile hashes, toolchain version, stage command, an env allowlist and the base SHA;
  - a changed base SHA alone is a miss ("no reuse across a changed base without integration proof");
  - "Cache stores pass results only; a failure is always re-run";
  - a bot noted that **nothing consults the cache yet**: wiring it into the gate was left for human review "because a cached pass could skip a real test in the gate".
- **Maturity (inference):** the idea is a decade old and trivially correct for hermetic tests. Every agent-era attempt stalls at the same two places: the environment fingerprint, and the fear of a wrong skip at the final gate. Anvil can avoid most of that fear by **always running the full suite once on the final tree** (unless that exact key is already green) and using the cache only to cut repeats.

### B. "Verdicts go stale" (GSD Core)

- **Fact:** each `*-VERIFICATION.md` stores `covered_files` and a `covered_digest`. Status is recomputed, and any change to a covered file reads as `stale` (round-1 community-frameworks report §GSD).
- **Fact: the bug history shows what goes wrong.**
  - **#4857** (2026-09-18): a report listed itself in `covered_files`, so it was *permanently* stale.
  - **#4697** (2026-09-13): several phases covered the shared `ROADMAP.md`, `REQUIREMENTS.md` and `AGENTS.md`, so finishing phase 18 flipped phases 16 and 17 to stale.
  - **#4682**: the stale route pointed to a command that never regenerated the report, so it looped.
  - **Epic #4907** (2026-09-21 to 2026-09-27): "verification is a pure function of inputs it does not contain, and stale has exactly one owner with a recovery path". PR #5103 (2026-09-28) made the fingerprint's input set "closed and idempotent".
- **Lessons for Anvil (inference):**
  1. The record must live **outside** the content it fingerprints, or writing it invalidates itself. For a tree key, that means outside the working tree, for example under `.git/`.
  2. Over-broad inputs cause false staleness, which trains the model to ignore "stale".
  3. Every "stale" or "no record" answer must name the **one** command that fixes it.

### C. Runner-native result caches

- **Go (fact):**
  - in package-list mode, `go test` "caches successful package test results to avoid unnecessary repeated running of tests";
  - tests that open files in the module or read env vars "only match future runs" where those are unchanged;
  - `(cached)` replaces the elapsed time, and `-count=1` is the idiom for disabling it.
  - **Inference:** a Go project already has the rule. Anvil's job there is only to stop agents passing `-count=1` out of habit.
- **Bazel (fact):** under `--cache_test_results=auto` (the default), Bazel reruns a test only if the test or its dependencies changed, it's tagged `external`, `--runs_per_test` was given, or it failed. The `external` tag forces unconditional execution. `flaky = True` retries up to 3 times.
  - **Inference:** Bazel's caveat is the general one. A test that reads the network, clock or an undeclared file gets a stale green forever, hence `external`.
- **Gradle 9.9.1 (fact):** `Test` is a built-in cacheable task. The key includes task type, classpath, declared inputs and plugin classpaths. Gradle "won't cache a task whose inputs and outputs aren't fully declared".
- **Nx 24 (fact):** affected detection is task-level: "Nx selects a task when your change touches one of its inputs". Remote cache replays tasks whose inputs are unchanged, and `nx affected` takes `--base`, `--head`, `--files`, `--uncommitted` and `--untracked`.
- **Turborepo 2.11 (fact):** a global hash (lockfile, `globalDependencies`, `globalEnv`, flags) plus a task hash (the package's source-controlled files or `inputs`, its `package.json` and lockfile slice). It replays logs from the first run.
  - Inference: untracked files are excluded by default ("source-controlled files").
- **Suits:** Go, Bazel, Gradle and Nx/Turborepo monorepos. Plain jest, vitest, pytest, cargo and dotnet projects have no result cache, and that's where Anvil's own record matters.

### D. Test impact analysis and affected-test selection

- **Jest 30.5 (fact):**
  - `--onlyChanged`/`-o` "requires a static dependency graph (ie. no dynamic requires)";
  - `--changedSince <ref>`, `--lastCommit`;
  - `--findRelatedTests <files>`, "useful for pre-commit hook integration";
  - `--listTests` shows the selection without running it, and `--passWithNoTests` exists.
- **Vitest 5.1 (fact):**
  - `vitest related <files>` works with static imports, "but not the dynamic ones (e.g., `import(filepath)`)";
  - `--changed` with no value covers uncommitted staged and unstaged changes; `--changed HEAD~1` or `origin/main` is relative to a ref;
  - `forceRerunTriggers` (default `package.json`, `vitest.config.*`, `vite.config.*`) forces the whole suite when matched in the diff. Its docs example is tests that run `dist/index.js` through a CLI, which the module graph can't see.
  - **Trap** (Myceliq/quality-kit #38, 2026-09-19): bare `vitest run --changed` "collects zero tests once work is committed, and exits 0". **A green with zero tests is not evidence.**
- **pytest-testmon 2.3.0 (fact; released 2026-11-02, development resumed 2026-10-26):**
  - collects dependencies between tests and executed code through Coverage.py, in `.testmondata`;
  - "works independently of version control";
  - tracks Python version, package versions and env vars (`run_variant_expression`, `--testmon-env`);
  - does **not** track "static files (txt, xml, other project assets)" or network services;
  - failed tests always rerun;
  - v2.3.0 fixed "the git sha calculation for cache hits in some edge cases".
- **Maturity (inference):** good enough for the *while-working* lane. Not trustworthy as the *final* gate, because every tool lists blind spots: dynamic imports, data files, CLI-spawned code, config. That's why the rule says "the full suite runs once, on the final state".

### E. Fast and slow lanes

- **Fact:** Anthropic's C-compiler write-up (round-1 report §4.3) used a default `--fast` that ran "a random 1% or 10% sample". It notes agents "can't tell time and would spend hours on test runs" and wants a few lines of output, with details in log files.
- **Fact:** Joxo (updated 2026-10-29) says to point turn-end hooks "at a quick check … and leave the slow suite for later". Common git-hook practice is related tests in pre-commit and the full suite in pre-push or CI (§1.3).
- **Suits:** everything. **Inference:** the plan's test strategy (notes §3.3) should name, per project:
  - the **focused** command, which takes files;
  - the **full** command;
  - optionally a **smoke** command;
  - which stage runs which.

### F. Claude Code hooks that record test results

- **Fact** (hooks reference, current page; it mentions Claude Code up to v2.1.314). These are the pieces a mechanism can use:
  - `PreToolUse` on `Bash` receives `tool_input.command`, `cwd`, `session_id`, `tool_use_id`, and `agent_id`/`agent_type` when fired inside a subagent. It can `deny` with `permissionDecisionReason`, or `allow` with `updatedInput`, which "replaces the entire input object". It can also add `additionalContext`.
  - `if` takes one permission rule such as `Bash(git commit *)`. It checks each subcommand and strips leading `VAR=value`. It is "best-effort", and hard enforcement belongs in permissions.
  - **`PostToolUse` for Bash returns `stdout`, `stderr`, `interrupted` and `isImage`, with no exit-code field.** A non-zero exit goes to `PostToolUseFailure`, whose `error` starts with `Exit code N`. The docs don't say when or whether `PostToolUse` fires for a `run_in_background` command.
  - `Stop` and `SubagentStop` can block (`decision: "block"`, or exit 2), and they get `last_assistant_message` and `stop_hook_active`. There's an **8-consecutive-continuation cap** (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`).
  - On v2.1.271+, a subagent's report goes through `SubagentHandback`, and a `PreToolUse` hook matched on it sees the report as `tool_input.message`.
  - Plugin hooks also fire inside subagents.
  - Windows: hooks default to Git Bash when it's installed. The exec form can't spawn `.cmd` shims. `CLAUDE_CODE_GIT_BASH_PATH` overrides discovery.
  - The default command timeout is 600 s.
- **Fact: community implementations.**
  - **Zenn, nonchan7720 (2026-08-11):**
    - a PostToolUse recorder logs edited files per session;
    - a Stop gate runs the checks whose globs match those files and retries only the ones that failed;
    - it runs "one more final pass … only when everything is green", so stale passes can't slip through;
    - it warns that session IDs isolate only the logs: "all sessions test the same working tree";
    - its process-group kill doesn't work on Windows.
  - **Joxo (updated 2026-10-29):**
    - a Stop hook that exits 2 on failure;
    - skip with `git diff --quiet && git diff --cached --quiet && exit 0`, but "leave this out if your agent commits as it goes";
    - check `stop_hook_active`, and keep output to `tail -20`.
    - **Inference:** "no diff" is a poor proxy for "unchanged since the last green run". A tree key fixes exactly the commit-as-you-go case it warns about.
  - **melodic-software/claude-code-plugins PR #6308 (2026-10-04):** skips test files git reports unchanged from HEAD. A reviewer found the hole: a test edited *and* committed in the same Bash call also got skipped. **Inference:** compare against the last tested tree, not HEAD.
  - **rjtenyks PR #4:** a stale `.pyc` can be reused when an edit keeps the file size within the same second. Each hook run got an empty `PYTHONPYCACHEPREFIX`. **Inference:** a reminder that build caches inside the run can lie even when the key is right.
- **Maturity:** no standard plugin exists. I found no published Claude Code plugin that keys test results by tree and skips reruns. **Inference:** Anvil would be early, but every piece it needs is documented.

### G. One agent owns test execution

- **Fact:** this is where late-2026 agent frameworks converged (jknofe #14, JPHutchins #315, QFAI #3695). Superpowers 7.x does it for reviewers (S6). Anthropic's Opus 5 guidance says "do not use subagents to verify or double-check your own work".
- **Fact** (jknofe #14): the named risk is that without CI, "the one full run is only the worker's recorded result line, and nobody reruns it". Their answer is a turn-end test hook for projects that need a deterministic check.
- **Inference:** ownership rules are prompt text, and Anvil's own brief reached 26 of about 400 dispatches. Ownership needs the record **and** a hook. Then a reviewer that does try to rerun gets "already green on this exact state" back instead of a 20-minute run.

---

## 3. Safety: when reuse is unsafe, and the key

### 3.1 When reusing a green result is wrong

| Case | Why the tree hash misses it | Rule |
|---|---|---|
| **Dependencies installed differently** (lockfile changed by a merge or pull but `npm install`/`pip install` not rerun, or a different `node_modules` per worktree) | The lockfile is in the tree, but the *installed* state isn't | Hash an installed-state marker: `node_modules/.package-lock.json` (npm), `.pnpm/lock.yaml` or `node_modules/.modules.yaml` (pnpm), the venv's `pyvenv.cfg` plus `pip freeze` output (Python). Configurable |
| **Toolchain change** (Node, Python, JDK, Go, compiler upgrade) | Not in the tree | Hash the output of configured `--version` commands (greentree's admitted gap; pi-engineering includes it) |
| **Gitignored inputs** (`.env`, local config, generated code that's gitignored, fixtures downloaded at setup) | `git add -A` skips ignored files | Declared `inputs:` list hashed per file (greentree). Generated sources that tests import should either be committed or listed here |
| **Untracked files** | Included by the temp-index method (non-ignored only) | Fine. A commit that leaves an untracked file out gets a different key, which is correctly a miss |
| **Config outside the tree** (`~/.npmrc`, global git config, user-level pytest or jest config, OS env vars such as `TZ`, `LANG`, `NODE_ENV`, `DATABASE_URL`) | Not in the tree | Env-var allowlist, hashed (never stored in clear). Undeclared global config stays a known gap; the max-age backstop covers it |
| **Non-hermetic tests** (network, live DB or schema, Docker images, clock or date, random seeds, external services) | Their outcome isn't a function of any key | Mark those commands `external`: never reused (Bazel's `external` tag). E2E against running services belongs here |
| **Flaky tests** | A lucky green is reused instead of re-rolled | Reusing a green adds no flake risk beyond the original run, but it doesn't re-roll the dice. Never reuse a failure; always rerun it. Record "passed after retry" (jest `retryTimes`, pytest-rerunfailures) so the summary says flaky |
| **Tree changed during the run** (parallel agent in the same worktree, editor autosave, the test writing files) | The record would claim a state it didn't fully see | Compute the tree before and after. If they differ, **don't record** (greentree). Parallel agents use separate worktrees |
| **Tests that write tracked files** (snapshot updates, golden files) | Tree after ≠ tree before | Same rule. This also catches `-u` snapshot rewrites |
| **Zero tests ran** (vitest `--changed` on a clean tree, an empty `related` selection, `--passWithNoTests`) | Exit 0 with nothing tested | Parse the count. **A green with 0 tests is not evidence** and never satisfies a gate |
| **Different command or scope** (`vitest related a.ts` vs `npm test`, extra flags, a different shard) | A different question | The command hash is part of the key. A *full* green satisfies a *focused* query on the same key; never the reverse |
| **Merge or rebase** | New tree | A miss, which is correct. Exception: a fast-forward has the identical tree, so it's a correct hit |
| **Submodules** | The superproject records the submodule commit, not dirty submodule contents | Include `git submodule status` output in the env hash, or declare submodules unsupported |
| **Line-ending normalisation** (`core.autocrlf` on Windows) | The same files can hash differently on two machines | Records are local (under `.git/`), never synced. Reuse across machines isn't a goal |
| **Timeouts, crashes, killed runs, the 10-minute Bash tool timeout** | Not a verdict | Never record (greentree) |
| **The agent forges a record** | Records are plain files | Only the wrapper writes them. Optionally add a permission deny on writes to the record directory |

### 3.2 The key

**Inference.** This is the simplest key that covers the table:

```
tree    = git write-tree of a temp index built by "git add -A"
          (a copy of the real index, so stat info makes it fast)
cmd     = hash(normalised command string)
env     = hash( lines of: each configured "<tool> --version" output,
                each declared input file's blob hash (or "absent"),
                each allowlisted env var as NAME=hash(value),
                installed-dependency marker hashes,
                git submodule status )
key     = git hash-object --stdin of "anvil-verify v1\n" + tree + cmd + env
```

- **Fact (measured):** on this repo, Git 2.55 on Windows under Git Bash, it ran as `cp <index> $tmp; GIT_INDEX_FILE=$tmp git add -A; GIT_INDEX_FILE=$tmp git write-tree`.
  - Wall time: **0.39 s**.
  - The real index's `git write-tree` was identical before and after (`a916a75…`), so the user's staging is untouched.
  - It includes the untracked `CLAUDE.md` and `docs/superpowers/` (tree `af27b55…` ≠ `a916a75…`).
  - Git printed LF→CRLF warnings; pass `-c core.safecrlf=false` and silence stderr.
- **Inference:** `git hash-object --stdin` gives a stable hash with only git, so there's no dependency on `sha256sum`, `jq`, Python or Node. That matters on Windows.
- **Inference: why not just HEAD.** HEAD misses uncommitted work. It changes on a commit that changes nothing (a rebase or reword). It misses the edit-and-commit-in-one-call case melodic #6308 hit. Trees fix all three, which is why git-test keys by tree.

### 3.3 Reuse rules

1. Reuse only `exit 0` with `tests_run > 0` (or a count the runner can't report, marked `count: unknown`).
2. Never reuse a failure, a timeout, a crash or an interrupted run. Never record a run whose before and after trees differ.
3. A **full** green satisfies **focused** and **full** queries for the same tree and env. A **focused** green satisfies only the identical focused command.
4. `external` commands are never reused.
5. **Max age** (default 24 h, configurable) as a backstop for undeclared environment drift. Inference: within one working session, drift is rare. Across days it's not (OS updates, toolchain auto-updates).
6. **Escape hatch:** `ANVIL_RERUN=1 <cmd>` always runs. The skill tells agents to use it only for a stated, specific doubt, which is the same bar Superpowers' reviewer prompt sets (`task-reviewer-prompt.md:77-79`).
7. **The full suite still runs once, on the final tree, unless that exact key is already green.** The cache removes repeats. It never replaces the final run with a selection.

---

## 4. Proposed mechanism for Anvil (sketch, not finished code)

### 4.1 Pieces

```
plugins/anvil/
  bin/anvil-verify            # bash + git only; the recorder and the oracle
  hooks/hooks.json            # PreToolUse(Bash) dedupe, PreToolUse(commit/PR) gate,
                              # SubagentHandback/Stop nudge
  hooks/run-hook.cmd          # polyglot wrapper (pattern from Superpowers, MIT, credited)
project: .claude/anvil-verify.json   # per-project commands and inputs (committed, so it is in the tree)
records: $(git rev-parse --git-common-dir)/anvil-verify/<key>.json  + <key>.log
```

- **Inference: why records live in the git common dir.**
  - They're outside the working tree, so writing a record can't change the tree it describes (GSD's #4857 lesson).
  - They're shared by every linked worktree, so a fast-forward merge in the main checkout reuses the green run from the feature worktree.
  - `git clean -fdx` doesn't touch them, they're never committed, and they're local to the machine (§3.1, line endings).
- **Alternative:** `${CLAUDE_PLUGIN_DATA}/<repo-id>/`. That survives deleting the repo, but it's per-user rather than per-repo and harder to inspect. I'd pick `.git/`.

### 4.2 Project config (example)

```json
{
  "full":     "npm test",
  "focused":  "npx vitest related --run {files}",
  "smoke":    "npm run test:smoke",
  "external": ["npm run e2e"],
  "tools":    ["node --version", "npm --version"],
  "inputs":   [".env.test", "node_modules/.package-lock.json"],
  "env":      ["NODE_ENV", "TZ", "DATABASE_URL"],
  "noTestPaths": ["docs/**", "**/*.md"],
  "maxAgeHours": 24
}
```

- **Inference:** the plan's test strategy (notes §3.3) writes or confirms this file once per project.
- `noTestPaths` is how "valid until the **code** changes" stays literal. If every path changed since the last green tree matches it (`git diff-tree -r --name-only <green-tree> <current-tree>`), the green still counts. Without it, a README edit would force a 20-minute run.

### 4.3 `anvil-verify` interface

```
anvil-verify run [--scope full|focused|smoke] -- <command...>
    key_before = key(); run the command with output to <key>.log;
    key_after = key(); if before != after: print "tree changed during run; not recorded"
    else write <key>.json atomically (write tmp, then mv):
      { v, key, tree, cmd, cmd_hash, env_hash, scope, exit, tests_run,
        started, finished, duration_s, summary (last ~5 lines / parsed counts),
        log, session_id, agent_id }
    print a 3-line summary + log path; exit with the command's code

anvil-verify check [--scope full|focused] [--cmd <command>]
    exit 0 + one line "GREEN <scope> <cmd> on tree <t7> at <time> (<summary>)"  if a fresh record exists
    exit 1 + one line naming the exact command to run                            otherwise

anvil-verify show [<key>|latest]      # print record + log tail (for reviewers)
anvil-verify files-since-green        # changed + untracked paths since the last full green
                                       # (feeds the focused command's {files})
```

- **Inference:** the output stays at a few lines, with details in the log file. That follows Anthropic's C-compiler advice and removes the "test-signal recovery" motive for reruns (arXiv 2609.30725).

### 4.4 Hooks

**H1. Dedupe: `PreToolUse`, matcher `Bash` (deterministic).**
- Read stdin. Find the command, either with `grep -o '"command":"[^"]*"'` (no jq on stock Git Bash) or with `node -e` when it's on PATH.
- If the command matches a configured `full`, `focused` or `smoke` command, isn't `external`, isn't already `anvil-verify …`, and lacks `ANVIL_RERUN=1`, it calls `anvil-verify check`.
  - **Green:** `permissionDecision: "deny"` with a factual reason: *"This exact code state (tree 3f2a9c1, same dependencies and env) already passed `npm test` at 14:02, 1,912 tests, 19 m 40 s. Log: <path>. The code has not changed since. To rerun for a specific doubt, prefix ANVIL_RERUN=1."* (Facts, not commands, per the hooks doc's prompt-injection note.)
  - **No record:** `allow` with `updatedInput` rewriting the command to `anvil-verify run --scope <s> -- <original>`. Keep `description`, `timeout` and `run_in_background`, because `updatedInput` replaces the whole object. The run is then recorded without the model having to remember to use the wrapper.
- It works the same inside subagents (plugin hooks fire there, with `agent_id`). That's what makes "the reviewer doesn't rerun" a fact rather than a request.

**H2. Gate: `PreToolUse` with `if: "Bash(git commit *)"`, plus a second handler for `Bash(gh pr create *)` (deterministic).**
- `git commit`: require at least a focused green for the key of the state being committed. The `noTestPaths` exception applies.
- `gh pr create` and the finish stage: require a **full** green.
- On a miss: deny, giving the exact command to run.
- Inference: this replaces Finishing's unconditional S9 with "run only if there's no record", and turns S10 on a fast-forward into a hit.
- The project's own pre-commit hook still runs. Optional and opt-in per project: a one-line husky guard, `anvil-verify check --cmd "<hook's test cmd>" && exit 0`, before the hook's test step. It's never installed silently.

**H3. Claim check: `PreToolUse` on `SubagentHandback`, plus `Stop` and `SubagentStop` (heuristic).**
- Match the report or `last_assistant_message` against a short claim pattern (`tests? (pass|green)|all (tests|checks) pass|verified|suite (is )?green`).
- If it matches and `anvil-verify check` fails for the current tree, block **once** with *"The report says tests pass; no passing run is recorded for the current code state (tree …). Last green: tree … at …, before N files changed."*
- Respect `stop_hook_active` and never block twice in a row: the cap is 8, and prose matching has false positives.
- **Inference:** this is the only way to catch a *claim*. Treat it as a nudge. The deterministic enforcement is H2 at commit and PR time.

**H4. SessionStart (already planned for Anvil)** adds one factual line: "Test runs in this repo are recorded per code state by anvil-verify; `anvil-verify show latest` prints the last result."

### 4.5 How the flow changes

| Stage | Today (Superpowers 7.0.2) | With the rule |
|---|---|---|
| Worktree baseline (S1) | Full run | `check` first. Run full only on a miss (a base already tested in the main checkout is a hit, because records are shared) |
| Implementer per task (S2, S3) | Focused, then full before commit | Focused (`{files}` = changed since the last green). Full only when the plan marks the task's blast radius as unknown (Anvil `:262-264`) |
| Fix round (S5) | Covering tests | Same, recorded |
| Task reviewer (S6, S7) | Told not to run | Reads `anvil-verify show`. A rerun attempt on the same tree is denied by H1 |
| Controller claims (S4) | Fresh run "in this message" | `check`. The record *is* the fresh evidence for this tree. Anvil's rewritten verification skill says so in one line |
| Final state | Fix wave runs full | **One full run on the final tree** (H2 requires it before PR or finish) |
| Finishing Step 1 (S9) | Full again | Hit. 0 min |
| Merge Option 1 (S10) | Full again | Fast-forward: hit. Real merge: one full run (a new tree, correctly) |
| Project pre-commit | Runs per commit | Unchanged by default. Opt-in guard skips a repeat |

**Inference:** the 3-task example goes from 7 to 10 full runs (2h20m to 3h20m) to **1 or 2** (20 to 40 min), plus focused runs measured in seconds to minutes. The one remaining 20-minute run is the floor the rule can't remove. Cutting that is suite work: sharding, parallel workers, the core-only test audit in notes §4.

### 4.6 Wording changes Anvil needs regardless of hooks

These are inferences about the skill text Anvil's rewrite should own.

- Define **fresh** once: "fresh = recorded for the current code state". Remove "in this message".
- Make the reviewer checklist item an evidence check: "a passing run is recorded for this state", not "All tests passing?".
- Anvil's own finishing step uses `check`, then runs on a miss. It doesn't inherit S9 and S10.
- Implementer briefs carry the focused command and say the orchestrator owns the full run. H1 backs that up, so the brief no longer has to be obeyed perfectly.

### 4.7 Cross-platform notes

- Needs only bash and git, which are always present with Claude Code on Windows when Git Bash is installed (hooks default to it).
  - Hash with `git hash-object`. Write atomically with `mv`. Run `date -u +%FT%TZ` in both Git Bash and GNU or BSD userlands.
  - Avoid `stat` flags, `sed -i` and `readlink -f`, which differ between GNU and BSD.
- Hook invocation copies Superpowers' `run-hook.cmd` polyglot and the `"shell": "bash"` and `"powershell"` command forms (Superpowers `hooks/hooks.json`). The exec form can't spawn `.cmd`.
- **Long suites:** the Bash tool's default timeout is 2 minutes and its maximum is 10. A 20-minute suite must run with `run_in_background`. The wrapper records the result itself when the process exits, so it doesn't depend on whether `PostToolUse` fires for background commands, which the docs don't say. That's the reason to record in a wrapper rather than in `PostToolUse`.
- **No jq on stock Git Bash:** H1 parses `"command":"…"` with grep, or with node when it's available. Escaped quotes inside commands are an edge case that falls through to "allow and run", which is always the safe failure.

---

## 5. Open risks

1. **Undeclared inputs give a false green.**
   - The cases: global config, system libraries, DB schema state, Docker images, generated-but-ignored code that nobody listed.
   - The mitigations: the `inputs`, `env` and `tools` lists, `external`, max age, and the full run on the final tree whenever the key changed.
   - The residual risk is a reused green on a final tree whose only change is undeclared environment. It's the same class of risk as Bazel's non-hermetic tests, and the same kind of answer.
2. **Command matching is brittle.**
   - `npm test`, `npm run test`, `pnpm test`, `npx vitest run`, `cd pkg && npm test` and `npm test -- --watch=false` are different strings.
   - H1 only dedupes what it recognises. Unrecognised forms just run, which is safe but wasteful.
   - A model could also dodge the dedupe by respelling the command. That's not a safety problem, only a speed one.
3. **Rewriting commands with `updatedInput`.** It's documented but less common than deny. It must preserve `run_in_background` and `timeout`, and its behaviour on Monitor-backed commands is restricted ("allow and updatedInput have no effect on Monitor commands"). Fallback: deny with "use `anvil-verify run -- <cmd>`", which costs one extra turn.
4. **Claim detection is heuristic.** False positives annoy, and false negatives let a prose claim through. Only H2, at commit and PR, is a real gate. Don't oversell H3 as "claims are blocked".
5. **Model behaviour against the record.**
   - Opus 5 self-verifies unprompted. A denied rerun might be followed by attempts with a different spelling.
   - If Superpowers is still installed alongside, its `verification-before-completion` ("in this message") contradicts the record, which is the two-skills conflict again.
   - These need a `claude plugin eval` fixture: a slow fake suite plus a counter of runs per tree.
6. **Concurrency in one worktree.** Before and after trees catch edits during a run, but the run is then wasted. Anvil's 3 to 4 parallel builders should each have their own worktree (notes §9). Records are shared via the common dir, and the atomic `mv` keeps concurrent writes safe.
7. **Object-store growth.** `git add -A` into a temp index writes blobs for untracked and modified files on every key computation. They're unreachable and get pruned by `git gc` after the default 2 weeks. Large untracked binaries make this slow. Mitigation: compute the key at most once per run and check, and document `.gitignore` hygiene.
8. **Focused-lane blind spots** (dynamic imports, data files, CLI-spawned code; testmon doesn't see static files). They're acceptable because the final full run catches them. They aren't acceptable if anyone later "optimises" the final run into a selection.
9. **A forged or stale record.** An agent could hand-write a JSON record. Only the wrapper should write. A permission deny on `Write` and `Edit` to the record directory is cheap. Records carry `agent_id` and `session_id` for audit.
10. **The one remaining 20-minute run is still a blocking wait** at merge time, the private-evidence complaint. The rule fixes the repeats, not that run. It needs progress visibility (the live progress file) and suite-speed work, which are separate items.
11. **The Windows hook path is the least tested.** Git Bash discovery (`CLAUDE_CODE_GIT_BASH_PATH`), the PowerShell fallback when Git Bash is missing, and CRLF warnings from `git add` all need a check on this machine before shipping.

---

## Sources

Local files (read 2026-11-18):
- Superpowers 7.0.2 (released 2026-11-03 per `RELEASE-NOTES.md`): `skills/verification-before-completion/SKILL.md`, `skills/subagent-driven-development/{SKILL.md, implementer-prompt.md, task-reviewer-prompt.md, re-review-prompt.md, references/fix-loop.md, references/final-review.md}`, `skills/finishing-a-development-branch/SKILL.md`, `skills/using-git-worktrees/SKILL.md`, `skills/test-driven-development/SKILL.md`, `skills/executing-plans/{SKILL.md, scripts/task-done}`, `skills/dispatching-parallel-agents/SKILL.md`, `skills/requesting-code-review/code-reviewer.md`, `hooks/hooks.json`, `RELEASE-NOTES.md`.
- Anvil: `plugins/anvil/skills/anvil/SKILL.md`, `plugins/anvil/.claude-plugin/plugin.json` (v0.2.0).
- Round-1 reports in this folder (2026-11-18); `docs/anvil-rebuild/private/2026-11-18-session-evidence.md` (counts only, gitignored).

Tree-keyed caches and stale verdicts:
- [mhagger/git-test](https://github.com/mhagger/git-test): created 2017-01-06, last push 2025-03-13.
- [spotify/git-test](https://github.com/spotify/git-test): created 2015-01-08, archived; [Spotify blog](https://engineering.atspotify.com/2015/03/git-test), 2015-03.
- [Reachpad/greentree](https://github.com/Reachpad/greentree): created 2026-08-12, last push 2026-09-27, archived and retired.
- [berlinguyinca/pi-engineering #149](https://github.com/berlinguyinca/pi-engineering/issues/149) and [PR #264](https://github.com/berlinguyinca/pi-engineering/pull/264): PR opened 2026-10-15, merged 2026-10-20.
- GSD Core: [#4857](https://github.com/open-gsd/gsd-core/issues/4857) (2026-09-18), [#4697](https://github.com/open-gsd/gsd-core/issues/4697) (2026-09-13), [#4682](https://github.com/open-gsd/gsd-core/issues/4682), [epic #4907](https://github.com/open-gsd/gsd-core/issues/4907) (2026-09-21 to 09-27), [#5095](https://github.com/open-gsd/gsd-core/issues/5095) and [PR #5103](https://github.com/open-gsd/gsd-core/pull/5103) (2026-09-28). Repo pushed 2026-11-18.

Runner caches and affected tests (doc versions as shown on the pages, fetched 2026-11-18):
- [Jest CLI](https://jestjs.io/docs/cli), docs 30.5; latest release v30.5.2 on 2026-09-18.
- [Vitest CLI](https://vitest.dev/guide/cli), v5.1.1 (released 2026-11-17); [`changed`](https://vitest.dev/config/changed); [`forceRerunTriggers`](https://vitest.dev/config/forcereruntriggers); [affected-tests recipe](https://main.vitest.dev/guide/recipes/affected-tests).
- [pytest-testmon](https://testmon.org/); [v2.3.0 release](https://github.com/tarpas/pytest-testmon/releases/tag/v2.3.0), 2026-11-02.
- [Go `go test` caching](https://pkg.go.dev/cmd/go#hdr-Test_packages), doc shown for go1.27.4.
- [Bazel user manual](https://bazel.build/docs/user-manual) and [common definitions](https://bazel.build/reference/be/common-definitions); Bazel 9.3.2 released 2026-11-05.
- [Gradle build cache](https://docs.gradle.org/current/userguide/build_cache.html), user manual 9.9.1 (released 2026-11-10).
- [Nx affected](https://nx.dev/docs/features/ci-features/affected) and [Nx commands](https://nx.dev/docs/reference/nx-commands); Nx 24 behaviour, latest tag 24.1.0-beta.1 on 2026-11-13.
- [Turborepo caching](https://turborepo.dev/docs/crafting-your-repository/caching); v2.11.12 released 2026-11-17.
- Vitest-in-hooks traps: [Myceliq/quality-kit #38](https://github.com/Myceliq/quality-kit/issues/38) (2026-09-19), [kamp-us/phoenix #7995](https://github.com/kamp-us/phoenix/issues/7995) (2026-09-05).
- Git-hook practice: [DEV guide on husky and lint-staged](https://dev.to/_d7eb1c1703182e3ce1782/git-hooks-with-husky-and-lint-staged-the-complete-setup-guide-for-2025-53ji) (2025); [planar-nexus PR #1668](https://github.com/anchapin/planar-nexus/pull/1668) (2026, from search; exact date not checked); [aihub-be #1017](https://github.com/AiHub-Ecosystem/aihub-be/issues/1017) (2026-10-23). husky v9.1.7 (2024-11-18); lint-staged v17.6.1 (2026-11-15).

Claude Code hooks and agent practice:
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks): live page, undated, mentions up to v2.1.314; fetched 2026-11-18.
- [Zenn: "Don't Finish Until Tests Pass" Stop-hook gate](https://zenn.dev/nozomi720/articles/claude_code_hooks_gate?locale=en), 2026-08-11 (updated 08-15).
- [Joxo: Make Claude Code run the tests before it says done](https://joxo.ai/blog/make-claude-code-run-tests-before-done), updated 2026-10-29.
- [melodic-software/claude-code-plugins PR #6308](https://github.com/melodic-software/claude-code-plugins/pull/6308), 2026-10-04.
- [rjtenyks/leveraged-etf-retest PR #4](https://github.com/rjtenyks/leveraged-etf-retest/pull/4), 2026; date not checked.
- [jknofe/llm-agent-framework PR #14](https://github.com/jknofe/llm-agent-framework/pull/14), opened 2026-11-10, merged 2026-11-11.
- [JPHutchins/code-review #315](https://github.com/JPHutchins/code-review/issues/315), 2026-10-24.
- [aganesy/QFAI #3695](https://github.com/aganesy/QFAI/issues/3695), 2026-10-13.
- [letrquan/book #236](https://github.com/letrquan/book/issues/236), 2026-09-23.
- [Hu et al., "Analyzing and Mitigating Cost-Inefficient Behaviors in Coding Agents", arXiv 2609.30725](https://arxiv.org/abs/2609.30725): v1 2026-09-25, v3 2026-10-12.
- Anthropic guidance (Opus 5 prompting guide; C-compiler write-up, Feb 2026): via [2026-11-18-anthropic-guidance.md](2026-11-18-anthropic-guidance.md) §3.3 and §4.3.
