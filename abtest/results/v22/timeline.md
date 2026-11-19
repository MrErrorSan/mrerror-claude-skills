# Where the time went: suite `v22`

Seconds of the main session's active time (Saad's thinking time excluded), by what was in flight.

| Run | Agent s | model | await-subagents | agent:foreground | bash:tests | bash:anvil-cli | bash:git | bash:other | read | edit | skill-load | Subagents (n / total s / parallelism) | Top phases |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo-A-r1 | 24 | 16 | 0 | 0 | 0 | 0 | 1 | 8 | 0 | 0 | 0 | 0 / 0 / None | router/none 25 |
| c1-typo-A-r2 | 14 | 12 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 16 |
| c1-typo-A-r3 | 26 | 21 | 0 | 0 | 0 | 0 | 2 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 27 |
| c2-top-n-A-r1 | 74 | 64 | 0 | 0 | 7 | 0 | 7 | 1 | 0 | 2 | 0 | 0 / 0 / None | anvil 74, router/none 6 |
| c2-top-n-A-r2 | 76 | 63 | 0 | 0 | 7 | 0 | 4 | 0 | 0 | 2 | 0 | 0 / 0 / None | anvil 70, router/none 6 |
| c2-top-n-A-r3 | 74 | 61 | 0 | 0 | 6 | 0 | 5 | 0 | 0 | 2 | 0 | 0 / 0 / None | anvil 68, router/none 7 |
| c3-ledger-three-A-r1 | 130 | 82 | 0 | 0 | 39 | 0 | 7 | 1 | 0 | 2 | 0 | 0 / 0 / None | anvil 126, router/none 5 |
| c3-ledger-three-A-r2 | 101 | 79 | 0 | 0 | 18 | 0 | 4 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 96, router/none 6 |
| c3-ledger-three-A-r3 | 99 | 73 | 0 | 0 | 19 | 0 | 5 | 1 | 0 | 2 | 0 | 0 / 0 / None | anvil 94, router/none 5 |
| c4-refund-bug-A-r1 | 35 | 28 | 0 | 0 | 2 | 0 | 4 | 0 | 0 | 1 | 0 | 0 / 0 / None | anvil 30, router/none 6 |
| c4-refund-bug-A-r2 | 40 | 35 | 0 | 0 | 2 | 0 | 4 | 0 | 0 | 1 | 0 | 0 / 0 / None | anvil 35, router/none 7 |
| c4-refund-bug-A-r3 | 40 | 34 | 0 | 0 | 3 | 0 | 4 | 0 | 0 | 1 | 0 | 0 / 0 / None | anvil 35, router/none 7 |
| c5-notes-tags-A-r1 | 599 | 471 | 0 | 42 | 34 | 28 | 1 | 4 | 0 | 24 | 0 | 1 / 42 / 1.0 | build 339, brainstorm 172, verify 71, anvil 17 |
| c5-notes-tags-A-r2 | 761 | 610 | 1 | 34 | 44 | 22 | 0 | 23 | 0 | 35 | 0 | 1 / 136 / 1.0 | build 430, brainstorm 194, verify 116, anvil 22 |
| c5-notes-tags-A-r3 | 619 | 483 | 7 | 35 | 34 | 21 | 1 | 5 | 0 | 34 | 0 | 1 / 35 / 1.0 | build 333, brainstorm 174, verify 92, anvil 15 |
| c6-csv-change-A-r1 | 109 | 94 | 0 | 0 | 8 | 0 | 4 | 1 | 0 | 2 | 0 | 0 / 0 / None | anvil 105, router/none 5 |
| c6-csv-change-A-r2 | 118 | 105 | 0 | 0 | 7 | 0 | 4 | 0 | 0 | 2 | 0 | 0 / 0 / None | anvil 112, router/none 6 |
| c6-csv-change-A-r3 | 105 | 92 | 0 | 0 | 7 | 0 | 4 | 1 | 0 | 3 | 0 | 0 / 0 / None | anvil 101, router/none 6 |
| c7-afk-import-A-r1 | 129 | 119 | 0 | 0 | 2 | 4 | 1 | 4 | 0 | 1 | 0 | 0 / 0 / None | afk 122, router/none 9 |
| c7-afk-import-A-r2 | 129 | 120 | 0 | 0 | 1 | 4 | 1 | 5 | 0 | 0 | 0 | 0 / 0 / None | afk 124, router/none 7 |
| c7-afk-import-A-r3 | 129 | 117 | 0 | 0 | 3 | 4 | 1 | 4 | 0 | 0 | 0 | 0 / 0 / None | afk 125, router/none 5 |
