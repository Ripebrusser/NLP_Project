# Phase 2 Summary — Classical Baselines

**Date:** 5 November 2026. **Classical Phase 2 report.** For transformer results, see `MURIL_BENCHMARK_REPORT.md` and `MODEL_COMPARISON.md` (Phase 2.2); this file is retained as the classical-baseline record.

## Headline results

| Experiment | Model | Accuracy | Macro-F1 | Key class metric |
|---|---|---|---|---|
| D1 Malayalam Ham/Spam (random grouped split) | Linear SVM, char 2–4, C=0.5 | **98.66%** | **0.9650** | Spam recall 88.24%; 0 false positives |
| D2 English Ham/Spam/Smishing | Logistic Regression, char 2–4, C=1.0 | **96.38%** | **0.8877** | Smishing recall 82.22%; Spam F1 0.8029 |

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
