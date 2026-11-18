<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/re-review-prompt.md -->

# Scoped re-review prompt

After each fix round, one re-review. It gives each finding a verdict and checks the fix diff for new breakage. It isn't a fresh review: the full review already happened. The same prompt serves the final review's single fix wave, with the fix range of the whole wave.

```
Agent (general-purpose), model: [MODEL], run in background
  description: "Re-review T<n> fix round <R>"
  prompt: |
    You are re-reviewing one fix round. A previous review produced findings;
    an implementer has tried to fix them. Give each finding a verdict and
    inspect the fix diff. Nothing else.

    ## The task
    The plan's T<n> section in [PLAN_PATH]. Its S-lines, verbatim:
    [SLINES]

    ## The findings under verification
    [FINDINGS]

    ## The fix
    Read the implementer's report; fix reports are appended at the end:
    [REPORT_FILE]

    Fix base [FIX_BASE_SHA] (the head the previous review saw), head
    [HEAD_SHA]. Diff file: [DIFF_FILE]

    Read the diff file once. If it's missing, run
    `git diff --stat [FIX_BASE_SHA]..[HEAD_SHA]` and
    `git diff [FIX_BASE_SHA]..[HEAD_SHA]` in [LANE_PATH].

    Your review is read-only: don't change the working tree, the index, HEAD
    or any branch. You don't dispatch subagents.

    ## Scope
    The findings list and the fix diff. Give every finding a verdict, and look
    for problems the fix itself introduced. Don't re-review code the fix
    didn't touch: an issue entirely outside the fix diff goes under
    out-of-scope observations, and it doesn't block this task.

    Where the fix report argues a finding was wrong instead of fixing it,
    judge the evidence it gives. Sound evidence makes the finding WITHDRAWN;
    otherwise it stays NOT ADDRESSED.

    ## Tests: never rerun them
    Treat the fix report as unverified claims. Confirm it names the covering
    tests and shows the command and output, and check its claims against the
    diff. Don't rerun tests. If a doubt remains that no reported run answers,
    name the test you would run.

    ## Output
    Your final message is the report. Start with the first verdict. No
    preamble, no narration.

    ### Finding verdicts
    For each finding, in order:
    - **<finding one-liner>** — ADDRESSED | NOT ADDRESSED | WITHDRAWN, with
      file:line evidence. "Attempted" isn't addressed: the defect has to be
      gone.

    ### New breakage in the fix diff
    Severity (Critical / Important / Minor) and file:line, or "none".

    ### Out-of-scope observations
    Non-blocking; the orchestrator logs them for the final review. Or "none".

    ### Verdict
    **Fix round:** All findings addressed, no new Critical or Important
    breakage | Findings remain open: <list>
```

**Placeholders**
- `[MODEL]`: cheap to mid tier for a small fix diff.
- `[FINDINGS]`: the open Critical and Important findings and spec gaps from the previous review, copied verbatim, one per bullet.
- `[FIX_BASE_SHA]`: the head the previous review saw. `[HEAD_SHA]`: the current head.
- `[DIFF_FILE]`: a package of `FIX_BASE..HEAD` (commit list, stat, `git diff -U10`) written into the build folder.
- The rest as in [task-reviewer.md](task-reviewer.md).
