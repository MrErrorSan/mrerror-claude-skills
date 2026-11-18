# Where the time went: suite `full`

Seconds of the main session's active time (Saad's thinking time excluded), by what was in flight.

| Run | Agent s | model | await-subagents | agent:foreground | bash:tests | bash:anvil-cli | bash:git | bash:other | read | edit | skill-load | Subagents (n / total s / parallelism) | Top phases |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo-A-r1 | 27 | 21 | 0 | 0 | 2 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | anvil 21, router/none 7 |
| c1-typo-A-r2 | 21 | 16 | 0 | 0 | 2 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | anvil 16, router/none 6 |
| c1-typo-A-r3 | 30 | 24 | 0 | 0 | 2 | 0 | 0 | 5 | 0 | 0 | 0 | 0 / 0 / None | anvil 24, router/none 7 |
| c1-typo-S-r1 | 14 | 11 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 15 |
| c1-typo-S-r2 | 18 | 14 | 0 | 0 | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 18 |
| c1-typo-S-r3 | 20 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 22 |
| c1-typo-V-r1 | 25 | 20 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 25 |
| c1-typo-V-r2 | 14 | 10 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 14 |
| c1-typo-V-r3 | 27 | 22 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 27 |
| c2-top-n-A-r1 | 327 | 233 | 0 | 72 | 10 | 25 | 0 | 0 | 0 | 1 | 0 | 2 / 72 / 1.0 | build 140, plan 107, verify 50, brainstorm 23 |
| c2-top-n-A-r2 | 328 | 238 | 0 | 66 | 12 | 26 | 0 | 0 | 0 | 1 | 0 | 2 / 66 / 1.0 | build 141, plan 110, verify 53, brainstorm 18 |
| c2-top-n-A-r3 | 185 | 242 | 13 | 64 | 11 | 21 | 0 | 1 | 0 | 0 | 0 | 3 / 148 / 1.19 | build 198, plan 75, verify 33, brainstorm 21 |
| c2-top-n-S-r1 | 113 | 105 | 0 | 0 | 12 | 0 | 4 | 1 | 0 | 0 | 0 | 0 / 0 / None | test-driven-development 116, router/none 6 |
| c2-top-n-S-r2 | 97 | 86 | 0 | 0 | 10 | 0 | 4 | 4 | 0 | 0 | 0 | 0 / 0 / None | router/none 104 |
| c2-top-n-S-r3 | 114 | 116 | 0 | 0 | 11 | 0 | 8 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 135 |
| c2-top-n-V-r1 | 87 | 84 | 0 | 0 | 4 | 0 | 4 | 8 | 0 | 0 | 0 | 0 / 0 / None | router/none 100 |
| c2-top-n-V-r2 | 86 | 82 | 0 | 0 | 12 | 0 | 4 | 2 | 0 | 0 | 0 | 0 / 0 / None | router/none 99 |
| c2-top-n-V-r3 | 65 | 64 | 0 | 0 | 3 | 0 | 8 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 75 |
| c3-ledger-three-A-r1 | 734 | 454 | 10 | 355 | 43 | 27 | 1 | 6 | 0 | 4 | 0 | 7 / 810 / 1.44 | build 642, plan 118, verify 88, brainstorm 25 |
| c3-ledger-three-A-r2 | 443 | 390 | 24 | 276 | 21 | 28 | 1 | 5 | 0 | 2 | 0 | 6 / 367 / 1.06 | build 490, plan 143, verify 65, brainstorm 29 |
| c3-ledger-three-A-r3 | 330 | 585 | 49 | 226 | 58 | 26 | 0 | 6 | 0 | 12 | 0 | 8 / 650 / 1.27 | plan 807, verify 107, brainstorm 30, anvil 14 |
| c3-ledger-three-S-r1 | 80 | 59 | 0 | 0 | 18 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 81 |
| c3-ledger-three-S-r2 | 88 | 67 | 0 | 0 | 17 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | test-driven-development 78, router/none 11 |
| c3-ledger-three-S-r3 | 96 | 59 | 0 | 0 | 33 | 0 | 3 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 96 |
| c3-ledger-three-V-r1 | 121 | 71 | 0 | 0 | 52 | 0 | 3 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 126 |
| c3-ledger-three-V-r2 | 69 | 48 | 0 | 0 | 17 | 0 | 3 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 69 |
| c3-ledger-three-V-r3 | 108 | 71 | 0 | 0 | 33 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 108 |
| c4-refund-bug-A-r1 | 44 | 36 | 0 | 0 | 4 | 4 | 1 | 1 | 0 | 0 | 0 | 0 / 0 / None | anvil 40, router/none 6 |
| c4-refund-bug-A-r2 | 37 | 31 | 0 | 0 | 2 | 4 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 34, router/none 5 |
| c4-refund-bug-A-r3 | 44 | 38 | 0 | 0 | 2 | 4 | 0 | 1 | 0 | 1 | 0 | 0 / 0 / None | anvil 37, router/none 8 |
| c4-refund-bug-S-r1 | 36 | 32 | 0 | 0 | 2 | 0 | 3 | 0 | 0 | 0 | 0 | 0 / 0 / None | systematic-debugging 31, router/none 6 |
| c4-refund-bug-S-r2 | 32 | 26 | 0 | 0 | 2 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | systematic-debugging 29, router/none 3 |
| c4-refund-bug-S-r3 | 41 | 35 | 0 | 0 | 2 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | systematic-debugging 35, router/none 6 |
| c4-refund-bug-V-r1 | 32 | 28 | 0 | 0 | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 32 |
| c4-refund-bug-V-r2 | 25 | 20 | 0 | 0 | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 25 |
| c4-refund-bug-V-r3 | 32 | 27 | 0 | 0 | 1 | 0 | 4 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 32 |
| c5-notes-tags-A-r1 | 1353 | 692 | 0 | 549 | 19 | 47 | 1 | 64 | 0 | 2 | 0 | 8 / 549 / 1.0 | build 745, brainstorm 278, plan 174, cross-model 102 |
| c5-notes-tags-A-r2 | 1263 | 785 | 12 | 422 | 14 | 48 | 1 | 205 | 0 | 3 | 0 | 9 / 726 / 1.07 | build 582, brainstorm 233, cross-model 216, debug 187 |
| c5-notes-tags-A-r3 | 735 | 987 | 92 | 668 | 24 | 57 | 3 | 72 | 0 | 3 | 0 | 12 / 2248 / 1.99 | build 1214, brainstorm 276, plan 148, cross-model 123 |
| c5-notes-tags-S-r1 | 1238 | 611 | 0 | 184 | 430 | 0 | 5 | 17 | 0 | 1 | 0 | 1 / 184 / 1.0 | test-driven-development 979, brainstorming 112, writing-plans 102, finishing-a-development-branch 25 |
| c5-notes-tags-S-r2 | 595 | 442 | 0 | 125 | 39 | 0 | 4 | 10 | 0 | 1 | 0 | 2 / 243 / 1.0 | test-driven-development 386, writing-plans 124, brainstorming 100, executing-plans 6 |
| c5-notes-tags-S-r3 | 759 | 591 | 0 | 100 | 76 | 0 | 4 | 7 | 0 | 1 | 0 | 1 / 100 / 1.0 | test-driven-development 468, writing-plans 150, brainstorming 103, finishing-a-development-branch 28 |
| c5-notes-tags-V-r1 | 337 | 309 | 0 | 0 | 36 | 0 | 4 | 9 | 0 | 0 | 0 | 0 / 0 / None | router/none 357 |
| c5-notes-tags-V-r2 | 348 | 294 | 0 | 0 | 38 | 0 | 4 | 11 | 0 | 1 | 0 | 0 / 0 / None | router/none 353 |
| c5-notes-tags-V-r3 | 235 | 224 | 0 | 0 | 5 | 0 | 3 | 8 | 0 | 0 | 0 | 0 / 0 / None | router/none 241 |
| c6-csv-change-A-r1 | 644 | 489 | 13 | 379 | 20 | 31 | 5 | 6 | 0 | 0 | 0 | 8 / 456 / 1.05 | build 449, verify 354, plan 91, brainstorm 28 |
| c6-csv-change-A-r2 | 609 | 413 | 0 | 153 | 16 | 35 | 0 | 3 | 0 | 2 | 0 | 4 / 152 / 1.0 | verify 340, build 141, plan 88, brainstorm 29 |
| c6-csv-change-A-r3 | 602 | 418 | 0 | 147 | 16 | 28 | 5 | 0 | 0 | 2 | 0 | 4 / 146 / 1.0 | verify 348, build 120, plan 88, brainstorm 34 |
| c6-csv-change-S-r1 | 134 | 121 | 0 | 0 | 11 | 0 | 5 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 138 |
| c6-csv-change-S-r2 | 170 | 170 | 0 | 0 | 16 | 0 | 4 | 0 | 0 | 1 | 0 | 0 / 0 / None | router/none 190 |
| c6-csv-change-S-r3 | 110 | 99 | 0 | 0 | 7 | 0 | 3 | 0 | 0 | 0 | 0 | 0 / 0 / None | router/none 110 |
| c6-csv-change-V-r1 | 66 | 60 | 0 | 0 | 5 | 0 | 4 | 1 | 0 | 0 | 0 | 0 / 0 / None | router/none 70 |
| c6-csv-change-V-r2 | 165 | 150 | 0 | 0 | 12 | 0 | 4 | 2 | 0 | 0 | 0 | 0 / 0 / None | router/none 169 |
| c6-csv-change-V-r3 | 108 | 101 | 0 | 0 | 7 | 0 | 4 | 1 | 0 | 0 | 0 | 0 / 0 / None | router/none 114 |
| c7-afk-import-A-r1 | 1080 | 474 | 0 | 566 | 7 | 30 | 0 | 7 | 0 | 2 | 0 | 8 / 566 / 1.0 | build 733, brainstorm 138, verify 117, plan 70 |
| c7-afk-import-A-r2 | 941 | 530 | 0 | 377 | 9 | 35 | 5 | 6 | 0 | 2 | 0 | 6 / 377 / 1.0 | build 484, verify 226, brainstorm 147, plan 75 |
| c7-afk-import-A-r3 | 148 | 537 | 30 | 396 | 10 | 24 | 1 | 16 | 0 | 2 | 0 | 8 / 1049 / 1.59 | build 669, brainstorm 160, verify 96, plan 62 |
| c7-afk-import-S-r1 | 130 | 120 | 0 | 0 | 8 | 0 | 4 | 1 | 0 | 0 | 0 | 0 / 0 / None | router/none 134 |
| c7-afk-import-S-r2 | 154 | 143 | 0 | 0 | 3 | 0 | 4 | 5 | 0 | 0 | 0 | 0 / 0 / None | router/none 155 |
| c7-afk-import-S-r3 | 152 | 142 | 0 | 0 | 3 | 0 | 4 | 8 | 0 | 0 | 0 | 0 / 0 / None | router/none 157 |
| c7-afk-import-V-r1 | 210 | 200 | 0 | 0 | 3 | 0 | 4 | 6 | 0 | 0 | 0 | 0 / 0 / None | router/none 213 |
| c7-afk-import-V-r2 | 129 | 120 | 0 | 0 | 1 | 0 | 4 | 3 | 0 | 0 | 0 | 0 / 0 / None | router/none 129 |
| c7-afk-import-V-r3 | 100 | 93 | 0 | 0 | 1 | 0 | 4 | 2 | 0 | 0 | 0 | 0 / 0 / None | router/none 100 |
