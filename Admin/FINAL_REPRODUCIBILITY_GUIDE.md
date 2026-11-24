# Final Reproducibility Guide

**Audit date:** 8 November 2026
**Purpose:** rebuild the verification environment, re-run every check and reproduce the prototype and literature workbook **without retraining any model and without regenerating any split**.

## 1. Environment

| Item | Value |
|---|---|
| OS | Windows 11 (10.0.26300) |
| Python | 3.14.3, project-local `.venv` |
| Verification stack | numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, scipy 1.18.1, joblib 1.6.0, openpyxl 3.1.5 |
| Prototype stack | streamlit 1.67.0 + the verification stack |
| MuRIL stack (not needed for verification) | torch 2.11.0+cu128, transformers 5.22.1, accelerate 1.15.0 |
| Test framework | `unittest` (pytest is not installed) |

The saved joblib pipelines require the same scikit-learn major version; use the pins above.

## 2. Install

```bash
py -m venv .venv
.venv/Scripts/python.exe -m pip install -r "Research Work/requirements-verification.txt"
.venv/Scripts/python.exe -m pip install -r "Research Work/prototype/requirements.txt"
```

MuRIL is only needed to retrain, which this audit does not do:

```bash
.venv/Scripts/python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
.venv/Scripts/python.exe -m pip install "transformers==5.22.1" "accelerate==1.15.0"
```

All commands below run from the project root. `PYTHONIOENCODING=utf-8` is set because the console is `cp1252` and the scripts print Malayalam.

## 3. Order of operations

```
p2_extract.py  ->  p2_duplicates.py  ->  p2_split.py  ->  p2_train_d1.py / p2_train_d2.py
                                                       ->  p2_validate.py  ->  p2_robustness.py
                                                       ->  p2_muril.py    ->  p2_muril_report.py
                                                       ->  p2_ci.py / p2_stats.py / p2_threshold.py
                                                       ->  p2_report.py
                                                       ->  p2_final_verification.py / p2_final_audit_stats.py
```

For **verification only**, start at step 4; steps 1–3 would rewrite frozen data, splits and models.

## 4. Do not run these

| Script | Why |
|---|---|
| `p2_split.py` | Rewrites the six frozen split files and `split_manifest.json` |
| `p2_train_d1.py`, `p2_train_d2.py` | Retrain and overwrite the four frozen `.joblib` pipelines |
| `p2_muril.py` | Retrains MuRIL (GPU); would overwrite the saved reference model |
| `p2_robustness.py` | Retrains diagnostic models and overwrites `d1_block_robustness.json` |
| `p2_ci.py` | Legacy; overwrites the richer `confidence_intervals.json` produced by `p2_stats.py` |

`p2_final_verification.py` and `p2_final_audit_stats.py` are safe: they read frozen predictions only, but they do rewrite their own JSON outputs. Preserve the previous copy first if you need it (the audit keeps `*.before_code_audit.json`).

## 5. Verification commands

### One command

```bash
.venv/Scripts/python.exe "Research Work/run_full_audit.py"
```

Runs the environment check, dataset/split/model/baseline hashes, the regression suite, both statistical verifications, the prototype verifier, the literature validator, the static code-risk invariants and a pre/post artifact comparison. Writes `Research Work/phase2/metrics/full_audit_results.json` and a preserved copy under `phase2/metrics/audit_runs/<run_id>/`. Exit status is 0 only if every required check passes. Expected final result: **15/15 PASS (14 required + browser evidence), 125 tests, ~34 s**.

Run it once with `--write-baseline` before any change window to record the 39 frozen-artifact hashes; afterwards every run compares against that baseline.

### Individual checks

```bash
# Frozen split, model and inference parity (exit 0 = PASS)
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/prototype/verify_prototype.py"

# Literature workbook against the verification register (exit 0 = PASS)
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/validate_literature_matrix.py"

# Recompute headline metrics and intervals from frozen predictions
cd "Research Work/phase2"
PYTHONIOENCODING=utf-8 ../../.venv/Scripts/python.exe p2_final_verification.py
PYTHONIOENCODING=utf-8 ../../.venv/Scripts/python.exe p2_final_audit_stats.py
cd ../..

# Full test suite + machine-readable result
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/tests/run_tests.py"

# One machine-readable aggregate of all of the above
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/tests/write_audit_verification.py"
```

Expected: verifier `PASS` with 4/4 model hashes, 6/6 split hashes, 299/299 and 883/883 parity; literature `PASS` with 24 records (23 active); 125/125 tests; aggregate `PASS`.

## 6. Prototype

```bash
.venv/Scripts/python.exe -m streamlit run "Research Work/prototype/app.py" --server.address 127.0.0.1 --server.port 8501
```

Open `http://127.0.0.1:8501`. Inputs are limited to 5,000 characters; D1 mode requires Malayalam Unicode, D2 mode requires Latin characters. No network calls, no file uploads, no text written to disk.

## 7. Rebuilding the literature workbook

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/build_final_lit_matrix.py"
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/validate_literature_matrix.py"
```

The builder is deterministic: it writes `Admin/FINAL_LITERATURE_COMPARISON_MATRIX.xlsx` and `Literature Review/FINAL_LITERATURE_COMPARISON_MATRIX.csv` from the verified 24-row table. The validator checks the workbook against `Admin/LITERATURE_VERIFICATION_REGISTER.md`, against the builder's declared rows, and against the CSV, and rejects uncaveated numeric results on non-full-text records.

## 8. Expected artifact hashes

| Artifact | SHA-256 (prefix) |
|---|---|
| `Datasets/Spam Message Collection.xlsx` | `24ca099a…a023b` |
| `Datasets/Dataset_5971.csv` | `649844f1…a71e` |
| `d1_malayalam_train.csv` | `bd4f5edb…ddc1` |
| `d1_malayalam_val.csv` | `5bcc228f…7f1f` |
| `d1_malayalam_test.csv` | `3922f037…be0b` |
| `d2_train.csv` | `ad19a6e8…8499` |
| `d2_val.csv` | `2fc68c05…400f` |
| `d2_test.csv` | `44409491…6c79` |
| `d1_malayalam_linear_svm.joblib` | `9ba1dcd6…25cd` |
| `d1_malayalam_logreg.joblib` | `fd4a1542…6e69` |
| `d2_linear_svm.joblib` | `5de720cf…042e` |
| `d2_logreg.joblib` | `6f8cd0e5…c856` |

Full values are in `splits/split_manifest.json`, `prototype/model_manifest.json` and `metrics/code_audit_verification.json`.

## 9. Known reproducibility caveats

1. **Manifest block table is stale.** `split_manifest.json` records 631/991/370; the correct composition from the frozen splits is 630/991/371. The manifest was **not edited** (frozen artifact). Use `p2_common.block_number()` as the authority; the test suite pins both facts.
2. **`d1_block_robustness.json` is historical** and uses the old block membership. Use `validation_summary.json` for block results.
3. **`p2_ci.py` is legacy.** `p2_stats.py` is authoritative for confidence intervals and paired comparisons.
4. **MuRIL training configuration** is only partially recoverable from saved artifacts. Do not claim an exact reproduction of the MuRIL run; only its predictions and metrics are frozen and verified.
5. **`load_d1()` returns all 7,717 workbook rows**; the 1,992-row Malayalam experiment is produced by `p2_extract.py`. Do not treat `len(load_d1())` as the experiment size.
6. **Windows console encoding.** Without `PYTHONIOENCODING=utf-8`, Malayalam output can raise `UnicodeEncodeError`. This is a display issue, not a computation issue.

## 10. Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| `UnicodeEncodeError` on print | console `cp1252` | set `PYTHONIOENCODING=utf-8` |
| joblib `InconsistentVersionWarning` | different scikit-learn version | install the pinned version; do not refit |
| Prototype says model not found | `.joblib` moved | restore from the frozen artifact; verify with `verify_prototype.py` |
| Split hash mismatch | a split was regenerated | restore the original; do not "fix" the manifest |
| Literature validation fails on counts | register/workbook drift | inspect the reported IDs; do not silence the check |
