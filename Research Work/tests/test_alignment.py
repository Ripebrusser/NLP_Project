"""Prediction/split alignment validation tests (missing, extra, duplicate, mixed)."""
from __future__ import annotations

import unittest

import pandas as pd

import support
from p2_common import align_predictions


def frame(ids, labels, predictions, groups=None):
    data = {"record_id": ids, "label": labels, "prediction": predictions}
    if groups is not None:
        data["group_id"] = groups
    return pd.DataFrame(data)


class TestAlignPredictions(unittest.TestCase):
    def setUp(self):
        self.split = frame(
            ["D1-00000", "D1-00001", "D1-00002"],
            ["Ham", "Spam", "Ham"],
            ["Ham", "Ham", "Ham"],
            ["G0", "G1", "G2"],
        )

    def test_reorders_by_record_id_not_position(self):
        pred = frame(
            ["D1-00002", "D1-00000", "D1-00001"],
            ["Ham", "Ham", "Spam"],
            ["Spam", "Spam", "Ham"],
            ["G2", "G0", "G1"],
        )
        aligned = align_predictions(pred, self.split, "unit", support.D1_LABELS)
        self.assertEqual(list(aligned["record_id"]),
                         ["D1-00000", "D1-00001", "D1-00002"])
        self.assertEqual(list(aligned["prediction"]), ["Spam", "Ham", "Spam"])
        self.assertEqual(list(aligned["group_id"]), ["G0", "G1", "G2"])

    def test_duplicate_prediction_id_is_rejected(self):
        pred = frame(
            ["D1-00000", "D1-00000", "D1-00001", "D1-00002"],
            ["Ham", "Ham", "Spam", "Ham"],
            ["Ham", "Spam", "Ham", "Ham"],
        )
        with self.assertRaisesRegex(ValueError, "duplicate record_id"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_missing_record_is_rejected(self):
        pred = frame(["D1-00000", "D1-00001"], ["Ham", "Spam"], ["Ham", "Ham"])
        with self.assertRaisesRegex(ValueError, "record mismatch"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_extra_record_is_rejected(self):
        pred = frame(["D1-00000", "D1-00001", "D1-00002", "D1-99999"],
                     ["Ham", "Spam", "Ham", "Ham"],
                     ["Ham", "Ham", "Ham", "Ham"])
        with self.assertRaisesRegex(ValueError, "record mismatch"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_label_disagreement_is_rejected(self):
        pred = frame(["D1-00000", "D1-00001", "D1-00002"],
                     ["Ham", "Ham", "Ham"],
                     ["Ham", "Ham", "Ham"])
        with self.assertRaisesRegex(ValueError, "labels disagree"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_unexpected_class_is_rejected(self):
        pred = frame(["D1-00000", "D1-00001", "D1-00002"],
                     ["Ham", "Spam", "Ham"],
                     ["Ham", "Phish", "Ham"])
        with self.assertRaisesRegex(ValueError, "unexpected labels"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_group_disagreement_is_rejected(self):
        pred = frame(["D1-00000", "D1-00001", "D1-00002"],
                     ["Ham", "Spam", "Ham"],
                     ["Ham", "Ham", "Ham"],
                     ["G0", "G1", "WRONG"])
        with self.assertRaisesRegex(ValueError, "group_id disagrees"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_null_record_id_is_rejected(self):
        pred = frame(["D1-00000", None, "D1-00002"],
                     ["Ham", "Spam", "Ham"],
                     ["Ham", "Ham", "Ham"])
        with self.assertRaisesRegex(ValueError, "null record_id"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_missing_column_is_rejected(self):
        pred = frame(["D1-00000", "D1-00001", "D1-00002"],
                     ["Ham", "Spam", "Ham"], ["Ham", "Ham", "Ham"]).drop(
            columns=["prediction"])
        with self.assertRaisesRegex(ValueError, "missing column"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_dataset_mixup_is_rejected(self):
        # D2 predictions must never be aligned to the D1 split.
        pred = frame(["D2-00000", "D2-00001", "D2-00002"],
                     ["ham", "spam", "ham"], ["ham", "ham", "ham"])
        with self.assertRaisesRegex(ValueError, "record mismatch"):
            align_predictions(pred, self.split, "unit", support.D1_LABELS)

    def test_frozen_files_align_cleanly(self):
        pairs = [
            ("d1_malayalam_test.csv", "d1_malayalam_logreg_test_predictions.csv",
             support.D1_LABELS, 299),
            ("d1_malayalam_test.csv", "d1_malayalam_linear_svm_test_predictions.csv",
             support.D1_LABELS, 299),
            ("d1_malayalam_test.csv", "muril_random_seed42_predictions.csv",
             support.D1_LABELS, 299),
            ("d2_test.csv", "d2_logreg_test_predictions.csv",
             support.D2_LABELS, 883),
            ("d2_test.csv", "d2_linear_svm_test_predictions.csv",
             support.D2_LABELS, 883),
        ]
        for split_name, pred_name, labels, expected in pairs:
            with self.subTest(pred=pred_name):
                aligned = align_predictions(support.prediction(pred_name),
                                            support.split(split_name),
                                            pred_name, labels)
                self.assertEqual(len(aligned), expected)
                self.assertTrue(aligned["record_id"].is_unique)


if __name__ == "__main__":
    unittest.main()
