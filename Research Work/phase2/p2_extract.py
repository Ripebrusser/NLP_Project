#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1: extract and preprocess the D1 Malayalam subset and the D2 corpus.

Writes:
  data/d1_all_records.csv      all 7,717 workbook records (audit view)
  data/d1_malayalam.csv        1,992 Malayalam-containing records (primary)
  data/d2_all_records.csv      5,971 Mendeley records (secondary)
  metrics/subset_audit.json    counts + discrepancy explanation
"""
from __future__ import annotations

import json
from collections import Counter

import pandas as pd

from p2_common import (CSV_PATH, DATA, METRICS, XLSX, add_script_flags, dump_json,
                       load_d1, load_d2, sha256_file)

# ---- D1 -------------------------------------------------------------------
d1 = load_d1()
mal = d1[d1["has_malayalam"]].copy()
mal = mal[mal["label"].isin(["Ham", "Spam"])].copy()  # no invalid/missing in this subset

# explicit exclusive script category for the Malayalam subset
mal["script_category"] = "malayalam_only_script"
mal.loc[mal["has_latin"], "script_category"] = "malayalam_plus_latin"

# ---- D2 -------------------------------------------------------------------
d2 = load_d2()

# ---- persistence ----------------------------------------------------------
d1_cols = ["record_id", "source_row", "message", "text", "label_raw", "label",
           "has_malayalam", "has_tamil", "has_telugu", "has_kannada", "has_latin",
           "other_indic", "malayalam_only_script"]
d1[d1_cols].to_csv(DATA / "d1_all_records.csv", index=False, encoding="utf-8-sig")
mal_out = mal[["record_id", "source_row", "message", "text", "label_raw", "label",
               "has_latin", "script_category", "malayalam_only_script"]]
mal_out.to_csv(DATA / "d1_malayalam.csv", index=False, encoding="utf-8-sig")

d2_cols = ["record_id", "source_row", "message", "text", "label_raw", "label",
           "has_malayalam", "has_latin", "other_indic", "URL", "EMAIL", "PHONE"]
d2[d2_cols].to_csv(DATA / "d2_all_records.csv", index=False, encoding="utf-8-sig")

# ---- audit report ---------------------------------------------------------
contains = {
    "malayalam": int(d1["has_malayalam"].sum()),
    "tamil": int(d1["has_tamil"].sum()),
    "telugu": int(d1["has_telugu"].sum()),
    "kannada": int(d1["has_kannada"].sum()),
    "latin": int(d1["has_latin"].sum()),
}
# exclusive buckets, defined so every record lands in exactly one bucket
def bucket(r):
    if r.has_malayalam:
        return "malayalam_plus_latin" if r.has_latin else "malayalam_only_script"
    if r.has_tamil:
        return "tamil_plus_latin" if r.has_latin else "tamil_only"
    if r.has_telugu:
        return "telugu_plus_latin" if r.has_latin else "telugu_only"
    if r.has_kannada:
        return "kannada_plus_latin" if r.has_latin else "kannada_only"
    if r.has_latin:
        return "latin_only"
    return "other_or_no_letters"

buckets = Counter(bucket(r) for r in d1.itertuples())
report = {
    "d1": {
        "records": len(d1),
        "raw_label_counts": dict(Counter(d1["label_raw"])),
        "invalid_labels": int((d1["label"] == "INVALID").sum()),
        "empty_messages": int(d1["message"].str.strip().eq("").sum()),
        "contains_counts_inclusive": contains,
        "contains_sum": sum(contains.values()),
        "exclusive_buckets": dict(buckets),
        "exclusive_sum": sum(buckets.values()),
        "discrepancy_explanation": (
            "Inclusive 'contains' counts sum to more than 7,717 because a message can "
            "contain more than one script (most often Malayalam + Latin). The earlier "
            "audit mixed inclusive counts with exclusive buckets; the exclusive buckets "
            "here sum exactly to 7,717. Malayalam-containing records = 1,992, of which "
            "503 also contain Latin and 1,489 contain no Latin. No Malayalam record "
            "contains Tamil, Telugu or Kannada."
        ),
        "malayalam": {
            "records": len(mal),
            "labels": dict(Counter(mal["label"])),
            "latin_cooccurrence": int(mal["has_latin"].sum()),
            "malayalam_only_script": int(mal["malayalam_only_script"].sum()),
            "other_indic_cooccurrence": int(mal["other_indic"].sum()),
            "script_categories": dict(Counter(mal["script_category"])),
            "mean_tokens": round(float(mal["text"].str.split().str.len().mean()), 3),
            "median_tokens": float(mal["text"].str.split().str.len().median()),
            "url_records": int(mal["message"].str.contains(r"https?://|www\.", case=False, regex=True).sum()),
        },
        "row_blocks": [],
    },
    "d2": {
        "records": len(d2),
        "raw_label_counts": dict(Counter(d2["label_raw"])),
        "normalised_label_counts": dict(Counter(d2["label"])),
        "empty_messages": int(d2["message"].str.strip().eq("").sum()),
        "indic_records": int((d2["has_malayalam"] | d2["has_tamil"] | d2["has_telugu"] | d2["has_kannada"]).sum()),
        "latin_records": int(d2["has_latin"].sum()),
        "url_flag_non_no": int((~d2["URL"].fillna("no").str.lower().isin(["no", "", "0"])).sum()),
        "email_flag_non_no": int((~d2["EMAIL"].fillna("no").str.lower().isin(["no", "", "0"])).sum()),
        "phone_flag_non_no": int((~d2["PHONE"].fillna("no").str.lower().isin(["no", "", "0"])).sum()),
    },
    "source_hashes": {
        "d1_xlsx": sha256_file(XLSX),
        "d2_csv": sha256_file(CSV_PATH),
    },
}

for start in range(0, len(d1), 1000):
    blk = d1.iloc[start:start + 1000]
    bm = blk[blk["has_malayalam"]]
    report["d1"]["row_blocks"].append({
        "data_rows": f"{start + 1}-{start + len(blk)}",
        "n": int(len(blk)),
        "malayalam": int(len(bm)),
        "malayalam_ham": int((bm["label"] == "Ham").sum()),
        "malayalam_spam": int((bm["label"] == "Spam").sum()),
        "all_spam": int((blk["label"] == "Spam").sum()),
    })

dump_json(report, METRICS / "subset_audit.json")

print("D1:", json.dumps(report["d1"]["contains_counts_inclusive"]))
print("D1 exclusive buckets:", report["d1"]["exclusive_buckets"])
print("D1 Malayalam:", json.dumps(report["d1"]["malayalam"], ensure_ascii=False))
print("D2:", json.dumps(report["d2"], ensure_ascii=False))
print("wrote", DATA / "d1_malayalam.csv", "and", DATA / "d2_all_records.csv")
