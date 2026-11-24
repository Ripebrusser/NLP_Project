"""Saved model artifact loading, hashing and prediction-parity tests."""
from __future__ import annotations

import hashlib
import unittest

import support
from inference import load_artifact, model_summary
from p2_common import align_predictions

MODEL_FILES = {
    "d1": "d1_malayalam_linear_svm.joblib",
    "d2": "d2_logreg.joblib",
}


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestModelHashes(unittest.TestCase):
    def test_all_four_model_hashes_match_manifest(self):
        manifest = support.model_manifest()["models"]
        self.assertEqual(set(manifest), {
            "d1_malayalam_linear_svm.joblib", "d1_malayalam_logreg.joblib",
            "d2_linear_svm.joblib", "d2_logreg.joblib"})
        for filename, expected in manifest.items():
            with self.subTest(model=filename):
                self.assertEqual(sha256(support.MODELS / filename), expected)


class TestPipelineStructure(unittest.TestCase):
    def test_artifacts_load_with_expected_keys(self):
        for task in ("d1", "d2"):
            artifact = load_artifact(task)
            self.assertLessEqual({"pipeline", "config", "C", "labels"},
                                 set(artifact))
            self.assertIn("tfidf", artifact["pipeline"].named_steps)
            self.assertIn("clf", artifact["pipeline"].named_steps)

    def test_vectorizer_configuration(self):
        for task in ("d1", "d2"):
            tfidf = load_artifact(task)["pipeline"].named_steps["tfidf"]
            params = tfidf.get_params()
            with self.subTest(task=task):
                self.assertEqual(params["analyzer"], "char_wb")
                self.assertEqual(tuple(params["ngram_range"]), (2, 4))
                self.assertTrue(params["sublinear_tf"])
                self.assertGreaterEqual(params["min_df"], 1)

    def test_regularisation_and_classes(self):
        d1 = load_artifact("d1")
        d2 = load_artifact("d2")
        self.assertAlmostEqual(float(d1["C"]), 0.5)
        self.assertAlmostEqual(float(d2["C"]), 1.0)
        self.assertEqual(list(d1["pipeline"].classes_), ["Ham", "Spam"])
        # sklearn stores classes alphabetically; inference.classify_english
        # re-orders the score map for display, which is checked separately.
        self.assertEqual(list(d2["pipeline"].classes_),
                         ["ham", "smishing", "spam"])

    def test_model_summary(self):
        summary = model_summary("d1")
        self.assertGreater(summary["n_features"], 1000)
        self.assertEqual(summary["classifier"], "LinearSVC")
        self.assertEqual(model_summary("d2")["classifier"], "LogisticRegression")

    def test_unknown_task_is_rejected(self):
        with self.assertRaises(ValueError):
            load_artifact("d3")


class TestPredictionParity(unittest.TestCase):
    CASES = (
        ("d1", "d1_malayalam_test.csv",
         "d1_malayalam_linear_svm_test_predictions.csv", support.D1_LABELS),
        ("d2", "d2_test.csv", "d2_logreg_test_predictions.csv",
         support.D2_LABELS),
    )

    def test_batch_predictions_reproduce_frozen_files(self):
        for task, split_name, pred_name, labels in self.CASES:
            with self.subTest(task=task):
                split = support.split(split_name)
                aligned = align_predictions(support.prediction(pred_name),
                                            split, pred_name, labels)
                pipeline = load_artifact(task)["pipeline"]
                predicted = [str(v) for v in pipeline.predict(split["text"])]
                self.assertEqual(len(predicted), len(aligned))
                mismatches = [(rid, a, b) for rid, a, b in
                              zip(aligned["record_id"], predicted,
                                  aligned["prediction"]) if a != b]
                self.assertEqual(mismatches, [])

    def test_prediction_is_order_independent(self):
        split = support.split("d1_malayalam_test.csv")
        pipeline = load_artifact("d1")["pipeline"]
        forward = [str(v) for v in pipeline.predict(split["text"])]
        shuffled = split.sample(frac=1.0, random_state=3)
        reverse = [str(v) for v in pipeline.predict(shuffled["text"])]
        mapping = dict(zip(shuffled["record_id"], reverse))
        for rid, value in zip(split["record_id"], forward):
            self.assertEqual(value, mapping[rid])


if __name__ == "__main__":
    unittest.main()
