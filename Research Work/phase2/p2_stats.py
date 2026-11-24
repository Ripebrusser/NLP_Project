#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2.3 Parts A/B: complete CIs and paired group bootstrap.

Reads frozen predictions only. No model is trained here.

Outputs
  metrics/confidence_intervals.json / .csv          (complete, incl. MuRIL)
  metrics/muril_seed_variation.json / .csv          (within-seed vs across-seed)
  metrics/paired_model_comparison.json / .csv       (paired differences)
  metrics/block_paired_comparison.csv               (pooled block sensitivity)
  reports/statistical_tables.md                     (machine tables)
"""
from __future__ import annotations

import json
from itertools import combinations

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, f1_score, precision_recall_fscore_support)

from p2_common import METRICS, REPORTS, SPLITS, align_predictions, dump_json

N_BOOT = 2000
SEED = 42
D1_LABELS = ["Ham", "Spam"]
D2_LABELS = ["ham", "spam", "smishing"]


def encode(values, labels: list[str]) -> np.ndarray:
    code = {lab: i for i, lab in enumerate(labels)}
    return np.asarray([code[str(v)] for v in values], dtype=np.int16)


def metrics_from_codes(y: np.ndarray, pred: np.ndarray, labels: list[str]) -> dict:
    """Fast metrics from integer-coded labels, used in every bootstrap replicate."""
    if len(y) == 0:
        raise ValueError("metrics_from_codes received no predictions")
    k = len(labels)
    cm = np.zeros((k, k), dtype=np.int64)
    np.add.at(cm, (y, pred), 1)
    tp = np.diag(cm).astype(float)
    support = cm.sum(axis=1).astype(float)
    predicted = cm.sum(axis=0).astype(float)
    precision = np.divide(tp, predicted, out=np.zeros(k), where=predicted > 0)
    recall = np.divide(tp, support, out=np.zeros(k), where=support > 0)
    f1 = np.divide(2 * precision * recall, precision + recall,
                   out=np.zeros(k), where=(precision + recall) > 0)
    spam = next(i for i, lab in enumerate(labels) if lab.lower() == "spam")
    out = {
        "n": int(y.size),
        "accuracy": float(tp.sum() / max(y.size, 1)),
        "macro_f1": float(f1.mean()),
        "spam_precision": float(precision[spam]),
        "spam_recall": float(recall[spam]),
        "spam_f1": float(f1[spam]),
        "spam_support": int(support[spam]),
        "confusion_matrix": cm.tolist(),
    }
    for j, lab in enumerate(labels):
        out[f"f1_{lab}"] = float(f1[j])
        out[f"precision_{lab}"] = float(precision[j])
        out[f"recall_{lab}"] = float(recall[j])
        out[f"support_{lab}"] = int(support[j])
    return out


def point_metrics(y_true, y_pred, labels: list[str]) -> dict:
    return metrics_from_codes(encode(y_true, labels), encode(y_pred, labels), labels)


def metric_keys(labels: list[str]) -> list[str]:
    keys = ["accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1"]
    for lab in labels:
        keys += [f"f1_{lab}", f"precision_{lab}", f"recall_{lab}"]
    return keys


def bootstrap(df: pd.DataFrame, labels: list[str], n_boot: int = N_BOOT,
              seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    groups = {gid: np.asarray(idx) for gid, idx in df.groupby("group_id").indices.items()}
    gids = list(groups)
    y = encode(df["label"], labels)
    pred = encode(df["prediction"], labels)
    point = metrics_from_codes(y, pred, labels)
    reps = {k: [] for k in metric_keys(labels)}
    for _ in range(n_boot):
        draw = rng.choice(len(gids), size=len(gids), replace=True)
        idx = np.concatenate([groups[gids[i]] for i in draw])
        m = metrics_from_codes(y[idx], pred[idx], labels)
        for k in reps:
            reps[k].append(m[k])
    out = {}
    for k, vals in reps.items():
        arr = np.asarray(vals)
        out[k] = {
            "point": float(point[k]),
            "ci_low": float(np.percentile(arr, 2.5)),
            "ci_high": float(np.percentile(arr, 97.5)),
            "boot_mean": float(arr.mean()),
            "boot_sd": float(arr.std(ddof=1)),
        }
    return {
        "n_boot": n_boot, "seed": seed,
        "n_groups": len(gids), "n_rows": int(len(df)),
        "rows_per_group_max": float(df.groupby("group_id").size().max()),
        "metrics": out,
    }


def load_d1_models() -> dict[str, pd.DataFrame]:
    test = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
    out = {}
    for name, f in (("Linear SVM", "d1_malayalam_linear_svm_test_predictions.csv"),
                    ("Logistic Regression", "d1_malayalam_logreg_test_predictions.csv")):
        d = pd.read_csv(METRICS / f, encoding="utf-8-sig")
        out[name] = align_predictions(d, test, f"D1::{name}", D1_LABELS)
    for seed in (42, 43, 44):
        f = f"muril_random_seed{seed}_predictions.csv"
        d = pd.read_csv(METRICS / f, encoding="utf-8-sig")
        out[f"MuRIL seed {seed}"] = align_predictions(d, test, f"D1::MuRIL seed {seed}",
                                                      D1_LABELS)
    return out


def load_d2_models() -> dict[str, pd.DataFrame]:
    test = pd.read_csv(SPLITS / "d2_test.csv", encoding="utf-8-sig")
    out = {}
    for name, f in (("Logistic Regression", "d2_logreg_test_predictions.csv"),
                    ("Linear SVM", "d2_linear_svm_test_predictions.csv")):
        d = pd.read_csv(METRICS / f, encoding="utf-8-sig")
        out[name] = align_predictions(d, test, f"D2::{name}", D2_LABELS)
    return out


def paired_bootstrap(a: pd.DataFrame, b: pd.DataFrame, labels: list[str],
                     n_boot: int = N_BOOT, seed: int = SEED,
                     metrics=("macro_f1", "spam_recall", "accuracy", "spam_precision")) -> dict:
    a = a[["record_id", "group_id", "label", "prediction"]].rename(
        columns={"prediction": "pred_a"})
    b = b[["record_id", "label", "prediction"]].rename(columns={"prediction": "pred_b"})
    d = a.merge(b, on="record_id", suffixes=("", "_b"), validate="one_to_one")
    if not (d["label"] == d["label_b"]).all():
        raise SystemExit("paired label mismatch")
    d["label"] = d["label"].astype(str)
    groups = {gid: np.asarray(idx) for gid, idx in d.groupby("group_id").indices.items()}
    gids = list(groups)
    y = encode(d["label"], labels)
    pa = encode(d["pred_a"], labels)
    pb = encode(d["pred_b"], labels)
    point_a = metrics_from_codes(y, pa, labels)
    point_b = metrics_from_codes(y, pb, labels)
    rng = np.random.default_rng(seed)
    reps = {k: [] for k in metrics}
    for _ in range(n_boot):
        draw = rng.choice(len(gids), size=len(gids), replace=True)
        idx = np.concatenate([groups[gids[i]] for i in draw])
        ma = metrics_from_codes(y[idx], pa[idx], labels)
        mb = metrics_from_codes(y[idx], pb[idx], labels)
        for k in metrics:
            reps[k].append(ma[k] - mb[k])
    out = {"n_rows": int(len(d)), "n_groups": len(gids), "metrics": {}}
    for k, vals in reps.items():
        arr = np.asarray(vals)
        obs = point_a[k] - point_b[k]
        out["metrics"][k] = {
            "a": float(point_a[k]), "b": float(point_b[k]),
            "difference": float(obs),
            "ci_low": float(np.percentile(arr, 2.5)),
            "ci_high": float(np.percentile(arr, 97.5)),
            "boot_sd": float(arr.std(ddof=1)),
            "share_positive": float((arr > 0).mean()),
            "share_negative": float((arr < 0).mean()),
            "share_tie": float((arr == 0).mean()),
        }
    return out


def block_pairs() -> tuple[list[dict], pd.DataFrame]:
    full = pd.concat([pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
                      for p in ("train", "val", "test")], ignore_index=True)
    groups = full.set_index("record_id")["group_id"]
    classic = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
    classic["group_id"] = classic["record_id"].map(groups)
    muril = []
    for seed in (42, 43, 44):
        for b in (4001, 5001, 6001):
            d = pd.read_csv(METRICS / f"muril_block{b}_seed{seed}_predictions.csv",
                            encoding="utf-8-sig")
            d["group_id"] = d["record_id"].map(groups)
            d["model"] = f"MuRIL seed {seed}"
            d["fold"] = f"{b}-{b + 999}"
            muril.append(d)
    muril = pd.concat(muril, ignore_index=True)
    frames = {}
    for m, g in classic.groupby("model"):
        frames[{"logreg": "Logistic Regression", "linear_svm": "Linear SVM"}[m]] = g
    for seed in (42, 43, 44):
        frames[f"MuRIL seed {seed}"] = muril[muril.model == f"MuRIL seed {seed}"]
    rows = []
    pairs = [("Logistic Regression", "Linear SVM"),
             ("Logistic Regression", "MuRIL seed 42"),
             ("Linear SVM", "MuRIL seed 42"),
             ("Linear SVM", "MuRIL seed 43"),
             ("Linear SVM", "MuRIL seed 44")]
    for a, b in pairs:
        if a not in frames or b not in frames:
            continue
        for subset in ("pooled", "6001-7000"):
            fa, fb = frames[a], frames[b]
            if subset != "pooled":
                fa = fa[fa.fold == subset]
                fb = fb[fb.fold == subset]
            r = paired_bootstrap(fa, fb, D1_LABELS)
            r.update({"a_model": a, "b_model": b, "subset": subset,
                      "note": ("pooled out-of-fold block predictions; three source blocks only"
                               if subset == "pooled" else
                               "single held-out block; descriptive only")})
            rows.append(r)
    flat = []
    for r in rows:
        for k, d in r["metrics"].items():
            flat.append({"a_model": r["a_model"], "b_model": r["b_model"],
                         "subset": r["subset"], "metric": k,
                         "a": d["a"], "b": d["b"], "difference": d["difference"],
                         "ci_low": d["ci_low"], "ci_high": d["ci_high"],
                         "boot_sd": d["boot_sd"], "share_positive": d["share_positive"],
                         "share_negative": d["share_negative"], "n_rows": r["n_rows"],
                         "n_groups": r["n_groups"]})
    pd.DataFrame(flat).to_csv(METRICS / "block_paired_comparison.csv",
                              index=False, encoding="utf-8-sig")
    return rows, pd.DataFrame(flat)


def fmt(v, nd=4):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def md_table(rows, cols):
    head = "| " + " | ".join(h for _, h in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    body = ["| " + " | ".join(fmt(r.get(k)) for k, _ in cols) + " |" for r in rows]
    return "\n".join([head, sep] + body)


def main() -> None:
    d1 = load_d1_models()
    d2 = load_d2_models()
    ci = {}
    for name, df in d1.items():
        ci[f"D1::{name}"] = bootstrap(df, D1_LABELS)
        print("D1", name, ci[f"D1::{name}"]["n_rows"], ci[f"D1::{name}"]["n_groups"])
    for name, df in d2.items():
        ci[f"D2::{name}"] = bootstrap(df, D2_LABELS)
        print("D2", name, ci[f"D2::{name}"]["n_rows"], ci[f"D2::{name}"]["n_groups"])

    # across-seed variation: point metrics, not a combined CI
    seed_rows = []
    for seed in (42, 43, 44):
        key = f"D1::MuRIL seed {seed}"
        m = {k: v["point"] for k, v in ci[key]["metrics"].items()}
        seed_rows.append({"seed": seed, **m})
    seed_df = pd.DataFrame(seed_rows)
    seed_variation = {}
    for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1",
              "f1_Ham", "f1_Spam"):
        vals = seed_df[k].to_numpy()
        seed_variation[k] = {"mean": float(vals.mean()), "sd": float(vals.std(ddof=1)),
                             "min": float(vals.min()), "max": float(vals.max()),
                             "values": [float(x) for x in vals]}
    seed_df.to_csv(METRICS / "muril_seed_variation.csv", index=False,
                   encoding="utf-8-sig")
    dump_json({"note": ("Within-seed bootstrap intervals are separate from across-seed "
                        "variation; no combined interval is formed."),
               "per_seed": seed_rows, "across_seed": seed_variation},
              METRICS / "muril_seed_variation.json")

    # paired comparisons on the frozen random test
    pairs = [
        ("D1", "Logistic Regression", "Linear SVM"),
        ("D1", "Logistic Regression", "MuRIL seed 42"),
        ("D1", "Linear SVM", "MuRIL seed 42"),
        ("D1", "Logistic Regression", "MuRIL seed 43"),
        ("D1", "Linear SVM", "MuRIL seed 43"),
        ("D1", "Logistic Regression", "MuRIL seed 44"),
        ("D1", "Linear SVM", "MuRIL seed 44"),
        ("D2", "Logistic Regression", "Linear SVM"),
    ]
    paired = []
    for dataset, a, b in pairs:
        source = d1 if dataset == "D1" else d2
        labels = D1_LABELS if dataset == "D1" else D2_LABELS
        r = paired_bootstrap(source[a], source[b], labels)
        r.update({"dataset": dataset, "a_model": a, "b_model": b,
                  "subset": "random test"})
        paired.append(r)
        print("paired", dataset, a, "vs", b,
              "macroF1 diff", round(r["metrics"]["macro_f1"]["difference"], 4),
              "CI", tuple(round(r["metrics"]["macro_f1"][k], 4)
                          for k in ("ci_low", "ci_high")))
    flat = []
    for r in paired:
        for k, d in r["metrics"].items():
            flat.append({"dataset": r["dataset"], "a_model": r["a_model"],
                         "b_model": r["b_model"], "subset": r["subset"], "metric": k,
                         "a": d["a"], "b": d["b"], "difference": d["difference"],
                         "ci_low": d["ci_low"], "ci_high": d["ci_high"],
                         "boot_sd": d["boot_sd"], "share_positive": d["share_positive"],
                         "share_negative": d["share_negative"], "n_rows": r["n_rows"],
                         "n_groups": r["n_groups"]})
    pd.DataFrame(flat).to_csv(METRICS / "paired_model_comparison.csv", index=False,
                              encoding="utf-8-sig")
    dump_json({"method": ("paired nonparametric percentile bootstrap over duplicate "
                          "groups; the same group resample is used for both models; "
                          f"{N_BOOT} replicates; seed {SEED}"),
               "note": ("The same resample is used for both predictions, so intervals "
                        "are for the paired difference. No model was retrained."),
               "pairs": paired}, METRICS / "paired_model_comparison.json")

    block_rows, block_flat = block_pairs()

    # complete block table incl. MuRIL (no conventional CI)
    cbp = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
    block_folds = []
    for (model, fold), g in cbp.groupby(["model", "fold"]):
        m = point_metrics(g["label"], g["prediction"], D1_LABELS)
        block_folds.append({"model": model, "fold": fold, "n": m["n"],
                            "ham": m["support_Ham"], "spam": m["support_Spam"],
                            "accuracy": m["accuracy"], "macro_f1": m["macro_f1"],
                            "spam_precision": m["spam_precision"] if m["spam_support"] else None,
                            "spam_recall": m["spam_recall"] if m["spam_support"] else None,
                            "spam_f1": m["spam_f1"] if m["spam_support"] else None,
                            "evaluable_for_spam": bool(m["spam_support"])})
    for seed in (42, 43, 44):
        for b, fold in ((4001, "4001-5000"), (5001, "5001-6000"), (6001, "6001-7000")):
            d = pd.read_csv(METRICS / f"muril_block{b}_seed{seed}_predictions.csv",
                            encoding="utf-8-sig")
            m = point_metrics(d["label"], d["prediction"], D1_LABELS)
            block_folds.append({"model": f"MuRIL seed {seed}", "fold": fold, "n": m["n"],
                                "ham": m["support_Ham"], "spam": m["support_Spam"],
                                "accuracy": m["accuracy"], "macro_f1": m["macro_f1"],
                                "spam_precision": m["spam_precision"] if m["spam_support"] else None,
                                "spam_recall": m["spam_recall"] if m["spam_support"] else None,
                                "spam_f1": m["spam_f1"] if m["spam_support"] else None,
                                "evaluable_for_spam": bool(m["spam_support"])})

    out = {
        "method": (f"nonparametric percentile bootstrap over duplicate groups, "
                   f"{N_BOOT} replicates, numpy default_rng({SEED}); 2.5/97.5 percentiles"),
        "unit": "duplicate group (group_id); every frozen test group has one row",
        "test_sets_changed": False,
        "models_retrained": False,
        "results": ci,
        "muril_seed_variation": seed_variation,
        "paired": paired,
        "block_paired": block_rows,
        "block_held_out": {"folds": block_folds,
                           "note": ("Three source blocks only; 5001-6000 has no Spam. "
                                    "No conventional confidence interval is reported for "
                                    "these descriptive folds.")},
    }
    dump_json(out, METRICS / "confidence_intervals.json")

    rows = []
    for key, r in ci.items():
        dataset, model = key.split("::")
        for metric, d in r["metrics"].items():
            rows.append({"dataset": dataset, "model": model, "metric": metric,
                         **d, "n_rows": r["n_rows"], "n_groups": r["n_groups"]})
    pd.DataFrame(rows).to_csv(METRICS / "confidence_intervals.csv", index=False,
                              encoding="utf-8-sig")

    # machine-readable tables
    parts = ["# Phase 2.3 statistical tables", "",
             "Generated by `p2_stats.py` from frozen predictions. Do not edit by hand.", "",
             "## Confidence intervals — D1", "",
             md_table([{"model": k.split("::")[1],
                        **{f"{m}_{s}": v for m, d in r["metrics"].items()
                           for s, v in d.items() if s in ("point", "ci_low", "ci_high")}}
                       for k, r in ci.items() if k.startswith("D1::")],
                      [("model", "Model")] +
                      [(f"{m}_{s}", f"{m} {s}") for m in
                       ("accuracy", "macro_f1", "spam_precision", "spam_recall",
                        "f1_Ham", "f1_Spam")
                       for s in ("point", "ci_low", "ci_high")]),
             "", "## Confidence intervals — D2", "",
             md_table([{"model": k.split("::")[1],
                        **{f"{m}_{s}": v for m, d in r["metrics"].items()
                           for s, v in d.items() if s in ("point", "ci_low", "ci_high")}}
                       for k, r in ci.items() if k.startswith("D2::")],
                      [("model", "Model")] +
                      [(f"{m}_{s}", f"{m} {s}") for m in
                       ("accuracy", "macro_f1", "f1_smishing", "precision_smishing",
                        "recall_smishing", "spam_precision", "spam_recall")
                       for s in ("point", "ci_low", "ci_high")]),
             "", "## MuRIL seed variation", "",
             md_table([{"metric": k, **v} for k, v in seed_variation.items()],
                      [("metric", "Metric"), ("mean", "Mean"), ("sd", "SD"),
                       ("min", "Min"), ("max", "Max")]),
             "", "## Paired random-test differences (A − B)", "",
             md_table([{"dataset": r["dataset"], "a": r["a_model"], "b": r["b_model"],
                        **{f"{k}_{s}": v for k, d in r["metrics"].items()
                           for s, v in d.items() if s in ("difference", "ci_low", "ci_high")}}
                       for r in paired],
                      [("dataset", "Set"), ("a", "A"), ("b", "B")] +
                      [(f"{m}_{s}", f"{m} {s}") for m in
                       ("macro_f1", "spam_recall") for s in
                       ("difference", "ci_low", "ci_high")]),
             "", "## Block-pooled paired differences (A − B)", "",
             md_table([{"subset": r["subset"], "a": r["a_model"], "b": r["b_model"],
                        **{f"{k}_{s}": v for k, d in r["metrics"].items()
                           for s, v in d.items() if s in ("difference", "ci_low", "ci_high")}}
                       for r in block_rows],
                      [("subset", "Subset"), ("a", "A"), ("b", "B")] +
                      [(f"{m}_{s}", f"{m} {s}") for m in
                       ("macro_f1", "spam_recall") for s in
                       ("difference", "ci_low", "ci_high")]),
             ""]
    (REPORTS / "statistical_tables.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote CI, paired, seed variation and statistical tables")


if __name__ == "__main__":
    main()
