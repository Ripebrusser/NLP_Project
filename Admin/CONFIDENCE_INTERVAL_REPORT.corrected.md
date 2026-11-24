# Confidence Interval Report — Corrected

**Correction date:** 6 November 2026. **Supersedes** `Research Work/phase2/reports/CONFIDENCE_INTERVAL_REPORT.md` for the statements corrected below. The original is preserved unchanged.

**What changed:** (1) the zero-false-positive bound is computed over **265 Ham**, not 299 test rows; (2) exact Clopper–Pearson/Wilson precision intervals replace “degenerate at 1.000”; (3) a conditional three-seed mean interval is added; (4) “block-held-out” is renamed “leave-one-row-block-out stress test.” All other point estimates and per-seed bootstrap intervals are unchanged and were independently reproduced.

## 1. Method

- Percentile group bootstrap, 2,000 replicates, seed 42; duplicate group is the sampling unit.
- D1: 299 rows / 299 groups; D2: 883 / 883. Every frozen test group is a singleton, so the bootstrap is numerically message-level; the grouped implementation is retained.
- Fixed label order. If a class is absent in a replicate, its F1 is 0; no replicate lost the Spam class (D1 0/2,000; D2 0/2,000).
- Paired comparisons use the **same** resample for both models.
- Exact intervals are Clopper–Pearson; Wilson is reported as a sensitivity. They are descriptive binomial intervals, not source-population intervals.

## 2. D1 random grouped test — corrected uncertainty

Test 299 = 265 Ham / 34 Spam. CM rows=true, cols=pred.

| Model | TP | FP | FN | TN | Spam precision (exact 95%) | Spam recall (exact 95%) | FPR among Ham (exact 95%) |
|---|---:|---:|---:|---:|---|---|---|
| Logistic Regression | 29 | 0 | 5 | 265 | 1.000 [0.8806, 1.0000] | 0.8529 [0.6894, 0.9505] | 0/265 [0, 0.01382] |
| Linear SVM | 30 | 0 | 4 | 265 | 1.000 [0.8843, 1.0000] | 0.8824 [0.7255, 0.9670] | 0/265 [0, 0.01382] |
| MuRIL 42/44 | 30 | 0 | 4 | 265 | 1.000 [0.8843, 1.0000] | 0.8824 [0.7255, 0.9670] | 0/265 [0, 0.01382] |
| MuRIL 43 | 29 | 0 | 5 | 265 | 1.000 [0.8806, 1.0000] | 0.8529 [0.6894, 0.9505] | 0/265 [0, 0.01382] |

Wilson precision: SVM **0.8865–1.0000**; LR **0.8830–1.0000**. Wilson FPR upper: **0.01429**.

**Why this matters:** precision is conditional on the number of predicted positives (29 or 30). It is not an estimate for a new source. The exact lower bound says the data are compatible with true precision as low as ~88%; the FPR bound says a true Ham false-positive rate up to ~1.4% is compatible with observing zero in 265 Ham. “100% precision” is an observed count, not a guarantee.

**Duplicate groups:** every predicted-Spam row is in a distinct group (30 or 29 groups). There is no within-test duplicate dependence among positives. There is, however, campaign/block dependence: 29/30 SVM positives are in block 6001–7000.

## 3. D1 random grouped test — bootstrap intervals unchanged

| Model | Accuracy | Macro-F1 | Spam recall | Spam F1 |
|---|---|---|---|---|
| LR | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9121, 0.9903] | 0.8529 [0.7222, 0.9655] | 0.9206 [0.8387, 0.9825] |
| SVM | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.8824 [0.7600, 0.9730] | 0.9375 [0.8636, 0.9863] |
| MuRIL 42 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.8824 [0.7600, 0.9730] | 0.9375 [0.8636, 0.9863] |
| MuRIL 43 | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9099, 0.9903] | 0.8529 [0.7188, 0.9655] | 0.9206 [0.8364, 0.9825] |
| MuRIL 44 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.8824 [0.7600, 0.9730] | 0.9375 [0.8636, 0.9863] |

The percentile intervals are descriptive within-source intervals. They are not confidence intervals for a new collection source.

## 4. MuRIL across seeds — corrected reporting

| Metric | Seed 42 | Seed 43 | Seed 44 | Mean | SD | Conditional 95% interval for the three-seed mean |
|---|---:|---:|---:|---:|---:|---|
| Accuracy | 0.9866 | 0.9833 | 0.9866 | 0.9855 | 0.0019 | **[0.9710, 0.9967]** |
| Macro-F1 | 0.9650 | 0.9556 | 0.9650 | 0.9619 | 0.0054 | **[0.9211, 0.9909]** |
| Spam recall | 0.8824 | 0.8529 | 0.8824 | 0.8725 | 0.0170 | **[0.7500, 0.9678]** |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | [1.0000, 1.0000] |

The mean interval is obtained by averaging the three seed metrics on each shared bootstrap draw. It describes test-sample uncertainty for **these three frozen seeds**. It is **not** a 95% interval for a new fine-tuning run, and the three seeds are not three independent test sets. The across-seed SD is training-run variation; it is reported separately and is not added to the bootstrap interval.

## 5. Paired model comparison

Shared 2,000-draw group bootstrap; difference = SVM − mean(MuRIL 42/43/44):

| Metric | Difference | 95% interval | Interpretation |
|---|---:|---|---|
| Macro-F1 | +0.0031 | [0.0000, 0.0101] | includes 0; not distinguishable |
| Accuracy | +0.0011 | [0.0000, 0.0033] | includes 0; not distinguishable |
| Spam recall | +0.0098 | [0.0000, 0.0303] | includes 0; not distinguishable |

Seed-level: SVM is identical to MuRIL 42 and 44; seed 43 differs by one Spam message. MuRIL is not shown to be better, and SVM is not shown to be meaningfully better.

## 6. D2 intervals (unchanged point estimates)

| Model | Accuracy | Macro-F1 | Spam precision | Spam recall |
|---|---|---|---|---|
| LR | 0.9638 [0.9513, 0.9762] | 0.8877 [0.8482, 0.9239] | 0.7857 [0.6885, 0.8784] | 0.8209 [0.7222, 0.9130] |
| SVM | 0.9638 [0.9513, 0.9762] | 0.8825 [0.8408, 0.9196] | 0.7761 [0.6735, 0.8710] | 0.7761 [0.6721, 0.8750] |

D2 test 883 = 726 Ham / 67 Spam / 90 Smishing. These are bootstrap intervals for the fixed experimental corpus; D2 has no source metadata. The LR−SVM Macro-F1 difference is 0.0052 [−0.0121, 0.0244], which includes zero; LR is the better point estimate, not a proven superior model.

## 7. Leave-one-row-block-out — descriptive only

Blocks 4001–5000 = 630 (618/12), 5001–6000 = 991 (991/0), 6001–7000 = 371 (158/213). Pooled metrics: LR 0.5448, SVM 0.5378, MuRIL mean 0.5028. There are three blocks, one with no Spam. No population-level confidence interval is defined. The 5001 fold’s Macro-F1 is an absent-class artefact; the 6001 fold is the decisive stress case.

## 8. Interpretation

- D1 intervals describe uncertainty within the existing corpus; the small test set and the block concentration are why the intervals are wide.
- The exact precision/FPR bounds are more honest than “100%”.
- MuRIL seed variation is smaller than test-sample uncertainty, but three seeds cannot estimate a training-run population.
- No interval supports a claim of SVM or MuRIL superiority, or of field performance.

*Values recomputed from frozen predictions; see `Admin/VERIFICATION_REPORT.md` and `metrics/final_verification.json`.*
