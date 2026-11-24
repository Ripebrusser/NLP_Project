# Final Technical Verification

**Date:** 8 November 2026  
**Scope:** frozen artifacts only. No model was trained, tuned, relabelled or overwritten.

## 1. Commands and outcomes

```bash
cd "Research Work/phase2"
PYTHONIOENCODING=utf-8 ../../.venv/Scripts/python.exe p2_final_verification.py
# exit 0

PYTHONIOENCODING=utf-8 ../../.venv/Scripts/python.exe p2_final_audit_stats.py
# exit 0

cd ../..
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/prototype/verify_prototype.py"
# exit 0, status PASS
```

The new audit script had one first-run failure: its D2 bootstrap branch assumed the D1 MuRIL seed columns existed. That was a verifier-code guard error, not an experimental failure. The guard was corrected and the full script rerun successfully. The first failure and final success are recorded rather than hidden.

## 2. Prediction alignment

| Artifact | Expected | Verified |
|---|---:|---:|
| D1 LR predictions | 299 unique IDs | 299, exact ID set, labels match manifest |
| D1 SVM predictions | 299 unique IDs | 299, exact ID set, labels match manifest |
| D1 MuRIL seed 42 | 299 unique IDs | 299, exact ID set, labels match manifest |
| D1 MuRIL seed 43 | 299 unique IDs | 299, exact ID set, labels match manifest |
| D1 MuRIL seed 44 | 299 unique IDs | 299, exact ID set, labels match manifest |
| D2 LR predictions | 883 unique IDs | 883, exact ID set, labels match manifest |
| D2 SVM predictions | 883 unique IDs | 883, exact ID set, labels match manifest |

All predictions were aligned by `record_id`, not by row position.

## 3. Metric reproduction

The original verifier reproduced 14/14 saved classical metrics to ≤1.1×10⁻¹⁶. The independent audit script reproduced:

- D1 LR Macro-F1 0.9556445631211987.
- D1 SVM Macro-F1 0.9650046816479401.
- MuRIL seeds 0.9650046816479401 / 0.9556445631211987 / 0.9650046816479401.
- D2 LR Macro-F1 0.8877423096432983.
- D2 SVM Macro-F1 0.8825029808024670.
- Pooled block LR 0.5447952856859739; SVM 0.5378449758089207; MuRIL mean 0.5028.

## 4. Split and duplicate integrity

- D1 test: **299 rows / 299 groups / maximum group size 1**.
- D2 test: **883 rows / 883 groups / maximum group size 1**.
- D1 test composition: 265 Ham / 34 Spam.
- D1 blocks: 4001–5000 = 630 (618/12); 5001–6000 = 991 (991/0); 6001–7000 = 371 (158/213).
- D1 test blocks: 86/3, 159/0, 20/31.
- D2 experimental: 5,895 rows / 5,663 groups; 37 conflicting groups / 76 records excluded from 5,971 original.
- Six split file hashes match `model_manifest.json` and the prototype verifier.
- No duplicate group and no normalised key crosses a split boundary.

## 5. Exact intervals

| Quantity | Calculation | 95% interval |
|---|---|---|
| SVM Spam precision | 30/30 | Clopper–Pearson [0.8842967, 1.0]; Wilson [0.8865, 1.0] |
| LR Spam precision | 29/29 | Clopper–Pearson [0.8805551, 1.0]; Wilson [0.8830, 1.0] |
| Zero FP among Ham | 0/265 | Exact upper FPR 0.01382386; Wilson upper 0.01429 |
| SVM Spam recall | 30/34 | Clopper–Pearson [0.7255, 0.9670] |
| LR Spam recall | 29/34 | Clopper–Pearson [0.6894, 0.9505] |

The exact precision interval is conditional on the number of predicted positives. It is not a prevalence-adjusted deployment interval.

## 6. Bootstrap

- 2,000 percentile replicates; seed 42.
- Sampling unit: duplicate group.
- Every frozen test group is a singleton, so the procedure is numerically a message-level bootstrap.
- One shared sequence of resamples is used for all models and for paired differences.
- No D1 or D2 replicate lost the Spam class.
- Percentile limits are 2.5% and 97.5%.
- `zero_division=0` is used consistently; fixed label order is used for Macro-F1.

Key outputs:

| Quantity | Value |
|---|---|
| LR − SVM Macro-F1 | −0.0093601 [−0.0321432, 0.0000] |
| SVM − LR Macro-F1 | +0.0093601 [0.0000, 0.0321432] |
| SVM − LR Spam recall | +0.0294118 [0.0000, 0.0975610] |
| SVM − LR accuracy | +0.0033445 [0.0000, 0.0100334] |
| SVM − mean(MuRIL) Macro-F1 | +0.0031200 [0.0000, 0.0101002] |
| SVM − mean(MuRIL) Spam recall | +0.0098039 [0.0000, 0.0303030] |
| MuRIL mean Macro-F1, conditional | 0.9619 [0.9211, 0.9909] |
| MuRIL mean accuracy, conditional | 0.9855 [0.9710, 0.9967] |

## 7. Prototype parity

`verify_prototype.py` returned PASS:

- D1 SVM model SHA-256 matches manifest; 299/299 prediction parity; 299/299 cleaning parity; classes Ham and Spam observed.
- D2 LR model SHA-256 matches manifest; 883/883 prediction parity; 883/883 cleaning parity; classes ham/spam/smishing observed.
- All six split hashes match.
- Malayalam and Latin script detection work; Malayalam is preserved after cleaning; empty input is rejected.

This is **prediction parity**, not evidence of field validity.

## 8. Source hashes

| Artifact | SHA-256 |
|---|---|
| D1 workbook | `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b` |
| D2 CSV | `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e` |
| D1 test | `3922f037a2f52045ffc1d682e799880a06311dec9017ff33abef3fdd3d40be0b` |
| D2 test | `44409491ebb1c4e22d3aa65b76ca6f4e18ad2eb6af1f58380ab7f19236b46c79` |

## 9. Machine outputs

- `Research Work/phase2/metrics/final_verification.json`
- `Research Work/phase2/metrics/final_audit_stats.json`
- `Research Work/phase2/metrics/paired_model_comparison.json`
- `Research Work/phase2/metrics/muril_seed_variation.json`
- `Research Work/phase2/metrics/block_paired_comparison.csv`

## 10. Unresolved technical limitations

1. Bootstrap does not model source or row-block uncertainty because source labels do not exist.
2. Three MuRIL seeds cannot estimate training-run variance in a population sense.
3. The structural diagnostic was not refitted; its arithmetic was checked from the saved confusion matrix. Refitting would be a new experiment.
4. `d1_block_robustness.json` retains historical 631/370 and 0.3677 values. It is not authoritative.
5. No external Malayalam test data exists, so no external-validity check can pass or fail.
