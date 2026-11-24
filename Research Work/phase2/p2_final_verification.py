#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent verification and uncertainty audit for the frozen experiments.

This script does not train, tune, relabel, resample the split, or write to any
dataset/model/split file. It reads frozen predictions and writes one JSON
artifact plus a console summary.

Key statistical choices:
  * D1/D2 test duplicate groups are all singletons; this is verified, not assumed.
  * One fixed sequence of group-bootstrap resamples is shared by all models.
  * MuRIL seed intervals are test-sample intervals conditional on each frozen seed.
  * The three-seed mean interval is conditional on the three fitted seeds; it is
    not an interval for a new training run.
  * Exact Clopper-Pearson and Wilson intervals are reported for precision,
    recall, and the zero-false-positive rate. These assume exchangeable errors
    and are descriptive, not a claim about future sources.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from p2_common import block_number

BASE = Path(__file__).resolve().parents[2]
PHASE = BASE / "Research Work" / "phase2"
METRICS = PHASE / "metrics"
SPLITS = PHASE / "splits"
OUT = METRICS / "final_verification.json"

N_BOOT = 2000
SEED = 42
D1_LABELS = ["Ham", "Spam"]
D2_LABELS = ["ham", "spam", "smishing"]

D1_FILES = {
    "Logistic Regression": "d1_malayalam_logreg_test_predictions.csv",
    "Linear SVM": "d1_malayalam_linear_svm_test_predictions.csv",
    "MuRIL seed 42": "muril_random_seed42_predictions.csv",
    "MuRIL seed 43": "muril_random_seed43_predictions.csv",
    "MuRIL seed 44": "muril_random_seed44_predictions.csv",
}
D2_FILES = {
    "Logistic Regression": "d2_logreg_test_predictions.csv",
    "Linear SVM": "d2_linear_svm_test_predictions.csv",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def encode(values, labels):
    code = {lab: i for i, lab in enumerate(labels)}
    return np.asarray([code[str(v)] for v in values], dtype=np.int16)


def metric_codes(y, pred, labels):
    if len(y) == 0:
        raise ValueError("metric_codes received no predictions")
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
    spam_i = next(i for i, lab in enumerate(labels) if lab.lower() == "spam")
    out = {
        "n": int(y.size),
        "accuracy": float(tp.sum() / y.size),
        "macro_f1": float(f1.mean()),
        "spam_precision": float(precision[spam_i]),
        "spam_recall": float(recall[spam_i]),
        "spam_f1": float(f1[spam_i]),
        "confusion_matrix": cm.tolist(),
        "support": {lab: int(support[i]) for i, lab in enumerate(labels)},
        "predicted": {lab: int(predicted[i]) for i, lab in enumerate(labels)},
        "per_class": {
            lab: {"precision": float(precision[i]), "recall": float(recall[i]),
                  "f1": float(f1[i]), "support": int(support[i])}
            for i, lab in enumerate(labels)
        },
    }
    for i, lab in enumerate(labels):
        out[f"f1_{lab}"] = float(f1[i])
    return out


def point_metrics(y_true, y_pred, labels):
    return metric_codes(encode(y_true, labels), encode(y_pred, labels), labels)


def cp_interval(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Clopper-Pearson exact interval for a binomial proportion."""
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(centre - half), float(centre + half)


def exact_checks(m: dict, labels: list[str]) -> dict:
    """Binary-only exact checks.

    D2 is three-class. Treating its non-Spam classes as one binary negative
    class would make the FPR denominator meaningless, so this function refuses
    that input instead of emitting a plausible-looking number.
    """
    if len(labels) != 2:
        raise ValueError("exact_checks is binary-only; use multiclass_exact_checks")
    spam_i = next(i for i, lab in enumerate(labels) if lab.lower() == "spam")
    cm = np.asarray(m["confusion_matrix"], dtype=np.int64)
    tp = int(cm[spam_i, spam_i])
    fp = int(cm[:, spam_i].sum() - tp)
    fn = int(cm[spam_i, :].sum() - tp)
    tn = int(m["n"] - tp - fp - fn)
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "predicted_spam": m["predicted"][labels[spam_i]],
        "spam_support": m["support"][labels[spam_i]],
        "precision_denominator": m["predicted"][labels[spam_i]],
        "precision_copper_pearson_95": cp_interval(tp, tp + fp),
        "precision_wilson_95": wilson_interval(tp, tp + fp),
        "recall_copper_pearson_95": cp_interval(tp, tp + fn),
        "recall_wilson_95": wilson_interval(tp, tp + fn),
        "false_positive_rate_copper_pearson_95": cp_interval(fp, fp + tn),
        "false_positive_rate_wilson_95": wilson_interval(fp, fp + tn),
        "note": ("Exact/Wilson intervals are descriptive binomial intervals for "
                 "exchangeable errors. Precision is conditional on the predicted "
                 "positive count; it is not an estimate for a new source."),
    }


def multiclass_exact_checks(m: dict, labels: list[str]) -> dict:
    """Per-class exact intervals for a multiclass confusion matrix.

    No FPR is produced: in a three-class task, "false positive" is not one
    quantity unless a class is explicitly one-vs-rest. Per-class precision and
    recall are unambiguous, so those are returned instead.
    """
    cm = np.asarray(m["confusion_matrix"], dtype=np.int64)
    n = int(m["n"])
    out = {}
    for i, lab in enumerate(labels):
        tp = int(cm[i, i])
        predicted = int(cm[:, i].sum())
        support = int(cm[i, :].sum())
        out[lab] = {
            "tp": tp,
            "predicted": predicted,
            "support": support,
            "precision_denominator": predicted,
            "precision_copper_pearson_95": cp_interval(tp, predicted),
            "precision_wilson_95": wilson_interval(tp, predicted),
            "recall_copper_pearson_95": cp_interval(tp, support),
            "recall_wilson_95": wilson_interval(tp, support),
        }
    return {"per_class": out,
            "note": "Per-class exact intervals; no multiclass FPR is defined here."}


def make_draws(groups: list[str], n_boot: int, seed: int):
    """Generate one shared sequence of group-index draws."""
    rng = np.random.default_rng(seed)
    n = len(groups)
    return [rng.choice(n, size=n, replace=True) for _ in range(n_boot)]


def bootstrap_predictions(y, preds_by_name, group_ids, labels, draws):
    """Percentile intervals for each model and for the mean of MuRIL seeds.

    All models see the same resample of the same test rows. If a class is absent
    from a replicate, its F1 is 0 (the frozen test has enough support that this
    does not occur in practice; the count is recorded).
    """
    groups = {gid: np.asarray(idx) for gid, idx in pd.Series(group_ids).groupby(group_ids).indices.items()}
    gids = list(groups)
    spam_key = "Spam" if "Spam" in labels else "spam"
    reps = {name: [] for name in preds_by_name}
    has_muril = all(f"MuRIL seed {s}" in preds_by_name for s in (42, 43, 44))
    if has_muril:
        reps["MuRIL 3-seed mean"] = []
    missing_spam = 0
    for draw in draws:
        idx = np.concatenate([groups[gids[i]] for i in draw])
        per = {name: metric_codes(y[idx], p[idx], labels)
               for name, p in preds_by_name.items()}
        for name, m in per.items():
            reps[name].append(m)
        if has_muril:
            reps["MuRIL 3-seed mean"].append({
                k: float(np.mean([per[f"MuRIL seed {s}"][k] for s in (42, 43, 44)]))
                for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1")
            })
        if per["Linear SVM"]["support"][spam_key] == 0:
            missing_spam += 1

    out = {}
    for name, rows in reps.items():
        if not rows:
            continue
        keys = ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1")
        out[name] = {}
        for k in keys:
            arr = np.asarray([r[k] for r in rows], dtype=float)
            out[name][k] = {
                "point": float(np.mean([r[k] for r in [metric_codes(y, preds_by_name[name], labels)]])
                               if name != "MuRIL 3-seed mean" else
                               np.mean([metric_codes(y, preds_by_name[f"MuRIL seed {s}"], labels)[k]
                                        for s in (42, 43, 44)])),
                "ci_low": float(np.percentile(arr, 2.5)),
                "ci_high": float(np.percentile(arr, 97.5)),
                "boot_mean": float(arr.mean()),
                "boot_sd": float(arr.std(ddof=1)),
            }
    return out, missing_spam


def paired_interval(y, a_pred, b_pred, group_ids, labels, draws, metric="macro_f1"):
    groups = {gid: np.asarray(idx) for gid, idx in pd.Series(group_ids).groupby(group_ids).indices.items()}
    gids = list(groups)
    obs_a = metric_codes(y, a_pred, labels)[metric]
    obs_b = metric_codes(y, b_pred, labels)[metric]
    diffs = []
    for draw in draws:
        idx = np.concatenate([groups[gids[i]] for i in draw])
        diffs.append(metric_codes(y[idx], a_pred[idx], labels)[metric]
                     - metric_codes(y[idx], b_pred[idx], labels)[metric])
    arr = np.asarray(diffs)
    return {
        "a": float(obs_a), "b": float(obs_b), "difference": float(obs_a - obs_b),
        "ci_low": float(np.percentile(arr, 2.5)),
        "ci_high": float(np.percentile(arr, 97.5)),
        "boot_sd": float(arr.std(ddof=1)),
        "share_positive": float((arr > 0).mean()),
        "share_tie": float((arr == 0).mean()),
        "share_negative": float((arr < 0).mean()),
    }


def main() -> None:
    d1_test = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
    d2_test = pd.read_csv(SPLITS / "d2_test.csv", encoding="utf-8-sig")
    assert len(d1_test) == 299 and d1_test["record_id"].is_unique
    assert len(d2_test) == 883 and d2_test["record_id"].is_unique
    assert d1_test.groupby("group_id").size().max() == 1
    assert d2_test.groupby("group_id").size().max() == 1
    d1_order = d1_test["record_id"].tolist()
    d2_order = d2_test["record_id"].tolist()

    d1_preds = {}
    d1_meta = {}
    for name, f in D1_FILES.items():
        d = pd.read_csv(METRICS / f, encoding="utf-8-sig")
        assert len(d) == 299 and d["record_id"].is_unique
        assert set(d["record_id"]) == set(d1_order), f
        d = d.set_index("record_id").loc[d1_order].reset_index()
        y = d1_test.set_index("record_id").loc[d1_order, "label"].astype(str).to_numpy()
        assert (d["label"].astype(str).to_numpy() == y).all(), f
        d1_preds[name] = encode(d["prediction"].astype(str), D1_LABELS)
        m = metric_codes(encode(y, D1_LABELS), d1_preds[name], D1_LABELS)
        d1_meta[name] = {"file": f, "sha256": sha256(METRICS / f),
                         "rows": int(len(d)), "metrics": m,
                         "exact": exact_checks(m, D1_LABELS)}

    d2_preds = {}
    d2_meta = {}
    for name, f in D2_FILES.items():
        d = pd.read_csv(METRICS / f, encoding="utf-8-sig")
        assert len(d) == 883 and d["record_id"].is_unique
        assert set(d["record_id"]) == set(d2_order), f
        d = d.set_index("record_id").loc[d2_order].reset_index()
        y = d2_test.set_index("record_id").loc[d2_order, "label"].astype(str).to_numpy()
        assert (d["label"].astype(str).to_numpy() == y).all(), f
        d2_preds[name] = encode(d["prediction"].astype(str), D2_LABELS)
        m = metric_codes(encode(y, D2_LABELS), d2_preds[name], D2_LABELS)
        d2_meta[name] = {"file": f, "sha256": sha256(METRICS / f),
                         "rows": int(len(d)), "metrics": m,
                         "exact": multiclass_exact_checks(m, D2_LABELS)}

    y1 = encode(d1_test["label"].astype(str), D1_LABELS)
    y2 = encode(d2_test["label"].astype(str), D2_LABELS)
    draws1 = make_draws(d1_test["group_id"].tolist(), N_BOOT, SEED)
    draws2 = make_draws(d2_test["group_id"].tolist(), N_BOOT, SEED)
    ci1, miss1 = bootstrap_predictions(y1, d1_preds, d1_test["group_id"].tolist(), D1_LABELS, draws1)
    ci2, miss2 = bootstrap_predictions(y2, d2_preds, d2_test["group_id"].tolist(), D2_LABELS, draws2)

    seed_vals = {k: float(d1_meta[f"MuRIL seed {s}"]["metrics"][k]) for k in
                 ("accuracy", "macro_f1", "spam_precision", "spam_recall") for s in (42, 43, 44)}
    across = {}
    for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1"):
        vals = np.asarray([d1_meta[f"MuRIL seed {s}"]["metrics"][k] for s in (42, 43, 44)])
        across[k] = {"mean": float(vals.mean()), "sd": float(vals.std(ddof=1)),
                     "min": float(vals.min()), "max": float(vals.max()),
                     "values": [float(x) for x in vals]}

    svm = d1_preds["Linear SVM"]
    muril_mean_metric = {}
    for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall"):
        muril_mean_metric[k] = float(np.mean([d1_meta[f"MuRIL seed {s}"]["metrics"][k]
                                              for s in (42, 43, 44)]))
    diff_mean = {}
    for k in ("accuracy", "macro_f1", "spam_recall"):
        # Compare SVM to a fixed metric-average of the three frozen MuRIL seeds.
        groups = {gid: np.asarray(idx) for gid, idx in pd.Series(d1_test["group_id"]).groupby(d1_test["group_id"]).indices.items()}
        gids = list(groups)
        diffs = []
        for draw in draws1:
            idx = np.concatenate([groups[gids[i]] for i in draw])
            sv = metric_codes(y1[idx], svm[idx], D1_LABELS)[k]
            mu = np.mean([metric_codes(y1[idx], d1_preds[f"MuRIL seed {s}"][idx], D1_LABELS)[k]
                          for s in (42, 43, 44)])
            diffs.append(sv - mu)
        arr = np.asarray(diffs)
        diff_mean[k] = {"svm": d1_meta["Linear SVM"]["metrics"][k],
                        "muril_mean": muril_mean_metric[k],
                        "difference": float(d1_meta["Linear SVM"]["metrics"][k] - muril_mean_metric[k]),
                        "ci_low": float(np.percentile(arr, 2.5)),
                        "ci_high": float(np.percentile(arr, 97.5)),
                        "share_positive": float((arr > 0).mean()),
                        "share_tie": float((arr == 0).mean()),
                        "share_negative": float((arr < 0).mean())}

    pair_seed = {}
    for s in (42, 43, 44):
        pair_seed[s] = paired_interval(y1, svm, d1_preds[f"MuRIL seed {s}"],
                                       d1_test["group_id"].tolist(), D1_LABELS, draws1)

    # D1 row-block audit from frozen block predictions (not a retrain).
    block_path = METRICS / "block_cv_predictions.csv"
    block = pd.read_csv(block_path, encoding="utf-8-sig")
    block_counts = (d1_test.assign(block=d1_test.source_row.map(block_number))
                    .groupby(["block", "label"]).size().unstack(fill_value=0))
    all_rows = pd.concat([pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
                          for p in ("train", "val", "test")], ignore_index=True)
    all_rows["block"] = all_rows.source_row.map(block_number).astype(int)
    block_all = all_rows.groupby(["block", "label"]).size().unstack(fill_value=0)
    block_folds = []
    for (model, fold), g in block.groupby(["model", "fold"]):
        m = point_metrics(g["label"], g["prediction"], D1_LABELS)
        block_folds.append({"model": model, "fold": fold, "n": m["n"],
                            "ham": m["support"]["Ham"], "spam": m["support"]["Spam"],
                            "accuracy": m["accuracy"], "macro_f1": m["macro_f1"],
                            "spam_precision": m["spam_precision"] if m["support"]["Spam"] else None,
                            "spam_recall": m["spam_recall"] if m["support"]["Spam"] else None})
    for s in (42, 43, 44):
        for b, fold in ((4001, "4001-5000"), (5001, "5001-6000"), (6001, "6001-7000")):
            d = pd.read_csv(METRICS / f"muril_block{b}_seed{s}_predictions.csv", encoding="utf-8-sig")
            assert len(d) == {"4001-5000": 630, "5001-6000": 991, "6001-7000": 371}[fold]
            m = point_metrics(d["label"], d["prediction"], D1_LABELS)
            block_folds.append({"model": f"MuRIL seed {s}", "fold": fold, "n": m["n"],
                                "ham": m["support"]["Ham"], "spam": m["support"]["Spam"],
                                "accuracy": m["accuracy"], "macro_f1": m["macro_f1"],
                                "spam_precision": m["spam_precision"] if m["support"]["Spam"] else None,
                                "spam_recall": m["spam_recall"] if m["support"]["Spam"] else None})
    pooled = []
    for model, g in block.groupby("model"):
        m = point_metrics(g["label"], g["prediction"], D1_LABELS)
        pooled.append({"model": model, "n": m["n"], "accuracy": m["accuracy"],
                       "macro_f1": m["macro_f1"], "spam_precision": m["spam_precision"],
                       "spam_recall": m["spam_recall"], "confusion_matrix": m["confusion_matrix"]})
    for s in (42, 43, 44):
        parts = [pd.read_csv(METRICS / f"muril_block{b}_seed{s}_predictions.csv", encoding="utf-8-sig")
                 for b in (4001, 5001, 6001)]
        d = pd.concat(parts, ignore_index=True)
        m = point_metrics(d["label"], d["prediction"], D1_LABELS)
        pooled.append({"model": f"MuRIL seed {s}", "n": m["n"], "accuracy": m["accuracy"],
                       "macro_f1": m["macro_f1"], "spam_precision": m["spam_precision"],
                       "spam_recall": m["spam_recall"], "confusion_matrix": m["confusion_matrix"]})

    out = {
        "audit": "Frozen-prediction verification; no model was trained or modified.",
        "bootstrap": {"n_boot": N_BOOT, "seed": SEED, "unit": "duplicate group",
                      "method": "percentile bootstrap, 2.5/97.5 percentiles",
                      "d1_groups": int(d1_test.group_id.nunique()),
                      "d1_max_group_size": int(d1_test.groupby("group_id").size().max()),
                      "d2_groups": int(d2_test.group_id.nunique()),
                      "d2_max_group_size": int(d2_test.groupby("group_id").size().max()),
                      "replicates_missing_d1_spam": miss1,
                      "replicates_missing_d2_spam": miss2},
        "d1_test": {"rows": len(d1_test), "labels": d1_test["label"].value_counts().to_dict(),
                    "block_composition": block_counts.to_dict(orient="index")},
        "d2_test": {"rows": len(d2_test), "labels": d2_test["label"].value_counts().to_dict()},
        "d1_models": d1_meta,
        "d1_bootstrap": ci1,
        "muril_across_seed": across,
        "muril_three_seed_mean_bootstrap": ci1.get("MuRIL 3-seed mean"),
        "svm_vs_muril_mean": diff_mean,
        "svm_vs_muril_seed": pair_seed,
        "d2_models": d2_meta,
        "d2_bootstrap": ci2,
        "d1_block_all_composition": block_all.to_dict(orient="index"),
        "d1_block_folds": block_folds,
        "d1_block_pooled": pooled,
        "notes": [
            "D1 and D2 test duplicate groups are all singletons; the group bootstrap is therefore numerically a message bootstrap.",
            "The three-seed mean interval is conditional on the three frozen MuRIL seeds and captures test-sample uncertainty only.",
            "Across-seed SD is reported separately; it is not a confidence interval and three seeds do not estimate a training-run population.",
            "Exact/Wilson precision intervals condition on the number of predicted positives; 30/30 and 29/29 do not mean zero future false positives.",
            "Block folds are a leave-one-row-block-out stress test, not a source-population estimate.",
        ],
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "out": str(OUT),
        "d1": {k: {"macro_f1": v["metrics"]["macro_f1"],
                   "acc": v["metrics"]["accuracy"],
                   "spam_precision": v["metrics"]["spam_precision"],
                   "spam_recall": v["metrics"]["spam_recall"],
                   "pred_spam": v["metrics"]["predicted"]["Spam"],
                   "exact_precision": v["exact"]["precision_copper_pearson_95"]}
               for k, v in d1_meta.items()},
        "muril_mean_ci": ci1.get("MuRIL 3-seed mean", {}).get("macro_f1"),
        "svm_vs_muril_mean": diff_mean,
        "d2": {k: {"macro_f1": v["metrics"]["macro_f1"],
                   "acc": v["metrics"]["accuracy"]} for k, v in d2_meta.items()},
        "block_pooled": pooled,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
