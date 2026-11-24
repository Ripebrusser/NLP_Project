"""Statistical correctness, interval edge cases and paired-direction tests."""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

import support
from p2_final_verification import (
    cp_interval,
    exact_checks,
    metric_codes,
    multiclass_exact_checks,
    wilson_interval,
)
from p2_stats import bootstrap, encode, metrics_from_codes, paired_bootstrap


def codes(values, labels):
    return encode(values, labels)


class TestIntervals(unittest.TestCase):
    def test_clopper_pearson_known_values(self):
        self.assertAlmostEqual(cp_interval(0, 10)[0], 0.0)
        self.assertAlmostEqual(cp_interval(0, 10)[1], 0.30850, delta=1e-4)
        self.assertAlmostEqual(cp_interval(10, 10)[0], 0.69150, delta=1e-4)
        self.assertAlmostEqual(cp_interval(10, 10)[1], 1.0)
        low, high = cp_interval(5, 10)
        self.assertAlmostEqual(low, 0.18709, delta=1e-4)
        self.assertAlmostEqual(high, 0.81291, delta=1e-4)

    def test_intervals_are_ordered_and_bounded(self):
        for k, n in ((0, 5), (1, 7), (3, 3), (17, 40)):
            for low, high in (cp_interval(k, n), wilson_interval(k, n)):
                self.assertLessEqual(0.0, low)
                self.assertLessEqual(low, high)
                self.assertLessEqual(high, 1.0)

    def test_empty_denominator_is_uninformative_not_a_number(self):
        self.assertEqual(cp_interval(0, 0), (0.0, 1.0))
        self.assertEqual(wilson_interval(0, 0), (0.0, 1.0))

    def test_wilson_known_values(self):
        self.assertAlmostEqual(wilson_interval(0, 10)[1], 0.27753, delta=5e-4)
        low, high = wilson_interval(5, 10)
        self.assertAlmostEqual(low, 0.23659, delta=5e-4)
        self.assertAlmostEqual(high, 0.76341, delta=5e-4)
        self.assertAlmostEqual(wilson_interval(10, 10)[1], 1.0)


class TestMetricCodes(unittest.TestCase):
    def test_matches_sklearn_reference(self):
        labels = support.D1_LABELS
        y = ["Ham", "Spam", "Spam", "Ham", "Spam"]
        pred = ["Ham", "Spam", "Ham", "Ham", "Spam"]
        m = metrics_from_codes(codes(y, labels), codes(pred, labels), labels)
        self.assertAlmostEqual(m["accuracy"], accuracy_score(y, pred))
        self.assertAlmostEqual(
            m["macro_f1"], f1_score(y, pred, labels=labels, average="macro")
        )
        self.assertEqual(m["n"], 5)
        self.assertEqual(m["confusion_matrix"], [[2, 0], [1, 2]])

    def test_denominators_for_spam(self):
        labels = support.D1_LABELS
        y = ["Ham", "Spam", "Spam", "Spam"]
        pred = ["Ham", "Spam", "Spam", "Ham"]
        m = metrics_from_codes(codes(y, labels), codes(pred, labels), labels)
        # predicted Spam = 2, of which 2 are correct
        self.assertAlmostEqual(m["spam_precision"], 1.0)
        # 3 true Spam, 2 recovered
        self.assertAlmostEqual(m["spam_recall"], 2 / 3)
        self.assertEqual(m["spam_support"], 3)

    def test_no_predicted_positive_gives_zero_precision(self):
        labels = support.D1_LABELS
        m = metrics_from_codes(codes(["Ham", "Spam"], labels),
                               codes(["Ham", "Ham"], labels), labels)
        self.assertAlmostEqual(m["spam_precision"], 0.0)
        self.assertAlmostEqual(m["spam_recall"], 0.0)
        self.assertAlmostEqual(m["spam_f1"], 0.0)
        # Ham: P=1.0, R=0.5 -> F1=2/3; Spam F1=0; macro-F1=1/3.
        self.assertAlmostEqual(m["macro_f1"], 1 / 3)
        self.assertAlmostEqual(m["accuracy"], 0.5)

    def test_perfect_and_single_class(self):
        labels = support.D1_LABELS
        perfect = metrics_from_codes(codes(["Ham", "Spam"], labels),
                                     codes(["Ham", "Spam"], labels), labels)
        self.assertAlmostEqual(perfect["macro_f1"], 1.0)
        single = metrics_from_codes(codes(["Ham", "Ham"], labels),
                                    codes(["Ham", "Ham"], labels), labels)
        # Absent class contributes 0 F1: macro-F1 is 0.5, not 1.0. Accuracy is 1.0.
        self.assertAlmostEqual(single["macro_f1"], 0.5)
        self.assertAlmostEqual(single["accuracy"], 1.0)

    def test_multiclass_macro_matches_sklearn(self):
        labels = support.D2_LABELS
        y = ["ham", "spam", "smishing", "ham", "smishing"]
        pred = ["ham", "spam", "ham", "ham", "smishing"]
        m = metrics_from_codes(codes(y, labels), codes(pred, labels), labels)
        self.assertAlmostEqual(
            m["macro_f1"], f1_score(y, pred, labels=labels, average="macro")
        )

    def test_invalid_label_fails_loudly(self):
        with self.assertRaises(KeyError):
            encode(["Phish"], support.D1_LABELS)

    def test_empty_input_fails_instead_of_returning_nan(self):
        # Regression: 0/0 produced a NaN macro-F1 rather than an error.
        with self.assertRaises(ValueError):
            metric_codes(np.asarray([], dtype=np.int16),
                         np.asarray([], dtype=np.int16), support.D1_LABELS)


class TestExactChecks(unittest.TestCase):
    def _binary(self):
        # rows = true Ham(5), Spam(5); tp=2, fp=1, fn=3, tn=4
        return {
            "n": 10,
            "confusion_matrix": [[4, 1], [3, 2]],
            "predicted": {"Ham": 7, "Spam": 3},
            "support": {"Ham": 5, "Spam": 5},
        }

    def test_binary_counts_and_denominators(self):
        checks = exact_checks(self._binary(), support.D1_LABELS)
        self.assertEqual((checks["tp"], checks["fp"], checks["fn"], checks["tn"]),
                         (2, 1, 3, 4))
        self.assertEqual(checks["precision_denominator"], 3)
        self.assertEqual(checks["false_positive_rate_copper_pearson_95"][0],
                         cp_interval(1, 5)[0])

    def test_zero_false_positives_interval_is_not_zero_risk(self):
        m = {"n": 40, "confusion_matrix": [[38, 0], [2, 0]],
             "predicted": {"Ham": 40, "Spam": 0}, "support": {"Ham": 38, "Spam": 2}}
        checks = exact_checks(m, support.D1_LABELS)
        self.assertEqual(checks["fp"], 0)
        low, high = checks["false_positive_rate_copper_pearson_95"]
        self.assertEqual(low, 0.0)
        self.assertGreater(high, 0.05)

    def test_multiclass_input_is_rejected(self):
        # Regression: a three-class confusion matrix cannot yield one binary FPR.
        with self.assertRaises(ValueError):
            exact_checks({"n": 3, "confusion_matrix": [[1, 0, 0], [0, 1, 0],
                                                       [0, 0, 1]],
                          "predicted": {"ham": 1, "spam": 1, "smishing": 1},
                          "support": {"ham": 1, "spam": 1, "smishing": 1}},
                         support.D2_LABELS)

    def test_multiclass_per_class_checks(self):
        cm = [[5, 1, 0], [0, 4, 0], [2, 0, 3]]
        m = {"n": 15, "confusion_matrix": cm,
             "predicted": {"ham": 7, "spam": 5, "smishing": 3},
             "support": {"ham": 6, "spam": 4, "smishing": 5}}
        checks = multiclass_exact_checks(m, support.D2_LABELS)
        self.assertNotIn("per_class", checks.get("false_positive_rate", {}))
        self.assertFalse(any("false_positive" in key for key in checks))
        spam = checks["per_class"]["spam"]
        self.assertEqual(spam["tp"], 4)
        self.assertEqual(spam["precision_denominator"], 5)
        self.assertEqual(spam["support"], 4)
        self.assertAlmostEqual(spam["precision_copper_pearson_95"][0],
                               cp_interval(4, 5)[0])


class TestBootstrap(unittest.TestCase):
    @staticmethod
    def _frame():
        rows = []
        for i in range(40):
            rows.append({
                "record_id": f"T-{i:03d}",
                "group_id": f"G{i:03d}",
                "label": "Spam" if i % 4 == 0 else "Ham",
                "prediction": "Spam" if i % 4 == 0 and i % 8 != 0 else "Ham",
            })
        return pd.DataFrame(rows)

    def test_same_seed_reproduces_identical_interval(self):
        df = self._frame()
        a = bootstrap(df, support.D1_LABELS, n_boot=200, seed=7)
        b = bootstrap(df, support.D1_LABELS, n_boot=200, seed=7)
        self.assertEqual(a["metrics"]["macro_f1"], b["metrics"]["macro_f1"])

    def test_different_seed_changes_interval(self):
        df = self._frame()
        a = bootstrap(df, support.D1_LABELS, n_boot=200, seed=7)
        b = bootstrap(df, support.D1_LABELS, n_boot=200, seed=8)
        self.assertNotEqual(a["metrics"]["macro_f1"]["ci_low"],
                            b["metrics"]["macro_f1"]["ci_low"])

    def test_interval_brackets_point_estimate(self):
        result = bootstrap(self._frame(), support.D1_LABELS, n_boot=300, seed=42)
        for metric, values in result["metrics"].items():
            self.assertLessEqual(values["ci_low"], values["point"], metric)
            self.assertLessEqual(values["point"], values["ci_high"], metric)

    def test_group_is_the_resampling_unit(self):
        df = self._frame()
        df = pd.concat([df, df.iloc[[0]].assign(record_id="T-900")],
                       ignore_index=True)
        df.loc[len(df) - 1, "group_id"] = df.loc[0, "group_id"]
        result = bootstrap(df, support.D1_LABELS, n_boot=50, seed=42)
        self.assertEqual(result["n_rows"], 41)
        self.assertEqual(result["n_groups"], 40)
        self.assertEqual(result["rows_per_group_max"], 2.0)

    def test_empty_frame_does_not_return_a_metric(self):
        empty = pd.DataFrame(columns=["record_id", "group_id", "label", "prediction"])
        with self.assertRaises((ValueError, ZeroDivisionError, IndexError)):
            bootstrap(empty, support.D1_LABELS, n_boot=10, seed=42)

    def test_paired_difference_direction_and_sign_symmetry(self):
        y = ["Ham", "Spam"] * 10
        perfect = y
        # Ham-only predictor: macro-F1 = (0.667 + 0) / 2 = 0.333
        ham_only = ["Ham"] * 20
        df_a = pd.DataFrame({"record_id": [f"R{i}" for i in range(20)],
                             "group_id": [f"G{i}" for i in range(20)],
                             "label": y, "prediction": perfect})
        df_b = df_a.assign(prediction=ham_only)
        forward = paired_bootstrap(df_a, df_b, support.D1_LABELS,
                                   n_boot=200, seed=11)
        reverse = paired_bootstrap(df_b, df_a, support.D1_LABELS,
                                   n_boot=200, seed=11)
        d = forward["metrics"]["macro_f1"]
        r = reverse["metrics"]["macro_f1"]
        self.assertGreater(d["difference"], 0)
        self.assertAlmostEqual(d["difference"], -r["difference"], places=12)
        self.assertAlmostEqual(d["ci_low"], -r["ci_high"], places=12)
        self.assertAlmostEqual(d["ci_high"], -r["ci_low"], places=12)
        self.assertGreaterEqual(d["share_positive"], 0.99)

    def test_paired_labels_must_agree(self):
        df_a = pd.DataFrame({"record_id": ["R0", "R1"], "group_id": ["G0", "G1"],
                             "label": ["Ham", "Spam"], "prediction": ["Ham", "Spam"]})
        df_b = pd.DataFrame({"record_id": ["R0", "R1"], "group_id": ["G0", "G1"],
                             "label": ["Ham", "Ham"], "prediction": ["Ham", "Ham"]})
        with self.assertRaises(SystemExit):
            paired_bootstrap(df_a, df_b, support.D1_LABELS, n_boot=10, seed=1)


class TestRealPairedDirection(unittest.TestCase):
    """Regression for the reported LR vs SVM sign confusion, using frozen data."""

    @classmethod
    def setUpClass(cls):
        from p2_stats import load_d1_models
        cls.models = load_d1_models()

    def test_logreg_minus_svm_is_negative(self):
        result = paired_bootstrap(self.models["Logistic Regression"],
                                  self.models["Linear SVM"],
                                  support.D1_LABELS, n_boot=2000, seed=42)
        d = result["metrics"]["macro_f1"]
        self.assertAlmostEqual(d["difference"], -0.009360118526741346, places=10)
        self.assertLess(d["ci_low"], 0)
        self.assertLessEqual(d["ci_low"], d["difference"])
        self.assertLessEqual(d["difference"], d["ci_high"])
        self.assertAlmostEqual(d["ci_low"], -0.03214315072560611, delta=1e-9)
        self.assertAlmostEqual(d["ci_high"], 0.0, delta=1e-12)

    def test_reverse_comparison_is_exact_negation(self):
        forward = paired_bootstrap(self.models["Logistic Regression"],
                                   self.models["Linear SVM"],
                                   support.D1_LABELS, n_boot=500, seed=42)
        reverse = paired_bootstrap(self.models["Linear SVM"],
                                   self.models["Logistic Regression"],
                                   support.D1_LABELS, n_boot=500, seed=42)
        a = forward["metrics"]["macro_f1"]
        b = reverse["metrics"]["macro_f1"]
        self.assertAlmostEqual(a["difference"], -b["difference"], places=12)
        self.assertAlmostEqual(a["ci_low"], -b["ci_high"], places=12)
        self.assertAlmostEqual(a["ci_high"], -b["ci_low"], places=12)

    def test_models_share_test_rows_and_labels(self):
        a = self.models["Logistic Regression"]
        b = self.models["Linear SVM"]
        self.assertEqual(len(a), 299)
        self.assertEqual(list(a["record_id"]), list(b["record_id"]))
        self.assertEqual(list(a["label"]), list(b["label"]))
        self.assertEqual(list(a["group_id"]), list(b["group_id"]))


if __name__ == "__main__":
    unittest.main()
