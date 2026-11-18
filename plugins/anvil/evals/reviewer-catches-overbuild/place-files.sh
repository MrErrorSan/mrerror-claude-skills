#!/usr/bin/env bash
set -eu
here="$(dirname "$0")"
cp -R "$here/files/." .
git init -q -b main
git config user.name "Eval Fixture"
git config user.email "fixture@example.com"
git config core.autocrlf false
git add -A
git commit -q -m "ledger: csv-export spec, plan and T1"
git branch csv-export
git switch -q -c anvil/csv-export/work
git tag t2-base
# T2's implementer, working on the work branch (sequential mode), committed its change.
cp -R "$here/lane-T2/." .
git add -A
git commit -q -m "feat(ledger): write_csv (T2)"
# The implementer's report goes in the build folder under the git dir, as the build skill does.
mkdir -p .git/anvil/build/csv-export
cp "$here/T2-report.md" .git/anvil/build/csv-export/T2-report.md
printf '%s\n' '{"slug": "csv-export", "dir": "docs/csv-export", "size": "full", "stage": "build"}' > .git/anvil/active.json
