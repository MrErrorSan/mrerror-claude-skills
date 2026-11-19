# Claude + Anvil vs Claude + Superpowers vs plain Claude

- **Date:** 2026-11-19. This builds on [2026-11-18-ab-results.md](2026-11-18-ab-results.md), with two harness corrections (§6).
- **Data:** suite `full`, 7 cases × 3 runs × 3 arms on Opus 5.5 high, with 6 c2 runs rerun after a harness fix. The raw data is in [summary.json](../../abtest/results/full/summary.json).
- **Arms:**
  - **Anvil** = Anvil 1.0 (tag `anvil-v1.0`);
  - **Superpowers** = Superpowers 7.0.2;
  - **plain** = no plugin.
- **Sources:**
  - hidden tests and timings from the harness;
  - quality from a blind Opus judge (21 replicate groups);
  - behaviour from two independent transcript reviews (one of Anvil, one of Superpowers and plain).

## 1. The headline

| | Claude + Anvil 1.0 | Claude + Superpowers | Plain Claude |
|---|---|---|---|
| **Hidden tests passed** | 191/195 (98%) | 193/195 (99%) | 193/195 (99%) |
| Core / edge / regression tests | all passed | all passed | all passed |
| Runs with every test passed | 17/21 | 19/21 | 19/21 |
| **Total agent time** | **165 min** | 68 min | **40 min** |
| **Total cost** | **$60.69** | $16.60 | **$9.41** |
| User turns needed | 33 | 21 | 13 |
| Test-suite runs | 237 | 123 | 59 |
| Files with rewritten line endings | **5** | 11 | 12 |
| Spec or plan docs written | 15/21 runs | 3/21 (c5 only) | 3/21 (c5 only, a spec only) |
| Claude co-author trailers | 0 | 0 | 0 |
| **Blind judge, mean 1–5** | 3.10 | **3.81** | 3.52 |
| Judge first places (of 21) | 4 | **9** | 8 |
| Judge mean rank (1 = best) | 2.43 | **1.71** | 1.86 |

**Accuracy is a three-way tie.** No arm failed a single test that the request, common sense or the existing suite defined. Every miss was a `brief` test, something only knowable by asking:
- **Anvil missed 4:** c3 ×3 (both export formats at once), and c2 ×1 (`--top 0`).
- **Superpowers missed 2:** c3 ×2.
- **Plain missed 2:** c3 ×2.

The c3 miss is the same guess in every arm: making `--csv` and `--json` mutually exclusive. It's a model habit, not a workflow one.

**What separates them is cost and process.**
- Plain Claude is fastest and cheapest, with the same accuracy.
- Superpowers costs about 1.7× plain, and is judged best.
- Anvil 1.0 costs about 4× plain and 2.4× Superpowers, and is judged last.

## 2. Judge scores by dimension

| Dimension | Anvil | Superpowers | Plain |
|---|---|---|---|
| Matches the request | 4.00 | **4.19** | **4.19** |
| Simplicity | 3.81 | **4.19** | **4.19** |
| Tests | **3.90** | 3.76 | 3.71 |
| Process fits the size | **2.48** | 3.90 | 3.86 |
| Communication | 3.05 | **4.05** | 3.95 |
| Your rules | **4.38** | 4.33 | 4.00 |
| **Overall** | 3.10 | **3.81** | 3.52 |

Anvil leads on tests and on your rules. It trails badly on process fit and communication, and slightly on simplicity.

## 3. Per case (medians of 3 runs)

| Case | Arm | Hidden % | Agent s | Cost $ | User turns | Suite runs | Subagents | Judge | Rank |
|---|---|---|---|---|---|---|---|---|---|
| **c1 typo** | Anvil | 100 | 27 | 0.18 | 0 | 1 | 0 | **5** | **1** |
| | Superpowers | 100 | 18 | 0.14 | 0 | 0 | 0 | 4 | 2 |
| | Plain | 100 | 25 | 0.14 | 0 | 0 | 0 | 4 | 3 |
| **c2 small feature** | Anvil | 100 | 327 | 1.60 | 3 | 7 | 2 | 3 | 3 |
| | Superpowers | 100 | **72** | 0.36 | 1 | 3 | 0 | **4** | **1** |
| | Plain | 100 | 75 | 0.38 | 1 | 4 | 0 | 3 | 2 |
| **c3 three parts, slow suite** | Anvil | 92 | 443 | 3.55 | 1 | 15 | 7 | 2 | 3 |
| | Superpowers | 92 | **88** | 0.34 | 0 | 3 | 0 | **4** | 2 |
| | Plain | 92 | 108 | 0.35 | 0 | 3 | 0 | 3 | **1** |
| **c4 bug by symptom** | Anvil | 100 | 44 | 0.25 | 0 | 1 | 0 | 4 | 3 |
| | Superpowers | 100 | 36 | 0.25 | 0 | 2 | 0 | **5** | **1** |
| | Plain | 100 | **32** | 0.18 | 0 | 1 | 0 | 4 | 2 |
| **c5 vague feature** | Anvil | 100 | 1263 | 6.32 | 3 | 16 | 8 | 3 | 3 |
| | Superpowers | 100 | 759 | 3.24 | 4 | 22 | 1 | 3 | 2 |
| | Plain | 100 | **337** | 1.13 | 1 | 6 | 0 | 3 | 2 |
| **c6 change after delivery** | Anvil | 100 | 609 | 2.83 | 2 | 17 | 4 | 3 | 2 |
| | Superpowers | 100 | 134 | 0.63 | 1 | 8 | 0 | 3 | 2 |
| | Plain | 100 | **108** | 0.45 | 1 | 3 | 0 | 3 | 2 |
| **c7 AFK** | Anvil | 100 | 941 | 4.37 | 1 | 17 | 8 | 2 | 3 (3/3 runs) |
| | Superpowers | 100 | 152 | 0.62 | 1 | 4 | 0 | **4** | 2 |
| | Plain | 100 | **129** | 0.50 | 0 | 2 | 0 | **4** | **1** |

## 4. How the model actually treats each plugin

**Anvil: always followed, at full weight.** The router fired on 21/21 runs.
- Every case above trivial got the whole flow: brainstorm, plan, build, verify. That included a docs stop, about 7 subagents per topic and a closing request to run `/anvil:finish`.
- The model never skipped a step to save time, even for a 14-line flag.
- Its own main thread spent a median of **474 s** reading skills and references, writing `plan.md` and `progress.md`, and calling the CLI. That's more than Superpowers' entire run on four cases.

**Superpowers: mostly ignored on Opus 5.5.** Skills fired in 9/21 runs; 12/21 fired none.
- **Brainstorming and writing-plans** fired only on c5 (3/3), where the request literally said "let's think it through". `systematic-debugging` fired on c4 (3/3); TDD fired 5 times.
- **verification-before-completion and requesting-code-review never fired** (0/21).
- **It chose to skip when the user was away.** c7-S-r2: "User's AFK… so I'll skip the interactive brainstorming".
- **Even without skills firing, it worked test-first:** failing test, then code, in 17/18 non-typo runs. Plain Claude did that in 1/18. The SessionStart text alone shifts the model's habits.
- **On c5, its full flow was slow too:** 759 s median, about 2.2× plain. In c5-S-r1, 430 s went into about 45 runs of a 7 s suite, chasing a flaky test with 25- and 20-run loops.

**Plain Claude: fast, direct, quietly decides.** It implements code-first, runs the suite once or twice, and reports in chat. It wrote a spec only on c5, and there built before approval in 2/3 runs ("spec was written and the code built in the same turn").

## 5. The problems the tests don't catch

| Issue | Anvil | Superpowers | Plain |
|---|---|---|---|
| Silent decisions (the judge flagged an edge case decided without saying) | 5/21 | 5/21 | **10/21** |
| Commits or branches nobody asked for | 0 (commits only per its plan) | 6/21 | 4/21 |
| Line endings rewritten (whole-file diffs) | **5 files** | 11 files | 12 files |
| Paper trail (spec, plan, decision log on disk) | **15/21** | 3/21 | 3/21 (spec only) |
| Asked a question the repo answers (c5) | **0/3** | 0/3 (but asked a storage A/B/C and the execution mode) | 0/3 |
| Named the c6 change as a change, and which tests it broke | partly (docs retire the old lines; chat is thin) | 0/3 | 0/3 |
| AFK: waited or asked anything (c7) | 0/3 before delivery; **stalled 1/3 after** | 0/3 | 0/3 |
| AFK decisions written to a file | **3/3** | 0/3 (chat only) | 0/3 (chat only) |
| Ran the tests on a typo (c1) | **3/3** | 1/3 | 0/3 |
| Scope creep (unasked fixes or limits) | low | c5: added a 50-character limit (3/3) and NFC normalisation; money() fixed unasked (3) | money() fixed unasked (2) |
| Destructive or careless commands | none found | c5-S-r3: `git checkout --` discarded its own uncommitted task | c5-V-r1: `taskkill /F /FI "WINDOWTITLE eq *"` |
| A real bug caught by review | **c7-A-r3 caught `&region` → `®ion` URL corruption; 8/9 other runs shipped it** | c5: a reviewer found real bugs (1 run) | none (no review) |
| Work left for the user to land | **14/14: "run `/anvil:finish`"** | no | no |
| Process jargon in chat (ids, stage names) | high | low | low |

### Implied issues on a larger codebase

- **Plain Claude:**
  - No plan, no review, decisions only in chat.
  - It makes silent calls twice as often as the others.
  - On multi-day or multi-person work, there's nothing to audit or resume from.
- **Superpowers:**
  - Its workflow only engages when the request asks for it.
  - When it does engage, it reruns the full suite in TDD loops (22 runs on c5). On a slow suite that's very expensive.
  - Test bloat: c5 ended with 29–40 tests.
- **Anvil 1.0:**
  - The right artifacts and the best discipline (paper trail, evidence, review that catches real bugs).
  - At a cost that doesn't scale down to the work.
  - It doesn't land its own work.
  - It talks in its own vocabulary.

## 6. Harness corrections since the first report

1. **Reply parsing crash (against Superpowers and plain).** Replies that began with `--top` were passed as a command-line argument, and `claude -p` parsed them as an option. That crashed the turn in all 6 Superpowers and plain c2 runs, and in no Anvil run.
   - **Fix:** agent turns now go through stdin.
   - The 6 runs were rerun. The originals are in `abtest/results/full/superseded/`.
   - Effect: on c2, Superpowers went from 113 s to 72 s and plain from 86 s to 75 s, and Anvil's c2 judge rank fell from 1st to 3rd.
2. **Line-ending rewrites were invisible to grading.** The diff compared text, not bytes. There's now an `eol_changes` metric, backfilled for every run.

Known remaining biases:
- **Toward Anvil:** the rubric rewards local Markdown reports, which come from your global CLAUDE.md.
- **Against Superpowers:**
  - Skill names are scrubbed to "[workflow]", which reads as jargon.
  - The judge only sees visible text, so tool-only verification goes unseen.

## 7. What this means for Anvil

Anvil's value is real but narrow. It's the only arm that:
- leaves a spec, plan and decision log on disk;
- reviews in a way that catches real bugs;
- keeps docs in step after a change;
- never touches line endings;
- never commits unasked.

None of that showed up as better hidden-test results on cases this small. The judge charged it heavily for the cost.

V2 ([../anvil-v2/2026-11-19-v2-plan.md](../anvil-v2/2026-11-19-v2-plan.md)) keeps those strengths and goes after the cost:
- small plans build inline with one review;
- verify lands the work;
- plain reports, taking from Superpowers and plain Claude what the judge rewarded:
  - evidence tables with real output;
  - a numbered "calls I made" list with the cost of reversing each;
  - one clear "landed / nothing pushed" line.

V2 is being measured on the same suite now.
