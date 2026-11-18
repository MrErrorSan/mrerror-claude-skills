"""Tests for the upstream watch tools in upstream/superpowers/tools (design §8.1)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from .helpers import write

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "upstream" / "superpowers"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, UPSTREAM / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


provenance = _load("provenance")

WORDS = ("one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty\n")


class ReadSourcesTest(unittest.TestCase):
    def test_read_sources_finds_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skills = repo / "plugins" / "anvil" / "skills"
            write(skills / "a" / "SKILL.md",
                  "---\nname: a\n---\n"
                  "<!-- adapted from superpowers@7.0.2: skills/a/SKILL.md -->\n"
                  "<!-- adapted from superpowers@7.0.2: skills/b/ref.md -->\n# A\n",
                  crlf=True)
            write(skills / "c" / "ref.md",
                  "<!-- adapted from superpowers@7.0.2: skills/c/x.md, skills/c/y.ts -->\n")
            write(repo / "plugins" / "anvil" / "hooks" / "run-hook.cmd",
                  "@echo off\nREM Adapted from superpowers@7.0.2: hooks/run-hook.cmd (comments changed only).\n")
            write(repo / "plugins" / "anvil" / "hooks" / "start",
                  "#!/usr/bin/env bash\n# adapted from superpowers@7.0.2: hooks/session-start\n")
            write(skills / "d" / "SKILL.md",
                  "Prose that mentions `<!-- adapted from superpowers@<v>: skills/<path> -->`.\n")
            # A copied file with no comment, mapped by hand.
            write(skills / "e" / "script.sh", "#!/usr/bin/env bash\necho hi\n")
            write(repo / "upstream" / "superpowers" / "manual-sources.json",
                  json.dumps({"plugins/anvil/skills/e/script.sh": ["skills/e/script.sh"]}))

            found = provenance.read_sources(repo)

        self.assertEqual(found, {
            "plugins/anvil/skills/a/SKILL.md": ["skills/a/SKILL.md", "skills/b/ref.md"],
            "plugins/anvil/skills/c/ref.md": ["skills/c/x.md", "skills/c/y.ts"],
            "plugins/anvil/hooks/run-hook.cmd": ["hooks/run-hook.cmd"],
            "plugins/anvil/hooks/start": ["hooks/session-start"],
            "plugins/anvil/skills/e/script.sh": ["skills/e/script.sh"],
        })

    def test_classify_labels(self):
        src = "# Title\n" + WORDS * 3
        dst_same = "<!-- adapted from superpowers@7.0.2: skills/x/SKILL.md -->\n" + src
        self.assertEqual(provenance.classify(src, dst_same.replace("\n", "\r\n")), "verbatim")
        self.assertEqual(provenance.classify(src, src.replace("seven", "SEVEN", 1)),
                         "lightly edited")
        self.assertEqual(provenance.classify(src, "Something else entirely.\n"), "adapted")


class RepoProvenanceTest(unittest.TestCase):
    def test_source_map_matches_comments(self):
        source_map = json.loads((UPSTREAM / "source-map.json").read_text(encoding="utf-8"))
        self.assertEqual(source_map, provenance.read_sources(ROOT))

    def test_provenance_lists_every_mapped_file(self):
        source_map = json.loads((UPSTREAM / "source-map.json").read_text(encoding="utf-8"))
        report = (UPSTREAM / "provenance.md").read_text(encoding="utf-8")
        self.assertTrue(source_map)
        for anvil_path, sources in source_map.items():
            self.assertIn(f"`{anvil_path}`", report)
            for src in sources:
                self.assertIn(f"`{src}`", report)


if __name__ == "__main__":
    unittest.main()
