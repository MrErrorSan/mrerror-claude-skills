# Anvil shared formats

These formats are pinned. Every skill, hook and `bin/anvil` module reads and writes exactly these; nothing else redefines them. The parsers live in `bin/anvil_cli/docs.py` and accept LF or CRLF files.

## Formats

Every skill and every CLI module uses exactly these.

**Topic folder.** The default is `docs/<slug>/`, holding `spec.md`, `plan.md` and `progress.md`. With size `direct`, only `plan.md` (spec part plus plan part) and `progress.md` exist.

**Header lines** (bullet lines near the top of `spec.md` and `plan.md`):

```
- **Approved:** no
- **Approved:** 2026-11-18 by Saad ("<quote>")
- **Approved:** pre-approved by Saad 2026-11-18 ("<quote>")
- **Approved:** skipped (AFK) 2026-11-18 ("<quote>")
- **Mode:** normal | redesign            (spec, or the spec part of a direct-size plan)
- **Size:** trivial | direct | full
- **Status:** draft | done <date>        (spec and plan; finish sets done)
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

- `Wave: <n> of <m>`: `<n>` is the wave number as written in the task table (a foundations wave is wave 0); `<m>` is the last wave's number.
- Indented sub-bullets under a task (`  - tests: …`, `  - minor (deferred): …`) are notes on that task; they are not tasks and aren't counted.
- `## Blockers` entries are `- ` bullets. The decision log is append-only: a reversed ruling gets a new entry naming the old one.
- Commit-point lines: `- C<k> <sha> pushed <date>`, `- C<k> <sha> not pushed (push failed <date>)`, or `- C<k> <sha> local <date>` for a `Push: no` row.
  The commit point that `finish` (or verify, in AFK) lands last is written before its own squash as `- C<k> (this commit) <date>`; the real sha and push result go in the finish report.

**State directory:** `<git common dir>/anvil/`, or `~/.claude/anvil/<sanitised-cwd>/` outside git. It's never committed. Files:

| File | Holds |
|---|---|
| `active.json` | `{slug, dir, size, stage, started}`; `started` is the epoch time of the first `topic start` (a same-slug restart keeps it; a record without it counts as 0) |
| `presented.json` | `{"spec"\|"plan": {hash, ts}}` |
| `prompts.jsonl` | `{ts, prompt}` per line, keeping the last 500 |
| `afk.json` | `{on, ts, quote}`; lifetime rules under "Calling the CLI" |
| `results.jsonl` | `{key, tree, prefix, cmd, scope, exit, tests_ran, ts, summary}`, plus `external: true` when set. `fresh` reuses the newest record for the key when it exits 0 and isn't external; scopes `targeted`, `full` and `smoke` also need `tests_ran > 0`, scope `check` (type-check, lint, build) doesn't |
| `stop.json` | `{hash, ts}`: sha256 of the `## Stop note` section text, saved by the stop hook; a Stop note counts as new only while its hash differs |

`result_key` includes the cwd prefix (`prefix`, the cwd relative to the repo root, empty at the root), so the same command run from two folders gets two keys. The active topic's `progress.md` is left out of the tree key, so status edits don't make results stale. Submodule contents are not part of the key (unsupported).

**CLI** (`anvil <subcommand>`). Every subcommand supports `--json`. Exit codes: 0 = ok or yes, 1 = no or refused (with a reason on stderr), 2 = usage error.

```
topic start <slug> [--size trivial|direct|full] [--dir <path>]   topic stage <spec|plan|build|verify|finish|done>   topic show   topic end
(`topic stage plan` and `topic stage build` are refused unless `check plan` / `check build` passes. Re-running `topic start` with a bigger `--size` steps a topic up a size. `topic start` with another slug while a topic is active is refused: `topic end` it first.)
present spec|plan
approve spec|plan --quote "<text>" [--pre] [--afk]
check plan|build
afk on --quote "<text>" | afk off | afk status
spec-lines [--live|--retired]
stale                                   (exit 1 only for a stale task or test; a result entry is informational)
plan-check
lane-check <task> --base <ref>          (paths inside the active topic folder are ignored: the orchestrator owns them)
run [--scope targeted|full|smoke|check] [--external] -- <cmd…>
fresh [--scope …] -- <cmd…>
progress
hook session-start|user-prompt-submit|pre-tool-use|stop        (reads hook JSON on stdin)
```

## Worked examples

**S-lines** under `## Spec lines`:

```markdown
## Spec lines

- ~~**S1** Saving a draft keeps the cursor position.~~ RETIRED → S4 (2026-11-20, CR: cursor moves to the end instead)
- **S2** A draft is saved every 30 seconds while the editor has unsaved changes.
- **S3** Closing the tab with unsaved changes asks before leaving.
- **S4** After a save, the cursor moves to the end of the document.
```

**Task table** under `## Task table`. Writes are backticked, so a glob with a comma inside braces stays one item.

```markdown
## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S2 | `src/drafts/types.ts` | - | - | 0 | yes |
| T2 | S2, S4 | `src/drafts/autosave.ts`, `src/drafts/autosave.test.ts` | - | T1 | 1 | yes |
| T3 | S3 | `src/editor/{leave-guard,leave-guard.test}.ts` | port:5173 | T1 | 1 | yes |
| T4 | S2 | `config/autosave.json` | - | T1 | 1 | skip (fully specified) |
```

**Test list** under `## Test strategy`:

```markdown
## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `src/drafts/autosave.test.ts` | keep | S2, S4 | Drafts lost after a crash | T2 |
| `src/editor/leave-guard.test.ts` | keep | S3 | Unsaved work closed without a prompt | T3 |
| smoke: open the editor, type, wait 30 s, reload, text is still there | smoke | S2 | The whole autosave path | T2 |
| `src/drafts/fixtures.ts` | scaffold | - | - | T2 |
```

**Commit points** under `## Commit points`:

```markdown
## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | waves 0–1 (T1, T2, T3, T4) | `feat(drafts): autosave and leave guard` | yes |
```

A cell that needs a literal `|` writes it as `\|`.

## Calling the CLI

**Is `bin/` on the Bash tool's PATH?** Yes. The Claude Code plugins reference, section "Standard layout", says of the `bin/` directory: "Files here are on the Bash tool's `PATH` while the plugin is enabled, so Claude runs them as bare commands." The same page notes that claude.ai and Cowork don't install a plugin that has a top-level `bin/` directory, and that `${CLAUDE_PLUGIN_ROOT}` is not set in the environment of Bash tool commands (it is substituted inline in skill content). Source: <https://code.claude.com/docs/en/plugins-reference#standard-layout>, checked 2026-11-18.

**How skills call it.** Skills write commands as bare `anvil <subcommand> …`. When a bare `anvil` isn't found, they use the absolute path that the session-start hook states:

- Git Bash, macOS, Linux: `<plugin root>/bin/anvil <subcommand> …`
- cmd.exe or PowerShell: `<plugin root>\bin\anvil.cmd <subcommand> …`

Both wrappers find Python (`python`, then `py -3`, then `python3`, checking every hit on PATH and skipping any path containing `WindowsApps`) and run it with `-I`. Under Git Bash, `bin/anvil` turns off MSYS path conversion, so an argument such as `--quote "/clear the cache"` reaches the CLI unchanged; the CLI drops those settings again before it runs a test command.

**Topic folder path.** `active.json` stores the topic `dir` repo-relative, with forward slashes (`topic start --dir` is resolved against the cwd first). Every command resolves it against the repo root (`git rev-parse --show-toplevel`; the cwd outside git), so the CLI finds the topic docs from any subdirectory.

**Stops and AFK.**

- `approve --pre` accepts a quote (3+ words) only from prompts logged at or after the last prompt logged at or before the topic's `started`: the request that started the topic counts, earlier work's prompts don't.
- AFK ends with its run. `topic end` turns it off. A fresh `topic start` (no active topic) turns it off unless it was turned on from the latest prompt, which keeps `afk on` then `topic start` in one turn working (`ts` is then restamped to `started`). A logged prompt with no AFK phrase turns it off. AFK whose `ts` is older than the active topic's `started` counts as off: `afk status`, `approve --afk` and the session-start fact all read it that way.
- In AFK the Stop hook never blocks while a task is `[~]` (lanes re-invoke the session). Otherwise it blocks while `[ ]` tasks are open or the topic stage is `build` or `verify`, until a new Stop note is written. `topic stage finish` releases it.
- `prompts.jsonl` holds only Saad's messages. UserPromptSubmit also fires for turns Claude Code starts itself (a background subagent reporting back, a scheduled `/loop` firing, a message from another session) and carries no origin field, so the hook skips any prompt carrying the harness's injected-message markers (`<task-notification`, `[SYSTEM NOTIFICATION`, `<agent-message`, …; `gate.INJECTED_RE`), and every gate ignores such records. Those turns never pass a stop or end AFK. This is a content check: a new wrapper format would need adding to `INJECTED_RE`.
