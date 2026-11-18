# notes

A small JSON notes service. Python 3.10+, standard library only: `http.server` for the
API and `sqlite3` for storage.

- `python -m notes.api` serves on port 8040.
- The caller's user name comes from the `X-User` header (the service runs behind a
  gateway that sets it).

Tests: `python -m unittest discover -s tests`
