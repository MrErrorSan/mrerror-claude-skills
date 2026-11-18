#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git config user.name "Eval Fixture"
git config user.email "fixture@example.com"
git config core.autocrlf false
git add -A
git commit -q -m "tally: daily report, report-filters spec and draft plan"
git branch report-filters
# The topic an earlier session left at the plan stage (state lives under the git dir).
mkdir -p .git/anvil
printf '%s\n' '{"slug": "report-filters", "dir": "docs/report-filters", "size": "full", "stage": "plan"}' > .git/anvil/active.json
