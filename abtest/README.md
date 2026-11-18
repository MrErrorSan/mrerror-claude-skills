# abtest: Anvil vs Superpowers vs no plugin

The harness behind [docs/anvil-ab/2026-11-18-ab-test-design.md](../docs/anvil-ab/2026-11-18-ab-test-design.md).

```bash
python abtest/harness/ab.py selftest --suite x          # hidden tests vs reference solutions; free
python abtest/harness/ab.py run --suite pilot --cases c1-typo,c2-top-n,c4-refund-bug --arms A,S,V --runs 1
python abtest/harness/ab.py judge  --suite pilot         # blind Opus judge, one call per case x replicate
python abtest/harness/ab.py report --suite pilot         # abtest/results/pilot/report.md + summary.json
```

## Layout

- `cases/<id>/case.json`: the request, the simulated user's brief (must-haves and answers), caps, judge notes.
- `cases/<id>/files/`: the fixture repo the agent sees.
- `cases/<id>/hidden/`: acceptance tests, copied in only after the session. They are named `test_core_*` (stated in the request), `test_edge_*` (unstated common sense) and `test_brief_*` (only knowable by asking). The fixture's own tests also run as `regression`.
- `cases/<id>/reference/`: a reference solution, used only by `selftest`.
- `harness/ab.py`: the runner, grader, judge and report. Prompts are in `harness/prompts/`.
- `results/<suite>/runs/*.json`: one record per run (committed). Raw transcripts, repos and diffs stay in `%LOCALAPPDATA%/Temp/anvil-abtest/<suite>/` (set `ABTEST_RUN_ROOT` to move it).

## Notes

- **Isolation.** Each run uses `--setting-sources project`. That loads Saad's global `CLAUDE.md` and the fixture's `CLAUDE.md`, but no installed plugins and no loose `~/.claude/skills`. `--safe-mode` does not isolate: installed plugins still load. Run repos live outside this checkout, so this repo's `CLAUDE.md` doesn't leak in.
- **Cost accounting.** In stream-json, `total_cost_usd` and `modelUsage` are cumulative across `--resume` calls and include subagents. `usage` and `num_turns` are per call and cover the main thread only.
- **Overrides.** Set these environment variables to change the defaults:
  - `ABTEST_MODEL` (default `claude-opus-5-5`)
  - `ABTEST_EFFORT` (`high`)
  - `ABTEST_SIM_MODEL` (`claude-sonnet-5-5`)
  - `ABTEST_JUDGE_MODEL` (`claude-opus-5-5`)
  - `ABTEST_SP_DIR` (the Superpowers 7.0.2 cache)
