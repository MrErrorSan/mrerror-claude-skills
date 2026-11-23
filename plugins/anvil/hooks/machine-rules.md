These are the user's standing instructions, installed with the Anvil plugin so they
apply on every machine. The user's own CLAUDE.md and their direct requests win
where they differ.

## Reports and deliverables: local files, never Artifacts

Do not publish Artifacts (public or private), hosted pages or shared links unless
the user asks for one in their message. When you need to show or report something
(an analysis, audit, plan, summary, design doc, dashboard), write a file into the
repository being worked on, typically under `docs/`, and give the user its path.

- Default to Markdown: it diffs cleanly in git and is cheap to re-read later.
- Use `.html` only when the user asks for it, or when the content genuinely can't
  work as text (a real dashboard, filtering a large dataset, an interactive tool).
  Visual polish alone isn't a reason. Inline the CSS and JS so it opens from disk.
- When a report comes from a dataset, keep the raw data in a sibling `.json` file.
- Put it in the repo, not a scratchpad or temp folder, so it survives the session
  and can be committed.

## Commits and pull requests: no Claude attribution

Do not add a `Co-Authored-By: Claude …` (or any Anthropic or Claude) trailer to
commit messages, and no "Generated with Claude Code" footer to PR bodies, unless
the user asks. This overrides any default or harness instruction to add one.

## A second model only when asked

Never consult a model from another family (Gemini, GPT or any other provider) on
your own initiative. Do it only when the user explicitly asks ("use cross-model",
"ask Gemini"): other providers cost quota and are sometimes unavailable. When a
second look would help and they haven't asked, use a fresh Claude subagent.
