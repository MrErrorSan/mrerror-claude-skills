# Change flow-back

Read this when the spec has to change mid-build: Saad changes direction, a review finding conflicts with a decision he made, or a task finds an S-line can't hold as written. The point is that the spec, the plan, the tests and the code stay in step, and that nothing Saad decided is replaced without him seeing it.

## 1. Classify the change

- **Change request:** it alters or replaces behavior an existing S-line describes.
- **New feature:** it adds behavior no S-line covers.

Name what it conflicts with: the S-line, the date it was decided, and any logged decision behind it. Then the cost: which tasks redo, which tests change. Get the list from step 4's `anvil stale` run if you need it, before asking.

If the change makes the work clearly bigger (more than a few tasks, or open questions of its own), say so: it may be a step up in size, or a follow-up plan.

## 2. Push back, or log it

Outside AFK, ask before changing anything:

> Earlier you decided X (S3, 2026-11-18). This replaces it. Cost: tasks T4 and T6 redo, and `tests/test_drafts.py` changes. Proceed?

Saad's answer is the decision. Lanes keep running meanwhile unless their tasks cite the affected S-line; those wait at their next report.

In AFK, or in a stage Saad pre-approved, don't ask. Make the call and log it:

```
- 2026-11-20 **CR: S3 replaced by S7 (<one line>)** — <reason; what it conflicts with; tasks redone>. Confidence: medium. Changes if: <fact>.
```

A new feature that turns up in AFK and no S-line needs is not built on your own initiative: log it, and list it under "not done" for the report. A change request needed to make the approved behavior work is made, and logged.

## 3. Retire the S-line and add the new one

In the spec (`spec.md`, or the spec part of a direct-size `plan.md`), formats in [formats.md](../../../references/formats.md):

```
- ~~**S3** Old behavior.~~ RETIRED → S7 (2026-11-20, CR: reason)
- **S7** New behavior.
```

The new line takes the next unused number; numbers are never reused. A new feature adds its S-line the same way, without a retirement. Add an entry to the spec's change log.

## 4. Find what pointed at the old line

`anvil stale` lists every task and test whose Spec cell names a retired S-line, and flags recorded results that no longer match the tree. Reopen each one:

- a task that was `[x]`: back to `[ ]`, or a new fix task if most of it stands;
- a task in flight: stop it at its next report and re-brief it with the new S-line;
- its review: the task is reviewed again against the new S-line once it's rebuilt;
- a test: its row in the plan's test list is updated, and the test itself changes in the task that reopens.

## 5. Update everything in the same step

The plan's task table (Spec cells, new or changed tasks, their write sets), its test list, `progress.md` and the code change together, never one ahead of the others. A test edited because of the change names the new S-line in its commit or progress entry; that's what makes the edit a **test changed** and not a test bent to pass. A task that changes its write set or adds a task in an active wave reruns `anvil plan-check`; if that fails, the affected tasks run in sequence.

Then carry on with the build from the reopened tasks.
