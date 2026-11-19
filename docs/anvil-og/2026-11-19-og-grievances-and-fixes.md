# Anvil OG: your grievances, and how to fix the original

- **Date:** 2026-11-19
- **Status:** fixes applied on branch `anvil-og-next` (0.2.0), not yet measured. §7 answered 2026-11-19: stay a governor over Superpowers; no new large case (the bar is "not worse than OG" on the existing suite); spec check per wave.
- **Target:** the original Anvil on `main`: [plugins/anvil/skills/anvil/SKILL.md](../../plugins/anvil/skills/anvil/SKILL.md) (0.1.0, 327 lines) and [afk/SKILL.md](../../plugins/anvil/skills/afk/SKILL.md).
- **Direction (yours, 2026-11-19):** "if old approach was working fine then we should be going back and optimizing it instead of wasting tokens on new things". Improve the verified variant. Don't build new machinery.
- **Raw data:** [2026-11-19-og-judge-extract.json](2026-11-19-og-judge-extract.json), which holds the blind judge's scores and problem notes for every OG run.

## Sources

All of these are on branch `anvil-v2` unless marked.

| Source | What it gives |
|---|---|
| `docs/anvil-rebuild/2026-11-18-brainstorm-notes.md` | Your grievances in your words (§2), your flow (§3), and your test rules (§4) |
| `docs/anvil-principles.md` | The same points as numbered principles P1–P44 |
| `docs/anvil-rebuild/private/2026-11-18-session-evidence.md` (local, gitignored) | 64 real sessions mined for failure patterns P1–P10 |
| `docs/anvil-ab/2026-11-19-three-way-comparison.md` | Anvil 1.0 vs Superpowers vs plain, with hidden issues |
| `docs/anvil-v2/2026-11-19-v2-results.md`, `progress.md` | The six-arm results, the V2.2 decision log, and your call to go back to OG |
| `abtest/results/og/`, `abtest/results/six/judge/` | How OG behaved in 21 runs, and what the judge flagged |
| Transcripts of the 4 earlier sessions in this repo | Your messages, including decisions that aren't in the docs |
| `plugins/anvil/skills/anvil/SKILL.md` on `anvil-v2` (V2.2) | The "just do it" path that measured well |

## 1. The short version

1. **OG's core is sound.** In the A/B test it matched V2.2 on accuracy (194/195 hidden tests), ran fastest of the plugin arms (41 min), and cost the least of them ($11.92). The judge ranked it joint 2nd of 6 (3.69, tied with V2.1). Keep its shape: one text skill, no CLI, no hooks.
2. **The A/B test never exercised the parts you complain about.** Every case was 1–3 tasks, and OG spawned **0 subagents in all 21 runs**. Its rules for parallel fan-out, per-task review and end-loaded verification never ran. Those rules are where most of your real-world grievances come from. A good OG score therefore doesn't clear those rules.
3. **Your real-world grievances came from a different copy.** All 39 real Anvil loads used the old React-frontend copy in `~/.claude/skills/anvil`, which is still the `anvil` skill loading in this session. Part of "fixing OG" is deploying it (§6).
4. **Even on small cases, OG has gaps that are easy to fix.** It writes plan docs that nobody approves, builds before the spec stop when you ask it to think first, makes calls without reasons, creates branches nobody asked for, and skips the test run on a typo. V2.2's "just do it" path already fixes most of these, in about 30 lines of text.
5. **The deepest problem is this: OG bought speed by deleting feedback loops, not by making them cheaper.** "Verify once at the end" removed the per-task spec check, and verification only ever means "run the commands", never "did we build what you asked". That loop (rebuild, pass the gates, hear the same complaint again) is most likely the déjà vu.

## 2. Your flow (the target)

This puts together what you've already decided. Nothing here is new.

**Three paths, picked on the fly and stated in the first line so you can correct it.** "If I tell you to go and do this in the code, it's a plan requirement, not a spec one" (2026-11-18). Spec and plan merge when the requirements are small. Simple, linear work stays dormant, the way Superpowers does (2026-11-19).

| Path | When | Stops |
|---|---|---|
| **Just do it** | Linear work in one area: a bug fix, a small feature, a few related additions | None. No docs, no subagents |
| **Spec first** | The request leaves open a product question that changes what gets built, or you ask to think it through first | One: a combined spec and plan |
| **Full** | 4+ separable tasks where parallel agents pay off, anything expensive to reverse, work spanning sessions, or you ask for it | Two: the spec, then the plan |

**The full flow:** brainstorm → spec → **stop** → plan → **stop** → build and verify with no stops → a working result.
- **Brainstorm:** ask the questions that matter, concrete and grounded in the code. When the picture is thin, offer 2–3 worked variations (mocks, web research) instead of an interrogation.
- **Spec:** plain words. Intent, goals, non-goals, anti-goals, and an explanation. The decisions go in the spec, because that's where you actually review them.
- **Plan:** the execution strategy (parallel or single, and how the work splits), the test strategy (which tests, when, why, and which get deleted afterwards), the to-do list, and the commit points.
- **Build:** follow the plan, keep the to-do list current, and change the spec and plan when the build changes. Push back on requirement changes.
- **AFK, "skip it", or a pre-approval** passes a stop. Each decision made for you is logged.
- **Commits:** the plan defines when they happen. Work happens on a local branch. At the end, Anvil offers the landing options: which branch, push or not, and cleaning up dead branches.

## 3. Your grievances with OG, and the fix for each

Ranked by cost. Each entry gives what you said, what the evidence shows, the OG rule behind it, and the fix.

### G1. The per-task spec check was dropped, so the rework landed at the end
- **You:** "Anvil switched off parts of Superpowers I liked."
- **Evidence:** of 9 real multi-agent builds, only 2 kept per-task review. Where it ran, it caught real bugs early, and the whole-branch review still found more. Where it didn't, a 66-agent build needed about 20 fix agents and still had 17 spec items open.
- **OG rule:** the SDD row ("checkpoints only at real dependencies"), Verification ("One phase, at the end") and the claim that interleaved checks "catch none this pass would miss" ([SKILL.md:81](../../plugins/anvil/skills/anvil/SKILL.md#L81), [:244-260](../../plugins/anvil/skills/anvil/SKILL.md#L244-L260)). The data contradicts that claim.
- **Fix:** on the Full path, add one **cheap spec check per wave**. A fresh reviewer reads the wave's diffs against each task's acceptance lines and runs no tests. Batch its findings into one fixer. Delete the "catches none" sentence.

### G2. "Verify" means run the commands, never "did we build what you asked"
- **You:** the déjà vu; "something isn't right".
- **Evidence:** one requirement ("flexible, not rigid") came back 6+ times over three weeks while every rework passed its gates. Asks were missed at the end (a deletion feature, a known-missing icon shipped in a release). You had to ask for browser checks yourself, three times. The model admitted it "took the reviewers' findings on trust".
- **OG rule:** the Verification table and the non-negotiable floor define evidence as type-check, lint, tests and build only ([:251-256](../../plugins/anvil/skills/anvil/SKILL.md#L251-L256), [:299](../../plugins/anvil/skills/anvil/SKILL.md#L299)).
- **Fix:** add **requirements reconciliation** to the final pass: list each of your asks (or spec lines) and tick each one with evidence. Run the real thing once: the CLI path, the endpoint, or the UI in a browser when UI changed. Spot-check subagent claims before repeating them.

### G3. Calls are made silently, and you don't know what was decided or why
- **You:** "Questions get skipped silently. I don't know what was decided or why."
- **Evidence (A/B):** OG rejected `--top 0` in all 3 c2 runs, either with no reason or listed as "a choice I made" with no justification. In c3 it decided the both-flags behaviour without asking in all 3 runs, and got it wrong in 1. In c4 it chose the zero and sub-dollar formatting silently.
- **OG rule:** OG only logs decisions under AFK. Outside AFK there's no rule for reporting calls.
- **Fix (from V2.2):** every report ends with **calls I made**, numbered, each with its reason and what it costs to reverse. Ask only when two readings would build different things and the repo can't tell. Then ask in one message, each question with your recommended answer.

### G4. The stops aren't defined, so docs get written that nobody approves
- **You:** design questions are a wasted stop. The spec and plan are where you review.
- **Evidence (A/B):** in c3 ×3 and c6, OG wrote a plan doc that it never offered for approval, sometimes after the code, with every to-do already "completed". The judge called it "ceremony without a checkpoint". In c5 ("think it through before anything gets built") it built straight after Q&A in 1 run and missed a must-have. In another run the spec still said "Not built yet" after delivery.
- **OG rule:** Tier 1 says "one lean plan" but never says whether to stop on it ([:94-95](../../plugins/anvil/skills/anvil/SKILL.md#L94-L95)). Nothing says when a stop happens.
- **Fix:** replace the tiers with the three paths in §2, each with its stops stated. **A doc is written only if it will be presented at a stop**, or because you asked for it. "Just do it" writes no doc.

### G5. The tiers don't gate anything
- **Evidence:** in real use the model rated work Tier 2 eighteen times, Tier 1 four times, and Tier 0 never. In the A/B, Tier 0's "no tests" made OG skip the test run on the typo in 2 of 3 runs (judge: "leaves verification to the user").
- **OG rule:** the Tiers section ([:88-108](../../plugins/anvil/skills/anvil/SKILL.md#L88-L108)).
- **Fix:** use the three paths, with V2.2's observable triggers. V2.2 routed correctly on 21/21 runs. Even "just do it" runs the targeted tests, plus the full suite once if it's fast.

### G6. Tests: written after the code, bloated, and nobody knows why they exist
- **You:** suites grow to 1,000–2,000 tests and take 20–30 minutes, nobody knows why each test exists, and it isn't clear whether the test or the code was changed. Tests should cover only the core.
- **Evidence:** a gate-test wave wrote about 190 tests after the code, each batch reporting "no bugs found". The real defects surfaced later. In the A/B bug case, the judge flagged that OG never showed the new test failing before the fix (c4, 2 of 3 runs).
- **OG rule:** "What earns a test" is a frontend layer table (services, hooks, components) ([:195-215](../../plugins/anvil/skills/anvil/SKILL.md#L195-L215)). The bug-repro exception is left as "a real call" ([:302-306](../../plugins/anvil/skills/anvil/SKILL.md#L302-L306)). The implementer brief says "do not author tests".
- **Fix:**
  - A bug fix **always** gets a repro test first, which you watch fail, and the report says so.
  - Tests cover only the core: behaviour where a change would break things elsewhere or change how the system works.
  - On the Full path, the plan names each test as **keep** (it says what breaks if it fails) or **scaffold** (deleted before finishing).
  - When a fix touches a test or the code, the report says which one and why. A test is edited to pass only when a requirement changed.
  - Replace the frontend table with these stack-neutral rules.

### G7. The same slow suite runs again and again against unchanged code
- **You:** "20 minutes in the subagent, 40 by the reviewer, 60 before commit." You aren't against testing, only against wasted time.
- **Evidence:** a 2,900-test final suite ran 28–35 minutes while you were waiting to merge. Twelve test workers maxed out your CPU and RAM.
- **OG rule:** OG already says to run the full suite once, by the orchestrator. That part is right. But it pushes every check to the end, where it becomes one long blocking wait.
- **Fix:** keep "the full suite runs once". Add "**a test result stays valid until the code changes**": don't rerun on an unchanged tree, before a commit, or in a reviewer. During the build, run only the narrowest tests that cover the change. Cap the test workers.

### G8. Redesigns anchor on the old code
- **You (mid-session, twice in one day):** "Why are we looking into the current implementation? We're reviewing the architecture we created to replace it."
- **Evidence:** a v2 design wrote "Wrap, don't rewrite" as its first decision without asking. Five days later it had to ask which was meant.
- **OG rule:** Anti-slop posture: "Preserve behavior… Minimize changes… Reuse utilities… binding at every tier", with no carve-out ([:314-322](../../plugins/anvil/skills/anvil/SKILL.md#L314-L322)).
- **Fix (V2.2's three lines):**
  - **Normal change:** the smallest diff, using existing patterns.
  - **Redesign:** build what the spec describes. Reuse only what the spec says stays.
  - **Nothing without a reason:** no module, option or helper that no ask or spec line needs. The A/B judge flagged OG adding an `export.py` module for about 20 lines in 4 runs (c3 ×3, c6).

### G9. Changes don't flow back, and there's no pushback
- **You:** "If the plan said A and the build switched to A1, the spec and plan still say A. Then the reviews disagree." And: "there was no verification, no pushing back… architecture is nothing but sand."
- **Evidence (A/B):** OG's plan cited the wrong invoice ids (c3). Its spec said "Not built yet" after delivery (c5). In real work, a simplification you proposed was applied across the whole spec without being checked.
- **OG rule:** none. OG has escalation triggers for code facts ([:110-128](../../plugins/anvil/skills/anvil/SKILL.md#L110-L128)), but nothing for requirement changes or for keeping docs in step.
- **Fix:**
  - A change mid-build edits the spec or plan line (dated) before the code moves on.
  - On a changed requirement, say whether it's a change request or a new feature, what earlier decision it conflicts with, and what it costs.
  - Check a proposed design change before applying it, and say where it's weak.
  - The final pass checks that the docs match the code.

### G10. Parallel by default overloads the machine and fights your layout
- **You:** parallel works best with isolated agents, 3–4 at a time. "Why do you keep making new folders instead of branches?"
- **Evidence:** 6 heavy jobs ran at once, plus 11 "stale base" worktree errors. One agent's `commit -a` swept up another agent's unfinished edits. About 30 "done?" pings in 12 sessions.
- **OG rule:** "Default to parallel; justify sequential" and "Continuous execution", applied to every tier ([:78](../../plugins/anvil/skills/anvil/SKILL.md#L78), [:268-290](../../plugins/anvil/skills/anvil/SKILL.md#L268-L290)).
- **Fix:**
  - Parallel only on the Full path, with at most 3–4 agents per wave.
  - Keep the parallel-safe test and contract pinning: both worked in practice.
  - Isolation follows the project's rule (branches, not folders, where you've said so). Agents never commit with `-a`.
  - A one-line status per wave, plus a live to-do list in the plan file, so you never have to ask "done?". Claude Code removed its todo tools, so the list lives in the file.

### G11. Branches and commits nobody asked for, and nothing landed
- **Evidence (A/B):** OG created `feature/top-n` without being asked in all 3 c2 runs, and `fix/…` in c4. The cause is "no work on main without consent" being read as "make a branch". Meanwhile AFK says "never commit".
- **OG rule:** branch safety ([:310](../../plugins/anvil/skills/anvil/SKILL.md#L310)), and AFK's commit rule ([afk/SKILL.md:49](../../plugins/anvil/skills/afk/SKILL.md#L49)).
- **Fix:**
  - **Just do it:** edit in place, commit nothing, and end with "Nothing committed."
  - **Full:** the plan names the commit points, and the work goes on a local branch. At the end, offer the landing options.
  - ~~Align AFK with this: commit at the plan's commit points, push nothing.~~ *Superseded 2026-11-19: controlling commits isn't AFK's job. AFK leaves commits and branches to the workflow, the project rules and the user.*

### G12. Contradicting layers make every session run a different workflow
- **You:** "Two skills give contradicting instructions. That confuses the model."
- **Evidence:** the model rarely hesitated. It confidently built a different blend each time. Anvil's verbatim implementer brief appeared in 26 of about 400 briefs. Project rules and memory files overrode both skills. The skills Anvil "keeps as written" (code review, verification) were never invoked, 0 times.
- **OG rule:** "Every other Superpowers skill is kept exactly as written" ([:83-86](../../plugins/anvil/skills/anvil/SKILL.md#L83-L86)). It relies on skills that don't fire.
- **Fix:** keep the override table, but make Anvil **carry its own short version** of the three things it actually relies on: the per-wave spec check (G1), the final reconciliation (G2) and the repro-first bug fix (G6). A few lines each, not copies of Superpowers. Then it doesn't matter whether a Superpowers skill fires.

### Smaller fixes
- **Line endings.** OG's typo fix used `sed`, which stripped CRLF. Edit with the Edit and Write tools only, and keep each file's line endings (from V2.2).
- **Narration and jargon in chat.** The judge flagged leaked progress text ("Reproduced. Now the fix:"). Use plain words, outcome first.
- **Questions without a recommendation.** In c5 OG opened with an open "what's prompting this?". Ask batched, concrete questions, each with a recommended answer.
- **Dangerous commands.** A broad `taskkill` on `python.exe` (c5). Never kill processes you didn't start.
- **Plan location.** OG defaults to `docs/plans/`. Your repos use `docs/superpowers/plans/`. Follow the project rule first.
- **Sibling skills aren't wired.** Nothing tells Anvil when `ui-mockup`, `ux-audit`, `cross-model` and `ticket-update` run. Add a short table. Also, `ui-mockup` says to make an Artifact, which your CLAUDE.md forbids.
- **Dead tool pointers.** `claude-session-driver` needs tmux, which isn't on this machine, and `episodic-memory` isn't installed. Change both to "if installed", with the `Agent` tool as the default.

## 4. What stays from OG

These held up in both the A/B test and real work. Don't touch them beyond wording:
- One text skill, read once: no CLI, hooks, gates or state files. That machinery is what made 1.0 2.4× slower than Superpowers.
- The lean contract plan template, including the pinned data-layer contracts and the `## Open questions` section.
- The parallel-safe test (disjoint writes, no shared decisions) and "pin the contract, then fan out".
- The escalation triggers, and "anything you invented is labelled as an assumption".
- The speed levers: batched fixes for one fixer, file handoffs, the cheapest capable model for mechanical work. *(Updated 2026-11-19: only batched fixes stayed in 0.2.0. Which model runs a task isn't something Anvil prescribes; whichever is available is used.)*
- The AFK skill: the decision log format and what AFK never unlocks. *(2026-11-19: AFK sets no commit rule of its own; see G11.)*
- "Project rules win over Anvil."

## 5. What to take from V2.2, and what not to

**Take** (measured to help, all plain text):
- the path picker, stated in the first line;
- the "just do it" steps: look first, decide small things and list them, build, check once, report;
- the report shape: what changed, how it was checked (commands and exit codes), calls I made, and the commit state;
- the Edit/Write-only rule and keeping line endings;
- approve-with-edits: "approved, one fix: …" means approve, apply exactly those edits, and don't stop again.

**Leave behind:** the `anvil` CLI, quote-checked approvals, the hooks, topic state, the split into 8 stage skills, the S-line ids in chat. Those are what V2.0–2.1 spent their time on.

## 6. Deployment: the fix doesn't count until it's the copy that runs

- `~/.claude/skills/anvil` and `~/.claude/skills/afk` are the old React-frontend copies, and they load in every repo, this one included.
- `anvil@mrerror-claude-skills` is installed only at **local** scope in this repo, at version **1.0.0** (the rebuild), not OG.
- `plugin.json` depends on `superpowers@superpowers-marketplace`. You run `superpowers@claude-plugins-official`, so installing as written adds a second Superpowers.

**To do, once the skill is fixed:**
1. Point the dependency at `claude-plugins-official`, or drop it.
2. Make `claude-session-driver` and `episodic-memory` optional.
3. Install the fixed plugin at user scope, and remove the 1.0.0 local install.
4. Move the loose `~/.claude/skills/{anvil,afk}` out of the way, keeping `skills.zip` as the backup.

## 7. Decisions that are yours

1. **Stay a governor over Superpowers, or become self-contained?** Your 2026-11-18 decision (P1, P42) was self-contained. That became 1.0, and 1.0 was too heavy. **Recommendation:** for this round, stay a governor, as measured, and carry only the three short pieces in G12. Revisit self-contained once OG-next is trusted. Cost to reverse: low; it's text.
2. **Add a large case to the A/B suite before calling this verified?** None of the 7 cases has 4+ tasks or a slow suite, so G1, G2, G7 and G10 can't show up in the numbers. **Recommendation:** add one c8 case (4–5 separable tasks, a suite of about 60 s, a vague requirement), and run it for OG-next, Superpowers and plain. Cost: about 9 extra runs.
3. **Per-wave or per-task spec check on the Full path?** **Recommendation:** per wave. It still catches drift before the next wave builds on it, at about a third of the review agents. Cost to reverse: one line.

## 8. Next steps

1. You read this and answer §7.
2. On a new branch from `main` (not `anvil-v2`), edit `anvil/SKILL.md` and `afk/SKILL.md` with the fixes in §3, keeping the size near OG's (about 350 lines). Bump to 0.2.0.
3. Review the diff with a fresh Claude subagent. Cross-model review (Gemini) runs only when you ask for it (your rule, 2026-11-19).
4. Rerun. The harness lives only on `anvil-v2`, and arm O is pinned to an exported copy of `46b7535` ([ab.py:46-47](https://github.com/MrErrorSan/mrerror-claude-skills/blob/anvil-v2/abtest/harness/ab.py#L46-L47)). Add an arm for the new branch's plugin (plus Superpowers, as O had), run it with `--runs 3` on the 7 cases (plus c8 if you agree), then compare against `og`, `v22`, Superpowers and plain. The bar: at least OG's accuracy, no slower than OG, and a judge mean above V2.2's 3.88.
5. Deploy (§6).
