#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent final audit statistics for the frozen D1/D2 artifacts.

This script reads only frozen splits and prediction files. It does not train,
tune, relabel, or rewrite any dataset, split, model, or existing prediction.

It exists to resolve the LR-SVM direction inconsistency in the historical model
selection report and to place every headline interval in one machine-readable
artifact. The original verifier is preserved; this is a second, independent
calculation with the same frozen inputs.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta, binomtest
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support

from p2_common import block_number

BASE = Path(__file__).resolve().parents[2]
PHASE = BASE / "Research Work" / "phase2"
METRICS = PHASE / "metrics"
SPLITS = PHASE / "splits"
OUT = METRICS / "final_audit_stats.json"

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
    return {
        "n": int(y.size),
        "accuracy": float(tp.sum() / y.size),
        "macro_f1": float(f1.mean()),
        "spam_precision": float(precision[spam_i]),
        "spam_recall": float(recall[spam_i]),
        "spam_f1": float(f1[spam_i]),
        "spam_support": int(support[spam_i]),
        "predicted_spam": int(predicted[spam_i]),
        "confusion_matrix": cm.tolist(),
    }


def cp(k: int, n: int, alpha: float = 0.05):
    if n == 0:
        return [0.0, 1.0]
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def wilson(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [float(centre - half), float(centre + half)]


def exact_checks(m, labels):
    """Binary-only exact checks; multiclass input is rejected explicitly."""
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
        "predicted_spam": int(m["predicted_spam"]),
        "precision_cp95": cp(tp, tp + fp),
        "precision_wilson95": wilson(tp, tp + fp),
        "recall_cp95": cp(tp, tp + fn),
        "recall_wilson95": wilson(tp, tp + fn),
        "fpr_cp95": cp(fp, fp + tn),
        "fpr_wilson95": wilson(fp, fp + tn),
    }


def multiclass_exact_checks(m, labels):
    """Per-class exact precision/recall intervals for a multiclass matrix."""
    cm = np.asarray(m["confusion_matrix"], dtype=np.int64)
    out = {}
    for i, lab in enumerate(labels):
        tp = int(cm[i, i])
        predicted = int(cm[:, i].sum())
        support = int(cm[i, :].sum())
        out[lab] = {
            "tp": tp, "predicted": predicted, "support": support,
            "precision_cp95": cp(tp, predicted),
            "precision_wilson95": wilson(tp, predicted),
            "recall_cp95": cp(tp, support),
            "recall_wilson95": wilson(tp, support),
        }
    return {"per_class": out,
            "note": "Per-class exact intervals; no multiclass FPR is defined here."}


def make_draws(groups, n_boot=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    n = len(groups)
    return [rng.choice(n, size=n, replace=True) for _ in range(n_boot)]


def bootstrap(y, preds, group_ids, labels, draws):
    groups = {gid: np.asarray(idx)
              for gid, idx in pd.Series(group_ids).groupby(group_ids).indices.items()}
    gids = list(groups)
    reps = {name: [] for name in preds}
    has_muril_seeds = all(f"MuRIL seed {s}" in preds for s in (42, 43, 44))
    if has_muril_seeds:
        reps["MuRIL 3-seed mean"] = []
    for draw in draws:
        idx = np.concatenate([groups[gids[i]] for i in draw])
        per = {name: metric_codes(y[idx], p[idx], labels) for name, p in preds.items()}
        for name, m in per.items():
            reps[name].append(m)
        if has_muril_seeds:
            reps["MuRIL 3-seed mean"].append({
                k: float(np.mean([per[f"MuRIL seed {s}"][k] for s in (42, 43, 44)]))
                for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1")
            })
    out = {}
    for name, rows in reps.items():
        out[name] = {}
        for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1"):
            arr = np.asarray([r[k] for r in rows], dtype=float)
            out[name][k] = {
                "point": (float(np.mean([metric_codes(y, preds[f"MuRIL seed {s}"], labels)[k]
                                         for s in (42, 43, 44)]))
                          if name == "MuRIL 3-seed mean"
                          else float(metric_codes(y, preds[name], labels)[k])),
                "ci_low": float(np.percentile(arr, 2.5)),
                "ci_high": float(np.percentile(arr, 97.5)),
                "boot_mean": float(arr.mean()),
                "boot_median": float(np.median(arr)),
                "boot_sd": float(arr.std(ddof=1)),
            }
    return out


def paired(y, a, b, group_ids, labels, draws, metric):
    groups = {gid: np.asarray(idx)
              for gid, idx in pd.Series(group_ids).groupby(group_ids).indices.items()}
    gids = list(groups)
    obs_a = metric_codes(y, a, labels)[metric]
    obs_b = metric_codes(y, b, labels)[metric]
    diffs = []
    for draw in draws:
        idx = np.concatenate([groups[gids[i]] for i in draw])
        diffs.append(metric_codes(y[idx], a[idx], labels)[metric]
                     - metric_codes(y[idx], b[idx], labels)[metric])
    arr = np.asarray(diffs)
    # Exact McNemar-style discordance test for the two-class predictions.
    wrong_a = a != y
    wrong_b = b != y
    n01 = int(np.sum(wrong_a & ~wrong_b))
    n10 = int(np.sum(~wrong_a & wrong_b))
    return {
        "a": float(obs_a), "b": float(obs_b),
        "difference": float(obs_a - obs_b),
        "ci_low": float(np.percentile(arr, 2.5)),
        "ci_high": float(np.percentile(arr, 97.5)),
        "boot_mean": float(arr.mean()),
        "boot_median": float(np.median(arr)),
        "boot_min": float(arr.min()),
        "boot_max": float(arr.max()),
        "q05": float(np.percentile(arr, 5)),
        "q95": float(np.percentile(arr, 95)),
        "boot_sd": float(arr.std(ddof=1)),
        "share_positive": float((arr > 0).mean()),
        "share_tie": float((arr == 0).mean()),
        "share_negative": float((arr < 0).mean()),
        "a_wrong_b_right": n01,
        "a_right_b_wrong": n10,
        "discordant_pairs": n01 + n10,
        "discordance_exact_two_sided_p": (
            float(binomtest(min(n01, n10), n01 + n10, 0.5).pvalue)
            if n01 + n10 else 1.0
        ),
        "observed_inside_interval": bool(
            np.percentile(arr, 2.5) <= (obs_a - obs_b) <= np.percentile(arr, 97.5)
        ),
    }


def main():
    d1 = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
    d2 = pd.read_csv(SPLITS / "d2_test.csv", encoding="utf-8-sig")
    assert len(d1) == 299 and len(d2) == 883
    assert d1.groupby("group_id").size().max() == 1
    assert d2.groupby("group_id").size().max() == 1
    d1_order = d1.record_id.tolist()
    d2_order = d2.record_id.tolist()
    y1 = encode(d1.label, D1_LABELS)
    y2 = encode(d2.label, D2_LABELS)
    draws1 = make_draws(d1.group_id.tolist())
    draws2 = make_draws(d2.group_id.tolist())

    p1 = {}
    meta1 = {}
    for name, fn in D1_FILES.items():
        p = pd.read_csv(METRICS / fn, encoding="utf-8-sig")
        assert set(p.record_id) == set(d1_order) and p.record_id.is_unique
        p = p.set_index("record_id").loc[d1_order].reset_index()
        assert (p.label.astype(str).to_numpy() == d1.label.astype(str).to_numpy()).all()
        p1[name] = encode(p.prediction, D1_LABELS)
        m = metric_codes(y1, p1[name], D1_LABELS)
        meta1[name] = {"file": fn, "sha256": sha256(METRICS / fn),
                       "rows": len(p), "metrics": m,
                       "exact": exact_checks(m, D1_LABELS)}

    p2 = {}
    meta2 = {}
    for name, fn in D2_FILES.items():
        p = pd.read_csv(METRICS / fn, encoding="utf-8-sig")
        assert set(p.record_id) == set(d2_order) and p.record_id.is_unique
        p = p.set_index("record_id").loc[d2_order].reset_index()
        assert (p.label.astype(str).to_numpy() == d2.label.astype(str).to_numpy()).all()
        p2[name] = encode(p.prediction, D2_LABELS)
        m = metric_codes(y2, p2[name], D2_LABELS)
        meta2[name] = {"file": fn, "sha256": sha256(METRICS / fn),
                       "rows": len(p), "metrics": m,
                       "exact": multiclass_exact_checks(m, D2_LABELS)}

    ci1 = bootstrap(y1, p1, d1.group_id.tolist(), D1_LABELS, draws1)
    ci2 = bootstrap(y2, p2, d2.group_id.tolist(), D2_LABELS, draws2)

    pairs = {}
    for metric in ("macro_f1", "spam_recall", "accuracy"):
        pairs[f"LR_minus_SVM_{metric}"] = paired(
            y1, p1["Logistic Regression"], p1["Linear SVM"],
            d1.group_id.tolist(), D1_LABELS, draws1, metric)
        pairs[f"SVM_minus_LR_{metric}"] = paired(
            y1, p1["Linear SVM"], p1["Logistic Regression"],
            d1.group_id.tolist(), D1_LABELS, draws1, metric)
    for seed in (42, 43, 44):
        pairs[f"SVM_minus_MuRIL_seed{seed}_macro_f1"] = paired(
            y1, p1["Linear SVM"], p1[f"MuRIL seed {seed}"],
            d1.group_id.tolist(), D1_LABELS, draws1, "macro_f1")

    # MuRIL mean must be computed by averaging metrics, not by majority-voting
    # the three seed predictions. The latter is not the reported estimand.
    muril_diffs = {}
    groups = {gid: np.asarray(idx)
              for gid, idx in pd.Series(d1.group_id).groupby(d1.group_id).indices.items()}
    gids = list(groups)
    for metric in ("macro_f1", "spam_recall", "accuracy"):
        obs_svm = metric_codes(y1, p1["Linear SVM"], D1_LABELS)[metric]
        obs_mu = float(np.mean([metric_codes(y1, p1[f"MuRIL seed {s}"], D1_LABELS)[metric]
                                for s in (42, 43, 44)]))
        vals = []
        for draw in draws1:
            idx = np.concatenate([groups[gids[i]] for i in draw])
            sv = metric_codes(y1[idx], p1["Linear SVM"][idx], D1_LABELS)[metric]
            mu = np.mean([metric_codes(y1[idx], p1[f"MuRIL seed {s}"][idx], D1_LABELS)[metric]
                          for s in (42, 43, 44)])
            vals.append(sv - mu)
        arr = np.asarray(vals)
        muril_diffs[metric] = {
            "svm": float(obs_svm), "muril_mean": obs_mu,
            "difference": float(obs_svm - obs_mu),
            "ci_low": float(np.percentile(arr, 2.5)),
            "ci_high": float(np.percentile(arr, 97.5)),
            "share_positive": float((arr > 0).mean()),
            "share_tie": float((arr == 0).mean()),
            "share_negative": float((arr < 0).mean()),
            "observed_inside_interval": bool(
                np.percentile(arr, 2.5) <= (obs_svm - obs_mu) <= np.percentile(arr, 97.5)
            ),
        }

    pairs["D2_LR_minus_SVM_macro_f1"] = paired(
        y2, p2["Logistic Regression"], p2["Linear SVM"],
        d2.group_id.tolist(), D2_LABELS, draws2, "macro_f1")

    # D1 test block composition, derived from the frozen manifest only.
    d1 = d1.copy()
    d1["block"] = d1.source_row.map(block_number).astype(int)
    block_test = d1.groupby(["block", "label"]).size().unstack(fill_value=0)
    all_parts = [pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
                 for p in ("train", "val", "test")]
    all_rows = pd.concat(all_parts, ignore_index=True)
    all_rows["block"] = all_rows.source_row.map(block_number).astype(int)
    block_all = all_rows.groupby(["block", "label"]).size().unstack(fill_value=0)

    block = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
    pooled = {}
    for model, g in block.groupby("model"):
        pooled[model] = metric_codes(encode(g.label, D1_LABELS),
                                     encode(g.prediction, D1_LABELS), D1_LABELS)
    for seed in (42, 43, 44):
        d = pd.concat([pd.read_csv(METRICS / f"muril_block{b}_seed{seed}_predictions.csv",
                                   encoding="utf-8-sig")
                       for b in (4001, 5001, 6001)], ignore_index=True)
        pooled[f"MuRIL seed {seed}"] = metric_codes(encode(d.label, D1_LABELS),
                                                    encode(d.prediction, D1_LABELS), D1_LABELS)

    subset = pd.read_csv(PHASE / "data" / "d1_malayalam.csv", encoding="utf-8-sig")
    script = subset.groupby(["script_category", "label"]).size().unstack(fill_value=0)

    validation = json.load(open(METRICS / "validation_summary.json", encoding="utf-8"))
    structure = validation.get("structure_models") or validation.get("structure_only")
    if structure is None:
        # Locate the key recursively without guessing its nesting.
        def find(obj, key):
            if isinstance(obj, dict):
                if key in obj:
                    return obj[key]
                for v in obj.values():
                    found = find(v, key)
                    if found is not None:
                        return found
            return None
        structure = find(validation, "structure_only")

    out = {
        "audit": "Independent frozen-artifact statistics; no model was trained or altered.",
        "bootstrap": {
            "method": "percentile bootstrap over duplicate groups; shared draws across models",
            "n_boot": N_BOOT, "seed": SEED,
            "d1_groups": int(d1.group_id.nunique()), "d1_rows": len(d1),
            "d1_max_group_size": int(d1.groupby("group_id").size().max()),
            "d2_groups": int(d2.group_id.nunique()), "d2_rows": len(d2),
            "d2_max_group_size": int(d2.groupby("group_id").size().max()),
            "numerically_message_level": True,
        },
        "d1_models": meta1,
        "d1_bootstrap": ci1,
        "d2_models": meta2,
        "d2_bootstrap": ci2,
        "paired_d1": pairs,
        "svm_vs_muril_mean": muril_diffs,
        "d1_test_block_composition": {
            f"{(int(b)-1)*1000+1}-{int(b)*1000}": {
                "n": int(block_test.loc[b].sum()),
                "ham": int(block_test.loc[b].get("Ham", 0)),
                "spam": int(block_test.loc[b].get("Spam", 0)),
            } for b in block_test.index
        },
        "d1_all_block_composition": {
            f"{(int(b)-1)*1000+1}-{int(b)*1000}": {
                "n": int(block_all.loc[b].sum()),
                "ham": int(block_all.loc[b].get("Ham", 0)),
                "spam": int(block_all.loc[b].get("Spam", 0)),
            } for b in block_all.index
        },
        "script_composition": {
            idx: {k: int(v) for k, v in row.items()} for idx, row in script.iterrows()
        },
        "d1_block_pooled": pooled,
        "structure_diagnostics_from_saved_validation": structure,
        "source_hashes": {
            "d1_xlsx": sha256(BASE / "Datasets" / "Spam Message Collection.xlsx"),
            "d2_csv": sha256(BASE / "Datasets" / "Dataset_5971.csv"),
            "d1_test": sha256(SPLITS / "d1_malayalam_test.csv"),
            "d2_test": sha256(SPLITS / "d2_test.csv"),
        },
        "notes": [
            "The LR-SVM historical report reversed the sign of the point estimate without reversing the interval.",
            "LR minus SVM is negative; SVM minus LR is positive. The forward direction is reported separately.",
            "Every frozen test duplicate group is a singleton; the interval is numerically message-level.",
            "The three-seed MuRIL interval is conditional on seeds 42/43/44 and is not a training-run population interval.",
            "The structural diagnostic is read from a saved validation artifact, not refitted in this audit.",
        ],
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "out": str(OUT),
        "LR_minus_SVM_macro_f1": pairs["LR_minus_SVM_macro_f1"],
        "SVM_minus_LR_macro_f1": pairs["SVM_minus_LR_macro_f1"],
        "SVM_minus_MuRIL_mean_macro_f1": muril_diffs["macro_f1"],
        "blocks": out["d1_all_block_composition"],
        "script_composition": out["script_composition"],
        "source_hashes": out["source_hashes"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
