# The user's voice

Drafts that sound polished and generic read as machine-written, and teammates
notice. The voice guide records how the user actually writes, so stand-up
answers, replies and ticket comments sound like them, minus their mistakes.

**Where it lives:** `log.voice_path` from the script, which is
`~/standups/voice.md`. `log.voice` is that path when the file exists, and
`null` when it doesn't. It's private: never copy it, or any message it was
built from, into a repo, a report, the tracker or chat.

## Using it

When `log.voice` is set, read it before drafting, and for every draft:

1. **Pick the register by audience and channel.** Match the language and
   register the other person used in that thread (a reply in a mixed-language
   chat may stay mixed). Posts to management, clients or a team channel use
   the guide's formal register.
2. **Copy the voice:** the user's verbs, sentence length, greetings, sign-offs,
   how they give estimates, and how they ask.
3. **Don't copy the mistakes** the guide lists (typos, missing words, vague
   dates, bare acks). Fix them quietly, keeping the user's short style.
4. **Avoid the giveaways:** stacked achievements in one line, adjective
   triplets, em dashes, and words the user never uses ("leveraged",
   "seamless", "robust", "comprehensive", "ensuring"). Shorter beats smoother.

When `log.voice` is `null`, draft in plain, short sentences, and after the
report is approved, offer once to build the guide. Don't nag.

## Building or refreshing it

Only when the user agrees, and only from the user's **own sent messages**,
read on **their own account** (the same rule as reading the stand-up chat).
Never read the guide's source through a connector signed in as someone else.

1. **Collect** the user's recent sent messages, read-only: a few hundred is
   plenty, and about 150 already shows the patterns. Use search sorted by
   newest, page slowly, and back off when rate-limited. Replace links with
   `<link>` and drop file-only messages. Keep the raw collection in a temp
   folder; it isn't kept after the guide is written.
2. **Never keep secrets.** Redact passwords, tokens, login links and keys
   before reading. Don't quote them in the guide, even partially.
3. **Group by audience:** their manager, seniors, juniors or mentees, team
   channels, clients, the stand-up bot. Note who gets which language and
   register.
4. **Write the guide** to `log.voice_path` with these sections:
   - **Registers:** a table, chat vs posts: language, length, openers,
     courtesy words, punctuation. Plus the rule for picking one.
   - **How I sound (keep):** 6 to 10 traits, each with a short real phrasing.
   - **How stand-ups should read:** the user's own best edited lines as the
     target, any machine-polished ones as counter-examples, and the length
     rule.
   - **Don't copy:** the weak spots drafts must fix, each with an example.
   - **Habits to change:** things that aren't about voice but cost the user,
     such as sharing credentials in chat or status without an ETA. Say these
     to the user plainly, once.
   - **Before / after:** 3 rows: too polished, too terse, the user at their best.
5. **Show the user** the key findings (traits to keep, weak spots, habits)
   and let them correct the guide. It's theirs.

Refresh every month or two, or when the user says drafts sound off. Refresh
by re-collecting, not by appending to the old file.
