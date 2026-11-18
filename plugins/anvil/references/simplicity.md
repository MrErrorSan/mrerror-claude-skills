# Simplicity

## Three always-on lines

- **Normal change:** the smallest diff that meets the spec lines, using existing patterns.
- **Redesign:** build what the spec describes. Existing code is reused only where the spec's *stays* list names it.
- **No piece without a spec line:** no abstraction, option or helper that no S-line needs.

The spec's `- **Mode:**` header line (`normal` or `redesign`) says which of the first two applies.

## Over-building checklist (per-task review)

List each of these you find in the diff, with file and line. Report all of them; the main agent decides what to change.

- **(a)** A new function, class, layer, wrapper or file with one caller, where no spec line needs it as a separate piece.
- **(b)** A parameter, option, flag, config value or extension point that no spec line asks for.
- **(c)** New code that does what existing code already does. Name the existing helper, component or library function. In a redesign, this applies only to code the spec keeps.
- **(d)** Error handling, fallbacks or validation for a state that cannot occur inside trusted code. Don't flag checks at trust boundaries (user input, external APIs, files, network) or checks that prevent data loss.
- **(e)** Tests, docs, comments or files no task asks for.
- **(f)** Normal change: edits to code outside the task. Redesign: new code shaped around old code that the spec replaces (wrapping it, adapting to it, or keeping its structure).

Don't suggest extra hardening, robustness or "maintainability" changes in this item.

## At the end

The converge check keeps an **unrequested** list: any changed file or behavior that no live S-line asks for is justified or removed.
