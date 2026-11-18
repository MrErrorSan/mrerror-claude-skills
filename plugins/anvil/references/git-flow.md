# Git flow

Where a project rule exists (its `CLAUDE.md`, `.claude/rules/*`), the project rule wins. For example, a repo that says "commit and push after every unit of work" treats each commit point as that unit.

## Two branches

- **The synced branch** is chosen at the plan stop and written in the plan header (`- **Synced branch:** …`, see [formats.md](formats.md)). It is one of: local only; a branch made from an existing remote branch; or a new remote branch. Using `main` or `master` needs Saad's explicit consent. The synced branch only ever receives **one squashed commit per commit point**.
- **The work branch** `anvil/<topic>/work` is local. It is branched from the synced branch and holds every task commit, lane merge and fix. Lane worktrees branch from its HEAD.

## At each commit point

Commit points (C1, C2, …) sit only at wave boundaries. A small plan has one, at the end.

1. Reuse the recorded checks (`anvil fresh`), rerunning only what changed.
2. Squash the work branch into the synced branch as one commit, with the plan's message.
3. Push, if the plan's row says `yes`.
4. Reset the work branch to the synced branch's new tip, so the next squash doesn't re-apply commits that already landed.
5. Record it in `progress.md`: `- C1 <sha> pushed <date>`, and mark the tasks it closed `[x] C1`.

Approving the plan, or pre-approving it, authorises its pushes. In AFK, Anvil pushes at each commit point.

If a push fails, say so plainly, keep working locally, and retry at the next commit point. A failed push is never reported as a success.

## Never

- Never force-push the synced branch. Resetting Anvil's own local work branch is fine.
- No work on `main` or `master` without Saad's consent.
- No `Co-Authored-By: Claude …` trailer, or any other Claude or Anthropic attribution, in commit messages. No "Generated with Claude Code" footer in PR bodies unless Saad asks.

## Cleanup, in finish

- After the last push is confirmed on the remote, delete Anvil's own local work branch and its worktrees.
- List other stale local `anvil/*` branches, and remote ones whose work is already merged. Delete them only after Saad confirms.
- Deleting a remote branch always needs confirmation.
