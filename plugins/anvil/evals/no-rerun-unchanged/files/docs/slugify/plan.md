# Slugify: spec and plan

- **Approved:** 2026-11-17 by Saad ("looks good, build it")
- **Mode:** normal
- **Size:** direct
- **Synced branch:** slugify (local)
- **Status:** draft

## Spec lines

- **S1** `slugify(text)` returns lowercase ASCII words joined by single hyphens.
- **S2** Accented letters lose their accents rather than being dropped.
- **S3** A slug is cut at a word boundary at `max_length` (default 60).

## Decisions

- **Standard library only** (`unicodedata`). Claude's call: no dependency for three rules.

## Change log

- 2026-11-17 Created.

## Task table

| Task | Spec | Writes | Shared | Depends | Wave | Review |
|---|---|---|---|---|---|---|
| T1 | S1, S2, S3 | `slugkit/slug.py`, `tests/test_slug.py` | - | - | 1 | yes |

## T1: slugify

- **Spec:** S1, S2, S3.
- **Interfaces (produces):** `slugkit/slug.py`: `slugify(text: str, max_length: int = 60) -> str`.
- **Tests:** `tests/test_slug.py` (keep, S1, S2, S3). Command: `anvil run --scope targeted -- python3 -m unittest tests.test_slug`.
- **Steps:** 1. Write `slugify`. 2. Write the tests and run them.

## Test strategy

| Test | Type | Spec | Breaks if it fails | Task |
|---|---|---|---|---|
| `tests/test_slug.py` | keep | S1, S2, S3 | Broken URLs | T1 |

- Full suite: `python3 -m unittest discover -s tests`, under a second.
- Type-check: none.

## Commit points

| Commit | Closes | Message | Push |
|---|---|---|---|
| C1 | wave 1 (T1) | `feat(slugkit): slugify` | no |

## Execution

Sequential: one task.

Checkpoints: none.
