"""Frozen split integrity tests: sizes, hashes, overlap, labels and uniqueness."""
from __future__ import annotations

import hashlib
import unittest

import pandas as pd

import support
from p2_common import assert_no_leakage

FILES = {
    "d1": ("d1_malayalam_train.csv", "d1_malayalam_val.csv", "d1_malayalam_test.csv"),
    "d2": ("d2_train.csv", "d2_val.csv", "d2_test.csv"),
}
EXPECTED_ROWS = {
    "d1": (1394, 299, 299),
    "d2": (4127, 885, 883),
}
EXPECTED_CLASSES = {
    "d1": ({"Ham": 1237, "Spam": 157}, {"Ham": 265, "Spam": 34},
           {"Ham": 265, "Spam": 34}),
    "d2": ({"ham": 3391, "spam": 315, "smishing": 421},
           {"ham": 727, "spam": 68, "smishing": 90},
           {"ham": 726, "spam": 67, "smishing": 90}),
}


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class TestSplitSizesAndHashes(unittest.TestCase):
    def test_sizes(self):
        for dataset, names in FILES.items():
            for name, expected in zip(names, EXPECTED_ROWS[dataset]):
                with self.subTest(file=name):
                    self.assertEqual(len(support.split(name)), expected)

    def test_hashes_match_manifest(self):
        manifest = support.split_manifest()
        for dataset, names in FILES.items():
            recorded = {item["file"]: item["sha256"]
                        for item in manifest[dataset]["files"]}
            for name in names:
                with self.subTest(file=name):
                    self.assertIn(name, recorded)
                    self.assertEqual(sha256(support.SPLITS / name), recorded[name])

    def test_source_hashes_recorded(self):
        manifest = support.split_manifest()
        for dataset, name in (("d1", "Spam Message Collection.xlsx"),
                              ("d2", "Dataset_5971.csv")):
            path = support.ROOT / "Datasets" / name
            self.assertEqual(sha256(path), manifest["source_hashes"][dataset])


class TestSplitContent(unittest.TestCase):
    def test_label_distribution(self):
        for dataset, names in FILES.items():
            for name, expected in zip(names, EXPECTED_CLASSES[dataset]):
                with self.subTest(file=name):
                    counts = support.split(name)["label"].value_counts().to_dict()
                    for label, value in expected.items():
                        self.assertEqual(counts.get(label), value)

    def test_record_ids_unique_and_disjoint(self):
        for dataset, names in FILES.items():
            seen: set[str] = set()
            for name in names:
                frame = support.split(name)
                self.assertTrue(frame["record_id"].is_unique, name)
                ids = set(frame["record_id"])
                overlap = seen & ids
                self.assertEqual(overlap, set(), f"{name} overlaps a previous split")
                seen |= ids
            total = sum(EXPECTED_ROWS[dataset])
            self.assertEqual(len(seen), total, dataset)

    def test_source_rows_unique_per_dataset(self):
        for dataset, names in FILES.items():
            combined = pd.concat([support.split(n) for n in names])
            self.assertTrue(combined["source_row"].is_unique, dataset)

    def test_group_and_norm_overlap_is_zero(self):
        for dataset, names in FILES.items():
            combined = pd.concat([support.split(n) for n in names], ignore_index=True)
            with self.subTest(dataset=dataset):
                checks = assert_no_leakage(combined)
                self.assertTrue(checks["ok"], checks)
                for key, value in checks.items():
                    if key != "ok":
                        self.assertEqual(value, 0, key)

    def test_no_missing_or_invalid_labels(self):
        for dataset, names in FILES.items():
            allowed = {"Ham", "Spam"} if dataset == "d1" else {
                "ham", "spam", "smishing"}
            for name in names:
                labels = set(support.split(name)["label"])
                self.assertEqual(labels, allowed, name)

    def test_test_groups_are_singletons(self):
        for name in ("d1_malayalam_test.csv", "d2_test.csv"):
            frame = support.split(name)
            self.assertEqual(frame.groupby("group_id").size().max(), 1, name)


if __name__ == "__main__":
    unittest.main()
