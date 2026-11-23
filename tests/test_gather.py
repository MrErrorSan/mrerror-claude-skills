"""Tests for plugins/anvil/skills/standup/scripts/gather.py.

Each test names what breaks if it fails. Run: python -m unittest discover -s tests -v
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins", "anvil", "skills", "standup", "scripts"))
import gather  # noqa: E402

UTC = dt.timezone.utc


def ts(h, m=0, day=23):
    return dt.datetime(2026, 11, day, h, m, tzinfo=UTC).isoformat().replace("+00:00", "Z")


def write_session(projects, name, lines):
    d = os.path.join(projects, "some-project")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".jsonl"), "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line if isinstance(line, str) else json.dumps(line))
            f.write("\n")


def user(cwd, t, text, **kw):
    return {"type": "user", "cwd": cwd, "timestamp": t, "gitBranch": "main",
            "message": {"role": "user", "content": text}, **kw}


def edit(cwd, t, path):
    return {"type": "assistant", "cwd": cwd, "timestamp": t,
            "message": {"content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": path}}]}}


class WindowTests(unittest.TestCase):
    """A4: a wrong window silently drops or double-reports a day's work."""

    def test_monday_covers_friday_and_weekend(self):
        tz = dt.timezone(dt.timedelta(hours=5))
        monday = dt.datetime(2026, 11, 23, 10, 0, tzinfo=tz)
        self.assertEqual(gather.previous_working_day_start(monday), dt.datetime(2026, 11, 20, 0, 0, tzinfo=tz))

    def test_tuesday_covers_monday(self):
        tuesday = dt.datetime(2026, 11, 24, 9, 0, tzinfo=UTC)
        self.assertEqual(gather.previous_working_day_start(tuesday).date(), dt.date(2026, 11, 23))

    def test_last_report_covered_until_wins(self):
        """A4: a second report the same day (-2) is newer than the first, not older."""
        with tempfile.TemporaryDirectory() as log:
            for name, until in (("2026-11-19.json", "2026-11-19T05:00:00+00:00"),
                                ("2026-11-20.json", "2026-11-20T05:00:00+00:00"),
                                ("2026-11-20-2.json", "2026-11-20T11:00:00+00:00")):
                with open(os.path.join(log, name), "w") as f:
                    json.dump({"covered_until": until}, f)
            start, source = gather.window_start(log, dt.datetime(2026, 11, 23, tzinfo=UTC))
            self.assertEqual(start, dt.datetime(2026, 11, 20, 11, 0, tzinfo=UTC))
            self.assertTrue(source.endswith("2026-11-20-2.json"))


class GapTests(unittest.TestCase):
    """A22: an undetected gap makes Yesterday start from a stale report."""

    def test_friday_report_on_monday_is_no_gap(self):
        self.assertEqual(gather.missed_working_days(dt.date(2026, 11, 20), dt.date(2026, 11, 23)), 0)

    def test_report_from_last_wednesday_on_monday_misses_two_days(self):
        self.assertEqual(gather.missed_working_days(dt.date(2026, 11, 18), dt.date(2026, 11, 23)), 2)

    def test_gather_reports_the_gap(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as log:
            open(os.path.join(log, "2026-01-05.md"), "w").close()
            r = gather.gather(root, projects_dir=os.path.join(root, "none"), with_prs=False, log_dir=log)
            self.assertEqual(r["log"]["latest_date"], "2026-01-05")
            self.assertGreater(r["log"]["missed_working_days"], 0)


class LogLocationTests(unittest.TestCase):
    """A10: the save path is computed, never guessed, so reports don't scatter across folders."""

    def test_default_log_dir_is_home_standups(self):
        self.assertEqual(gather.default_log_dir(), os.path.join(os.path.expanduser("~"), "standups"))

    def test_next_report_path_adds_suffix_when_taken(self):
        with tempfile.TemporaryDirectory() as log:
            day = dt.date(2026, 11, 23)
            md, js = gather.next_report_paths(log, day)
            self.assertEqual((md, js), (os.path.join(log, "2026-11-23.md"), os.path.join(log, "2026-11-23.json")))
            open(md, "w").close()
            self.assertEqual(gather.next_report_paths(log, day)[0], os.path.join(log, "2026-11-23-2.md"))

    def test_gather_reports_log_paths_independent_of_root(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as log:
            r = gather.gather(root, projects_dir=os.path.join(root, "none"), with_prs=False, log_dir=log)
            self.assertEqual(r["log"]["dir"], os.path.abspath(log))
            self.assertTrue(r["log"]["save_report_to"].startswith(os.path.abspath(log)))
            self.assertIsNone(r["log"]["latest_report"])

    def test_voice_path_is_reported_only_when_the_file_exists(self):
        """A26: drafts must not claim a voice guide that isn't there, nor build one in a random folder."""
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as log:
            run = lambda: gather.gather(root, projects_dir=os.path.join(root, "none"), with_prs=False, log_dir=log)["log"]
            first = run()
            self.assertIsNone(first["voice"])
            self.assertEqual(first["voice_path"], os.path.join(os.path.abspath(log), "voice.md"))
            open(first["voice_path"], "w").close()
            self.assertEqual(run()["voice"], first["voice_path"])


class SessionScopeTests(unittest.TestCase):
    """A13: titles or prompts from outside the scope would leak another project's work into a report."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = self.tmp.name
        self.root = os.path.join(base, "work")
        self.other = os.path.join(base, "elsewhere")
        self.projects = os.path.join(base, "projects")
        os.makedirs(os.path.join(self.root, "app"))
        os.makedirs(self.other)
        self.since = dt.datetime(2026, 11, 23, 0, tzinfo=UTC)
        self.until = dt.datetime(2026, 11, 23, 23, tzinfo=UTC)

    def tearDown(self):
        self.tmp.cleanup()

    def run_sessions(self):
        out, _ = gather.sessions_evidence(self.projects, self.root, [], self.since, self.until)
        return {s["id"]: s for s in out}

    def test_inside_session_has_title_and_prompts(self):
        write_session(self.projects, "in", [
            {"type": "ai-title", "aiTitle": "Fix the login page"},
            user(self.root, ts(9), "fix the login redirect"),
        ])
        s = self.run_sessions()["in"]
        self.assertEqual(s["scope"], "inside")
        self.assertEqual(s["title"], "Fix the login page")
        self.assertEqual(s["prompts"], ["fix the login redirect"])

    def test_outside_session_that_edited_inside_is_files_only(self):
        target = os.path.join(self.root, "app", "main.py")
        write_session(self.projects, "out", [
            {"type": "ai-title", "aiTitle": "Secret client work"},
            user(self.other, ts(9), "private client prompt"),
            edit(self.other, ts(9, 5), target),
            edit(self.other, ts(9, 6), os.path.join(self.other, "x.py")),
        ])
        s = self.run_sessions()["out"]
        self.assertEqual(s["scope"], "files-only")
        self.assertNotIn("title", s)
        self.assertNotIn("prompts", s)
        self.assertEqual(s["files_edited"], [os.path.join("app", "main.py")])

    def test_outside_session_with_no_edits_inside_is_absent(self):
        write_session(self.projects, "away", [user(self.other, ts(9), "unrelated")])
        self.assertNotIn("away", self.run_sessions())

    def test_session_outside_window_is_absent(self):
        write_session(self.projects, "old", [user(self.root, ts(9, day=10), "last week")])
        self.assertNotIn("old", self.run_sessions())

    def test_malformed_lines_and_unknown_types_are_skipped(self):
        """A3: a format change in session files must not crash the run."""
        write_session(self.projects, "messy", [
            "{not json", "[1, 2]", {"type": "brand-new-type", "timestamp": ts(9)},
            user(self.root, ts(9, 1), "real prompt"),
        ])
        self.assertEqual(self.run_sessions()["messy"]["prompts"], ["real prompt"])

    def test_noise_prompts_are_dropped(self):
        write_session(self.projects, "noise", [
            user(self.root, ts(9), "<command-name>/clear</command-name>"),
            user(self.root, ts(9, 1), "Base directory for this skill: /x"),
            user(self.root, ts(9, 2), "subagent brief", isSidechain=True),
            user(self.root, ts(9, 3), "the real ask"),
        ])
        self.assertEqual(self.run_sessions()["noise"]["prompts"], ["the real ask"])

    def test_long_gaps_are_not_active_time(self):
        """A3: counting idle gaps would inflate the durations in Other."""
        write_session(self.projects, "gap", [
            user(self.root, ts(9, 0), "a"), user(self.root, ts(9, 20), "bb"),
            user(self.root, ts(14, 0), "ccc"), user(self.root, ts(14, 10), "dddd"),
        ])
        self.assertEqual(self.run_sessions()["gap"]["active_minutes"], 30)


class GitTests(unittest.TestCase):
    """A3: commits by someone else, or missed untracked work, make Yesterday wrong."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.repo = os.path.join(self.root, "svc")
        os.makedirs(self.repo)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Me Dev")
        self.git("config", "user.email", "me@example.com")
        self.commit("mine: ABC-12 add retry", "Me Dev <me@example.com>")
        self.commit("theirs", "Other Person <other@example.com>")
        with open(os.path.join(self.repo, "notes.txt"), "w") as f:
            f.write("wip")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, env=None):
        subprocess.run(["git", "-C", self.repo, *args], check=True, capture_output=True,
                       env={**os.environ, **(env or {})})

    def commit(self, msg, author):
        self.git("commit", "-q", "--allow-empty", "-m", msg, f"--author={author}")

    def test_author_filter_untracked_and_ticket_ids(self):
        since = dt.datetime.now(UTC) - dt.timedelta(hours=1)
        result = gather.gather(self.root, since=since, projects_dir=os.path.join(self.root, "none"), with_prs=False,
                               log_dir=os.path.join(self.root, "log"))
        repo = result["repos"][0]
        self.assertEqual(repo["path"], "svc")
        self.assertEqual([c["subject"] for c in repo["commits"]], ["mine: ABC-12 add retry"])
        self.assertEqual(repo["dirty"]["untracked"], 1)
        self.assertEqual(result["ticket_ids"], ["ABC-12"])
        self.assertEqual(result["schema_version"], 1)

    def test_explicit_author_overrides_repo_config(self):
        since = dt.datetime.now(UTC) - dt.timedelta(hours=1)
        repo = gather.repo_evidence(self.repo, since, dt.datetime.now(UTC), ["other@example.com"])
        self.assertEqual([c["subject"] for c in repo["commits"]], ["theirs"])


class PrTests(unittest.TestCase):
    def test_missing_gh_is_skipped_not_fatal(self):
        """A3: a machine without gh must still get a stand-up."""
        with mock.patch.object(gather.shutil, "which", return_value=None):
            self.assertTrue(gather.prs_evidence(dt.datetime.now(UTC), [])["status"].startswith("skipped"))


if __name__ == "__main__":
    unittest.main()
