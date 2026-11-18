---
name: finish
description: Use when Saad runs `/anvil:finish` on an Anvil topic after `anvil:verify` has landed the work (stage `finish`), to push or merge beyond the plan's commit points, open a PR, update the ticket, or clean up branches.
disable-model-invocation: true
---
<!-- adapted from superpowers@7.0.2: skills/finishing-a-development-branch/SKILL.md -->

# Finish

Finish is optional. Verify normally lands the last commit point itself, running this skill's sections 2 to 5, so the work is already on the synced branch. Finish handles what's left that needs Saad: pushes and merges beyond the plan's commit points, a PR, the ticket, the clean-up, and the report. If verify couldn't land it, finish does it here. Most committing and pushing already happened at the build's commit points ([git-flow.md](../../references/git-flow.md)). Saad started this, so the questions here get asked; they're batched into one message so he answers once.

**Project rules win.** The project's `CLAUDE.md` and `.claude/rules/*` override these steps where they differ. A repo that says "commit and push after every unit of work" treats each commit point as that unit. Follow its sync rules too: if it asks to name untracked files before a push, name them.

**Branch safety, throughout:** no work on `main` or `master` without Saad's consent; never force-push the synced branch (a rejected push means the remote moved: look, and say so); no `Co-Authored-By` trailer or any Claude or Anthropic attribution in commit messages, and no "Generated with Claude Code" footer in PR bodies unless he asks. Resetting or deleting Anvil's own local work branch is fine.

## 1. Entry

1. `anvil topic show`. If the stage isn't `finish`, say which stage it's at and offer `/anvil:verify` (or the build) first. Go on only if Saad says so, and note in the report that verify didn't run.
2. `git fetch`, then `git status`. If the synced branch (the plan header's `- **Synced branch:**` line) is behind its remote, pull it; if it has diverged, stop and tell Saad.
3. Read, once:
   - `progress.md`: tasks with their indented notes (`  - tests: …`, deferred minors, parked findings), `## Commit points`, `## Decision log`, `## Stop note`;
   - the plan's `## Test strategy` and `## Commit points` tables;
   - verify's notes, `$(git rev-parse --path-format=absolute --git-common-dir)/anvil/build/<slug>/verify.md`: the converge table, the evidence, the leftovers.
4. If `## Commit points` already lists every row of the plan's table, verify landed the last one (its line reads `(this commit)`); that is the normal case. Skip sections 2 to 5: take its sha from `git log -1 --format=%h <synced>`, check the push as in section 5, and go on to section 6.

## 2. Entry checks

Check now, before deleting or editing anything: the tree key covers every file except the topic's `progress.md`, so the scaffold deletions and Status edits below change it. These runs confirm that verify's results cover the tree it left.

```bash
anvil fresh --scope full -- <full-suite cmd>
anvil fresh --scope check -- <cmd>    # each of type-check, lint and build that isn't none
anvil fresh --scope smoke -- <cmd>    # each smoke command verify ran without --external
```

Exit 1 means no passing result for this tree: rerun that one with `anvil run` and the same scope. `--external` paths are never reused; verify.md holds their result, so don't call the live service again.

A check that is red, or not fresh and failing on rerun, stops finish here, before the squash: report it with its output and ask Saad how to go on. The exception is a failure Saad already accepted as a verify leftover; name it in the report.

These checks aren't rerun after sections 3 and 4. Deleting test-only files nothing references and editing header lines don't change what any test runs; the report says the deletion and the edits came after the runs.

## 3. Scaffold tests

Every `scaffold` row in the plan's test list is deleted now, so the deletion travels in the last commit point.

- Before deleting one, search for references to it (imports, fixture paths, test config). A file a keep test or the product code still uses isn't scaffold any more: keep it, and log that in the decision log with the file that uses it.
- Delete the rest, on the work branch, and list each file for the report.
- If you had to change anything else to delete them, run the type-check and the affected targeted tests through `anvil run`.

## 4. Mark the documents done

- In `spec.md` and `plan.md` (direct size: `plan.md` only), set the `- **Status:**` header line to `- **Status:** done <YYYY-MM-DD>`. Brainstorm's template writes `draft`, so the line is usually there: update it. If it's missing, add it next to `- **Approved:**`. Leave the `Approved:` line exactly as it is.
- In `progress.md`, set `- **Stage:** done`, mark every task the last commit point closes `[x] T<n> <title> C<k>`, and add its line under `## Commit points` before the squash: `- C<k> (this commit) <date>`. Its real sha and push result go in the report and the ticket comment, never in a later commit: the synced branch gets exactly one squashed commit per commit point.
- The progress file stays as the record. Don't delete it.

## 5. The last commit point

```bash
git status                                # nothing that belongs to the work left untracked
git add <topic folder> <deleted scaffold files>
git commit -m "docs(<slug>): done markers"  # on the work branch
git switch <synced>
git merge --squash anvil/<slug>/work
git commit -m "<the plan's message>"      # no co-author trailer
git push                                  # only if the row says yes; `git push -u <remote> <synced>` the first time
```

**Confirm the push landed:** `git rev-parse <synced> <synced>@{u}` prints the same sha twice. If the push fails, say so plainly: it's not done, the work branch stays, and "retry the push" goes in the questions (section 8). A failed push is never reported as a success. A `Push: no` row is local by design; say so in the report.

## 6. The ticket

If the repo tracks its work in a ticket system, run `anvil:ticket-update` for the completion comment: the evidence (the full-suite summary line, the smoke results, the commit point shas and where they're pushed) and the stand-up line. No tracker, skip this.

## 7. Clean-up, before the report

Run this from the main checkout, not from inside a worktree you're about to remove.

- **Lane worktrees** for this topic (`git worktree list`, branches `anvil/<slug>/T<n>`): `git worktree remove <path>`, then `git branch -d anvil/<slug>/T<n>`, then `git worktree prune`. These don't depend on the push.
  - A worktree removal refused because it holds modified or untracked files: those files exist nowhere else. Don't force it. Show `git -C <path> status --porcelain -uall` and ask Saad: commit them, move them, or delete them.
  - A `git branch -d` refusal means the branch holds work that isn't merged. Don't force it with `-D`: list the branch and its unmerged commits (`git log --oneline <synced>..anvil/<slug>/T<n>`) for Saad.
- **The work branch**, only once the push is confirmed: `git switch <synced>`, then `git branch -D anvil/<slug>/work`. It was squashed into the synced branch, which is on the remote.

The build folder stays until section 9: the report cites `verify.md` and the screenshots in it.

**Only after Saad confirms** (they go in the questions below):
- the work branch, when the synced branch is local-only or the push didn't land;
- lane branches `git branch -d` refused;
- other stale local `anvil/*` branches (`git branch --list "anvil/*"`);
- remote `anvil/*` branches whose work is already merged (`git branch -r --merged <synced> --list "<remote>/anvil/*"`). Deleting a remote branch always needs his confirmation: `git push <remote> --delete <branch>`.

## 8. The report and the questions

One message: the report first, then the questions. The report covers, in this order:

1. **What shipped.** The behavior, by S-line; the commit points with their shas; where they're pushed, or that the push failed.
2. **Verification evidence.** Real output: the full-suite, type-check, lint and build summary lines (and which tree they ran on, from the entry checks), each smoke path's result, and the converge table from `verify.md`. Say that the scaffold deletion and header edits came after those runs and change nothing a test runs.
3. **The tests, by type.** Failures and weak spots come first: a failing or skipped test, an S-line met only by test evidence, a leftover from verify, a check that couldn't run here. Then:
   - keep tests, each with the S-lines it guards (from the plan's test list);
   - smoke paths run;
   - bug repros added;
   - scaffold tests deleted, one line per file (and any kept, with the reason);
   - any test changed, and why: from the `  - tests:` lines under each task in `progress.md`, saying whether the test or the code changed and which S-line allowed it.
4. **The decision log,** most review-worthy first: low confidence before high, and anything that replaced one of Saad's decisions at the top.
5. **The weakest part.** The one place most likely to break or to need rework, and why.
6. **What wasn't done.** Leftovers from verify, deferred minors, parked findings, anything cut.

Then the questions, numbered, only the ones that apply:

- **Retry the push** (it failed): retry now, or keep it local for now.
- **Make it live** (the synced branch is local-only): push it to a new remote branch, or to an existing one (name it), or keep it local.
- **Merge** the synced branch into another branch:
  1. merge it into `<branch>` locally;
  2. push and open a pull request into `<branch>`;
  3. keep it as it is.
- **Delete** the branches listed in section 7 that need his confirmation, by name.

Wait for his answer.

## 9. On his answer

- **Retry the push:** push, confirm with `git rev-parse <synced> <synced>@{u}`, then delete the work branch as in section 7. A second failure is reported the same way.
- **Merge locally:** confirm the target branch first, since a wrong base is costly to undo. `git switch <target>`, `git pull`, `git merge <synced>`. A fast-forward leaves the tree already checked: nothing to run. A real merge gets `anvil run --scope full -- <full-suite cmd>` on the merged result; if it fails, stop, leave the branches as they are and say so. Merging into `main` or `master` needs his choice to name it. Push the target only if he says to.
- **Pull request:** push the synced branch if it isn't on the remote, then open the PR with the forge's CLI, following the repo's PR template, with no Claude footer. Give him the URL.
- **Keep:** nothing to do.
- **Discard:** only if he asks to throw the work away. List what would be lost (branches, commits, worktrees) and ask him to type `discard` to confirm.
- **Deletions:** delete exactly the branches he confirmed.

Then remove the build folder and close the topic:

```bash
rm -rf "$(git rev-parse --path-format=absolute --git-common-dir)/anvil/build/<slug>"   # check the path ends in anvil/build/<slug> first
anvil topic stage done
anvil topic end
```

End with one line per thing done: merged, pushed, the PR URL, branches deleted, topic closed.
