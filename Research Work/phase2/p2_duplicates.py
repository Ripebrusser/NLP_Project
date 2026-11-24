#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 2: exact, normalised and fuzzy duplicate grouping + label conflicts.

D1 (primary) gets all three passes. D2 (secondary) uses exact + normalised
groups; its audit already showed 180 near-duplicate groups and 37 conflicts.
Conflicting groups are flagged and excluded from supervised experiments.
"""
from __future__ import annotations

import sys
from collections import Counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

from p2_common import (DATA, METRICS, UnionFind, add_norm_groups, dump_json,
                       group_conflicts)


def jaccard(a: str, b: str) -> float:
    A, B = set(a.split()), set(b.split())
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def fuzzy_pairs(texts: list[str], threshold: float = 0.90) -> list[tuple[int, int, float]]:
    """Conservative char-TF-IDF cosine neighbours, verified by token overlap."""
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2,
                          sublinear_tf=True)
    X = vec.fit_transform(texts)
    nn = NearestNeighbors(radius=1.0 - threshold, metric="cosine",
                          algorithm="brute", n_jobs=-1)
    nn.fit(X)
    dist, ind = nn.radius_neighbors(X, return_distance=True)
    pairs = []
    for i in range(len(texts)):
        for d, j in zip(dist[i], ind[i]):
            if j <= i:
                continue
            sim = 1.0 - float(d)
            # very high cosine is enough; otherwise require lexical agreement
            if sim >= 0.97 or jaccard(texts[i], texts[j]) >= 0.60:
                pairs.append((i, int(j), sim))
    return pairs


def build(df: pd.DataFrame, fuzzy: bool) -> tuple[pd.DataFrame, dict]:
    n = len(df)
    uf = UnionFind(n)
    exact_keys = df["message"].tolist()

    # exact groups
    first = {}
    exact_groups = 0
    for i, t in enumerate(exact_keys):
        if t in first:
            uf.union(first[t], i)
        else:
            first[t] = i
    exact_groups = len(first)

    # normalised groups
    df = add_norm_groups(df)
    norm_first = {}
    for i, k in enumerate(df["norm_key"]):
        if k in norm_first:
            uf.union(norm_first[k], i)
        else:
            norm_first[k] = i

    fp = []
    if fuzzy:
        fp = fuzzy_pairs(df["text"].tolist())
        for a, b, _ in fp:
            uf.union(a, b)

    roots = [uf.find(i) for i in range(n)]
    root_to_gid = {}
    gids = []
    for r in roots:
        if r not in root_to_gid:
            root_to_gid[r] = f"G{len(root_to_gid):05d}"
        gids.append(root_to_gid[r])
    df["group_id"] = gids
    df = group_conflicts(df)

    summary = {
        "records": n,
        "exact_groups": exact_groups,
        "exact_excess": n - exact_groups,
        "norm_groups": len(norm_first),
        "fuzzy_extra_pairs": len(fp),
        "final_groups": df["group_id"].nunique(),
        "final_excess": n - df["group_id"].nunique(),
        "conflict_groups": int(df.loc[df["conflict_group"], "group_id"].nunique()),
        "conflict_records": int(df["conflict_group"].sum()),
        "conflict_labels": {},
        "largest_groups": [],
    }
    for gid, g in df[df["conflict_group"]].groupby("group_id"):
        summary["conflict_labels"][gid] = dict(Counter(g["label"]))
    sizes = df.groupby("group_id").size().sort_values(ascending=False)
    summary["largest_groups"] = [
        {"group_id": gid, "n": int(n_), "labels": dict(Counter(df.loc[df.group_id == gid, "label"]))}
        for gid, n_ in sizes.head(10).items()
    ]
    return df, summary


def main() -> None:
    d1 = pd.read_csv(DATA / "d1_malayalam.csv", encoding="utf-8-sig")
    d2 = pd.read_csv(DATA / "d2_all_records.csv", encoding="utf-8-sig")
    d1 = d1[d1["label"].isin(["Ham", "Spam"])].reset_index(drop=True)
    d2 = d2[d2["label"].isin(["ham", "spam", "smishing"])].reset_index(drop=True)

    d1g, s1 = build(d1, fuzzy=True)
    d2g, s2 = build(d2, fuzzy=False)

    keep1 = ["record_id", "source_row", "message", "text", "label", "group_id",
             "norm_key", "conflict_group", "has_latin", "malayalam_only_script"]
    keep2 = ["record_id", "source_row", "message", "text", "label", "group_id",
             "norm_key", "conflict_group", "has_latin", "URL", "EMAIL", "PHONE"]
    d1g[keep1].to_csv(DATA / "d1_malayalam_grouped.csv", index=False, encoding="utf-8-sig")
    d2g[keep2].to_csv(DATA / "d2_grouped.csv", index=False, encoding="utf-8-sig")

    report = {"d1_malayalam": s1, "d2": s2,
              "note": ("D1 fuzzy pass: char_wb 3-5 TF-IDF cosine >= 0.90 plus token "
                       "Jaccard >= 0.60 (or cosine >= 0.97). D2 uses exact + normalised "
                       "groups only; fuzzy matching on 5,971 short texts risks merging "
                       "generic templates, and D2 is secondary.")}
    dump_json(report, METRICS / "duplicates.json")
    print("D1:", s1)
    print("D2:", s2)
    print("wrote", DATA / "d1_malayalam_grouped.csv", "and", DATA / "d2_grouped.csv")


if __name__ == "__main__":
    sys.exit(main())
