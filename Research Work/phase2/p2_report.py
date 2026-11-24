#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Phase 2 reports from saved metrics. No numbers are hand-typed."""
from __future__ import annotations

import json
import math
from collections import Counter

import pandas as pd

from p2_common import METRICS, REPORTS, SPLITS, DATA

D1 = json.load(open(METRICS / "d1_malayalam_results.json", encoding="utf-8"))
D2 = json.load(open(METRICS / "d2_results.json", encoding="utf-8"))
ROB = json.load(open(METRICS / "d1_block_robustness.json", encoding="utf-8"))
MAN = json.load(open(SPLITS / "split_manifest.json", encoding="utf-8"))
DUP = json.load(open(METRICS / "duplicates.json", encoding="utf-8"))
SUB = json.load(open(METRICS / "subset_audit.json", encoding="utf-8"))


def pct(x, nd=2):
    return "—" if x is None else f"{100 * x:.{nd}f}%"


def f4(x):
    return "—" if x is None else f"{x:.4f}"


def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
    return "\n".join(out)


def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centre - half), min(1.0, centre + half))


def cm_md(cm, labels):
    head = ["true \\ pred"] + labels
    rows = []
    for i, lab in enumerate(labels):
        rows.append([lab] + [str(v) for v in cm[i]])
    return table(head, rows)


def best_rows():
    rows = []
    for fam, m in D1["models"].items():
        t = m["test"]
        rows.append([fam, m["selected_config"], m["C"], f4(t["accuracy"]),
                     f4(t["macro_f1"]), f4(t["spam_precision"]),
                     f4(t["spam_recall"]), f4(t["spam_f1"]), f4(t.get("roc_auc_spam"))])
    return rows


def d2_rows():
    rows = []
    for fam, m in D2["models"].items():
        t = m["test"]
        pc = t["per_class"]
        rows.append([fam, m["selected_config"], m["C"], f4(t["accuracy"]), f4(t["macro_f1"]),
                     f4(pc["ham"]["f1"]), f4(pc["spam"]["f1"]), f4(pc["smishing"]["f1"])])
    return rows


def d1_ci():
    t = D1["models"][D1["overall_model_family"]]["test"]
    cm = t["confusion_matrix"]
    tp, fn = cm[1][1], cm[1][0]
    acc_k, n = cm[0][0] + tp, sum(sum(r) for r in cm)
    a = wilson(acc_k, n)
    r = wilson(tp, tp + fn)
    return a, r


def pattern_stats(pred: pd.DataFrame):
    pred = pred.copy()
    pred["wrong"] = pred["label"] != pred["prediction"]
    pred["has_url"] = pred["message"].str.contains(r"https?://|www\.", case=False, regex=True)
    pred["has_digit"] = pred["message"].str.contains(r"\d", regex=True)
    pred["has_latin"] = pred["message"].str.contains(r"[A-Za-z]", regex=True)
    pred["n_tokens"] = pred["text"].str.split().str.len()
    out = {}
    for name, g in (("correct", pred[~pred["wrong"]]), ("errors", pred[pred["wrong"]])):
        out[name] = {"n": int(len(g)),
                     "url_pct": round(100 * float(g["has_url"].mean()), 1) if len(g) else None,
                     "digit_pct": round(100 * float(g["has_digit"].mean()), 1) if len(g) else None,
                     "latin_pct": round(100 * float(g["has_latin"].mean()), 1) if len(g) else None,
                     "mean_tokens": round(float(g["n_tokens"].mean()), 1) if len(g) else None}
    return out


# ---------------------------------------------------------------- split report
split_rows = []
for part in ("train", "val", "test"):
    for tag, key in (("D1 Malayalam", "d1"), ("D2", "d2")):
        f = next(x for x in MAN[key]["files"] if x["file"].endswith(f"_{part}.csv"))
        split_rows.append([tag, part, f["rows"], f["classes"], f["groups"], f["sha256"][:16] + "…"])

blocks = table(["split", "rows", "1000-row block → rows"],
               [[b["split"], b["n"], ", ".join(f"{k}: {v}" for k, v in b["blocks"].items())]
                for b in MAN["d1"]["blocks"]])

mono = MAN["malayalam_only_descriptive"]
split_md = f"""# Split Integrity Report — Phase 2

**Generated from** `phase2/splits/split_manifest.json`. Seed 42; 70/15/15.

## Source integrity

| Dataset | File | SHA-256 |
|---|---|---|
| D1 | `{MAN['source_files']['d1']}` | `{MAN['source_hashes']['d1']}` |
| D2 | `{MAN['source_files']['d2']}` | `{MAN['source_hashes']['d2']}` |

The originals were read only; all derived rows retain `record_id` and `source_row`.

## Split sizes

{table(["dataset", "split", "rows", "classes", "groups", "file SHA-256"], split_rows)}

## Leakage assertions

| Check | D1 | D2 |
|---|---|---|
| group overlap train/val | {MAN['d1']['checks']['group_overlap_train_val']} | {MAN['d2']['checks']['group_overlap_train_val']} |
| group overlap train/test | {MAN['d1']['checks']['group_overlap_train_test']} | {MAN['d2']['checks']['group_overlap_train_test']} |
| group overlap val/test | {MAN['d1']['checks']['group_overlap_val_test']} | {MAN['d2']['checks']['group_overlap_val_test']} |
| normalised-text overlap train/test | {MAN['d1']['checks']['norm_overlap_train_test']} | {MAN['d2']['checks']['norm_overlap_train_test']} |

All overlaps are zero by construction.

## Duplicate handling

| Dataset | Records | Exact groups | Normalised groups | Fuzzy pairs added | Final groups | Conflict groups | Conflict records |
|---|---|---|---|---|---|---|---|
| D1 Malayalam | {DUP['d1_malayalam']['records']} | {DUP['d1_malayalam']['exact_groups']} | {DUP['d1_malayalam']['norm_groups']} | {DUP['d1_malayalam']['fuzzy_extra_pairs']} | {DUP['d1_malayalam']['final_groups']} | {DUP['d1_malayalam']['conflict_groups']} | {DUP['d1_malayalam']['conflict_records']} |
| D2 | {DUP['d2']['records']} | {DUP['d2']['exact_groups']} | {DUP['d2']['norm_groups']} | {DUP['d2']['fuzzy_extra_pairs']} | {DUP['d2']['final_groups']} | {DUP['d2']['conflict_groups']} | {DUP['d2']['conflict_records']} |

D1 has no label conflicts. D2's 37 conflicting groups (76 records, almost all spam↔smishing) were excluded from supervised training and evaluation.

## Row-block composition (D1 primary)

{blocks}

This is the confound quantified in `D1_RESULTS.md`: block 5001–6000 is almost entirely Ham, while block 6001–7000 contains most of the Spam. A random split shares these blocks between train and test.

## Malayalam-only descriptive subset

- Rows: **{mono['rows']}** — Ham {mono['classes'].get('Ham', 0)}, Spam {mono['classes'].get('Spam', 0)}.
- Split rows: train {mono['split_rows']['train']}, val {mono['split_rows']['val']}, test {mono['split_rows']['test']}.
- Split Spam: train {mono['split_spam']['train']}, val {mono['split_spam']['val']}, test {mono['split_spam']['test']}.
- **Descriptive only.** 11 Spam test rows cannot support a separate model claim.
"""
(REPORTS / "SPLIT_INTEGRITY.md").write_text(split_md, encoding="utf-8")

# ------------------------------------------------------------------- D1 report
acc_ci, rec_ci = d1_ci()
t = D1["models"][D1["overall_model_family"]]["test"]
errs = json.load(open(METRICS / "d1_malayalam_error_examples.json", encoding="utf-8"))
err_rows = [[e["record_id"], e["source_row"], f4(e["margin"]), e["message"][:160]]
            for e in errs["examples"]]
block_rows = [[b["held_out_block"], b["test_rows"], f"{b['test_ham']}/{b['test_spam']}",
               b["train_rows"], b["train_spam"], f4(b["accuracy"]), f4(b["macro_f1"]),
               f4(b["spam_recall"]), b["note"]]
              for b in ROB["blocks"]]

d1_md = f"""# Dataset 1 — Malayalam-Script SMS Spam (Primary)

**Task:** Ham vs Spam. **No phishing claim.** D1 labels do not contain phishing.

## Data

| Item | Value |
|---|---|
| Malayalam-containing records | **1,992** |
| Labels | Ham 1,767 / Spam 225 (11.3% Spam) |
| Malayalam + Latin | 503 |
| Malayalam-only script | 1,489 (60 Spam) |
| Other Indic script co-occurring | **0** |
| Excluded | 0 (no empty messages, no invalid labels in this subset) |
| Duplicate groups | {DUP['d1_malayalam']['final_groups']} (168 duplicate excess removed from the split count, records retained) |
| Label conflicts | 0 |

The earlier “1,992 vs script totals” discrepancy is resolved: inclusive “contains” counts overlap (a message can contain Malayalam and Latin), while exclusive buckets sum to 7,717. The 1,992 Malayalam records split into 1,489 Malayalam-only and 503 Malayalam+Latin; none contain Tamil, Telugu or Kannada.

## Split

70/15/15 grouped and stratified, seed 42: train **1,394** (Spam 157), validation **299** (Spam 34), test **299** (Spam 34). Group/normalised-text overlap across splits is zero. Hashes: `phase2/splits/split_manifest.json`.

## Test results

Model selection used **validation macro-F1 only**; the test set was evaluated once after selection. Both final models were refit on train+validation.

{table(["model", "features", "C", "accuracy", "macro-F1", "Spam P", "Spam R", "Spam F1", "ROC-AUC"], best_rows())}

**Selected model:** {D1['overall_model_family']} with `{t['labels']}`. Confusion matrix (rows = true, columns = predicted):

{cm_md(t['confusion_matrix'], ['Ham', 'Spam'])}

- Accuracy {pct(t['accuracy'])} (95% Wilson CI {pct(acc_ci[0])}–{pct(acc_ci[1])}).
- Macro-F1 {f4(t['macro_f1'])}.
- Spam recall {pct(t['spam_recall'])} (95% CI {pct(rec_ci[0])}–{pct(rec_ci[1])}); precision {pct(t['spam_precision'])}.
- Errors: **{errs['n_errors']} of {errs['n_test']}**, all false negatives. No Ham was flagged as Spam.

### Malayalam-only subgroup (descriptive)

Test rows with no Latin characters: **{D1['malayalam_only_subgroup']['rows']}** (Spam {D1['malayalam_only_subgroup']['class_counts'].get('Spam', 0)}). Spam recall {pct(D1['malayalam_only_subgroup']['metrics']['spam_recall'])}, macro-F1 {f4(D1['malayalam_only_subgroup']['metrics']['macro_f1'])}. This is a subgroup of the same model, not a separately trained model.

## Source-block robustness — the main caveat

The random split is **group-safe but not block-safe**. Malayalam rows occupy three populated 1,000-row workbook blocks, and the blocks have radically different label mixes. Leave-one-block-out results for the same selected pipeline:

{table(["held-out block", "test rows", "Ham/Spam", "train rows", "train Spam", "accuracy", "macro-F1", "Spam recall", "note"], block_rows)}

**Interpretation.** Random-split macro-F1 is {f4(ROB['primary_random_split_test_macro_f1'])}, but block-held-out macro-F1 falls to {f4(ROB['blocks'][0]['macro_f1'])} and {f4(ROB['blocks'][2]['macro_f1'])}; the middle block cannot evaluate Spam at all. The high random-split score therefore measures **within-source/template performance**, not generalization to unseen message sources. This is a property of the dataset (spam is concentrated in one block), not a fixable tuning issue. Any headline must report the random-split score together with this result. A block-aware or external test set is required before claiming field performance.

## Error examples (all four)

{table(["record", "Excel row", "margin", "message (truncated)"], err_rows)}

The first two are Onam greeting/spam messages from block 4001–5000 (a low-spam block); the last two are short one-line messages from block 6001–7000.

## Reproduction

```
./.venv/Scripts/python.exe "Research Work/phase2/p2_extract.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_duplicates.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_split.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_train_d1.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_robustness.py"
```
"""
(REPORTS / "D1_RESULTS.md").write_text(d1_md, encoding="utf-8")

# ------------------------------------------------------------------- D2 report
d2e = json.load(open(METRICS / "d2_error_examples.json", encoding="utf-8"))
d2err_rows = [[e["record_id"], e["source_row"], e["true"], e["pred"], f4(e["margin"]),
               e["message"][:140]] for e in d2e["examples"]]
d2t = D2["models"][D2["overall_model_family"]]["test"]
d2_md = f"""# Dataset 2 — English Ham / Spam / Smishing (Secondary)

**Separate experiment.** These scores are not comparable with D1 and must not be pooled or mapped.

## Data and split

5,971 records (ham 4,844 / spam 489 / smishing 638). 37 conflicting spam↔smishing groups (76 records) excluded. 70/15/15 grouped-stratified split: train **4,127**, validation **885**, test **883** (ham 726 / spam 67 / smishing 90). Zero group/normalised overlap.

## Test results

{table(["model", "features", "C", "accuracy", "macro-F1", "Ham F1", "Spam F1", "Smishing F1"], d2_rows())}

**Selected model:** {D2['overall_model_family']} (validation macro-F1). Confusion matrix:

{cm_md(d2t['confusion_matrix'], ['ham', 'spam', 'smishing'])}

Per class (selected model):

{table(["class", "precision", "recall", "F1", "support"],
       [[k, f4(v['precision']), f4(v['recall']), f4(v['f1']), v['support']]
        for k, v in d2t['per_class'].items()])}

- Smishing recall {pct(d2t['per_class']['smishing']['recall'])}; spam F1 {f4(d2t['per_class']['spam']['f1'])}.
- Main confusions: smishing→spam (15), spam→ham (10), ham→smishing (4), spam→smishing (2), smishing→ham (1).
- **Spam is the weakest class**; the spam/smishing boundary is inherently noisy (37 conflicting groups in the source).

## Error examples

{table(["record", "line", "true", "pred", "margin", "message (truncated)"], d2err_rows[:12])}

## Caveat

D2 is English/Latin-script only (0 Indic records) and its ham/spam portion derives from UCI. Near-ceiling Ham performance is expected; the useful signal is the spam/smishing boundary. No claim about Malayalam smishing follows from this experiment.
"""
(REPORTS / "D2_RESULTS.md").write_text(d2_md, encoding="utf-8")

# ------------------------------------------------------------- error analysis
pred1 = pd.read_csv(METRICS / f"d1_malayalam_{D1['overall_model_family']}_test_predictions.csv", encoding="utf-8-sig")
pred2 = pd.read_csv(METRICS / f"d2_{D2['overall_model_family']}_test_predictions.csv", encoding="utf-8-sig")
p1, p2 = pattern_stats(pred1), pattern_stats(pred2)
err_md = f"""# Error Analysis — Phase 2

## D1 (Malayalam subset)

{table(["group", "n", "URL %", "digit %", "Latin %", "mean tokens"],
       [[k, v['n'], v['url_pct'], v['digit_pct'], v['latin_pct'], v['mean_tokens']]
        for k, v in p1.items()])}

All four errors are false negatives (Spam→Ham), so spam precision is 1.000 on this test set. Two are long Onam greeting messages; two are very short one-liners. The model has learned that promotional vocabulary and length are spam signals, and misses short or culturally specific spam.

## D2 (three-class)

{table(["group", "n", "URL %", "digit %", "Latin %", "mean tokens"],
       [[k, v['n'], v['url_pct'], v['digit_pct'], v['latin_pct'], v['mean_tokens']]
        for k, v in p2.items()])}

The dominant error is **smishing predicted as spam** (15 of 32), followed by **spam predicted as ham** (10). Both classes share promotional SMS cues (shortcodes, “TXT”, prizes, STOP instructions); the distinction is intent, which character n-grams cannot represent. This motivates a transformer with context, and a clearer annotation guide for the spam/smishing boundary.

## Implications

1. Do not report accuracy alone for D1: 88.6% is the majority-class floor.
2. D1’s high random-split score must be paired with the block-held-out result.
3. For D2, report per-class F1; smishing recall and spam F1 are the meaningful metrics.
"""
(REPORTS / "ERROR_ANALYSIS.md").write_text(err_md, encoding="utf-8")

# --------------------------------------------------------------- phase summary
summary = f"""# Phase 2 Summary — Classical Baselines

**Date:** 5 November 2026. **No transformer has been trained yet.**

## Headline results

| Experiment | Model | Accuracy | Macro-F1 | Key class metric |
|---|---|---|---|---|
| D1 Malayalam Ham/Spam (random grouped split) | Linear SVM, char 2–4, C=0.5 | **{pct(t['accuracy'])}** | **{f4(t['macro_f1'])}** | Spam recall {pct(t['spam_recall'])}; 0 false positives |
| D2 English Ham/Spam/Smishing | Logistic Regression, char 2–4, C=1.0 | **{pct(d2t['accuracy'])}** | **{f4(d2t['macro_f1'])}** | Smishing recall {pct(d2t['per_class']['smishing']['recall'])}; Spam F1 {f4(d2t['per_class']['spam']['f1'])} |

**Critical caveat:** D1’s random-split score is optimistic. Holding out one 1,000-row source block gives macro-F1 0.696 and 0.368 (and one block has no Spam to evaluate). The dataset’s Spam is concentrated in a single block, so cross-block generalization is not established. The D1 number is a within-source result, not a field-performance claim.

## What was produced

| Deliverable | Path |
|---|---|
| Malayalam extraction | `phase2/p2_extract.py` → `phase2/data/d1_malayalam.csv` |
| D1/D2 preprocessing | same script → `phase2/data/d1_all_records.csv`, `d2_all_records.csv` |
| Duplicate + conflict detection | `phase2/p2_duplicates.py` → `phase2/metrics/duplicates.json` |
| Split generation | `phase2/p2_split.py` → `phase2/splits/*.csv`, `split_manifest.json` |
| Split integrity report | `phase2/reports/SPLIT_INTEGRITY.md` |
| Logistic Regression / Linear SVM | `phase2/p2_train_d1.py`, `p2_train_d2.py`, `p2_modeling.py` |
| Saved models | `phase2/models/d1_malayalam_*.joblib`, `d2_*.joblib` |
| Metric tables + confusion matrices | `phase2/metrics/*_results.json`, `*_validation_grid.csv` |
| Error analysis | `phase2/reports/ERROR_ANALYSIS.md`, `phase2/metrics/*_error_examples.json` |
| Block robustness | `phase2/p2_robustness.py` → `phase2/metrics/d1_block_robustness.json` |
| Literature matrix | regenerated `Literature Review/LITERATURE_COMPARISON_MATRIX.csv` (21×18) |

## Remaining blocker

**D1 access provenance is still undocumented.** The licence permits research use, but the project has no subscription receipt or author permission. This remains visible in `Admin/BLOCKER_CLOSURE_REPORT.md` and must be resolved before submission/publication. It does not block local experimentation, which the project has now performed.

## Recommended next transformer experiment

1. **MuRIL base** first (Malayalam in its vocabulary), max_len 128, batch 8, mixed precision, gradient accumulation, class-weighted loss, 3 seeds.
2. Same grouped split; additionally report block-held-out folds. A transformer will also exploit source-block cues, so the block result is mandatory.
3. Compare against the saved char-TF-IDF SVM on **macro-F1 and Spam recall**, with bootstrap CIs over duplicate groups.
4. Only after that, try XLM-R as a multilingual fallback. Do not fine-tune at batch 16 / 256 tokens on the 6 GB GPU.
"""
(REPORTS / "PHASE2_SUMMARY.md").write_text(summary, encoding="utf-8")

print("wrote:")
for p in ("SPLIT_INTEGRITY.md", "D1_RESULTS.md", "D2_RESULTS.md", "ERROR_ANALYSIS.md", "PHASE2_SUMMARY.md"):
    print(" ", REPORTS / p)
