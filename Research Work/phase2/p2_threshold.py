#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2.3 Part C: decision-threshold calibration and diagnosis.

Rules enforced here:
- Random split: thresholds are selected on the frozen validation split using a
  model fitted on the frozen training split only. The final saved test scores
  are then thresholded; test labels are used only for descriptive reporting.
- Block folds: for each fold, the threshold is selected on an inner validation
  split drawn only from the two training blocks. The held-out block is never
  used to choose a threshold.
- MuRIL block-fold models were not saved. Their held-out scores are analysed
  descriptively (PR-AUC, score ranges, threshold sweep); the random-validation
  threshold for seed 42 is transferred only as a labelled sensitivity check.

No model is selected or tuned on a held-out block. No new architecture is run.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score, precision_recall_curve, roc_auc_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from p2_common import METRICS, MODELS, REPORTS, SPLITS, dump_json
from p2_modeling import make_pipeline, scores
from p2_stats import point_metrics

warnings.filterwarnings("ignore", category=UserWarning)
LABELS = ["Ham", "Spam"]
BLOCKS = [(5, "4001-5000"), (6, "5001-6000"), (7, "6001-7000")]
FIG = REPORTS / "figures"
FIG.mkdir(exist_ok=True)
D1_RESULTS = json.load(open(METRICS / "d1_malayalam_results.json", encoding="utf-8"))


def load_splits():
    return {p: pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
            for p in ("train", "val", "test")}


def candidates(s: np.ndarray) -> np.ndarray:
    u = np.unique(np.asarray(s, dtype=float))
    if len(u) == 1:
        return np.array([u[0] - 1e-9, u[0], u[0] + 1e-9])
    eps = max(1e-9, (u[-1] - u[0]) * 1e-9)
    return np.r_[u[0] - eps, (u[:-1] + u[1:]) / 2.0, u[-1] + eps]


def select_threshold(score, y, min_precision: float | None = None) -> dict | None:
    rows = []
    for t in candidates(score):
        pred = np.where(score >= t, "Spam", "Ham")
        m = point_metrics(y, pred, LABELS)
        if min_precision is not None:
            if m["spam_precision"] < min_precision or m["spam_support"] == 0:
                continue
        rows.append((float(t), m))
    if not rows:
        return None
    best = max(r[1]["macro_f1"] for r in rows)
    tied = [r for r in rows if np.isclose(r[1]["macro_f1"], best, atol=1e-12)]
    # Prefer the widest margin to the nearest validation score (stable threshold).
    def margin(r):
        return float(np.min(np.abs(score - r[0])))
    chosen = max(tied, key=lambda r: (margin(r), r[1]["spam_recall"]))
    return {"threshold": chosen[0], "validation": chosen[1],
            "n_candidates": len(rows), "tied_at_best": len(tied)}


def apply_threshold(score, t: float) -> np.ndarray:
    return np.where(np.asarray(score) >= t, "Spam", "Ham")


def held_metrics(df: pd.DataFrame, score, threshold: float) -> dict:
    pred = apply_threshold(score, threshold)
    m = point_metrics(df["label"], pred, LABELS)
    m["false_positives"] = int(((df["label"].to_numpy() == "Ham") & (pred == "Spam")).sum())
    m["false_negatives"] = int(((df["label"].to_numpy() == "Spam") & (pred == "Ham")).sum())
    m["threshold"] = float(threshold)
    return m


def random_classical(splits) -> list[dict]:
    out = []
    for fam in ("logreg", "linear_svm"):
        cfg = D1_RESULTS["models"][fam]["selected_config"]
        C = float(D1_RESULTS["models"][fam]["C"])
        pipe = make_pipeline(cfg, fam, C, 2).fit(splits["train"]["text"],
                                                 splits["train"]["label"])
        sv = scores(pipe, splits["val"]["text"])
        st_cal = scores(pipe, splits["test"]["text"])
        picked = select_threshold(sv, splits["val"]["label"])
        picked_c = select_threshold(sv, splits["val"]["label"], min_precision=0.90)
        saved = pd.read_csv(
            METRICS / f"d1_malayalam_{fam}_test_predictions.csv", encoding="utf-8-sig")
        st_final = saved["score_spam"].to_numpy()
        default_t = 0.5 if fam == "logreg" else 0.0
        item = {
            "model": "Logistic Regression" if fam == "logreg" else "Linear SVM",
            "config": cfg, "C": C,
            "threshold_default": default_t,
            "threshold_selected": picked["threshold"] if picked else None,
            "threshold_precision_constrained": picked_c["threshold"] if picked_c else None,
            "validation_at_selected": picked["validation"] if picked else None,
            "validation_at_precision_constrained": picked_c["validation"] if picked_c else None,
            "validation_default": point_metrics(
                splits["val"]["label"], apply_threshold(sv, default_t), LABELS),
            "calibration_model_test_default": point_metrics(
                splits["test"]["label"], apply_threshold(st_cal, default_t), LABELS),
            "final_test_default": point_metrics(
                saved["label"], saved["prediction"], LABELS),
            "final_test_selected": held_metrics(saved, st_final, picked["threshold"]),
            "final_test_precision_constrained": (
                held_metrics(saved, st_final, picked_c["threshold"]) if picked_c else None),
            "changed_predictions_selected": int(
                (apply_threshold(st_final, picked["threshold"]) != saved["prediction"]).sum()),
        }
        out.append(item)
    return out


@torch.no_grad()
def muril_probs(df, tokenizer, model, max_len=128, device=None):
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval().to(device)
    out = []
    for i in range(0, len(df), 32):
        enc = tokenizer(df["text"].iloc[i:i + 32].tolist(), truncation=True,
                        max_length=max_len, padding="max_length",
                        return_tensors="pt").to(device)
        with torch.amp.autocast("cuda", enabled=device.type == "cuda",
                                dtype=torch.float16):
            logits = model(**enc).logits
        out.append(torch.softmax(logits.float(), -1).cpu().numpy()[:, 1])
    return np.concatenate(out)


def random_muril(splits) -> dict:
    tok = AutoTokenizer.from_pretrained(MODELS / "muril_d1_seed42")
    model = AutoModelForSequenceClassification.from_pretrained(MODELS / "muril_d1_seed42")
    sv = muril_probs(splits["val"], tok, model)
    st = muril_probs(splits["test"], tok, model)
    saved = pd.read_csv(METRICS / "muril_random_seed42_predictions.csv",
                        encoding="utf-8-sig")
    picked = select_threshold(sv, splits["val"]["label"])
    picked_c = select_threshold(sv, splits["val"]["label"], min_precision=0.90)
    out = {
        "model": "MuRIL seed 42",
        "threshold_default": 0.5,
        "threshold_selected": picked["threshold"],
        "threshold_precision_constrained": picked_c["threshold"] if picked_c else None,
        "validation_at_selected": picked["validation"],
        "validation_default": point_metrics(
            splits["val"]["label"], apply_threshold(sv, 0.5), LABELS),
        "final_test_default": point_metrics(saved["label"], saved["prediction"], LABELS),
        "final_test_selected": held_metrics(saved, st, picked["threshold"]),
        "final_test_precision_constrained": (
            held_metrics(saved, st, picked_c["threshold"]) if picked_c else None),
        "changed_predictions_selected": int(
            (apply_threshold(st, picked["threshold"]) != saved["prediction"]).sum()),
        "validation_score_range": [float(sv.min()), float(sv.max())],
        "test_score_range": [float(st.min()), float(st.max())],
    }
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return out


def block_classical(full: pd.DataFrame, block_cv: pd.DataFrame) -> tuple[list[dict], pd.DataFrame]:
    rows, split_rows = [], []
    for fam in ("logreg", "linear_svm"):
        cfg = D1_RESULTS["models"][fam]["selected_config"]
        C = float(D1_RESULTS["models"][fam]["C"])
        name = "Logistic Regression" if fam == "logreg" else "Linear SVM"
        for b, fold in BLOCKS:
            tr = full[full["block"] != b]
            held = block_cv[(block_cv["model"] == fam) & (block_cv["fold"] == fold)]
            hs = held["score"].to_numpy()
            default = held_metrics(held, hs, 0.0)
            split_metrics = []
            for seed in range(42, 62):
                itr, iva = train_test_split(tr, test_size=0.20, stratify=tr["label"],
                                            random_state=seed)
                pipe = make_pipeline(cfg, fam, C, 2).fit(itr["text"], itr["label"])
                sv = scores(pipe, iva["text"])
                picked = select_threshold(sv, iva["label"])
                hm = held_metrics(held, hs, picked["threshold"])
                split_metrics.append({
                    "seed": seed, "threshold": picked["threshold"],
                    "inner_val_spam": int((iva["label"] == "Spam").sum()),
                    "inner_val_recall": picked["validation"]["spam_recall"],
                    "inner_val_precision": picked["validation"]["spam_precision"],
                    **{f"held_{k}": v for k, v in hm.items()
                       if k in ("accuracy", "macro_f1", "spam_recall", "spam_precision",
                                "spam_f1", "false_positives", "false_negatives")},
                })
            sm = pd.DataFrame(split_metrics)
            primary = split_metrics[0]
            picked_c = None
            # precision-constrained threshold on the same primary inner split
            itr, iva = train_test_split(tr, test_size=0.20, stratify=tr["label"],
                                        random_state=42)
            pipe = make_pipeline(cfg, fam, C, 2).fit(itr["text"], itr["label"])
            sv = scores(pipe, iva["text"])
            pc = select_threshold(sv, iva["label"], min_precision=0.90)
            if pc:
                picked_c = {"threshold": pc["threshold"],
                            "validation": pc["validation"],
                            "held": held_metrics(held, hs, pc["threshold"])}
            item = {
                "model": name, "fold": fold, "train_rows": int(len(tr)),
                "train_spam": int((tr["label"] == "Spam").sum()),
                "held_rows": int(len(held)),
                "held_spam": int((held["label"] == "Spam").sum()),
                "threshold_default": 0.0,
                "held_default": default,
                "primary_inner_seed": 42,
                "threshold_selected": primary["threshold"],
                "inner_val_spam": primary["inner_val_spam"],
                "inner_val_recall": primary["inner_val_recall"],
                "inner_val_precision": primary["inner_val_precision"],
                "held_selected": held_metrics(held, hs, primary["threshold"]),
                "threshold_precision_constrained": picked_c["threshold"] if picked_c else None,
                "held_precision_constrained": picked_c["held"] if picked_c else None,
                "stability": {
                    "n_splits": len(sm),
                    "threshold_mean": float(sm["threshold"].mean()),
                    "threshold_sd": float(sm["threshold"].std(ddof=1)),
                    "threshold_min": float(sm["threshold"].min()),
                    "threshold_max": float(sm["threshold"].max()),
                    "held_macro_f1_mean": float(sm["held_macro_f1"].mean()),
                    "held_macro_f1_sd": float(sm["held_macro_f1"].std(ddof=1)),
                    "held_recall_mean": float(sm["held_spam_recall"].mean()),
                    "held_recall_sd": float(sm["held_spam_recall"].std(ddof=1)),
                    "held_precision_mean": float(sm["held_spam_precision"].mean()),
                    "held_precision_sd": float(sm["held_spam_precision"].std(ddof=1)),
                    "share_macro_above_default": float(
                        (sm["held_macro_f1"] > default["macro_f1"]).mean()),
                    "share_recall_above_default": float(
                        (sm["held_spam_recall"] > default["spam_recall"]).mean()),
                },
            }
            rows.append(item)
            split_rows.extend([{**r, "model": name, "fold": fold} for r in split_metrics])
    return rows, pd.DataFrame(split_rows)


def block_muril_real(random_muril_item: dict) -> tuple[list[dict], list[dict]]:
    out, sweep = [], []
    transfer = random_muril_item["threshold_selected"]
    for seed in (42, 43, 44):
        for b, fold in BLOCKS:
            start = (b - 1) * 1000 + 1
            d = pd.read_csv(METRICS / f"muril_block{start}_seed{seed}_predictions.csv",
                            encoding="utf-8-sig")
            y = d["label"].to_numpy()
            s = d["prob_spam"].to_numpy()
            m = point_metrics(y, d["prediction"], LABELS)
            item = {
                "model": f"MuRIL seed {seed}", "fold": fold, "n": int(len(d)),
                "spam": int((y == "Spam").sum()),
                "default": m,
                "pr_auc": float(average_precision_score((y == "Spam").astype(int), s))
                if (y == "Spam").any() else None,
                "roc_auc": float(roc_auc_score((y == "Spam").astype(int), s))
                if (y == "Spam").any() else None,
                "spam_score_min": float(s[y == "Spam"].min()) if (y == "Spam").any() else None,
                "spam_score_median": float(np.median(s[y == "Spam"])) if (y == "Spam").any() else None,
                "spam_score_max": float(s[y == "Spam"].max()) if (y == "Spam").any() else None,
                "ham_score_median": float(np.median(s[y == "Ham"])),
                "ham_score_max": float(s[y == "Ham"].max()),
                "transfer_threshold": float(transfer) if seed == 42 else None,
                "transfer_result": held_metrics(d, s, transfer) if seed == 42 else None,
            }
            out.append(item)
            for t in (0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90):
                hm = held_metrics(d, s, t)
                sweep.append({"model": f"MuRIL seed {seed}", "fold": fold,
                              "threshold": t, **{k: hm[k] for k in
                                                 ("accuracy", "macro_f1", "spam_precision",
                                                  "spam_recall", "spam_f1",
                                                  "false_positives", "false_negatives")}})
    return out, sweep


def fig_pr_random(splits, muril_item):
    test = splits["test"].copy()
    curves = []
    for fam, name in (("logreg", "Logistic Regression"), ("linear_svm", "Linear SVM")):
        saved = pd.read_csv(METRICS / f"d1_malayalam_{fam}_test_predictions.csv",
                            encoding="utf-8-sig")
        y = (saved["label"] == "Spam").astype(int)
        curves.append((name, y, saved["score_spam"].to_numpy()))
    mp = pd.read_csv(METRICS / "muril_random_seed42_predictions.csv", encoding="utf-8-sig")
    curves.append(("MuRIL seed 42", (mp["label"] == "Spam").astype(int),
                   mp["prob_spam"].to_numpy()))
    plt.figure(figsize=(6.4, 4.8))
    for name, y, s in curves:
        p, r, _ = precision_recall_curve(y, s)
        ap = average_precision_score(y, s)
        plt.plot(r, p, label=f"{name} (AP {ap:.3f})")
    plt.xlabel("Spam recall")
    plt.ylabel("Spam precision")
    plt.title("D1 random test — precision–recall")
    plt.legend(loc="lower left", fontsize=8)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG / "pr_random_d1.png", dpi=160)
    plt.close()


def fig_pr_block6001():
    classic = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
    plt.figure(figsize=(6.4, 4.8))
    for fam, name in (("logreg", "Logistic Regression"), ("linear_svm", "Linear SVM")):
        d = classic[(classic["model"] == fam) & (classic["fold"] == "6001-7000")]
        y = (d["label"] == "Spam").astype(int)
        p, r, _ = precision_recall_curve(y, d["score"])
        plt.plot(r, p, label=f"{name} (AP {average_precision_score(y, d['score']):.3f})")
    d = pd.read_csv(METRICS / "muril_block6001_seed42_predictions.csv",
                    encoding="utf-8-sig")
    y = (d["label"] == "Spam").astype(int)
    p, r, _ = precision_recall_curve(y, d["prob_spam"])
    plt.plot(r, p, label=f"MuRIL 42 (AP {average_precision_score(y, d['prob_spam']):.3f})")
    plt.axhline(213 / 371, color="black", ls=":", lw=1, label="Spam prevalence 0.574")
    plt.xlabel("Spam recall")
    plt.ylabel("Spam precision")
    plt.title("D1 held-out block 6001–7000 — precision–recall")
    plt.legend(loc="lower left", fontsize=8)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG / "pr_block6001.png", dpi=160)
    plt.close()


def fig_scores_block6001():
    classic = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    series = []
    for fam, name in (("logreg", "Logistic Regression"), ("linear_svm", "Linear SVM")):
        d = classic[(classic["model"] == fam) & (classic["fold"] == "6001-7000")]
        series.append((name, d["label"], d["score"]))
    d = pd.read_csv(METRICS / "muril_block6001_seed42_predictions.csv",
                    encoding="utf-8-sig")
    series.append(("MuRIL seed 42", d["label"], d["prob_spam"]))
    for ax, (name, y, s) in zip(axes, series):
        ax.hist(s[y == "Ham"], bins=35, alpha=0.55, label="Ham", density=True)
        ax.hist(s[y == "Spam"], bins=35, alpha=0.55, label="Spam", density=True)
        ax.set_title(name, fontsize=9)
        ax.set_xlabel("score")
        ax.set_ylabel("density")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.2)
    fig.suptitle("Held-out block 6001–7000: score distributions by true class", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "scores_block6001.png", dpi=160)
    plt.close(fig)


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
    splits = load_splits()
    full = pd.concat([splits[p] for p in ("train", "val", "test")], ignore_index=True)
    full["block"] = ((full["source_row"].astype(int) - 1) // 1000) + 1
    block_cv = pd.read_csv(METRICS / "block_cv_predictions.csv", encoding="utf-8-sig")

    rnd_classic = random_classical(splits)
    rnd_muril = random_muril(splits)
    block_classic, block_splits = block_classical(full, block_cv)
    block_muril, muril_sweep = block_muril_real(rnd_muril)

    fig_pr_random(splits, rnd_muril)
    fig_pr_block6001()
    fig_scores_block6001()

    out = {
        "method": {
            "random_split": ("threshold selected on frozen validation split; model fitted on "
                             "frozen training split only; applied to saved final test scores"),
            "block_folds": ("threshold selected on a 80/20 stratified inner split of the two "
                            "training blocks (20 seeds); held-out block never used for selection"),
            "selection_rule": ("maximum Spam macro-F1; ties broken by maximum margin to the "
                               "nearest validation score; precision-constrained variant uses "
                               "validation Spam precision >= 0.90"),
            "muril_block": ("fold models were not saved; held-out score diagnostics only, plus "
                            "a labelled transfer of the seed-42 random-validation threshold"),
        },
        "random_split": {"classical": rnd_classic, "muril_seed42": rnd_muril},
        "block_folds": {"classical": block_classic, "muril": block_muril},
        "muril_threshold_sweep": muril_sweep,
        "figures": ["reports/figures/pr_random_d1.png",
                    "reports/figures/pr_block6001.png",
                    "reports/figures/scores_block6001.png"],
    }
    dump_json(out, METRICS / "threshold_calibration.json")
    block_splits.to_csv(METRICS / "threshold_calibration_splits.csv",
                        index=False, encoding="utf-8-sig")
    rows = []
    for r in rnd_classic + [rnd_muril]:
        rows.append({"context": "random", "model": r["model"],
                     "threshold_default": r["threshold_default"],
                     "threshold_selected": r["threshold_selected"],
                     "threshold_precision_constrained": r.get("threshold_precision_constrained"),
                     "test_default_macro_f1": r["final_test_default"]["macro_f1"],
                     "test_selected_macro_f1": r["final_test_selected"]["macro_f1"],
                     "test_default_recall": r["final_test_default"]["spam_recall"],
                     "test_selected_recall": r["final_test_selected"]["spam_recall"],
                     "test_default_precision": r["final_test_default"]["spam_precision"],
                     "test_selected_precision": r["final_test_selected"]["spam_precision"],
                     "changed_predictions": r["changed_predictions_selected"]})
    for r in block_classic:
        rows.append({"context": r["fold"], "model": r["model"],
                     "threshold_default": r["threshold_default"],
                     "threshold_selected": r["threshold_selected"],
                     "threshold_precision_constrained": r["threshold_precision_constrained"],
                     "test_default_macro_f1": r["held_default"]["macro_f1"],
                     "test_selected_macro_f1": r["held_selected"]["macro_f1"],
                     "test_default_recall": r["held_default"]["spam_recall"],
                     "test_selected_recall": r["held_selected"]["spam_recall"],
                     "test_default_precision": r["held_default"]["spam_precision"],
                     "test_selected_precision": r["held_selected"]["spam_precision"],
                     "changed_predictions": None})
    pd.DataFrame(rows).to_csv(METRICS / "threshold_calibration.csv", index=False,
                              encoding="utf-8-sig")

    parts = ["# Phase 2.3 threshold tables", "",
             "Generated by `p2_threshold.py`. Held-out labels are never used to select a threshold.", "",
             "## Random split", "",
             md_table([{"model": r["model"],
                        "t0": r["threshold_default"], "ts": r["threshold_selected"],
                        "tc": r.get("threshold_precision_constrained"),
                        "d_mf1": r["final_test_default"]["macro_f1"],
                        "s_mf1": r["final_test_selected"]["macro_f1"],
                        "d_r": r["final_test_default"]["spam_recall"],
                        "s_r": r["final_test_selected"]["spam_recall"],
                        "d_p": r["final_test_default"]["spam_precision"],
                        "s_p": r["final_test_selected"]["spam_precision"]}
                       for r in rnd_classic + [rnd_muril]],
                      [("model", "Model"), ("t0", "Default t"), ("ts", "Selected t"),
                       ("tc", "Precision t"), ("d_mf1", "Default macro-F1"),
                       ("s_mf1", "Selected macro-F1"), ("d_r", "Default R"),
                       ("s_r", "Selected R"), ("d_p", "Default P"), ("s_p", "Selected P")]),
             "", "## Block folds — primary inner split (seed 42)", "",
             md_table([{"model": r["model"], "fold": r["fold"],
                        "train_spam": r["train_spam"], "val_spam": r["inner_val_spam"],
                        "t0": r["threshold_default"], "ts": r["threshold_selected"],
                        "tc": r["threshold_precision_constrained"],
                        "d_mf1": r["held_default"]["macro_f1"],
                        "s_mf1": r["held_selected"]["macro_f1"],
                        "d_r": r["held_default"]["spam_recall"],
                        "s_r": r["held_selected"]["spam_recall"],
                        "d_p": r["held_default"]["spam_precision"],
                        "s_p": r["held_selected"]["spam_precision"]}
                       for r in block_classic],
                      [("model", "Model"), ("fold", "Held-out"), ("train_spam", "Train S"),
                       ("val_spam", "Inner-val S"), ("t0", "Default t"), ("ts", "Selected t"),
                       ("tc", "Precision t"), ("d_mf1", "Default macro-F1"),
                       ("s_mf1", "Selected macro-F1"), ("d_r", "Default R"),
                       ("s_r", "Selected R"), ("d_p", "Default P"), ("s_p", "Selected P")]),
             "", "## Block folds — 20-split threshold stability", "",
             md_table([{"model": r["model"], "fold": r["fold"],
                        "t_mean": r["stability"]["threshold_mean"],
                        "t_sd": r["stability"]["threshold_sd"],
                        "t_min": r["stability"]["threshold_min"],
                        "t_max": r["stability"]["threshold_max"],
                        "mf1_mean": r["stability"]["held_macro_f1_mean"],
                        "mf1_sd": r["stability"]["held_macro_f1_sd"],
                        "r_mean": r["stability"]["held_recall_mean"],
                        "r_sd": r["stability"]["held_recall_sd"],
                        "share": r["stability"]["share_macro_above_default"]}
                       for r in block_classic],
                      [("model", "Model"), ("fold", "Held-out"), ("t_mean", "t mean"),
                       ("t_sd", "t SD"), ("t_min", "t min"), ("t_max", "t max"),
                       ("mf1_mean", "Held macro-F1 mean"), ("mf1_sd", "SD"),
                       ("r_mean", "Held recall mean"), ("r_sd", "SD"),
                       ("share", "Share > default")]),
             "", "## MuRIL block diagnostics", "",
             md_table([{"model": r["model"], "fold": r["fold"], "spam": r["spam"],
                        "pr_auc": r["pr_auc"], "roc_auc": r["roc_auc"],
                        "s_min": r["spam_score_min"], "s_med": r["spam_score_median"],
                        "s_max": r["spam_score_max"], "h_med": r["ham_score_median"],
                        "h_max": r["ham_score_max"], "t": r["transfer_threshold"],
                        "trans_r": r["transfer_result"]["spam_recall"] if r["transfer_result"] else None,
                        "trans_p": r["transfer_result"]["spam_precision"] if r["transfer_result"] else None}
                       for r in block_muril],
                      [("model", "Model"), ("fold", "Held-out"), ("spam", "Spam"),
                       ("pr_auc", "PR-AUC"), ("roc_auc", "ROC-AUC"),
                       ("s_min", "Spam min"), ("s_med", "Spam median"), ("s_max", "Spam max"),
                       ("h_med", "Ham median"), ("h_max", "Ham max"),
                       ("t", "Transferred t"), ("trans_r", "Transferred R"),
                       ("trans_p", "Transferred P")]),
             ""]
    (REPORTS / "threshold_tables.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote threshold_calibration.json/.csv, threshold_calibration_splits.csv, tables and figures")
    for r in rnd_classic + [rnd_muril]:
        print("random", r["model"], "t", r["threshold_selected"],
              "default", round(r["final_test_default"]["macro_f1"], 4),
              round(r["final_test_default"]["spam_recall"], 4),
              "selected", round(r["final_test_selected"]["macro_f1"], 4),
              round(r["final_test_selected"]["spam_recall"], 4))
    for r in block_classic:
        print("block", r["model"], r["fold"], "t", round(r["threshold_selected"], 4),
              "default", round(r["held_default"]["macro_f1"], 4),
              round(r["held_default"]["spam_recall"], 4),
              "selected", round(r["held_selected"]["macro_f1"], 4),
              round(r["held_selected"]["spam_recall"], 4),
              "stab", round(r["stability"]["threshold_sd"], 3))


if __name__ == "__main__":
    main()
