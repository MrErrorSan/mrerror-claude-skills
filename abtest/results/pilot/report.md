# A/B results: suite `pilot`

Generated 2026-11-18 21:24. Arms: A = Anvil, S = Superpowers 7.0.2, V = no plugin. Agent model claude-opus-5-5 at effort high.

## Per case (median over replicates)

| Case | Arm | Hidden pass % | Agent time s | Cost $ | User turns | Suite runs | Subagents | Code lines | Test lines | Docs | Judge (1-5) | Judge rank |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo | A | 100 | 27.9 | 0.1909 | 0 | 1 | 0 | 2 | 0 | 0 | 4 | 2 |
| c1-typo | S | 100 | 15.1 | 0.1331 | 0 | 0 | 0 | 2 | 0 | 0 | 3 | 3 |
| c1-typo | V | 100 | 20.5 | 0.1268 | 0 | 1 | 0 | 2 | 0 | 0 | 5 | 1 |
| c2-top-n | A | 100 | 235.9 | 2.1482 | 2 | 9 | 3 | 14 | 27 | 3 | 3 | 1 |
| c2-top-n | S | 100 | 94.7 | 0.3822 | 2 | 4 | 0 | 16 | 24 | 1 | 3 | 2 |
| c2-top-n | V | 100 | 97.7 | 0.4017 | 3 | 5 | 0 | 19 | 36 | 1 | 2 | 3 |
| c4-refund-bug | A | 100 | 39.2 | 0.2374 | 0 | 1 | 0 | 6 | 5 | 0 | 4 | 3 |
| c4-refund-bug | S | 100 | 38.1 | 0.2542 | 0 | 2 | 0 | 6 | 7 | 0 | 5 | 1 |
| c4-refund-bug | V | 100 | 32.7 | 0.1886 | 0 | 2 | 0 | 6 | 6 | 0 | 4 | 2 |

## Every run

| Run | Status | End | Hidden | core | edge | brief | regr | Agent s | Wall s | $ | User turns | Suite runs | Own tests | Trailers | Result in | Skills |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c1-typo A r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 27.9 | 33.8 | 0.1909 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-A-r1 | anvil:anvil |
| c1-typo S r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 15.1 | 19.2 | 0.1331 | 0 | 0 | 3 ok | 0 | worktree:c1-typo-S-r1 |  |
| c1-typo V r1 | complete | done | 5/5 | 2/2 | - | - | 3/3 | 20.5 | 25.3 | 0.1268 | 0 | 1 | 3 ok | 0 | worktree:c1-typo-V-r1 |  |
| c2-top-n A r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 235.9 | 459.9 | 2.1482 | 2 | 9 | 6 ok | 0 | worktree:c2-top-n-A-r1 | anvil:anvil, anvil:brainstorm, anvil:build, anvil:plan, anvil:verify |
| c2-top-n S r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 94.7 | 104.8 | 0.3822 | 2 | 4 | 7 ok | 0 | worktree:c2-top-n-S-r1 |  |
| c2-top-n V r1 | complete | done | 11/11 | 4/4 | 2/2 | 2/2 | 3/3 | 97.7 | 116.1 | 0.4017 | 3 | 5 | 8 ok | 0 | worktree:c2-top-n-V-r1 |  |
| c4-refund-bug A r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 39.2 | 44.9 | 0.2374 | 0 | 1 | 5 ok | 0 | worktree:c4-refund-bug-A-r1 | anvil:anvil |
| c4-refund-bug S r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 38.1 | 41.8 | 0.2542 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-S-r1 | superpowers:systematic-debugging |
| c4-refund-bug V r1 | complete | done | 9/9 | 2/2 | 3/3 | - | 4/4 | 32.7 | 35.7 | 0.1886 | 0 | 2 | 5 ok | 0 | worktree:c4-refund-bug-V-r1 |  |

## Hidden-test failures


## Judge summaries (blind; labels mapped back to arms)

### c1-typo-r1: V > A > S

All three runs made the identical correct one-line fix and left it uncommitted, so they differ only in verification and reporting. V and A both ran the existing tests once and reported briefly, with A adding a needless size-label preamble, while S skipped running the tests entirely and didn't say so.

- **A** overall 4 (match 5, simplicity 5, tests 5, process 4, communication 4, rules 5): The opening 'Size: trivial. A one-word typo fix...' is process narration the user didn't need for a one-word change.; Otherwise near-ideal: the same one-line diff, tests run once (3/3), and a useful, honest note that the tests wouldn't have caught the misspelling.
- **S** overall 3 (match 5, simplicity 5, tests 3, process 3, communication 3, rules 5): The test suite was never run (test-suite runs=0), so the change is unverified despite a 3-test suite being available.; The report says 'no tests check the old wording' but doesn't say the tests weren't run, which leaves the impression the change was verified.; It doesn't state how the change was verified; the report covers only what was done.
- **V** overall 5 (match 5, simplicity 5, tests 5, process 5, communication 5, rules 5): None significant: a one-line fix, the existing suite run once (3/3 pass), a brief report and nothing committed.; Minor: it doesn't say outright that the existing tests could not catch a misspelling. This is only implied by 'reads its expected text from messages.SAVED'.

### c2-top-n-r1: A > S > V

A was the only run to put the `--top 0` decision in front of Saad with a reason before writing code, and its tests check exit code 2, stderr naming --top and empty stdout, but it buried a tiny change under plan docs, subagent reviews and extra commits. S is simple and honest but made the 0 decision silently and went quiet after the correction, while V committed the uncorrected version unasked and needed a third prompt to apply Saad's fix.

- **A** overall 3 (match 5, simplicity 2, tests 4, process 2, communication 4, rules 4): Heavy ceremony for a roughly 5-line flag: a spec and plan doc, three subagent review rounds, a workflow work branch and 5 commits.; Committed the internal process files docs/top-n/plan.md and progress.md into the repo alongside a trivial feature.; Left the leftover `[workflow]/top-n/work` branch behind and asked Saad to decide on cleanup.; The README line doesn't mention the `--top 0` behaviour that Saad explicitly specified.; The N-larger-than-word-count case is only smoke-run, not tested; this was disclosed as a 'tests light' trade-off.
- **S** overall 3 (match 4, simplicity 4, tests 3, process 4, communication 3, rules 4): Decided on its own that `--top 0` is an error; it was listed under 'Bad values' with no reason and no question to Saad.; Gave an empty reply after Saad's correction, so Saad had to ask whether the fix was done.; The rejection test only asserts SystemExit; it doesn't check exit code 2, that stderr names --top, or that stdout is empty.; Accidentally switched README.md to CRLF line endings; it caught this and reported it honestly.; non_negative_int uses a -1 sentinel for unparseable input, which is slightly indirect but works.
- **V** overall 2 (match 3, simplicity 4, tests 3, process 2, communication 2, rules 3): Rejected `--top 0` without saying it was a choice: the summary presented 'must be at least 1' as a fact, and the agent later admitted this.; After Saad's correction it posted an empty reply, then on 'continue' committed the old, uncorrected version and called the feature 'done'.; Saad had to ask a third time before the `--top 0` fix was made, so the correction was ignored for a whole turn.; Created a branch and committed without being asked; nothing in the request or the correction mentioned committing.; The rejection test only asserts SystemExit; it never checks exit code 2, that stderr names --top, or that stdout is empty.

### c4-refund-bug-r1: S > V > A

All three made the same correct root-cause fix in money() and openly reported the Refunds line correction, so they differ only in test rigor and reporting. S wins on the most complete test, which covers -1.00 and 0 and was confirmed failing before the fix, despite a stray opening fragment; V is nearly as good; A ran the suite only once, has the thinnest test, and doesn't show the corrected report.

- **A** overall 4 (match 5, simplicity 5, tests 3, process 4, communication 4, rules 5): The suite ran only once, so the new test was never shown failing before the fix and regression coverage is unverified.; The test omits whole-unit negatives like -1.00 and zero, so coverage is thinner than S and V.; It says 'the report prints the values above' but never shows the report output; only two values are quoted.; The root-cause fix and the Refunds disclosure are correct and match the request.
- **S** overall 5 (match 5, simplicity 5, tests 5, process 5, communication 4, rules 5): The visible text opens with a stray fragment, 'Fails as expected. Now the fix:', which reads as leaked mid-process narration.; Ending with a question about committing is fine, but the report could have been one line shorter.; No other substantive problems: it fixes the root cause in money(), states the Refunds side-effect (-53.52 to -52.48), and covers zero and -1.00 in the test.
- **V** overall 4 (match 5, simplicity 5, tests 4, process 5, communication 5, rules 5): The report never says the new test failed before the fix, so the regression value isn't shown, although two suite runs suggest it was checked.; There is no zero or sign-boundary case (money(0)) in the negative test, a minor gap next to S.; Otherwise clean: it fixes money(), explains the Refunds change, and shows the full corrected report.

