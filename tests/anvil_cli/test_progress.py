import tempfile
import unittest
from pathlib import Path

from anvil_cli import progress, state

from .helpers import make_repo, write

PROGRESS = """# Progress: demo
- **Stage:** build
- **Wave:** 1 of 3
## Tasks
- [x] T1 Foundations C1
- [~] T2 Gates (lane anvil/demo/T2)
- [~] T3 Plan check (lane anvil/demo/T3)
- [ ] T4 Results
  - [ ] a sub-bullet, not a task
- [ ] T5 Hooks
- [ ] T6 Stale
## Commit points
- C1 abc1234 pushed 2026-11-18
- [ ] not a task, outside the Tasks section
## Blockers
<!-- one line each: - <task>: <what it waits on> -->
- T3 waits on a port decision
  more detail on the T3 blocker

## Decision log
<!-- newest first; each: - 2026-11-18 **<choice>** — <reason>. Confidence: high|medium|low. Changes if: <fact>. -->
- 2026-11-19 **Use port 3001** — 3000 is taken. Confidence: high. Changes if: 3000 frees up.
- 2026-11-18 **Older choice** — reason. Confidence: low. Changes if: x.
## Stop note
"""


class ProgressTests(unittest.TestCase):
    def test_summary_counts_markers(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            repo = make_repo(Path(tmp))
            self.assertIsNone(progress.progress_summary(repo))
            state.save(repo, "active.json",
                       {"slug": "demo", "dir": "docs/demo", "size": "full", "stage": "build"})
            self.assertIsNone(progress.progress_summary(repo))
            write(repo / "docs/demo/progress.md", PROGRESS, crlf=True)
            self.assertEqual(progress.progress_summary(repo), {
                "stage": "build",
                "wave": "1 of 3",
                "open": 3,
                "in_progress": 2,
                "done": 1,
                "blockers": ["T3 waits on a port decision"],
                "last_decision": "2026-11-19 **Use port 3001** — 3000 is taken. "
                                 "Confidence: high. Changes if: 3000 frees up.",
            })


if __name__ == "__main__":
    unittest.main()
