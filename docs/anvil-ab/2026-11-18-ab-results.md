# Anvil vs Superpowers: A/B results

- **Date:** 2026-11-18.
- **Suite:** `full`: 7 cases × 3 runs × 3 arms = 63 runs.
- **Arms:**
  - **A:** Anvil 1.0 (`plugins/anvil` at `06a092d`).
  - **S:** Superpowers 7.0.2.
  - **V:** no plugin.
- **Models:**
  - agent: `claude-opus-5-5` at effort high;
  - simulated Saad: Sonnet 5.5;
  - blind judge: Opus 5.5.
- **Method:** [2026-11-18-ab-test-design.md](2026-11-18-ab-test-design.md). The harness is in [abtest/](../../abtest/).
- **Raw data:**
  - [summary.json](../../abtest/results/full/summary.json): every run, plus the judge verdicts;
  - [timeline.json](../../abtest/results/full/timeline.json): where each run's time went;
  - [runs/](../../abtest/results/full/runs/): one record per run;
  - generated tables in [report.md](../../abtest/results/full/report.md) and [timeline.md](../../abtest/results/full/timeline.md).

> **Correction (2026-11-19).** A harness bug crashed the 6 Superpowers and no-plugin c2 runs: a reply starting with `--top` was parsed as a CLI option. They were rerun with the message on stdin. Corrected totals: Superpowers 68 min / $16.60 / judge 3.81; no plugin 40 min / $9.41 / judge 3.52; Anvil unchanged at 165 min / $60.69 / judge 3.10. Anvil's c2 rank fell from 1st to 3rd. Current numbers and the full three-way comparison: [2026-11-19-three-way-comparison.md](2026-11-19-three-way-comparison.md).

## Verdict

**Not ready to replace Superpowers yet.** The reason is speed and process, not correctness.

- **Correctness is a tie.** All three arms passed all 69 core tests and every edge-case and regression test.
  - Every miss in any arm was a `brief` test, which is only knowable by asking you.
  - Anvil missed 4, Superpowers 2 and no-plugin 3. Most of them were the same unasked c3 question, which every arm guessed the same way.
- **Anvil is 2.4× slower and 3.6× costlier overall.** Across the suite it used 165 agent-minutes and $60.69. Superpowers used 70 minutes and $17.03. No plugin used 40 minutes and $9.39.
  - On four of the seven cases, Anvil is 3–9× slower.
- **The blind judge ranked Anvil last overall.**

  | | Anvil | Superpowers | No plugin |
  |---|---|---|---|
  | Mean score (1–5) | 3.19 | **3.71** | 3.33 |
  | Process fit | **2.43** | 3.76 | 3.67 |
  | Communication | 3.14 | 3.81 | 3.62 |
  | First places (of 21) | 6 | 8 | 7 |

  Anvil is level or ahead on matching the request, tests and your rules. It loses on process fit and communication.
- **The upside is real.** Anvil settles edge cases before writing code, never asks what the repo already answers, keeps docs and code in step after a change, and its final review caught a real bug that 8 of 9 other runs shipped.

The slowness has fixable causes; see §3. The first five fixes there target the measured time sinks directly.

### Against the pass bar (design §6)

| Bar | Result |
|---|---|
| 1. Correctness ≥ Superpowers on every case | **Met.** Medians are equal on every case. |
| 2. Median time ≤ Superpowers, and clearly lower on c1 and c3 | **Failed.** c1 is 27 s against 18 s, and c3 is 443 s against 88 s. |
| 3. No more user turns than Superpowers | **Failed narrowly.** 33 against 28. The extra turns are mostly declined `/anvil:finish` requests. |
| 4. Judge mean ≥ Superpowers; no co-author trailers; doc rules kept | **Partly.** Judge 3.19 against 3.71. Trailers: 0 in every arm. The c5 doc rule was kept by every arm. |
| 5. No hangs, loops or false "done" | **Failed once.** c7-A-r2 refused to keep working while AFK and hit the turn cap. There were no false "done" claims. |

## 1. Per case (medians of 3 runs)

Agent time is the main session's active time, with the simulated user's thinking excluded. Judge rank is 1 to 3 within the replicate.

| Case | Arm | Hidden % | Agent s | Cost $ | User turns | Suite runs | Subagents | Judge | Rank |
|---|---|---|---|---|---|---|---|---|---|
| c1 typo | A | 100 | 27 | 0.18 | 0 | 1 | 0 | 5 | **1** |
| | S | 100 | 18 | 0.14 | 0 | 0 | 0 | 4 | 2 |
| | V | 100 | 25 | 0.14 | 0 | 0 | 0 | 4 | 3 |
| c2 `--top N` | A | 100 | 327 | 1.60 | 3 | 7 | 2 | 4 | **1** |
| | S | 100 | 113 | 0.49 | 3 | 6 | 0 | 3 | 2 |
| | V | 100 | 86 | 0.38 | 3 | 3 | 0 | 2 | 3 |
| c3 three parts, slow suite | A | 92 | 443 | 3.55 | 1 | 15 | 7 | 2 | 3 |
| | S | 92 | 88 | 0.34 | 0 | 3 | 0 | 4 | 2 |
| | V | 92 | 108 | 0.35 | 0 | 3 | 0 | 3 | **1** |
| c4 refund bug | A | 100 | 44 | 0.25 | 0 | 1 | 0 | 4 | 3 |
| | S | 100 | 36 | 0.25 | 0 | 2 | 0 | 5 | **1** |
| | V | 100 | 32 | 0.18 | 0 | 1 | 0 | 4 | 2 |
| c5 vague feature | A | 100 | 1263 | 6.32 | 3 | 16 | 8 | 3 | 3 |
| | S | 100 | 759 | 3.24 | 4 | 22 | 1 | 3 | 2 |
| | V | 100 | 337 | 1.13 | 1 | 6 | 0 | 3 | 2 |
| c6 change after delivery | A | 100 | 609 | 2.83 | 2 | 17 | 4 | 3 | 2 |
| | S | 100 | 134 | 0.63 | 1 | 8 | 0 | 3 | 2 |
| | V | 100 | 108 | 0.45 | 1 | 3 | 0 | 3 | 2 |
| c7 AFK import | A | 100 | 941 | 4.37 | 1 | 17 | 8 | 2 | 3 (3/3 runs) |
| | S | 100 | 152 | 0.62 | 1 | 4 | 0 | 4 | 2 |
| | V | 100 | 129 | 0.50 | 0 | 2 | 0 | 4 | **1** |

### What this comparison really measures

On Opus 5.5, Superpowers ran its own workflow (brainstorming, writing-plans, executing-plans) **only on c5**, where the request says "let's think it through before anything gets built".
- That happened in all 3 runs.
- On c4 it fired `systematic-debugging`, and twice `test-driven-development` elsewhere.
- Otherwise it fired nothing, and it behaves almost like the no-plugin arm.

Anvil ran brainstorm, plan, build and verify on every case above trivial size. That gives two different comparisons:

- **Full workflow vs full workflow (c5):** Anvil is 1.7× slower (1263 s against 759 s) and 2× costlier. Both are 100% correct and both kept the doc rule.
- **Anvil's workflow vs Superpowers' default behaviour (c2, c3, c6, c7):** Anvil is 3–6× slower for the same correctness.

The `-p` sessions may trigger Superpowers less than interactive use does. So the c5 number is the fairest like-for-like figure. To firm it up, a follow-up set is suggested in §6.

## 2. Where Anvil's time goes

From [timeline.md](../../abtest/results/full/timeline.md), medians over Anvil's 15 runs that started a topic:

| Component | Median s | Notes |
|---|---|---|
| Orchestrator's own model time | **474** | Reading skills and references, writing plan and progress docs, deciding. On its own this exceeds Superpowers' entire run on c2, c3, c6 and c7. |
| Subagents, waited on in the foreground | 355 | About 7 subagents per topic: implementer, reviewer, a fix round, a re-review, a whole-branch review on Opus, and another fix and re-review. |
| `anvil` CLI calls | 28 | Gates, plan-check, progress, `run` and `fresh`. |
| Test-suite runs | about 15 per topic | Superpowers about 4. Result reuse fired, but verify reran suites on purpose. |
| Parallelism | 1.0–2.0, mostly 1.0 | In c3 both tasks write `ledger/cli.py`, so plan-check correctly put them in sequence. Real parallel lanes never happened. |

The parallel speed-up Anvil was designed for (P33–P36) didn't show up on any case. Each per-task review loop costs more than it catches on small changes.

## 3. Findings, ranked

The evidence is in each run's `conversation.json` and `turn-*.jsonl` under `%LOCALAPPDATA%/Temp/anvil-abtest/full/<run>/`. The counts are Anvil runs.

### Critical

1. **Process cost doesn't scale down: 3–9× slower on small and medium work.**
   - **Evidence:** c2 is a 14-line flag and took 327 s against 113 s. c3 took 443 s against 88 s, and c7 941 s against 152 s.
   - **Driver:** every task gets implement, then review, then a fix round, then a re-review, then an Opus whole-branch review, then verify.
   - **Fix:**
     - A one-task or under-100-line direct plan builds **inline** with no per-task subagent review. It keeps one final review.
     - Run the whole-branch review only when there are 2+ tasks or the change touches 3+ files.
     - Re-review a fix round only when the fix touched code outside the finding.
2. **Work never lands: 14/14 topic runs end with "run `/anvil:finish`".**
   - **Evidence:** `finish` has `disable-model-invocation: true`.
   - **What's left behind:** the topic stays at stage `finish`, HEAD sits on `anvil/<slug>/work`, and in 10/14 runs the feature branch named in the plan still points at `main`.
   - **Cost:** 11 user turns across the suite were spent declining that step.
   - **Fix:** let verify make the squash commit on the work branch and close the topic, as AFK already does. Leave only merge and push for you.
3. **AFK refuses to keep going after delivery: c7, 2/3 runs; r2 hit the 6-turn cap.**
   - **Evidence:** "I've made the call, and it's to stop… `/anvil:finish` can only be started by you". This came after it had flagged its own parser weakness. Superpowers, given the same "keep going", fixed that exact weakness.
   - **Fix:** under AFK, never ask you to run a command. Treat "keep going" as permission to fix cheap, in-scope deferred items.

### Important

4. **The orchestrator's model time is the biggest single cost (median 474 s).**
   - **Fix:**
     - Trim what build and verify make the main thread read on every run (the reference files the trace shows being `cat`-ed).
     - Write `progress.md` less often: at wave boundaries, not after every step.
5. **Verify reruns suites that build already ran green (about 15 suite runs per topic, against about 4).**
   - **Fix:** verify trusts `anvil fresh` for any scope whose code hasn't changed since build, and only runs smoke paths and spec checks.
6. **Re-approval after your own dictated fix (c2, 2/3).**
   - **Evidence:** "Since the document changed after you read it, it needs your approval again". This was in reply to "approved, go ahead. one fix: `--top 0`…".
   - **Fix:** if the only edits are the ones you dictated, record the approval with your quote.
7. **`anvil run` doesn't convert POSIX paths on Windows (4/14).**
   - **Evidence:** `bin/anvil` exports `MSYS_NO_PATHCONV=1` for every command, so a `/tmp/...` argument reaches Windows Python unconverted and the run fails.
   - **Fix:** scope that setting to `--quote`, or convert path-like arguments with `cygpath` before running the test command.
8. **The edit hold is inconsistent.**
   - **c5-A-r1:** Edit on `docs/decisions.md` was denied twice, even though the project `CLAUDE.md` requires that file.
   - **c5-A-r3:** the same file was written by `cat >>` in Bash, and nothing held it.
   - **Fix:** allow docs that project rules require before approval, and treat Bash redirects the same as Edit.
9. **Heredoc doc edits break (6/14).**
   - **Evidence:** in c5-A-r3, a shell script emptied `spec.md` and the empty file was committed. In c3-A-r1, the approval message opens with "The shell heredoc failed…".
   - **Fix:** the skills say to edit Anvil docs with Edit or Write only.

### Minor

10. **Implementers rewrite line endings (5/14).** CRLF files come back as LF, and each costs a fix round. **Fix:** the lane brief says to keep each file's line endings, and to check `git diff --stat` before reporting.
11. **An unrequested restriction was presented as a requirement (c3, 3/3).**
    - **What happened:** "neither or both flags is a usage error" was listed under behaviour, not under "Calls I made", so the approval let it through.
    - **Not only Anvil:** Superpowers and no-plugin made the same guess 2/3 times each.
    - **Fix:** any restriction the request didn't state goes in the calls list.
12. **The change request was handled well in the docs but thinly in chat (c6, 3/3).**
    - **Good:** the spec marks the old lines as retired and points to the new ones (`~~S2~~ RETIRED → S9`), and the docs match the code.
    - **Thin:** there was no pushback and no stated cost. That's true in every arm, so P15 isn't really exercised.
    - **Missing:** the reply rarely names which tests changed (P18).
13. **Leftovers.**
    - The docs refer to "Saad" in the third person (14/14).
    - Harness notices leak into chat.
    - `plan.md`, `progress.md` and `spec.md` get committed with the feature. The judge flagged this as clutter on small changes.
    - The router's "Size: trivial…" preamble on a typo was called noise.

### Not a problem

The approval gate refused nothing wrongly in 21 Opus runs. The punctuation-mismatch refusal seen in the Haiku smoke test didn't recur. Every pre-approval in AFK was recorded as "Approved: skipped (AFK)".

## 4. Where Anvil did better

- **It settles edge cases before code (c2, 3/3).**
  - Anvil listed its calls on `--top 0`, negative N and too-large N in the plan. You corrected `--top 0` before anything was built.
  - Superpowers (2/3) and no-plugin (1/3) built `--top 0` as an error silently, then reworked it after delivery. One no-plugin run committed the uncorrected version.
- **It catches real bugs in review (c7-A-r3).** The final review caught `?a=1&region=us` being saved as `?a=1®ion=us`, an HTML-entity corruption. Anvil fixed and tested it. All 8 other c7 runs shipped it.
- **It doesn't ask what the repo already answers (c5).** Anvil stated the repo facts (SQLite, owner-private notes, no dependencies) and asked only product questions. Superpowers asked a storage question the brief leaves as "your call".
- **Its decision logs survive the session (c7, 3/3).** Each call is recorded with "Confidence: … Changes if: …" in `progress.md`, not only in chat.
- **Its docs stay in step with the code after a change (c6, 3/3).** Superpowers and no-plugin wrote no spec or plan to keep in step.
- **It follows your rules** (judge "rules" score 4.35, the highest). No co-author trailers, the doc-location rule kept, and `docs/decisions.md` updated.

## 5. Caveats

- **Small fixtures.** Parallel lanes need independent write sets, and small CLIs share one file. The phase-5 replay of a real multi-file feature (design §9.2) is still the fair test of fan-out.
- **`-p` vs interactive.** Superpowers fires its workflow less often here than you may see interactively. The c5 numbers are the like-for-like comparison.
- **The simulated user is a model.** It declined `/anvil:finish` by design (simulator rule 5), so finish time isn't counted for Anvil. Counting it would make Anvil slower, not faster.
- **Blinding is partial.** Anvil's docs (S-lines, `progress.md`) are recognisable even with names scrubbed.
- **Harness fixes during the run.** These didn't affect the results:
  - Cost now comes from the last call's cumulative `modelUsage`.
  - The simulator stopped volunteering commit instructions. This was fixed after the pilot; the full suite used the fixed version throughout.
  - Read-only git objects blocked run-folder resets, so three c5 r2 runs were rerun.

## 6. Suggested next steps

1. **Fix findings 1–5 first.** They're where the time goes.
   - Then rerun `python abtest/harness/ab.py run --suite full-v2 --arms A --runs 3`. Superpowers and no-plugin don't need rerunning, so this costs about $60 for Anvil's 21 runs.
   - Compare with `report`. The target is Anvil's median at or under 1.5× Superpowers on c2, c3, c6 and c7, with c2's and c7's wins kept.
2. **Fair full-workflow comparison (optional, about 12 runs).** Run c3, c6 and c7 with "plan it properly before building" added to the request for both Anvil and Superpowers. That forces both full workflows, so the comparison doesn't rest on c5 alone.
3. **Real-feature replay (design §9.2).** One multi-file feature with genuinely independent parts, to test parallel lanes.
4. **Keep this suite as the regression gate.** Rerun it after every Anvil change that touches build, verify or the router.
