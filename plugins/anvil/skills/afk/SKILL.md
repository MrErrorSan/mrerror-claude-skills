---
name: afk
description: >-
  Use the moment Saad signals he is stepping away or doesn't want to be
  interrupted: "AFK", "I'm going to bed", "just finish it", "don't ask me
  anything", "no approvals", "work through the plan", "run with it", "make the
  call yourself", "I'll review in the morning". Also use when he pre-approves a
  stop in his own words ("approve the spec yourself", "go straight to the
  build"), because that stage then runs on decisions made for him. Works inside
  an Anvil topic or on a plain request.
---

# AFK: decide, don't wait

Saad is not at the keyboard. Every question you ask now costs hours of dead
time, so a question is the most expensive thing you can produce. The job is to
finish the work and leave a record good enough that he can audit every choice
in a few minutes when he's back.

This is a change of *response*, not of *judgment*. You still notice the same
ambiguities you always would; you resolve them and write them down instead of
stopping. Blocking on a question you could have answered yourself is the
failure AFK exists to prevent. Quietly burying a choice you knew was a coin
flip is the failure that makes AFK untrustworthy. Avoid both.

## Turning it on

- **Inside an Anvil topic** (`anvil topic show` names one): run
  `anvil afk on --quote "<Saad's words>"`. Quote 3 or more consecutive words
  of his latest message that include the AFK phrase, or his whole message if
  it's shorter. A longer verbatim excerpt is fine; invented or paraphrased
  words aren't. The CLI checks the quote against that message, so the model
  can't switch AFK on by itself. If it refuses, AFK is off: don't rephrase
  the quote to force it through. Work up to the next stop, stop there as
  usual, and say why AFK didn't turn on.
- **A pre-approval only** ("approve the spec yourself", "don't stop for the
  plan"): AFK stays off. Pass that one stop with
  `anvil approve <doc> --quote "<his exact words>" --pre` (3+ words, verbatim)
  and run that stage with the decision-making below. Stops his words don't
  cover stay stops.
- **A plain request with no topic:** nothing to switch on. Decide and log the
  same way; the decision log goes in your final reply. If the `anvil` router
  sizes the work direct or full, start the topic first, then run `afk on` from
  the same message.

`anvil afk status` says whether it's on. AFK turns off by itself at
`anvil topic end` and when Saad sends a message with no AFK phrase. Parking
another topic ends it too: run `anvil afk on` again with the same quote. Run
`anvil afk off` when the run ends, so a later stop isn't skipped by accident.

## What changes

| Normally | Under AFK |
| --- | --- |
| Ask a clarifying question | Choose the best reading, log it as a decision, continue |
| "Should I continue?" between tasks | Continue. Don't ask this |
| Stop 1 or stop 2: present and wait | `anvil approve <doc> --afk --quote "<the AFK quote>"` and continue. The CLI records the quote that turned AFK on |
| Wait for approval on an approach | Take the approach, log why |
| The work outgrows its size | Still say so and step up the size, log it, continue |
| Present options and wait | Pick one; name the runners-up in the log |
| Ask before pushing | Push at the plan's commit points (below) |

The `anvil` router and the stage skills still govern everything else: size,
documents, waves, tests and verification. AFK only removes the waiting.

## Commits and pushes

The branches, the commit-point steps and the project-rule override are in
[git-flow.md](../../references/git-flow.md). What AFK adds:

- **Local commits on the work branch** (and lane worktrees branched from it)
  are always allowed. That's how the build records its tasks.
- **The squash onto the synced branch and the push at each of the plan's
  commit points** are authorised by the plan being approved, pre-approved or
  skipped under AFK. No pushes between commit points.
- **A failed push** goes in the final report, and is retried at the next
  commit point.
- **Outside an Anvil plan**, commits and pushes follow the project's rules and
  what Saad asked for, nothing more.

## What AFK never unlocks

These aren't interruptions to optimise away. They're the reason unattended work
is safe to hand back, and AFK grants no permission it doesn't already have:

- **Destructive or irreversible actions:** `push --force`, history rewrites
  (except resetting Anvil's own work branch after a commit point), deleting
  files you didn't create for this task, dropping or migrating data, anything
  `git checkout` can't undo.
- **Branch safety:** no work on `main`/`master` without consent given in
  advance.
- **Anything else leaving the machine:** publishing, posting, sending,
  deploying, calling an outside service with repo content. The plan's pushes
  and the tracker updates the project's rules already allow are the only
  exceptions.
- **Verification.** The end-of-work verification still runs, and no done or passing claim
  stands without fresh evidence.
- **Secrets:** never read, move or embed credentials to get unblocked.

If finishing genuinely needs one of these, that's a legitimate stop (below),
not a question.

## When to stop anyway

Rare, and worth getting right. Pressing on here produces work that gets thrown
away, which costs Saad far more than the wait:

- The request is ambiguous **at the root**: different readings give entirely
  different deliverables, and no assumption rescues it.
- A finding **breaks the plan's premise**: the thing already exists, or can't
  exist as described.
- You're **blocked on access** you don't have: missing credentials, an
  endpoint that doesn't exist, a service that's down.
- Continuing needs one of the never-unlocked actions above.

Stop *late*: finish every part of the work that doesn't depend on the unknown
first. A stop that still delivers 80% of the task is a good outcome; a stop at
the first doubt is what AFK exists to prevent.

**How to stop.** While AFK is on and the stage is `build` or `verify`, the
Stop hook keeps the run going, except while a task is `[~]` (lanes running in
the background report back on their own). It blocks once per stop unless the
`## Stop note` section has changed since AFK turned on or since the last stop.
Any change counts; the convention is a new dated entry saying what's done,
what's left, and why it stopped. If the hook fires right after you wrote a
Stop note, end the turn again.

```markdown
## Stop note
- 2026-11-18 23:40. Done: T1–T4, C1 pushed. Left: T5, T6. Stopped: T5 needs
  the sandbox API key, which isn't in this environment.
```

Write a Stop note only for the reasons above. It isn't a way to end a long run
early; when the hook says tasks are open, pick up the next one.

## Deciding well

You're choosing on Saad's behalf, so choose the way he would:

- **Prefer reversible over irreversible.** A flag you can flip beats a
  migration you have to undo. When two options are close, take the one that's
  cheaper to change later.
- **Prefer the repo's precedent over invention.** If a module already solves
  this shape of problem, follow it, and cite it in the log. A consistent wrong
  guess is easier to fix than a novel one.
- **Prefer the smaller cut.** Ship the narrower thing that works over the
  broader thing that might. Note what you left out.
- **Gate what you had to invent.** A contract that doesn't exist yet (an
  endpoint, a DTO) goes behind a default-off flag, following whatever
  precedent the repo has.
- **Confidence scales disclosure, not silence.** A low-confidence call still
  gets made; it just gets flagged harder.

## The decision log

This is what makes AFK safe. Write each entry when you make the decision;
rebuilding it at the end is how details get lost.

In a topic, entries go under `## Decision log` in `progress.md`: newest first,
append-only, in the format from [formats.md](../../references/formats.md).
Name the question you would have asked inside the reason.

```markdown
## Decision log
- 2026-11-18 **Saved filters persist to localStorage, not the backend** — no preferences endpoint exists, so where should they live? Followed `useColumnVisibility`. Confidence: medium. Changes if: a preferences API is planned.
- 2026-11-18 **Kept the `?type=` param name** — rename to `?kind=`? No caller depends on the old behaviour either way. Confidence: high. Changes if: the API docs already promise `kind`.
```

Without a topic, keep the same entries and put them in your final reply.

## Finishing

When every task is `[x]` and verify has run, run `anvil afk off`. Then give
one report Saad can act on in one pass, in this order:

1. **What shipped:** one line per deliverable and the state it's in, and each
   commit point with its sha and whether the push landed.
2. **Verification evidence:** the actual command output, not a claim about it.
3. **Decisions to review first:** the load-bearing coin flips from the log,
   ordered by what deserves review first, not by time, each with what has to
   change if it's reversed. The full log stays in `progress.md`.
4. **What I'd look at first:** your honest read on the weakest part.
5. **What I didn't do:** anything left out, blocked or deferred, and why.

When an Anvil topic is at the finish stage, end the report with a line
telling Saad to run `/anvil:finish`; only he can run it.

Report faithfully. If something failed, say so with the output; if you skipped
part of the scope, say that plainly. An unattended run that overstates its own
success is worse than one that failed loudly: Saad trusted you because he
wasn't watching.
