---
name: debug
description: Use when a bug, test failure, build failure or unexpected behavior has a cause that isn't obvious, before proposing a fix - at any Anvil stage, inside a build lane, or when Saad reports that something is broken. Also use when a fix didn't work, or the same failure keeps coming back.
---
<!-- adapted from superpowers@7.0.2: skills/systematic-debugging/SKILL.md -->

# Debug

Find the root cause before changing any code. A fix aimed at the symptom usually moves the bug somewhere else, and each guess that half-works makes the next one harder to read.

So the rule is: no fix until Phase 1 has produced a cause you can state. The four phases run in order.

## Where you came from

Debug runs inside another stage and goes back to it when done. Check `anvil topic show` first:

- **No active topic:** run the phases; skip the `progress.md` and S-line steps.
- **Stage `spec` or `plan`:** until the plan is approved, a hook holds edits in the repo outside the topic folder. Test hypotheses with commands, or with throwaway scripts outside the repo (the hook allows those). Instrumentation inside the repo waits for the build. A hypothesis only a code change can confirm is logged with its confidence, and the plan's repro task confirms it. Stop after Phase 3 and hand back: the bug, the expected behavior and the reproduction go into the spec part; the repro test and the fix become plan tasks.
- **Stage `build`, `verify` or `finish`:** run all four phases, log in `progress.md` (unless you're an implementer), then return to the stage.
- **Inside a lane** (any implementer subagent, sequential mode included): `progress.md` belongs to the orchestrator; don't edit it. Put the cause, the fix and the test in your report.

## Phase 1: Root cause

1. **Read the error.** All of it: the stack trace, line numbers, file paths, error codes, and any warnings around it. It often names the answer.
2. **Reproduce it.** Find the exact steps and check that they trigger it every time. If it won't reproduce, gather more data rather than guessing. To repeat a test run on an unchanged tree, prefix the command with `ANVIL_RERUN=1 `; otherwise the fresh-result hook hands back the last green result.
3. **Check what changed.** `git diff`, recent commits, new dependencies, config, environment differences.
4. **Instrument component boundaries.** When the failure crosses components (CI → build → signing, API → service → database), log what enters and leaves each one, and whether config and environment reach it. Run once, see which boundary breaks, then look at that component.
   ```bash
   echo "workflow: IDENTITY $([ -n "${IDENTITY:-}" ] && echo set || echo unset)"  # layer 1
   printenv IDENTITY >/dev/null && echo "IDENTITY in environment" || echo "IDENTITY not in environment"  # layer 2
   security find-identity -v  # layer 3
   ```
5. **Trace the data back.** When the error is deep in the call stack, ask where the bad value came from, and keep going up the callers to the source. Fix there. The technique is in [root-cause-tracing.md](references/root-cause-tracing.md).

When something appears during the test run but you can't tell which test causes it, bisect with the bundled script. Run it from the project root: it uses `find .` and runs `npm test <file>` one file at a time, stopping at the first file that creates the path. For another runner, adapt the test command in a copy.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/debug/scripts/find-polluter.sh" '.git' 'src/**/*.test.ts'
```

If `CLAUDE_PLUGIN_ROOT` isn't set, use `scripts/find-polluter.sh` under this skill's base directory.

## Phase 2: Pattern

1. **Find working code** like the broken code, in the same codebase.
2. **Read the reference fully** if you are following a pattern or a library's documented usage. Skimming is where the missing step hides.
3. **List every difference** between working and broken, however small. Don't rule one out because it "can't matter".
4. **Note the dependencies:** other components, settings, environment, and the assumptions the code makes.

## Phase 3: Hypothesis

1. **State one hypothesis:** "X is the root cause because Y." Be specific.
2. **Test it with the smallest change**, one variable at a time.
3. **Check the result.** Not confirmed: form a new hypothesis. Don't stack another change on top of the last one. Confirmed: while a topic is active and you're not an implementer, log the root cause as a decision-log entry in `progress.md` ([formats.md](../../references/formats.md), newest first), then go to Phase 4:
   ```
   - 2026-11-18 **Root cause: <what is wrong, where>** — <the evidence>. Confidence: high|medium|low. Changes if: <what would disprove it>.
   ```
   The log is append-only. If a logged cause is later disproved, add a new entry that names the old one.
4. **When you don't understand something,** say so plainly, then research it or ask. A confident guess costs more than the question.

## Phase 4: Fix

1. **Write the repro test first.** The simplest test that fails because of this bug: an automated test where the project has a framework, a one-off script where it doesn't. Run it and see it fail for the bug's reason, not a typo or an import. Here test-first is the cheapest order ([test-policy.md](../../references/test-policy.md)).
2. **Fix the root cause.** One change. No "while I'm here" improvements and no bundled refactoring.
3. **Run the test for the fix** through the CLI, so the result is recorded and reused:
   ```bash
   anvil run --scope targeted -- <test command>
   ```
   Read the output: the repro passes, the tests around it still pass, and the original symptom is gone. Report what the output shows, not what you expect it to show.
4. **Keep the repro test.** Give it the S-line whose behavior it guards, in its name or a comment beside it, and say what breaks if it fails. If no live S-line describes the correct behavior, the spec has a gap: say so, and the calling stage adds the S-line before the test is kept. It also adds the test's row to the plan's `## Test strategy` list (type `repro`, its S-line, what breaks if it fails), so `anvil stale`, the edit warning and finish's report see it. In a lane, your report asks the orchestrator to add it.
5. **Log the fix** while a topic is active and you're not an implementer:
   ```
   - 2026-11-18 **Fix: <the change>** — <why it addresses the root cause>. Test: `<file>` (repro, S3). Confidence: high. Changes if: <fact>.
   ```

### When the fix doesn't work

Count the fixes you have tried. Fewer than three: go back to Phase 1 with what the failed fix taught you.

**Three failed fixes means the architecture needs questioning,** not a fourth fix. The signs:

- each fix uncovers new shared state, coupling or a problem in a different place;
- a fix needs a large refactor to land;
- each fix creates new symptoms somewhere else.

Ask whether the pattern is sound at all, or whether it is being kept out of inertia. This is a design problem, not a failed hypothesis, so try nothing else first:

- **In a lane:** report `BLOCKED`, with what you tried and what each attempt showed.
- **In AFK or a pre-approved build:** nothing asks Saad. Log your ruling in the decision log. If every path is a guess, add a `- ` bullet under `## Blockers` and a dated `## Stop note` entry, and stop.
- **Otherwise:** ask Saad, with the same account.

While you are stuck (three failed fixes, or no cause after a full Phase 1) and you're not an implementer, add a `- ` bullet under `## Blockers`: what fails, what you ruled out, and what you need. Remove it when it clears.

## Signs you have skipped ahead

Go back to Phase 1 when you notice yourself thinking:

- "Quick fix for now, investigate later."
- "Just try changing X and see."
- "Change several things, then run the tests."
- "Skip the test, I'll check it by hand."
- "It's probably X, let me fix that."
- "I don't fully understand it, but this might work."
- "The pattern says X, but I'll adapt it."
- A list of fixes with no investigation behind it.
- "One more attempt" after two have failed.

The same goes when Saad says "Is that not happening?" (you assumed), "Will it show us...?" (gather evidence), "Stop guessing", "Think harder" (question the fundamentals), or "We're stuck?".

| Thought | What's true |
|---|---|
| "It's simple, I don't need the process." | Simple bugs have root causes too, and the process is quick on them. |
| "No time for process." | Guess-and-check takes longer than investigating. |
| "I'll write the test once the fix works." | A test written after the fix may never have failed, so it proves nothing. |
| "I see the problem." | Seeing the symptom is not the same as knowing the cause. |

## When there is no root cause

If the investigation shows the problem really is environmental, timing-dependent or external. Then write down what you investigated, add the handling that fits (a retry, a timeout, a clear error message), and add logging so the next occurrence leaves evidence. Most such conclusions are an investigation that stopped early, so check that Phase 1 was complete.

## Quick reference

| Phase | Do | Done when |
|---|---|---|
| 1. Root cause | read errors, reproduce, check changes, instrument, trace | you can say what is wrong and why |
| 2. Pattern | find working code, compare | the differences are listed |
| 3. Hypothesis | one theory, smallest test | it is confirmed, or replaced |
| 4. Fix | repro test, one fix, `anvil run --scope targeted` | repro passes, nothing else broke, logged |

## References

- [root-cause-tracing.md](references/root-cause-tracing.md): trace a bug back through the call stack to the original trigger.
- [defense-in-depth.md](references/defense-in-depth.md): after the fix, add validation at each layer the bad data passed through.
- [condition-based-waiting.md](references/condition-based-waiting.md): replace sleeps in flaky tests with waits on the real condition.
