import unittest

from notes import store


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.conn = store.connect(":memory:")

    def test_list_is_per_owner(self):
        store.add_note(self.conn, "ana", "groceries")
        store.add_note(self.conn, "ben", "taxes")
        self.assertEqual([n["title"] for n in store.list_notes(self.conn, "ana")], ["groceries"])

    def test_archived_hidden_unless_asked(self):
        note = store.add_note(self.conn, "ana", "old")
        store.archive_note(self.conn, "ana", note)
        self.assertEqual(store.list_notes(self.conn, "ana"), [])
        self.assertEqual(len(store.list_notes(self.conn, "ana", archived=True)), 1)

    def test_cannot_archive_someone_elses_note(self):
        note = store.add_note(self.conn, "ana", "mine")
        self.assertFalse(store.archive_note(self.conn, "ben", note))


if __name__ == "__main__":
    unittest.main()
