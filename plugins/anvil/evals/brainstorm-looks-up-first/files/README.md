# notes

A small JSON notes service. Python 3.10+, standard library only: `http.server` for the
API and `sqlite3` for storage.

- `python3 -m notes.api` serves on port 8040.
- The caller's user name comes from the `X-User` header (the service runs behind a
  gateway that sets it).

Tests: `python3 -m unittest discover -s tests`
