# A/B results: suite `v22`

Generated 2026-11-19 11:57. Arms: A = Anvil, S = Superpowers 7.0.2, V = no plugin. Agent model claude-opus-5-5 at effort high.

## Per case (median over replicates)

| Case | Arm | Hidden pass % | Agent time s | Cost $ | User turns | Suite runs | Subagents | Code lines | Test lines | Docs | EOL rewrites | Judge (1-5) | Judge rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo | A | 100 | 23.9 | 0.1658 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | None | None |
| c2-top-n | A | 100 | 73.8 | 0.3873 | 1 | 2 | 0 | 14 | 29 | 1 | 0 | None | None |
| c3-ledger-three | A | 100 | 101.2 | 0.4266 | 0 | 2 | 0 | 45 | 74 | 1 | 0 | None | None |
| c4-refund-bug | A | 100 | 40.2 | 0.2687 | 0 | 2 | 0 | 6 | 6 | 0 | 0 | None | None |
| c5-notes-tags | A | 100 | 618.8 | 2.9189 | 2 | 12 | 1 | 120 | 185 | 3 | 0 | None | None |
| c6-csv-change | A | 100 | 109.2 | 0.5166 | 1 | 3 | 0 | 23 | 34 | 1 | 0 | None | None |
| c7-afk-import | A | 100 | 129.0 | 0.5666 | 0 | 2 | 0 | 109 | 163 | 1 | 1 | None | None |

## Totals per arm

| Arm | Runs | Hidden passed | Perfect runs | Agent min | Cost $ | User turns | Suite runs | EOL rewrites | Judge mean | First places |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 21 | 194/195 | 20 | 57 | 16.18 | 13 | 68 | 4 | None | 0 |

## Every run

| Run | Status | End | Hidden | core | edge | brief | regr | Agent s | Wall s | $ | User turns | Suite runs | Own tests | Trailers | Result in | Skills |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo A r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 23.9 | 31.7 | 0.1658 | 0 | 0 | 3 ok | 0 | worktree:c1-typo-A-r1 |  |
| c1-typo A r2 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 14.4 | 20.9 | 0.1429 | 0 | 0 | 3 ok | 0 | worktree:c1-typo-A-r2 |  |
| c1-typo A r3 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 25.9 | 32.6 | 0.1777 | 0 | 0 | 3 ok | 0 | worktree:c1-typo-A-r3 |  |
| c2-top-n A r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 73.8 | 87.2 | 0.4021 | 1 | 2 | 7 ok | 0 | worktree:c2-top-n-A-r1 | anvil:anvil |
| c2-top-n A r2 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 75.6 | 89.3 | 0.3731 | 1 | 2 | 7 ok | 0 | worktree:c2-top-n-A-r2 | anvil:anvil |
| c2-top-n A r3 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 73.6 | 90.2 | 0.3873 | 1 | 2 | 7 ok | 0 | worktree:c2-top-n-A-r3 | anvil:anvil |
| c3-ledger-three A r1 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 130.5 | 146.2 | 0.5014 | 1 | 3 | 9 ok | 0 | worktree:c3-ledger-three-A-r1 | anvil:anvil |
| c3-ledger-three A r2 | complete | done | 11/12 | 4/4 | 3/3 | 1/2 | 3/3 | 101.2 | 107.9 | 0.4204 | 0 | 2 | 8 ok | 0 | worktree:c3-ledger-three-A-r2 | anvil:anvil |
| c3-ledger-three A r3 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 98.9 | 105.3 | 0.4266 | 0 | 2 | 8 ok | 0 | worktree:c3-ledger-three-A-r3 | anvil:anvil |
| c4-refund-bug A r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 35.1 | 41.7 | 0.2687 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-A-r1 | anvil:anvil |
| c4-refund-bug A r2 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 40.2 | 46.7 | 0.2615 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-A-r2 | anvil:anvil |
| c4-refund-bug A r3 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 40.5 | 47.6 | 0.2755 | 0 | 3 | 5 ok | 0 | worktree:c4-refund-bug-A-r3 | anvil:anvil |
| c5-notes-tags A r1 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 598.6 | 619.1 | 2.6304 | 2 | 9 | 20 ok | 0 | worktree:c5-notes-tags-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c5-notes-tags A r2 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 760.7 | 782.1 | 3.583 | 2 | 13 | 22 ok | 0 | worktree:c5-notes-tags-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c5-notes-tags A r3 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 618.8 | 640.4 | 2.9189 | 2 | 12 | 20 ok | 0 | worktree:c5-notes-tags-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c6-csv-change A r1 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 109.2 | 122.9 | 0.5237 | 1 | 3 | 3 ok | 0 | worktree:c6-csv-change-A-r1 | anvil:anvil |
| c6-csv-change A r2 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 117.5 | 130.6 | 0.5166 | 1 | 3 | 4 ok | 0 | worktree:c6-csv-change-A-r2 | anvil:anvil |
| c6-csv-change A r3 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 105.0 | 118.4 | 0.5017 | 1 | 3 | 3 ok | 0 | worktree:c6-csv-change-A-r3 | anvil:anvil |
| c7-afk-import A r1 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 129.0 | 136.0 | 0.5532 | 0 | 2 | 12 ok | 0 | worktree:c7-afk-import-A-r1 | anvil:afk |
| c7-afk-import A r2 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 129.4 | 136.4 | 0.5666 | 0 | 1 | 16 ok | 0 | worktree:c7-afk-import-A-r2 | anvil:afk |
| c7-afk-import A r3 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 128.7 | 135.1 | 0.5786 | 0 | 2 | 12 ok | 0 | worktree:c7-afk-import-A-r3 | anvil:afk |

## Hidden-test failures

- **c3-ledger-three A r2**: test_brief_export_both_formats_at_once
