# A/B results: suite `v21`

Generated 2026-11-19 11:31. Arms: A = Anvil, S = Superpowers 7.0.2, V = no plugin. Agent model claude-opus-5-5 at effort high.

## Per case (median over replicates)

| Case | Arm | Hidden pass % | Agent time s | Cost $ | User turns | Suite runs | Subagents | Code lines | Test lines | Docs | EOL rewrites | Judge (1-5) | Judge rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo | A | 100 | 30.2 | 0.2086 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | None | None |
| c2-top-n | A | 100 | 293.4 | 1.3993 | 1 | 4 | 1 | 17 | 36 | 3 | 0 | None | None |
| c3-ledger-three | A | 100 | 402.6 | 1.7855 | 1 | 5 | 1 | 35 | 122 | 3 | 0 | None | None |
| c4-refund-bug | A | 100 | 42.1 | 0.2705 | 0 | 2 | 0 | 6 | 5 | 0 | 0 | None | None |
| c5-notes-tags | A | 100 | 783.1 | 3.5015 | 3 | 7 | 2 | 116 | 150 | 4 | 0 | None | None |
| c6-csv-change | A | 100 | 484.8 | 2.3006 | 2 | 9 | 2 | 22 | 77 | 3 | 0 | None | None |
| c7-afk-import | A | 90 | 345.7 | 1.7057 | 0 | 3 | 1 | 61 | 102 | 3 | 0 | None | None |

## Totals per arm

| Arm | Runs | Hidden passed | Perfect runs | Agent min | Cost $ | User turns | Suite runs | EOL rewrites | Judge mean | First places |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 21 | 192/195 | 18 | 159 | 33.79 | 22 | 88 | 0 | None | 0 |

## Every run

| Run | Status | End | Hidden | core | edge | brief | regr | Agent s | Wall s | $ | User turns | Suite runs | Own tests | Trailers | Result in | Skills |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo A r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 30.2 | 37.3 | 0.2028 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r1 | anvil:anvil |
| c1-typo A r2 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 31.1 | 37.6 | 0.2086 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r2 | anvil:anvil |
| c1-typo A r3 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 29.1 | 35.5 | 0.2132 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r3 | anvil:anvil |
| c2-top-n A r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 299.3 | 316.2 | 1.4634 | 1 | 3 | 8 ok | 0 | worktree:c2-top-n-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c2-top-n A r2 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 293.4 | 308.4 | 1.3993 | 1 | 4 | 8 ok | 0 | worktree:c2-top-n-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c2-top-n A r3 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 253.5 | 271.0 | 1.3802 | 1 | 4 | 5 ok | 0 | worktree:c2-top-n-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c3-ledger-three A r1 | complete | done | 11/12 | 4/4 | 3/3 | 1/2 | 3/3 | 408.7 | 421.2 | 1.7855 | 1 | 6 | 16 ok | 0 | worktree:c3-ledger-three-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c3-ledger-three A r2 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 402.6 | 421.5 | 1.7967 | 1 | 5 | 14 ok | 0 | worktree:c3-ledger-three-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c3-ledger-three A r3 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 318.6 | 335.1 | 1.6045 | 1 | 4 | 12 ok | 0 | worktree:c3-ledger-three-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c4-refund-bug A r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 47.1 | 53.4 | 0.2705 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-A-r1 | anvil:anvil |
| c4-refund-bug A r2 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 37.7 | 46.6 | 0.2455 | 0 | 1 | 5 ok | 0 | worktree:c4-refund-bug-A-r2 | anvil:anvil |
| c4-refund-bug A r3 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 42.1 | 48.6 | 0.2768 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-A-r3 | anvil:anvil |
| c5-notes-tags A r1 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 1771.8 | 1797.3 | 4.3233 | 3 | 6 | 14 ok | 0 | worktree:c5-notes-tags-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c5-notes-tags A r2 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 783.1 | 812.2 | 3.5015 | 3 | 7 | 12 ok | 0 | worktree:c5-notes-tags-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c5-notes-tags A r3 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 685.3 | 724.7 | 3.1537 | 4 | 7 | 11 ok | 0 | worktree:c5-notes-tags-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c6-csv-change A r1 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 1314.1 | 1334.9 | 2.3006 | 2 | 9 | 9 ok | 0 | worktree:c6-csv-change-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c6-csv-change A r2 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 470.9 | 491.8 | 2.1347 | 2 | 6 | 6 ok | 0 | worktree:c6-csv-change-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c6-csv-change A r3 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 484.8 | 509.2 | 2.4399 | 2 | 9 | 6 ok | 0 | worktree:c6-csv-change-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c7-afk-import A r1 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 1161.2 | 1167.5 | 1.6685 | 0 | 4 | 6 ok | 0 | worktree:c7-afk-import-A-r1 | anvil:afk, anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c7-afk-import A r2 | complete | done | 9/10 | 4/4 | 2/3 | - | 3/3 | 345.7 | 354.7 | 1.7057 | 0 | 3 | 11 ok | 0 | worktree:c7-afk-import-A-r2 | anvil:afk, anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |
| c7-afk-import A r3 | complete | done | 9/10 | 4/4 | 2/3 | - | 3/3 | 323.8 | 331.8 | 1.7181 | 0 | 3 | 9 ok | 0 | worktree:c7-afk-import-A-r3 | anvil:afk, anvil:anvil, anvil:brainstorm, anvil:build, anvil:verify |

## Hidden-test failures

- **c3-ledger-three A r1**: test_brief_export_both_formats_at_once
- **c7-afk-import A r2**: test_edge_importing_twice_does_not_duplicate
- **c7-afk-import A r3**: test_edge_importing_twice_does_not_duplicate
