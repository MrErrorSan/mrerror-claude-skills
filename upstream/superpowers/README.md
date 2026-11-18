# Superpowers upstream watch: the runbook

Anvil copies and adapts parts of [Superpowers](https://github.com/obra/superpowers) (MIT). Once they're copied, Anvil no longer gets upstream improvements automatically. This folder is how each new Superpowers release gets compared against the parts Anvil took, and adopted or rejected on purpose (design §8.1).

**Trigger:** run this when Saad asks to "check Superpowers upstream", or when a weekly `/schedule` routine reports a new release. There's no network check at session start.

## What's here

| Path | Holds |
|---|---|
| `baseline.json` | The Superpowers version Anvil last synced to |
| `source-map.json` | Anvil file → Superpowers source file(s). Generated: don't edit by hand |
| `manual-sources.json` | Hand-written entries for copied files that don't carry a source line (`NOTICE`, `hooks.json`, `find-polluter.sh`). Merged into `source-map.json` |
| `decisions.md` | The append-only ledger of every upstream change considered: verdict, reason, date |
| `provenance.md` | For each Anvil file: verbatim, lightly edited, adapted or new; what was kept; what changed and why. Also lists the parts not taken |
| `provenance/diffs/` | One diff per mapped file, from the Superpowers source to the Anvil file |
| `reviews/` | One review report per release (`YYYY-MM-DD-vX.Y.Z.md`) |
| `tools/prepare_review.py` | Gathers the data for a release |
| `tools/provenance.py` | Regenerates `source-map.json` and the diffs, and prints each file's status |

Principles that verdicts cite (`P1`, `P2`, …) are in [docs/anvil-principles.md](../../docs/anvil-principles.md).

**Source lines.** Every adapted file names its source with a comment, placed right after the frontmatter, with one comment per source:

```
<!-- adapted from superpowers@7.0.2: skills/<path> -->
```

- Paths are relative to the Superpowers repo root (`skills/…`, `hooks/…`).
- `provenance.py` also reads the same text in a `#` or `REM` comment, as in `hooks/run-hook.cmd`. In a script the `#` line goes right after the shebang.
- A file that doesn't carry a source line goes in `manual-sources.json`.

## The runbook

### 1. Gather the data

```
python -I upstream/superpowers/tools/prepare_review.py <new-tag> [--base <tag>] [--cache <dir>]
```

- **Base:** defaults to the tag in `baseline.json`.
- **Cache:** the clone of `https://github.com/obra/superpowers` goes in `~/.cache/anvil/superpowers-upstream/` (or `$XDG_CACHE_HOME`), never inside this repo. Both tags are checked out under `<cache>/tags/<tag>/`.
- **Output:** the script writes `reviews/<today>-<new-tag>.md`. It refuses to overwrite an existing review. The review has these sections:
  - **Release notes:** the lines added to `RELEASE-NOTES.md`, the linked issues, the commits and the release page. Read the notes for any eval numbers.
  - **Mapped changes:** each changed upstream source once, with its diff and the Anvil files it feeds.
  - **Unmapped changes:** upstream files that changed but feed no Anvil file. Added files (such as new skills) are listed first.
  - **Verdicts:** an empty table to fill in.

### 2. Read the Anvil side

Read these before judging anything:
- the mapped Anvil files, plus their `provenance/diffs/` (what Anvil already changed, and why, is in `provenance.md`);
- [docs/anvil-principles.md](../../docs/anvil-principles.md);
- the design's goals and anti-goals (`docs/anvil-rebuild/2026-11-18-anvil-design.md` §2–§4);
- [decisions.md](decisions.md). A rejection already recorded there isn't reopened without new evidence.

### 3. Classify every change and give it a verdict

Use this rubric:

| Kind of upstream change | Default verdict |
|---|---|
| A. A bug or robustness fix in copied material | Adopt |
| B. Model or Claude Code compatibility | Adopt if it applies to Claude Code; confirm against Anthropic's docs |
| C. A behavior improvement with evidence | Adopt or adapt if it fits the principles. On a conflict, take the mechanism, not the rule |
| D. A behavior change without evidence | Reject, with a note |
| E. A change where Anvil deliberately differs (TDD Iron Law, sequential-only build, ceremony, forceful wording, deleting logs) | Reject, unless the new evidence answers Saad's original reason. Then it goes to Saad |
| F. A new skill or feature | Never adopted automatically; listed as a candidate for Saad |
| G. Support for other agent tools | Ignore |

- **Anything that changes the flow, the stops or a principle always goes to Saad.**
- Weigh each candidate on cost:
  - the 20,000-character skill-size budget;
  - whether it adds ceremony.

### 4. Write the review report, then stop

Fill in the Verdicts table with one row per change:
- the change;
- its category;
- the verdict;
- the reason, as a principle id or evidence;
- the Anvil files affected.

Churn in upstream `tests/`, `docs/` and other-harness files (rubric G) can share one grouped row with one verdict, such as "`tests/**` (12 files) | G | ignore".

Then **stop for Saad's approval.**

**The AFK exception:** in AFK, only categories **A** and **B** are applied without waiting. Everything else waits for Saad.

### 5. Apply

Apply the approved changes as a normal Anvil plan:
1. edit the Anvil files;
2. rerun the skill lint (`python -I -m unittest discover -s tests -t . -p "test_skills.py"`) and the evals;
3. update the records listed below.

## What to update after every review

Do this after every completed review, including one that adopts nothing. Otherwise the next review compares from a stale base and shows the same changes again.

- **`baseline.json`:** the reviewed release's `version`, `tag`, `sha` (the commit the tag points at), `released` and `synced` (today).
- **The source lines:** change `superpowers@<old>` to `superpowers@<new>` in every Anvil file whose mapped sources were reviewed against the new release, whether or not the file changed. Add or remove source lines where a file's sources changed, and edit `manual-sources.json` for files that don't carry one.
- **Regenerate the map and diffs.** Run this against a checkout of the new tag, such as `<cache>/tags/<new-tag>` or the plugin cache copy:

  ```
  python -I upstream/superpowers/tools/provenance.py <superpowers dir>
  ```

  It rewrites `source-map.json` and `provenance/diffs/`, and prints each file's status.
- **`provenance.md`:** update the status column from that output. Update the Kept and Changed cells for every file you edited, and add a row for any newly mapped file.
- **`decisions.md`:** append one row per change considered, including rejections and ignores, with the date, the version, the verdict and the reason.
- **Check:** run `python -I -m unittest discover -s tests -t . -p "test_upstream.py"`. It fails if `source-map.json` is out of date with the source lines, or if `provenance.md` is missing a mapped file.

## How `classify` decides a status

`provenance.py` normalises line endings and ignores the source-line comment. Then:
- **verbatim:** the texts are identical;
- **lightly edited:** a word-level `difflib` similarity of 0.85 or more;
- **adapted:** a similarity below 0.85.

A file with no source is **new**. These labels describe how much text changed. Whether the behavior changed is recorded in the Changed column of `provenance.md`.
