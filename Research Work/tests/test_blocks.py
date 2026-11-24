"""Row-block boundary and composition tests.

The frozen split manifest still contains the block table produced by the old
off-by-one formula. These tests pin the corrected composition derived from the
frozen splits, so a silent return to the old formula fails the suite. They do
not modify the manifest; the mismatch is reported in the audit documents.
"""
from __future__ import annotations

import unittest

import pandas as pd

import support
from p2_common import block_number

D1_PARTS = ("d1_malayalam_train.csv", "d1_malayalam_val.csv",
            "d1_malayalam_test.csv")


def stale_block_number(source_row) -> int:
    """The historical formula from p2_split.py / p2_robustness.py."""
    return ((int(source_row) - 1) - 1) // 1000 + 1


def d1_all_rows() -> pd.DataFrame:
    return pd.concat([support.split(p) for p in D1_PARTS], ignore_index=True)


class TestBlockBoundaries(unittest.TestCase):
    def test_first_and_last_row_of_each_block(self):
        expected = {4001: 5, 5000: 5, 5001: 6, 6000: 6, 6001: 7, 7000: 7,
                    3999: 4, 7001: 8, 1: 1}
        for row, block in expected.items():
            self.assertEqual(block_number(row), block, row)

    def test_stale_formula_differs_at_the_boundary(self):
        # Excel row 4001 is the first data row of block 5; the old formula said 4.
        self.assertEqual(stale_block_number(4001), 4)
        self.assertEqual(block_number(4001), 5)
        self.assertEqual(stale_block_number(5001), 5)
        self.assertEqual(block_number(5001), 6)
        self.assertNotEqual(stale_block_number(4001), block_number(4001))

    def test_only_the_block_boundary_rows_shift(self):
        # The stale formula moves the first row of every block, not all rows.
        moved = [row for row in range(4001, 7002)
                 if stale_block_number(row) != block_number(row)]
        self.assertEqual(moved, [4001, 5001, 6001, 7001])


class TestFrozenComposition(unittest.TestCase):
    def test_corrected_block_totals(self):
        rows = d1_all_rows()
        counts = rows.assign(block=rows["source_row"].map(block_number)) \
                     .groupby("block").size().to_dict()
        self.assertEqual(counts, {5: 630, 6: 991, 7: 371})
        self.assertEqual(sum(counts.values()), 1992)

    def test_corrected_label_composition(self):
        rows = d1_all_rows()
        table = (rows.assign(block=rows["source_row"].map(block_number))
                     .groupby(["block", "label"]).size().unstack(fill_value=0))
        self.assertEqual(int(table.loc[5, "Ham"]), 618)
        self.assertEqual(int(table.loc[5, "Spam"]), 12)
        self.assertEqual(int(table.loc[6, "Ham"]), 991)
        self.assertEqual(int(table.loc[6, "Spam"]), 0)
        self.assertEqual(int(table.loc[7, "Ham"]), 158)
        self.assertEqual(int(table.loc[7, "Spam"]), 213)

    def test_block_numbers_match_block_prediction_files(self):
        rows = d1_all_rows().set_index("record_id")
        for block, fold, size in ((4001, "4001-5000", 630),
                                  (5001, "5001-6000", 991),
                                  (6001, "6001-7000", 371)):
            ordered = pd.read_csv(
                support.METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
            ordered = ordered[ordered["fold"] == fold]
            self.assertEqual(len(ordered.groupby("record_id")), size)
            mapped = rows.loc[ordered["record_id"].unique(), "source_row"] \
                         .map(block_number).unique().tolist()
            self.assertEqual(mapped, [block // 1000 + 1])

    def test_manifest_block_table_is_stale_and_still_unmodified(self):
        manifest = support.split_manifest()
        sums = {"4001-5000": 0, "5001-6000": 0, "6001-7000": 0}
        for entry in manifest["d1"]["blocks"]:
            for fold, value in entry["blocks"].items():
                sums[fold] += value
        # 631/991/370 is the old off-by-one result, not the true 630/991/371.
        self.assertEqual(sums, {"4001-5000": 631, "5001-6000": 991,
                                "6001-7000": 370})
        self.assertNotEqual(list(sums.values()), [630, 991, 371])

    def test_boundary_record_is_in_block_five_in_the_full_workbook(self):
        # source_row is a workbook row, so the boundary check uses all 7,717
        # records; the Malayalam subset itself starts one row later.
        from p2_common import load_d1

        full = load_d1()
        self.assertEqual(len(full), 7717)
        boundary = full[full["source_row"] == 4001]
        self.assertEqual(len(boundary), 1)
        self.assertEqual(block_number(int(boundary.iloc[0]["source_row"])), 5)
        mal = full[full["has_malayalam"]]
        self.assertEqual(len(mal), 1992)
        self.assertNotIn(4001, set(mal["source_row"]))
        in_block_5 = mal[mal["source_row"].map(block_number) == 5]
        self.assertEqual(len(in_block_5), 630)


class TestTestSplitComposition(unittest.TestCase):
    def test_test_split_blocks(self):
        test = support.split("d1_malayalam_test.csv")
        table = (test.assign(block=test["source_row"].map(block_number))
                     .groupby(["block", "label"]).size().unstack(fill_value=0))
        self.assertEqual(int(table.loc[5, "Ham"]), 86)
        self.assertEqual(int(table.loc[5, "Spam"]), 3)
        self.assertEqual(int(table.loc[6, "Ham"]), 159)
        self.assertEqual(int(table.loc[6, "Spam"]), 0)
        self.assertEqual(int(table.loc[7, "Ham"]), 20)
        self.assertEqual(int(table.loc[7, "Spam"]), 31)


if __name__ == "__main__":
    unittest.main()
