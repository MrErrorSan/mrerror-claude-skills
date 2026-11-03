# Cross-model backends

The `cross-model` skill is backend-agnostic. This file is the one place that
knows *how* to reach an external model. Add a backend here and the skill picks it
up without changing its logic. Detection order: **Antigravity CLI (`agy`)** →
router gateway → Gemini API key → Claude-only fallback.

## 1. Antigravity CLI — `agy` (PRIMARY, subscription-backed, no API key)

`agy` is Google's Antigravity CLI, signed in with a Google **AI Pro/Ultra**
account. It gives a real second model with **no API key and no per-token
billing** — the cost is the subscription that's already paid for. This is the
preferred backend.

**Important:** `agy` is an *agentic coding CLI*, not a plain inference endpoint.
If you hand it a workspace (`--add-dir`) or put it in `--mode plan`, it tries to
*act* — reach for shell tools (which headless auto-denies → **empty output**) or
draft a plan and ask for confirmation (useless headless). To use it as a one-shot
reviewer you must force a direct answer. The pattern below was **verified working
on this machine (Nov 2026)**; keep to it.

- **Detect:** `command -v agy` (and `agy --version`).
- **List models on the current plan:** `agy models` — don't hardcode blindly.
  Verified here:
  **Review default → `gpt-oss-120b-medium`** — fast, reliable headless, and a
  *different vendor* from the Claude running the review → true cross-model signal.
  Verified cleanly in testing.

  **Research default → `gemini-3.8-flash-medium`** — a lower-cost Gemini tier
  that's strong at research; the right default for most questions. **Scale the
  model to the task, on the fly:** `gemini-3.8-flash-low` (quick lookups) ·
  `gemini-3.8-flash-medium` (default) · `gemini-3.8-flash-high` (deep / high-stakes,
  but noticeably slower headless — reserve it for when depth is worth the wait).

  **Other vendors:** `gpt-oss-120b-medium` (a third vendor, for research
  triangulation) and `claude-sonnet-4-6` / `claude-opus-4-6-thinking` (same family
  as the reviewer, so NOT a true cross-model check — use only for a stronger/fresh
  *Claude* pass).

  Headless `agy` cannot browse (tools are denied), so research answers are
  **parametric** — pair them with Claude's own web research for live sources.

- **Invoke (verified one-shot review):**

  ```bash
  read -r -d '' PROMPT <<'EOF'
  Output ONLY the review findings now, in this message. Do NOT create a plan. Do
  NOT write any files. Do NOT use tools. Do NOT ask questions. This is a one-shot
  review; your entire response must be the findings and nothing else.

  Review this unified git diff; report real defects in the + lines, blockers
  first, max 10, one per line as:
  SEVERITY | file:line | what is wrong | the failure it causes | the fix
  If none: NO-FINDINGS.

  --- DIFF ---
  <PASTE `git diff HEAD` HERE>
  EOF
  agy --model gpt-oss-120b-medium -p "$PROMPT"
  ```

- **Why this shape:**
  - **Inline the content into the prompt** (paste the diff/question). Do **not**
    use `--add-dir` for it — that makes the model reach for a file/shell tool that
    headless denies. Inlining also means the reviewer has nothing in your repo to
    touch → read-only by construction.
  - **No `--mode plan`** — default print mode + the hardened preamble gives a
    direct answer; plan mode triggers agentic planning.
  - **The hardened preamble** ("Output ONLY … no plan, no files, no tools, no
    questions") is what stops it acting. Keep it.
  - **Never** pass `--dangerously-skip-permissions`.
- **Timeout:** wrap in `timeout 120 agy …` so a slow/stuck model can't hang the
  turn; `gpt-oss-120b-medium` returns in well under that.
- **Large content** that won't fit a prompt: as a fallback, `--add-dir` a temp dir
  holding just the file + `--sandbox`, and allow a read-only command — but inline
  is strongly preferred; most reviews fit.
- **Quota:** inside the TUI (`agy` with no `-p`), `/usage` shows remaining
  subscription quota.

## 2. Router gateway — omniroute / CCR (optional)

If a local OpenAI-compatible router is running, it can reach many models/APIs
behind one endpoint — handy for polling several models or using providers `agy`
doesn't expose. (Not installed by default here; set up only if wanted.)

- **omniroute:** endpoint `http://localhost:20128/v1`; check with
  `curl -s http://localhost:20128/`.
- **claude-code-router (`ccr`):** gateway `http://127.0.0.1:3456`.
- Call the OpenAI-compatible `/v1/chat/completions` (or `/v1/messages`) with the
  content in the request body. Treat each model you poll as an independent track.

## 3. Gemini API key (optional, no subscription needed)

A direct Gemini CLI/API with an AI Studio key, if you prefer a keyed path over
`agy`. Free tier is Flash-only and ~250 req/day (Nov 2026).

- Install: `npm install -g @google/gemini-cli`; set `GEMINI_API_KEY`.
- Note: the consumer-subscription OAuth login was removed in June 2026 — a key is
  required for this route. For subscription access use `agy` (backend 1) instead.

## 4. Claude-only fallback (always available)

If no external backend is reachable, don't fail. Spawn a fresh Claude subagent
with **no** context from the original reasoning and have it review/research
independently. It shares model blind spots with you, so it's weaker than a true
second model — say so in the report — but an unbiased fresh pass still catches
real mistakes.

## Adding a new backend

1. Add a section here: how to detect it, how to call it, how to pass content
   (never stdin unless proven safe), which model/tier to use.
2. Slot it into the detection order in `SKILL.md` ("Pick a backend").
3. Keep the universal rules (read-only, strong reasoning tier, verify the content
   landed, constrained output) — they apply to every backend.
