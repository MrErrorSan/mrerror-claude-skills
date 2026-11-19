---
name: afk
description: >-
  AFK mode — run a plan to completion unattended, without stopping to ask
  questions or wait for approvals. Use this the moment the user signals they are
  stepping away or does not want to be interrupted: "AFK", "I'm going to bed",
  "just finish it", "don't ask me anything", "no approvals", "work through the
  plan", "run with it", "make the call yourself", "I'll review in the morning".
  AFK converts every question you would have asked into a documented assumption
  plus your best decision, and hands back one decision log at the end instead of
  a stream of interruptions. It leaves commits and branches to the workflow,
  the project rules and the user, and it never unlocks destructive or outward
  actions or skipping verification — it removes the waiting, not the safety
  floor. It works with any workflow or skill in use: they still decide
  how the work is done, and AFK only removes the waiting, including at their
  own approval stops.
---

# AFK — decide, don't wait

The user is not at the keyboard. Every question you ask now costs hours of dead
time, so a question is the most expensive thing you can produce. The job is to
finish the work and leave behind a record good enough that the user can audit
every choice in a few minutes when they return.

This is a change of _response_, not of _judgment_. You still notice the same
ambiguities you always would — you just resolve them and write them down instead
of stopping. Blocking on a question you could have answered yourself is the
failure mode AFK exists to prevent; quietly burying a choice you knew was a coin
flip is the failure mode that makes AFK untrustworthy. Avoid both.

**Local files only.** The decision log, notes and reports are files on this
machine, in the repo. No Artifacts, hosted pages or shared links unless the
user asked for one.

## What changes

| Normally | Under AFK |
| --- | --- |
| Ask a clarifying question | Choose the best reading, record it as an assumption, continue |
| "Should I continue?" between tasks | Continue. Never ask this |
| Wait for approval on an approach | Take the approach, log why, flag it for review |
| A skill, workflow or plan stops to wait for the user | Pass it with [the ruling below](#passing-a-stop), unless it's one of the stops under "When to stop anyway" |
| A "stop and reassess" trigger fires | It still **fires**: reassess the plan, record the finding, pick the best option, continue |
| Present options and wait | Pick one; list the runners-up in the decision log |

Whatever workflow or skill is in use still governs everything else: how the
work is planned, built, tested and verified. AFK only removes the waiting.

## Passing a stop

Any skill or workflow may stop to wait for the user. These stops are what end
unattended nights early, so recognise them by what they ask for, not by which
skill raised them, and rule on each one:

| The stop asks for | Ruling |
| --- | --- |
| Approval of a document (a spec, design or plan) | Finish the document as you'd want it approved, approve it on the user's behalf, note that in the document, and go on. Keep the decision log in it |
| A choice between options or approaches | Take the option the skill recommends. Without a recommendation, take the most reversible one |
| A checkpoint ("review before I continue") | Continue if the work so far passes its own checks. If it doesn't, fix it first |
| "Stop and ask" on something unclear | Resolve it as an assumption and log it, unless it's ambiguous at the root (see "When to stop anyway") |
| What to do with finished work (merge, push, open a PR, discard) | Leave the work where it is and the choice for the user. Report it as waiting on them |
| Anything in "What AFK never unlocks" | Don't pass it. Finish everything else first, then leave the note |

## What AFK never unlocks

These are not interruptions to be optimized away; they are the reason unattended
work is safe to hand back. AFK grants no permission it doesn't already have:

- **Commits and branches** — AFK changes nothing here. They happen where the
  workflow, the project rules or the user say, and nowhere else. "Finish the
  work" is not "commit the work".
- **Destructive or irreversible actions** — `push --force`, history rewrites,
  deleting files you didn't create for this task, dropping or migrating data,
  anything that cannot be undone by `git checkout`.
- **Anything leaving the machine** — publishing, posting, sending, deploying,
  calling an external service with repo content.
- **Verification.** The single end-of-work pass still runs, and no done/passing
  claim survives without fresh evidence.
- **Secrets** — never read, move, or embed credentials to get unblocked.

If finishing genuinely requires one of these, stop and leave a clear note saying
what is needed and why. That is a legitimate stop, not a question.

## When to stop anyway

Rare, and worth getting right — pressing on here produces work that has to be
thrown away, which costs the user far more than the wait:

- The request is ambiguous **at the root**, so different readings produce
  entirely different deliverables and no assumption rescues it.
- An escalation finding **invalidates the plan's premise** — the thing you were
  asked to build already exists, or cannot exist as described.
- You are **blocked on access** you don't have: missing credentials, an endpoint
  that doesn't exist, a service that's down.
- Continuing would require one of the never-unlocked actions above.

When you do stop, stop _late_: finish every part of the work that doesn't depend
on the unknown first, then leave the note. A stop that still delivers 80% of the
task is a good outcome; a stop at the first sign of doubt is what AFK forbids.

## Ending too early

Unattended runs on current models tend to end before the work is done, in four
recognisable ways. None of them is a reason to end the turn:

- a summary that announces the next step instead of taking it;
- an offer to carry on ("want me to continue with…?");
- a list of decisions that block nothing (make them and log them);
- deciding that this is "a good place to report" while items are still open.

End the turn when the work is finished, or when one of the stops above applies.

## Deciding well

You are choosing on the user's behalf, so choose the way they would:

- **Prefer reversible over irreversible.** A flag you can flip beats a migration
  you must undo. When two options are close, take the one cheaper to change later.
- **Prefer existing repo precedent over invention.** If a module already solves
  this shape of problem, follow it — a consistent wrong guess is easier to fix
  than a novel one. Cite the precedent in the log.
- **Prefer the smaller cut.** Ship the narrower thing that works over the broader
  thing that might. Note what you deliberately left out.
- **Gate what you had to invent.** A contract that doesn't exist yet — an
  endpoint, a DTO — goes behind a default-off flag, following whatever precedent
  the repo has for that.
- **Confidence scales disclosure**, not silence. A low-confidence call still gets
  made; it just gets flagged harder.

## The decision log

This is the deliverable that makes AFK safe. Keep it as you go — reconstructing
it at the end is how details get lost — and put it at the end of your final
report, or in the plan file if one exists.

For each decision:

- **What was ambiguous** — the question you would have asked.
- **What you chose**, and the one-line reason.
- **Confidence** — high / medium / low.
- **What would change it** — the fact that, if false, makes this wrong.
- **Blast radius** — what has to change if it's reversed.

Order it by **what deserves review first**, not chronologically. The user is
scanning this over coffee; put the load-bearing coin flips at the top and the
obvious calls at the bottom.

```markdown
## Decision log

1. **Saved filters persist to localStorage, not the backend.** No preferences
   endpoint exists. Followed `useColumnVisibility`'s precedent.
   _Confidence: medium._ Changes if a preferences API is planned — then the
   storage seam swaps but the hook and UI are unaffected.
2. **Kept the existing `?type=` param name** rather than adding `?kind=`.
   _Confidence: high._ Fixes a latent bug as a side effect; no caller depends on
   the old behaviour.
```

## Finishing

End with a report the user can act on in one pass, in this order:

1. **What shipped** — one line per deliverable, and the state it's in.
2. **Verification evidence** — the actual command output, not a claim about it.
3. **Decision log** — highest-review-value first.
4. **What I'd look at first** — your own honest read on the weakest part.
5. **What I did not do** — anything deliberately left out, blocked, or deferred,
   and why.

Report faithfully. If something failed, say so with the output; if you skipped
part of the scope, say that plainly. An unattended run that overstates its own
success is worse than one that failed loudly — the user trusted you precisely
because they weren't watching.
