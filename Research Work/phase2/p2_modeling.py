#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared TF-IDF + linear model training, selection and evaluation."""
from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from p2_common import (METRICS, MODELS, SPLITS, binary_metrics, dump_json,
                       multiclass_metrics)

CONFIGS = {
    "word_1_1": dict(analyzer="word", ngram_range=(1, 1)),
    "word_1_2": dict(analyzer="word", ngram_range=(1, 2)),
    "char_2_4": dict(analyzer="char_wb", ngram_range=(2, 4)),
    "char_2_5": dict(analyzer="char_wb", ngram_range=(2, 5)),
}

FAMILIES = {
    "logreg": lambda C, n_classes: LogisticRegression(
        C=C, class_weight="balanced", max_iter=5000,
        solver="liblinear" if n_classes == 2 else "lbfgs"),
    "linear_svm": lambda C, n_classes: LinearSVC(
        C=C, class_weight="balanced", max_iter=10000, dual="auto"),
}


def make_pipeline(config: str, family: str, C: float, n_classes: int = 2) -> Pipeline:
    vec = TfidfVectorizer(min_df=2, sublinear_tf=True, lowercase=True,
                          max_features=300_000, **CONFIGS[config])
    return Pipeline([("tfidf", vec), ("clf", FAMILIES[family](C, n_classes))])


def load_splits(tag: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames = {}
    for p in ("train", "val", "test"):
        df = pd.read_csv(SPLITS / f"{tag}_{p}.csv", encoding="utf-8-sig")
        df["has_latin"] = df["has_latin"].astype(str).str.lower().isin(["true", "1"])
        frames[p] = df
    return frames["train"], frames["val"], frames["test"]


def scores(pipe: Pipeline, X) -> np.ndarray:
    if hasattr(pipe, "predict_proba"):
        proba = pipe.predict_proba(X)
        if proba.shape[1] == 2:
            return proba[:, 1]
        return proba
    dec = pipe.decision_function(X)
    return dec


def margins(pipe: Pipeline, X) -> np.ndarray:
    s = scores(pipe, X)
    if s.ndim == 1:
        return np.abs(s)
    part = np.partition(s, -2, axis=1)
    return part[:, -1] - part[:, -2]


def grid_search(train, val, task: str, labels: list[str], c_grid=(0.5, 1.0, 2.0)) -> pd.DataFrame:
    rows = []
    ytr, yva = train["label"], val["label"]
    for family in FAMILIES:
        for config in CONFIGS:
            for C in c_grid:
                t0 = time.perf_counter()
                pipe = make_pipeline(config, family, C, len(labels))
                pipe.fit(train["text"], ytr)
                pred = pipe.predict(val["text"])
                if task == "binary":
                    m = binary_metrics(yva, pred)
                    row = {"val_accuracy": m["accuracy"], "val_macro_f1": m["macro_f1"],
                           "val_spam_recall": m["spam_recall"], "val_spam_precision": m["spam_precision"]}
                else:
                    m = multiclass_metrics(yva, pred, labels)
                    row = {"val_accuracy": m["accuracy"], "val_macro_f1": m["macro_f1"],
                           "val_weighted_f1": m["weighted_f1"]}
                rows.append({"task": task, "model": family, "config": config, "C": C,
                             "n_features": len(pipe.named_steps["tfidf"].vocabulary_),
                             "fit_seconds": round(time.perf_counter() - t0, 3), **row})
    return pd.DataFrame(rows).sort_values(["model", "val_macro_f1"], ascending=[True, False])


def fit_and_evaluate(train, val, test, task: str, labels: list[str], tag: str) -> dict:
    grid = grid_search(train, val, task, labels)
    grid.to_csv(METRICS / f"{tag}_validation_grid.csv", index=False, encoding="utf-8-sig")

    best_by_family = {}
    for family, sub in grid.groupby("model"):
        best_by_family[family] = sub.sort_values(
            ["val_macro_f1", "val_accuracy"], ascending=False).iloc[0].to_dict()

    # choose overall model by validation macro-F1 only (never test)
    overall_family = max(best_by_family, key=lambda f: best_by_family[f]["val_macro_f1"])
    trainval = pd.concat([train, val], ignore_index=True)
    results = {"task": task, "labels": labels, "tag": tag,
               "train_rows": int(len(train)), "val_rows": int(len(val)),
               "test_rows": int(len(test)),
               "train_class_counts": dict(Counter(train["label"])),
               "val_class_counts": dict(Counter(val["label"])),
               "test_class_counts": dict(Counter(test["label"])),
               "selection_metric": "validation macro-F1",
               "overall_model_family": overall_family,
               "models": {}}

    for family, best in best_by_family.items():
        pipe = make_pipeline(best["config"], family, float(best["C"]), len(labels))
        pipe.fit(trainval["text"], trainval["label"])
        pred = pipe.predict(test["text"])
        score = scores(pipe, test["text"])
        if task == "binary":
            metrics = binary_metrics(test["label"], pred, score)
            report = classification_report(test["label"], pred, labels=labels,
                                           output_dict=True, zero_division=0)
        else:
            metrics = multiclass_metrics(test["label"], pred, labels)
            report = classification_report(test["label"], pred, labels=labels,
                                           output_dict=True, zero_division=0)

        model_path = MODELS / f"{tag}_{family}.joblib"
        joblib.dump({"pipeline": pipe, "config": best["config"], "C": float(best["C"]),
                     "val_macro_f1": float(best["val_macro_f1"]), "labels": labels},
                    model_path)

        pred_df = test[["record_id", "source_row", "message", "text", "label", "group_id"]].copy()
        pred_df["prediction"] = pred
        if task == "binary":
            pred_df["score_spam"] = score
        else:
            pred_df["margin"] = margins(pipe, test["text"])
            for i, lab in enumerate(labels):
                pred_df[f"score_{lab}"] = score[:, i]
        pred_path = METRICS / f"{tag}_{family}_test_predictions.csv"
        pred_df.to_csv(pred_path, index=False, encoding="utf-8-sig")

        err = pred_df[pred_df["label"] != pred_df["prediction"]].copy()
        err["true"] = err["label"]
        err["pred"] = err["prediction"]
        err["has_url"] = err["message"].str.contains(r"https?://|www\.", case=False, regex=True)
        err["has_digit"] = err["message"].str.contains(r"\d", regex=True)
        err["n_tokens"] = err["text"].str.split().str.len()

        results["models"][family] = {
            "selected_config": best["config"], "C": float(best["C"]),
            "val": {k: float(best[k]) for k in best if k.startswith("val_")},
            "test": metrics,
            "classification_report": report,
            "model_file": model_path.name,
            "predictions_file": pred_path.name,
            "n_errors": int(len(err)),
        }

    # subgroup analysis for D1: Malayalam-only script rows in test
    if task == "binary" and "malayalam_only_script" in test.columns:
        mono = test["malayalam_only_script"].astype(str).str.lower().isin(["true", "1"])
        sub = test[mono]
        best = results["models"][overall_family]
        pipe = joblib.load(MODELS / f"{tag}_{overall_family}.joblib")["pipeline"]
        pred = pipe.predict(sub["text"])
        results["malayalam_only_subgroup"] = {
            "rows": int(len(sub)),
            "class_counts": dict(Counter(sub["label"])),
            "metrics": binary_metrics(sub["label"], pred, scores(pipe, sub["text"])),
            "note": "descriptive only; 11 spam test rows, no separate model was trained",
        }

    dump_json(results, METRICS / f"{tag}_results.json")
    return results


def error_examples(results: dict, tag: str, labels: list[str], top: int = 15) -> dict:
    """Top confident errors for the validation-selected model."""
    family = results["overall_model_family"]
    pred = pd.read_csv(METRICS / results["models"][family]["predictions_file"],
                       encoding="utf-8-sig")
    wrong = pred[pred["label"] != pred["prediction"]].copy()
    if "margin" in wrong.columns:
        wrong = wrong.sort_values("margin", ascending=False)
    elif "score_spam" in wrong.columns:
        wrong["margin"] = np.where(wrong["prediction"] == "Spam",
                                   wrong["score_spam"], 1 - wrong["score_spam"])
        wrong = wrong.sort_values("margin", ascending=False)
    out = []
    for _, r in wrong.head(top).iterrows():
        out.append({"record_id": r["record_id"], "source_row": int(r["source_row"]),
                    "true": r["label"], "pred": r["prediction"],
                    "margin": round(float(r.get("margin", 0)), 4),
                    "message": str(r["message"])[:300]})
    summary = {
        "model_family": family,
        "n_test": int(len(pred)),
        "n_errors": int(len(wrong)),
        "false_positives": int(((pred.label == "Ham") & (pred.prediction != "Ham")).sum())
        if labels == ["Ham", "Spam"] else None,
        "false_negatives": int(((pred.label == "Spam") & (pred.prediction != "Spam")).sum())
        if labels == ["Ham", "Spam"] else None,
        "examples": out,
    }
    dump_json(summary, METRICS / f"{tag}_error_examples.json")
    return summary
