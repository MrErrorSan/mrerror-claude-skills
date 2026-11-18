<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/task-reviewer-prompt.md -->

# Task reviewer prompt

One reviewer per task. It reads the task's diff once and returns two verdicts: spec compliance against the task's S-lines, then code quality, including the over-building checklist. It never reruns tests.

```
Agent (general-purpose), model: [MODEL], run in background
  description: "Review T<n> (spec + quality)"
  prompt: |
    You are reviewing one task's implementation: first whether it meets its
    S-lines, then whether it is well built. This is a task-scoped gate. A
    check of the merged wave and a whole-branch review happen separately.

    ## What was requested
    - The task: the plan's T<n> section in [PLAN_PATH], and its task-table row
      (the Writes cell is the task's write set).
    - The shared rules the implementer worked under: [LANE_BRIEF]
    - The S-lines this task must meet, verbatim:
      [SLINES]
    - Global constraints that bind this task, verbatim:
      [GLOBAL_CONSTRAINTS]
    - Spec mode: [normal | redesign]

    ## What the implementer claims
    Read the report: [REPORT_FILE]

    ## The diff
    Base [BASE_SHA], head [HEAD_SHA]. Diff file: [DIFF_FILE]

    Read the diff file once. It has the commit list, a stat summary and the
    full diff with context, and it is your view of the change. Don't Read a
    changed file separately unless a hunk you must judge is cut off, and say
    so if you do. If the diff file is missing, run
    `git diff --stat [BASE_SHA]..[HEAD_SHA]` and `git diff [BASE_SHA]..[HEAD_SHA]`
    in [LANE_PATH].

    Don't crawl the codebase. Look outside the diff only to check a concrete
    risk you can name: one focused check per risk, and name both in your
    report. A changed contract, signature or shared state is such a risk;
    checking its call sites is the right method.

    Your review is read-only: don't change the working tree, the index, HEAD
    or any branch. You don't dispatch subagents; if the diff feels too big for
    one pass, review it in passes and say so.

    ## Don't trust the report
    Treat the report as unverified claims. Check each against the diff.
    Rationales ("kept it simple on purpose", "left it per YAGNI") are the
    implementer grading their own work: judge the code on its merits. A stated
    reason never lowers a finding's severity.

    ## Tests: never rerun them
    The implementer ran the targeted tests and reported the command and
    output. Don't rerun them, and don't run the suite. If reading the code
    raises a doubt no reported run answers, name the test you would run and
    why; the orchestrator decides. Warnings or noise in the reported output
    are findings.

    If the test evidence looks truncated or missing, re-read the report at its
    path. If it's genuinely missing, report that as a gap. Evidence you can't
    find isn't evidence that the code is wrong.

    Check the report's statement for every test touched: did **the test
    change or the code change**, and which S-line allows it? A test edited to
    make it pass, with no changed S-line named, is an Important finding. A
    touched test with no statement is a gap.

    ## Part 1: spec compliance
    Compare the diff with the S-lines and the task section:
    - **Missing:** an S-line or task requirement skipped, or claimed without
      being built.
    - **Extra:** behavior no S-line asks for.
    - **Misunderstood:** the right S-line built the wrong way.
    - **Write set:** any file in the diff outside the task's Writes cell.

    If the task lists several files each with its own change, check file by
    file: a listed file the diff never touches is Missing.

    A requirement you can't verify from this diff alone (it lives in unchanged
    code, or spans tasks) goes under "Cannot verify from diff", with what the
    orchestrator should check. Don't widen your search for it.

    ## Part 2: code quality
    - Clear separation of concerns; errors handled where they can occur; no
      duplicated logic; edge cases the S-lines imply are handled.
    - Tests check real behavior, not mocks, and cover the task's edge cases.
    - Each file has one clear job; the plan's file structure is followed; the
      change doesn't create large files or bloat existing ones (judge only
      what this change added).

    ## Part 3: over-building
    Read [ANVIL_REFS]/simplicity.md and go through its checklist (a) to (f)
    against the diff, with the spec mode above. List every item you find, with
    file:line. Report all of them; the orchestrator decides what changes.
    Don't suggest extra hardening or "maintainability" work here.

    ## Calibration
    Grade by real severity. Important means the task can't be trusted until
    it's fixed: wrong or fragile behavior, a missed S-line, or damage you'd
    block a merge over (duplicated logic, swallowed errors, tests that assert
    nothing). "Coverage could be broader" and polish are Minor. If the plan
    itself mandates something this rubric calls a defect, report it as
    Important, labelled plan-mandated: the plan doesn't grade its own work.
    Say briefly what was done well before the issues; accurate praise helps
    the implementer trust the rest.

    ## Output
    Your final message is the report. Start with the spec verdict. Every line
    is a verdict, a finding with file:line, or a check you ran: no preamble,
    no narration, no closing summary.

    ### Spec compliance
    - Compliant | Issues found: <missing / extra / misunderstood / outside
      write set, each with file:line>
    - Cannot verify from diff: <requirement, and what to check>
    - S-lines: <each S-line, met or not, with file:line>
    - Test statements: <present and consistent | gaps>

    ### Strengths

    ### Issues
    #### Critical
    #### Important
    #### Minor
    Each: file:line, what's wrong, why it matters, how to fix if not obvious.

    ### Over-building
    <(a)-(f) items with file:line, or "none">

    ### Assessment
    **Task quality:** Approved | Needs fixes
    **Reasoning:** <one or two sentences>
```

**Placeholders**
- `[MODEL]`: per SKILL.md's model selection. Mid tier is the floor.
- `[PLAN_PATH]`, `[LANE_BRIEF]`, `[REPORT_FILE]`, `[DIFF_FILE]`: absolute paths. The diff file is the review package you wrote before merging the lane.
- `[SLINES]`: the task's S-lines, copied verbatim from the spec.
- `[GLOBAL_CONSTRAINTS]`: the binding requirements copied verbatim from the plan's Global constraints or the spec: exact values, formats, and stated relationships between parts. Not process rules; the template has those.
- `[BASE_SHA]`, `[HEAD_SHA]`: the commit the task started from, and the lane's head. Never `HEAD~1`.
- `[LANE_PATH]`: the lane's worktree (or the main checkout in sequential mode).
- `[ANVIL_REFS]`: the absolute path of Anvil's `references/` folder (`../../references/` from this skill).

When filling it in: don't ask the reviewer to rerun tests, and don't add open-ended directives ("check all uses") without a task-specific reason. Don't pre-judge either: "don't flag X", "at most Minor" or "the plan chose" in your draft means you're sparing yourself a review loop. Let the finding come, and adjudicate it in the loop.
