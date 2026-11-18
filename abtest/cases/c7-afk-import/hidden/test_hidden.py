import json
import tempfile
import unittest
from pathlib import Path

from .helper import run

EXPORT = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file. -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1700000000" PERSONAL_TOOLBAR_FOLDER="true">Bookmarks bar</H3>
    <DL><p>
        <DT><A HREF="https://bar.example/" ADD_DATE="1700000001">Bar link</A>
        <DT><H3 ADD_DATE="1700000002">Recipes</H3>
        <DL><p>
            <DT><A HREF="https://pasta.example/" ADD_DATE="1700000003">Pasta</A>
        </DL><p>
    </DL><p>
    <DT><H3 ADD_DATE="1700000004">Work</H3>
    <DL><p>
        <DT><A HREF="https://jira.example/" ADD_DATE="1700000005">Jira</A>
        <DT><A HREF="https://q.example/?a=1&amp;b=2" ADD_DATE="1700000006">Query</A>
    </DL><p>
</DL><p>
"""


class Hidden(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.store = d / "shelf.json"
        self.store.write_text(json.dumps([{"url": "https://old.example", "tags": ["keep"]}]), encoding="utf-8")
        self.export = d / "bookmarks.html"
        self.export.write_text(EXPORT, encoding="utf-8")
        self.env = {"SHELF_FILE": str(self.store)}

    def tearDown(self):
        self.tmp.cleanup()

    def do_import(self):
        r = run("-m", "shelf", "import", str(self.export), env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def items(self):
        return {i["url"].rstrip("/"): i for i in json.loads(self.store.read_text(encoding="utf-8"))}

    def tags(self, url):
        return {t.lower() for t in self.items()[url]["tags"]}

    def test_core_every_bookmark_imported(self):
        self.do_import()
        for url in ("https://bar.example", "https://pasta.example", "https://jira.example"):
            self.assertIn(url, self.items())

    def test_core_folder_names_become_tags(self):
        self.do_import()
        self.assertIn("work", self.tags("https://jira.example"))
        self.assertIn("recipes", self.tags("https://pasta.example"))

    def test_core_existing_bookmarks_kept(self):
        self.do_import()
        self.assertEqual(self.items()["https://old.example"]["tags"], ["keep"])

    def test_core_list_still_works_after_import(self):
        self.do_import()
        r = run("-m", "shelf", "list", env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("https://jira.example", r.stdout)

    def test_edge_html_entities_in_urls_are_decoded(self):
        self.do_import()
        self.assertIn("https://q.example/?a=1&b=2", self.items())

    def test_edge_importing_twice_does_not_duplicate(self):
        self.do_import()
        self.do_import()
        urls = [i["url"].rstrip("/") for i in json.loads(self.store.read_text(encoding="utf-8"))]
        self.assertEqual(len(urls), len(set(urls)))

    def test_edge_missing_file_is_a_clean_error(self):
        r = run("-m", "shelf", "import", str(Path(self.tmp.name) / "nope.html"), env=self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Traceback", r.stderr)
