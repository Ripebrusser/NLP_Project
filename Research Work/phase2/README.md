# Phase 2 — Classical, MuRIL and Statistical Validation

Reproducible pipeline for the Malayalam-first SMS spam study. Originals are read-only.

## Environment

Python 3.14 with a project-local virtual environment:

```bash
py -m venv .venv
./.venv/Scripts/python.exe -m pip install scikit-learn pandas openpyxl joblib matplotlib
```

For the MuRIL benchmark, install a CUDA build of PyTorch and Transformers into the same environment:

```bash
./.venv/Scripts/python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
./.venv/Scripts/python.exe -m pip install transformers
```

## Run order

```bash
./.venv/Scripts/python.exe "Research Work/phase2/p2_extract.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_duplicates.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_split.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_train_d1.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_train_d2.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_robustness.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_report.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_validate.py"   # Phase 2.1 validation
./.venv/Scripts/python.exe "Research Work/phase2/p2_ci.py"         # Phase 2.2 legacy; superseded by p2_stats.py
./.venv/Scripts/python.exe "Research Work/phase2/p2_muril.py" --seeds 42 43 44   # GPU
./.venv/Scripts/python.exe "Research Work/phase2/p2_muril_report.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_stats.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_threshold.py"
```

## Artifacts

| Path | Contents |
|---|---|
| `data/d1_malayalam.csv` | 1,992 Malayalam records, source rows, script flags |
| `data/d1_malayalam_grouped.csv` | + duplicate group and conflict flags |
| `data/d2_grouped.csv` | 5,971 D2 records with groups/conflicts |
| `splits/*.csv` | train/val/test files |
| `splits/split_manifest.json` | seed, counts, assertions, SHA-256 |
| `models/*.joblib` | best LR and Linear SVM per dataset |
| `metrics/*_validation_grid.csv` | all validation runs |
| `metrics/*_results.json` | test metrics, confusion matrices, per-class |
| `metrics/*_test_predictions.csv` | row-level predictions and scores |
| `metrics/d1_block_robustness.json` | Phase 2 leave-one-block-out diagnostic (historical block labels) |
| `metrics/validation_summary.json` | Phase 2.1 block audit, corrected block CV, D2 diagnostics |
| `metrics/baseline_comparison.csv` | flat four-model comparison |
| `metrics/block_cv_predictions.csv` | row-level predictions for all six block folds |
| `reports/BASELINE_VALIDATION_AND_ROBUSTNESS_REPORT.md` | Phase 2.1 validation report |
| `reports/baseline_validation_tables.md` | machine-generated Phase 2.1 tables |
| `metrics/confidence_intervals.json` / `.csv` | Phase 2.3 complete bootstrap CIs, all classical models and MuRIL seeds |
| `models/muril_d1_seed42/` | saved MuRIL model + tokenizer (913 MB) |
| `metrics/muril_results.json` | MuRIL runs, histories, metrics, confusion matrices, versions |
| `metrics/muril_*_predictions.csv` | random-split and block-fold predictions, all seeds |
| `metrics/muril_error_examples.json` | MuRIL error rows with text and probabilities |
| `reports/CONFIDENCE_INTERVAL_REPORT.md` | Part A report |
| `reports/MURIL_BENCHMARK_REPORT.md` | Parts B/C report |
| `reports/MODEL_COMPARISON.md` | Part D comparison and Part E external-validation design |
| `reports/muril_tables.md` | machine-generated MuRIL tables |
| `metrics/paired_model_comparison.json/.csv` | paired bootstrap differences, random test |
| `metrics/block_paired_comparison.csv` | paired differences, pooled and block 6001 |
| `metrics/muril_seed_variation.json/.csv` | across-seed variation, reported separately from within-seed CIs |
| `metrics/threshold_calibration.json/.csv` | validation-selected thresholds and sweeps |
| `metrics/threshold_calibration_splits.csv` | all 120 inner-split threshold results |
| `metrics/final_model_comparison.csv/.json` | consolidated final comparison |
| `reports/statistical_tables.md` | machine-generated CI and paired tables |
| `reports/threshold_tables.md` | machine-generated threshold tables |
| `reports/PAIRED_MODEL_COMPARISON.md` | Phase 2.3 paired comparison |
| `reports/THRESHOLD_CALIBRATION_REPORT.md` | Phase 2.3 threshold/source-shift diagnosis |
| `reports/FINAL_MODEL_SELECTION.md` | Phase 2.3 selection decision |
| `reports/FINAL_EXPERIMENTAL_METHODOLOGY.md` | reproducible final methodology |
| `reports/figures/pr_random_d1.png`, `pr_block6001.png`, `scores_block6001.png` | PR curves and block-6001 score distributions |
| `reports/` | split integrity, D1/D2 results, error analysis, summary |

## Code audit and verification (8 November 2026)

The Phase 2 artifacts are frozen. The single entry point runs every check and proves nothing moved:

```bash
# from the project root
.venv/Scripts/python.exe "Research Work/run_full_audit.py"
```

It writes `metrics/full_audit_results.json` and preserves prior verification outputs under `metrics/audit_runs/<run_id>/`. Exit status 0 means all required checks passed. Individual checks:

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/tests/run_tests.py"
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/prototype/verify_prototype.py"
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/validate_literature_matrix.py"
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/tests/write_audit_verification.py"
```

`p2_final_verification.py` and `p2_final_audit_stats.py` are also safe to re-run: they read frozen predictions only and rewrite their own JSON outputs. Preserve `*.before_code_audit.json` copies before doing so.

Audit findings that affect how this directory should be read:

- **`p2_common.block_number()` is the authority for row blocks.** The stale double subtraction in the old `p2_split.py` / `p2_robustness.py` mapped the first row of every block into the previous block. The frozen `splits/split_manifest.json` still contains the resulting 631/991/370 table; the correct composition is **630/991/371** (618H/12S, 991H/0S, 158H/213S). The manifest is deliberately not edited.
- **`metrics/d1_block_robustness.json` is historical** and uses the old membership. Use `validation_summary.json` and `block_cv_predictions.csv` for block results.
- **`p2_ci.py` is legacy.** `p2_stats.py` is authoritative. `p2_ci.py` now writes `confidence_intervals_legacy.json/.csv` and `CONFIDENCE_INTERVAL_REPORT.legacy.md`; only an explicit `--overwrite-authoritative` writes the canonical files.
- **Prediction files are aligned by `record_id`** through `p2_common.align_predictions()`, which rejects missing, extra, duplicate or mislabelled rows instead of silently merging.
- **Do not rerun** `p2_split.py`, `p2_robustness.py`, `p2_train_d1.py`, `p2_train_d2.py` or `p2_muril.py`: they rewrite frozen splits, diagnostic output or trained models.

Full evidence: `Admin/FINAL_CODE_AUDIT_REPORT.md`, `Admin/FINAL_CODE_FIX_REGISTER.md`, `Admin/FINAL_TEST_REPORT.md`, `Admin/FINAL_REPRODUCIBILITY_GUIDE.md`, `Admin/ONE_COMMAND_AUDIT_REPORT.md`, `metrics/code_audit_verification.json`, `metrics/full_audit_results.json` and `metrics/browser_ui_test_results.json`.

## Design notes

- **D1 primary:** Malayalam-containing rows only. Task is Ham vs Spam; D1 has no phishing labels.
- **D2 secondary:** separate three-class experiment; never pooled or label-mapped to D1.
- **Grouping:** exact message + audit-normalised key + conservative fuzzy pass (D1 only). Groups never cross splits.
- **Split:** 70/15/15, seed 42, class-stratified at group level.
- **Model selection:** validation macro-F1 only. Test is evaluated once after selection.
- **Final fit:** train+validation; the test split is untouched during selection.
- **D1 caveat:** the random split is a within-batch estimate. 95.5% of training Spam and 91.2% of test Spam come from block 6001–7000. Pooled leave-one-block-out macro-F1 is 0.538 (SVM) / 0.545 (LR), with Spam recall 7.6% / 8.9%. MuRIL does not improve this: 0.9619 random-split macro-F1 but 0.5028 pooled block macro-F1 and 3.56% Spam recall. See `reports/BASELINE_VALIDATION_AND_ROBUSTNESS_REPORT.md` and `reports/MODEL_COMPARISON.md`.
