#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 3: reproducible 70/15/15 grouped-stratified splits + SHA-256 manifest."""
from __future__ import annotations

import json
from collections import Counter

import pandas as pd

from p2_common import (CSV_PATH, DATA, METRICS, SPLITS, XLSX, assert_no_leakage,
                       block_number, dump_json, sha256_file, split_grouped)


def class_counts(df: pd.DataFrame) -> dict:
    return {str(k): int(v) for k, v in Counter(df["label"]).most_common()}


def save_split(df: pd.DataFrame, name: str, cols: list[str]) -> dict:
    path = SPLITS / f"{name}.csv"
    df[cols].to_csv(path, index=False, encoding="utf-8-sig")
    return {"file": path.name, "rows": int(len(df)), "classes": class_counts(df),
            "groups": int(df["group_id"].nunique()), "sha256": sha256_file(path)}


def main() -> None:
    d1_all = pd.read_csv(DATA / "d1_malayalam_grouped.csv", encoding="utf-8-sig")
    d2_all = pd.read_csv(DATA / "d2_grouped.csv", encoding="utf-8-sig")
    # count exclusions BEFORE filtering, otherwise the manifest records zero
    d1_excl_groups = int(d1_all.loc[d1_all["conflict_group"], "group_id"].nunique())
    d1_excl_records = int(d1_all["conflict_group"].sum())
    d2_excl_groups = int(d2_all.loc[d2_all["conflict_group"], "group_id"].nunique())
    d2_excl_records = int(d2_all["conflict_group"].sum())
    d1 = d1_all[~d1_all["conflict_group"]].reset_index(drop=True)
    d2 = d2_all[~d2_all["conflict_group"]].reset_index(drop=True)

    d1 = split_grouped(d1, seed=42)
    d2 = split_grouped(d2, seed=42)

    checks1 = assert_no_leakage(d1)
    checks2 = assert_no_leakage(d2)
    if not checks1["ok"] or not checks2["ok"]:
        raise SystemExit(f"leakage check failed: {checks1} {checks2}")

    cols1 = ["record_id", "source_row", "message", "text", "label", "group_id",
             "norm_key", "has_latin", "malayalam_only_script", "split"]
    cols2 = ["record_id", "source_row", "message", "text", "label", "group_id",
             "norm_key", "has_latin", "URL", "EMAIL", "PHONE", "split"]

    files1 = [save_split(d1[d1.split == p], f"d1_malayalam_{p}", cols1)
              for p in ("train", "val", "test")]
    files2 = [save_split(d2[d2.split == p], f"d2_{p}", cols2)
              for p in ("train", "val", "test")]

    # descriptive Malayalam-only subset (no Latin), split inherited from primary
    mono = d1[d1["malayalam_only_script"]]
    mono.to_csv(SPLITS / "d1_malayalam_only_descriptive.csv", index=False, encoding="utf-8-sig")

    # row-block composition, to expose the source-order confound.
    # block 1 = data rows 1-1000 (Excel rows 2-1001), etc.
    block_table = []
    for p in ("train", "val", "test"):
        part = d1[d1.split == p]
        b = part["source_row"].map(block_number).value_counts().sort_index()
        block_table.append({"split": p, "n": int(len(part)),
                            "blocks": {f"{int(k)*1000-999}-{int(k)*1000}": int(v)
                                       for k, v in b.items()}})

    manifest = {
        "seed": 42,
        "ratios": {"train": 0.70, "val": 0.15, "test": 0.15},
        "algorithm": ("groups = exact + normalised + fuzzy duplicate clusters; "
                      "within each label stratum, groups shuffled with numpy default_rng(42), "
                      "sorted by size, assigned to the split with the largest record deficit"),
        "source_files": {"d1": XLSX.name, "d2": CSV_PATH.name},
        "source_hashes": {"d1": sha256_file(XLSX), "d2": sha256_file(CSV_PATH)},
        "exclusions": {
            "d1_conflict_groups": d1_excl_groups,
            "d1_conflict_records": d1_excl_records,
            "d2_conflict_groups": d2_excl_groups,
            "d2_conflict_records": d2_excl_records,
        },
        "d1": {"rows": int(len(d1)), "groups": int(d1.group_id.nunique()),
               "classes": class_counts(d1), "checks": checks1, "files": files1,
               "blocks": block_table},
        "d2": {"rows": int(len(d2)), "groups": int(d2.group_id.nunique()),
               "classes": class_counts(d2), "checks": checks2, "files": files2},
        "malayalam_only_descriptive": {
            "rows": int(len(mono)), "classes": class_counts(mono),
            "split_rows": {p: int((mono.split == p).sum()) for p in ("train", "val", "test")},
            "split_spam": {p: int(((mono.split == p) & (mono.label == "Spam")).sum())
                           for p in ("train", "val", "test")},
        },
    }
    dump_json(manifest, SPLITS / "split_manifest.json")

    print("D1 checks:", checks1)
    print("D2 checks:", checks2)
    for row in files1 + files2:
        print(row)
    print("D1 blocks:", block_table)
    print("Malayalam-only:", manifest["malayalam_only_descriptive"])
    print("wrote", SPLITS / "split_manifest.json")


if __name__ == "__main__":
    main()
