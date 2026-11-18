# Anvil principles

These are Saad's decisions, as numbered principles. Upstream-review verdicts cite them by id (see `upstream/superpowers/README.md`).

**Source:** every item labelled **[user]** in the [brainstorm notes](anvil-rebuild/2026-11-18-brainstorm-notes.md), one line each, with the section it came from.
- Where the same point appears in more than one section, it's listed once, with every section.
- Ids are never reused or renumbered.
- A new principle gets the next number. A withdrawn one is struck through, with the date and the reason.

| Id | Principle | From |
|---|---|---|
| P1 | Anvil is the workflow itself. It copies and rewrites only the Superpowers skills it needs, keeps the credit, and drops the Superpowers dependency. | §1 |
| P2 | Anvil connects the sibling skills (`ticket-update`, `ui-mockup`, `ux-audit`, `cross-model`, `afk`, and future ones) so they work as one system. | §1 |
| P3 | Anvil covers architecture, research, demos, mocks, requirements, planning, and splitting a problem for parallel agents, not only code changes. | §1 |
| P4 | Better than today, with no regressions. It's checked against current community practice and against how Claude models actually behave. Nothing deprecated or out of date. | §1 |
| P5 | Two skills never give contradicting instructions. | §2 |
| P6 | Don't switch off the parts of Superpowers that Saad liked. | §2 |
| P7 | Saad reported a recurring "something isn't right"; treat it as a real signal. | §2 |
| P8 | When the picture is thin, offer 2 or 3 worked variations instead of an interrogation. Research them on the web where useful, and show them visually (mocks especially). | §2, §3 (1) |
| P9 | Design questions are a wasted stop. Decisions go into the spec, where Saad actually reviews them. | §2, §3 (2) |
| P10 | TDD is slow, and must not stall sessions while Saad is away. | §2 |
| P11 | Verification fits the change and runs once. There's no re-verification by both the subagent and the main agent, and none again after the commit. | §2, §4 |
| P12 | There's a visible to-do list and progress tracking, so Saad never has to ask "done?". | §2, §3 (3, 4) |
| P13 | Questions are never skipped silently. Say what was decided and why. | §2 |
| P14 | Changes flow back. A change mid-build updates the spec and the plan, so the spec, the plan, the code and the reviews never disagree. | §2, §3 (7) |
| P15 | Push back on requirement changes. Name whether it's a change request or a new feature, what it conflicts with that was decided earlier, and what it costs. | §2, §3 (8) |
| P16 | Tests cover only the core: behavior where a change would cause bugs across the system, or alter how it works. No 1,000-test, 30-minute suites. | §2, §4 |
| P17 | Every test can say why it exists. | §2, §4 |
| P18 | When a fix touches a test or the code, say which one and why. If a requirement changed, say so. | §2, §4 |
| P19 | Simple solutions, not an over-built codebase. | §2 |
| P20 | Brainstorm asks the questions that matter and refines the requirements. | §3 (1) |
| P21 | Stop after the spec. Saad reviews and approves it before planning starts. | §3 (2) |
| P22 | The spec is in plain words for a human: intent, goals, non-goals, anti-goals, and an explanation. | §3 (2) |
| P23 | Stop after the plan. Saad reviews and approves it before building starts. | §3 (3) |
| P24 | The plan holds three things: the execution strategy (parallel agents or a single agent, and how the work is split); the test strategy (which tests, when, why, and which build-only tests are removed afterwards); and the to-do list. | §3 (3) |
| P25 | Build and verify run with no stops. They follow the plan, write the planned tests, keep the to-do list current, and hand back a fully working result with no errors. | §3 (4) |
| P26 | Stops are the default. "I'm AFK" (or "skip it" for one phase) runs without waiting, and each decision made on Saad's behalf is logged. | §3 (5) |
| P27 | Extra checkpoints happen only when Saad asks for one. Nothing automatic. | §3 (6) |
| P28 | Reports rank what's critical and what isn't. | §4 |
| P29 | Auditing an existing bloated suite (keep, merge or delete) is an ordinary request. It goes through the normal flow and the test rules, not a separate skill. | §4 |
| P30 | Saad keeps both plugins installed. He uses Anvil alone once he trusts it, and alongside Superpowers until then. The coexistence design is delegated to Claude. | §7 |
| P31 | Demos and POCs are pre-production work, not throwaway. They get the same treatment as a real feature: they ship if they meet the requirements, and are iterated until they do. | §8 |
| P32 | Throwaway work is limited to mocks, including interactive mocks with realistic data, used to show a hard problem to a non-technical reviewer. The mock is kept as a reference. Once it's approved, the feature is built from the ground up. | §8 |
| P33 | Saad likes how Superpowers does things, and wants it faster, mainly by running in parallel what it runs one step at a time. Evaluate the consequences of parallelizing before deciding whether, and how. | §9 |
| P34 | Saad isn't against verification or thorough testing, only against wasted time. The bottleneck is repeated runs of a slow suite against unchanged code. | §9 |
| P35 | Parallel building works best with isolated agents, 3 to 4 at a time. The aim is roughly 3 to 4 times Superpowers' default speed. | §9 |
| P36 | The plan is designed for parallel work, starting from the spec stage. | §9 |
| P37 | Claims about rules that make Claude write simple code are checked. Only what holds up is kept. | §9 |
| P38 | Research how others already do it before settling how Anvil does it. | §9 |
| P39 | See the whole market before fixing on Superpowers: Anthropic's own skills, skills by Anthropic employees, alternatives, and anything faster. | §10 |
| P40 | Know how updates work: whether they're automatic or manual, which versions are installed, and what should be updated. | §10 |
| P41 | Anvil is Saad's own take on Superpowers: how he wants Claude Code to do the work. | §11 |
| P42 | Anvil contains everything his workflow relies on, even where that repeats another skill, because he doesn't maintain those skills and his flow has to stay consistent and predictable. | §11 |
| P43 | Anvil enforces what Saad likes and removes what he doesn't. | §11 |
| P44 | Anvil takes the best of everything researched, and covers known model limitations and Superpowers' issues. | §11 |
