# Anvil 1.0: Implementation Plan (phases 1–2: core flow and packaging)

- **Spec:** [2026-11-18-anvil-design.md](2026-11-18-anvil-design.md). Approved by Saad on 2026-11-18 ("Okay, that's all look good, and I approve").
- **Approved:** no (waiting at stop 2)
- **Synced branch:** `anvil-rebuild` (remote `origin/anvil-rebuild`)
- **Work branch:** `anvil/anvil-1.0/work` (local)
- **Size:** full

> **For agentic workers:**
> - Each task names the design sections it implements. Read those sections, plus the shared references written in T1, before starting.
> - Lanes work only inside their declared write set.
> - Implementers run only their task's targeted tests and the skill lint, never the full suite.
> - Your report must state, for each test you touched, whether **the test changed or the code changed**, and why.

**Goal:** a self-contained Anvil plugin that runs the approved flow (brainstorm → spec → stop → plan → stop → build → verify → finish), with gates on disk, test-result reuse, parallel waves and live progress. It has no Superpowers dependency.

**Architecture:**
- **Stage skills:** each is a plain-language `SKILL.md`, adapted from Superpowers 7.0.2. Long detail goes in `references/` and `prompts/`.
- **The CLI:** one small Python CLI, `bin/anvil`, does everything the model can't be trusted to do in its head: S-line parsing, gates, parallel-safe checks, result reuse, and stale detection.
- **Hooks:** thin bash hooks call that CLI.
- **Shared formats:** the formats every piece parses are pinned in T1 and never redefined elsewhere.

**Tech stack:**
- Markdown skills.
- Python ≥ 3.10, standard library only.
- bash hooks behind Superpowers' `run-hook.cmd` polyglot wrapper.
- `unittest`.
- `claude plugin eval` (run in WSL2 Ubuntu).

**Out of this plan** (later plans, design §10):
- rewriting `ui-mockup` and `ux-audit`;
- folding the machine's Gemini tooling into `cross-model`;
- the replays and the parallel pilot.

## Global constraints

Each line is copied from the spec.

- **Skill size.** Each `SKILL.md` must be under **20,000 characters**. Aim for ≤ 15,000.
- **Plain wording.** No `MUST`, `IMPORTANT`, `EXTREMELY`, `ABSOLUTELY`, "Iron Law", or ALL-CAPS commands in skills or hook output. Hook text is phrased as facts.
- **Descriptions say when to use the skill.** They don't summarise its workflow.
- **No forbidden tools or links.** No todo-tool instructions (TodoWrite/Task\* are gone). No Artifacts. No Superpowers skill invoked from an Anvil skill.
- **Credit and exclusions.** Superpowers is MIT: ship `NOTICE`, and credit it in the README. Leave out its logo, the visual companion and the visual companion's telemetry.
- **Source line on every adapted file.** It's an HTML comment placed right after the frontmatter: `<!-- adapted from superpowers@7.0.2: skills/<path> -->`. List every source a file draws on. The upstream watch (design §8) depends on it.
- **Platform.** Windows 11 with Git Bash comes first. Python is called as `python`, then `py -3`, then `python3`. On this machine `python3` is the broken Microsoft Store stub.
- **Commit messages** carry no Claude co-author trailer.
- **The repo is public.** No client names or quotes in committed files.
- **Project rules win** over Anvil defaults. These are `CLAUDE.md`, `.claude/rules/*` and doc-location rules.

## Review focus

These are failure modes the spec implies but no task's tests would otherwise catch. Each has a test in the owning task.

1. **CRLF files.** The repo's markdown is checked out with CRLF. The S-line, task-table and approval parsers handle `\r\n`, and hook scripts stay LF, or bash breaks. Covered by T1 (`test_parse_crlf`, `.gitattributes`).
2. **Repos that never used Anvil.** Every hook is a no-op there: no blocking, no files written except the prompt log. Covered by T5 (`test_pretool_allows_without_active_topic`).
3. **No working Python, or a broken PATH.** The hooks fail open: exit 0 with a one-line warning in context, never blocking every tool call. Covered by T5 (`smoke: run-hook with empty PATH`).
4. **Pre-approval quotes with whitespace or quote characters.** Quote matching normalises whitespace and smart quotes, and an invented quote never matches. Covered by T2 (`test_quote_normalised`, `test_invented_quote_rejected`).
5. **Lanes in worktrees.** Result reuse and state are shared across worktrees (they're stored under the git common dir), and a lane's diff is checked against its own write set only. Covered by T3 and T4 (`test_state_shared_across_worktrees`, `test_lane_check_flags_outside_write`).

---

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | §7.1, §7.4–7.6, §7.9 (formats) | `plugins/anvil/references/*`, `plugins/anvil/bin/anvil`, `plugins/anvil/bin/anvil.cmd`, `plugins/anvil/bin/anvil_cli/__init__.py`, `plugins/anvil/bin/anvil_cli/cli.py`, `plugins/anvil/bin/anvil_cli/docs.py`, `plugins/anvil/bin/anvil_cli/state.py`, `plugins/anvil/NOTICE`, `.gitattributes`, `tests/anvil_cli/__init__.py`, `tests/anvil_cli/helpers.py`, `tests/anvil_cli/test_docs.py`, `tests/anvil_cli/test_state.py` | - | - | 0 | yes |
| T2 | §7.2 (gates, AFK) | `plugins/anvil/bin/anvil_cli/gate.py`, `tests/anvil_cli/test_gate.py` | - | T1 | 1 | yes |
| T3 | §7.5, §7.6 (plan-check, lane-check) | `plugins/anvil/bin/anvil_cli/plancheck.py`, `tests/anvil_cli/test_plancheck.py` | - | T1 | 1 | yes |
| T4 | §7.7 (result reuse) | `plugins/anvil/bin/anvil_cli/results.py`, `tests/anvil_cli/test_results.py` | - | T1 | 1 | yes |
| T5 | §7.2, §7.6, §7.7, §7.11 (hooks) | `plugins/anvil/hooks/*`, `plugins/anvil/bin/anvil_cli/hooks.py`, `tests/anvil_cli/test_hooks.py` | - | T2, T4 | 2 | yes |
| T6 | §7.6 (stale, progress) | `plugins/anvil/bin/anvil_cli/stale.py`, `plugins/anvil/bin/anvil_cli/progress.py`, `tests/anvil_cli/test_stale.py`, `tests/anvil_cli/test_progress.py` | - | T1 | 1 | yes |
| T7 | §7.2, §7.3, §7.4, §7.12, §7.13 | `plugins/anvil/skills/anvil/**`, `plugins/anvil/skills/brainstorm/**` | - | T1 | 2 | yes |
| T8 | §7.5 | `plugins/anvil/skills/plan/**` | - | T1 | 2 | yes |
| T9 | §7.6 | `plugins/anvil/skills/build/**` | - | T1 | 2 | yes |
| T10 | §7.7, §7.8 | `plugins/anvil/skills/verify/**`, `plugins/anvil/skills/finish/**` | - | T1 | 3 | yes |
| T11 | §7.6 (debug) | `plugins/anvil/skills/debug/**` | - | T1 | 3 | yes |
| T12 | §7.11 (afk, tickets) | `plugins/anvil/skills/afk/**`, `plugins/anvil/skills/ticket-update/SKILL.md` | - | T1, T2 | 3 | yes |
| T13 | §5, §8, §10.2 | `plugins/anvil/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md`, `tests/anvil_cli/test_skills.py`, `plugins/anvil/references/upstream.md` | - | T7–T12 | 4 | yes |
| T14 | §9.1 | `plugins/anvil/evals/**` | - | T5, T7–T12 | 4 | yes |

**Integrator-only work** (the orchestrator, not a lane):
- merges, per-wave checks and commit points;
- the T15 install and final verification.

No lockfiles, generated files or migrations are involved.

## Parallel-safe check, done by hand (the `plan-check` CLI doesn't exist yet)

- **Write sets don't overlap.** T1 owns `cli.py`, which registers every subcommand by module name. Lanes never edit `cli.py`.
- **Dependencies only point at earlier waves.** T5 needs T2 and T4 from wave 1. T12 needs T2 from wave 1. T13 and T14 need wave 2 and wave 3.
- **No shared resources.** No ports, no database, no dev server.
- **One deliberate overlap.** `tests/anvil_cli/test_skills.py` is written in T13, after every skill lane has landed. It's the mechanical consistency check across the parallel skill lanes.

## Waves and execution

| Wave | Lanes | Estimate |
|---|---|---|
| 0 | T1 (alone; foundations) | one lane |
| 1 | T2, T3, T4, T6 (4 lanes) | replaces 4 sequential tasks |
| 2 | T5, T7, T8, T9 (4 lanes) | replaces 4 |
| 3 | T10, T11, T12 (3 lanes) | replaces 3 |
| 4 | T13, T14 (2 lanes) | replaces 2 |

That's 14 tasks in 5 waves. Done one at a time, it would be 14 sequential tasks. The expected saving on the build stage is roughly 1.5 to 2.5 times, because the skill lanes are similar in size.

- **Proposed mode:** parallel, 4 lanes maximum, with a per-task review in every lane.
- **Lane isolation, Claude's call:** the orchestrator creates each lane's worktree itself, with `git worktree add ../anvil-lane-<task> -b anvil/anvil-1.0/<task> anvil/anvil-1.0/work`. Agents are briefed with that absolute path.
  - This avoids relying on `isolation: "worktree"` and its base-ref default.
  - After each wave, lanes are merged into the work branch in task order, and their worktrees are removed.

## Test strategy

The full suite is `python -I -m unittest discover -s tests -t .`. It's expected to take under 10 seconds, so it may also run after each wave (spec §7.6: under about 2 minutes).

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `test_docs.test_parse_live_and_retired_slines` | keep | §7.4 | S-line tracking: stale detection and the converge check | T1 |
| `test_docs.test_parse_crlf` | keep | Review focus 1 | Every parser on Windows checkouts | T1 |
| `test_docs.test_task_table_and_commit_points` | keep | §7.5 | plan-check and the build loop | T1 |
| `test_docs.test_test_list_table` | keep | §7.5 | Test strategy enforcement and the finish report | T1 |
| `test_docs.test_direct_size_reads_slines_from_plan` | keep | §7.2 (direct size) | A merged spec-and-plan document | T1 |
| `test_state.test_state_dir_under_git_common_dir` | keep | Review focus 5 | Sharing state across worktrees | T1 |
| `test_state.test_state_dir_outside_git` | keep | Review focus 2 | Running outside a repo | T1 |
| `test_gate.test_approve_requires_prompt_after_present` | keep | §7.2 | The model approving its own document | T2 |
| `test_gate.test_approve_rejects_changed_doc` | keep | §7.2 | Approving a document edited after it was shown | T2 |
| `test_gate.test_pre_approval_quote_must_exist` | keep | §4, §7.2 | Invented pre-approvals | T2 |
| `test_gate.test_invented_quote_rejected` | keep | Review focus 4 | Same | T2 |
| `test_gate.test_quote_normalised` | keep | Review focus 4 | A real pre-approval being refused | T2 |
| `test_gate.test_check_build_needs_plan_approved` | keep | §7.2 | The build starting without approval | T2 |
| `test_gate.test_afk_on_needs_afk_phrase` | keep | §7.2 | AFK turned on without Saad saying so | T2 |
| `test_plancheck.test_overlapping_write_sets_fail` | keep | §7.5 | Parallel lanes clobbering each other | T3 |
| `test_plancheck.test_shared_resource_same_wave_fails` | keep | §7.5 | Port or DB contention | T3 |
| `test_plancheck.test_dependency_on_same_or_later_wave_fails` | keep | §7.5 | Wave ordering | T3 |
| `test_plancheck.test_integrator_only_paths` | keep | §7.5 | Lockfile or migration damage | T3 |
| `test_plancheck.test_lane_check_flags_outside_write` | keep | §7.6 | Write-set drift | T3 |
| `test_results.test_key_changes_on_edit_and_untracked` | keep | §7.7 | A stale green result being reused | T4 |
| `test_results.test_key_changes_on_lockfile` | keep | §7.7 | Same, after a dependency change | T4 |
| `test_results.test_fresh_only_reuses_passing_with_tests` | keep | §7.7 | A failing or empty run being reused | T4 |
| `test_results.test_external_never_reused` | keep | §7.7 | Live-service tests being skipped | T4 |
| `test_results.test_state_shared_across_worktrees` | keep | Review focus 5 | Reuse between lanes and the orchestrator | T4 |
| `test_results.test_index_untouched` | keep | §7.7 | Corrupting Saad's staged changes | T4 |
| `test_hooks.test_pretool_allows_without_active_topic` | keep | Review focus 2 | Blocking normal work in other repos | T5 |
| `test_hooks.test_pretool_blocks_agent_when_plan_unapproved` | keep | §7.2 | The gate being prompt-only | T5 |
| `test_hooks.test_pretool_returns_fresh_result` | keep | §7.7 | The repeated-suite waste | T5 |
| `test_hooks.test_pretool_warns_on_keep_test_edit` | keep | §7.6 | Testwashing | T5 |
| `test_hooks.test_stop_blocks_in_afk_with_open_tasks` | keep | §7.11 | AFK stalling | T5 |
| `test_hooks.test_stop_allows_with_stop_note` | keep | §7.11 | AFK never stopping | T5 |
| `test_hooks.test_prompt_logged` | keep | §7.2 | Gates that can't be verified | T5 |
| `test_stale.test_retired_sline_flags_tasks_and_tests` | keep | §7.6 | Plan-says-A, code-says-A1 drift | T6 |
| `test_progress.test_summary_counts_markers` | keep | §7.6 | The live progress view | T6 |
| `test_skills.*`: frontmatter, size < 20k, no forbidden words, CLI subcommands exist, referenced files exist, no `superpowers:` invocations | keep | Global constraints | Consistency across the parallel skill lanes | T13 |
| `smoke: bin/anvil --help` via Git Bash and via cmd | smoke | §7.9 | The CLI unreachable on Windows | T1 |
| `smoke: session-start emits valid JSON` | smoke | §7.13 | Anvil never bootstrapping | T5 |
| `smoke: run-hook with empty PATH exits 0` | smoke | Review focus 3 | Hooks blocking everything | T5 |
| `smoke: claude plugin details lists all skills` | smoke | §10.2 | A broken install | T15 |
| Fixture repos under `tests/anvil_cli/fixtures/` (git init on the fly by `helpers.py`) | scaffold → **kept** as test helpers | - | - | T1 |

No bug-repro tests: this plan fixes no reported bug.

The evals in T14 are behavior checks, not unit tests. They run in WSL2 (T15).

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | waves 0–1 (T1, T2, T3, T4, T6) | `feat(anvil): bin/anvil CLI with shared formats, gates, plan-check, result reuse and stale detection` | yes |
| C2 | wave 2 (T5, T7, T8, T9) | `feat(anvil): hooks, router, brainstorm, plan and build skills` | yes |
| C3 | wave 3 (T10, T11, T12) | `feat(anvil): verify, finish, debug and revised afk skills` | yes |
| C4 | wave 4 plus T15 (T13, T14) | `feat(anvil): 1.0 packaging, skill lint and evals` | yes |

At each commit point:
1. Squash the work branch onto `anvil-rebuild`.
2. Push.
3. Reset the work branch to the new tip.

---

## Shared formats (pinned here; T1 writes them into `plugins/anvil/references/`)

Every skill and every CLI module uses exactly these.

**Topic folder.** The default is `docs/<slug>/`, holding `spec.md`, `plan.md` and `progress.md`. With size `direct`, only `plan.md` (spec part plus plan part) and `progress.md` exist.

**Header lines** (bullet lines near the top of `spec.md` and `plan.md`):

```
- **Approved:** no
- **Approved:** 2026-11-18 by Saad ("<quote>")
- **Approved:** pre-approved by Saad 2026-11-18 ("<quote>")
- **Approved:** skipped (AFK) 2026-11-18 ("<quote>")
- **Mode:** normal | redesign            (spec only)
- **Size:** trivial | direct | full
- **Synced branch:** <branch> (local) | <branch> (remote <remote>/<branch>)   (plan only)
```

**S-lines** (spec `## Spec lines`, or the spec part of a direct-size plan):

```
- **S3** One behavior, one line.
- ~~**S3** Old behavior.~~ RETIRED → S7 (2026-11-20, CR: reason)
```

- Regex: `^- (~~)?\*\*S(\d+)\*\*`
- Numbers are never reused.

**Task table** (plan `## Task table`). Columns, in order:

`| Task | Spec | Writes | Shared | Depends | Wave | Review |`

- Task: `T<n>`.
- Spec: comma-separated `S<n>`.
- Writes: comma-separated backticked repo-relative paths or globs.
- Shared: comma-separated resource ids from `port:<n>`, `db`, `lockfile`, `generated`, `migrations`, `devserver`, or `-`.
- Depends: comma-separated task ids, or `-`.
- Wave: an integer.
- Review: `yes`, or `skip (fully specified)`.

**Test list** (plan `## Test strategy`): `| Test | Type | Spec | Breaks if it fails | Task |`

- Type is one of `smoke`, `keep`, `repro`, `scaffold`.

**Commit points** (plan `## Commit points`): `| Commit | Closes | Message | Push |`

- Commit: `C<n>`.
- Push: `yes` or `no`.

**Progress file** (`progress.md`):

```
# Progress: <topic>
- **Stage:** spec | plan | build | verify | finish | done
- **Wave:** <n> of <m>
## Tasks
- [ ] T1 <title>
- [~] T2 <title> (lane anvil/<topic>/T2)
- [x] T3 <title> C1
## Commit points
- C1 <sha> pushed 2026-11-18
## Blockers
## Decision log
<!-- newest first; each: - 2026-11-18 **<choice>** — <reason>. Confidence: high|medium|low. Changes if: <fact>. -->
## Stop note
```

**State directory:** `<git common dir>/anvil/`, or `~/.claude/anvil/<sanitised-cwd>/` outside git. It's never committed. Files:

| File | Holds |
|---|---|
| `active.json` | `{slug, dir, size, stage}` |
| `presented.json` | `{"spec"\|"plan": {hash, ts}}` |
| `prompts.jsonl` | `{ts, prompt}` per line, keeping the last 500 |
| `afk.json` | `{on, ts, quote}` |
| `results.jsonl` | `{key, cmd, scope, exit, tests_ran, ts, summary}` |

**CLI** (`anvil <subcommand>`). Every subcommand supports `--json`. Exit codes: 0 = ok or yes, 1 = no or refused (with a reason on stderr), 2 = usage error.

```
topic start <slug> [--size trivial|direct|full] [--dir <path>]   topic show   topic end
present spec|plan
approve spec|plan --quote "<text>" [--pre] [--afk]
check plan|build
afk on --quote "<text>" | afk off | afk status
spec-lines [--live|--retired]
stale
plan-check
lane-check <task> --base <ref>
run [--scope targeted|full|smoke] [--external] -- <cmd…>
fresh [--scope …] -- <cmd…>
progress
hook session-start|user-prompt-submit|pre-tool-use|stop        (reads hook JSON on stdin)
```

---

## T1: Foundations (formats, CLI skeleton, parser, state)

**Files:**
- Create: `plugins/anvil/references/formats.md`. This is the "Shared formats" section above, verbatim, plus one worked example of each table.
- Create: `plugins/anvil/references/test-policy.md`, covering:
  - the four test types;
  - the budget per kind of work (design §7.5);
  - "name the tests that guard each task, not 'do TDD'";
  - the test-changed vs code-changed rule.
- Create: `plugins/anvil/references/git-flow.md`, covering:
  - the work and synced branches;
  - the commit-point procedure (squash, push, reset);
  - cleanup rules;
  - no force-push of the synced branch;
  - the no-trailer rule.
- Create: `plugins/anvil/references/simplicity.md`. This is the three lines from design §7.12, plus the six-part over-building checklist from [simple-code rules](research/2026-11-18-simple-code-rules.md).
- Create: `plugins/anvil/bin/anvil` (bash) and `plugins/anvil/bin/anvil.cmd`.
  - Both locate Python (`python`, then `py -3`, then `python3`, skipping the WindowsApps stub), then run `-I -m anvil_cli.cli` with `PYTHONPATH` set to `bin/`.
  - The `.cmd` file follows the polyglot pattern of Superpowers' `run-hook.cmd`.
- Create: `plugins/anvil/bin/anvil_cli/cli.py`. It's an argparse dispatcher with a registry `COMMANDS: dict[str, str]` that maps each subcommand to `"module:function"`, imported lazily.
  - Every subcommand in the CLI block above is registered now, including ones whose module a later lane writes.
  - A missing module prints `not available yet` and exits 1.
- Create: `plugins/anvil/bin/anvil_cli/docs.py`.
- Create: `plugins/anvil/bin/anvil_cli/state.py`.
- Create: `plugins/anvil/NOTICE`. This is Superpowers' MIT license text, with "Portions adapted from obra/superpowers 7.0.2".
- Create: `.gitattributes` with `plugins/anvil/hooks/** text eol=lf`, `plugins/anvil/bin/anvil text eol=lf`, `*.sh text eol=lf`.
- Create: `tests/anvil_cli/helpers.py`. It provides `make_repo(tmp) -> Path` (git init, one commit) and `write(path, text, crlf=False)`.
- Test: `tests/anvil_cli/test_docs.py` and `tests/anvil_cli/test_state.py`.

**Interfaces (produces):**

```python
# docs.py
@dataclass class SLine: num: int; text: str; retired: bool; replaced_by: int | None
@dataclass class Task: id: str; spec: list[str]; writes: list[str]; shared: list[str]; depends: list[str]; wave: int; review: str
@dataclass class TestEntry: name: str; type: str; spec: list[str]; breaks: str; task: str
@dataclass class CommitPoint: id: str; closes: str; message: str; push: bool
def read_text(path: Path) -> str                     # normalises \r\n to \n
def parse_header(text: str) -> dict[str, str]        # "Approved", "Mode", "Size", "Synced branch"
def parse_slines(text: str) -> list[SLine]
def parse_tasks(text: str) -> list[Task]
def parse_tests(text: str) -> list[TestEntry]
def parse_commit_points(text: str) -> list[CommitPoint]
def set_header(text: str, key: str, value: str) -> str
def topic_docs(topic_dir: Path) -> tuple[Path | None, Path]   # (spec or None for direct size, plan)
# state.py
def state_dir(cwd: Path) -> Path                     # git common dir /anvil, or ~/.claude/anvil/<sanitised>
def load(cwd: Path, name: str, default) -> object    # JSON file in state_dir
def save(cwd: Path, name: str, value) -> None
def append_jsonl(cwd: Path, name: str, record: dict, keep: int | None = None) -> None
def read_jsonl(cwd: Path, name: str) -> list[dict]
def active_topic(cwd: Path) -> dict | None
# cli.py: topic start/show/end are implemented here, on top of state.py
```

**Steps:**
1. Write `test_docs.py`. Cover live and retired S-lines (`replaced_by == 7`), CRLF input, the task table (including the `-` cells), the test list and commit points. For a direct-size plan, `topic_docs` returns `(None, plan)` and S-lines come from `plan.md`. Run `python -I -m unittest tests.anvil_cli.test_docs` and confirm it fails.
2. Implement `docs.py`, then run the tests until they pass.
3. Write `test_state.py`:
   - Inside a repo, `state_dir` is under `git rev-parse --git-common-dir`.
   - A linked worktree resolves to the same dir.
   - Outside git, it resolves under a temporary `HOME`.

   Then implement `state.py` until the tests pass.
4. Write the wrappers and `cli.py` (registry plus topic commands), the references, `NOTICE` and `.gitattributes`.
5. Smoke-test `plugins/anvil/bin/anvil --help` from Git Bash and `cmd /c plugins\anvil\bin\anvil.cmd --help`. Both should print the subcommand list.
6. **Check one fact:** does Claude Code add a plugin's `bin/` to the Bash tool's PATH (docs: plugins reference)? Write the answer into `references/formats.md` under "Calling the CLI". **Either way, skills call the CLI by the absolute path the session-start hook supplies (T5).**
7. Report, following the implementer prompt.

## T2: Gates and AFK (`gate.py`)

- **Spec:** §4 (self-approval), §7.2.
- **Files:** create `plugins/anvil/bin/anvil_cli/gate.py` and `tests/anvil_cli/test_gate.py`.

**Interfaces:**
- Consumes `docs.*` and `state.*`.
- Produces:

```python
def present(cwd: Path, which: str) -> None          # stores sha256 of the doc text + now()
def approve(cwd, which, quote: str, pre: bool=False, afk: bool=False) -> str   # returns the header value written; raises GateError(reason)
def check(cwd, stage: str) -> tuple[bool, str]      # "plan": spec approved, or size=direct. "build": plan approved
def afk_on(cwd, quote) -> None; afk_off(cwd) -> None; afk_status(cwd) -> dict
def quote_in_prompts(cwd, quote, after_ts: float | None) -> bool
AFK_PHRASES = ("afk", "going to bed", "don't ask", "dont ask", "no approvals", "just finish", "run with it", "work through the plan", "i'll review", "make the call yourself")
```

**Rules:**
- **Normal approval.** `approve` without `--pre` needs all of:
  - the doc's current hash equals the presented hash;
  - a prompt with `ts > presented ts`;
  - that prompt contains `quote`.
- **Pre-approval.** `--pre` needs the quote in any logged prompt since `topic start`.
- **Quote matching** is case-insensitive. It collapses whitespace, maps `“”‘’` to `"'`, and requires at least 3 words.
- **AFK.** `afk on` requires the quote to be in a logged prompt **and** to contain an `AFK_PHRASES` entry.
- **What gets written.** On success, `approve` writes the header line in the format pinned above. `--afk` writes the `skipped (AFK)` form.

**Steps:**
1. Write the 7 gate tests from the test table. Run them and confirm they fail.
2. Implement until they pass.
3. Report.

## T3: Parallel-safe check and lane check (`plancheck.py`)

- **Spec:** §7.5, §7.6.
- **Files:** `plugins/anvil/bin/anvil_cli/plancheck.py` and `tests/anvil_cli/test_plancheck.py`.

**Interfaces:**

```python
@dataclass class Finding: rule: str; tasks: list[str]; detail: str
def plan_check(tasks: list[Task]) -> list[Finding]            # empty list = parallel-safe
def lane_check(cwd: Path, task: Task, base: str) -> list[str] # changed paths outside task.writes
INTEGRATOR_ONLY = ("package-lock.json","pnpm-lock.yaml","yarn.lock","poetry.lock","uv.lock","Cargo.lock","go.sum","**/migrations/**","**/generated/**")
```

**Rules:** the 9 points from [parallel build](research/2026-11-18-parallel-build.md) ("What the plan must contain"). At minimum:

1. Writes don't overlap between tasks in the same wave. Globs are compared with `fnmatch` both ways.
2. No shared resource appears twice in the same wave.
3. Each dependency points at a strictly earlier wave.
4. Integrator-only paths appear in no lane's writes.
5. Every task has at least one spec line, or the review column is `skip (fully specified)`.
6. Wave 0 holds exactly the foundation tasks, the ones others depend on.
7. Unknown task ids in Depends are flagged.
8. Each wave has at most 4 tasks.
9. Shared ids are well-formed.

`lane_check` uses `git diff --name-only <base>...HEAD`.

**Steps:**
1. Write the tests and confirm they fail.
2. Implement until they pass.
3. Report.

## T4: Result reuse (`results.py`)

- **Spec:** §7.7. Mechanism from [test-run reuse](research/2026-11-18-test-run-reuse.md).
- **Files:** `plugins/anvil/bin/anvil_cli/results.py` and `tests/anvil_cli/test_results.py`.

**Interfaces:**

```python
def tree_key(cwd: Path) -> str
#   = sha256 of: git write-tree from a TEMP index (GIT_INDEX_FILE) after `git add -A`;
#     hashes of the lockfiles present; python/node/go versions on PATH;
#     env vars listed in ANVIL_KEY_ENV
def result_key(cwd, cmd: list[str], scope: str) -> str
def run(cwd, cmd, scope="targeted", external=False) -> int
#   runs cmd; records {key, cmd, scope, exit, tests_ran, ts, summary(last 40 lines)};
#   skips recording if tree_key changed during the run
def fresh(cwd, cmd, scope="targeted") -> dict | None
#   newest record with the same key and exit==0 and tests_ran>0 and not external
def count_tests(output: str) -> int
#   recognises the unittest, pytest, vitest/jest and go test summaries; 0 if unknown
```

**Steps:**
1. Write the 6 tests from the test table. `test_index_untouched` asserts that `git diff --cached` is identical before and after `tree_key`. Confirm they fail.
2. Implement until they pass.
3. Report.

## T5: Hooks (`hooks.py` and `plugins/anvil/hooks/`)

- **Spec:** §7.2, §7.6, §7.7, §7.11, §7.13.
- **Files:** create `plugins/anvil/hooks/hooks.json`, `run-hook.cmd`, `session-start`, `user-prompt-submit`, `pre-tool-use` and `stop` (extensionless, LF), plus `plugins/anvil/bin/anvil_cli/hooks.py` and `tests/anvil_cli/test_hooks.py`.

**Interfaces:**
- Consumes `gate.check`, `gate.afk_status`, `results.fresh`, `docs.parse_tests`, `docs.parse_tasks` and `state.*`.
- Produces:

```python
def session_start(event: dict) -> dict      # {"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext": FACTS}}
def user_prompt_submit(event: dict) -> dict # appends {ts, prompt} to prompts.jsonl (keep=500); returns {}
def pre_tool_use(event: dict) -> dict       # permissionDecision allow/deny + reason, or additionalContext warning
def stop(event: dict) -> dict               # {"decision":"block","reason":...} or {}
```

**Behavior:**
- **`FACTS`** are plain statements, under 2,000 characters:
  - Anvil is installed; its CLI is at `<abs path>/bin/anvil`.
  - The flow and the stops.
  - When Superpowers is also installed, Anvil's skills cover brainstorming, planning, building, review and finishing.
  - The active topic, if there is one, with its stage and its progress summary.
- **`pre_tool_use`** is a no-op without an active topic. With one:
  - **Agent dispatches, and Edit/Write outside the topic dir, are denied** while `check build` fails and the stage is `spec` or `plan`. The reason names the missing approval.
  - **A test command with a fresh green result is denied.** The reason quotes the recorded summary, and gives `ANVIL_RERUN=1` as the override. Commands count as test commands if they match the plan's test-strategy commands or `anvil run`.
  - **An Edit/Write on a path listed as a `keep` test** returns `additionalContext`: "This file is a keep test for S<n>; state test-changed vs code-changed with the S-line in your report."
- **`stop`.** When AFK is on, `stop_hook_active` is false, and `progress.md` has `[ ]` or `[~]` tasks with no new `## Stop note` entry, it blocks with "AFK: open tasks <ids>. Continue, or write a Stop note in progress.md."
- **Failing open.** Any exception or missing Python means exit 0 with `{}`, plus a one-line stderr warning.

**Steps:**
1. Check the current stdin and stdout JSON schema of the four events against code.claude.com/docs/en/hooks. Note any field-name differences in the report.
2. Write the 7 hook tests from the test table. Each feeds `hooks.py` a dict directly. Confirm they fail.
3. Implement `hooks.py` until the tests pass.
4. Write the bash scripts. Each is about 5 lines: locate Python the same way as `bin/anvil`, run `-m anvil_cli.cli hook <event>`, and pass stdin through. Adapt `run-hook.cmd` from Superpowers 7.0.2, unchanged except for comments. Write `hooks.json`:
   - SessionStart, matcher `startup|clear|compact`;
   - UserPromptSubmit;
   - PreToolUse, matcher `Agent|Task|Edit|Write|MultiEdit|NotebookEdit|Bash`;
   - Stop.
5. Smoke tests:
   - `echo '{}' | plugins/anvil/hooks/run-hook.cmd session-start | python -m json.tool`;
   - `env PATH= plugins/anvil/hooks/run-hook.cmd pre-tool-use < fixture.json; echo $?` should print `0`.
6. Report.

## T6: Stale detection and progress (`stale.py`, `progress.py`)

- **Spec:** §7.6.
- **Files:** `plugins/anvil/bin/anvil_cli/stale.py`, `progress.py`, `tests/anvil_cli/test_stale.py` and `test_progress.py`.

**Interfaces:**

```python
def stale(cwd) -> list[dict]
#   {kind: "task"|"test", id, retired: "S3", replaced_by: 7}
#   for every task or test whose Spec cell names a retired S-line;
#   also {kind: "result", key} when results.jsonl has no record for the current tree_key
#   (import results lazily; skip if absent)
def progress_summary(cwd) -> dict
#   {stage, wave, open, in_progress, done, blockers, last_decision}
```

**Steps:**
1. Write the tests and confirm they fail.
2. Implement until they pass.
3. Report.

## T7: `anvil` router and `brainstorm` skills

- **Spec:** §7.2, §7.3, §7.4, §7.12, §7.13.
- **Sources to adapt:** Superpowers 7.0.2 `using-superpowers/SKILL.md` (structure only), `brainstorming/SKILL.md` and `brainstorming/builder-check-prompt.md`. Also Matt Pocock's grill-me mechanics, from the [market scan](research/2026-11-18-market-scan.md) §3.
- **Files:**
  - **Rewrite** `plugins/anvil/skills/anvil/SKILL.md` (≤ 8k characters).
  - **Create** `plugins/anvil/skills/brainstorm/SKILL.md` (≤ 15k), `plugins/anvil/skills/brainstorm/references/spec-template.md` and `plugins/anvil/skills/brainstorm/prompts/builder-check.md`.
- **Decided (Claude's call, under design §11):** there is **no separate `spec` skill**. `brainstorm` writes the spec. For direct size, it writes the merged `plan.md` spec part, and then hands off to `plan` in the same document.

**The `anvil` router must state:**
- what Anvil is, in plain facts;
- the size table, and the one-line statement of the chosen size;
- the flow and stops;
- how stops are passed: `anvil present`, then `anvil approve … --quote`;
- pre-approval and AFK;
- which skill runs each stage;
- the three simplicity lines;
- "project rules win";
- file locations (§7.10);
- the sibling-skill table (§7.11);
- the coexistence note.

Its description says *when* to use it: "Use for any feature, bug fix, refactor, migration, POC, research, architecture or mock request in a codebase…", plus the existing exclusions. It doesn't summarise the workflow.

**The `brainstorm` skill must contain:**
- look first, with subagents for broad lookups;
- one batched round of questions, each with a recommended answer;
- variations when information is thin;
- the exploration loop, handed to `ui-mockup` for UI;
- it ends when no question is left;
- the spec written per `spec-template.md` (header lines, ≤3 waiting-on-you questions, S-lines, shared surface, replaces/stays, decisions, change log);
- the builder check, with its three piles;
- `anvil present spec`, then stop 1.

**Steps:**
1. Draft both skills from the sources, applying the global constraints. Every CLI call uses the exact subcommand names pinned above.
2. Self-check: count characters with `wc -c`, and grep for the forbidden words.
3. Report, listing which Superpowers passages were kept close to verbatim.

## T8: `plan` skill

- **Spec:** §7.5.
- **Source:** Superpowers 7.0.2 `writing-plans/SKILL.md`.
- **Files:** `plugins/anvil/skills/plan/SKILL.md` (≤ 15k) and `plugins/anvil/skills/plan/references/plan-template.md`. The template follows `references/formats.md`.

**What the skill must contain:**
- **Kept from Superpowers:**
  - the reader model;
  - signatures, not bodies;
  - interfaces per task;
  - the review focus;
  - the self-review, including proportion.
- **Replaced:**
  - "TDD, frequent commits" becomes the test strategy (`references/test-policy.md`) and the commit points;
  - the checkbox steps become a task table plus a short step list per task.
- **Added:**
  - the foundations task;
  - `anvil plan-check` before presenting, and running sequentially with the stated reason if it fails;
  - the execution-mode proposal with numbers;
  - the synced branch choice;
  - checkpoints only where Saad asked for them;
  - `anvil present plan`, then stop 2;
  - the offer of a fresh session (`/clear`, then `/anvil:build docs/<slug>/plan.md`).

**Steps:**
1. Draft the skill.
2. Self-check: size and forbidden words.
3. Report.

## T9: `build` skill

- **Spec:** §7.6.
- **Sources:** Superpowers 7.0.2:
  - `subagent-driven-development/SKILL.md`, `implementer-prompt.md`, `task-reviewer-prompt.md`, `re-review-prompt.md`;
  - `subagent-driven-development/references/{fix-loop,final-review,handling-reports,preflight,resuming,cannot-verify}.md`;
  - `executing-plans/SKILL.md`, for single-agent mode;
  - `dispatching-parallel-agents/SKILL.md`;
  - `receiving-code-review/SKILL.md`.
- **Files:**
  - `plugins/anvil/skills/build/SKILL.md` (≤ 18k);
  - `plugins/anvil/skills/build/prompts/{implementer,task-reviewer,re-review,wave-review,final-review}.md`;
  - `plugins/anvil/skills/build/references/{waves,change-flow-back,receiving-review,resuming}.md`.

**What the skill must contain:**
- **Kept from Superpowers:**
  - continuous execution with the four named stops;
  - fresh context per implementer;
  - the single reviewer giving two verdicts (spec, then quality);
  - "don't trust the report";
  - the 5-round fix cap;
  - "Rulings I made".
- **Changed:**
  - **Preflight:** `anvil check build`, then `topic`/stage set to `build`, then create the work branch from the synced branch.
  - **Waves:**
    - the orchestrator creates the lane worktrees (`git worktree add …` from the work branch);
    - up to 4 implementer dispatches in one turn;
    - `anvil lane-check` per lane;
    - merges in task order;
    - the per-wave check: type-check, the wave's targeted tests via `anvil run`, the `wave-review` prompt looking for semantic conflicts, and the full suite only if it takes under about 2 minutes.
  - **Implementer prompt:**
    - targeted tests via `anvil run --scope targeted`;
    - never the full suite;
    - the test-changed vs code-changed statement;
    - the S-lines covered;
    - stay inside the write set.
  - **Reviewer prompts:**
    - never rerun tests;
    - check against the task's S-lines;
    - the over-building checklist from `references/simplicity.md`.
  - **Review rule:** every task gets reviewed unless its row says `skip (fully specified)`.
  - **`progress.md`:** updated at every state change; the decision log stays append-only.
  - **Commit points:** follow `references/git-flow.md`.
  - **Change flow-back:**
    1. classify the change;
    2. push back, or log it in AFK;
    3. retire the S-line and add the new one;
    4. `anvil stale`;
    5. update the plan, tests and progress in the same step.
  - **Debugging:** route to `/anvil:debug`.
  - **No todo tools,** and no Superpowers invocations.

**Steps:**
1. Draft the skill.
2. Self-check: size and forbidden words.
3. Report.

## T10: `verify` and `finish` skills

- **Spec:** §7.7, §7.8.
- **Sources:** Superpowers 7.0.2 `verification-before-completion/SKILL.md`, `finishing-a-development-branch/SKILL.md` and `requesting-code-review/code-reviewer.md`.
- **Files:** `plugins/anvil/skills/verify/SKILL.md` (≤ 12k) and `plugins/anvil/skills/finish/SKILL.md` (≤ 12k). The finish skill also gets `disable-model-invocation: true`.

**The `verify` skill:**
- **Evidence before claims.** This is kept from Superpowers, but **reuse comes first**: run `anvil fresh` before rerunning anything.
- **One full suite** on the final merged state, via `anvil run --scope full`.
- **Smoke paths,** as behavior evidence.
- **The converge check:** every live S-line from `anvil spec-lines --live` is marked met, missing, partial or contradicts, plus an **unrequested** list. "Met" needs evidence. It loops through fixes until it's clean.
- **UI work:** `ux-audit` against the mock.
- **Before done:** `cross-model` on large or expensive-to-reverse changes.

**The `finish` skill:**
- the remaining commit point;
- the make-live offer;
- the merge options;
- cleanup per `references/git-flow.md`;
- deleting scaffold tests, listing each one;
- the `ticket-update` completion comment;
- marking the spec and plan done;
- the report, in the §7.8 order.

**Steps:**
1. Draft both skills.
2. Self-check: size and forbidden words.
3. Report.

## T11: `debug` skill

- **Spec:** §7.6 (debugging).
- **Sources:** Superpowers 7.0.2 `systematic-debugging/` (all files).
- **Files:**
  - `plugins/anvil/skills/debug/SKILL.md` (≤ 10k);
  - `plugins/anvil/skills/debug/references/{root-cause-tracing,defense-in-depth,condition-based-waiting}.md`;
  - `plugins/anvil/skills/debug/scripts/find-polluter.sh`, copied as-is and kept LF.
- **Changes:**
  - plain wording;
  - a reproduced bug becomes a `repro` test (`references/test-policy.md`);
  - findings and fixes are logged in `progress.md` when a topic is active.
- **Steps:**
  1. Draft the skill.
  2. Self-check: size and forbidden words.
  3. Report.

## T12: `afk` revision and `ticket-update` hook-in

- **Spec:** §7.2, §7.11.
- **Files:** `plugins/anvil/skills/afk/SKILL.md` (revise) and `plugins/anvil/skills/ticket-update/SKILL.md` (add one short section only).

**`afk` changes:**
- AFK turns on with `anvil afk on --quote`, using Saad's words.
- Pre-approved stops get `approve --pre`.
- Local commits on the work branch are always allowed, and pushes happen at the plan's commit points once the plan is approved. This replaces "never commit".
- The Stop hook keeps the run going, and a legitimate stop is a `## Stop note` in `progress.md`.
- The decision log lives in `progress.md`.
- The "never unlocks" list stays, minus commits on Anvil's own branch.

**`ticket-update` addition:** a section "From an Anvil plan" that maps the plan's task table to tickets:

| Plan | Ticket |
|---|---|
| Spec cell | Goal |
| Writes | In scope |
| Depends | Dependencies |
| Test list rows for the task | Done when |

Ticket comments are posted at commit points.

**Steps:**
1. Make the edits.
2. Self-check: size and forbidden words.
3. Report.

## T13: Packaging and skill lint

- **Spec:** §5, §8, §10.2.
- **Files:** `plugins/anvil/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `README.md` and `tests/anvil_cli/test_skills.py`.
- **`plugin.json`:** `"version": "1.0.0"`. Remove `dependencies` entirely. The description says what Anvil is: "Saad's development workflow: brainstorm, spec, plan, parallel build, verify, finish." Keywords stay.
- **`marketplace.json`:** remove `allowCrossMarketplaceDependenciesOn`, and update both descriptions.
- **`README.md`:**
  - what's inside: the new skill table;
  - install (no Superpowers prerequisite);
  - turning on auto-update for this marketplace;
  - "bump `version` on every release";
  - coexistence with Superpowers (the three setups from §7.13);
  - credits and NOTICE;
  - the layout.
- **`references/upstream.md`.** The upstream-watch procedure:
  1. Run `gh release list -R obra/superpowers`.
  2. For each new release, diff the source files named in the `adapted from` comments: `git diff v7.0.2..vX -- <paths>` in a clone.
  3. Record adopt or reject, with a reason, in a dated table in this file.
  4. Bump the `adapted from` versions for the files adopted.

  The trigger is manual, as listed in the README's maintenance section.
- **`test_skills.py`:**
  - for every `plugins/anvil/skills/*/SKILL.md`: frontmatter has `name` and `description`; size under 20,000; none of the forbidden words (case-sensitive `MUST`, `IMPORTANT`, `EXTREMELY`, `ABSOLUTELY`, `Iron Law`);
  - no `superpowers:` skill invocation, and no `TodoWrite`;
  - every `anvil <subcommand>` it mentions is in `cli.COMMANDS`;
  - every relative file link resolves;
  - every skill directory whose files were adapted (all except `anvil`, `afk`, `ticket-update`, `ui-mockup`, `ux-audit`, `cross-model`) has at least one `adapted from superpowers@` comment.
- **Steps:**
  1. Write `test_skills.py` and run it against the merged skills. Fix lint failures **only in the files T13 owns**. Failures in skill files go back to their lane's owner as fix tasks in the fix loop.
  2. Make the packaging edits.
  3. Report.

## T14: Evals

- **Spec:** §9.1.
- **Files:** `plugins/anvil/evals/<case>/{prompt.md, case.yaml, graders/*.md, files/**}`, following `skills/ticket-update/evals/` layout and `schema_version: "1.1"`.

**Cases** (one each; `tool_used: Skill` plus 2 to 4 `llm` or `file_exists` graders):

| Case | What it checks |
|---|---|
| `trivial-one-line` | A one-word copy fix: no spec or plan file, one check, Anvil states the size |
| `brainstorm-looks-up-first` | Asks nothing the fixture repo answers; questions are batched, each with a recommendation |
| `spec-format` | `spec.md` has parseable S-lines, ≤ 3 waiting-on-you items, and `Approved: no` |
| `plan-check-rejects-overlap` | Fixture plan with overlapping writes: the plan is marked sequential, with the reason |
| `change-retires-sline` | Mid-build change: S3 is retired, a new S-line is added, the change is classified, and `anvil stale` output is quoted |
| `reviewer-catches-overbuild` | Fixture diff with an unrequested helper: the reviewer flags it |
| `no-rerun-unchanged` | A test command is run twice on an unchanged tree: the second is reused |
| `afk-runs-through` | An AFK request with a pre-approval quote: no question is asked, and the decision log is written |
| `coexists-with-superpowers` | A Superpowers-like fixture skill is present: Anvil's skill is used |

**Steps:**
1. Write the cases.
2. Validate the YAML, by parsing it with `python -I -c` if PyYAML is present, or else by eye.
3. Report. **Don't run the evals.** T15 runs them in WSL2.

## T15: Integration and final verification (orchestrator)

1. Run the full suite, `python -I -m unittest discover -s tests -t .`, on the final merged state with `anvil run --scope full`, and record the output.
2. Run all smoke tests from the test strategy.
3. **Install locally:**
   - `claude plugin marketplace add <repo path>` (or `update`), then `claude plugin install anvil@mrerror-claude-skills`;
   - `claude plugin details anvil@mrerror-claude-skills` should list all skills and the hooks.
4. **Evals in WSL2.** Check `wsl -- claude --version`.
   - **If Claude Code isn't installed in WSL, stop and ask Saad** before installing anything there.
   - Otherwise run `claude plugin eval <repo>/plugins/anvil --concurrency 2` from WSL and record the scores and the with-vs-without deltas.
5. **Converge check** against this plan and the design. Every task is done. Every design section listed in the task table is covered, or listed as left to a later plan.
6. **Regression review** (Saad's request). This is a whole-branch review against the old Anvil (`git diff 46b7535 -- plugins/anvil`). Run it once with the final-review prompt and once with `cross-model`.
7. **Stop and hand over** to Saad: the report and these **actions needing his consent**:
   - removing the loose `~/.claude/skills/{anvil,afk}` copies (`cross-model-review` stays until phase 4);
   - adding the coexistence line to `~/.claude/CLAUDE.md`;
   - turning on marketplace auto-update;
   - squash-merging `anvil-rebuild` into `main`.
