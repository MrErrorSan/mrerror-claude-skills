# Anvil vs Superpowers: A/B test design

- **Date:** 2026-11-18
- **Question:** Is Anvil 1.0 (`plugins/anvil`, branch `anvil-rebuild`) at least as good as Superpowers 7.0.2 on the work Saad actually does? Good means correct, faster, and structured the way he wants. If yes, it can replace Superpowers.
- **Status:** design only. Nothing has been run yet except the feasibility probes (§7).

## 1. Why not `claude plugin eval`

The 9 cases in `plugins/anvil/evals/` check that Anvil follows **its own** process, for example that `anvil topic start` ran. They can't be run against Superpowers. The runner also falls short as an A/B tool:

| Need | `claude plugin eval` |
|---|---|
| Plugin A vs plugin B | No. Only plugin vs no plugin. |
| Per-run time, cost, turns | No. Suite totals only. |
| Run hidden tests after the session | No. "There are no custom-code graders." |
| A user who answers questions and approves at stops | No. One follow-up turn at most, via `history_file`. |
| Shell tools on native Windows | No. Needs the WSL2 sandbox. |

Those 9 cases stay as Anvil's conformance suite. This A/B harness is separate.

## 2. Harness

A small Python runner in `abtest/`, driving `claude -p` directly.

**Per run:**
1. Copy the case fixture into a fresh temp git repo. No remote, so nothing can be pushed. Anvil's `.git/anvil/` state starts empty.
2. Start the agent:

   ```
   claude -p <request> --setting-sources "" --plugin-dir <arm plugin> \
     --model <pinned> --effort <pinned> --permission-mode bypassPermissions \
     --output-format stream-json --verbose --session-id <uuid>
   ```

   `--setting-sources ""` loads none of the installed plugins and none of the loose `~/.claude/skills` copies. Only the arm's plugin loads, with its own hooks. This was probed; see §7.
3. **The simulated user.** When the agent's turn ends, a separate Claude call plays Saad. It has no plugins and no tools. It gets the case's hidden **user brief** and the agent's last message, and writes Saad's reply. The reply goes back with `--resume <uuid>`. This repeats until the agent says it's done, or it hits the case's cap on user turns.
4. **Grading.** The hidden acceptance tests are copied in only after the session ends, so the agent never sees them. They run along with the fixture's original tests. Then the measures below are collected.

**The simulated user's fixed rules (same for every arm):**
- Answer questions from the brief. If the brief doesn't cover something, say "your call".
- Approve a spec or plan in plain words ("Approved, go ahead") when it covers the brief's must-haves. Otherwise name the missing must-have, once.
- On a choice with a recommendation (inline or subagents, fresh session or here), take the recommendation. Otherwise say "continue here".
- At finishing: "Leave it committed on the branch, don't merge or push."
- If the request said AFK: "I'm away, decide yourself."
- Some cases inject a requirement change at a scripted point (case 6).

**Arms:**
- **A: Anvil.** `plugins/anvil` at a pinned commit.
- **S: Superpowers 7.0.2.** The installed cache copy.
- **V: vanilla**, no plugin (optional). It shows whether either plugin beats plain Claude at all, and it's the cheapest control.

Saad's global `~/.claude/CLAUDE.md` still loads in every arm (`--setting-sources` doesn't remove it). It's the same for all arms and it's his real environment, so it stays. Cases also grade whether each arm obeys it: no co-author trailer, no Artifacts.

## 3. Measures

| Area | Measure | How |
|---|---|---|
| **Correct** | Hidden acceptance tests passed | The harness runs them after the session |
| | Existing tests still pass | The fixture suite |
| | Matches the request | Blind judge, from the rubric |
| **Fast** | Agent time | Sum of `duration_ms` over the agent's turns. The simulated user's time is excluded |
| | User turns needed | Count of interruptions: questions and stops |
| | Cost and tokens | `total_cost_usd`, `usage` from stream-json |
| | Test-suite runs | Bash calls matching the case's test command |
| | Agent turns, tool calls, subagents | From the trace |
| **Structure** | Code diff size, files touched, test lines added | `git diff` against the fixture commit, split into code, tests and docs |
| | Documents written and where | Paths. One case has a project rule for doc location |
| | Commits and trailers | `git log`. A Claude co-author trailer breaks Saad's rule |
| | Over-build, test bloat, unexplained decisions, questions the repo already answers, pushback on changes | Blind judge |

**Blind judge.** An Opus call gets each run's request, final diff, documents, user-turn log and closing message. Plugin names and skill names are scrubbed, and the order is randomised. It does two things:
- Scores each run 1–5 on the case rubric.
- Picks a pairwise winner, A vs S, per case.

## 4. Cases

Each case is a small Python repo using the standard library only, with a user brief and hidden tests. They are built to reproduce Saad's complaints about Superpowers and the places where Anvil might lose.

| # | Case | What it tests | Expected winner | Main grade |
|---|---|---|---|---|
| 1 | **Typo fix** (one-line message change) | Ceremony on trivial work | A | Time, user turns, no docs |
| 2 | **Small feature with edge cases** (`wordfreq --top N`: N=0, N > word count, bad N) | Does test-first catch edge cases that test-after misses? | S? | Hidden edge tests |
| 3 | **Three independent parts plus a slow suite** (`ledger`: CSV export, JSON export, `--since` filter; the suite takes about 20 s) | Parallel fan-out, test reruns on unchanged code | A | Agent time, suite runs, hidden tests |
| 4 | **Bug reported by symptom** (wrong totals after a refund; the cause is two files away from the symptom) | Debugging discipline: root cause, not a patch | ? | Hidden repro test, the judge on root cause |
| 5 | **Vague feature** ("tags on notes"). The repo answers most questions, and the repo `CLAUDE.md` says docs go in `docs/<feature>/` | Questions asked vs looked up, the doc-location rule | A | User turns, judge, doc paths, hidden tests |
| 6 | **Change mid-build** (CSV export, then after plan approval: "use semicolons, the accountant is in Germany") | Does the change flow back into the spec and plan, with pushback? | A | Hidden tests (new behavior), the judge on doc and code agreement |
| 7 | **AFK** ("I'm going to bed, finish it", a medium feature) | Runs to the end without asking | ? | Completion, user turns = 0, hidden tests |

These come from three sources:
- the build session's list of complaints (reruns of a slow suite, "checks pass but it isn't what I asked", silent decisions, independent tasks run one at a time, test bloat);
- the design session's list (an interview for a one-file change, plans that restate full code, ignored doc-location rules);
- both sessions' "where Anvil might lose" lists (small tasks, edge-case logic, AFK).

## 5. Scale and cost

- **Pilot first:** cases 1, 2 and 4, one run each for A and S (6 runs). This calibrates the simulated user, the time and cost per run, and catches harness bugs before money goes into the full set.
- **Full:** 7 cases × 3 runs × 2 arms = 42 runs. Add 21 more for arm V.
- Runs are interleaved A, S, A, S…, two at a time.
- The cost estimate comes from the pilot. Each run uses Saad's Claude subscription on the current account.
- **Pinned:**
  - agent model `claude-opus-5-5` at effort `high` (Saad's setting);
  - the simulated user on Sonnet 5.5;
  - the judge on Opus 5.5.

## 6. Pass bar for replacing Superpowers

Anvil is ready when all of these hold across the full run:
1. **Correctness:** Anvil's hidden-test pass rate is ≥ Superpowers' on every case. No regressions in the existing tests.
2. **Speed:** median agent time is ≤ Superpowers' overall, and clearly lower on cases 1 and 3.
3. **Friction:** no more user turns than Superpowers on any case, except where a stop Saad wants (spec or plan) accounts for the difference.
4. **Structure:** the judge's mean is ≥ Superpowers' on rubric scores, and there are no co-author trailers and no ignored doc rules.
5. **Hard failures:** no run where Anvil hangs at a stop, loops, or claims done with failing tests.

Any miss becomes a finding with the transcript excerpt, a ranked severity and a proposed fix to the skill.

## 7. Feasibility probes (done 2026-11-18, Haiku, about $0.01)

- **`--safe-mode` does not isolate.** All installed plugins still loaded, Superpowers included. Rejected.
- **`--setting-sources ""` isolates.** Only the `--plugin-dir` plugin and three built-ins loaded. No loose user skills loaded. The user `CLAUDE.md` still loads.
- **Anvil hooks under `claude -p` work.** SessionStart fired. UserPromptSubmit logged both the first prompt and the `--resume` follow-up to `.git/anvil/prompts.jsonl`. This settles two open questions from the 1.0 handover: a scripted user can pass Anvil's stops.
- **`gate.INJECTED_RE` already filters `<cross-session` messages**, so a peer session's text can't count as Saad's words.

## 8. Known biases

- The fixtures are small. Parallel speed-up shows best on bigger work, so case 3 is the only fair test of fan-out. The phase-5 replays of real requests (design §9.2) are still needed after this.
- The simulated user is a model. It could approve something Saad wouldn't. Its log is in the report for spot checks.
- Anvil gets a slight edge: its gates are tuned for "Saad's words", and the simulated user writes like Saad. Superpowers has no such gate, so it can't lose on that.
- Each Anvil hook starts Python and git (about 0.3–0.5 s on Windows). That's counted, because Saad pays for it too.
