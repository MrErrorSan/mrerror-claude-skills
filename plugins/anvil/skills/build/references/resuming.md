<!-- adapted from superpowers@7.0.2: skills/subagent-driven-development/references/resuming.md -->

# Resuming a build

Read this when a build starts and `progress.md` already has `[~]` or `[x]` tasks, or lanes for this topic exist (`git worktree list`). That happens after `/clear`, compaction, a usage limit, or a second machine. Conversation memory doesn't survive any of them. The commits do: trust `progress.md`, `git log` and the worktrees over your own recollection.

1. **Sync first.** `git fetch`, then `git status`, as in preflight. If another machine landed commit points, pull the synced branch; if the work branch is behind it, reset the work branch to the synced tip only after checking it has no commits of its own that haven't landed.
2. **Read the state.** `anvil topic show` and `anvil progress`, then `progress.md` itself: the wave, the task markers, the indented lines under each task, blockers, the newest decisions, any stop note.
3. **`[x]` tasks are done.** Never re-dispatch them. Confirm that each one's merge is in `git log anvil/<topic>/work`, or that the commit point named after it is on the synced branch.
4. **Each `[~]` task: inspect before you relaunch.** A relaunch over existing work stacks duplicate edits on unreviewed code.
   - Does its worktree exist, and what has it committed since the work branch (`git -C <lane> log --oneline anvil/<topic>/work..HEAD`)? Any uncommitted changes (`git -C <lane> status --short`)?
   - Is there a report file for it in the build folder? A lane that stopped mid-flight (a usage limit) can leave commits and no report. A "completed" status alone proves nothing.
   - Its last indented line says where it stood: a fix round line means it's mid-loop; resume at the next round.
   - Then: a report and commits → carry on from the lane-check. Commits but no report → dispatch a fresh implementer on the same worktree to finish the task and write the report, telling it what's already committed. Nothing at all → dispatch it again.
5. **A merged but unreviewed lane** (merged into the work branch, task not `[x]`): find its merge commit `M`; the lane's range is `$(git merge-base M^1 M^2)..M^2`. Write the review package from that range in the main checkout, and review it.
6. **Then continue** at the first task that isn't `[x]`, in the current wave, and finish that wave's check before the next wave.

Leftover worktrees whose tasks are `[x]` are removed. A `progress.md` that belongs to a different topic, or a build folder from another plan, isn't yours: leave it alone and start your own.
