#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git config user.name "Eval Fixture"
git config user.email "fixture@example.com"
git config core.autocrlf false
git add -A
git commit -q -m "ledger: csv-export spec, plan, T1 and T2"
git branch csv-export
git switch -q -c anvil/csv-export/work
# The topic is mid-build: T1 and T2 done, T3 open (state lives under the git dir).
mkdir -p .git/anvil
printf '%s\n' '{"slug": "csv-export", "dir": "docs/csv-export", "size": "full", "stage": "build"}' > .git/anvil/active.json
