#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared loading, cleaning, grouping and metric helpers for Phase 2.

Originals are read-only. Every derived row keeps source_row and record_id so it
can be traced back to the workbook/CSV.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
XLSX = BASE / "Datasets" / "Spam Message Collection.xlsx"
CSV_PATH = BASE / "Datasets" / "Dataset_5971.csv"
OUT = Path(__file__).resolve().parent
DATA = OUT / "data"
SPLITS = OUT / "splits"
MODELS = OUT / "models"
METRICS = OUT / "metrics"
REPORTS = OUT / "reports"
for _p in (DATA, SPLITS, MODELS, METRICS, REPORTS):
    _p.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE / "Research Work"))
from audit_datasets import norm_key  # noqa: E402  (same normalisation as the audit)

MAL = re.compile(r"[\u0D00-\u0D7F]")
TAM = re.compile(r"[\u0B80-\u0BFF]")
TEL = re.compile(r"[\u0C00-\u0C7F]")
KAN = re.compile(r"[\u0C80-\u0CFF]")
LAT = re.compile(r"[A-Za-z]")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
DIGIT_RE = re.compile(r"\d")
WS_RE = re.compile(r"\s+")
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def clean_text(s: str) -> str:
    """Conservative Unicode cleanup. Keeps Malayalam, punctuation and URLs."""
    s = unicodedata.normalize("NFKC", str(s))
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff"):
        s = s.replace(ch, "")
    s = s.replace("\u00a0", " ")
    s = CTRL_RE.sub(" ", s)
    return WS_RE.sub(" ", s).strip()


def block_number(source_row) -> int:
    """Map an Excel source row to its 1,000-row block.

    Excel row 4001 is the first data row of block 5 (4001-5000). The old
    p2_split/p2_robustness code subtracted 1 twice and produced the stale
    630-vs-631 membership. This is the single authoritative formula.
    """
    return (int(source_row) - 1) // 1000 + 1


def add_script_flags(df: pd.DataFrame) -> pd.DataFrame:
    msg = df["message"].fillna("")
    df["has_malayalam"] = msg.str.contains(MAL, regex=True)
    df["has_tamil"] = msg.str.contains(TAM, regex=True)
    df["has_telugu"] = msg.str.contains(TEL, regex=True)
    df["has_kannada"] = msg.str.contains(KAN, regex=True)
    df["has_latin"] = msg.str.contains(LAT, regex=True)
    df["other_indic"] = df[["has_tamil", "has_telugu", "has_kannada"]].any(axis=1)
    df["malayalam_only_script"] = df["has_malayalam"] & ~df["has_latin"] & ~df["other_indic"]
    return df


def load_d1() -> pd.DataFrame:
    """All workbook records with Excel row numbers preserved."""
    raw = pd.read_excel(XLSX, header=None, dtype=str)
    df = raw.iloc[1:].copy()
    df.columns = ["message", "label_raw"]
    df["source_row"] = df.index + 1  # pandas index 1 -> Excel row 2
    df["message"] = df["message"].fillna("")
    df["label_raw"] = df["label_raw"].fillna("")
    # drop only fully blank row(s)
    blank = df["message"].str.strip().eq("") & df["label_raw"].str.strip().eq("")
    df = df.loc[~blank].copy()
    df["record_id"] = [f"D1-{i:05d}" for i in range(len(df))]
    df["label"] = df["label_raw"].str.strip()
    df.loc[~df["label"].isin(["Ham", "Spam"]), "label"] = "INVALID"
    df["text"] = df["message"].map(clean_text)
    df = add_script_flags(df)
    return df.reset_index(drop=True)


def load_d2() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    df["source_row"] = df.index + 2  # CSV line number (header = line 1)
    df["record_id"] = [f"D2-{i:05d}" for i in range(len(df))]
    df["message"] = df["TEXT"].fillna("")
    df["label_raw"] = df["LABEL"].fillna("")
    lab = df["label_raw"].str.strip().str.lower()
    lab = lab.replace({"smishing": "smishing", "spam": "spam", "ham": "ham"})
    df["label"] = lab.where(lab.isin(["ham", "spam", "smishing"]), "INVALID")
    df["text"] = df["message"].map(clean_text)
    df = add_script_flags(df)
    return df.reset_index(drop=True)


class UnionFind:
    def __init__(self, n: int):
        self.p = list(range(n))

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def add_norm_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Group by the audit's aggressive normalisation (URLs/numbers/punctuation)."""
    df = df.copy()
    df["norm_key"] = df["message"].map(norm_key)
    groups = {}
    next_id = 0
    ids = []
    for k in df["norm_key"]:
        if k not in groups:
            groups[k] = f"G{next_id:05d}"
            next_id += 1
        ids.append(groups[k])
    df["group_id"] = ids
    return df


def group_conflicts(df: pd.DataFrame, label_col: str = "label") -> pd.DataFrame:
    """Rows belonging to a group whose labels are not unanimous."""
    bad = df.groupby("group_id")[label_col].nunique()
    bad = set(bad[bad > 1].index)
    df = df.copy()
    df["conflict_group"] = df["group_id"].isin(bad)
    return df


def split_grouped(
    df: pd.DataFrame,
    label_col: str = "label",
    ratios: tuple[float, float, float] = (0.70, 0.15, 0.15),
    seed: int = 42,
) -> pd.DataFrame:
    """Deterministic group-stratified 70/15/15 assignment.

    Groups (duplicate clusters) are never split. Within each label stratum,
    groups are shuffled with `seed`, sorted by size, then assigned to the split
    with the largest remaining record deficit. This keeps class ratios close to
    the requested proportions while keeping every group intact.
    """
    df = df.copy()
    rng = np.random.default_rng(seed)
    parts = ("train", "val", "test")
    assign: dict[str, str] = {}

    for label, stratum in df.groupby(label_col, sort=True):
        sizes = stratum.groupby("group_id").size().to_dict()
        keys = list(sizes)
        rng.shuffle(keys)
        keys.sort(key=lambda k: -sizes[k])
        total = sum(sizes.values())
        targets = {p: ratios[i] * total for i, p in enumerate(parts)}
        counts = {p: 0 for p in parts}
        for k in keys:
            p = max(parts, key=lambda q: targets[q] - counts[q])
            assign[k] = p
            counts[p] += sizes[k]
        if len(keys) >= 3:
            for q in ("val", "test"):
                if counts[q] == 0:
                    cands = [k for k in keys if assign[k] == "train"]
                    if len(cands) > 1:
                        k = min(cands, key=lambda x: sizes[x])
                        assign[k] = q
                        counts["train"] -= sizes[k]
                        counts[q] += sizes[k]

    df["split"] = df["group_id"].map(assign)
    if df["split"].isna().any():
        raise RuntimeError("unassigned groups in split")
    return df


def assert_no_leakage(df: pd.DataFrame, split_col: str = "split") -> dict:
    sets = {p: set(g) for p, g in df.groupby(split_col)["group_id"]}
    norm = {p: set(g) for p, g in df.groupby(split_col)["norm_key"]}
    checks = {}
    for a, b in (("train", "val"), ("train", "test"), ("val", "test")):
        checks[f"group_overlap_{a}_{b}"] = len(sets.get(a, set()) & sets.get(b, set()))
        checks[f"norm_overlap_{a}_{b}"] = len(norm.get(a, set()) & norm.get(b, set()))
    checks["ok"] = all(v == 0 for k, v in checks.items() if k != "ok")
    return checks


def align_predictions(
    pred: pd.DataFrame,
    split: pd.DataFrame,
    name: str,
    labels: list[str],
) -> pd.DataFrame:
    """Align a frozen prediction file to its frozen split by ``record_id``.

    The historical code used a plain inner merge. That silently drops a record
    missing from the prediction file, silently keeps a duplicated ID twice, and
    never checks that the prediction file's label column agrees with the split.
    Any of those changes a metric without leaving a trace. Here a mismatch is a
    hard error, and the returned frame has the split's row order, label and
    group_id with the prediction attached.
    """
    for column in ("record_id", "label", "prediction"):
        if column not in pred.columns:
            raise ValueError(f"{name}: prediction file is missing column {column!r}")
    if pred["record_id"].isna().any():
        raise ValueError(f"{name}: prediction file contains a null record_id")
    if not pred["record_id"].is_unique:
        dupes = pred.loc[pred["record_id"].duplicated(), "record_id"].head(5).tolist()
        raise ValueError(f"{name}: duplicate record_id values in predictions: {dupes}")
    if not split["record_id"].is_unique:
        raise ValueError(f"{name}: split contains duplicate record_id values")
    missing = sorted(set(split["record_id"]) - set(pred["record_id"]))
    extra = sorted(set(pred["record_id"]) - set(split["record_id"]))
    if missing or extra:
        raise ValueError(
            f"{name}: prediction/split record mismatch "
            f"(missing={len(missing)} e.g. {missing[:5]}, "
            f"extra={len(extra)} e.g. {extra[:5]})"
        )

    order = split["record_id"].tolist()
    indexed = pred.set_index("record_id")
    aligned = split[["record_id", "group_id", "label"]].copy()
    aligned["label"] = aligned["label"].astype(str)
    aligned["prediction"] = indexed.loc[order, "prediction"].astype(str).to_numpy()
    pred_label = indexed.loc[order, "label"].astype(str).to_numpy()
    if not (aligned["label"].to_numpy() == pred_label).all():
        bad = int((aligned["label"].to_numpy() != pred_label).sum())
        raise ValueError(f"{name}: {bad} prediction labels disagree with the frozen split")

    unexpected = (set(aligned["prediction"]) | set(aligned["label"])) - set(labels)
    if unexpected:
        raise ValueError(
            f"{name}: unexpected labels {sorted(unexpected)}; expected {labels}"
        )
    if "group_id" in pred.columns:
        pred_group = indexed.loc[order, "group_id"].astype(str).to_numpy()
        if not (pred_group == aligned["group_id"].astype(str).to_numpy()).all():
            raise ValueError(f"{name}: prediction group_id disagrees with the frozen split")
    return aligned.reset_index(drop=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def binary_metrics(y_true, y_pred, score=None) -> dict:
    from sklearn.metrics import (
        accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support,
        roc_auc_score, average_precision_score,
    )
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=["Ham", "Spam"], zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=["Ham", "Spam"])
    out = {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted")),
        "spam_precision": float(p[1]), "spam_recall": float(r[1]), "spam_f1": float(f[1]),
        "ham_precision": float(p[0]), "ham_recall": float(r[0]), "ham_f1": float(f[0]),
        "confusion_matrix": cm.tolist(),
        "labels": ["Ham", "Spam"],
    }
    if score is not None:
        y_bin = np.array([1 if v == "Spam" else 0 for v in y_true])
        try:
            out["roc_auc_spam"] = float(roc_auc_score(y_bin, score))
            out["pr_auc_spam"] = float(average_precision_score(y_bin, score))
        except ValueError:
            out["roc_auc_spam"] = None
            out["pr_auc_spam"] = None
    return out


def multiclass_metrics(y_true, y_pred, labels) -> dict:
    from sklearn.metrics import (
        accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support,
    )
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    per = {lab: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]),
                 "support": int(s[i])} for i, lab in enumerate(labels)}
    return {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted")),
        "per_class": per,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "labels": list(labels),
    }


def dump_json(obj, path: Path) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def print_counts(df: pd.DataFrame, name: str) -> None:
    print(f"{name}: n={len(df)} labels={dict(Counter(df['label']))} "
          f"groups={df['group_id'].nunique()} mal={int(df['has_malayalam'].sum())} "
          f"latin={int(df['has_latin'].sum())}")
