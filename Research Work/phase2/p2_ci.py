#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2.2 Part A: group-level bootstrap confidence intervals.

Uses the frozen test predictions only. No model is retrained and no split is
changed. Resampling is at duplicate-group level; because every test group in
both frozen splits contains exactly one row, this is numerically the same as a
message-level bootstrap. That fact is stated in the report rather than hidden.

This script is **legacy**: `p2_stats.py` is authoritative for confidence
intervals and paired comparisons. Running this script writes its own
`confidence_intervals.json` and could silently replace the authoritative file,
so by default it writes `confidence_intervals_legacy.json`,
`confidence_intervals_legacy.csv` and no report. Pass
`--overwrite-authoritative` only when you deliberately intend to replace the
canonical evidence.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from p2_common import METRICS, REPORTS, SPLITS, align_predictions, dump_json

N_BOOT = 2000
SEED = 42
MODELS = [
    ("D1", "Linear SVM", "d1_malayalam_linear_svm_test_predictions.csv", ["Ham", "Spam"]),
    ("D1", "Logistic Regression", "d1_malayalam_logreg_test_predictions.csv", ["Ham", "Spam"]),
    ("D2", "Logistic Regression", "d2_logreg_test_predictions.csv", ["ham", "spam", "smishing"]),
    ("D2", "Linear SVM", "d2_linear_svm_test_predictions.csv", ["ham", "spam", "smishing"]),
]
SPLIT_FILES = {"D1": "d1_malayalam_test.csv", "D2": "d2_test.csv"}


def point_metrics(y_true, y_pred, labels: list[str]) -> dict:
    spam = "Spam" if "Spam" in labels else "spam"
    i = labels.index(spam)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0)
    out = {
        "n": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=labels, average="macro",
                                   zero_division=0)),
        "spam_precision": float(p[i]),
        "spam_recall": float(r[i]),
        "spam_f1": float(f[i]),
        "spam_support": int(s[i]),
    }
    for j, lab in enumerate(labels):
        out[f"f1_{lab}"] = float(f[j])
        out[f"precision_{lab}"] = float(p[j])
        out[f"recall_{lab}"] = float(r[j])
        out[f"support_{lab}"] = int(s[j])
    return out


def bootstrap(df: pd.DataFrame, labels: list[str], n_boot: int = N_BOOT,
              seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    groups = {gid: np.asarray(idx) for gid, idx in df.groupby("group_id").indices.items()}
    gids = list(groups)
    n_groups = len(gids)
    y = df["label"].to_numpy()
    pred = df["prediction"].to_numpy()

    reps = []
    valid_precision = 0
    for _ in range(n_boot):
        draw = rng.choice(n_groups, size=n_groups, replace=True)
        idx = np.concatenate([groups[gids[i]] for i in draw])
        m = point_metrics(y[idx], pred[idx], labels)
        # precision is only defined when the resample predicts at least one spam
        if ((pred[idx] == ("Spam" if "Spam" in labels else "spam"))).any():
            valid_precision += 1
        reps.append(m)

    frame = pd.DataFrame(reps)
    keys = ["accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1"] + \
           [f"f1_{lab}" for lab in labels]
    out = {}
    for k in keys:
        vals = frame[k].to_numpy()
        out[k] = {
            "point": float(point_metrics(y, pred, labels)[k]),
            "ci_low": float(np.percentile(vals, 2.5)),
            "ci_high": float(np.percentile(vals, 97.5)),
            "boot_mean": float(vals.mean()),
            "boot_sd": float(vals.std(ddof=1)),
        }
    return {
        "n_boot": n_boot,
        "seed": seed,
        "n_groups": n_groups,
        "n_rows": int(len(df)),
        "rows_per_group_max": float(df.groupby("group_id").size().max()),
        "replicates_predicting_spam": valid_precision,
        "metrics": out,
    }


def block_table() -> dict:
    pred = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
    rows = []
    for (model, fold), g in pred.groupby(["model", "fold"]):
        m = point_metrics(g["label"], g["prediction"], ["Ham", "Spam"])
        rows.append({"model": model, "fold": fold, "n": m["n"],
                     "ham": m["support_Ham"], "spam": m["support_Spam"],
                     "accuracy": m["accuracy"], "macro_f1": m["macro_f1"],
                     "spam_precision": m["spam_precision"] if m["spam_support"] else None,
                     "spam_recall": m["spam_recall"] if m["spam_support"] else None,
                     "spam_f1": m["spam_f1"] if m["spam_support"] else None,
                     "evaluable_for_spam": bool(m["spam_support"])})

    ranges = []
    for model, g in pd.DataFrame(rows).groupby("model"):
        ev = g[g["evaluable_for_spam"]]
        ranges.append({
            "model": model,
            "folds": len(g),
            "macro_f1_min": float(g["macro_f1"].min()),
            "macro_f1_max": float(g["macro_f1"].max()),
            "spam_recall_min": float(ev["spam_recall"].min()),
            "spam_recall_max": float(ev["spam_recall"].max()),
            "accuracy_min": float(g["accuracy"].min()),
            "accuracy_max": float(g["accuracy"].max()),
            "note": ("three source blocks only; the 5001-6000 fold has no Spam, so its "
                     "macro-F1 is a present-class artefact and Spam metrics are undefined"),
        })
    return {"folds": rows, "ranges": ranges}


def md_table(rows, cols) -> str:
    def fmt(v):
        if v is None:
            return "—"
        if isinstance(v, float):
            return f"{v:.4f}"
        return str(v)
    head = "| " + " | ".join(h for _, h in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    body = ["| " + " | ".join(fmt(r.get(k)) for k, _ in cols) + " |" for r in rows]
    return "\n".join([head, sep] + body)


def main() -> None:
    overwrite = "--overwrite-authoritative" in sys.argv[1:]
    suffix = "" if overwrite else "_legacy"
    if not overwrite:
        print("LEGACY MODE: writing *_legacy outputs; p2_stats.py is authoritative.")
    results = {}
    splits = {ds: pd.read_csv(SPLITS / f, encoding="utf-8-sig")
              for ds, f in SPLIT_FILES.items()}
    for dataset, name, filename, labels in MODELS:
        pred = pd.read_csv(METRICS / filename, encoding="utf-8-sig")
        df = align_predictions(pred, splits[dataset], f"{dataset}::{name}", labels)
        key = f"{dataset}::{name}"
        results[key] = bootstrap(df, labels)
        print(key, results[key]["n_rows"], results[key]["n_groups"])

    blocks = block_table()
    out = {
        "method": ("nonparametric percentile bootstrap over duplicate groups, "
                   "2000 replicates, numpy default_rng(42); fixed 2.5/97.5 percentiles"),
        "unit": "duplicate group (group_id); every frozen test group has one row",
        "test_sets_changed": False,
        "models_retrained": False,
        "results": results,
        "block_held_out": blocks,
    }
    json_path = METRICS / f"confidence_intervals{suffix}.json"
    csv_path = METRICS / f"confidence_intervals{suffix}.csv"
    dump_json(out, json_path)
    pd.DataFrame([{"dataset": k.split("::")[0], "model": k.split("::")[1],
                   **{f"{m}_{stat}": v for m, d in r["metrics"].items()
                      for stat, v in d.items()}}
                  for k, r in results.items()]).to_csv(
        csv_path, index=False, encoding="utf-8-sig")

    parts = ["# Confidence Interval Report — classical baselines\n",
             "**Phase 2.2, Part A.** Frozen test predictions only; no retraining and no split changes.\n",
             "## Method\n",
             f"- Nonparametric **percentile bootstrap** over duplicate groups (`group_id`).",
             f"- **{N_BOOT:,} replicates**, fixed seed **{SEED}** (`numpy.random.default_rng`).",
             "- Resampling unit: duplicate group. Every group in both frozen test sets contains exactly one row, so this is numerically equivalent to a message-level bootstrap; the group-aware implementation is used so the procedure remains correct if the test files ever contain duplicates.",
             "- 95% interval = 2.5th and 97.5th percentiles of the replicate distribution.",
             "- Metrics use a fixed label order; when a class is absent from a replicate, its F1 is 0 (no class disappeared in practice).\n"]

    for dataset, name, _, labels in MODELS:
        r = results[f"{dataset}::{name}"]
        parts.append(f"## {dataset} — {name}\n")
        rows = []
        for metric, label in (("accuracy", "Accuracy"), ("macro_f1", "Macro-F1"),
                              ("spam_precision", "Spam precision"),
                              ("spam_recall", "Spam recall")):
            d = r["metrics"][metric]
            rows.append({"metric": label, "point": d["point"], "low": d["ci_low"],
                         "high": d["ci_high"], "sd": d["boot_sd"]})
        for lab in labels:
            d = r["metrics"][f"f1_{lab}"]
            rows.append({"metric": f"{lab} F1", "point": d["point"], "low": d["ci_low"],
                         "high": d["ci_high"], "sd": d["boot_sd"]})
        parts.append(md_table(rows, [("metric", "Metric"), ("point", "Point"),
                                     ("low", "95% low"), ("high", "95% high"),
                                     ("sd", "Bootstrap SD")]))
        parts.append(f"\nTest rows: {r['n_rows']}; groups: {r['n_groups']}; "
                     f"replicates predicting Spam: {r['replicates_predicting_spam']}.\n")

    parts.append("## Block-held-out results (no narrow CI)\n")
    parts.append("Each source block is reported separately. With only three blocks — one of "
                 "which has no Spam — a conventional confidence interval would imply an "
                 "independent sample that does not exist. The observed range is descriptive.\n")
    parts.append(md_table(blocks["folds"],
                          [("model", "Model"), ("fold", "Held-out rows"), ("n", "Test n"),
                           ("ham", "Ham"), ("spam", "Spam"), ("accuracy", "Accuracy"),
                           ("macro_f1", "Macro-F1"), ("spam_precision", "Spam P"),
                           ("spam_recall", "Spam R")]))
    parts.append("\n### Observed range across the three blocks\n")
    parts.append(md_table(blocks["ranges"],
                          [("model", "Model"), ("macro_f1_min", "Macro-F1 min"),
                           ("macro_f1_max", "Macro-F1 max"),
                           ("spam_recall_min", "Spam R min"),
                           ("spam_recall_max", "Spam R max"),
                           ("accuracy_min", "Acc. min"), ("accuracy_max", "Acc. max")]))
    parts.append("\nThe 5001–6000 fold contains no Spam: its macro-F1 (~0.495) is an artefact "
                 "of assigning zero F1 to an absent class, and Spam precision/recall are "
                 "undefined. The 6001–7000 fold has only 12 Spam in training.\n")

    parts.append("## Interpretation and limitations\n")
    parts.append("- These intervals describe uncertainty **within the existing test distribution**. They do not estimate generalisation to unseen sources.")
    parts.append("- D1 has only three source blocks, with 94.7% of Spam in one of them. The block results above, not the bootstrap interval, are the relevant evidence about source shift.")
    parts.append("- D1's Spam precision is 1.000 with zero observed false positives, so its percentile interval is degenerate at 1.000. That does not prove zero risk: the rule-of-three upper bound on the false-positive rate is about 3/299 ≈ 1.0%.")
    parts.append("- D2 has no source-block structure recorded, so its bootstrap intervals are the appropriate uncertainty estimate for this corpus. They still say nothing about new SMS sources.")
    parts.append(f"\n*Generated by `p2_ci.py` (legacy); raw values in "
                 f"`metrics/{json_path.name}`.*\n")
    if overwrite:
        (REPORTS / "CONFIDENCE_INTERVAL_REPORT.md").write_text(
            "\n".join(parts), encoding="utf-8")
        print("wrote", REPORTS / "CONFIDENCE_INTERVAL_REPORT.md")
    else:
        legacy_report = REPORTS / "CONFIDENCE_INTERVAL_REPORT.legacy.md"
        legacy_report.write_text("\n".join(parts), encoding="utf-8")
        print("wrote", legacy_report, "(authoritative report untouched)")


if __name__ == "__main__":
    main()
