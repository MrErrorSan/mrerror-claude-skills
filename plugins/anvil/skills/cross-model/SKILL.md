---
name: cross-model
description: >-
  Research a question on two independent tracks, Claude subagents and a model
  from another family that this machine can reach (whatever CLI, API key or
  local router the user has set up), then compare and consolidate them, so the
  answer doesn't rest on one model's mistakes. Use ONLY when the user asks for
  it in their message: "use cross-model", "research this with another model
  too", "get a second model's view on this". Never run it on your own
  initiative, because other providers cost quota and aren't always available.
  For research without that request, use Claude subagents alone. Not for
  reviewing a diff.
---

# Cross-model research

Claude subagents research well, but they share one model's blind spots, so
their agreement can be one mistake repeated. A track from another model family
on the same question catches some of what they miss, and agreement means more
when it comes from two families.

**Local files only.** The brief, both tracks' output and the consolidated
answer are files on this machine. Only the brief goes to the second model:
the question and its context, never secrets or whole files it doesn't need.
No Artifacts, hosted pages or shared links unless the user asks for one.

## 1. Find the second track

Look at what's available now. Don't assume what was there last time, because
subscriptions and models change. How to look is in
[references/backends.md](references/backends.md).

- **Candidates:** model CLIs on the PATH, API keys that are configured (check
  that the variable exists; never print or read its value), and local model
  routers or servers. Keep only those from a family other than Claude.
- **Choose:** the user's stated preference (in CLAUDE.md or what they say),
  otherwise **the cheapest model** any candidate offers. List the backend's
  models each time instead of assuming names. If its answer isn't good enough
  for the question (empty, shallow or off-target), move up to the next tier
  from the same backend, again if needed, and say which model gave the answer
  you used.
- **Nothing available:** tell the user, suggest how they could add a second
  track, and offer to run the Claude track alone.

## 2. The flow

1. **Brief the second track.** It has none of the conversation. Write a
   self-contained brief: the question, the constraints, what's already
   established, the output shape, and "cite every claim with a URL; say when
   you're answering from memory".
2. **Launch it in the background** (Bash with `run_in_background: true`),
   writing to a file in the scratchpad.
3. **Run the Claude track at the same time:** research subagents in parallel,
   one sub-question each. Use web search and fetch for live, cited sources.
   **Write the Claude track's findings down** before step 4.
4. **Don't read the second track's output until then.** Reading it first
   anchors you to its framing and turns two investigations into one, and that
   independence is the whole point.
5. **Compare,** sorting every claim into:
   - **agreed by both:** the strongest, but still only a signal. Two models
     reading the same bad source fail the same way, so spot-check that the
     citations resolve;
   - **conflicting:** run a tiebreak search and rule on it;
   - **unique to one track:** say which track found it, and whether it holds
     up.
6. **Consolidate** into one answer: your ruling, your confidence, and what
   neither track could settle. For a substantial question, write it to
   `docs/research/YYYY-MM-DD-<topic>.md` with the second track's raw output in
   an appendix. Otherwise answer in chat.

## Gotchas, for any backend

- **Make sure the content landed.** Some CLIs silently ignore stdin and answer
  confidently about nothing. Put the brief in the prompt argument, and check
  that the answer is about your question.
- **Agentic CLIs try to act.** Given a workspace or a planning mode, they reach
  for tools that headless mode denies, and return nothing. Ask for a one-shot
  answer: "answer now, no plan, no files, no tools, no questions".
- **Keep it read-only.** Never pass a flag that auto-approves its tools.
- **It may not be able to browse.** Part of its answer can come from memory, so
  treat any claim without a working citation as unverified.
- **Set a timeout,** so a stuck backend can't hang the run.

## Output shape

```markdown
## Cross-model research: <question>
Tracks: Claude (<n> subagents) and <backend: model>, or "Claude only: <why>"

### Agreed
- <claim> (sources)

### Conflicting, and the ruling
- <claim A> vs <claim B>: <tiebreak> → <ruling>

### Unique to one track
- <claim>, found by <track>: <holds up / doesn't>

### Answer
<the consolidated answer, confidence, and what neither track settled>
```

The value is in judging the two tracks against each other, not in pasting
them. A second model is leverage on blind spots, not an authority.
