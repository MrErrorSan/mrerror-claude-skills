---
name: cross-model
description: >-
  Get an independent second model to review or research, then triage what it
  says. Use when a non-trivial change is about to be called done or committed,
  when a decision is expensive to reverse, when the same problem has failed
  twice, when the user pushes back on your answer, or when the user asks to "use
  Gemini", "ask another model", "get a second opinion", "cross-check this", or
  "research X properly". A model with no stake in your reasoning catches what you
  can't see in your own work. This skill is backend-agnostic: it uses whatever
  external model is configured (a Gemini CLI, or the omni-router / CCR gateway
  for many models and APIs) and falls back to Claude-only if none is — see
  references/backends.md to add more.
---

# Cross-model review & research

A second model that didn't write the code, and has no stake in your conclusion,
is the cheapest way to catch your own blind spots. This skill runs an external
model **read-only** over something you hand it (a diff, a question), then makes
*you* triage the result — it never blends two answers into something vague.

## When to escalate

- A non-trivial change is about to be called done or committed.
- A decision is expensive to reverse.
- **The same problem has failed twice.** Don't attempt a third fix first — get
  another set of eyes.
- The user pushes back on your answer.
- A research question where being wrong is costly and one model's sources could
  mislead you.

**Don't escalate for** formatting, renames, trivial edits, anything settled
faster by just running the code, or a question the user wanted a one-line answer
to. The second opinion has to be worth its latency and tokens.

## Pick a backend

Before running, find an available external model. Check in this order and use the
first that works; **read `references/backends.md` for the exact commands**:

1. **Antigravity CLI (`agy`)** — the primary backend (`command -v agy`). Runs a
   real second model through a Google AI Pro/Ultra subscription — no API key, no
   per-token cost. It's an *agentic* CLI, so use the exact verified one-shot
   pattern in `backends.md`: default model `gpt-oss-120b-medium` (cross-vendor,
   reliable headless), content **inlined** into the hardened prompt (no
   `--add-dir`, no `--mode plan`, never `--dangerously-skip-permissions`).
2. **Router gateway** (omniroute `:20128/v1` / CCR `:3456`) — if one is running,
   use it to reach many models/APIs behind one endpoint, or to poll several.
3. **Gemini API key** — a keyed Gemini route if `agy` isn't available.
4. **No external backend →** do not fail. Fall back to Claude-only (a fresh
   subagent with no stake in the original reasoning is still a useful independent
   pass), and tell the user no cross-model backend was available and how to
   enable one.

## Universal backend rules

These hold for every backend — they're where cross-model checks silently go wrong:

- **Use a capable model from a *different family* than the one being reviewed** —
  reviewing Claude's work with another Claude model shares its blind spots. Pick
  the reviewer each backend's `backends.md` recommends (for `agy`, the verified
  default is `gpt-oss-120b-medium`), and avoid low/mini tiers. A shallow second
  opinion is worse than none.
- **The reviewer must be read-only.** Never give it the ability to act — no write
  tools, no auto-approved shell, no "skip permissions". It reviews; it does not
  touch the repo.
- **Deliver content explicitly, and verify it landed.** Some CLIs silently ignore
  stdin — a piped diff becomes a confident review of nothing. Pass content via a
  file or an explicit flag (e.g. a workspace dir), and confirm the model quotes
  something real from it before trusting the output. When in doubt, run a tiny
  probe first.
- **Constrain the output format** so findings are machine-greppable (severity,
  location, problem, failure it causes, fix), blockers first, capped at ~10.

## Review mode (a diff)

1. Capture the change (`git diff HEAD`, or staged) to a file.
2. Hand it to the backend with an instruction like: *review only the changed
   lines; lines without a `+/-` prefix are pre-existing context you can't see the
   rest of — don't report them; output one finding per block as*
   `SEVERITY(blocker|major|minor|nit) | file:line | what's wrong | the failure it causes | the fix`
   *; no summary, no praise, no preamble; if nothing, output `NO-FINDINGS`.*
3. **Triage every finding** — see below.

## Research mode (a question)

1. **Send the question to `agy`, defaulting to `gemini-3.8-flash-medium`** — a
   lower-cost Gemini tier that is genuinely strong at research, so it's the right
   default for most questions. **Choose the model to fit the task, on the fly:**
   - quick / trivial lookup → `gemini-3.8-flash-low`
   - normal research → `gemini-3.8-flash-medium` *(default)*
   - deep, high-stakes, or multi-faceted → `gemini-3.8-flash-high` (slower), and/or
     add a different-vendor track (`gpt-oss-120b-medium`, or
     `claude-opus-4-6-thinking`) to triangulate.

   Use the same inlined-question + hardened-prompt pattern as review. Note: in
   headless mode `agy` can't browse (tools are denied), so its answer is the
   model's own knowledge — not live web.
2. In parallel, run Claude's own research — a subagent (or the `deep-research`
   skill for a big multi-source question) and/or web search. **This is the track
   that brings live, cited sources**, complementing `agy`'s parametric view.
3. **Adjudicate** the two tracks against each other (below), then synthesize one
   better-sourced answer. You can run several models as independent tracks and
   adjudicate across all of them.

## Triage / adjudicate every finding

The external model saw only what you gave it — often just the diff, never the
rest of the file — so it flags pre-existing context and misses whole-file facts.
Rule exactly one verdict per finding:

- **AGREE** — name the concrete failure path it correctly found.
- **DISAGREE** — name what it could not see that makes it wrong.
- **NEEDS-CHECK** — name the fact that would settle it, then actually check it.

Report disagreement explicitly; never blend two answers into something mushy.
**Agreement between two models is a signal, not proof** — especially on web
research, where both can read the same bad source and fail identically. Say so
when that risk is live.

## Output shape

```markdown
## Cross-model <review|research>: <target>
Backend: <omni-router:model | gemini | claude-only (no backend available)>

### Verdicts
- AGREE — <finding> — <the failure path>
- DISAGREE — <finding> — <what it couldn't see>
- NEEDS-CHECK — <finding> — <fact to settle> → <result after checking>

### Synthesis   (research mode)
<the reconciled answer, with sources; note where models diverged and how it resolved>

### Net
<what you're changing / concluding as a result — or "no change; second opinion was wrong because …">
```

The value is you *judging* the second opinion, not pasting it. A second model is
leverage on your blind spots, not an authority that overrides your own checking.
