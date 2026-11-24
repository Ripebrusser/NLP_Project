"""Duplicate grouping, conflict detection and leakage tests."""
from __future__ import annotations

import unittest

import pandas as pd

import support
from audit_datasets import norm_key
from p2_common import (
    UnionFind,
    add_norm_groups,
    assert_no_leakage,
    group_conflicts,
    load_d1,
    load_d2,
    split_grouped,
)


class TestNormKey(unittest.TestCase):
    def test_url_variants_collapse(self):
        self.assertEqual(norm_key("Visit http://a.com/x now"),
                         norm_key("Visit https://b.org/y now"))

    def test_number_variants_collapse(self):
        self.assertEqual(norm_key("Call 9876543210"), norm_key("Call 1234567890"))

    def test_case_and_punctuation_collapse(self):
        self.assertEqual(norm_key("Hello, WORLD!!"), norm_key("hello world"))

    def test_different_text_stays_different(self):
        self.assertNotEqual(norm_key("Call me tomorrow"), norm_key("Call me today"))

    def test_malayalam_text_is_preserved_and_numbers_collapse(self):
        a = norm_key("വിളിക്കൂ 9876543210")
        b = norm_key("വിളിക്കൂ 1234567890")
        self.assertEqual(a, b)
        self.assertIn("വിളിക്കൂ", a)
        self.assertNotEqual(a, norm_key("അയക്കൂ 1234567890"))

    def test_url_placeholder_is_inserted(self):
        # The placeholder survives normalisation as the token "url". The angle
        # brackets are stripped after substitution; changing this would change
        # frozen group IDs, so it is documented rather than altered.
        key = norm_key("go to www.example.com")
        self.assertIn("url", key.split())
        self.assertEqual(key, norm_key("go to http://other.example.org"))


class TestGrouping(unittest.TestCase):
    def test_union_find_is_transitive(self):
        uf = UnionFind(5)
        uf.union(0, 1)
        uf.union(1, 2)
        uf.union(3, 4)
        self.assertEqual(uf.find(0), uf.find(2))
        self.assertNotEqual(uf.find(0), uf.find(3))

    def test_group_assignment_is_deterministic_and_stable(self):
        df = pd.DataFrame({
            "message": ["Call 111", "Call 222", "Different text", "call 333"],
            "label": ["Ham", "Ham", "Spam", "Ham"],
        })
        a = add_norm_groups(df)
        b = add_norm_groups(df)
        self.assertEqual(list(a["group_id"]), list(b["group_id"]))
        self.assertEqual(a.loc[0, "group_id"], a.loc[1, "group_id"])
        self.assertEqual(a.loc[0, "group_id"], a.loc[3, "group_id"])
        self.assertNotEqual(a.loc[0, "group_id"], a.loc[2, "group_id"])
        self.assertTrue(a["group_id"].str.fullmatch(r"G\d{5}").all())

    def test_conflict_groups_are_flagged_only_when_labels_differ(self):
        df = pd.DataFrame({
            "message": ["Same text", "Same text", "Other", "Other"],
            "label": ["Ham", "Spam", "Ham", "Ham"],
        })
        grouped = add_norm_groups(df)
        result = group_conflicts(grouped)
        self.assertTrue(result.loc[0, "conflict_group"])
        self.assertTrue(result.loc[1, "conflict_group"])
        self.assertFalse(result.loc[2, "conflict_group"])
        self.assertFalse(result.loc[3, "conflict_group"])


class TestSplitGrouped(unittest.TestCase):
    @staticmethod
    def fixture():
        rows = []
        for g in range(20):
            label = "Spam" if g % 4 == 0 else "Ham"
            for r in range(3):
                rows.append({
                    "record_id": f"X-{g:02d}-{r}",
                    "group_id": f"G{g:03d}",
                    "norm_key": f"key {g}",
                    "label": label,
                    "text": f"text {g} {r}",
                })
        return pd.DataFrame(rows)

    def test_groups_stay_intact_and_all_three_splits_are_used(self):
        df = split_grouped(self.fixture(), "label", seed=42)
        self.assertEqual(set(df["split"]), {"train", "val", "test"})
        membership = df.groupby("group_id")["split"].nunique()
        self.assertTrue((membership == 1).all())
        self.assertEqual(len(df), 60)

    def test_deterministic_with_same_seed(self):
        a = split_grouped(self.fixture(), "label", seed=42)
        b = split_grouped(self.fixture(), "label", seed=42)
        self.assertEqual(list(a["split"]), list(b["split"]))

    def test_no_group_or_norm_overlap(self):
        df = split_grouped(self.fixture(), "label", seed=42)
        checks = assert_no_leakage(df)
        self.assertTrue(checks["ok"])
        self.assertEqual(checks["group_overlap_train_test"], 0)
        self.assertEqual(checks["norm_overlap_train_test"], 0)


class TestFrozenGroupCounts(unittest.TestCase):
    def test_d1_grouping_pipeline_reproduces_frozen_groups(self):
        from p2_duplicates import build

        full = load_d1()
        self.assertEqual(len(full), 7717)  # the whole Dravidian workbook
        mal = full[full["has_malayalam"] & full["label"].isin(["Ham", "Spam"])]
        mal = mal.reset_index(drop=True)
        grouped, summary = build(mal, fuzzy=True)
        manifest = support.split_manifest()
        self.assertEqual(len(grouped), 1992)
        self.assertEqual(summary["final_groups"], manifest["d1"]["groups"])
        self.assertEqual(summary["final_excess"], 168)
        self.assertEqual(summary["conflict_records"], 0)
        frozen = pd.concat(
            [support.split(n) for n in
             ("d1_malayalam_train.csv", "d1_malayalam_val.csv",
              "d1_malayalam_test.csv")], ignore_index=True)
        mapping = frozen.set_index("record_id")["group_id"]
        expected = mapping.reindex(grouped["record_id"]).to_numpy()
        self.assertTrue((grouped["group_id"].to_numpy() == expected).all())

    def test_d2_group_structure_matches_manifest(self):
        full = load_d2()
        df = group_conflicts(add_norm_groups(full))
        manifest = support.split_manifest()
        self.assertEqual(len(df), 5971)
        # The manifest counts groups after removing conflicting-label groups.
        kept = df[~df["conflict_group"]]
        self.assertEqual(len(kept), 5895)
        self.assertEqual(kept["group_id"].nunique(), manifest["d2"]["groups"])
        self.assertEqual(len(kept) - kept["group_id"].nunique(), 232)
        self.assertEqual(df.loc[df["conflict_group"], "group_id"].nunique(),
                         manifest["exclusions"]["d2_conflict_groups"])
        self.assertEqual(int(df["conflict_group"].sum()),
                         manifest["exclusions"]["d2_conflict_records"])


if __name__ == "__main__":
    unittest.main()
