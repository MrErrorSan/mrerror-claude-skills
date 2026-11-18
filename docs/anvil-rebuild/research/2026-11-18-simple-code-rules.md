# "N rules for simple code": claims, evidence, and what Anvil should keep

- **Researched:** 2026-11-18
- **Question:** Do the viral "4 rules" files (and similar prompts) make Claude write simple code without over-engineering? Which of them should Anvil adopt, and where in the flow?
- **Feeds:** [brainstorm notes](../2026-11-18-brainstorm-notes.md) §5 ("Simplicity stays a rule, but it must not anchor redesigns on old code") and session-evidence problem P4 (redesigns anchored on old code).
- **Sibling research, not repeated here:** [anthropic-guidance](2026-11-18-anthropic-guidance.md) §3.5 (Opus 5 scope sample, Fable 5.2 ownership finding), [community-frameworks](2026-11-18-community-frameworks.md) P5 (spec-kit converge "unrequested" bucket, GSD necessity review), [practitioner-sentiment](2026-11-18-practitioner-sentiment.md) §6 (catch it in the plan, checkable limits, a simplify pass, a fresh reviewer).

## How to read this

- **Fact** lines come from a dated source in the list at the end. GitHub stars and dates come from `gh api` on 2026-11-18 unless the line says otherwise.
- **Inference** lines are my reading of the facts.
- **No evidence** means I looked and found nothing measured behind the claim.
- "Size" means lines of delivered code. Fewer lines is not the same as better code. Every benchmark below measures size more carefully than it measures quality.

## Bottom line

1. **The "4 rules" are the Karpathy-inspired CLAUDE.md** (forrestchang/andrej-karpathy-skills, now multica-ai). It has 234,128 stars. Andrej Karpathy did not write it. **The repo publishes no evaluation.** The figure that circulates, "mistakes cut from 41% to 11%", traces to one X post with a self-reported method and no data.
2. **The only controlled tests of the Karpathy file show little or no effect on Claude-5-generation models.** On SWE-bench Verified (20 tasks, Sonnet 5), its scope was *looser* than no skill, and the model never invoked the skill. In a microbenchmark, it helped only on the underspecified task. On explicit "simple" and "surgical" tasks it changed nothing, because the bare model already passed.
3. **The strongest evidence belongs to a different file, Ponytail** (193,616 stars). On Opus 5.5 in Claude Code it cut delivered code by about half with no loss on hidden correctness checks. An independent tester confirmed the size effect. He also found that it drops about half of the "nice to have" features people wanted on vague prompts. **A seven-word prompt got the same size cut**, with more data-loss bugs and fewer tests.
4. **Claude Code already ships most of these rules in its own system prompt** ("Don't add features, refactor, or introduce abstractions beyond what the task requires … Three similar lines is better than a premature abstraction"). Anthropic removed over 80% of that prompt for Claude 5 models with "no measurable loss" ([E1](#sources)). Restating the rules in Anvil mostly duplicates the harness.
5. **The contrary evidence matches Saad's P4.** Anthropic measured that when the code is framed as someone else's, Fable 5.2 "tended to add to the existing structure … even when that duplicated existing code." A scope-limiting rule did not cancel the opposite effect either. "Preserve, minimise, reuse" is exactly that framing. It is right for edits and wrong for redesigns.
6. **For Anvil:** replace the five-line anti-slop posture with **three plain lines that know the mode** (normal change or redesign). Move the checkable parts into **the plan template** (every new piece names the spec line that needs it) and **one reviewer checklist item** that lists over-building in the diff. Keep spec-kit's "unrequested" bucket as the final check. Drop the rest.

---

## 1. The claims, verbatim

### 1.1 The Karpathy-inspired CLAUDE.md: the "4 rules"

**Facts**
- **Origin.** Karpathy posted "A few random notes from claude coding quite a bit last few weeks" on X on **2026-01-26** ([K0](#sources)). The lines the repo quotes are: "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should." And: "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."
- **The repo.** `forrestchang/andrej-karpathy-skills` was created **2026-01-27**, the day after the post. It now redirects to `multica-ai/andrej-karpathy-skills`. On 2026-11-18 it had **234,128 stars and 23,283 forks**. The last push was 2026-04-20. Issues are turned off, so the community talks only through PRs (216 so far). Stars over time, as reported by others: about 70k ([HN, Apr 2026](#sources)), 179k (Apr 2026, one blog), and 222,612 on 2026-10-23 ([OrcaRouter](#sources)).
- **Attribution.** Karpathy "did not write it, did not publish it, and as far as publicly available information shows, did not endorse it" ([Rusin, 2026-04-26](#sources)).
- **The file, verbatim** (`CLAUDE.md`, 65 lines, unchanged since April 2026):

> Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.
>
> **Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.
>
> **1. Think Before Coding.** **Don't assume. Don't hide confusion. Surface tradeoffs.** Before implementing:
> - State your assumptions explicitly. If uncertain, ask.
> - If multiple interpretations exist, present them - don't pick silently.
> - If a simpler approach exists, say so. Push back when warranted.
> - If something is unclear, stop. Name what's confusing. Ask.
>
> **2. Simplicity First.** **Minimum code that solves the problem. Nothing speculative.**
> - No features beyond what was asked.
> - No abstractions for single-use code.
> - No "flexibility" or "configurability" that wasn't requested.
> - No error handling for impossible scenarios.
> - If you write 200 lines and it could be 50, rewrite it.
>
> Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.
>
> **3. Surgical Changes.** **Touch only what you must. Clean up only your own mess.** When editing existing code:
> - Don't "improve" adjacent code, comments, or formatting.
> - Don't refactor things that aren't broken.
> - Match existing style, even if you'd do it differently.
> - If you notice unrelated dead code, mention it - don't delete it.
>
> When your changes create orphans:
> - Remove imports/variables/functions that YOUR changes made unused.
> - Don't remove pre-existing dead code unless asked.
>
> The test: Every changed line should trace directly to the user's request.
>
> **4. Goal-Driven Execution.** **Define success criteria. Loop until verified.** Transform tasks into verifiable goals:
> - "Add validation" → "Write tests for invalid inputs, then make them pass"
> - "Fix the bug" → "Write a test that reproduces it, then make it pass"
> - "Refactor X" → "Ensure tests pass before and after"
>
> For multi-step tasks, state a brief plan: `1. [Step] → verify: [check]` …
>
> Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
>
> **These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

- **Copies.** Robert Walaski's dev.to post "The 4 rules in my CLAUDE.md that fixed most of my bad Claude Code sessions" (Oct 13, 2026) restates the same four rules in shorter form ("No silent assumptions … Minimum code that solves the problem … Touch only what you must … Define success criteria. Loop until verified."). Many blogs repeat them with small wording changes.

### 1.2 The "41% to 11%" spin-off: 12 rules

**Facts**
- The circulating headline "Karpathy's 4 CLAUDE.md rules cut Claude mistakes from 41% to 11%" comes from an X article by @Mnilax, **2026-05-09** ([M1](#sources)). The method given is: "I tracked the same set of 50 representative tasks across 30 codebases for 6 weeks. Three configurations." And: "Mistake rate = task required correction or rewrite to match intent." The body also says "41% to 3%", which conflicts with the headline.
- It adds eight rules. The ones about over-building are: "Read before you write" (an unread function was duplicated), "Convention beats novelty" (React hooks were added to a class-component codebase), and "Surface conflicts, don't average them" (two error-handling patterns were merged, so errors were swallowed twice). Each rule rests on one anecdote.
- Repeaters: aibuilderclub.com (Jason Zhou, 2026-05-22) uses the 41%→11% figure as its lede with **no source, method, or dataset** ([M2](#sources)). Xeve (2026-05-25) cites "roughly 40% to near 3%" with no source.

### 1.3 Ponytail: the "laziness ladder"

**Facts**
- `DietrichGebert/ponytail`, created **2026-06-12**, **193,616 stars**, last push 2026-10-29. It is one prompt (`skills/ponytail/SKILL.md`, plus a compact `AGENTS.md`) and a plugin with review and audit commands.
- Verbatim core from `AGENTS.md`:

> Read the task and the code it touches. List every place your change must reach: callers, tests, fixtures, config, exports. … That is scope. Extra features are not.
>
> Take the first option that fully works:
> 1. Does it need to exist? Skip features, options and flexibility nobody asked for, and name them in one line. …
> 2. Already in this codebase (a helper, component, service, pattern)? Use it the way the surrounding code does.
> 3. Standard library or a platform feature? Use it, unless the project has its own. …
> 4. An installed dependency? Use it. Never add a dependency for a few lines.
> 5. Can it be one line a reader gets at a glance? One line.
> 6. Otherwise: the minimum code that works.
>
> - Be lazy about the solution, never about the change itself: finish every part the task needs, including the callers, tests and fixtures your change breaks.
> - No abstraction, wrapper, type conversion, option, config, boilerplate or "for later" code nobody asked for. … Deletion beats addition. Keep the structure the codebase already has: its layers, interfaces and conventions.
> - The shortest working diff wins, once you know everything it must touch. A one-liner that needs decoding is not short.
> - Code you move or merge keeps its error handling and validation.
> - Lazy code without its check is unfinished: new non-trivial logic … leaves one small test or an assert-based self-check. Trivial changes need none.
>
> Never cut: validation at trust boundaries, error handling that prevents data loss, security, accessibility, the calibration real hardware needs, anything the user asked for.

- The Karpathy repo has an open PR (#177, 2026-06-22) to add "three simplicity guidelines inspired by ponytail". A merged variant also exists (`karpathy-ponytail-skills`, 67 stars).

### 1.4 The seven-word prompt

**Fact.** Chase Hannegan's Ponytail test (2026-10-19) used this as a control in `agents.md`: **"follow YAGNI principles and prefer one-liner solutions."** ([C1](#sources))

### 1.5 Anthropic's own wording

**Facts**
- **Prompting best practices, "Overeagerness"** (current page, read 2026-11-18; it names Opus 4.5 and 4.6) ([A1](#sources)): "Claude Opus 4.5 and Claude Opus 4.6 have a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested. If you're seeing this undesired behavior, add specific guidance to keep solutions minimal." The sample:

> Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused:
> - Scope: Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.
> - Documentation: Don't add docstrings, comments, or type annotations to code you didn't change. Only add comments where the logic isn't self-evident.
> - Defensive coding: Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs).
> - Abstractions: Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task.

- **Same page, on forceful language:** "If your prompts were designed to reduce undertriggering on tools or skills, these models might now overtrigger. The fix is to soften any aggressive language. Where you might have said 'CRITICAL: You MUST use this tool when...,' you can use more normal prompting such as 'Use this tool when...' instead."
- **Prompting Opus 5, "Task scope and over-verification"** ([A2](#sources)): "Claude Opus 5 can also expand the scope of a task, adding steps that weren't requested or applying its own judgment about what the task should be." Sample: "Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole task, and stop short of actions that are clearly beyond what was asked."
- **Prompting Sonnet 5.5, "Steer initiative and scope"** ([A3](#sources)): "The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. It does this at every effort level, and more at higher effort. The requested change itself stays close to what was asked." Sample: "When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs, or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it." Result: "At `xhigh` and `max` effort, that paragraph reduces these additions and makes changes smaller overall."
- **Prompting Fable 5.2, "Say who owns the code"** ([A4](#sources)): "the model tended to add to the existing structure when the prompt said nothing about ownership or presented the code base as someone else's, even when that duplicated existing code." With "You are the owner and long-term maintainer of this codebase, and its design is up to you.", consolidation rose from "under 10 percent of runs" to "about 75 percent". Output tokens rose "about 70 to 80 percent", and the model "made changes nobody had asked for". Also: "A rule that limits scope doesn't cancel it … the model still consolidated duplicated code in more than half of runs when 'No drive-by refactors, renames or cleanups' appeared earlier in the same prompt."
- **Same page, "Keep caution from piling up":** "The model treats an instruction that contains 'never' as absolute. For example, write 'ask for approval before deleting files' instead of 'never delete files'". Also: "rewrite absolute rules with their scope and reason."
- **Claude Code's own system prompt** (third-party extraction, Piebald-AI tracker, fragment last changed 2026-07-20) ([A5](#sources)): "Don't add features, refactor, or introduce abstractions beyond what the task requires. A bug fix doesn't need surrounding cleanup; a one-shot operation doesn't need a helper. Don't design for hypothetical future requirements. Three similar lines is better than a premature abstraction. No half-finished implementations either." A second fragment covers "Don't add error handling, fallbacks, or validation for scenarios that can't happen … Only validate at system boundaries". A third, "Delivering work", says "The requested scope is the deliverable — don't quietly narrow, widen, or transform it" and "Reserve blocking questions … for cases where proceeding under any assumption would be unsafe".
- **"The new rules of context engineering for Claude 5 generation models"** (Thariq Shihipar, Anthropic, **2026-07-24**) ([E1](#sources)): "We removed over 80% of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5 with no measurable loss on our coding evaluations." "We found that we were overconstraining Claude Code, both through our system prompt and in our CLAUDE.md files and skills." The heading is "Then: Give Claude rules. Now: Let Claude use judgement." One old rule was replaced with: "Write code that reads like the surrounding code: match its comment density, naming, and idiom."

### 1.6 Smaller YAGNI / KISS skills

**Facts** (stars on 2026-11-18): `alvindemesadev/boring-engineering` (25, 2026-08-25), `JordanCoin/codingskills` (16, 2026-02-28), `ilindaniel/ponytail-lite` (254, 2026-06-28), `JayPokale/Chisle` (1,181, 2026-06-30; "terse prose, YAGNI-first code"), and `lennney/stop-that-shit` (3,994, 2026-08-11; a hook that blocks "unrequested hashes, checksums, and task-scope creep"). Only Chisle publishes measurements. **No evidence** for the others.

### 1.7 "4 questions before coding"

**Fact.** I found no viral "four questions that stop over-engineering" prompt. The "four questions" posts I did find are about writing a good *prompt* (context, problem, what was tried, what good looks like; Aaron Rose, about March 2026). **Inference:** the "4 questions" Saad saw is probably a retelling of the Karpathy file. The nearest real question list is Ponytail's ladder ("Does it need to exist? Already in this codebase? …").

---

## 2. Evidence, for and against

### 2.1 Karpathy file: almost no evidence, and the tests that exist show little effect

**For**
- **Fact.** PR #186 (sumonrh, open, July 2026) ran microbenchmarks ([K2](#sources)). On GPT-5.3-Codex (3 tasks × 5 repetitions, 30 calls), the full skill raised pass rate from 66.7% to 100%. **But the whole gain came from the one underspecified task** ("Underspecified export request: 0% to 100%"). On "Explicit simple implementation" and "Explicit surgical edit" the pass rate was "unchanged at 100%". The full skill also raised request tokens by **+203.6%**. The author's verdict on always-loading it was "Reject". An "adaptive" rewrite (ask one question on vague requests, otherwise add nothing) kept the quality gain and cut tokens. An older Gemini run used n = 1 per task with "permissive graders". The author calls it "descriptive results, not statistically reliable estimates".
- **Fact.** Practitioner reports are anecdotes: "roughly twice as fast" reviews (Walaski, no data), and an IN-PRACTICE.md (PR #197, 2026-08-18) with four incidents from one production repo. None of the incidents is about over-engineering. They are about verification and reporting.

**Against, or no effect**
- **Fact.** The repo publishes no evaluation. OrcaRouter (2026-10-23): "nobody has run the trial" ([OrcaRouter](#sources)).
- **Fact.** The `karpathy-jev` fork (reliable-era, Oct 2026) ran **SWE-bench Verified, 20 tasks, one attempt each** ([K3](#sources)):

| Claude Code / Sonnet 5 | Resolved | False "done" | Files outside gold patch (median) | Size ratio vs gold |
|---|--:|--:|--:|--:|
| Native | 18/20 | 2 | 0 | 1.16 |
| Karpathy skill (prompt-only) | 19/20 | 1 | **1** | **1.42** |

  Sign test vs native: 1 won / 0 lost / 19 tied, p = 1.00. The authors' pre-registered expectation that the skill would be "tighter in scope than native" came out **"inconsistent"**. Footnote: "The model never invoked the skill in any Sonnet run (0/20): this arm is native plus a skill listing." On Codex / GPT-5.5 the Karpathy arm was identical to native (16/20 each).
- **Inference.** With n = 20 and one attempt, none of this is significant. Even so, it is the only scope measurement of the Karpathy text on a Claude-5-generation model, and it does not show tighter diffs. Part of the reason is plain: as a skill, the model did not load it.
- **Fact.** A humorous PR (#191, 2026-07-25) was written by a Claude 5 model auditing the file against its own defaults. It said §2 and §3 are "verbatim my factory settings", and that "If uncertain, ask" "now contradicts my training". **This is not evidence.** It is one model's self-report, and it was asked to be funny. It does agree with Anthropic's facts in §1.5.

### 2.2 Ponytail: the best-measured file, with real limits

**For**
- **Fact.** Author benchmark, **2026-10-07** ([P1](#sources)): Opus 5.5, default effort, Claude Code CLI 2.1.288, headless sessions, **39 tasks × 5 runs × 3 arms = 585 sessions**, arms alternated, bootstrap intervals. Against no skill: **lines of code −53% [−63..−41], output tokens −45%, cost −26%, time −41%**. On the 18 tasks with hidden checks: 86/90 (no skill) vs 87/90 (Ponytail 5). A blind completeness judge scored 100/100 vs 105/105 as fully done. "Less code did not cost correctness or safety. It did not add any either."
- **Fact.** Independent test (Chase Hannegan, 2026-10-19, "700+ Claude Code sessions") ([C1](#sources)): code size −61%, cost −24%, 145 trick-input scenarios 99.5% vs 100% for plain Claude. "The numbers are real — they're just not the whole story."

**Against, or limits**
- **Fact.** Where the size came from. Per task, the big cuts are in greenfield and frontend work: a date picker (335 → 10 lines), a wizard (311 → 90), "build me a password app" (224 → 38). **On targeted edits the bare model was already lean:** `reuse-money` 9/9/9 lines, `reuse-slug` 20/19/21, `scope-rename` 3/3/3, `cache` 11/11/11.
- **Inference.** On Opus 5.5, the default model already reuses and stays surgical when a task is narrow. A simplicity rule pays off when *the model chooses the scope*. That is the brainstorm and plan stage in Anvil, not a one-line edit.
- **Fact.** Benchmark conditions: Bash off for every arm, fresh temp folders outside any git repo, CLAUDE.md and auto memory off, and one real repo (a FastAPI + React template). Results are author-run.
- **Fact.** **It removes features people wanted.** Hannegan: on open-ended prompts, "nice-to-have" features fell from **82% (plain) to 41% (Ponytail 5)**. Asking it to "polish it" afterwards recovered extras only to 63% of plain Claude's level. The polish run cost $0.50 vs $0.32 for plain Claude. "Don't install it globally and don't take the benchmarks at face value."
- **Fact.** **Measured by a competitor** (Chisle docs, 2026-11-06, Haiku 4.5, 25 cells): Ponytail's billed tokens were 90% of bare (95% CI 66–120%), with "backfires" on 12 of 25 cells ([CH1](#sources)). Chisle says separate runs "have differed by 10–30 points".

### 2.3 The seven-word prompt: same size cut, worse safety net

**Fact** ([C1](#sources)). "follow YAGNI principles and prefer one-liner solutions": **code −72%, cost −38%**. Trick inputs 98.4% (vs 100% plain). On the email-BCC privacy task it failed 3 of 3. It shipped **2 data-loss bugs in 24 builds** (Ponytail 0). It left tests in 14 of 24 builds (Ponytail 24 of 24) and met spec in 89% (Ponytail 95%).

**Inference.** Telling the model "be simple" is enough to get the size cut on current Claude. A long ruleset adds nothing to that. What the longer prompts buy is the "never cut" list (trust boundaries, data loss, a test for real logic). "Prefer one-liners" is the risky part: it rewards golfed code. Anvil should take the "never cut" idea and leave out "one-liner".

### 2.4 Papers

- **Fact.** Bohr, "Show and Tell: Prompt Strategies for Style Control in Multi-Turn LLM Code Generation", arXiv 2511.13972, **2025-11-17** ([R1](#sources)). With 160 paired Python programs, instruction prompts cut initial verbosity a lot, and accuracy stayed near ceiling. But **every condition grew more verbose when asked to revise for "readability, maintainability, and error handling."** Instructions combined with examples held the line best.
- **Inference for Anvil.** A reviewer prompt that asks for "robustness" or "maintainability" in general will push code toward bloat. The reviewer item has to name specific over-building patterns, and it must not invite generic hardening.
- **Fact.** I found no 2026 controlled study of "simplicity" instructions on *abstractions* (as opposed to token count) in coding agents. **No evidence** beyond the benchmarks above.

### 2.5 Contrary evidence: rules that anchor, make the model timid, or block needed refactors

- **Fact, measured, the anchoring mechanism.** Fable 5.2 (§1.5): when the code is framed as not the model's, it adds to the existing structure "even when that duplicated existing code". "Preserve behaviour … minimise changes … check existing architecture first" is that framing, applied to every tier. Anthropic measured this on Fable 5.2, not on Opus 5.5.
- **Fact, Saad's sessions** (P4, 3 incidents, 2026-11-12 to 11-17). In two of them the user flagged that the model read the old implementation while reviewing the replacement architecture. In the third, the model wrote "**Wrap, don't rewrite.**" as design decision #1 without brainstorming. Five days later it had to ask which intent was right.
- **Fact, critiques.** "Surgical changes can discourage a needed cleanup when the surrounding code is the actual source of the bug" (DevelopersDigest, 2026). Simplicity First "applied without judgment, can lead the agent to refuse to build abstractions when they would in fact be justified" (Pillitteri, 2026). The file itself says it biases "toward caution over speed".
- **Fact, the opposite risk.** Over-building is also often "inventing a structure the codebase already has" (MCP.Directory, in [practitioner-sentiment](2026-11-18-practitioner-sentiment.md) §6). Mnilax's "Read before you write" incident is a duplicate function. Ponytail's rung 2 is "Already in this codebase?". So "reuse existing" is a real fix in a normal change. It only goes wrong when it applies to code the spec is replacing.
- **Fact, timidity.** The Karpathy rule "If something is unclear, stop … Ask" conflicts with Claude Code's own "Reserve blocking questions …" and with Anvil's AFK mode. Fable 5.2: "never" is read as absolute, and caution "piles up". Opus 5 reviewers told to "only report high-severity issues" "might follow that instruction literally and report less" ([A2](#sources)).
- **Fact, duplication with defaults.** The harness already says these things (§1.5, [A5](#sources)). Anthropic's own measured direction for Claude 5 is fewer rules, not more ([E1](#sources)).

### 2.6 Evidence summary

| Claim | Evidence | Strength |
|---|---|---|
| Karpathy 4 rules reduce over-engineering | No repo eval. SWE-bench 20 tasks: scope looser, ns. Microbenchmark: no change on explicit tasks | **None to negative** on Claude 5-gen |
| "41% → 11%" | One self-reported X post, no data | **None** |
| "Ask when unclear" helps on vague requests | GPT-5.3-Codex microbenchmark, 1 task × 5 reps | Weak |
| A simplicity prompt cuts code size on Opus 5.5 | Ponytail 585 sessions; independent replication | **Moderate** (size, not quality) |
| ...without losing correctness | Hidden checks level, 18 tasks; trick inputs 99.5% | Moderate, small samples |
| A seven-word prompt does the same | One independent tester | Weak to moderate |
| The size gain is in greenfield and open scope, not targeted edits | Ponytail per-task table | Moderate (inference from the table) |
| Simplicity prompts drop wanted features on vague prompts | One independent tester (82% → 41%) | Moderate |
| "Not your code" framing makes the model bolt on and duplicate | Anthropic, Fable 5.2 | **Strong** (vendor-measured; model not verified on Opus 5.5) |
| Generic "maintainability" revision adds bloat | One paper, 2025 | Weak to moderate |
| Forceful words (MUST, NEVER) cause over-application | Anthropic docs (Opus 4.5/4.6; Fable 5.2 on "never") | Strong (vendor guidance) |

---

## 3. Verdict per rule, for Anvil

Two modes, as the brainstorm notes define them:
- **Normal change:** keep the diff small. Reuse what exists.
- **Redesign:** the spec says what is replaced and what stays. "Reuse existing" applies only to the parts that stay.

Where a rule can live: **always-on** (Anvil SKILL.md, read every time), **spec template**, **plan template**, **per-task reviewer checklist**, or **final converge check**.

| Rule | Verdict | Where | Why |
|---|---|---|---|
| K1a "State your assumptions explicitly" | **Keep** (Anvil already does it) | Spec (assumptions) and decision log | Already in "labelled assumptions and decision logs", which worked |
| K1b "If uncertain, ask" / "If something is unclear, stop … Ask" | **Drop** as always-on | Questions belong in brainstorm | Conflicts with AFK and the harness's "reserve blocking questions". The only gain measured was on vague one-shot prompts, and Anvil's brainstorm handles those |
| K1c "Present multiple interpretations" | **Keep**, already planned | Brainstorm ("offer 2 or 3 variations") | Matches Saad's flow |
| K1d "If a simpler approach exists, say so. Push back" | **Adapt** to the Opus 5 form: "say so in a sentence and continue" | Always-on (one clause) | Measured pattern. Avoids both silent scope changes and stopping |
| K2a "No features beyond what was asked" | **Adapt** to the Sonnet 5.5 form: "mention it at the end instead of doing it" | Always-on | Turns unrequested additions into suggestions, so they are not lost. Addresses Hannegan's lost nice-to-haves |
| K2b "No abstractions for single-use code" | **Keep, made checkable** | Plan template and reviewer | "A second caller or a spec line" can be checked. Already in the harness, so do not repeat it as prose |
| K2c "No flexibility / configurability that wasn't requested" | **Keep, made checkable** | Plan template and reviewer | Same reason |
| K2d "No error handling for impossible scenarios" | **Keep, with the trust-boundary exception** | Reviewer (GSD necessity review) | Ponytail and GSD both keep boundary checks. The seven-word prompt that lacked them shipped data-loss bugs |
| K2e "200 lines → 50, rewrite it" and "Would a senior engineer say…" | **Drop** | n/a | Not checkable. "Write clean code" is noise ([practitioner-sentiment](2026-11-18-practitioner-sentiment.md) §6) |
| K3a "Touch only what you must … Don't refactor things that aren't broken" | **Keep for normal change only** | Always-on, scoped by mode | Correct for edits. It is the cause of P4 in redesigns |
| K3b "Match existing style" | **Keep for code that stays** | Always-on, inside the mode line | Matches the Claude Code line "reads like the surrounding code" |
| K3c "Mention unrelated dead code, don't delete it" / "remove orphans you created" | **Keep** (normal change) | Reviewer | Cheap and checkable. In a redesign, the spec's Replaces list covers deletion |
| K3d "Every changed line should trace directly to the user's request" | **Keep, as spec lines** | Final converge check ("unrequested") | Anvil already proposes this: every change names its S-line |
| K4 "Write a test … then make it pass" | **Drop** the test-first transforms | n/a | Conflicts with Anvil's implement-first decision. The plan's test strategy covers it |
| K4 "State a brief plan: step → verify: check" | **Keep** (already in the plan design) | Plan template | Already agreed |
| Anthropic "Avoid over-engineering" sample | **Use as source text** for the reviewer item, not as always-on | Reviewer | Already in the harness. Anthropic offers it "if you're seeing this", for Opus 4.5/4.6 |
| Fable 5.2 ownership sentence | **Adapt, redesign mode only**, scoped to the replaced parts | Spec template (Replaces section) → plan brief | The measured fix for bolt-on and duplication. Cost: +70–80% tokens and unrequested changes, so do not use it in normal mode. Not verified on Opus 5.5 |
| Ponytail rungs 1–2 ("Does it need to exist? Already in this codebase?") | **Adapt** | Plan template, per new piece | Plan time is where over-building is cheapest to catch |
| Ponytail "never cut" list | **Keep the idea** | Reviewer item (d) | The safety net the seven-word prompt lacked |
| Ponytail "Keep the structure the codebase already has" | **Normal mode only** | n/a | In a redesign this is exactly the P4 anchor |
| Installing Ponytail itself | **Don't** | n/a | Duplicates the harness and Anvil. Strips features on vague prompts. Always-on context cost |
| Seven-word "prefer one-liner solutions" | **Drop** | n/a | Golfed code; 2 data-loss bugs in 24 builds |
| Current Anvil rules 1–3 (preserve, minimise, reuse) | **Replace** with the mode line below | Always-on | Binding at every tier with no redesign carve-out caused P4 |
| Current Anvil rule 4 (strip boilerplate) | **Move** to the reviewer item | Reviewer | Checkable there |
| Current Anvil rule 5 (concise output) | **Move** to report and spec guidance | Not about code | A different concern |

---

## 4. Proposed Anvil wording

The principles behind the wording: plain words; no MUST, NEVER, CRITICAL or ALL-CAPS; every exception stated in the rule; every rule names the failure it prevents, so it can be deleted when the model stops making that mistake ([anthropic-guidance](2026-11-18-anthropic-guidance.md) §4.1).

### 4.1 Always-on: three lines in Anvil SKILL.md

These replace the whole "Anti-slop posture" section.

> **Simple solutions**
> 1. Build what the spec and plan ask for, at that scope. If an extra would help (a feature, option, file, test or refactor), name it in your report instead of building it. If you see a simpler approach than the plan, say so in a sentence and carry on with the plan.
> 2. In a normal change, keep the diff to what the task needs, reuse what already exists, and match the surrounding code. In a redesign, design the parts the spec replaces from the spec, not from the old code. Reuse and match only the code the spec keeps.
> 3. Add an abstraction, option, layer or dependency only when a spec line or a second caller needs it today. Keep checks at trust boundaries (user input, external APIs, files, network). Leave out checks for states that cannot occur inside trusted code.

*Failure each line prevents:* (1) scope creep and silently lost good ideas (Opus 5 and Sonnet 5.5 docs; Hannegan's lost nice-to-haves); (2) P4, redesigns anchored on old code, while keeping reuse as the fix for duplication in normal changes; (3) speculative structure and defensive bloat, without the seven-word prompt's data-loss failure.

### 4.2 Spec template: say the mode, and what is replaced

> **Mode:** normal change | redesign
>
> *(Redesign only)*
> **Replaces:** the modules, files or behaviours this design replaces. Design these from this spec. The old code is a reference for behaviour that must survive, listed under "Must keep working", and nothing more.
> **Stays:** the code this design keeps and builds on. Reuse it and match its style.
> **Must keep working:** observable behaviours of the replaced code that the new design keeps (each one an S-line).

*Optional, test before adopting:* in redesign briefs, add one sentence: "For the parts listed under Replaces, you own the design." This is the Fable 5.2 ownership finding, scoped. It may raise tokens and unrequested changes, as measured on Fable 5.2. Run it on one real redesign before making it standard.

### 4.3 Plan template: every new piece names what needs it

> **New pieces.** List each new file, module, abstraction, option or config value, and dependency. Next to each, give the spec line that needs it. For each, answer: does it already exist in the code the spec keeps? Is it in the standard library, the platform, or an installed dependency?

Practitioners report they catch over-building most cheaply at plan review ([practitioner-sentiment](2026-11-18-practitioner-sentiment.md) §6). This line makes the plan show it.

### 4.4 Per-task reviewer checklist item

> **Over-building.** List each of these you find in the diff, with file and line. Report all of them; the main agent decides what to change.
> - **(a)** A new function, class, layer, wrapper or file with one caller, where no spec line needs it as a separate piece.
> - **(b)** A parameter, option, flag, config value or extension point that no spec line asks for.
> - **(c)** New code that does what existing code already does. Name the existing helper, component or library function. In a redesign, this applies only to code the spec keeps.
> - **(d)** Error handling, fallbacks or validation for a state that cannot occur inside trusted code. Do not flag checks at trust boundaries (user input, external APIs, files, network) or checks that prevent data loss.
> - **(e)** Tests, docs, comments or files no task asks for.
> - **(f)** Normal change: edits to code outside the task. Redesign: new code shaped around old code that the spec replaces (wrapping it, adapting to it, or keeping its structure).
>
> Do not suggest extra hardening, robustness or "maintainability" changes in this item.

Design notes:
- "Report all of them" follows Anthropic's Opus 5 review guidance: a reviewer told to be conservative reports less.
- The last line follows Bohr (2025): general "maintainability and error handling" revisions grow code.
- Items (c) and (f) carry the two modes. That is how the same checklist catches both duplication (normal) and anchoring (redesign).
- The reviewer is a fresh-context agent, which is what Anthropic and practitioners both recommend ([anthropic-guidance](2026-11-18-anthropic-guidance.md) §3.4, [practitioner-sentiment](2026-11-18-practitioner-sentiment.md) §6).

### 4.5 Final converge check

There is nothing new here. Keep spec-kit's **unrequested** bucket ([community-frameworks](2026-11-18-community-frameworks.md) P5): any changed file or behaviour that no live S-line asks for gets justified or removed. That is Karpathy's "every changed line should trace to the request", expressed through spec lines.

### 4.6 What not to add

- The Karpathy file, Ponytail, or any YAGNI skill as an install. They overlap with the harness prompt and with §4.1.
- "If uncertain, stop and ask" during the build.
- Size targets such as "under 100 lines" or "one file", unless the plan has a reason for them in that task.
- MUST, NEVER or CRITICAL in any of the above.

### 4.7 How to check this works

**Inference.** No public evidence shows that *any* of these lines helps on Opus 5.5 in a spec-driven flow. The cheapest check uses Saad's own repo. Replay one past normal-change task and one past redesign task (the 11-17 architecture replacement is a good one), with and without §4.1 to §4.4. Count unrequested files, new single-caller abstractions, and reads of replaced code. Ponytail's harness (`benchmarks/agentic/run.py`) shows a workable setup: headless `claude -p`, fresh workspace, five runs per arm. If a line makes no difference, delete it, as Anthropic did with 80% of Claude Code's prompt.

---

## Sources

All read on 2026-11-18 unless noted. Dates are publication dates.

**Karpathy file and its offshoots**
- **K0** Andrej Karpathy, X post, 2026-01-26: https://x.com/karpathy/status/2015883857489522876 (read through search snippets and the repo README quotes)
- **K1** forrestchang/andrej-karpathy-skills (now multica-ai), created 2026-01-27, `CLAUDE.md` and `README.md` read via `gh api`: https://github.com/forrestchang/andrej-karpathy-skills
- **K2** PR #186 "benchmark report and runner comparing baseline vs guidelines", sumonrh, opened 2026-07-06, benchmark run 2026-07-15: https://github.com/forrestchang/andrej-karpathy-skills/pull/186
- PR #191 "per Guideline #2, Claude 5 models should skip this file", shihyuho, 2026-07-25 · PR #197 IN-PRACTICE.md, condratiuc, 2026-08-18 · PR #177 ponytail guidelines, 2026-06-22 (same repo)
- **K3** reliable-era/andrej-karpathy-skills-jev, `eval/EVALUATION.md`, repo created 2026-10-09, historical results from 2026-09: https://github.com/reliable-era/andrej-karpathy-skills-jev
- **M1** @Mnilax, X article, 2026-05-09 (via the YouMind mirror): https://youmind.com/landing/x-viral-articles/karpathy-claude-md-coding-rules
- **M2** Jason Zhou, aibuilderclub, 2026-05-22 (updated 2026-06-18): https://www.aibuilderclub.com/blog/karpathy-claude-md-rules
- Robert Walaski, dev.to, Oct 13 (2026 by context): https://dev.to/robertwalaski/the-4-rules-in-my-claudemd-that-fixed-most-of-my-bad-claude-code-sessions-468i
- Alex Rusin, 2026-04-26: https://blog.alexrusin.com/the-viral-karpathy-claude-md-file-heres-the-honest-truth-about-what-it-actually-is/
- Xeve blog, 2026-05-25: https://xeve.io/blog/karpathys-claude-md-code-review-for-ai
- **OrcaRouter**, jinhao.song, 2026-10-23: https://www.orcarouter.ai/blog/karpathy-claude-md-file-explained
- HN, "What's inside the trending 'skills' repos for Claude Code", about April 2026: https://news.ycombinator.com/item?id=48383438
- Pasquale Pillitteri (2026): https://pasqualepillitteri.it/en/news/1872/karpathy-claude-md-trending-github-llm-coding · DevelopersDigest (2026): https://www.developersdigest.tech/blog/karpathy-claude-md-skills-menu (both via search snippets)

**Ponytail and competitors**
- **P1** DietrichGebert/ponytail, created 2026-06-12; `AGENTS.md`; `benchmarks/results/2026-10-07-agentic.md`: https://github.com/DietrichGebert/ponytail
- **C1** Chase Hannegan, "Is Ponytail 5 Worth It? I Tested It Across 700 Claude Code Sessions", 2026-10-19: https://chaseai.io/blog/ponytail-5-claude-code-skill-tested
- **CH1** JayPokale/Chisle, `docs/benchmarks.md`, run 2026-11-06: https://github.com/JayPokale/Chisle
- Smaller skills (stars via `gh api`): alvindemesadev/boring-engineering, JordanCoin/codingskills, ilindaniel/ponytail-lite, lennney/stop-that-shit

**Anthropic**
- **A1** Prompting best practices ("Overeagerness"; the aggressive-language note): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices (current page; the section names Opus 4.5/4.6)
- **A2** Prompting Claude Opus 5 ("Task scope and over-verification"; code review): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5
- **A3** Prompting Claude Sonnet 5.5 ("Steer initiative and scope"): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5
- **A4** Prompting Claude Fable 5.2 ("Say who owns the code"; "Keep caution from piling up"): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2
- Prompting Claude Opus 5.5 (checked; it has no over-engineering section): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5
- **A5** Claude Code system prompt fragments, third-party extraction by Piebald-AI (repo last pushed 2026-11-17; the "no unnecessary additions" fragment last changed 2026-07-20, v2.1.216): https://github.com/Piebald-AI/claude-code-system-prompts. Not an official Anthropic document.
- **E1** Thariq Shihipar, "The new rules of context engineering for Claude 5 generation models", 2026-07-24: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models (redirects to claude.dev)

**Papers**
- **R1** Jeremiah Bohr, "Show and Tell: Prompt Strategies for Style Control in Multi-Turn LLM Code Generation", arXiv 2511.13972, 2025-11-17: https://arxiv.org/abs/2511.13972
