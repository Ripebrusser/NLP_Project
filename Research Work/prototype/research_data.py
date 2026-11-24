#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only access to the frozen Phase 2 result artifacts.

Nothing here retrains, writes or modifies an experiment artifact. The app
formats these values for display; it does not invent or estimate metrics.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PHASE2 = PROJECT_ROOT / "Research Work" / "phase2"
METRICS = PHASE2 / "metrics"


def _json(name: str) -> dict:
    with open(METRICS / name, encoding="utf-8") as handle:
        return json.load(handle)


def d1_results() -> dict:
    return _json("d1_malayalam_results.json")


def d2_results() -> dict:
    return _json("d2_results.json")


def muril_results() -> dict:
    return _json("muril_results.json")


def validation_summary() -> dict:
    return _json("validation_summary.json")


def confidence_intervals() -> dict:
    return _json("confidence_intervals.json")


def final_comparison() -> pd.DataFrame:
    return pd.read_csv(METRICS / "final_model_comparison.csv", encoding="utf-8-sig")


def _ci_text(interval: dict | None) -> str:
    if not interval:
        return "—"
    return f"{interval['point']:.4f} [{interval['ci_low']:.4f}, {interval['ci_high']:.4f}]"


def d1_model_table() -> pd.DataFrame:
    data = d1_results()
    ci = confidence_intervals()["results"]
    rows = []
    for family, name in (("logreg", "Logistic Regression"), ("linear_svm", "Linear SVM")):
        test = data["models"][family]["test"]
        interval = ci[f"D1::{name}"]["metrics"]["macro_f1"]
        rows.append({
            "Model": name,
            "Accuracy": test["accuracy"],
            "Macro-F1 [95% CI]": _ci_text(interval),
            "Ham F1": test["ham_f1"],
            "Spam F1": test["spam_f1"],
            "Spam recall": test["spam_recall"],
        })
    aggregate = muril_results()["random_split"]["aggregate"]
    rows.append({
        "Model": "MuRIL (3-seed mean)",
        "Accuracy": f"{aggregate['accuracy']['mean']:.4f} ± {aggregate['accuracy']['sd']:.4f}",
        "Macro-F1 [95% CI]": f"{aggregate['macro_f1']['mean']:.4f} ± {aggregate['macro_f1']['sd']:.4f} (seed SD)",
        "Ham F1": f"{aggregate['ham_f1']['mean']:.4f}",
        "Spam F1": f"{aggregate['spam_f1']['mean']:.4f}",
        "Spam recall": f"{aggregate['spam_recall']['mean']:.4f} ± {aggregate['spam_recall']['sd']:.4f}",
    })
    return pd.DataFrame(rows)


def d2_model_table() -> pd.DataFrame:
    data = d2_results()
    ci = confidence_intervals()["results"]
    rows = []
    for family, name in (("logreg", "Logistic Regression"), ("linear_svm", "Linear SVM")):
        test = data["models"][family]["test"]
        per = test["per_class"]
        interval = ci[f"D2::{name}"]["metrics"]["macro_f1"]
        rows.append({
            "Model": name,
            "Accuracy": test["accuracy"],
            "Macro-F1 [95% CI]": _ci_text(interval),
            "Ham F1": per["ham"]["f1"],
            "Spam F1": per["spam"]["f1"],
            "Smishing F1": per["smishing"]["f1"],
            "Spam recall": per["spam"]["recall"],
            "Smishing recall": per["smishing"]["recall"],
        })
    return pd.DataFrame(rows)


def d1_confusion(family: str) -> list[list[int]]:
    return d1_results()["models"][family]["test"]["confusion_matrix"]


def d2_confusion(family: str) -> list[list[int]]:
    return d2_results()["models"][family]["test"]["confusion_matrix"]


def muril_random_table() -> pd.DataFrame:
    runs = muril_results()["random_split"]["runs"]
    rows = []
    for run in runs:
        test = run["test"]
        rows.append({
            "Seed": run["seed"],
            "Accuracy": test["accuracy"],
            "Macro-F1": test["macro_f1"],
            "Ham F1": test["ham_f1"],
            "Spam F1": test["spam_f1"],
            "Spam recall": test["spam_recall"],
            "Spam precision": test["spam_precision"],
        })
    return pd.DataFrame(rows)


def classic_block_table() -> pd.DataFrame:
    blocks = validation_summary()["block_cv"]
    rows = []
    for family, name in (("logreg", "Logistic Regression"), ("linear_svm", "Linear SVM")):
        for fold in blocks[family]["folds"]:
            rows.append({
                "Block": fold["held_out_block"],
                "Model": name,
                "Rows": fold["test_rows"],
                "Spam": fold["test_spam"],
                "Accuracy": fold["accuracy"],
                "Macro-F1": fold["macro_f1"],
                "Spam recall": fold["spam_recall"],
                "False positives": fold["confusion_matrix"][0][1],
            })
    return pd.DataFrame(rows)


def muril_block_table() -> pd.DataFrame:
    rows = []
    for run in muril_results()["block_held_out"]["per_seed_pooled"]:
        for fold in run["folds"]:
            rows.append({
                "Block": fold["held_out_block"],
                "Seed": run["seed"],
                "Rows": fold["ham_support"] + fold["spam_support"],
                "Spam": fold["spam_support"],
                "Accuracy": fold["accuracy"],
                "Macro-F1": fold["macro_f1"],
                "Spam recall": fold["spam_recall"],
                "False positives": fold["confusion_matrix"][0][1],
            })
    return pd.DataFrame(rows)


def muril_block_aggregate() -> dict:
    return muril_results()["block_held_out"]["aggregate_pooled"]
