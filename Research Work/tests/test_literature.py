"""Literature workbook validation: register agreement and corruption detection."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import support
import validate_literature_matrix as vlm


class TestLiteratureMatrix(unittest.TestCase):
    def test_register_parses_24_unique_records(self):
        register = vlm.parse_register()
        self.assertEqual(len(register), 24)
        self.assertTrue(register["id"].is_unique)
        self.assertEqual(set(register["access"]),
                         {"FULL", "ABSTRACT", "METADATA", "EXCLUDED"})

    def test_workbook_matches_register(self):
        result = vlm.validate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["records_workbook"], 24)
        self.assertEqual(result["active_records"], 23)
        self.assertEqual(result["verification_counts"],
                         vlm.EXPECTED_COUNTS)

    def test_every_register_id_is_present(self):
        register = vlm.parse_register()
        book = vlm.load_workbook_rows()
        self.assertEqual(set(register["id"]), set(book["ID"]))
        self.assertTrue((book["ID"].str.fullmatch(r"[A-Z]\d{2}")).all())

    def test_excluded_record_is_not_citable(self):
        book = vlm.load_workbook_rows()
        excluded = book[book["Verification"] == "EXCLUDED"]
        self.assertEqual(list(excluded["ID"]), ["P10"])
        self.assertIn("do not cite", excluded.iloc[0]["Relevance"].lower())

    def test_no_decimal_result_on_unverified_records(self):
        book = vlm.load_workbook_rows()
        for _, row in book[book["Verification"] != "FULL TEXT"].iterrows():
            cell = str(row["Verified results"])
            if vlm.NUMBER_RE.search(cell):
                self.assertTrue(
                    cell.strip().lower().startswith(vlm.ALLOWED_NO_NUMBER),
                    f"{row['ID']}: {cell}",
                )


class TestCorruptionDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="litcheck_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, frame, name):
        xlsx = self.tmp / f"{name}.xlsx"
        csv = self.tmp / f"{name}.csv"
        with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
            frame.to_excel(writer, sheet_name="Paper Matrix", index=False)
            (frame.groupby("Verification").size().reset_index(name="Count")
             .to_excel(writer, sheet_name="Verification Summary", index=False))
        frame.to_csv(csv, index=False, encoding="utf-8-sig")
        return xlsx, csv

    def _assert_fails(self, frame, expected_text, name):
        xlsx, csv = self._write(frame, name)
        with self.assertRaises(vlm.LiteratureValidationError) as ctx:
            vlm.validate(xlsx_path=xlsx, csv_path=csv)
        self.assertIn(expected_text, str(ctx.exception))

    def test_missing_reference_is_detected(self):
        frame = vlm.load_workbook_rows()
        self._assert_fails(frame[frame["ID"] != "P08"], "P08", "missing")

    def test_reclassification_is_detected(self):
        frame = vlm.load_workbook_rows()
        frame.loc[frame["ID"] == "P10", "Verification"] = "FULL TEXT"
        self._assert_fails(frame, "P10", "reclass")

    def test_numeric_claim_on_abstract_is_detected(self):
        frame = vlm.load_workbook_rows()
        frame.loc[frame["ID"] == "P02", "Verified results"] = "98.5% accuracy"
        self._assert_fails(frame, "P02", "numeric")

    def test_csv_workbook_divergence_is_detected(self):
        frame = vlm.load_workbook_rows()
        xlsx, csv = self._write(frame, "csvdrift")
        drifted = pd.read_csv(csv, encoding="utf-8-sig", dtype=str).fillna("")
        drifted.loc[drifted["ID"] == "P01", "Year"] = "1900"
        drifted.to_csv(csv, index=False, encoding="utf-8-sig")
        with self.assertRaises(vlm.LiteratureValidationError) as ctx:
            vlm.validate(xlsx_path=xlsx, csv_path=csv)
        self.assertIn("CSV content differs", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
