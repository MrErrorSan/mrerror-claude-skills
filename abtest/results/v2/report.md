# A/B results: suite `v2`

Generated 2026-11-19 10:28. Arms: A = Anvil, S = Superpowers 7.0.2, V = no plugin. Agent model claude-opus-5-5 at effort high.

## Per case (median over replicates)

| Case | Arm | Hidden pass % | Agent time s | Cost $ | User turns | Suite runs | Subagents | Code lines | Test lines | Docs | EOL rewrites | Judge (1-5) | Judge rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo | A | 100 | 28.5 | 0.2086 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | None | None |
| c2-top-n | A | 100 | 342.3 | 1.8493 | 2 | 4 | 1 | 16 | 33 | 3 | 0 | None | None |
| c3-ledger-three | A | 92 | 414.8 | 2.0147 | 1 | 6 | 1 | 44 | 109 | 3 | 0 | None | None |
| c4-refund-bug | A | 100 | 38.4 | 0.2581 | 0 | 1 | 0 | 6 | 5 | 0 | 0 | None | None |
| c5-notes-tags | A | 100 | 1045.5 | 4.5751 | 3 | 15 | 2 | 123 | 170 | 4 | 0 | None | None |
| c6-csv-change | A | 100 | 508.6 | 2.5615 | 2 | 10 | 2 | 18 | 69 | 3 | 0 | None | None |
| c7-afk-import | A | 100 | 650.2 | 3.3519 | 6 | 11 | 2 | 80 | 187 | 3 | 0 | None | None |

## Totals per arm

| Arm | Runs | Hidden passed | Perfect runs | Agent min | Cost $ | User turns | Suite runs | EOL rewrites | Judge mean | First places |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 21 | 193/195 | 19 | 151 | 44.5 | 38 | 138 | 1 | None | 0 |

## Every run

| Run | Status | End | Hidden | core | edge | brief | regr | Agent s | Wall s | $ | User turns | Suite runs | Own tests | Trailers | Result in | Skills |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo A r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 28.5 | 36.3 | 0.2108 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r1 | anvil:anvil |
| c1-typo A r2 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 31.4 | 37.8 | 0.2013 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r2 | anvil:anvil |
| c1-typo A r3 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 26.5 | 32.8 | 0.2086 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r3 | anvil:anvil |
| c2-top-n A r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 370.4 | 397.8 | 1.8493 | 3 | 5 | 7 ok | 0 | worktree:c2-top-n-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c2-top-n A r2 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 332.8 | 349.2 | 1.6479 | 1 | 4 | 6 ok | 0 | worktree:c2-top-n-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c2-top-n A r3 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 342.3 | 361.3 | 1.9367 | 2 | 3 | 7 ok | 0 | worktree:c2-top-n-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c3-ledger-three A r1 | complete | done | 11/12 | 4/4 | 3/3 | 1/2 | 3/3 | 414.8 | 430.5 | 2.0147 | 1 | 4 | 8 ok | 0 | worktree:c3-ledger-three-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c3-ledger-three A r2 | complete | done | 12/12 | 4/4 | 3/3 | 2/2 | 3/3 | 554.8 | 575.5 | 2.8312 | 2 | 8 | 10 ok | 0 | worktree:c3-ledger-three-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c3-ledger-three A r3 | complete | done | 11/12 | 4/4 | 3/3 | 1/2 | 3/3 | 368.8 | 384.1 | 1.9081 | 1 | 6 | 11 ok | 0 | worktree:c3-ledger-three-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c4-refund-bug A r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 39.7 | 47.6 | 0.2622 | 0 | 1 | 5 ok | 0 | worktree:c4-refund-bug-A-r1 | anvil:anvil |
| c4-refund-bug A r2 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 38.4 | 44.7 | 0.2581 | 0 | 1 | 5 ok | 0 | worktree:c4-refund-bug-A-r2 | anvil:anvil |
| c4-refund-bug A r3 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 37.7 | 44.9 | 0.2543 | 0 | 1 | 5 ok | 0 | worktree:c4-refund-bug-A-r3 | anvil:anvil |
| c5-notes-tags A r1 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 1104.7 | 1128.6 | 4.6416 | 3 | 16 | 10 ok | 0 | worktree:c5-notes-tags-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:cross-model, anvil:plan, anvil |
| c5-notes-tags A r2 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 1045.5 | 1071.6 | 4.5751 | 3 | 15 | 13 ok | 0 | worktree:c5-notes-tags-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:cross-model, anvil:plan, anvil |
| c5-notes-tags A r3 | complete | done | 12/12 | 4/4 | 2/2 | 3/3 | 3/3 | 799.0 | 822.9 | 3.7953 | 3 | 5 | 13 ok | 0 | worktree:c5-notes-tags-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c6-csv-change A r1 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 497.7 | 517.8 | 2.5398 | 2 | 7 | 5 ok | 0 | worktree:c6-csv-change-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c6-csv-change A r2 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 532.5 | 551.3 | 2.7536 | 2 | 10 | 6 ok | 0 | worktree:c6-csv-change-A-r2 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c6-csv-change A r3 | complete | done | 6/6 | 3/3 | 1/1 | - | 2/2 | 508.6 | 529.5 | 2.5615 | 2 | 12 | 5 ok | 0 | worktree:c6-csv-change-A-r3 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c7-afk-import A r1 | complete | done | 10/10 | 4/4 | 3/3 | - | 3/3 | 571.1 | 583.9 | 2.8389 | 1 | 11 | 16 ok | 0 | worktree:c7-afk-import-A-r1 | anvil:afk, anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c7-afk-import A r2 | complete | max_user_turns | 10/10 | 4/4 | 3/3 | - | 3/3 | 650.2 | 688.0 | 3.3519 | 6 | 9 | 11 ok | 0 | worktree:c7-afk-import-A-r2 | anvil:afk, anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c7-afk-import A r3 | complete | max_user_turns | 10/10 | 4/4 | 3/3 | - | 3/3 | 792.3 | 839.7 | 3.862 | 6 | 17 | 18 ok | 0 | worktree:c7-afk-import-A-r3 | anvil:afk, anvil:anvil, anvil:brainstorm |

## Hidden-test failures

- **c3-ledger-three A r1**: test_brief_export_both_formats_at_once
- **c3-ledger-three A r3**: test_brief_export_both_formats_at_once
