# Finding and driving a second-model backend

The `cross-model` skill doesn't depend on any one provider. It uses whatever
model from a family other than Claude this machine can reach today. This file
says how to find one, how to drive an unfamiliar one, and what's been learned
about the ones already met. When a new provider is added (a new subscription,
a new CLI), it's found by the steps below. A note in "Known backends" is
optional, and only worth adding once a quirk has cost time.

## 1. Look for candidates

Check all of these, and keep every hit from a family other than Claude:

- **Model CLIs on the PATH.** Check with `command -v <name>` for the CLIs of
  the major model providers, and for any CLI the user's CLAUDE.md or tool
  folders (`~/.local/bin` and similar) mention.
- **API keys that are configured.** Check whether the provider key variables
  are set (`[ -n "$VAR" ]`). Never print, log or read the value.
- **Local routers or model servers.** An OpenAI-compatible endpoint on
  localhost, a local model server, or a gateway the user runs. A quick request
  to its models endpoint shows whether it's up and what it serves.

## 2. Choose

1. The user's stated preference, if any (CLAUDE.md, a profile, or what they
   said this session).
2. Otherwise, **the cheapest model** any candidate offers. Ask the backend for
   its current model list every time (`<cli> models`, `--list-models`, the
   models endpoint). Don't rely on names from an earlier session: plans and
   model lists change.
3. If its answer isn't good enough for the question (empty, shallow or
   off-target), move up to the next tier from the same backend, again if
   needed, and say in the result which model gave the answer used.

If nothing is found, tell the user, suggest how they could add a second track
(a model CLI with their subscription, or an API key), and offer to run the
Claude track alone.

## 3. Driving an unfamiliar CLI

Read its `--help` (and the `--help` of any subcommand) before the first call,
and find:

- **non-interactive mode:** usually `-p`, `--print`, `--prompt` or `exec`;
- **model selection,** and how to list models;
- **a timeout** flag, or wrap the call in `timeout`;
- **output format:** prefer plain text or JSON you can parse; when there's a
  status field, check it rather than the exit code;
- **flags to avoid:** anything that auto-approves tools or edits files.

Then send a one-line probe ("reply with the word READY") before the real
brief. That confirms the call shape, the sign-in and the model in a few
seconds.

## 4. The one-shot shape

```bash
read -r -d '' PROMPT <<'EOF'
Output ONLY your research answer now, in this message. Do NOT create a plan.
Do NOT write any files. Do NOT use tools. Do NOT ask questions. Your entire
response must be the answer and nothing else.

<THE SELF-CONTAINED BRIEF: question, constraints, what is established,
output shape. Cite every claim with a URL; say when you answer from memory.>
EOF
<cli> <non-interactive flag> <model flag> <cheapest model> "$PROMPT" \
  > "<scratchpad>/second-track.txt" 2>&1
```

Put the content in the prompt argument. Don't pipe it through stdin unless
you've confirmed the CLI reads stdin.

## 5. Known backends

Notes from real use on this machine. Model names are deliberately left out:
list them from the tool each time.

### Antigravity CLI (`agy`)

- An agentic coding CLI with a Google subscription sign-in, so there's no API
  key and no per-token cost. Models: `agy models`.
- **stdin is ignored** by `agy -p`. Put the brief in the prompt.
- **`--mode plan` or `--add-dir`** makes it reach for shell tools, which
  headless mode auto-denies, so it returns nothing. Use plain `-p` with the
  one-shot preamble above. If a file is unavoidable, `--add-dir` a temp folder
  holding only that file, and tell it to use only its file-reading tool.
- **`--effort` is rejected** for models whose tier is in the name. Leave it
  off unless `agy --help` and the chosen model accept it.
- **`--print-timeout <n>s`** sets the timeout.
- **It can't browse when headless.** Its answers come partly from memory.
- **Never** pass `--dangerously-skip-permissions`.
- Remaining quota: `/usage` inside the interactive `agy`.

### Claude-only fallback

When no second family is available: run the Claude track alone, and label the
result as single-model research. Another Claude model isn't a second family.
It shares Claude's blind spots, so it doesn't count as the second track.
