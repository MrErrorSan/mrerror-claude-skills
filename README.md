# MrError Claude Skills

A personal [Claude Code](https://code.claude.com) plugin marketplace with one
plugin, **anvil**: Saad's development workflow. A change goes brainstorm → spec →
stop → plan → stop → parallel build → verify → finish, with the gates, test
results and progress kept on disk. Anvil is self-contained: it doesn't need
Superpowers or any other plugin.

## What's new in 2.0

2.0 comes from an A/B test of 1.0 against Superpowers 7.0.2 and plain Claude: 63 runs on Opus 5.5. The results are in [docs/anvil-ab/](docs/anvil-ab/2026-11-18-ab-results.md) and the plan is in [docs/anvil-v2/](docs/anvil-v2/2026-11-19-v2-plan.md). All three were equally correct; 1.0 was 2.4× slower. 2.0 keeps the stops, the docs and the gates and cuts the waiting:

- **Small plans build inline.** For 3 tasks or fewer, the orchestrator builds them itself, and one reviewer checks the whole diff once. There are no per-task subagent rounds.
- **Fewer review rounds.** A fix that stays inside its findings is checked without a re-review. The whole-branch review runs only for 4+ tasks or a 300+-line diff.
- **Verify lands the work.** The last commit point is on the synced branch at hand-off, and `/anvil:finish` is optional: push, merge, PR, clean-up. New work parks a finished topic by itself.
- **"Approved, one fix: …" passes the stop.** Saad's dictated edits are applied after approving (or with `anvil approve --amended`), with no second round.
- **AFK keeps going.** It never asks Saad to run a command, and "keep going" fixes the cheap deferred items.
- **Smaller fixes:**
  - `anvil run` converts `/tmp/...` paths on Windows;
  - docs under `docs/` aren't held before approval;
  - doc and code edits never use shell heredocs;
  - implementers keep line endings;
  - unstated restrictions are listed as calls;
  - reports use plain words.

## What's inside `anvil`

| Skill | Use it for |
|---|---|
| **anvil** | The entry point. Sizes a request (trivial, direct or full), starts the topic and says which stage skill runs next. |
| **brainstorm** | Thinking a change through: looks things up first, asks batched questions with recommended answers, and writes the spec with numbered S-lines. Stop 1 is the spec approval. |
| **plan** | The lean plan: a task table with write sets, waves, a test strategy and commit points. Stop 2 is the plan approval. |
| **build** | Runs an approved plan, in parallel waves where the write sets allow it, with a review per task and a live `progress.md`. Picks up an interrupted build. |
| **verify** | The converge check against the spec, with evidence of behavior, reusing test results from an unchanged tree. |
| **finish** | Commit and push per the project's rule, scaffold cleanup, tickets, branch safety. Runs only when invoked (`/anvil:finish`). |
| **debug** | Systematic debugging when a cause isn't obvious, at any stage. |
| **afk** | Unattended mode: questions become logged decisions, stops can be pre-approved in Saad's own words, and a Stop hook keeps the run going until no task is open. |
| **ui-mockup** | Mock-first UI before production UI code. Due for a rewrite in a later phase. |
| **ux-audit** | UX review of a built UI. Due for a rewrite in a later phase. |
| **cross-model** | An independent second model for review or research, with its findings triaged. |
| **ticket-update** | Keeps the tracker (Linear, Jira, GitHub, GitLab, Azure DevOps) current at real stops. |

Each stage skill can be called directly, for example `/anvil:plan`.

## Install

```bash
claude plugin marketplace add MrErrorSan/mrerror-claude-skills
claude plugin install anvil@mrerror-claude-skills
```

Then run `/reload-plugins` in an open session, or start a new one. No other
marketplace or plugin is needed.

### Turn on auto-update

Third-party marketplaces don't auto-update by default. On each machine, run
`/plugin`, open the **Marketplaces** tab, select `mrerror-claude-skills` and
choose **Enable auto-update**. Or set it in `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "mrerror-claude-skills": {
      "source": { "source": "github", "repo": "MrErrorSan/mrerror-claude-skills" },
      "autoUpdate": true
    }
  }
}
```

Sources: [Install and manage plugins, "Keep plugins updated"](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated)
and [Plugin loading reference, "When auto-update runs"](https://code.claude.com/docs/en/plugins/loading#when-auto-update-runs),
checked 2026-11-18. To update by hand: `claude plugin update anvil@mrerror-claude-skills`.

### Upgrading from 0.2.0

Anvil 0.2.0 declared `superpowers@superpowers-marketplace`,
`claude-session-driver` and `episodic-memory` as dependencies, so Claude Code
installed them automatically. 1.0 drops them, but updating doesn't uninstall
them: they stay installed until you run `claude plugin prune`, which removes
auto-installed dependencies that no installed plugin needs anymore (add
`--scope project` or `--scope local` for those scopes; the default is `user`).
Run `claude plugin prune --dry-run` first to see the list. Skip the prune if
you want to keep Superpowers for the "both installed" setup below.
Source: [plugins reference, "plugin prune"](https://code.claude.com/docs/en/plugins/cli-reference#plugin-prune),
checked 2026-11-18.

### Releases

**Bump `version` in `plugins/anvil/.claude-plugin/plugin.json` on every
release.** Claude Code compares that string to decide whether there is an
update, so a release with an unchanged `version` never reaches other machines.

## Coexistence with Superpowers

| Setup | How |
|---|---|
| **Anvil only** (the target) | Turn Superpowers off with `enabledPlugins`, per project (`.claude/settings.json`) or for the user (`~/.claude/settings.json`). Example below. |
| **Both installed** (while building trust) | One line in the global `~/.claude/CLAUDE.md` saying Anvil's workflow replaces Superpowers' brainstorming, planning, building, review and finishing skills. Anvil's startup facts say the same, and the skill names are distinct. This works through wording only, so it is measured with evals. |
| **Superpowers only** (escape hatch) | `/plugin disable anvil` |

```json
{
  "enabledPlugins": {
    "superpowers@claude-plugins-official": false
  }
}
```

Use the plugin id that `claude plugin list` shows on your machine.

## The CLI

`plugins/anvil/bin/anvil` is one small Python CLI (Python ≥ 3.10, standard
library only). It does what the model shouldn't do in its head: S-line
parsing, gates, the parallel-safe check, test-result reuse and stale detection.
Files in a plugin's `bin/` are on the Bash tool's PATH while the plugin is
enabled, so skills call it as a bare `anvil <subcommand>`. `bin/anvil.cmd` is
the wrapper for cmd.exe and PowerShell. Both look for Python as `python`, then
`py -3`, then `python3`. The hooks in `plugins/anvil/hooks/` are thin bash
scripts that call the CLI, behind a `run-hook.cmd` wrapper for Windows.

claude.ai and Cowork don't install a plugin that has a top-level `bin/`
directory, so Anvil is for Claude Code only
([plugins reference, "Standard layout"](https://code.claude.com/docs/en/plugins-reference#standard-layout)).

## Tests

```bash
python -I -m unittest discover -s tests -t .
```

`tests/anvil_cli/` covers the CLI and the hooks, and lints every skill
(`test_skills.py`: frontmatter, size, wording, CLI subcommands, links and
source lines).

## Layout

```
.claude-plugin/marketplace.json     marketplace manifest
plugins/anvil/
  .claude-plugin/plugin.json        plugin manifest; bump version every release
  bin/anvil, bin/anvil.cmd          the CLI wrappers
  bin/anvil_cli/                    the CLI (Python, standard library)
  hooks/                            hooks.json, run-hook.cmd and the bash hooks
  references/                       shared formats, test policy, git flow, simplicity
  skills/<name>/                    SKILL.md, plus references/ and prompts/ where needed
  evals/                            plugin eval cases (claude plugin eval)
  NOTICE                            Superpowers MIT notice
upstream/superpowers/               upstream watch and provenance
tests/anvil_cli/                    unittest suite
docs/                               designs, plans and research
```

## Credits

The stage skills, the review prompts and the Windows hook wrapper are adapted
from [Superpowers](https://github.com/obra/superpowers) 7.0.2 by Jesse Vincent
(obra), under the MIT license. Each adapted Markdown file names its source in an
`<!-- adapted from superpowers@7.0.2: ... -->` line; scripts and the hook
wrapper carry it as a comment or are listed in
`upstream/superpowers/provenance.md`. The license notice is in
[`plugins/anvil/NOTICE`](plugins/anvil/NOTICE). Superpowers' logo and visual
companion are not included.

MIT ([LICENSE](LICENSE)). Personal tooling; use at your own discretion.
