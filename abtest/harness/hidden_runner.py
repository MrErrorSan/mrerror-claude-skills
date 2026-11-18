"""Run the hidden tests in ./_hidden and print one JSON object with per-test outcomes.

Usage (cwd = the graded copy of the repo): python hidden_runner.py
Test names carry their category: test_core_*, test_edge_*, test_brief_*; anything under
_hidden/regression/ is category "regression".
"""
import io
import json
import re
import sys
import unittest

sys.path.insert(0, ".")


def category(test_id: str) -> str:
    if ".regression." in test_id:
        return "regression"
    m = re.search(r"\.test_(core|edge|brief)_", test_id)
    return m.group(1) if m else "core"


class Collect(unittest.TextTestResult):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.outcomes = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[test.id()] = ("pass", "")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test.id()] = ("fail", self._exc_info_to_string(err, test)[-600:])

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test.id()] = ("error", self._exc_info_to_string(err, test)[-600:])

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test.id()] = ("skip", reason)


def main() -> None:
    suite = unittest.defaultTestLoader.discover("_hidden", top_level_dir=".")
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, resultclass=Collect, verbosity=0)
    result = runner.run(suite)
    tests = [{"id": tid, "category": category(tid), "outcome": o, "detail": d}
             for tid, (o, d) in sorted(result.outcomes.items())]
    # Import errors show up as failed "unittest.loader._FailedTest" entries.
    print(json.dumps({"tests": tests, "ran": result.testsRun}))


if __name__ == "__main__":
    main()
