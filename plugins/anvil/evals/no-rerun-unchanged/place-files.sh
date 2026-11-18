#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git config user.name "Eval Fixture"
git config user.email "fixture@example.com"
git config core.autocrlf false
git add -A
git commit -q -m "slugkit: slugify topic, built"
git branch slugify
git switch -q -c anvil/slugify/work
# The topic is built and waiting for verify (state lives under the git dir).
mkdir -p .git/anvil
printf '%s\n' '{"slug": "slugify", "dir": "docs/slugify", "size": "direct", "stage": "verify"}' > .git/anvil/active.json
