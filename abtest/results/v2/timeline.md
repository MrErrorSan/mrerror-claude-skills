# Where the time went: suite `v2`

Seconds of the main session's active time (Saad's thinking time excluded), by what was in flight.

| Run | Agent s | model | await-subagents | agent:foreground | bash:tests | bash:anvil-cli | bash:git | bash:other | read | edit | skill-load | Subagents (n / total s / parallelism) | Top phases |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo-A-r1 | 28 | 22 | 0 | 0 | 2 | 0 | 5 | 0 | 0 | 0 | 0 | 0 / 0 / None | anvil 23, router/none 6 |
| c1-typo-A-r2 | 31 | 26 | 0 | 0 | 2 | 0 | 4 | 1 | 0 | 0 | 0 | 0 / 0 / None | anvil 26, router/none 7 |
| c1-typo-A-r3 | 26 | 22 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / None | anvil 21, router/none 7 |
| c2-top-n-A-r1 | 370 | 293 | 0 | 19 | 12 | 38 | 1 | 3 | 0 | 6 | 0 | 1 / 19 / 1.0 | build 179, plan 100, verify 53, brainstorm 18 |
| c2-top-n-A-r2 | 333 | 272 | 0 | 14 | 8 | 25 | 1 | 1 | 0 | 12 | 0 | 1 / 14 / 1.0 | plan 140, build 101, verify 50, brainstorm 19 |
| c2-top-n-A-r3 | 342 | 288 | 0 | 16 | 6 | 32 | 0 | 3 | 0 | 10 | 0 | 1 / 16 / 1.0 | build 158, plan 102, verify 53, brainstorm 20 |
| c3-ledger-three-A-r1 | 415 | 323 | 0 | 23 | 23 | 26 | 1 | 6 | 0 | 14 | 0 | 1 / 23 / 1.0 | build 155, plan 121, verify 81, brainstorm 33 |
| c3-ledger-three-A-r2 | 555 | 433 | 0 | 22 | 47 | 35 | 0 | 4 | 0 | 23 | 0 | 2 / 32 / 1.0 | verify 251, build 159, plan 99, brainstorm 30 |
| c3-ledger-three-A-r3 | 369 | 282 | 0 | 19 | 29 | 26 | 2 | 1 | 0 | 12 | 0 | 1 / 19 / 1.0 | build 165, verify 91, plan 69, brainstorm 25 |
| c4-refund-bug-A-r1 | 40 | 33 | 0 | 0 | 2 | 5 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 36, router/none 6 |
| c4-refund-bug-A-r2 | 38 | 32 | 0 | 0 | 2 | 4 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 34, router/none 5 |
| c4-refund-bug-A-r3 | 38 | 31 | 0 | 0 | 2 | 4 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 34, router/none 5 |
| c5-notes-tags-A-r1 | 1105 | 743 | 0 | 108 | 44 | 155 | 1 | 49 | 0 | 16 | 0 | 2 / 108 / 1.0 | build 325, brainstorm 276, verify 193, cross-model 156 |
| c5-notes-tags-A-r2 | 1046 | 700 | 0 | 122 | 43 | 133 | 0 | 39 | 0 | 13 | 0 | 2 / 122 / 1.0 | build 310, brainstorm 304, verify 162, plan 135 |
| c5-notes-tags-A-r3 | 799 | 606 | 0 | 107 | 15 | 45 | 2 | 8 | 0 | 24 | 0 | 2 / 107 / 1.0 | brainstorm 286, build 250, plan 155, verify 95 |
| c6-csv-change-A-r1 | 498 | 396 | 0 | 36 | 20 | 29 | 3 | 3 | 0 | 17 | 0 | 2 / 36 / 1.0 | verify 256, build 105, plan 91, brainstorm 30 |
| c6-csv-change-A-r2 | 532 | 418 | 0 | 40 | 26 | 35 | 0 | 2 | 0 | 13 | 0 | 2 / 40 / 1.0 | verify 288, build 130, plan 69, brainstorm 26 |
| c6-csv-change-A-r3 | 509 | 382 | 0 | 38 | 30 | 35 | 0 | 5 | 0 | 19 | 0 | 2 / 37 / 1.0 | verify 277, build 122, plan 60, brainstorm 26 |
| c7-afk-import-A-r1 | 571 | 456 | 0 | 45 | 26 | 25 | 3 | 2 | 0 | 22 | 0 | 2 / 45 / 1.0 | verify 302, build 153, plan 51, brainstorm 43 |
| c7-afk-import-A-r2 | 650 | 513 | 0 | 98 | 19 | 27 | 3 | 5 | 0 | 14 | 0 | 2 / 98 / 1.0 | verify 223, build 181, brainstorm 169, plan 74 |
| c7-afk-import-A-r3 | 792 | 629 | 0 | 52 | 49 | 34 | 5 | 9 | 1 | 23 | 0 | 2 / 51 / 1.0 | brainstorm 762, anvil 29, router/none 6, afk 4 |
