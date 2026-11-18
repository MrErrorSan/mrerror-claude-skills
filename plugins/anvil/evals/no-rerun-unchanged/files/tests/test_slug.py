import unittest

from slugkit.slug import slugify


class SlugifyTest(unittest.TestCase):
    def test_punctuation_becomes_single_hyphens(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_accents_are_dropped(self):
        self.assertEqual(slugify("Café déjà vu"), "cafe-deja-vu")

    def test_cut_at_a_word_boundary(self):
        self.assertEqual(slugify("one two three", max_length=8), "one-two")

    def test_empty_title(self):
        self.assertEqual(slugify("!!!"), "")


if __name__ == "__main__":
    unittest.main()
