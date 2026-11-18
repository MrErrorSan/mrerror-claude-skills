<!-- adapted from superpowers@7.0.2: skills/receiving-code-review/SKILL.md -->
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/references/fix-loop.md -->
<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/references/cannot-verify.md -->

# Receiving a review

Read this whenever a review comes back with anything other than two clean verdicts, and again before every fix round. It covers the per-task, wave and final reviews, and review comments from Saad.

## Read it as claims

A review is a set of claims about the code, from an agent that has seen less than you have. Before acting on a finding, read the lines it cites and check it against the code, the S-lines and the plan. Restate what it asks for in your own words; if you can't, it isn't clear enough to dispatch.

Agreeing out loud adds nothing. Don't write "good catch" or "you're right"; state the fix, or the evidence against the finding. Your verification decides which findings go into the loop; it doesn't let you drop them quietly.

## Triage

Sort every finding before any fix goes out.

- **Spec gap, Critical, Important:** into the fix loop.
- **Cannot verify from diff:** resolve it yourself before the task is `[x]`; you hold the plan and the cross-task context the reviewer lacked. A real gap goes into the loop as a failed spec item. Not a gap: one indented line under the task saying what you checked.
- **Over-building items** (the simplicity checklist): remove each piece unless an S-line needs it. Removals go into the loop; each piece you keep gets a decision-log entry naming the S-line that needs it.
- **Plan-mandated, or in conflict with the plan's text:** yours to rule on, with the spec as the binding authority. Log the ruling before acting on it. Don't dismiss a finding because the plan mandates it, and don't dispatch a fix that contradicts the plan without a logged ruling.
- **In conflict with a decision Saad made** (a logged decision, an S-line he approved): don't fix it in the loop. Take it through [change-flow-back.md](change-flow-back.md).
- **Minor:** never enters the loop. Record it as an indented line under the task in `progress.md` (`  - minor (deferred): <one-liner>`), and point the final review at these lines. A roll-up nobody reads is a silent discard.
- **Out-of-scope observations** from a re-review: recorded the same way, as deferred minors. They never extend the loop.

Indented lines under a task aren't counted as tasks, so they're safe in `## Tasks`.

## The fix loop

A fix round is one fix dispatch plus one scoped re-review. **Five rounds at most per task.**

- **Rounds 1–3:** resume the original implementer with the open findings verbatim, using the fix message in [../prompts/implementer.md](../prompts/implementer.md). Its context is intact: it knows the task, the code and its own choices. If the agent can't be resumed, dispatch a fresh one with the lane brief, the report file and the findings; the report file is the memory either way.
- **Rounds 4–5:** a fresh implementer on a model one tier up, with the same inputs and this framing: "A prior implementer attempted this task <N> times; you own it now. Read the report file for what was tried." A loop that survives three resumes usually means the implementer can't see its own problem.
- **Every round:** the implementer checks each finding against the code (it may argue one is wrong, with evidence), fixes the rest, reruns the covering targeted tests through `anvil run --scope targeted`, appends a fix report and commits. Before the re-review, confirm the fix report has the covering tests, the command and the output. Name the covering test files in the fix message: a one-line fix doesn't need more.
- **The re-review is scoped:** package `FIX_BASE..HEAD`, where FIX_BASE is the head the previous review saw, and dispatch [../prompts/re-review.md](../prompts/re-review.md) with the findings, the report and the package. New Critical or Important breakage in the fix diff joins the open findings.
- **After each round,** add an indented line under the task:
  `  - fix round <R>/5: <X> addressed, <Y> open (<one-liners>); <a7>..<b7>`
- After a wave, fixes are batched by disjoint file groups ([waves.md](waves.md), "Batched fixes"). A batched round counts as one round for every task it touches.

Never fix findings yourself in the orchestrator session: your context stays for coordination, and an orchestrator fix skips review.

## The breaker

When round 5's re-review still leaves findings open, stop dispatching and adjudicate each open finding yourself:

- **The reviewer is wrong, or the point is contestable:** park it. A decision-log entry: `- <date> **T<n> parked: <finding>** — <why the code stands>. Confidence: <level>. Changes if: <fact>.` The final review sees both sides.
- **Real, but nothing downstream builds on it:** park it the same way, saying it's real and deferred.
- **Real and load-bearing** (a later task builds on it, or it shows a plan defect): rule on the smallest change that unblocks the dependent work, log it, and carry it into the next dispatch that touches the area. Parking a structural failure lets every dependent task build on it. Stop only when the defect leaves every path forward a guess.

Adjudicate only at the cap. Adjudicating earlier to end a loop is pre-judging under another name. Every adjudication is a decision-log entry; nothing is dropped silently.

## Feedback from Saad

Saad's review comments are trusted: implement them once you understand them. Still:

- If any item is unclear, ask about every unclear item before implementing any of them. Items are often related, and a partial reading builds the wrong thing.
- If an item conflicts with an approved S-line or a logged decision, it's a change request: [change-flow-back.md](change-flow-back.md).
- If an item would add something nothing uses, check for real usage first (search the code) and say what you found.
- If you think an item is technically wrong for this codebase (it breaks existing behavior, a platform or version needs the current code, the context is missing), say so once, with the evidence, and let him decide. If you pushed back and were wrong, say what you checked and fix it; no long apology.
- Implement in this order: blocking issues (breakage, security), then simple fixes, then complex ones. Each change goes through an implementer and the targeted tests, like any fix.
