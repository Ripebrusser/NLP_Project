#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Source-block robustness for D1: leave-one-1000-row-block-out.

The primary split is group-safe but random with respect to workbook row order.
Malayalam records sit in three populated 1,000-row blocks, one of which is 100%
Ham, so this check measures how much the random-split score depends on block
overlap. It is a diagnostic, not the headline result.
"""
from __future__ import annotations

import json
from collections import Counter

import joblib
import pandas as pd

from p2_common import METRICS, MODELS, SPLITS, binary_metrics, block_number, dump_json
from p2_modeling import make_pipeline

df = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
# rebuild the full labeled frame from the three split files
parts = [pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
         for p in ("train", "val", "test")]
full = pd.concat(parts, ignore_index=True)
full["block"] = full["source_row"].map(block_number)

best = json.load(open(METRICS / "d1_malayalam_results.json", encoding="utf-8"))
fam = best["overall_model_family"]
cfg = best["models"][fam]["selected_config"]
C = best["models"][fam]["C"]

rows = []
for block, test in sorted(full.groupby("block")):
    train = full[full["block"] != block]
    pipe = make_pipeline(cfg, fam, float(C), 2)
    pipe.fit(train["text"], train["label"])
    pred = pipe.predict(test["text"])
    score = pipe.decision_function(test["text"]) if hasattr(pipe, "decision_function") else pipe.predict_proba(test["text"])[:, 1]
    n_spam = int((test["label"] == "Spam").sum())
    m = binary_metrics(test["label"], pred, score)
    rows.append({
        "held_out_block": f"{(block-1)*1000+1}-{block*1000}",
        "test_rows": int(len(test)),
        "test_ham": int((test["label"] == "Ham").sum()),
        "test_spam": n_spam,
        "train_rows": int(len(train)),
        "train_spam": int((train["label"] == "Spam").sum()),
        "accuracy": m["accuracy"],
        "macro_f1": m["macro_f1"],
        "spam_recall": m["spam_recall"] if n_spam else None,
        "spam_precision": m["spam_precision"] if n_spam else None,
        "confusion_matrix": m["confusion_matrix"],
        "evaluable_for_spam": bool(n_spam and (train["label"] == "Spam").sum()),
        "note": ("test block contains no Spam" if not n_spam else
                 "train blocks contain almost no Spam" if (train["label"] == "Spam").sum() < 20 else ""),
    })

out = {
    "model": {"family": fam, "config": cfg, "C": C},
    "design": "leave-one-1000-row-block-out; blocks derived from Excel source_row",
    "blocks": rows,
    "primary_random_split_test_macro_f1": best["models"][fam]["test"]["macro_f1"],
    "primary_random_split_test_spam_recall": best["models"][fam]["test"]["spam_recall"],
    "interpretation": ("If block-held-out scores are materially lower than the random-split "
                       "score, the random split is optimistic because train and test share "
                       "source-block style/template structure. The headline result must then "
                       "be reported with that caveat, and a block-aware split should be the "
                       "confirmatory design."),
}
dump_json(out, METRICS / "d1_block_robustness.json")
print(json.dumps(out, ensure_ascii=False, indent=2))
