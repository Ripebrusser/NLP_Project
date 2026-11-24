#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2.1 baseline validation and source-block robustness.

Reads the existing Phase 2 artifacts only (no retraining of the headline models,
no hyperparameter tuning). Produces:

  metrics/validation_summary.json      all computed tables
  metrics/baseline_comparison.csv      D1 + D2 model comparison
  metrics/block_cv_predictions.csv     pooled leave-one-source-block-out rows
  reports/baseline_validation_tables.md  markdown tables for the final report

Block definition (corrected in Phase 2.1):
    block = (source_row - 1) // 1000 + 1
source_row is the Excel row number (header = row 1), so block 5 is source rows
4001-5000. The Phase 2 robustness script labelled its blocks one row low; its
membership differed by exactly two Ham rows. All numbers here are recomputed
with the corrected definition.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from itertools import combinations

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from scipy.stats import chi2_contingency
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             f1_score, precision_recall_fscore_support, roc_auc_score)
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from p2_common import DATA, METRICS, MODELS, REPORTS, SPLITS, dump_json
from p2_modeling import make_pipeline as make_text_pipeline

TOKEN_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
D1_LABELS = ["Ham", "Spam"]
D2_LABELS = ["ham", "spam", "smishing"]


def block_of(source_row: pd.Series) -> pd.Series:
    return ((source_row.astype(int) - 1) // 1000) + 1


def block_label(block: int) -> str:
    return f"{(int(block) - 1) * 1000 + 1}-{int(block) * 1000}"


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #
def eval_binary(y_true, y_pred, score=None) -> dict:
    """Binary metrics that never invent a score for an absent class."""
    cm = confusion_matrix(y_true, y_pred, labels=D1_LABELS)
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=D1_LABELS, zero_division=0)
    present = [i for i in range(2) if s[i] > 0]
    out = {
        "n": int(len(y_true)),
        "ham_support": int(s[0]), "spam_support": int(s[1]),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1_present_labels": float(np.mean([f[i] for i in present])),
        "balanced_accuracy_present": float(np.mean([r[i] for i in present])),
        "ham_precision": float(p[0]), "ham_recall": float(r[0]), "ham_f1": float(f[0]),
        "spam_precision": float(p[1]) if s[1] else None,
        "spam_recall": float(r[1]) if s[1] else None,
        "spam_f1": float(f[1]) if s[1] else None,
        "confusion_matrix": cm.tolist(),
        "labels": D1_LABELS,
        "evaluable_for_spam": bool(s[1] > 0),
    }
    if score is not None and s[1] > 0:
        y = np.array([1 if v == "Spam" else 0 for v in y_true])
        out["spam_pr_auc"] = float(average_precision_score(y, score))
        out["spam_roc_auc"] = float(roc_auc_score(y, score))
    else:
        out["spam_pr_auc"] = None
        out["spam_roc_auc"] = None
    return out


def per_class(report: dict, labels: list[str]) -> list[dict]:
    out = []
    for lab in labels:
        d = report.get(lab, {})
        out.append({"label": lab, "precision": d.get("precision"), "recall": d.get("recall"),
                    "f1": d.get("f1-score"), "support": d.get("support")})
    return out


# --------------------------------------------------------------------------- #
# 1. verify saved artifacts
# --------------------------------------------------------------------------- #
def verify_artifacts() -> dict:
    checks = []
    for tag, res_name, split_prefix, labels in (
        ("D1", "d1_malayalam_results.json", "d1_malayalam", D1_LABELS),
        ("D2", "d2_results.json", "d2", D2_LABELS),
    ):
        res = json.load(open(METRICS / res_name, encoding="utf-8"))
        test = pd.read_csv(SPLITS / f"{split_prefix}_test.csv", encoding="utf-8-sig")
        for fam, m in res["models"].items():
            obj = joblib.load(MODELS / m["model_file"])
            pipe = obj["pipeline"]
            pred = pipe.predict(test["text"])
            saved = pd.read_csv(METRICS / m["predictions_file"], encoding="utf-8-sig")
            checks.append({
                "dataset": tag, "model": fam, "model_file": m["model_file"],
                "config": m["selected_config"], "C": m["C"],
                "n_features": int(len(pipe.named_steps["tfidf"].vocabulary_)),
                "rows": int(len(test)),
                "accuracy_recomputed": float(accuracy_score(test["label"], pred)),
                "accuracy_recorded": float(m["test"]["accuracy"]),
                "accuracy_match": bool(abs(accuracy_score(test["label"], pred)
                                           - m["test"]["accuracy"]) < 1e-12),
                "predictions_match_saved_file": bool((pred == saved["prediction"]).all()),
            })
    return {"checks": checks, "all_match": all(c["accuracy_match"] and
                                               c["predictions_match_saved_file"]
                                               for c in checks)}


# --------------------------------------------------------------------------- #
# 2. baseline comparison
# --------------------------------------------------------------------------- #
def comparison_table() -> tuple[list[dict], list[dict]]:
    d1 = json.load(open(METRICS / "d1_malayalam_results.json", encoding="utf-8"))
    d2 = json.load(open(METRICS / "d2_results.json", encoding="utf-8"))
    out = {}
    for tag, res, labels in (("D1", d1, D1_LABELS), ("D2", d2, D2_LABELS)):
        rows = []
        for fam, m in res["models"].items():
            t = m["test"]
            rows.append({
                "dataset": tag, "task": "Ham vs Spam" if tag == "D1" else "Ham vs Spam vs Smishing",
                "model": fam, "config": m["selected_config"], "C": m["C"],
                "val_macro_f1": m["val"].get("val_macro_f1"),
                "accuracy": t["accuracy"], "macro_f1": t["macro_f1"],
                "precision_macro": m["classification_report"]["macro avg"]["precision"],
                "recall_macro": m["classification_report"]["macro avg"]["recall"],
                "n_test": t["n"], "n_errors": m["n_errors"],
                "confusion_matrix": t["confusion_matrix"], "labels": labels,
                "per_class": per_class(m["classification_report"], labels),
                "per_class_f1": " / ".join(
                    f"{c['label']} {c['f1']:.3f}"
                    for c in per_class(m["classification_report"], labels)),
            })
        out[tag] = rows
    return out["D1"], out["D2"]


# --------------------------------------------------------------------------- #
# 3. block-level audit
# --------------------------------------------------------------------------- #
def tokens(text: str) -> list[str]:
    return [w.lower() for w in TOKEN_RE.findall(str(text)) if len(w) >= 2]


def token_counter(texts) -> Counter:
    c = Counter()
    for t in texts:
        c.update(tokens(t))
    return c


def log_odds(c_in: Counter, n_in: int, c_out: Counter, n_out: int, k: int = 12) -> list[dict]:
    """Monroe et al. log-odds ratio with an informative Dirichlet prior."""
    alpha = 0.5
    rows = []
    for w in set(c_in) | set(c_out):
        if c_in[w] < 3:
            continue
        a, b = c_in[w], c_out[w]
        pa = (a + alpha) / (n_in + 2 * alpha)
        pb = (b + alpha) / (n_out + 2 * alpha)
        var = 1 / (a + alpha) + 1 / (b + alpha)
        z = (math.log(pa / (1 - pa)) - math.log(pb / (1 - pb))) / math.sqrt(var)
        rows.append({"token": w, "in_block": int(a), "outside": int(b), "z": round(z, 3)})
    rows.sort(key=lambda r: -r["z"])
    return rows[:k]


def char_dist(texts) -> Counter:
    c = Counter()
    for t in texts:
        s = f" {str(t)} "
        for i in range(len(s) - 2):
            c[s[i:i + 3]] += 1
    return c


def js_divergence(c1: Counter, c2: Counter) -> float:
    keys = set(c1) | set(c2)
    n1, n2 = sum(c1.values()), sum(c2.values())
    if not n1 or not n2:
        return float("nan")
    total = 0.0
    for k in keys:
        p, q = c1[k] / n1, c2[k] / n2
        m = (p + q) / 2
        if p:
            total += 0.5 * p * math.log2(p / m)
        if q:
            total += 0.5 * q * math.log2(q / m)
    return float(total)


def skeleton(text: str) -> str:
    s = str(text).lower()
    s = URL_RE.sub(" <url> ", s)
    s = re.sub(r"\d+", "#", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:90]


def block_audit(d1: pd.DataFrame) -> dict:
    d1 = d1.copy()
    d1["block"] = block_of(d1["source_row"])
    d1["label"] = d1["label"].astype(str)
    d1["n_chars"] = d1["message"].astype(str).str.len()
    d1["n_tokens"] = d1["text"].astype(str).str.split().str.len()
    d1["has_url"] = d1["message"].astype(str).str.contains(URL_RE)
    d1["has_digit"] = d1["message"].astype(str).str.contains(r"\d")
    d1["latin"] = d1["has_latin"].astype(str).str.lower().isin(["true", "1"])
    d1["mono"] = d1["malayalam_only_script"].astype(str).str.lower().isin(["true", "1"])
    d1["skel"] = d1["message"].map(skeleton)

    blocks = sorted(d1["block"].unique())
    block_records = []
    for b in blocks:
        g = d1[d1["block"] == b]
        spam = g[g["label"] == "Spam"]
        ham = g[g["label"] == "Ham"]
        item = {
            "block": block_label(b),
            "source_row_min": int(g["source_row"].min()),
            "source_row_max": int(g["source_row"].max()),
            "rows": int(len(g)),
            "ham": int(len(ham)),
            "spam": int(len(spam)),
            "spam_rate": float(len(spam) / len(g)),
            "malayalam_only": int(g["mono"].sum()),
            "latin_also": int(g["latin"].sum()),
            "n_unique_text": int(g["text"].nunique()),
            "n_unique_skeleton": int(g["skel"].nunique()),
            "length_chars": {
                "all_mean": float(g["n_chars"].mean()),
                "ham_median": float(ham["n_chars"].median()),
                "spam_median": float(spam["n_chars"].median()) if len(spam) else None,
                "all_p90": float(g["n_chars"].quantile(0.90)),
            },
            "tokens": {
                "all_mean": float(g["n_tokens"].mean()),
                "ham_median": float(ham["n_tokens"].median()),
                "spam_median": float(spam["n_tokens"].median()) if len(spam) else None,
            },
            "url_rate": float(g["has_url"].mean()),
            "url_rate_ham": float(ham["has_url"].mean()),
            "url_rate_spam": float(spam["has_url"].mean()) if len(spam) else None,
            "digit_rate": float(g["has_digit"].mean()),
            "digit_rate_ham": float(ham["has_digit"].mean()),
            "digit_rate_spam": float(spam["has_digit"].mean()) if len(spam) else None,
            "latin_rate_ham": float(ham["latin"].mean()),
            "latin_rate_spam": float(spam["latin"].mean()) if len(spam) else None,
            "top_tokens": log_odds(token_counter(g["text"]), sum(len(tokens(t)) for t in g["text"]),
                                   token_counter(d1.loc[d1.block != b, "text"]),
                                   sum(len(tokens(t)) for t in d1.loc[d1.block != b, "text"]),
                                   k=10),
            "top_templates": [
                {"skeleton": k, "n": int(v),
                 "spam": int((g.loc[g.skel == k, "label"] == "Spam").sum())}
                for k, v in g["skel"].value_counts().head(5).items()
            ],
        }
        block_records.append(item)

    # pair-wise vocabulary / character divergence
    pair_div = []
    for a, b in combinations(blocks, 2):
        ga, gb = d1[d1.block == a], d1[d1.block == b]
        ta, tb = set(token_counter(ga["text"])), set(token_counter(gb["text"]))
        pair_div.append({
            "a": block_label(a), "b": block_label(b),
            "token_jaccard": round(len(ta & tb) / len(ta | tb), 4),
            "char_trigram_js": round(js_divergence(char_dist(ga["text"]), char_dist(gb["text"])), 4),
        })

    # spam-centroid cosine between blocks that contain spam
    spam_blocks = [b for b in blocks if (d1.loc[d1.block == b, "label"] == "Spam").sum() > 0]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)
    X = vec.fit_transform(d1["text"])
    centroids = {}
    for b in spam_blocks:
        mask = ((d1["block"] == b) & (d1["label"] == "Spam")).to_numpy()
        v = np.asarray(X[mask].mean(axis=0)).ravel()
        centroids[block_label(b)] = v / (np.linalg.norm(v) + 1e-12)
    spam_centroid = [{"a": a, "b": b, "cosine": round(float(np.dot(centroids[a], centroids[b])), 4)}
                     for a, b in combinations(centroids, 2)]

    # template confinement: skeletons appearing in one block only
    skel_blocks = d1.groupby("skel")["block"].nunique()
    confined = d1[d1["skel"].isin(skel_blocks[skel_blocks == 1].index)]
    template_confinement = {
        "unique_skeletons": int(d1["skel"].nunique()),
        "confined_to_one_block": int((skel_blocks == 1).sum()),
        "records_in_confined_skeletons": int(len(confined)),
        "spam_share_in_confined": float((confined["label"] == "Spam").mean()) if len(confined) else None,
    }

    # label vs block association
    table = pd.crosstab(d1["block"], d1["label"])
    chi2, p, dof, _ = chi2_contingency(table.to_numpy())
    n = len(d1)
    cramers_v = math.sqrt(chi2 / (n * (min(table.shape) - 1)))

    # block-only predictor (majority label per block)
    majority = d1.groupby("block")["label"].agg(lambda s: s.mode().iloc[0])
    block_pred = d1["block"].map(majority)
    block_only = eval_binary(d1["label"], block_pred)
    # evaluated on the frozen random test set
    test = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
    test_pred = block_of(test["source_row"]).map(majority)
    block_only_test = eval_binary(test["label"], test_pred)

    # label runs in source order (Malayalam records only)
    ordered = d1.sort_values("source_row")
    labs = ordered["label"].tolist()
    runs = 1 + sum(a != b for a, b in zip(labs, labs[1:]))
    n1 = sum(v == "Spam" for v in labs)
    n2 = n - n1
    exp_runs = 1 + 2 * n1 * n2 / n
    var_runs = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n * n * (n - 1))
    same_next = sum(a == b for a, b in zip(labs, labs[1:])) / (n - 1)
    runs_test = {"observed_runs": int(runs), "expected_runs": round(exp_runs, 2),
                 "z": round((runs - exp_runs) / math.sqrt(var_runs), 2),
                 "p_same_label_as_previous_record": round(same_next, 4)}

    # exact contiguous label runs in source order (the batch footprint)
    run_detail = []
    start = 0
    rows = ordered["source_row"].tolist()
    for i in range(1, len(labs) + 1):
        if i == len(labs) or labs[i] != labs[start]:
            run_detail.append({"label": labs[start], "start_row": int(rows[start]),
                               "end_row": int(rows[i - 1]), "n": int(i - start)})
            start = i

    # 100-row bins: is the label a function of row position?
    d1["bin_start"] = ((d1["source_row"].astype(int) - 1) // 100) * 100 + 1
    bins = []
    for start, g in d1.groupby("bin_start"):
        spam = int((g["label"] == "Spam").sum())
        bins.append({"bin": f"{start}-{start + 99}", "n": int(len(g)),
                     "ham": int(len(g) - spam), "spam": spam,
                     "spam_rate": round(spam / len(g), 4)})
    bins = sorted(bins, key=lambda r: r["bin"])
    all_ham = sum(1 for b in bins if b["spam"] == 0)
    all_spam = sum(1 for b in bins if b["ham"] == 0)
    mixed = sum(1 for b in bins if b["ham"] and b["spam"])

    return {
        "blocks": block_records,
        "pairwise_divergence": pair_div,
        "spam_centroid_cosine": spam_centroid,
        "template_confinement": template_confinement,
        "label_by_block": {"table": table.to_dict(),
                           "chi2": round(float(chi2), 2), "p_value": float(p),
                           "dof": int(dof), "cramers_v": round(float(cramers_v), 4)},
        "block_only_predictor": {"full_corpus": block_only, "random_test": block_only_test,
                                 "majority_label_by_block": {block_label(k): v for k, v in majority.items()}},
        "label_runs": runs_test,
        "label_run_detail": run_detail,
        "row_bins": {"n_bins": len(bins), "all_ham": all_ham, "all_spam": all_spam,
                     "mixed": mixed, "bins": bins},
    }


# --------------------------------------------------------------------------- #
# 4. structure-only leakage models (no text)
# --------------------------------------------------------------------------- #
def structure_models(d1: pd.DataFrame) -> dict:
    full = d1.copy()
    full["block"] = block_of(full["source_row"])
    train = pd.read_csv(SPLITS / "d1_malayalam_train.csv", encoding="utf-8-sig")
    test = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")

    def feats(df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame({
            "n_chars": df["message"].astype(str).str.len(),
            "n_tokens": df["text"].astype(str).str.split().str.len(),
            "n_digits": df["message"].astype(str).str.count(r"\d"),
            "has_url": df["message"].astype(str).str.contains(URL_RE).astype(int),
            "has_latin": df["has_latin"].astype(str).str.lower().isin(["true", "1"]).astype(int),
            "malayalam_only": df["malayalam_only_script"].astype(str).str.lower().isin(["true", "1"]).astype(int),
        })
        b = block_of(df["source_row"])
        for k in sorted(full["block"].unique()):
            out[f"block_{block_label(k)}"] = (b == k).astype(int)
        return out

    def run(cols: list[str], name: str) -> dict:
        pipe = make_pipeline(StandardScaler(),
                             LogisticRegression(C=1.0, class_weight="balanced",
                                                max_iter=5000, solver="lbfgs"))
        pipe.fit(feats(train)[cols], train["label"])
        pred = pipe.predict(feats(test)[cols])
        m = eval_binary(test["label"], pred)
        return {"name": name, "features": cols, "accuracy": m["accuracy"],
                "macro_f1": m["macro_f1"], "spam_precision": m["spam_precision"],
                "spam_recall": m["spam_recall"], "confusion_matrix": m["confusion_matrix"]}

    struct_cols = ["n_chars", "n_tokens", "n_digits", "has_url", "has_latin", "malayalam_only"]
    block_cols = [c for c in feats(full).columns if c.startswith("block_")]
    return {
        "structure_only": run(struct_cols, "structure only (no text, no block id)"),
        "block_only_logreg": run(block_cols, "block identity only"),
        "structure_plus_block": run(struct_cols + block_cols, "structure + block identity"),
        "note": "Trained on the frozen random-split train rows and evaluated on its test rows. "
                "These models are diagnostics of metadata leakage, not competing classifiers.",
    }


# --------------------------------------------------------------------------- #
# 5. leave-one-source-block-out validation
# --------------------------------------------------------------------------- #
def block_cv(d1: pd.DataFrame, random_scores: dict) -> dict:
    d1 = d1.copy()
    d1["block"] = block_of(d1["source_row"])
    blocks = sorted(d1["block"].unique())
    results = {}
    pooled_rows = []
    for fam in ("logreg", "linear_svm"):
        res = random_scores[fam]
        cfg, C = res["selected_config"], float(res["C"])
        folds = []
        pooled_pred, pooled_true, pooled_score = [], [], []
        for b in blocks:
            train = d1[d1["block"] != b]
            test = d1[d1["block"] == b]
            pipe = make_text_pipeline(cfg, fam, C, 2)
            pipe.fit(train["text"], train["label"])
            pred = pipe.predict(test["text"])
            score = pipe.decision_function(test["text"])
            m = eval_binary(test["label"], pred, score)
            folds.append({
                "held_out_block": block_label(b),
                "source_row_min": int(test["source_row"].min()),
                "source_row_max": int(test["source_row"].max()),
                "train_rows": int(len(train)), "train_ham": int((train["label"] == "Ham").sum()),
                "train_spam": int((train["label"] == "Spam").sum()),
                "test_rows": int(len(test)), "test_ham": m["ham_support"],
                "test_spam": m["spam_support"],
                "accuracy": m["accuracy"], "macro_f1": m["macro_f1"],
                "macro_f1_present_labels": m["macro_f1_present_labels"],
                "balanced_accuracy_present": m["balanced_accuracy_present"],
                "ham_precision": m["ham_precision"], "ham_recall": m["ham_recall"],
                "ham_f1": m["ham_f1"],
                "spam_precision": m["spam_precision"], "spam_recall": m["spam_recall"],
                "spam_f1": m["spam_f1"], "spam_pr_auc": m["spam_pr_auc"],
                "confusion_matrix": m["confusion_matrix"], "labels": D1_LABELS,
                "evaluable_for_spam": m["evaluable_for_spam"],
                "note": ("test block contains no Spam; spam precision/recall are undefined"
                         if m["spam_support"] == 0 else
                         "training blocks contain only 12 Spam" if (train["label"] == "Spam").sum() < 20
                         else ""),
            })
            pooled_pred.extend(pred.tolist())
            pooled_true.extend(test["label"].tolist())
            pooled_score.extend(score.tolist())
            for rid, y, p_, s_ in zip(test["record_id"], test["label"], pred, score):
                pooled_rows.append({"model": fam, "fold": block_label(b), "record_id": rid,
                                    "label": y, "prediction": p_, "score": float(s_)})

        pool = eval_binary(pooled_true, pooled_pred, pooled_score)
        results[fam] = {
            "config": cfg, "C": C,
            "folds": folds,
            "pooled": {k: pool[k] for k in ("n", "ham_support", "spam_support", "accuracy",
                                            "macro_f1", "macro_f1_present_labels",
                                            "balanced_accuracy_present", "ham_precision",
                                            "ham_recall", "ham_f1", "spam_precision",
                                            "spam_recall", "spam_f1", "spam_pr_auc",
                                            "confusion_matrix", "labels")},
            "random_split_reference": {
                "accuracy": res["test"]["accuracy"], "macro_f1": res["test"]["macro_f1"],
                "spam_precision": res["test"]["spam_precision"],
                "spam_recall": res["test"]["spam_recall"],
                "confusion_matrix": res["test"]["confusion_matrix"],
            },
        }

    pd.DataFrame(pooled_rows).to_csv(METRICS / "block_cv_predictions.csv",
                                     index=False, encoding="utf-8-sig")
    return results


# --------------------------------------------------------------------------- #
# 6. D2 diagnostics
# --------------------------------------------------------------------------- #
def d2_diagnostics() -> dict:
    d2 = pd.read_csv(DATA / "d2_grouped.csv", encoding="utf-8-sig")
    train = pd.read_csv(SPLITS / "d2_train.csv", encoding="utf-8-sig")
    test = pd.read_csv(SPLITS / "d2_test.csv", encoding="utf-8-sig")
    res = json.load(open(METRICS / "d2_results.json", encoding="utf-8"))

    def style(df: pd.DataFrame) -> list[dict]:
        rows = []
        for lab in D2_LABELS:
            g = df[df["label"] == lab]
            rows.append({
                "label": lab, "n": int(len(g)),
                "chars_mean": round(float(g["message"].astype(str).str.len().mean()), 1),
                "chars_median": float(g["message"].astype(str).str.len().median()),
                "tokens_mean": round(float(g["text"].astype(str).str.split().str.len().mean()), 2),
                "url_rate": round(float(g["message"].astype(str).str.contains(URL_RE).mean()), 4),
                "digit_rate": round(float(g["message"].astype(str).str.contains(r"\d").mean()), 4),
                "latin_rate": round(float(g["has_latin"].astype(str).str.lower()
                                         .isin(["true", "1"]).mean()), 4),
            })
        return rows

    # class centroid similarity in char TF-IDF space (fit on train only)
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=2, sublinear_tf=True)
    X = vec.fit_transform(train["text"])
    cent = {}
    for lab in D2_LABELS:
        v = np.asarray(X[(train["label"] == lab).to_numpy()].mean(axis=0)).ravel()
        cent[lab] = v / (np.linalg.norm(v) + 1e-12)
    centroid = [{"a": a, "b": b, "cosine": round(float(np.dot(cent[a], cent[b])), 4)}
                for a, b in combinations(D2_LABELS, 2)]

    # top learned features per class and their overlap
    obj = joblib.load(MODELS / "d2_logreg.joblib")
    pipe = obj["pipeline"]
    names = np.array(pipe.named_steps["tfidf"].get_feature_names_out())
    coef = pipe.named_steps["clf"].coef_
    classes = list(pipe.named_steps["clf"].classes_)
    tops = {}
    for i, lab in enumerate(classes):
        idx = np.argsort(coef[i])[::-1][:50]
        tops[lab] = set(names[idx])
    overlap = {}
    for a, b in combinations(D2_LABELS, 2):
        inter = tops[a] & tops[b]
        overlap[f"{a}__{b}"] = {
            "jaccard_top50": round(len(inter) / len(tops[a] | tops[b]), 4),
            "shared_terms": sorted(inter)[:12],
        }

    # error pairs and examples per model
    diagnostics = {}
    for fam in ("logreg", "linear_svm"):
        pred = pd.read_csv(METRICS / f"d2_{fam}_test_predictions.csv", encoding="utf-8-sig")
        wrong = pred[pred["label"] != pred["prediction"]]
        pairs = Counter(f"{r.label}->{r.prediction}" for r in wrong.itertuples())
        examples = []
        for r in wrong.sort_values("margin", ascending=False).head(6).itertuples():
            examples.append({"record_id": r.record_id, "true": r.label, "pred": r.prediction,
                             "margin": round(float(r.margin), 4),
                             "message": str(r.message)[:220]})
        diagnostics[fam] = {
            "n_errors": int(len(wrong)),
            "error_pairs": dict(pairs.most_common()),
            "examples": examples,
            "per_class": res["models"][fam]["test"]["per_class"],
            "confusion_matrix": res["models"][fam]["test"]["confusion_matrix"],
            "labels": D2_LABELS,
            "accuracy": res["models"][fam]["test"]["accuracy"],
            "macro_f1": res["models"][fam]["test"]["macro_f1"],
        }

    return {
        "class_style": style(d2),
        "train_style": style(train),
        "centroid_cosine": centroid,
        "top_feature_overlap": overlap,
        "models": diagnostics,
        "train_support": {k: int(v) for k, v in train["label"].value_counts().items()},
        "test_support": {k: int(v) for k, v in test["label"].value_counts().items()},
    }


# --------------------------------------------------------------------------- #
# markdown
# --------------------------------------------------------------------------- #
def md_table(rows: list[dict], cols: list[tuple[str, str]]) -> str:
    head = "| " + " | ".join(h for _, h in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    def fmt(v):
        if v is None:
            return "—"
        if isinstance(v, float):
            return f"{v:.4f}"
        return str(v).replace("|", "\\|")
    body = ["| " + " | ".join(fmt(r.get(k)) for k, _ in cols) + " |" for r in rows]
    return "\n".join([head, sep] + body)


def write_tables(summary: dict) -> None:
    parts = ["# Phase 2.1 — computed tables\n",
             "Generated by `p2_validate.py` from the frozen Phase 2 artifacts. "
             "All values are machine-computed; do not edit by hand.\n"]

    parts.append("## Artifact verification\n")
    parts.append(md_table(summary["verification"]["checks"],
                          [("dataset", "Set"), ("model", "Model"), ("config", "TF-IDF"),
                           ("C", "C"), ("n_features", "Features"), ("accuracy_recorded", "Recorded acc."),
                           ("accuracy_recomputed", "Recomputed acc."),
                           ("predictions_match_saved_file", "Predictions identical")]))

    for tag in ("D1", "D2"):
        parts.append(f"\n## {tag} model comparison\n")
        parts.append(md_table(summary["comparison"][tag],
                              [("model", "Model"), ("config", "TF-IDF"), ("C", "C"),
                               ("val_macro_f1", "Val macro-F1"), ("accuracy", "Test acc."),
                               ("precision_macro", "P macro"), ("recall_macro", "R macro"),
                               ("macro_f1", "Test macro-F1"), ("per_class_f1", "Per-class F1"),
                               ("n_errors", "Errors")]))

    parts.append("\n## D1 source blocks\n")
    block_rows = [{"block": b["block"], "rows": b["rows"], "ham": b["ham"],
                   "spam": b["spam"], "spam_rate": b["spam_rate"],
                   "malayalam_only": b["malayalam_only"],
                   "mean_chars": b["length_chars"]["all_mean"],
                   "url_rate": b["url_rate"], "digit_rate": b["digit_rate"],
                   "spam_chars": b["length_chars"]["spam_median"]}
                  for b in summary["block_audit"]["blocks"]]
    parts.append(md_table(block_rows,
                          [("block", "Source rows"), ("rows", "n"), ("ham", "Ham"),
                           ("spam", "Spam"), ("spam_rate", "Spam rate"),
                           ("malayalam_only", "Malayalam-only"),
                           ("mean_chars", "Mean chars"),
                           ("spam_chars", "Spam median chars"),
                           ("url_rate", "URL rate"), ("digit_rate", "Digit rate")]))

    parts.append("\n## D1 label vs block\n")
    lb = summary["block_audit"]["label_by_block"]
    parts.append(md_table([{"metric": "Cramér's V", "value": lb["cramers_v"]},
                           {"metric": "chi-square", "value": lb["chi2"]},
                           {"metric": "p-value", "value": lb["p_value"]},
                           {"metric": "block-only accuracy (full corpus)",
                            "value": summary["block_audit"]["block_only_predictor"]["full_corpus"]["accuracy"]},
                           {"metric": "block-only macro-F1 (full corpus)",
                            "value": summary["block_audit"]["block_only_predictor"]["full_corpus"]["macro_f1"]},
                           {"metric": "block-only accuracy (random test)",
                            "value": summary["block_audit"]["block_only_predictor"]["random_test"]["accuracy"]},
                           {"metric": "block-only macro-F1 (random test)",
                            "value": summary["block_audit"]["block_only_predictor"]["random_test"]["macro_f1"]}],
                          [("metric", "Quantity"), ("value", "Value")]))

    parts.append("\n## Leave-one-source-block-out\n")
    rows = []
    for fam, r in summary["block_cv"].items():
        for f in r["folds"]:
            rows.append({**f, "model": fam})
    parts.append(md_table(rows,
                          [("model", "Model"), ("held_out_block", "Held-out rows"),
                           ("train_rows", "Train n"), ("train_spam", "Train Spam"),
                           ("test_rows", "Test n"), ("test_ham", "Test Ham"),
                           ("test_spam", "Test Spam"), ("accuracy", "Acc."),
                           ("macro_f1", "Macro-F1"), ("spam_precision", "Spam P"),
                           ("spam_recall", "Spam R"), ("spam_pr_auc", "Spam PR-AUC")]))

    parts.append("\n## Pooled block-held-out vs random split\n")
    rows = []
    for fam, r in summary["block_cv"].items():
        p = r["pooled"]
        q = r["random_split_reference"]
        rows.append({"model": fam, "setting": "random grouped split (all blocks in every split)",
                     "accuracy": q["accuracy"], "macro_f1": q["macro_f1"],
                     "spam_precision": q["spam_precision"], "spam_recall": q["spam_recall"]})
        rows.append({"model": fam, "setting": "pooled leave-one-block-out",
                     "accuracy": p["accuracy"], "macro_f1": p["macro_f1"],
                     "spam_precision": p["spam_precision"], "spam_recall": p["spam_recall"]})
    parts.append(md_table(rows,
                          [("model", "Model"), ("setting", "Evaluation"), ("accuracy", "Acc."),
                           ("macro_f1", "Macro-F1"), ("spam_precision", "Spam P"),
                           ("spam_recall", "Spam R")]))

    parts.append("\n## D2 per-class performance\n")
    rows = []
    for fam, d in summary["d2"]["models"].items():
        for lab in D2_LABELS:
            c = d["per_class"][lab]
            rows.append({"model": fam, "label": lab, "precision": c["precision"],
                         "recall": c["recall"], "f1": c["f1"], "support": c["support"]})
    parts.append(md_table(rows, [("model", "Model"), ("label", "Class"),
                                 ("precision", "Precision"), ("recall", "Recall"),
                                 ("f1", "F1"), ("support", "Support")]))

    (REPORTS / "baseline_validation_tables.md").write_text("\n".join(parts) + "\n",
                                                           encoding="utf-8")


def main() -> None:
    d1 = pd.concat([pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
                    for p in ("train", "val", "test")], ignore_index=True)
    d1_results = json.load(open(METRICS / "d1_malayalam_results.json", encoding="utf-8"))

    verification = verify_artifacts()
    comp_d1, comp_d2 = comparison_table()
    audit = block_audit(d1)
    struct = structure_models(d1)
    cv = block_cv(d1, d1_results["models"])
    d2 = d2_diagnostics()

    summary = {
        "generated_by": "Research Work/phase2/p2_validate.py",
        "block_definition": "block = (source_row - 1) // 1000 + 1; source_row is the Excel row",
        "block_definition_note": ("Phase 2's p2_robustness.py used "
                                  "((source_row-1)-1)//1000+1, which labelled blocks one row low; "
                                  "membership differed by two Ham rows. Corrected here."),
        "verification": verification,
        "comparison": {"D1": comp_d1, "D2": comp_d2},
        "block_audit": audit,
        "structure_models": struct,
        "block_cv": cv,
        "d2": d2,
    }
    dump_json(summary, METRICS / "validation_summary.json")

    compare_rows = []
    for tag in ("D1", "D2"):
        for r in summary["comparison"][tag]:
            flat = {k: v for k, v in r.items() if k not in ("confusion_matrix", "labels", "per_class")}
            for c in r["per_class"]:
                flat[f"f1_{c['label']}"] = c["f1"]
                flat[f"precision_{c['label']}"] = c["precision"]
                flat[f"recall_{c['label']}"] = c["recall"]
            compare_rows.append(flat)
    pd.DataFrame(compare_rows).to_csv(METRICS / "baseline_comparison.csv",
                                      index=False, encoding="utf-8-sig")

    write_tables(summary)
    print(json.dumps({
        "verification_all_match": verification["all_match"],
        "blocks": [(b["block"], b["rows"], b["ham"], b["spam"], b["spam_rate"])
                   for b in audit["blocks"]],
        "cramers_v": audit["label_by_block"]["cramers_v"],
        "block_only_macro_f1": audit["block_only_predictor"]["full_corpus"]["macro_f1"],
        "block_cv": {f: {k: r["pooled"][k] for k in ("accuracy", "macro_f1", "spam_recall")}
                     for f, r in cv.items()},
        "structure": {k: (v["macro_f1"] if isinstance(v, dict) and "macro_f1" in v else v)
                      for k, v in struct.items()},
        "d2_centroids": d2["centroid_cosine"],
        "d2_overlap": d2["top_feature_overlap"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
