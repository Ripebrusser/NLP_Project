"""Unicode cleaning, script detection and prototype input-guard tests."""
from __future__ import annotations

import re
import unittest

import support
from inference import MAX_INPUT_CHARS, clean_text as proto_clean
from inference import has_latin, has_malayalam, validate_input
from p2_common import clean_text

MAL = re.compile(r"[\u0D00-\u0D7F]")


class TestCleanText(unittest.TestCase):
    def test_malayalam_text_is_preserved(self):
        text = "ഇന്ന് വൈകുന്നേരം യോഗം ഉണ്ടോ?"
        self.assertEqual(clean_text(text), text)

    def test_malayalam_combining_marks_survive(self):
        text = "കോട്ടയം കെട്ടിടം"
        cleaned = clean_text(text)
        self.assertEqual(cleaned, text)
        self.assertEqual(len(cleaned), len(text))
        self.assertTrue(all(MAL.match(ch) or ch == " " for ch in cleaned))

    def test_zero_width_and_bom_removed(self):
        self.assertEqual(clean_text("ഇന്ന്\u200b യോഗം"), "ഇന്ന് യോഗം")
        self.assertEqual(clean_text("\ufeffHello"), "Hello")
        self.assertEqual(clean_text("a\u200cb\u200dc"), "abc")

    def test_non_breaking_space_and_whitespace_collapse(self):
        self.assertEqual(clean_text("a\u00a0b"), "a b")
        self.assertEqual(clean_text("a\t\n  b"), "a b")
        self.assertEqual(clean_text("   "), "")

    def test_control_characters_become_space(self):
        self.assertEqual(clean_text("a\u0001b"), "a b")
        self.assertEqual(clean_text("\u0000\u0002"), "")

    def test_nfkc_normalisation(self):
        self.assertEqual(clean_text("ﬁle"), "file")
        self.assertEqual(clean_text("ＡＢＣ"), "ABC")

    def test_replacement_character_is_kept(self):
        # Documented: U+FFFD is not silently deleted; it stays visible.
        self.assertEqual(clean_text("a\ufffdb"), "a\ufffdb")

    def test_no_transliteration(self):
        text = "വിളിക്കൂ 9876543210"
        cleaned = clean_text(text)
        self.assertIn("വിളിക്കൂ", cleaned)
        self.assertIn("9876543210", cleaned)
        self.assertEqual(set(MAL.findall(text)), set(MAL.findall(cleaned)))

    def test_idempotent(self):
        for text in ("  ഇന്ന്\u200b   യോഗം  ", "a\u00a0 b\u0001c", "ﬁle 123",
                     "മലയാളം + English"):
            once = clean_text(text)
            self.assertEqual(clean_text(once), once)

    def test_prototype_and_training_cleaning_agree_on_every_frozen_row(self):
        files = ("d1_malayalam_train.csv", "d1_malayalam_val.csv",
                 "d1_malayalam_test.csv", "d2_train.csv", "d2_val.csv",
                 "d2_test.csv")
        for name in files:
            frame = support.split(name)
            with self.subTest(file=name):
                for message in frame["message"]:
                    self.assertEqual(proto_clean(message), clean_text(message))

    def test_training_text_column_equals_cleaned_message(self):
        # Detects preprocessing drift between p2_extract output and the cleaner.
        files = ("d1_malayalam_train.csv", "d1_malayalam_val.csv",
                 "d1_malayalam_test.csv", "d2_train.csv", "d2_val.csv",
                 "d2_test.csv")
        for name in files:
            frame = support.split(name)
            with self.subTest(file=name):
                expected = frame["message"].map(clean_text)
                self.assertTrue((expected == frame["text"]).all())


class TestScriptDetection(unittest.TestCase):
    def test_malayalam_and_latin_detection(self):
        self.assertTrue(has_malayalam("ഇന്ന് യോഗം"))
        self.assertFalse(has_malayalam("Hello"))
        self.assertTrue(has_latin("Hello 123"))
        self.assertFalse(has_latin("മലയാളം മാത്രം"))
        self.assertTrue(has_malayalam("മലയാളം English"))
        self.assertTrue(has_latin("മലയാളം English"))

    def test_digits_only_is_neither_script(self):
        self.assertFalse(has_malayalam("12345"))
        self.assertFalse(has_latin("12345"))

    def test_script_detection_is_not_language_identification(self):
        # Romanised Malayalam is Latin script; the detector must say so.
        self.assertTrue(has_latin("njan innu varam"))
        self.assertFalse(has_malayalam("njan innu varam"))


class TestInputValidation(unittest.TestCase):
    def test_empty_inputs_rejected(self):
        for value in (None, "", "   ", "\t\n"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "empty"):
                    validate_input(value, "d2")

    def test_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError, "bytes"):
            validate_input(b"hello", "d2")

    def test_length_limit(self):
        self.assertEqual(len(validate_input("a" * MAX_INPUT_CHARS, "d2")),
                         MAX_INPUT_CHARS)
        with self.assertRaisesRegex(ValueError, "limit"):
            validate_input("a" * (MAX_INPUT_CHARS + 1), "d2")

    def test_control_only_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "no usable characters"):
            validate_input("\u0001\u0002", "d2")

    def test_wrong_script_rejected_per_task(self):
        with self.assertRaisesRegex(ValueError, "Malayalam"):
            validate_input("hello there", "d1")
        with self.assertRaisesRegex(ValueError, "Latin"):
            validate_input("മലയാളം മാത്രം", "d2")

    def test_valid_input_returned_unchanged(self):
        text = "  ഇന്ന് യോഗം  "
        self.assertEqual(validate_input(text, "d1"), text)


if __name__ == "__main__":
    unittest.main()
