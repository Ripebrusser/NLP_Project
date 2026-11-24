# Verification Report

**Date:** 6 November 2026  
**Scope:** frozen predictions, split integrity, metric reproduction, uncertainty calculations, script counts and row-block counts. No model was trained or modified.

## 1. Commands executed

```bash
cd "Research Work/phase2"
PYTHONIOENCODING=utf-8 ../../.venv/Scripts/python.exe p2_final_verification.py
# exit 0

PYTHONIOENCODING=utf-8 ../../.venv/Scripts/python.exe p2_final_audit_stats.py
# exit 0

cd ../..
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe \
  "Research Work/prototype/verify_prototype.py"
# exit 0, status PASS
```

All three commands were rerun on 8 November 2026. The prototype verifier checks model hashes, 299/299 and 883/883 prediction parity, split hashes, Unicode handling and class coverage. The independent audit script resolves the paired-comparison direction and writes `metrics/final_audit_stats.json`. Full details are in `FINAL_TECHNICAL_VERIFICATION.md`.

## 2. Independent metric reproduction

`p2_final_verification.py` reads the frozen prediction CSVs directly, aligns every model to the frozen test manifest by `record_id`, and recomputes confusion matrices and metrics with fixed label order. It does not read the saved metric JSON as input.

Checks passed:

- D1: five prediction files (`LR`, `SVM`, `MuRIL 42`, `43`, `44`) each contain exactly **299 unique record IDs**; all sets equal the frozen `d1_malayalam_test.csv`; every prediction row’s label equals the manifest label.
- D2: both prediction files contain exactly **883 unique record IDs**; both sets equal the frozen `d2_test.csv`; labels match.
- 14/14 saved classical D1/D2 metrics (accuracy, Macro-F1, Spam precision, recall, F1; D2 accuracy/Macro-F1) matched the saved result JSON to ≤1.1×10⁻¹⁶.
- D1 test duplicate groups: **299 groups / 299 rows / maximum group size 1**. D2: **883 / 883 / 1**. The group bootstrap is therefore numerically a message bootstrap, but the grouped implementation remains valid.
- No bootstrap replicate lost the Spam class: D1 0/2,000; D2 0/2,000.
- D1 test composition: 265 Ham / 34 Spam; blocks 4001–5000 = 86/3, 5001–6000 = 159/0, 6001–7000 = 20/31.
- D1 predicted Spam: SVM 30 (1 in block 4001, 29 in block 6001), LR 29 (all in block 6001), MuRIL 42/44 30 (1+29), MuRIL 43 29 (1+28). All predicted-Spam duplicate groups are distinct.

Machine output: `Research Work/phase2/metrics/final_verification.json`.

## 3. Corrected uncertainty calculations

The verifier computes:

- Exact Clopper–Pearson and Wilson intervals for Spam precision (conditional on predicted positives), Spam recall, and the zero-false-positive rate among Ham.
- Per-seed MuRIL percentile group-bootstrap intervals.
- One shared 2,000-draw group-bootstrap sequence for all D1 models; the **same** resample is used for paired differences.
- A three-seed mean interval, conditional on the three frozen seeds, by averaging the three seed metrics on each shared draw. This is **not** an interval for a new training run.
- Paired SVM − mean(MuRIL seeds) differences on the same draws.
- D1 block-fold and pooled metrics from frozen block predictions.

Key values:

| Quantity | Result |
|---|---|
| SVM Spam precision, exact 95% | 30/30 = 1.000 [0.8843, 1.0000] |
| LR Spam precision, exact 95% | 29/29 = 1.000 [0.8806, 1.0000] |
| Zero FP among Ham, exact 95% upper | 0/265 → 1.382% |
| MuRIL three-seed mean Macro-F1, conditional 95% | 0.9619 [0.9211, 0.9909] |
| MuRIL three-seed mean accuracy, conditional 95% | 0.9855 [0.9710, 0.9967] |
| SVM − MuRIL mean Macro-F1 | +0.0031 [0.0000, 0.0101] |
| SVM − MuRIL mean Spam recall | +0.0098 [0.0000, 0.0303] |

The interval includes zero; no statistical separation is demonstrated.

## 4. Split and duplicate checks

- D1 groups: 1,824 final groups / 168 duplicate excess; 0 conflicting-label groups in the Malayalam subset.
- D2: 5,700 groups before conflict exclusion; 37 conflicting groups / 76 records excluded, leaving **5,663 experimental groups / 232 duplicate excess**; experimental rows n = 5,895.
- D1 train/validation/test group counts: 1,226 / 299 / 299; test max group size 1; train max 4.
- D2 train/validation/test: 3,895 / 885 / 883; test max group size 1; train max 8.
- `split_manifest.json` records zero group-ID and zero normalised-key overlap; the six file hashes match `model_manifest.json` and the prototype verifier.
- Hashes are recorded in `model_manifest.json`, `split_manifest.json` and `verification_results.json`.

## 5. Script-count reconciliation

**Resolved.** The original audit output `Research Work/audit_output/dataset_audit.json` reports `malayalam_only: 1489`. `subset_audit.json` and `d1_malayalam.csv` also report 1,489 Malayalam-only and 503 Malayalam+Latin. The 1,486 entry in `Admin/DATASET_AUDIT_REPORT.md` §C is a **stale table typo**, not a different filter: the same report’s class-by-language table and the machine output give 1,489. There is no change in filtering logic. 1,489 + 503 = 1,992; no Malayalam record contains Tamil, Telugu or Kannada.

## 6. Row-block reconciliation

Correct block definition is `(source_row - 1) // 1000 + 1`, using the Excel row number:

| Block | Records | Ham | Spam |
|---|---:|---:|---:|
| 4001–5000 | 630 | 618 | 12 |
| 5001–6000 | 991 | 991 | 0 |
| 6001–7000 | 371 | 158 | 213 |

The old 631/370 and 631/619/12 tables come from the off-by-one `p2_robustness.py` formula or positional slicing in `subset_audit.row_blocks`, not from `source_row`. They are superseded. The corrected SVM block-6001 fold is **0.368470**, not **0.3677**.

## 7. Checks that could not be performed

- No Git history exists, so the exact diff of the previously changed nine prototype files cannot be verified.
- D1 access provenance cannot be verified from the workspace (no subscription receipt, download log or author permission).
- FSSHAP full text is paywalled; no numeric result was verified.
- No external source-diverse Malayalam test set exists; no generalisation test is possible with current data.
- The original cause of the Streamlit process termination is inferred from logs, not a process-supervisor trace.

## 8. Failures found and fixed during verification

The first run of `p2_final_verification.py` had two implementation errors in the **verifier itself**: an exact-interval helper assumed zero false positives for every dataset (invalid for D2 multiclass), and a local variable was referenced before assignment. Both were corrected; no dataset, split, model or saved metric was affected. The final run completed successfully and wrote the JSON above.

## 9. Verdict

**PASS for traceability and arithmetic.** Every current D1/D2 headline metric is reproducible from frozen predictions. **FAIL for external validity and D1 provenance.** The statistical record is now internally consistent; the remaining blockers are data access, source diversity and claim scope, not arithmetic.
