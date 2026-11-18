#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main
git config user.name "Eval Fixture"
git config user.email "fixture@example.com"
git config core.autocrlf false
git add -A
git commit -q -m "shelf: initial version"
