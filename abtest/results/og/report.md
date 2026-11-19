# A/B results: suite `og`

Generated 2026-11-19 11:30. Arms: A = Anvil, S = Superpowers 7.0.2, V = no plugin. Agent model claude-opus-5-5 at effort high.

## Per case (median over replicates)

| Case | Arm | Hidden pass % | Agent time s | Cost $ | User turns | Suite runs | Subagents | Code lines | Test lines | Docs | EOL rewrites | Judge (1-5) | Judge rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo | O | 100 | 16.6 | 0.1725 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | None | None |
| c2-top-n | O | 100 | 77.3 | 0.431 | 1 | 2 | 0 | 14 | 37 | 1 | 0 | None | None |
| c3-ledger-three | O | 100 | 101.7 | 0.4959 | 0 | 3 | 0 | 54 | 93 | 2 | 1 | None | None |
| c4-refund-bug | O | 100 | 34.4 | 0.2353 | 0 | 2 | 0 | 6 | 7 | 0 | 0 | None | None |
| c5-notes-tags | O | 100 | 319.1 | 1.2973 | 3 | 5 | 0 | 125 | 140 | 3 | 0 | None | None |
| c6-csv-change | O | 100 | 108.2 | 0.552 | 1 | 3 | 0 | 29 | 44 | 1 | 0 | None | None |
| c7-afk-import | O | 100 | 154.0 | 0.6767 | 0 | 2 | 0 | 63 | 131 | 2 | 0 | None | None |

## Totals per arm

| Arm | Runs | Hidden passed | Perfect runs | Agent min | Cost $ | User turns | Suite runs | EOL rewrites | Judge mean | First places |
|---|---|---|---|---|---|---|---|---|---|---|
| O | 21 | 194/195 | 20 | 41 | 11.92 | 16 | 50 | 5 | None | 0 |

## Every run

| Run | Status | End | Hidden | core | edge | brief | regr | Agent s | Wall s | $ | User turns | Suite runs | Own tests | Trailers | Result in | Skills |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo O r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 27.7 | 35.6 | 0.1906 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-O-r1 |  |
| c1-typo O r2 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 16.6 | 24.9 | 0.1725 | 0 | 0 | 3 ok | 0 | worktree:c1-typo-O-r2 |  |
| c1-typo O r3 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 11.8 | 20.0 | 0.167 | 0 | 0 | 3 ok | 0 | worktree:c1-typo-O-r3 |  |
| c2-top-n O r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 77.3 | 94.0 | 0.4115 | 1 | 2 | 8 ok | 0 | worktree:c2-top-n-O-r1 | anvil:anvil |
| c2-top-n O r2 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 86.6 | 103.3 | 0.4683 | 1 | 3 | 7 ok | 0 | worktree:c2-top-n-O-r2 | anvil:anvil |
| c2-top-n O r3 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 69.9 | 86.2 | 0.431 | 1 | 2 | 7 ok | 0 | worktree:c2-top-n-O-r3 | anvil:anvil |
| c3-ledger-three O r1 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 97.0 | 104.1 | 0.4557 | 0 | 2 | 11 ok | 0 | worktree:c3-ledger-three-O-r1 | anvil:anvil |
| c3-ledger-three O r2 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 138.6 | 154.3 | 0.559 | 1 | 3 | 13 ok | 0 | worktree:c3-ledger-three-O-r2 | anvil:anvil |
| c3-ledger-three O r3 | complete | done | 11/12 | 4/4 | 3/3 | 1/2 | 3/3 | 101.7 | 110.2 | 0.4959 | 0 | 3 | 10 ok | 0 | worktree:c3-ledger-three-O-r3 | anvil:anvil |
| c4-refund-bug O r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 35.7 | 42.6 | 0.2353 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-O-r1 |  |
| c4-refund-bug O r2 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 34.4 | 41.7 | 0.2288 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-O-r2 |  |
| c4-refund-bug O r3 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 33.5 | 41.0 | 0.2942 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-O-r3 | anvil:anvil |
| c5-notes-tags O r1 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 319.1 | 368.5 | 1.2973 | 2 | 5 | 23 ok | 0 | worktree:c5-notes-tags-O-r1 | anvil:anvil |
| c5-notes-tags O r2 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 282.8 | 315.3 | 1.2045 | 3 | 2 | 14 ok | 0 | worktree:c5-notes-tags-O-r2 | anvil:anvil |
| c5-notes-tags O r3 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 332.1 | 360.0 | 1.476 | 3 | 5 | 18 ok | 0 | worktree:c5-notes-tags-O-r3 | anvil:anvil, superpowers:brainstorming, superpowers:writing-plans |
| c6-csv-change O r1 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 157.2 | 173.1 | 0.6184 | 1 | 3 | 7 ok | 0 | worktree:c6-csv-change-O-r1 | anvil:anvil |
| c6-csv-change O r2 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 108.2 | 130.8 | 0.552 | 2 | 4 | 5 ok | 0 | worktree:c6-csv-change-O-r2 | anvil:anvil |
| c6-csv-change O r3 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 76.6 | 88.2 | 0.4591 | 1 | 2 | 3 ok | 0 | worktree:c6-csv-change-O-r3 | anvil:anvil |
| c7-afk-import O r1 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 154.0 | 161.1 | 0.6767 | 0 | 2 | 10 ok | 0 | worktree:c7-afk-import-O-r1 | anvil:afk |
| c7-afk-import O r2 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 130.3 | 137.9 | 0.6411 | 0 | 2 | 11 ok | 0 | worktree:c7-afk-import-O-r2 | anvil:afk, anvil:anvil |
| c7-afk-import O r3 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 181.1 | 189.1 | 0.881 | 0 | 3 | 9 ok | 0 | worktree:c7-afk-import-O-r3 | anvil:afk, anvil:anvil |

## Hidden-test failures

- **c3-ledger-three O r3**: test_brief_export_both_formats_at_once
