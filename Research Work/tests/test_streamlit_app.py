#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget-level tests for the Streamlit prototype.

These exercise the real application script and its widget tree through
``streamlit.testing.v1.AppTest``: page selection, form submission, warnings,
error display and the research dashboard. They complement the unit tests in
``test_inference.py`` by checking what a user actually sees and can act on.

No network, no browser download, no deployment, and no file written by the app.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

TESTS = Path(__file__).resolve().parent
PROTOTYPE = TESTS.parent / "prototype"
APP = PROTOTYPE / "app.py"
if str(PROTOTYPE) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE))

import inference  # noqa: E402

MALAYALAM_HAM = "ഇന്ന് വൈകുന്നേരം യോഗം ഉണ്ടോ? വരണം."
MALAYALAM_SPAM = (
    "അഭിനന്ദനങ്ങൾ! നിങ്ങൾ 25,000 രൂപ സമ്മാനം നേടി. "
    "ക്ലെയിം ചെയ്യാൻ ഈ നമ്പറിൽ വിളിക്കുക: 9876543210"
)
LATIN_HAM = "Your parcel could not be delivered. Call this number to reschedule."
LATIN_MIXED = "നിങ്ങൾ ഇപ്പോൾ വിളിക്കുക call this number now"


class StreamlitAppTests(unittest.TestCase):
    def open(self, view: str | None = None, text: str | None = None,
             submit: bool = False) -> AppTest:
        at = AppTest.from_file(str(APP), default_timeout=120)
        at.run()
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        if view is not None:
            at.radio[0].set_value(view)
            at.run()
            self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        if text is not None:
            at.text_area[0].set_value(text)
        if submit:
            at.button[0].click()
        if text is not None or submit:
            at.run()
        return at

    @staticmethod
    def cards(at: AppTest) -> list[str]:
        return [m.value for m in at.markdown
                if 'class="result-card' in m.value]

    @staticmethod
    def warnings(at: AppTest) -> list[str]:
        return [w.value for w in at.warning]

    @staticmethod
    def errors(at: AppTest) -> list[str]:
        return [e.value for e in at.error]

    # ----- Dataset 1 -------------------------------------------------------

    def test_d1_page_loads(self):
        at = self.open()
        self.assertIn("Malayalam SMS text", [t.label for t in at.text_area])
        body = " ".join(m.value for m in at.markdown)
        self.assertIn("SMS Classification Research Prototype", body)
        self.assertIn("Linear SVM", body)
        self.assertIn("0.9650", body)
        self.assertIn("0.5378", body)

    def test_d1_malayalam_prediction_renders(self):
        at = self.open(text=MALAYALAM_SPAM, submit=True)
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        cards = self.cards(at)
        self.assertEqual(len(cards), 1, cards)
        self.assertIn('class="result-card', cards[0])
        self.assertTrue(
            any(f'>{label}<' in cards[0] for label in ("Ham", "Spam")), cards[0]
        )
        self.assertEqual(self.warnings(at), [])
        self.assertEqual(self.errors(at), [])

    def test_d1_rejects_latin_only_input(self):
        at = self.open(text=LATIN_HAM, submit=True)
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        self.assertEqual(self.cards(at), [])
        self.assertTrue(any("Malayalam Unicode" in w for w in self.warnings(at)),
                        self.warnings(at))

    def test_d1_empty_input_warns(self):
        at = self.open(text="", submit=True)
        self.assertEqual(self.cards(at), [])
        self.assertTrue(any("Enter a message" in w for w in self.warnings(at)),
                        self.warnings(at))

    def test_d1_widget_caps_oversized_input_at_5000(self):
        # The text area enforces max_chars, so a user cannot submit 5,001
        # characters through the UI. The library-level rejection of 5,001 is
        # covered by test_inference.py; here we pin the widget cap itself.
        at = self.open(text="ക" * 5001, submit=True)
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        self.assertEqual(len(at.text_area[0].value), 5000)
        self.assertEqual(self.errors(at), [])
        self.assertEqual(len(self.cards(at)), 1, self.errors(at))

    def test_d1_control_characters_do_not_crash(self):
        at = self.open(text="\x00\x01" + MALAYALAM_HAM + "\x02", submit=True)
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        self.assertEqual(len(self.cards(at)), 1, self.errors(at))

    # ----- Dataset 2 -------------------------------------------------------

    def test_d2_page_and_prediction_render(self):
        at = self.open(view="English SMS", text=LATIN_HAM, submit=True)
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        self.assertIn("English / Latin-script SMS text",
                      [t.label for t in at.text_area])
        cards = self.cards(at)
        self.assertEqual(len(cards), 1, cards)
        self.assertTrue(
            any(f'>{label}<' in cards[0] for label in ("Ham", "Spam", "Smishing")),
            cards[0],
        )
        self.assertEqual(len(at.dataframe), 1)

    def test_d2_rejects_malayalam_only_input(self):
        at = self.open(view="English SMS", text=MALAYALAM_HAM, submit=True)
        self.assertEqual(self.cards(at), [])
        self.assertTrue(any("Latin-script" in w for w in self.warnings(at)),
                        self.warnings(at))

    def test_d2_warns_on_mixed_script_but_still_predicts(self):
        at = self.open(view="English SMS", text=LATIN_MIXED, submit=True)
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        self.assertTrue(any("Malayalam Unicode was detected" in w
                            for w in self.warnings(at)), self.warnings(at))
        self.assertEqual(len(self.cards(at)), 1, self.errors(at))

    # ----- Dashboard -------------------------------------------------------

    def test_dashboard_renders_all_sections(self):
        at = self.open(view="Research dashboard")
        self.assertEqual(len(at.exception), 0, [e.value for e in at.exception])
        labels = [m.label for m in at.metric]
        self.assertIn("D1 selected model", labels)
        self.assertIn("D1 random Macro-F1", labels)
        self.assertIn("D2 selected model", labels)
        body = " ".join(m.value for m in at.markdown)
        self.assertIn("Block-held-out evaluation", body)
        self.assertIn("Consolidated comparison", body)
        self.assertTrue(len(at.dataframe) >= 1)

    # ----- Failure display -------------------------------------------------

    def test_missing_model_shows_error_instead_of_blank_page(self):
        original = inference.load_artifact

        def broken(task):
            raise FileNotFoundError("simulated missing artifact")

        inference.load_artifact = broken
        try:
            at = self.open()
            self.assertEqual(len(at.exception), 0,
                             [e.value for e in at.exception])
            self.assertTrue(any("could not be loaded" in e
                                for e in self.errors(at)), self.errors(at))
            self.assertIn("Malayalam SMS text",
                          [t.label for t in at.text_area])
        finally:
            inference.load_artifact = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
