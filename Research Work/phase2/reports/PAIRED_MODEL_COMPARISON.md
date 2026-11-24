# Paired Model Comparison

> **HISTORICAL / SUPERSEDED.** Retained for experiment provenance. Do not cite for current numbers or claims. Current authority: `Admin/CANONICAL_FINAL_RESULTS.md` and `Admin/CANONICAL_FINAL_RESULTS.md`.


**Phase 2.3, Part B.** Same Malayalam test rows for every pair; paired group-level bootstrap. No model was retrained and no test label influenced selection.

## 1. Method

- **Paired percentile bootstrap** over duplicate groups (`group_id`), 2,000 replicates, seed 42.
- For each replicate, the **same group resample** is applied to both models' predictions on the matched test rows, so the interval is for the difference, not for two independent scores.
- Difference = **A − B**. Positive means model A has the higher metric.
- 95% interval = 2.5th/97.5th percentile of the paired difference distribution.
- All test groups contain one row, so the group bootstrap is numerically the message bootstrap; the grouped implementation is retained for correctness.
- No p-value is reported. A 95% interval that includes zero is **not** evidence of no difference, and one that excludes zero is **not** proof of practical importance.
- **Practical threshold, fixed before looking at the results:** a difference is treated as practically meaningful only if it reaches **0.01 Macro-F1 and 0.05 Spam recall**. On the 34-Spam random test, 0.05 recall is only 1.7 messages; on the 225-Spam pooled block set it is 11.3 messages. This asymmetry is stated wherever it matters.

## 2. D1 random-test pairs

Matched frozen test: 299 rows (265 Ham / 34 Spam), 299 groups.

| A − B | Δ Macro-F1 (95% CI) | Δ Spam recall (95% CI) | Replicate direction |
|---|---|---|---|
| Logistic Regression − Linear SVM | −0.0094 [−0.0321, 0.0000] | −0.0294 [−0.0976, 0.0000] | 63.1% negative, 36.9% tie |
| Logistic Regression − MuRIL 42 | −0.0094 [−0.0321, 0.0000] | −0.0294 [−0.0976, 0.0000] | 63.1% negative, 36.9% tie |
| Linear SVM − MuRIL 42 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 100% tie |
| Logistic Regression − MuRIL 43 | 0.0000 [−0.0276, 0.0264] | 0.0000 [−0.0833, 0.0800] | 33.8% positive, 35.2% negative |
| Linear SVM − MuRIL 43 | **0.0094 [0.0000, 0.0303]** | **0.0294 [0.0000, 0.0909]** | 62.5% positive, 37.5% tie |
| Logistic Regression − MuRIL 44 | −0.0094 [−0.0321, 0.0000] | −0.0294 [−0.0976, 0.0000] | 63.1% negative, 36.9% tie |
| Linear SVM − MuRIL 44 | 0.0000 [0.0000, 0.0000] | 0.0000 [0.0000, 0.0000] | 100% tie |

**The seed-42 MuRIL and linear SVM predictions are identical on all 299 test rows.** The seed-44 predictions are also identical to the SVM. Seed 43 differs on one Spam message: the SVM recovers it, hence the 0.0094 Macro-F1 / 0.0294 recall difference. Since one message is 2.94 percentage points of Spam recall, the seed-43 interval is driven by a single example.

The LR intervals are the mirror image: LR misses one more Spam message than the SVM/MuRIL-42/44. Its 0.0094 Macro-F1 gap is below the 0.01 practical threshold, and its 0.0294 recall gap is below 0.05. None of the random-test differences is practically meaningful.

## 3. D2 random-test pair

Matched frozen test: 883 rows (726 Ham / 67 Spam / 90 Smishing).

| A − B | Δ Macro-F1 (95% CI) | Δ Spam recall (95% CI) | Replicate direction |
|---|---|---|---|
| Logistic Regression − Linear SVM | 0.0052 [−0.0121, 0.0244] | 0.0448 [0.0000, 0.1000] | 71.7% positive; 94.8% positive on recall |

The Macro-F1 interval includes zero and the point difference is 0.0052, below the practical threshold. Spam recall favours LR by 4.48 points — three Spam messages — with the interval touching zero. This is weak, model-specific evidence for LR, not a decisive statistical separation. LR's better Spam F1 (0.803 vs 0.776) and Macro-F1 point estimate support the secondary recommendation, but the comparison does not establish superiority.

## 4. Block-pooled pairs (robustness, not a population estimate)

Pooled out-of-fold predictions over all 1,992 rows. These are **not** independent test rows: the three source blocks are the sampling units, and one has no Spam. Intervals are descriptive.

| A − B | Δ Macro-F1 (95% CI) | Δ Spam recall (95% CI) | Replicate direction |
|---|---|---|---|
| LR − SVM | 0.0070 [−0.0043, 0.0217] | 0.0133 [0.0000, 0.0311] | 86.6% / 95.2% positive |
| LR − MuRIL 42 | **0.0469 [0.0115, 0.0839]** | **0.0578 [0.0153, 0.1038]** | 99.5% / 99.8% positive |
| SVM − MuRIL 42 | **0.0399 [0.0053, 0.0774]** | **0.0444 [0.0049, 0.0890]** | 99.0% / 98.4% positive |
| SVM − MuRIL 43 | **0.0373 [0.0024, 0.0746]** | **0.0444 [0.0049, 0.0891]** | 98.3% / 98.5% positive |
| SVM − MuRIL 44 | 0.0280 [−0.0096, 0.0677] | 0.0311 [−0.0124, 0.0781] | 92.2% / 90.6% positive |

LR versus SVM is negligible on both metrics. MuRIL is **worse** than both classical models under source holdout: 4–4.7 Macro-F1 points and 4.4–5.8 recall points, with intervals above zero for seeds 42 and 43. Seed 44 is less bad because it recovers 10 Spam in block 4001; its interval still includes zero, so seed sensitivity is real.

## 5. Block-6001-only pairs (the decisive fold)

Block 6001–7000 contains 213 of the 225 Spam messages; this is where the pooled gap is produced.

| A − B | Δ Macro-F1 (95% CI) | Δ Spam recall (95% CI) |
|---|---|---|
| LR − SVM | 0.0140 [0.0000, 0.0321] | 0.0141 [0.0000, 0.0324] |
| LR − MuRIL 42 | **0.0838 [0.0473, 0.1278]** | **0.0798 [0.0437, 0.1256]** |
| SVM − MuRIL 42 | **0.0698 [0.0356, 0.1085]** | **0.0657 [0.0327, 0.1055]** |

The classical models detect 14–17 of 213 Spam; MuRIL detects **none** in every seed. The interval for LR−SVM touches zero, so their 0.014 difference is not distinguishable. The MuRIL gap is larger and does not include zero, but it comes from a single held-out block and cannot be generalised to unseen sources.

## 6. Verdict

1. **Random split:** no model is meaningfully better. SVM and MuRIL-42/44 are identical; LR is one Spam message behind. The 95% intervals are narrow but the differences are smaller than the practical threshold.
2. **D2:** LR is the better point estimate, but the Macro-F1 difference is not distinguishable from zero and the Spam-recall interval touches zero. Choose LR for the secondary task on parsimony and Spam F1, not on proof of superiority.
3. **Source holdout:** MuRIL is worse, not better. The result is consistent across seeds 42 and 43, with seed 44 showing the same direction but a wider interval. This is evidence against a transformer advantage on this corpus, not evidence about Malayalam SMS in general.
4. **Selection:** the paired analysis does not justify replacing the SVM with MuRIL. It supports retaining the SVM as the primary D1 model and LR as the secondary D2 model, with MuRIL kept as a documented comparator.

*Generated from `metrics/paired_model_comparison.json` and `block_paired_comparison.csv`; full machine table in `reports/statistical_tables.md`.*
