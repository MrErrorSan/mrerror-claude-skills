# Where the time went: suite `v21`

Seconds of the main session's active time (Saad's thinking time excluded), by what was in flight.

| Run | Agent s | model | await-subagents | agent:foreground | bash:tests | bash:anvil-cli | bash:git | bash:other | read | edit | skill-load | Subagents (n / total s / parallelism) | Top phases |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo-A-r1 | 30 | 25 | 0 | 0 | 2 | 0 | 0 | 3 | 0 | 0 | 0 | 0 / 0 / None | anvil 25, router/none 7 |
| c1-typo-A-r2 | 31 | 22 | 0 | 0 | 4 | 0 | 5 | 0 | 0 | 1 | 0 | 0 / 0 / None | anvil 26, router/none 7 |
| c1-typo-A-r3 | 29 | 23 | 0 | 0 | 2 | 0 | 5 | 0 | 0 | 1 | 0 | 0 / 0 / None | anvil 24, router/none 6 |
| c2-top-n-A-r1 | 299 | 242 | 0 | 17 | 9 | 19 | 2 | 2 | 0 | 8 | 0 | 1 / 17 / 1.0 | build 113, brainstorm 111, verify 55, anvil 16 |
| c2-top-n-A-r2 | 293 | 222 | 0 | 17 | 14 | 22 | 2 | 4 | 0 | 14 | 1 | 1 / 17 / 1.0 | build 119, brainstorm 98, verify 52, anvil 19 |
| c2-top-n-A-r3 | 254 | 202 | 0 | 15 | 12 | 21 | 3 | 1 | 0 | 9 | 0 | 1 / 15 / 1.0 | brainstorm 110, build 83, verify 51, anvil 15 |
| c3-ledger-three-A-r1 | 409 | 308 | 0 | 24 | 47 | 19 | 2 | 5 | 0 | 10 | 0 | 1 / 24 / 1.0 | build 235, brainstorm 98, verify 47, anvil 28 |
| c3-ledger-three-A-r2 | 403 | 297 | 0 | 21 | 49 | 19 | 3 | 1 | 0 | 14 | 0 | 1 / 21 / 1.0 | build 180, brainstorm 126, verify 75, anvil 17 |
| c3-ledger-three-A-r3 | 319 | 234 | 0 | 16 | 29 | 20 | 2 | 1 | 0 | 16 | 0 | 1 / 16 / 1.0 | build 138, brainstorm 102, verify 57, anvil 18 |
| c4-refund-bug-A-r1 | 47 | 39 | 0 | 0 | 3 | 4 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 40, router/none 8 |
| c4-refund-bug-A-r2 | 38 | 30 | 0 | 0 | 3 | 5 | 0 | 0 | 0 | 1 | 0 | 0 / 0 / None | anvil 33, router/none 6 |
| c4-refund-bug-A-r3 | 42 | 32 | 0 | 0 | 4 | 5 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 38, router/none 6 |
| c5-notes-tags-A-r1 | 1772 | 666 | 0 | 116 | 18 | 949 | 4 | 4 | 0 | 19 | 0 | 2 / 116 / 1.0 | build 1063, brainstorm 296, verify 233, plan 166 |
| c5-notes-tags-A-r2 | 783 | 583 | 0 | 75 | 35 | 59 | 3 | 4 | 0 | 24 | 0 | 2 / 75 / 1.0 | build 281, brainstorm 198, plan 178, verify 108 |
| c5-notes-tags-A-r3 | 685 | 541 | 0 | 45 | 29 | 44 | 0 | 7 | 0 | 21 | 0 | 1 / 45 / 1.0 | plan 267, build 217, brainstorm 101, verify 81 |
| c6-csv-change-A-r1 | 1314 | 1208 | 0 | 33 | 25 | 26 | 2 | 2 | 0 | 19 | 0 | 2 / 32 / 1.0 | verify 1067, build 131, brainstorm 84, anvil 27 |
| c6-csv-change-A-r2 | 471 | 360 | 0 | 36 | 22 | 35 | 0 | 5 | 0 | 12 | 0 | 2 / 36 / 1.0 | verify 270, build 112, brainstorm 62, anvil 20 |
| c6-csv-change-A-r3 | 485 | 368 | 0 | 34 | 30 | 34 | 2 | 1 | 0 | 15 | 0 | 2 / 34 / 1.0 | verify 264, build 126, brainstorm 75, anvil 16 |
| c7-afk-import-A-r1 | 1161 | 268 | 0 | 32 | 12 | 836 | 1 | 4 | 0 | 9 | 0 | 1 / 32 / 1.0 | verify 905, build 145, brainstorm 83, anvil 19 |
| c7-afk-import-A-r2 | 346 | 271 | 0 | 26 | 11 | 20 | 2 | 4 | 0 | 12 | 0 | 1 / 26 / 1.0 | build 137, brainstorm 89, verify 82, afk 22 |
| c7-afk-import-A-r3 | 324 | 254 | 0 | 26 | 8 | 24 | 0 | 3 | 0 | 9 | 0 | 1 / 26 / 1.0 | build 150, brainstorm 78, verify 65, anvil 21 |
