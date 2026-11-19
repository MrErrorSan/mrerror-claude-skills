---
name: verify
description: Use when an Anvil build has finished and handed over (every task `[x]` in `progress.md`, stage `verify`), when Saad runs `/anvil:verify`, or when he asks to check an Anvil topic against its spec, re-run the converge check, or confirm the work is really done before finishing.
---
<!-- adapted from superpowers@7.0.2: skills/verification-before-completion/SKILL.md -->
<!-- adapted from superpowers@7.0.2: skills/requesting-code-review/code-reviewer.md -->

# Verify

Verify proves the built work does what the live spec lines say, on the final merged tree, with real output. It ends with the converge check clean, or with the leftovers stated plainly, lands the last commit point on the synced branch, and reports to Saad.

Prove each thing once. A green targeted run from the build, on this exact tree, is evidence: `anvil fresh` says so. Don't rerun a suite to feel sure.

## Evidence before claims

A claim about the work (it passes, it's fixed, it meets S3) is backed by output you can quote: a command's summary line and exit code, a curl response, a browser snapshot. Without that output, state what you actually know.

For each claim:
1. Name the command or check that would prove it.
2. Get its result: a fresh recorded result (below) or a new run of the whole command.
3. Read the output: exit code, failure count, the lines that matter.
4. Say what it shows. If it doesn't confirm the claim, state the real status with that output.

| Claim | Needs | Not enough |
|---|---|---|
| Tests pass | the suite's summary line: 0 failures | an earlier run on another tree, "should pass" |
| Build or type-check clean | the command's exit 0 | the linter passing |
| Bug fixed | the original symptom, rechecked | code changed |
| An S-line is met | behavior evidence for it | tests passing |
| An agent finished | the diff shows the change | the agent's report |

Words like "should", "probably" and "seems to", or "Done!" before any output, mean the check hasn't happened yet.

**Reuse comes first.** Every test run made through `anvil run` is recorded against the tree, the command and the environment. Before rerunning anything, ask:

```bash
anvil fresh --scope <the scope it ran with> -- <the same command>
```

Exit 0 means a passing result exists for this exact tree: quote its summary as the evidence and don't rerun. Exit 1 means run it. A result is never reused when it touched a live service (`--external`), or when a test run ran no tests; a `check` run (type-check, lint, build) needs only exit 0. Test rules: [test-policy.md](../../references/test-policy.md).

## Entry

1. `anvil topic show`. The stage should be `verify`, set by `anvil:build`. If the build is still open (tasks not `[x]` in `progress.md`), say so and go back to `anvil:build`. If every task is `[x]` but the stage wasn't moved, run `anvil topic stage verify`.
2. Read the plan's `## Test strategy` (the smoke paths, keep tests and full-suite command), the `Type-check:`, `Lint:` and `Build:` commands, and the plan header's synced branch. Read `progress.md`: the per-task notes, deferred minors and parked findings.
3. The topic's whole diff runs from the synced branch before the first commit point (`<C1 sha>^`, from `## Commit points` in `progress.md`), or from the synced branch tip if none has landed, to the work branch's HEAD. Call this RANGE. The commit point closing the last wave hasn't landed: it's left for this skill's exit, so fixes made here travel in it. Work on the work branch.
4. Notes go in `$(git rev-parse --path-format=absolute --git-common-dir)/anvil/build/<slug>/verify.md` (create the folder if the build already removed it). `finish` reads that file for its report, so keep real output in it, trimmed to the lines that matter.

## 1. Smoke paths

Run each smoke path from the plan's test list. They are the behavior evidence for the converge check.

- A command: `anvil fresh --scope smoke -- <cmd>` first; exit 0 means a passing result for this tree exists, so quote it. Otherwise `anvil run --scope smoke -- <cmd>`. Add `--external` when it touches a live service or the network; those runs are never reused, so `fresh` doesn't help them: run them directly.
- A browser step: chrome-devtools-mcp first (navigate, act, take a snapshot or screenshot, read the console); playwright-core if the MCP isn't available. Save screenshots next to `verify.md` and note the path.
- An HTTP path: curl, with the status line and the part of the body that matters.

Record each path, the command or steps, and the real result in `verify.md`. A smoke path that fails is a finding for the fix loop (section 5), unless its cause isn't obvious: then `anvil:debug` first.

## 2. The converge check

`anvil spec-lines --live` lists the S-lines to check. Retired lines are out: run `anvil stale`, and any task or test it lists as still naming a retired line is a finding. Its `result: no recorded run for the current tree` line is expected until the full run in section 6 and isn't a finding.

Sort every live S-line into one of four:

| Verdict | Means |
|---|---|
| **met** | behavior evidence shows it working: browser, curl or CLI output |
| **partial** | some of it works; say which part doesn't |
| **missing** | nothing in RANGE does it |
| **contradicts** | the code does something the line rules out |

"Met" needs behavior evidence. A passing keep test helps, but on its own it shows the test passes, not that the behavior is there. Where no smoke path covers an S-line, get the evidence directly: run the CLI, curl the endpoint, drive the page. When the behavior can't be exercised here (it needs a live account, hardware, a production-only service), mark the line **partial**, say why, and name what Saad would check.

The spec says what the software does; it doesn't list every input it will meet. Where it's silent, judge by what a reasonable person using it would expect: a blank field, a slow network, a second click, a file with spaces in its name. A break there is a finding against the nearest S-line.

**Unrequested.** Go through `git diff --stat RANGE` and the behavior you saw. Any file or behavior no live S-line asks for goes on the unrequested list, with the over-building checklist from [simplicity.md](../../references/simplicity.md) applied to the diff: items (a) to (f), each with file and line. Each item is either justified by naming the S-line that needs it (log that in the decision log) or removed in the fix loop.

**Declined to judge.** List anything you looked at and set aside as outside the spec, one line each, with the reason. Nothing set aside is dropped silently.

Write the result to `verify.md`:

```
| S-line | Verdict | Evidence |
|---|---|---|
| S2 | met | `anvil run --scope smoke`: "draft restored after reload" (exit 0) |
| S3 | partial | prompt shows on tab close; not on window close (screenshot s3-window.png) |
Unrequested: src/drafts/retry.ts:12 (b) a retry option no S-line asks for
Declined to judge: ...
```

## 3. UI work

When the work changed a UI, run `anvil:ux-audit` on the built UI: against the chosen mock when the topic has one (`<topic folder>/mocks/`), against its heuristics otherwise. Its findings join the fix loop. Findings that need Saad's call (a design choice the mock and spec don't settle) are listed for him, not fixed.

## 4. A second model

Before calling it done, run `anvil:cross-model` on the diff when the change is large or expensive to reverse: a migration or data change, a public API or file format, auth or permissions, deleting data, or a diff across many files. Triage what it says the way a review is triaged: verify each claim against the code before acting on it.

## 5. The fix loop

Every partial, missing or contradicts verdict, every unrequested item that isn't justified, every failed smoke path and the audit and second-model findings that hold up go through `anvil:build`'s fix rules: grouped by disjoint files, one fixer per group (you, for an inline build), a scoped re-review only when a fix reached beyond its findings' lines, the 5-round cap ([batched fixes](../build/references/waves.md), [receiving a review](../build/references/receiving-review.md)). A finding that conflicts with a decision Saad made (an S-line he approved, a logged decision) goes through the build's change flow-back instead of being fixed quietly.

After each round, recheck only the S-lines and smoke paths the fix touched, and update `verify.md`. Loop until every live S-line is met and the unrequested list is resolved, or until what's left can't be fixed here (the cap is reached, Saad's call is needed, the behavior can't be exercised). Those are the **leftovers**.

## 6. The full suite, once

When the tree has stopped changing, run the full suite once, on this final state:

```bash
anvil fresh --scope full -- <full-suite cmd>   # the build's last wave check may already cover this tree
anvil run --scope full -- <full-suite cmd>     # only if fresh says no
```

Then run each of the type-check, lint and build commands that isn't `none`, once on this tree, with the `check` scope:

```bash
anvil fresh --scope check -- <cmd>
anvil run --scope check -- <cmd>     # only if fresh says no
```

Resolve the warnings that matter; never hide one (no lint-disable comment or config change to mask the output). Put the summary lines in `verify.md`. A failure goes through the fix loop, and then the suite runs again on the new tree: a green result only proves the tree it ran on.

## Short form: an inline build

For an inline build (3 tasks or fewer), verify is a few calls, not a ceremony:
1. One Bash call: `anvil stale`, each smoke path through `anvil run --scope smoke`, and the full suite (`anvil fresh --scope full -- <cmd> || anvil run --scope full -- <cmd>`).
2. One Write of `verify.md`: the converge table (each S-line met, partial, missing or contradicts, with the smoke output as evidence) and the unrequested list.
3. Fix anything that isn't met (you are the fixer), rechecking only what the fix touched.
4. The exit below, with the done markers and the squash in one Bash call: set the Status and Stage lines and the `C1 (this commit)` line with Edits first, then `git add <topic folder> && git commit -m "docs(<slug>): done markers" && git switch <synced> && git merge --squash anvil/<slug>/work && git commit -m "<message>" && git branch -f anvil/<slug>/work <synced> && anvil topic stage finish`. You don't need to open `finish`: these are its sections 2 to 5 for this case (an inline build has no scaffold tests unless the plan lists some).

## Exit: land the work

Verify lands the last commit point itself, in every mode, so the work is on the synced branch when Saad reads the report. `/anvil:finish` stays for what needs him: pushing or merging beyond the plan's commit points, a PR, the ticket, deleting branches. Nobody has to run it for the work to be in.

1. Follow sections 2 to 4 of [finish](../finish/SKILL.md) (entry checks, scaffold tests, done markers). Ask nothing; log each choice in the decision log. A red entry check stops the landing: no squash; write why under `## Stop note` in `progress.md`, commit it on the work branch, and report it.
2. In AFK, write the report (below) under `## Stop note` in `progress.md` before the squash, so it travels in the last commit point and the Stop hook lets the turn end.
3. The squash, and the push only if the plan's last commit-point row says yes: section 5 of finish.
4. `git switch <synced>` (so the checkout shows the landed work), then `git branch -f anvil/<slug>/work <synced>`. Deleting the work branch is `finish`'s clean-up.
5. `anvil topic stage finish`. The topic stays listed until new work parks it (`topic start` does that by itself for a topic at `finish`) or `/anvil:finish` ends it.

Leftovers don't block the exit; they're named in the report, and Saad decides whether to ask for more work.

## The report

Saad reads this one message to decide whether the work is done. Plain words, his language, no internal ids (S3, T1, C1, RANGE) unless he asked for them: the docs hold those.

1. **What shipped**, one line per behaviour, with where it is: "Landed on `feature/x` as `a1b2c3d`. Nothing pushed." (or the push result).
2. **How it was checked:** a small table of the real commands with their exit codes and the lines that matter (suite summary, a smoke run's actual output). Quote, don't paraphrase.
3. **Calls I made for you**, numbered, most worth checking first, each with what it costs to reverse ("--top 0 prints nothing; flipping it to an error is a one-line change").
4. **Leftovers and deferred minors**, each with why it's left.
5. Only if something needs him: the one question, or "Run `/anvil:finish` to push and clean up" when the plan's push or a merge is still open. Never ask him to run a command while AFK is on.
