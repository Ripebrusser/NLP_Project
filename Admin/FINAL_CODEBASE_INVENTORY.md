# Final Codebase Inventory

**Project:** Classical and Multilingual Transformer Models for SMS Spam and Smishing Detection in Malayalam-Script and English Text
**Audit date:** 8 November 2026
**Scope:** every Python source file, configuration, manifest and dependency file that participates in the frozen experiments, the statistical verification, the prototype and the literature workbook.

All paths are relative to the project root. Nothing in this inventory was inferred from a report: each file was opened and its inputs/outputs traced from the code.

## 1. Counts

| Item | Count |
|---|---:|
| Python source files under `Research Work/` (excluding `__pycache__`) | 40 |
| Files under `Research Work/` excluding caches and logs | 155 |
| Files in `Research Work/phase2/metrics/` | 49 (before the audit added 4) |
| Admin reports before this audit | 30 |
| Datasets | 2 (D1 workbook, D2 CSV) |
| Frozen split files | 6 + 1 descriptive |
| Saved joblib pipelines | 4 |
| Saved MuRIL reference models | 1 directory (seed 42) |

The 40 Python files audited were: 18 in `phase2/`, 5 in `prototype/`, 6 top-level pipeline/audit scripts, 1 literature validator added by this audit, and 10 test-suite files. The engineering-closure pass added two more (`run_full_audit.py` and `tests/test_streamlit_app.py`), for 42 total.

## 2. Pipeline source files

| File | Purpose | Inputs | Outputs | Dependencies | Status |
|---|---|---|---|---|---|
| `Research Work/audit_datasets.py` | Stdlib dataset audit; defines `norm_key`, `script_bucket`, `manglish_screen` | D1 xlsx, D2 csv | `audit_output/dataset_audit.json` | stdlib only | Active; `norm_key` is the frozen grouping key |
| `Research Work/audit_forensics.py` | Label conflicts, template clusters, cross-dataset label agreement | D1 xlsx, D2 csv | `audit_output/*` | `audit_datasets` | Historical audit; read-only |
| `Research Work/audit_scripts.py` | Script census over all Indic blocks | D1 xlsx, D2 csv | `audit_output/*` | `audit_datasets` | Historical audit; read-only |
| `Research Work/split_plan_simulation.py` | Pre-experiment split feasibility simulation | datasets | `audit_output/*` | `audit_datasets` | Superseded by `p2_split.py`; safe to keep, do not rerun |
| `Research Work/build_lit_matrix.py` | Legacy 18-column literature CSV builder | hard-coded rows | `Literature Review/LITERATURE_COMPARISON_MATRIX.csv` | stdlib | Superseded by `build_final_lit_matrix.py`; outputs a different schema |
| `Research Work/build_final_lit_matrix.py` | Authoritative 24-record workbook + CSV builder | hard-coded verified rows | `Admin/FINAL_LITERATURE_COMPARISON_MATRIX.xlsx`, `Literature Review/FINAL_LITERATURE_COMPARISON_MATRIX.csv` | pandas, openpyxl | Active; validated by `validate_literature_matrix.py` |
| `Research Work/validate_literature_matrix.py` | **Added by this audit.** Checks workbook/CSV against the verification register | register, workbook, CSV, builder rows | exit status + JSON | pandas, openpyxl | Active |
| `Research Work/phase2/p2_common.py` | Shared loading, Unicode cleaning, script flags, grouping, split, metrics, `block_number`, `align_predictions` | datasets, splits | shared helpers | pandas, numpy, scikit-learn, `audit_datasets` | Active; central dependency |
| `Research Work/phase2/p2_extract.py` | Builds the 1,992-row D1 Malayalam subset and D2 view | D1 xlsx (7,717 rows), D2 csv (5,971) | `data/d1_all_records.csv`, `data/d1_malayalam.csv`, `data/d2_all_records.csv`, `metrics/subset_audit.json` | `p2_common` | Active; must precede `p2_duplicates` |
| `Research Work/phase2/p2_duplicates.py` | Exact + normalised + fuzzy duplicate groups, conflict flagging | `data/*.csv` | `data/d1_malayalam_grouped.csv`, `data/d2_grouped.csv`, `metrics/duplicates.json` | `p2_common`, sklearn TF-IDF/kNN | Active; D1 fuzzy pass reproduced exactly by tests |
| `Research Work/phase2/p2_split.py` | 70/15/15 grouped-stratified splits + manifest | grouped CSVs | `splits/*.csv`, `split_manifest.json` | `p2_common` | Active; **do not rerun** (rewrites frozen splits and manifest) |
| `Research Work/phase2/p2_modeling.py` | TF-IDF + LR/SVM pipelines, validation grid, final refit, metrics | splits | models, results, predictions | sklearn, joblib | Active; TF-IDF fitted inside the pipeline |
| `Research Work/phase2/p2_train_d1.py` | Trains/selects the D1 LR and SVM | D1 splits | `models/d1_*.joblib`, `metrics/d1_malayalam_results.json` | `p2_modeling` | Frozen output; do not retrain |
| `Research Work/phase2/p2_train_d2.py` | Trains/selects the D2 LR and SVM | D2 splits | `models/d2_*.joblib`, `metrics/d2_results.json` | `p2_modeling` | Frozen output; do not retrain |
| `Research Work/phase2/p2_validate.py` | Phase 2.1 block CV, baselines, diagnostics | splits, models | `metrics/validation_summary.json`, `metrics/block_cv_predictions.csv`, `metrics/baseline_comparison.csv` | sklearn, scipy | Active; **block CV source of truth** |
| `Research Work/phase2/p2_robustness.py` | Historical leave-one-block-out diagnostic | splits | `metrics/d1_block_robustness.json` | `p2_modeling` | Diagnostic; output is stale (old block formula); **do not rerun** |
| `Research Work/phase2/p2_muril.py` | MuRIL fine-tuning, seeds 42/43/44 | splits, `google/muril-base-cased` | `models/muril_d1_seed42/`, `metrics/muril_*` | torch, transformers | Frozen; GPU; do not rerun |
| `Research Work/phase2/p2_muril_report.py` | MuRIL verification, errors, tables | saved MuRIL artifacts | reports/metrics | torch, transformers | Read-only |
| `Research Work/phase2/p2_ci.py` | Legacy group bootstrap CIs (4 models) | frozen predictions | `metrics/confidence_intervals.json/.csv`, `reports/CONFIDENCE_INTERVAL_REPORT.md` | sklearn, numpy | **Legacy duplicate** of `p2_stats.py`; writes the same JSON path |
| `Research Work/phase2/p2_stats.py` | Complete CIs, seed variation, paired bootstrap, block pairs | frozen predictions | `confidence_intervals.json/.csv`, `muril_seed_variation.json/.csv`, `paired_model_comparison.json/.csv`, `block_paired_comparison.csv`, `reports/statistical_tables.md` | sklearn, numpy | Active; canonical CI/paired output |
| `Research Work/phase2/p2_threshold.py` | Validation-only threshold calibration and score diagnosis | splits, models | `metrics/threshold_calibration*`, figures, report | torch, transformers, matplotlib | Active; descriptive |
| `Research Work/phase2/p2_report.py` | Generates Phase 2 reports from saved metrics | metrics JSON | `reports/*.md` | pandas | Read-only |
| `Research Work/phase2/p2_final_verification.py` | Independent recomputation from frozen predictions; exact/Wilson intervals; block audit | splits, predictions | `metrics/final_verification.json` | scipy, sklearn | Active; regenerated in this audit |
| `Research Work/phase2/p2_final_audit_stats.py` | Second independent calculation; paired direction; block/script composition | splits, predictions | `metrics/final_audit_stats.json` | scipy, sklearn | Active; regenerated in this audit |

## 3. Prototype files

| File | Purpose | Inputs | Outputs | Dependencies | Status |
|---|---|---|---|---|---|
| `Research Work/prototype/app.py` | Streamlit UI: D1 mode, D2 mode, read-only dashboard | models, metrics JSON/CSV | rendered page | streamlit, pandas | Active |
| `Research Work/prototype/inference.py` | Frozen artifact loading, exact cleaning, guards, prediction | 2 joblib pipelines | result dicts | joblib, numpy | Active; guards added by this audit |
| `Research Work/prototype/research_data.py` | Read-only loaders for saved metrics | metrics JSON/CSV | DataFrames/dicts | pandas | Active |
| `Research Work/prototype/verify_prototype.py` | Hashes, alignment, inference parity, class coverage, guards | manifests, splits, predictions, models | `verification_results.json`, exit status | pandas | Active; strengthened by this audit |
| `Research Work/prototype/model_manifest.json` | Baseline SHA-256 for 4 models + 6 splits | — | — | — | Frozen reference |
| `Research Work/prototype/requirements.txt` | Prototype runtime pins | — | — | — | Active (5 packages) |
| `Research Work/prototype/verification_results.json` | Latest verifier output | — | — | — | Regenerated; previous copy kept as `verification_results.before_code_audit.json` |

## 4. Test suite (added by this audit)

| File | Covers |
|---|---|
| `tests/support.py` | Paths, cached read-only fixtures, manifests |
| `tests/test_statistics.py` | CP/Wilson values, metric denominators, zero-division, macro-F1 vs sklearn, pair direction/symmetry, bootstrap reproducibility, real-data LR−SVM regression |
| `tests/test_alignment.py` | Missing/extra/duplicate/null IDs, label and group disagreement, class validation, D1/D2 mix-up, frozen-file alignment |
| `tests/test_blocks.py` | Block boundaries, stale-formula regression, 630/991/371 composition, test-split blocks, manifest staleness |
| `tests/test_unicode.py` | Malayalam preservation, ZWSP/BOM/NBSP/control handling, NFKC, idempotence, cleaning parity on 7,887 rows, script detection, input guards |
| `tests/test_duplicates.py` | `norm_key` behaviour, union-find, conflict flagging, split grouping, leakage, frozen 1,824/5,663 group reproduction |
| `tests/test_splits.py` | Sizes, source hashes, split hashes, disjoint IDs, label totals, group/norm overlap, singleton test groups |
| `tests/test_models.py` | All four model hashes, pipeline structure, vectorizer config, classes, batch parity |
| `tests/test_inference.py` | 299/883 classify parity, payload shape, score normalisation, guards |
| `tests/test_literature.py` | Register parse, workbook agreement, counts, corruption detection |
| `tests/run_tests.py` | Discovery + `metrics/code_audit_test_results.json` |

## 5. Configuration, manifests and dependency files

| File | Role | Notes |
|---|---|---|
| `Research Work/phase2/splits/split_manifest.json` | Frozen split manifest: seed 42, sizes, class counts, group counts, six SHA-256 | Its `d1.blocks` table is **stale** (631/991/370 vs 630/991/371); preserved unmodified, see fix register F-02 |
| `Research Work/phase2/splits/split_manifest.before_validation.json` | Pre-validation copy | Historical; not used by code |
| `Research Work/prototype/model_manifest.json` | Model + split baseline hashes | Verified: 4/4 models, 6/6 splits |
| `Research Work/prototype/requirements.txt` | streamlit 1.67.0, scikit-learn 1.9.1, joblib 1.6.0, pandas 3.1.1, numpy 2.5.4 | Matches installed environment |
| `.streamlit/config.toml` | Streamlit runtime config | No credentials |
| `Research Work/requirements-verification.txt` | **Added:** audit/verification pins | Separate from prototype and MuRIL dependencies |
| `Admin/LITERATURE_VERIFICATION_REGISTER.md` | Authoritative 24-record access register | Summary count corrected 9 → 10 (F-07) |
| `Research Work/prototype/MODEL_AND_DATASET_NOTES.md` | Model/dataset caveats | Consistent with results |

## 6. Dead code, duplication and orphaned artifacts

1. **`p2_ci.py` vs `p2_stats.py`** — both write `metrics/confidence_intervals.json`. `p2_stats.py` is the superset (adds paired comparisons and seed variation). Running both in the documented order silently replaces the richer file with the simpler one. Documented in the reproducibility guide; not deleted (it is historical evidence).
2. **`build_lit_matrix.py` vs `build_final_lit_matrix.py`** — the legacy builder writes a different 18-column schema to a different path. It is not used by the final workbook; `validate_literature_matrix.py` validates only the final pair of files.
3. **`split_plan_simulation.py`** — pre-experiment feasibility script; its outputs are not consumed by Phase 2.
4. **`d1_block_robustness.json`** — produced with the old block formula; superseded by `validation_summary.json`. Kept as historical evidence and flagged stale.
5. **`load_d1()` returns 7,717 rows** (the whole Dravidian workbook), not the 1,992-row Malayalam subset. This is correct and documented in its docstring, but it is an easy place to misread the experiment size; `p2_extract.py` performs the 1,992-row filter.
6. **No root README** — the project has no top-level README; the two operative READMEs are `Research Work/phase2/README.md` and `Research Work/prototype/README.md`. Both were updated by this audit.
