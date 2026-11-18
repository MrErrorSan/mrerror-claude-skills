"""Hidden tests for tags on notes, through the HTTP API.

Interface from the user brief: POST /notes accepts "tags": [...]; GET /notes returns each
note with "tags"; GET /notes?tag=<t> filters; PUT /notes/<id>/tags {"tags": [...]} replaces.
"""
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer


class Hidden(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from notes import api, store
        cls.tmp = tempfile.TemporaryDirectory()
        db = os.path.join(cls.tmp.name, "t.db")
        ready = threading.Event()

        def serve():
            api.Handler.conn = store.connect(db)   # created in the serving thread
            cls.srv = HTTPServer(("127.0.0.1", 0), api.Handler)
            ready.set()
            cls.srv.serve_forever()

        threading.Thread(target=serve, daemon=True).start()
        ready.wait(10)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def call(self, method, path, user="ana", body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"X-User": user, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read() or b"null")
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw or b"null")
            except ValueError:
                return e.code, raw.decode(errors="replace")

    def add(self, title, tags=None, user="ana"):
        body = {"title": title}
        if tags is not None:
            body["tags"] = tags
        status, payload = self.call("POST", "/notes", user, body)
        self.assertEqual(status, 201, payload)
        return payload["id"]

    def titles(self, path, user="ana"):
        status, payload = self.call("GET", path, user)
        self.assertEqual(status, 200, payload)
        return sorted(n["title"] for n in payload)

    def test_core_create_with_tags_and_list_shows_them(self):
        nid = self.add("c1-standup", ["work", "daily"])
        _, notes = self.call("GET", "/notes")
        note = next(n for n in notes if n["id"] == nid)
        self.assertEqual(sorted(note["tags"]), ["daily", "work"])

    def test_core_note_without_tags_has_empty_list(self):
        nid = self.add("c2-plain")
        _, notes = self.call("GET", "/notes")
        self.assertEqual(next(n for n in notes if n["id"] == nid)["tags"], [])

    def test_core_filter_by_tag(self):
        self.add("c3-a", ["c3tag"])
        self.add("c3-b", ["other"])
        self.assertEqual(self.titles("/notes?tag=c3tag"), ["c3-a"])

    def test_core_filter_is_per_owner(self):
        self.add("c4-ana", ["c4tag"])
        self.add("c4-ben", ["c4tag"], user="ben")
        self.assertEqual(self.titles("/notes?tag=c4tag"), ["c4-ana"])

    def test_edge_unknown_tag_returns_empty_list(self):
        self.assertEqual(self.titles("/notes?tag=no-such-tag-zz"), [])

    def test_edge_filter_combines_with_archived(self):
        live = self.add("e2-live", ["e2tag"])
        old = self.add("e2-old", ["e2tag"])
        self.call("POST", f"/notes/{old}/archive")
        self.assertEqual(self.titles("/notes?tag=e2tag"), ["e2-live"])
        self.assertEqual(self.titles("/notes?tag=e2tag&archived=1"), ["e2-old"])

    def test_brief_tags_are_case_insensitive(self):
        self.add("b1-mixed", ["B1Tag"])
        self.assertEqual(self.titles("/notes?tag=b1tag"), ["b1-mixed"])

    def test_brief_replace_tags_on_existing_note(self):
        nid = self.add("b2-note", ["b2old"])
        status, _ = self.call("PUT", f"/notes/{nid}/tags", body={"tags": ["b2new"]})
        self.assertIn(status, (200, 204))
        self.assertEqual(self.titles("/notes?tag=b2new"), ["b2-note"])
        self.assertEqual(self.titles("/notes?tag=b2old"), [])

    def test_brief_more_than_ten_tags_rejected(self):
        status, _ = self.call("POST", "/notes", body={"title": "b3", "tags": [f"t{i}" for i in range(11)]})
        self.assertEqual(status, 400)
