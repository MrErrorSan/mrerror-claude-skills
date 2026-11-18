---
name: brainstorm
description: >-
  Use once the anvil router has started a direct or full topic, or when Saad
  runs /anvil:brainstorm or asks to think a change through, scope it, weigh
  options or write its spec before anything is planned or built. Use it for
  features, bug fixes, refactors, migrations, POCs and redesigns in a codebase,
  including when Saad has only a rough idea of what he wants.
---
<!-- adapted from superpowers@7.0.2: skills/brainstorming/SKILL.md -->

# Brainstorm

You are very good at building. You build what you believe Saad wants, and that belief is usually thinner than it feels. This stage is for finding out what he actually wants, and why, before anything gets built.

People often haven't finished working out what they want. Good questions help them think it through. When you understand the why, you make the hundred decisions he never mentions the way he would have made them.

**Where this sits.** The router has stated the size and run `anvil topic start`; `anvil topic show` gives the topic folder. If it reports no active topic, state the size line and run `anvil topic start <slug> --size <size>` first, as the router does. This stage ends with a written spec:

- **Full size:** `<topic dir>/spec.md`, a builder check, `anvil present spec`, then **stop 1**.
- **Direct size:** the spec part at the top of `<topic dir>/plan.md`, then straight on to `anvil:plan` in the same document. The one stop is at the plan.

Nothing gets built before the stop: no product code, scaffolding, dependency installs or implementation skills. Reading, looking things up and writing the documents are fine. While the plan is unapproved, a hook denies edits outside the topic folder.

## Look before you ask

In an existing project, or when Saad has given you context (a spec, a plan, a handoff, files he pointed at, earlier conversation), dig in before your first message. Read what he referred to and the code or material it connects to, and keep reading until you can explain how the relevant parts work today and what this change would touch.

Finding facts is your job, never Saad's. The decisions are his. Anything the repo, the docs or the earlier conversation can answer gets looked up, not asked, and nothing he has already decided gets reopened. When a lookup is broad (several modules, a library's behavior, how other projects solve it), hand it to a subagent with a narrow brief and keep going; only the questions that depend on its answer wait for it. Say what you looked for and what you found.

**A bug with an unclear cause:** use `anvil:debug` to find the cause, then write the spec part: the bug, the expected behavior as S-lines, and the repro that becomes a keep test.

## The question round

Ask a question only when the answer would change what gets built and neither the request nor the project answers it. With no question open, skip the round and write the spec. Everything else is your call: state it as a decision in the spec, with your reason, where Saad will review it. Process steps are always your calls (writing things up, where files go, looking further, how to show something): do them and say so.

**Map the decisions first.** Every decision branches into the decisions that hang off it. The open decisions whose prerequisites are already settled are the ones to ask now.

**Open with the request in your words.** Start the round's message with two or three lines restating what he asked for, as you understand it, plus anything the lookup found that changes the request: a constraint, a conflict, a cheaper path.

**Ask them all in one batched round.** Number each question and give your recommended answer, worded so that "yes" accepts it:

```
**Q1 Who can see a shared draft?** Today drafts are private to their author
(`drafts/policy.ts`). Sharing changes the permission check and the list query.
Recommended: anyone with the link can read; only the author can edit.

**Q2 ...**
```

End with one line: "Reply yes to take every recommendation, or yes except Q2: …". A question whose answer depends on another question still open in the same round waits: write your expected answer for it into the spec as a decision, and it gets checked at the stop.

**Get him describing when the why is missing.** If you don't know why he wants this, make the first question an open one, in his own terms, with no options and no recommendation. He answers it in his own words, so "yes to every recommendation" doesn't cover it. His words carry intent your options can't. Once you know why, sketch the choices concretely, with what each trades off and which you'd pick. When he says "just guess" or "what do you think?", propose something concrete.

**How it gets made.** Read from how he talks which choices he wants to make. If he raises the how or asks about trade-offs, give the options with your pick. If he talks about outcomes, he is handing you the how: make those calls and state each in a line. When there's existing work, build on what it already uses. A choice you make goes in the spec as your call, never as something he agreed to.

**Make every question specific** to his project and what he told you. Build it on something you found, so it helps him think through a consequence or a case he may have missed. Use plain language and his vocabulary, with no process jargon. You never need to quote this skill to him.

**Ground to cover.** This is territory, not a script; never read it out as questions: what kind of thing this is and what makes it special; why now and what success looks like; goals, non-goals and anti-goals (what would make it a failure even if it technically works); prior art he loved or hated; what exists now and what he has tried; the details he cares about.

If his answers open a new question that changes what gets built, ask it in one short follow-up round. Otherwise there is no second round: the rest becomes decisions in the spec.

## Variations when information is thin

When Saad doesn't have the full picture yet, don't interrogate him. Show 2 or 3 worked options he can react to, and recommend one.

- Come up with several real alternatives and drop the weak ones, including any that work against why he wants it and any the existing code rules out.
- Sketch the two or three that remain concretely enough to picture, grounded in what the project actually does, with what each trades off. Research on the web where that helps; for a big question, `anvil:cross-model` can research it independently.
- Put them in the question round as one question whose recommended answer is your pick. The ones not taken go into the spec's Decisions as alternatives.
- When there's genuinely one sensible way, say so and say why the others don't fit.

Whenever seeing would help more than reading, and the look isn't the open question, sketch it in text: a few lines of what he'd see.

## The exploration loop

When the look itself is open and Saad's to decide, talking won't settle it. A question about a UI topic isn't automatically a visual one. Offer the loop as a question in the round, with a recommended answer. Text sketches cover the rest. If he takes it, `anvil:ui-mockup` runs the loop:

1. research;
2. a shared `BRIEF.md`;
3. 2 to 4 variants built in parallel, one file per agent;
4. a comparison `index.html` and screenshots;
5. Saad's reaction;
6. if the round misses, a measured critique (`FLAWS.md`), and the next round (`-r2`, `-r3`, …) changes only what he reacted to.

Mocks live in `docs/<slug>/mocks/` and are throwaway. The chosen one becomes the spec's visual reference: link it in the header, and point the S-lines that describe what he'll see at it.

## When brainstorming ends

It ends when no question is left open. Every decision is in one of three places:

- answered by Saad;
- decided by you, and written into the spec as your call with its reason;
- among at most three **Waiting on you** questions at the top of the spec, each with a recommended answer.

If more than three of Saad's questions remain, the brainstorm isn't finished: ask them as a round first.

If the work has grown past its size (open questions on a direct topic, more than about 5 tasks), say so and step up: `anvil topic start <slug> --size full`. If it's really several independent projects, say so, agree an order with Saad, and brainstorm them one at a time.

## Write the spec

Write a plain document, for a human, that a talented builder in the domain could plan from without going back to Saad. Use [spec-template.md](references/spec-template.md) and the pinned header and S-line formats in [formats.md](../../references/formats.md).

- **Header:** `- **Approved:** no`, `- **Mode:** normal` or `redesign`, `- **Size:**`, dates, and the link to the mock or reference.
- **Waiting on you:** at most three questions, each with a recommended answer.
- **Spec lines:** one behavior per line, numbered `S1`, `S2`, … in the parseable form. A line is never edited in place: a change gets a new number, and the old line is struck through and marked `RETIRED → S<n>`.
- **Goals** carry a **Constraints** line (platform, performance, compatibility). **Left to the builder** lists what you're leaving open on purpose.
- **Shared surface:** the exact names of the types, routes, contracts, files and resources more than one part touches. The plan's parallel split is built from this list, so leave nothing implied.
- **Replaces / stays** (redesign mode only): what the design replaces, what existing code stays, and what must keep working. "Reuse existing" applies only to what's listed under stays.
- **Decisions:** each with the call, the reason, the alternatives not taken, and whether it is *decided* (by Saad, or as your call) or *waiting on Saad*.
- **Change log:** a dated "Created" entry. Later entries say whether each change is a change request or a new feature, and what earlier decision it conflicts with.

Only what Saad said goes in as his. Anything you filled in is marked as your call.

**A bug fix** keeps the spec part to a few lines: the bug, the expected behavior as S-lines, and the reproduction steps. The repro test is written before the fix and stays as a keep test.

**Direct size** uses the same sections, kept short, at the top of `plan.md`, under the header lines. Leave the plan part to `anvil:plan`.

## Builder check (full size)

Before stop 1, a fresh reader checks the spec. When you tell Saad you're writing it up, say a reviewer will read it first.

1. Dispatch a fresh general-purpose subagent with [builder-check.md](prompts/builder-check.md), filled in with the domain and the spec path. Don't hand the spec over until the check is back.
2. Sort what the builder asks into three piles:
   - **Answered already** by the conversation or the project: put the answer in the spec.
   - **Minor:** a sensible builder could settle it without changing what gets built. Settle it yourself and mark it in the spec as your call.
   - **Saad's:** only he can answer it, and the answer changes what gets built. It goes into **Waiting on you**, most important first, with your recommended answer.
3. That's the only round of questions the check produces. If the **Saad's** pile would push **Waiting on you** past three, ask the extras as that round before stop 1 and fold his answers into the spec. Without a subagent tool, or if the dispatch is denied, read the spec as that builder yourself.

Direct size skips the builder check: the plan's own checks cover the merged document.

## Stop 1 (full size)

1. Run `anvil present spec` after your last edit. Any later edit needs another `present`.
2. Send Saad one message: the spec's path, a few lines on what it says, the **Waiting on you** questions with their recommended answers, and a short list of the calls you made, so he can check those while reading. End with how to approve: "Reply yes to approve with the recommendations, or tell me what to change." Then end the turn.
3. On his reply:
   - **He approves** (with or without answers): run `anvil approve spec --quote "<his words>"`, three or more words from his reply or his whole message. Then fold his answers in as decisions (`decided by Saad`), not change requests, and move them out of Waiting on you. An answer that changes an S-line retires it and adds a new number, as above.
   - **He asks for changes:** make them, run `anvil present spec` again, and stop again.
   - **`approve` refuses:** tell him the reason it gave. Don't work around it, and never write the `Approved:` line by hand.
4. After approval: `anvil:plan` (it runs `anvil topic stage plan`).

**Pre-approved or AFK.** If Saad's own words already pass this stop ("approve the spec yourself", "go straight to the build"), run `anvil approve spec --quote "<his exact words>" --pre` instead of stopping. If AFK is on, run `anvil approve spec --quote "<the AFK quote>" --afk`. Either way, the Waiting on you questions take their recommended answers, and each choice made for him goes into `progress.md`'s decision log with its reason and confidence (create the file from [formats.md](../../references/formats.md) if it isn't there). Then go on to `anvil:plan`, as after a normal approval.

## Direct size: on to the plan

Once the spec part is written, invoke `anvil:plan` and carry on in the same `plan.md`. Don't present or stop here; Saad reviews the spec part and the plan together at stop 2.

## Traps

| Thought | Reality |
|---|---|
| "I'll offer a menu of what he might want" | Options steer. Until you know why he wants it, ask him to describe it. |
| "I'll fill in sensible defaults" | Good. Write them in the spec as your calls. A default he never saw is one he couldn't reject. |
| "Quick question to confirm how X works" | If the repo answers it, look it up. |
| "One more round of questions" | Points that don't change what gets built are your calls, written into the spec. |
| "He said 'sounds good' to the idea" | Approval covers what he saw. Only `anvil approve` after `anvil present` passes the stop. |
| "I'll start a small piece while he reads" | Nothing gets built before the stop. |
| "The old code shows how it should work" | In a redesign, the spec's stays list says what is reused. The rest is designed from the spec. |
