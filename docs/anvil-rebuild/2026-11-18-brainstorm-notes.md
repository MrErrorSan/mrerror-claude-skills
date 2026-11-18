# Anvil rebuild: brainstorm notes

- **Started:** 2026-11-18
- **Status:** brainstorming in progress. This is **not** the spec yet. It records what we've learned and agreed so far, so the work can continue on any machine.
- **Related:** [skills audit, 2026-11-18](../2026-11-18-skills-audit.md)
- **Raw evidence:** `docs/anvil-rebuild/private/2026-11-18-session-evidence.md`. It is gitignored and on this machine only, because it quotes client work and this repo is public.

Labels used below:
- **[user]**: Saad said or decided it.
- **[evidence]**: seen in past session transcripts.
- **[proposal]**: Claude's suggestion, not yet approved.

---

## 1. The goal

Anvil stops being an override layer on top of Superpowers and **becomes the workflow itself**. We copy and rewrite only the Superpowers skills it actually needs. Superpowers is MIT-licensed, so we keep the credit. Then the Superpowers dependency is removed. **[user]**

Anvil also connects the sibling skills, so the whole set works as one system. That covers tickets (`ticket-update`), mocks (`ui-mockup`), UX audits (`ux-audit`), second-model review (`cross-model`) and unattended mode (`afk`), plus any future skills. **[user]**

What Anvil is used for: architecture, research, demos, mocks, requirements work, planning, and splitting a problem into parts that parallel agents work on. This is more than code changes. **[user]**

The bar: **better than today, with no regressions**, checked against current community practice and against how Claude models actually behave. Nothing deprecated or out of date. **[user]**

## 2. Why: what's wrong today

### What Saad reported [user]

- **Two skills give contradicting instructions.** That confuses the model, and results are worse than plain Superpowers was.
- **Anvil switched off parts of Superpowers he liked.**
- **There's a déjà vu feeling.** Something isn't right, but he can't name it.
- **Superpowers' own problems,** which are why Anvil exists:
  - **Too many questions** when he doesn't have the full picture yet. He wants 2 or 3 worked variations instead, researched on the web where useful and shown visually (mocks especially), so he can react to them. Superpowers' gate blocks this.
  - **Design questions are a wasted stop.** He said yes to nearly all of them and did his real review in the spec.
  - **TDD is slow.** It made sessions stop while he was away, and tasks slipped.
  - **Verification is out of proportion.** For a one-line change it ran verify in the subagent, verify in the main agent, then committed, then verified again.
  - **There's no to-do or tracking list,** so he can't see progress.
- **Anvil's own problems:**
  - **Questions get skipped silently.** He doesn't know what was decided or why.
  - **Changes don't flow back.** If the plan said A and the build switched to A1, the spec and plan still say A. Reviews then disagree with each other because the plan and the code disagree, and he has to go back and fix it all.
  - **No pushback on changed requirements.** It should say "earlier you decided X, now it's Y; is this a change request or a new feature, and will you regret it?"
  - **Tests are unhappy territory:**
    - suites grow to 1,000 to 2,000 tests and take 20 to 30 minutes to run;
    - nobody knows why each test exists;
    - when something fails, it isn't clear whether the test or the code was changed, or why;
    - tests should cover only the **core**, meaning places where a change would cause bugs across the system or alter how it behaves.
  - **Over-engineering.** He wants simple solutions, not an over-built codebase.

### What the session transcripts show [evidence]

64 sessions between 2026-10-16 and 2026-11-18 loaded Anvil's description. These counts and findings were mined automatically.

- **Every Anvil load used the old React-frontend copy** at `~/.claude/skills/anvil`, including in Python, Rust and C# repos. The general version in this repo has **never run in real work**.
- **Skill invocations:**

  | Skill | Calls |
  |---|---|
  | anvil | 39 |
  | brainstorming | 26 |
  | writing-plans | 10 |
  | subagent-driven-development | 6 |
  | systematic-debugging | 3 |
  | test-driven-development | 0 |
  | requesting-code-review | 0 |
  | verification-before-completion | 0 |

  Brainstorming mostly ran because Saad typed it himself.
- **Tiers barely gated anything.** The model rated work Tier 2 18 times, Tier 1 4 times, and Tier 0 never.
- **The biggest loss was the per-task spec review.**
  - Of 9 build sessions, 2 kept it, 2 ran it per phase, 2 had one final review and 3 had almost none.
  - Where it ran, it caught real bugs early.
  - Where it didn't, rework came late. One session ran 66 agents with a single audit at the end, then needed about 20 fix agents and still had 17 spec items open.
  - This contradicts Anvil's claim that per-step checks find nothing the final pass would miss.
- **This is the likely root of the déjà vu:**
  - Anvil defines "verify" as "run the commands" and never as "did we build what was asked".
  - So the cycle was: rebuild, pass the checks, get the same complaint again.
  - On one project the same "flexible, not rigid" request was repeated 6 or more times over three weeks. A rigid project rule also contributed there.
- **Each session ran a different workflow.**
  - Anvil's "implement only" brief appears in only 26 of about 400 implementer briefs.
  - Project rules and memory files also overrode both skills.
- **Long, opaque waits.** Saad sent about 30 "done?" or "what is taking so long" messages, and there were 13 usage-limit hits.
- **Redesigns anchored on old code.** In two cases the model read the old code instead of the new design. The likely cause (inference) is Anvil's always-on "preserve, minimise, reuse existing" rules.
- **Tests written after the code found nothing:** about 190 tests, "no bugs found" each time. This is from one session only.
- **The model agreed instead of pushing back,** and it took subagent findings on trust.

**What worked, and must survive the rewrite:**
- a fresh reviewer checking the spec before building ("builder check");
- pinning the shared contracts before splitting work across agents;
- parallel agents for research and checking;
- labelled assumptions and decision logs;
- systematic-debugging;
- cross-model review.

## 3. The flow (agreed)

```
Brainstorm ─► Spec ─[STOP: approve spec]─► Plan ─[STOP: approve plan]─► Build + verify ─► Done, working
 questions,    plain words,                 parallel or single, test       follows the plan, keeps
 variations    numbered lines               strategy, todo list            the todo current, no stops
```

1. **Brainstorm.** Ask the questions that matter and refine the requirements. When information is thin, offer 2 or 3 variations instead of an interrogation: research the web and show mocks or sketches. **[user]**
2. **Spec**, then a **stop**. Saad reviews and approves before planning starts. **[user]**
   - The spec is in plain words for a human: intent, goals, non-goals, anti-goals, and an explanation. **[user]**
   - Decisions go *into* the spec, where Saad actually reviews them. **[user]**
3. **Plan**, then a **stop**. Saad reviews and approves before building starts. **[user]** The plan holds:
   - the execution strategy: parallel agents or a single agent, and how the work is split;
   - the test strategy: which tests, when, why, and which build-only tests are removed afterwards;
   - the to-do list.
4. **Build and verify, with no stops.** Follow the plan, write the planned tests, keep the to-do list current, and verify. Hand back a **fully working result with no errors.** **[user]**
5. **Stops by default, skippable on request.**
   - "I'm AFK" (or "skip it" for a single phase) runs every phase without waiting. Each decision is made on Saad's behalf and logged.
   - Without that instruction, it stops at each gate above. **[user]**
6. **Extra checkpoints** happen only when Saad asks for one, during planning or building. Nothing automatic. **[user]**
7. **Changes flow back.** A change mid-build updates the spec and the plan, so the spec, the plan, the code and the reviews never disagree. **[user]**
8. **Push back on requirement changes.** Name whether it's a change request or a new feature, what it conflicts with that was decided earlier, and what it costs. **[user]**

## 4. Tests and verification (agreed in principle)

- **Verification fits the change.** A one-line edit gets one quick check, done once. There's no re-verification by both subagent and main agent. **[user]**
- **Tests only for the core:** behavior where a change would cause bugs across the system or alter how it works. **[user]**
- **Every test can say why it exists.** **[user]**
- **When a fix touches a test or the code, the model says which one and why.** If a requirement changed, it says so. **[user]**
- **Reports rank what's critical and what isn't.** **[user]**
- **Auditing an existing bloated suite** (keep, merge or delete) is not a separate skill. It's an ordinary request that Anvil handles through its normal flow, using these test rules. **[user]**

## 5. Proposals not yet approved [proposal]

- **Numbered spec lines** (S1, S2…). Each plan task, to-do item, test and review finding names the spec lines it covers.
  - The per-task review checks "does this match S3".
  - A change from A to A1 becomes a dated edit to S3, and everything that points at S3 is flagged for a re-check.
  - This is what keeps spec, plan, code and reviews in agreement.
- **Decisions in the spec are written as:** the call made, the reason, and the alternatives not taken. Anything that is genuinely Saad's to decide sits at the top.
- **One live progress file per piece of work,** readable at any time, so there's no need to ask "done?".
- **Two kinds of test, named in the plan:**
  - **Keep:** guards core behavior, names its spec line, and says what breaks if it fails.
  - **Scaffold:** used during the build and deleted before finishing.
- **Editing a test to make it pass requires a changed spec line.** Otherwise the code gets fixed.
- **A cheap per-task spec review comes back.** A reviewer reads each finished task's changes against its spec lines. It doesn't rerun tests, so the biggest gap gets fixed without bringing back the slowness.
- **One verification run,** by the main agent, sized to the change: a quick check for small edits, the full check once at the end for features.
- **Simplicity stays a rule,** but it must not anchor redesigns on old code. "Reuse what exists" applies to code that the spec says stays.

## 6. Still open

These still need to be covered before the design can be written:

1. **Finishing:** what "done" means after the build: review, commit and push, PR, ticket update. This repo's rule is commit and push after every unit of work, but `afk` says never commit unless asked. That conflict needs a decision.
2. **Ecosystem wiring:** when each sibling skill runs, and how tickets are created and updated from the spec and plan.
3. **Non-code work:** how the same flow fits research, architecture, demos and mocks.
4. **Coexistence with Superpowers:** whether it is uninstalled everywhere, or must still be present on some machines or team projects. Superpowers starts itself with a session-start hook, so a self-contained Anvil needs its own reliable way to start.
5. **Research phase:** current community practice (GitHub, Reddit, developer forums), Anthropic's own skills and guidance on development workflows, and how current Claude models respond to skill instructions.
6. **The approaches:** ways to build the new Anvil, compared, with a pick.
7. **Sizing,** and then the full written design, with a builder check before review.
