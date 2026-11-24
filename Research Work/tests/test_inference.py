"""Public inference-path tests: parity with frozen predictions and safe defaults."""
from __future__ import annotations

import math
import unittest

import support
from inference import classify_english, classify_malayalam, load_artifact
from p2_common import align_predictions


class TestFrozenParity(unittest.TestCase):
    CASES = (
        ("d1", "d1_malayalam_test.csv",
         "d1_malayalam_linear_svm_test_predictions.csv", support.D1_LABELS,
         classify_malayalam),
        ("d2", "d2_test.csv", "d2_logreg_test_predictions.csv",
         support.D2_LABELS, classify_english),
    )

    def test_every_frozen_row_is_reproduced(self):
        for task, split_name, pred_name, labels, classify in self.CASES:
            split = support.split(split_name)
            aligned = align_predictions(support.prediction(pred_name), split,
                                        pred_name, labels)
            mismatches = []
            for message, expected in zip(split["message"], aligned["prediction"]):
                got = classify(message)["label"]
                if got != expected:
                    mismatches.append((got, expected))
            with self.subTest(task=task):
                self.assertEqual(mismatches, [])
                self.assertEqual(len(aligned), len(split))

    def test_classify_matches_batch_pipeline(self):
        split = support.split("d1_malayalam_test.csv").head(25)
        batch = [str(v) for v in load_artifact("d1")["pipeline"].predict(
            split["text"])]
        single = [classify_malayalam(m)["label"] for m in split["message"]]
        self.assertEqual(batch, single)


class TestResultPayload(unittest.TestCase):
    def test_d1_payload(self):
        row = support.split("d1_malayalam_test.csv").iloc[0]
        result = classify_malayalam(row["message"])
        self.assertEqual(result["task"], "d1")
        self.assertIn(result["display_label"], {"Ham", "Spam"})
        self.assertIsNotNone(result["decision_value"])
        self.assertTrue(math.isfinite(result["decision_value"]))
        self.assertEqual(result["input_characters"], len(row["message"]))
        self.assertEqual(result["clean_text"], row["text"])

    def test_d2_scores_are_ordered_and_normalised(self):
        row = support.split("d2_test.csv").iloc[0]
        result = classify_english(row["message"])
        self.assertEqual(result["task"], "d2")
        self.assertEqual(list(result["scores"]), ["Ham", "Spam", "Smishing"])
        self.assertAlmostEqual(sum(result["scores"].values()), 1.0, places=9)
        best = max(result["scores"], key=result["scores"].get)
        self.assertEqual(best, result["display_label"])

    def test_unicode_input_is_accepted(self):
        result = classify_malayalam("ഇന്ന് വൈകുന്നേരം യോഗം ഉണ്ടോ?")
        self.assertEqual(result["label"], "Ham")
        self.assertGreater(result["input_characters"], 0)


class TestGuardsThroughPublicApi(unittest.TestCase):
    def test_empty_and_whitespace_rejected(self):
        for classify in (classify_malayalam, classify_english):
            for value in (None, "", "   "):
                with self.subTest(classify=classify.__name__, value=value):
                    with self.assertRaises(ValueError):
                        classify(value)

    def test_wrong_dataset_model_is_not_applied(self):
        with self.assertRaises(ValueError):
            classify_malayalam("Your parcel is waiting, call now")
        with self.assertRaises(ValueError):
            classify_english("നിങ്ങളുടെ പാഴ്സൽ വന്നിട്ടുണ്ട്")

    def test_extremely_long_input_rejected_before_prediction(self):
        text = "a" * 50_000
        with self.assertRaises(ValueError):
            classify_english(text)

    def test_repeated_character_input_is_handled(self):
        result = classify_english("a" * 5000)
        self.assertIn(result["label"], {"ham", "spam", "smishing"})


if __name__ == "__main__":
    unittest.main()
