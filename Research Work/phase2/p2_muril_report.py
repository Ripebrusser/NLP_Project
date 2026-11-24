#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2.2: verification, error extraction and tables for the D1 MuRIL run.

Reads only saved artifacts. Does not train, tune or change any split.

Run:
    ./.venv/Scripts/python.exe "Research Work/phase2/p2_muril_report.py"
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from p2_common import METRICS, MODELS, REPORTS, SPLITS

LABELS = ["Ham", "Spam"]
BLOCKS = ["4001-5000", "5001-6000", "6001-7000"]


def fmt(v, nd=4):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def load_full() -> pd.DataFrame:
    return pd.concat([pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
                      for p in ("train", "val", "test")], ignore_index=True)


def verify_model(results: dict, full: pd.DataFrame) -> dict:
    test = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
    saved = pd.read_csv(METRICS / "muril_random_seed42_predictions.csv", encoding="utf-8-sig")
    tok = AutoTokenizer.from_pretrained(MODELS / "muril_d1_seed42")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODELS / "muril_d1_seed42").eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    probs = []
    with torch.no_grad():
        for i in range(0, len(test), 32):
            enc = tok(test["text"].iloc[i:i + 32].tolist(), truncation=True,
                      max_length=results["max_len"], padding="max_length",
                      return_tensors="pt").to(device)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda",
                                    dtype=torch.float16):
                logits = model(**enc).logits
            probs.append(torch.softmax(logits.float(), -1).cpu().numpy())
    prob = np.concatenate(probs)
    pred = np.array(LABELS)[prob.argmax(1)]
    saved_aligned = saved.set_index("record_id").loc[test["record_id"]]
    out = {
        "model_dir": "models/muril_d1_seed42",
        "tokenizer_class": type(tok).__name__,
        "vocab_size": int(tok.vocab_size),
        "params": int(sum(p.numel() for p in model.parameters())),
        "malayalam_roundtrip": bool(
            tok.decode(tok.encode("ഇന്ന് വൈകുന്നേരം 5 മണിക്ക് ഫോൺ ചെയ്യുക",
                                  add_special_tokens=False))
            == "ഇന്ന് വൈകുന്നേരം 5 മണിക്ക് ഫോൺ ചെയ്യുക"),
        "predictions_reproduced": bool((pred == saved_aligned["prediction"].to_numpy()).all()),
        "max_abs_prob_diff": float(np.abs(prob[:, 1] - saved_aligned["prob_spam"].to_numpy()).max()),
        "n_checked": int(len(test)),
    }
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return out


def main() -> None:
    results = json.load(open(METRICS / "muril_results.json", encoding="utf-8"))
    classic = json.load(open(METRICS / "validation_summary.json", encoding="utf-8"))
    full = load_full()
    text = full.set_index("record_id")["text"]

    verification = verify_model(results, full)
    (METRICS / "muril_artifact_verification.json").write_text(
        json.dumps(verification, indent=2), encoding="utf-8")

    random_runs = results["random_split"]["runs"]
    agg = results["random_split"]["aggregate"]
    lines = ["# MuRIL D1 — machine-generated tables", "",
             "Source: `metrics/muril_results.json`; do not edit by hand.", "",
             "## Configuration and data", "",
             "| Item | Value |", "|---|---|",
             f"| Model | `{results['model_name']}` |",
             f"| Max sequence length | {results['max_len']} (covers "
             f"{results['token_lengths']['coverage_at_max_len']*100:.1f}% of rows) |",
             f"| Token length median / p95 / p99 / max | "
             f"{results['token_lengths']['median']:.0f} / {results['token_lengths']['p95']:.0f} / "
             f"{results['token_lengths']['p99']:.2f} / {results['token_lengths']['max']} |",
             f"| Learning rate | {results['hyperparameters']['lr']} |",
             f"| Batch / accumulation / effective | {results['hyperparameters']['batch']} / "
             f"{results['hyperparameters']['accum']} / {results['hyperparameters']['effective_batch']} |",
             f"| Max epochs / patience | {results['hyperparameters']['epochs_max']} / "
             f"{results['hyperparameters']['patience']} |",
             f"| Class weights (train) | {random_runs[0]['class_weights'][0]:.4f} Ham / "
             f"{random_runs[0]['class_weights'][1]:.4f} Spam |",
             f"| Package versions | torch {results['versions']['torch']}, transformers "
             f"{results['versions']['transformers']}, CUDA {results['versions']['cuda']} |",
             f"| GPU | {results['versions']['gpu']} |",
             f"| Saved reference model reproduces predictions | "
             f"{verification['predictions_reproduced']} (max prob diff "
             f"{verification['max_abs_prob_diff']:.2e}) |", ""]

    lines += ["## Random grouped split — per seed", "",
              "| Seed | Selected epoch | Accuracy | Macro-F1 | Ham F1 | Spam P | Spam R | Spam F1 | Train s | Peak GPU MB |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in random_runs:
        t = r["test"]
        lines.append(f"| {r['seed']} | {r['selected_epoch']} | {fmt(t['accuracy'])} | "
                     f"{fmt(t['macro_f1'])} | {fmt(t['ham_f1'])} | {fmt(t['spam_precision'])} | "
                     f"{fmt(t['spam_recall'])} | {fmt(t['spam_f1'])} | "
                     f"{r['train_seconds']:.0f} | {r['max_gpu_memory_mb']:.0f} |")
    lines.append(f"| **Mean ± SD** | — | {fmt(agg['accuracy']['mean'])} ± "
                 f"{fmt(agg['accuracy']['sd'])} | **{fmt(agg['macro_f1']['mean'])} ± "
                 f"{fmt(agg['macro_f1']['sd'])}** | {fmt(agg['ham_f1']['mean'])} ± "
                 f"{fmt(agg['ham_f1']['sd'])} | {fmt(agg['spam_precision']['mean'])} ± "
                 f"{fmt(agg['spam_precision']['sd'])} | {fmt(agg['spam_recall']['mean'])} ± "
                 f"{fmt(agg['spam_recall']['sd'])} | {fmt(agg['spam_f1']['mean'])} ± "
                 f"{fmt(agg['spam_f1']['sd'])} | — | — |")
    lines += ["", "Confusion matrices (rows Ham, Spam; columns Ham, Spam):", ""]
    for r in random_runs:
        lines.append(f"- seed {r['seed']}: `{r['test']['confusion_matrix']}`")
    lines.append("")

    lines += ["## Block-held-out — every fold and seed", "",
              "Fixed epochs per seed from random validation; held-out block never used for "
              "stopping or tuning.", "",
              "| Seed | Held-out block | Test n | Ham/Spam | Accuracy | Macro-F1 | Spam P | Spam R | Confusion |",
              "|---|---|---|---|---|---|---|---|---|"]
    for s in results["block_held_out"]["per_seed_pooled"]:
        for f in s["folds"]:
            lines.append(f"| {s['seed']} | {f['held_out_block']} | {sum(f['confusion_matrix'][0])+sum(f['confusion_matrix'][1])} | "
                         f"{f['ham_support']}/{f['spam_support']} | {fmt(f['accuracy'])} | "
                         f"{fmt(f['macro_f1'])} | {fmt(f['spam_precision'])} | "
                         f"{fmt(f['spam_recall'])} | `{f['confusion_matrix']}` |")
    lines += ["", "## Block-held-out — pooled per seed", "",
              "| Seed | Accuracy | Macro-F1 | Spam P | Spam R | Spam F1 | Confusion |",
              "|---|---|---|---|---|---|---|"]
    for s in results["block_held_out"]["per_seed_pooled"]:
        p = s["pooled"]
        lines.append(f"| {s['seed']} | {fmt(p['accuracy'])} | {fmt(p['macro_f1'])} | "
                     f"{fmt(p['spam_precision'])} | {fmt(p['spam_recall'])} | "
                     f"{fmt(p['spam_f1'])} | `{p['confusion_matrix']}` |")
    pa = results["block_held_out"]["aggregate_pooled"]
    lines.append(f"| **Mean ± SD** | {fmt(pa['accuracy']['mean'])} ± {fmt(pa['accuracy']['sd'])} | "
                 f"**{fmt(pa['macro_f1']['mean'])} ± {fmt(pa['macro_f1']['sd'])}** | "
                 f"{fmt(pa['spam_precision']['mean'])} ± {fmt(pa['spam_precision']['sd'])} | "
                 f"{fmt(pa['spam_recall']['mean'])} ± {fmt(pa['spam_recall']['sd'])} | "
                 f"{fmt(pa['spam_f1']['mean'])} ± {fmt(pa['spam_f1']['sd'])} | — |")
    lines.append("")

    lines += ["## Classical versus MuRIL (actual saved results)", "",
              "| Model | Random-split Macro-F1 | Random-split Spam recall | Block-held-out Macro-F1 (pooled) | Block-held-out Spam recall |",
              "|---|---|---|---|---|"]
    for name, key in (("Logistic Regression", "logreg"), ("Linear SVM", "linear_svm")):
        c = next(x for x in classic["comparison"]["D1"] if x["model"] == key)
        pooled = classic["block_cv"][key]["pooled"]
        lines.append(f"| {name} | {fmt(c['macro_f1'])} | {fmt(c['per_class'][1]['recall'])} | "
                     f"{fmt(pooled['macro_f1'])} | {fmt(pooled['spam_recall'])} |")
    lines.append(f"| MuRIL (3-seed mean) | {fmt(agg['macro_f1']['mean'])} | "
                 f"{fmt(agg['spam_recall']['mean'])} | {fmt(pa['macro_f1']['mean'])} | "
                 f"{fmt(pa['spam_recall']['mean'])} |")
    lines.append("")
    (REPORTS / "muril_tables.md").write_text("\n".join(lines), encoding="utf-8")

    # Error examples, seed 42 (reference model), joined to source text.
    errors = {}
    rp = pd.read_csv(METRICS / "muril_random_seed42_predictions.csv", encoding="utf-8-sig")
    test = pd.read_csv(SPLITS / "d1_malayalam_test.csv", encoding="utf-8-sig")
    rd = rp.merge(test[["record_id", "group_id"]], on="record_id")
    errors["random_seed42"] = [
        {**{k: (int(v) if k == "source_row" else v) for k, v in row.items()
           if k in ("record_id", "source_row", "label", "prediction", "prob_spam", "group_id")},
         "text": str(text[row["record_id"]])[:240]}
        for _, row in rd[rd["label"] != rd["prediction"]].iterrows()]

    for b in (4001, 5001, 6001):
        bp = pd.read_csv(METRICS / f"muril_block{b}_seed42_predictions.csv",
                         encoding="utf-8-sig")
        err = bp[bp["label"] != bp["prediction"]]
        errors[f"block_{b}_seed42"] = {
            "n_errors": int(len(err)),
            "false_negatives": int(((bp["label"] == "Spam") & (bp["prediction"] == "Ham")).sum()),
            "false_positives": int(((bp["label"] == "Ham") & (bp["prediction"] == "Spam")).sum()),
            "examples": [
                {**{k: (int(v) if k == "source_row" else v) for k, v in row.items()
                   if k in ("record_id", "source_row", "label", "prediction", "prob_spam")},
                 "text": str(text[row["record_id"]])[:240]}
                for _, row in err.head(10).iterrows()],
        }
    (METRICS / "muril_error_examples.json").write_text(
        json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")

    print("verification:", json.dumps(verification, indent=1))
    print("wrote reports/muril_tables.md, metrics/muril_error_examples.json")
    print("random errors:", len(errors["random_seed42"]))
    for b in (4001, 5001, 6001):
        print(b, errors[f"block_{b}_seed42"]["n_errors"],
              "FN", errors[f"block_{b}_seed42"]["false_negatives"],
              "FP", errors[f"block_{b}_seed42"]["false_positives"])


if __name__ == "__main__":
    main()
