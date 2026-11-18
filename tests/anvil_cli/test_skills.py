"""Lint for the Anvil skills and hook scripts (plan T13, design §5)."""
import re
import unittest
from pathlib import Path

from anvil_cli import cli

PLUGIN = Path(__file__).resolve().parents[2] / "plugins" / "anvil"
SKILLS = sorted(p.parent for p in (PLUGIN / "skills").glob("*/SKILL.md"))
NOT_ADAPTED = {"anvil", "afk", "ticket-update", "ui-mockup", "ux-audit", "cross-model"}
BANNED = (
    (r"\bMUST\b", "MUST"),
    (r"\bIMPORTANT\b", "IMPORTANT"),
    (r"\bEXTREMELY\b", "EXTREMELY"),
    (r"\bABSOLUTELY\b", "ABSOLUTELY"),
    (r"\bIron Laws?\b", "Iron Law"),
    (r"superpowers:", "a Superpowers skill invocation"),
    (r"TodoWrite", "TodoWrite"),
    (r"\bTask(Create|Update|List|Get)\b", "a Task* todo tool"),
    (r"\bArtifact\b", "Artifact"),
)
SUB_INLINE = re.compile(r"`(?:ANVIL_RERUN=1 )?anvil ([a-z][\w-]*)")
SUB_FENCED = re.compile(r"^\s*(?:\$\s*)?(?:ANVIL_RERUN=1\s+)?anvil ([a-z][\w-]*)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)[^)]*\)")
INLINE_CODE = re.compile(r"`[^`]*`")
FILE_REF = re.compile(r"`((?:references|scripts|prompts)/[\w.-][\w./-]*)`")
FENCE = re.compile(r"^\s*(```|~~~)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def skill_files(d: Path) -> list:
    files = [d / "SKILL.md"]
    for sub in ("references", "prompts"):
        files += sorted((d / sub).rglob("*.md"))
    return files


# (base directory for file references, file) for every Markdown file linted.
FILES = [(d, f) for d in SKILLS for f in skill_files(d)]
FILES += [(PLUGIN, f) for f in sorted((PLUGIN / "references").glob("*.md"))]


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1].strip()
    return value


def frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields, key = {}, None
    for line in lines[1:]:
        if line.strip() == "---":
            return {k: unquote(re.sub(r"^[>|][-+]?\s*", "", v)) for k, v in fields.items()}
        m = re.match(r"([A-Za-z][\w-]*):\s*(.*)", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2)
        elif key and line[:1].isspace():
            fields[key] += " " + line.strip()
    return {}


def lines_with_fence(text: str):
    """Yield (line number, line, inside a fenced block) for each non-fence line."""
    fenced = False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
        else:
            yield i, line, fenced


def rel(path: Path) -> str:
    return path.relative_to(PLUGIN).as_posix()


class TestSkills(unittest.TestCase):
    def test_skills_found(self):
        self.assertTrue(SKILLS, f"no skills under {PLUGIN / 'skills'}")

    def test_frontmatter(self):
        for d in SKILLS:
            f = d / "SKILL.md"
            with self.subTest(file=rel(f)):
                fm = frontmatter(read(f))
                self.assertEqual(fm.get("name"), d.name, f"{rel(f)}: frontmatter name must equal the directory")
                self.assertTrue(fm.get("description"), f"{rel(f)}: frontmatter has no description")

    def test_size(self):
        for d in SKILLS:
            f = d / "SKILL.md"
            with self.subTest(file=rel(f)):
                n = len(read(f))
                self.assertLess(n, 20000, f"{rel(f)}: {n} characters, limit is 20,000")

    def test_banned_wording(self):
        for _, f in FILES:
            for i, line in enumerate(read(f).splitlines(), 1):
                for pattern, label in BANNED:
                    if re.search(pattern, line):
                        with self.subTest(file=rel(f), line=i, banned=label):
                            self.fail(f"{rel(f)}:{i}: {label}: {line.strip()}")

    def test_cli_subcommands_exist(self):
        for _, f in FILES:
            for i, line, fenced in lines_with_fence(read(f)):
                subs = SUB_INLINE.findall(line)
                if fenced:
                    subs += SUB_FENCED.findall(line)
                for sub in subs:
                    with self.subTest(file=rel(f), line=i, sub=sub):
                        self.assertIn(sub, cli.COMMANDS, f"{rel(f)}:{i}: `anvil {sub}` is not a CLI subcommand")

    def test_relative_links_resolve(self):
        for _, f in FILES:
            for i, line, fenced in lines_with_fence(read(f)):
                if fenced:
                    continue
                for target in LINK.findall(INLINE_CODE.sub("", line)):
                    if re.match(r"[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                        continue
                    path = target.split("#", 1)[0]
                    with self.subTest(file=rel(f), line=i, link=target):
                        self.assertTrue((f.parent / path).exists(), f"{rel(f)}:{i}: link {target!r} does not resolve")

    def test_file_references_exist(self):
        for base, f in FILES:
            for i, line in enumerate(read(f).splitlines(), 1):
                for ref in FILE_REF.findall(line):
                    with self.subTest(file=rel(f), line=i, ref=ref):
                        self.assertTrue((base / ref).exists(), f"{rel(f)}:{i}: `{ref}` not found under {rel(base) or '.'}/")

    def test_adapted_source_line(self):
        for d in SKILLS:
            if d.name in NOT_ADAPTED:
                continue
            with self.subTest(skill=d.name):
                found = any("<!-- adapted from superpowers@" in read(f) for f in d.rglob("*.md"))
                self.assertTrue(found, f"{rel(d)}/: no '<!-- adapted from superpowers@' line in any file")


class TestHookScripts(unittest.TestCase):
    def test_hooks_are_lf(self):
        hooks = sorted(p for p in (PLUGIN / "hooks").iterdir() if p.is_file())
        self.assertTrue(hooks, "no files in plugins/anvil/hooks")
        for f in hooks:
            with self.subTest(file=rel(f)):
                self.assertNotIn(b"\r", f.read_bytes(), f"{rel(f)}: has CR line endings; hook scripts stay LF")


if __name__ == "__main__":
    unittest.main()
