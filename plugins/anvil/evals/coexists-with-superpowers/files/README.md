# shelf

A small command-line bookmark keeper. Python 3.10+, standard library only.

- `python3 -m shelf add <url> [--tag <tag>]` saves a bookmark.
- `python3 -m shelf list` prints them, newest first.

Bookmarks are stored as JSON in the file named by `SHELF_FILE` (default `~/.shelf.json`).

Tests: `python3 -m unittest discover -s tests`
