<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/task-reviewer-prompt.md -->

# Wave review prompt

One short review per merged wave, on the merged tree. Per-task reviewers each saw one lane's diff; each lane passed its own tests. This review looks for what neither could see: merges that applied cleanly but are wrong together. It is not a second per-task review.

```
Agent (general-purpose), model: [MODEL], run in background
  description: "Wave <w> review (semantic conflicts)"
  prompt: |
    You are checking one merged wave of a parallel build for semantic
    conflicts: changes from different lanes that merged without a textual
    conflict but don't fit together. Each lane was reviewed on its own
    already. Don't repeat those reviews; look between the lanes.

    ## The wave
    - Tasks in this wave, their S-lines and write sets: the task-table rows
      for [TASK_IDS] in [PLAN_PATH], and those tasks' sections.
    - The pinned contracts every lane was given: [LANE_BRIEF], section
      "Pinned contracts".
    - The spec's shared surface and cross-cutting scenarios: [SPEC_PATH].
    - The merged diff: [DIFF_FILE] (wave start [WAVE_BASE_SHA] to merged
      head [HEAD_SHA], in [WORK_PATH]).
    - Results already recorded on this tree (type-check, targeted tests,
      smoke): [CHECK_SUMMARY]

    Read the diff file once. Look outside it only to check a concrete risk you
    can name, one focused check per risk, and name both in your report.

    Your review is read-only: don't change the working tree, the index, HEAD
    or any branch. You don't dispatch subagents. Don't rerun tests: the
    results above are the test evidence. If a doubt remains, name the test you
    would run.

    ## What to look for
    1. **Contract drift:** a producer and a consumer that spell a pinned name,
       field, type, route or signature differently, or disagree on its shape,
       units or nullability.
    2. **Replace against extend:** one lane replaced or removed something that
       another lane extended or called.
    3. **Duplicates across lanes:** two lanes that each added a helper, type,
       constant or config key for the same thing.
    4. **Shared files:** registries, barrels, route lists, manifests or config
       that more than one lane touched, merged into something inconsistent
       (an entry lost, doubled, or out of order where order matters).
    5. **Ordering and state:** one lane assumes an initialisation order, a
       default, or a state another lane changed.
    6. **Cross-cutting scenarios:** a spec scenario that needs these tasks
       together and that the merged code no longer meets.

    Ignore per-lane style and anything the per-task reviews own (a single
    lane's quality, its tests, its over-building).

    ## Output
    Your final message is the report. No preamble.

    ### Conflicts
    #### Critical
    #### Important
    #### Minor
    Each: the lanes involved (T<a>, T<b>), file:line on both sides, what
    breaks and for whom, and the smallest fix.

    ### Contracts checked
    One line per pinned contract: consistent | drift (file:line).

    ### Verdict
    **Wave:** Clean | Needs fixes
```

**Placeholders**
- `[MODEL]`: mid tier.
- `[TASK_IDS]`: the wave's tasks.
- `[DIFF_FILE]`: a package of `WAVE_BASE..HEAD` on the work branch (commit list, stat, `git diff -U10`), written into the build folder after every lane of the wave merged. `[WAVE_BASE_SHA]` is the work branch tip before the wave's first merge.
- `[CHECK_SUMMARY]`: one line per check already run on the merged tree, with its command and summary line.
- `[WORK_PATH]`: the main checkout, on the work branch.
