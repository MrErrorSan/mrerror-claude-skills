---
name: superpowers-upstream
description: >-
  Use in this repo when Saad asks to check Superpowers upstream, says there's a
  new Superpowers release or version, asks whether Anvil is behind obra/superpowers,
  asks what changed upstream since Anvil's baseline, or wants upstream changes
  adopted into Anvil. Also use when a scheduled check reports a new Superpowers tag.
  Not for installing, updating or debugging the Superpowers plugin itself.
---

# Superpowers upstream watch

Anvil copied and adapted parts of Superpowers at the version in
`upstream/superpowers/baseline.json`. It doesn't receive upstream improvements on
its own, so each new release is reviewed against the parts Anvil took, and every
change is adopted or rejected on purpose.

The runbook is `upstream/superpowers/README.md`. Read it in full before doing
anything else; it is the single source for the steps, the A–G rubric, the AFK
exception and what to update after every review. This skill only points to it, so the
two never drift apart.

In short: gather the data, read the Anvil side, give every change a verdict, stop for Saad, then apply and update the records; the README has each step.

If you only need to know whether a new release exists, compare the latest tag from
`git ls-remote --tags https://github.com/obra/superpowers` with the tag in
`baseline.json`, report it, and stop there.
