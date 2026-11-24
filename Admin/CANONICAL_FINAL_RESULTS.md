# Canonical Final Results

**Status:** authoritative for all metrics as of 8 November 2026. Supersedes conflicting numbers in older reports. Models, splits and datasets were not changed. All values were recomputed from frozen predictions by `Research Work/phase2/p2_final_verification.py` and independently by `Research Work/phase2/p2_final_audit_stats.py`; machine outputs are `metrics/final_verification.json` and `metrics/final_audit_stats.json`.

## 1. Scope and metric definitions

- **D1:** Malayalam-containing subset of the Dravidian SMS workbook. Binary Ham/Spam. Primary experiment.
- **D2:** separate English/Latin three-class Ham/Spam/Smishing corpus. Secondary experiment. Never pooled with D1.
- **Grouped random-split test Macro-F1:** duplicate-group-aware, label-stratified 70/15/15 split, seed 42; one frozen test evaluation after validation-only model selection. Macro-F1 is the unweighted mean of the two or three class F1 scores.
- **Pooled leave-one-row-block-out Macro-F1:** hold out one complete consecutive 1,000-row workbook block, train on the other two, predict the held-out block, concatenate all held-out predictions, then compute one Macro-F1. It is not an average of fold scores. The blocks are **row-order proxies**, not verified collection sources.
- **95% group-bootstrap interval:** percentile bootstrap, 2,000 replicates, seed 42. The sampling unit is the duplicate group. Every D1/D2 frozen test group is a singleton, so it is numerically a message bootstrap; this was verified, not assumed.
- **MuRIL mean:** mean of three frozen fine-tuning seeds (42, 43, 44). The across-seed SD is training-run variation, not a confidence interval. The three-seed mean interval below is **conditional on those three fitted seeds** and captures test-sample uncertainty only.

## 2. Dataset 1 — random grouped test

Test: **299 rows**, 265 Ham / 34 Spam; 299 duplicate groups, maximum group size 1. Test block composition: block 4001–5000 = 86 Ham/3 Spam; 5001–6000 = 159 Ham/0 Spam; 6001–7000 = 20 Ham/31 Spam. The test set spans all three blocks, but Spam is concentrated in block 6001.

| Model | Accuracy (95% group-bootstrap CI) | Macro-F1 (95% CI) | Ham P / R / F1 | Spam P / R / F1 | CM (true Ham/Spam × pred) |
|---|---|---|---|---|---|
| Logistic Regression | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9121, 0.9903] | 0.9815 / 1.0000 / 0.9907 | 1.0000 / 0.8529 / 0.9206 | `[[265,0],[5,29]]` |
| Linear SVM | **0.9866 [0.9732, 0.9967]** | **0.9650 [0.9250, 0.9922]** | 0.9851 / 1.0000 / 0.9925 | 1.0000 / **0.8824** / 0.9375 | `[[265,0],[4,30]]` |
| MuRIL seed 42 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.8824 / 0.9375 | `[[265,0],[4,30]]` |
| MuRIL seed 43 | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9099, 0.9903] | 0.9815 / 1.0000 / 0.9907 | 1.0000 / 0.8529 / 0.9206 | `[[265,0],[5,29]]` |
| MuRIL seed 44 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.8824 / 0.9375 | `[[265,0],[4,30]]` |
| **MuRIL mean ± SD** | **0.9855 ± 0.0019** | **0.9619 ± 0.0054** | Ham F1 **0.9919 ± 0.0009** | Spam F1 **0.9319 ± 0.0097**; P 1.0000 / R 0.8725 ± 0.0170 | — |

**MuRIL three-seed mean, conditional test-sample interval:** Macro-F1 **0.9619 [0.9211, 0.9909]**; accuracy **0.9855 [0.9710, 0.9967]**; Spam recall **0.8725 [0.7500, 0.9678]**. This interval is for the average of the three frozen seed predictions, not for a new training run.

**SVM − MuRIL three-seed mean (paired group bootstrap):** Macro-F1 difference **+0.0031200 [0.0000, 0.0101002]**; accuracy **+0.0011148 [0.0000, 0.0033445]**; Spam recall **+0.0098039 [0.0000, 0.0303030]**. All intervals include zero. The models are **not statistically distinguishable** on this test at the available sample size.

**SVM − LR (paired group bootstrap):** Macro-F1 **+0.0093601 [0.0000, 0.0321432]**; Spam recall **+0.0294118 [0.0000, 0.0975610]**; accuracy **+0.0033445 [0.0000, 0.0100334]**. The corresponding LR − SVM values are the negatives: **−0.0093601 [−0.0321432, 0.0000]**, etc. The difference is one test message; 36.85% of shared bootstrap resamples contain neither member of the discordant pair and are exactly tied, which is why the percentile lower bound is 0. Exact two-sided discordance p = 1.0. SVM is not statistically superior to LR; the historical model-selection report's `+0.0094 [−0.0321, 0.0000]` mixed the SVM−LR sign with the LR−SVM interval and is corrected.

**MuRIL seed-to-seed variation:** Macro-F1 0.9650, 0.9556, 0.9650; mean 0.9619, SD 0.0054. Seed 42 and 44 predictions are identical to the SVM; seed 43 is one Spam false negative worse than SVM but not prediction-identical to LR (their aggregate scores tie while individual errors differ). The three seeds therefore provide only one distinct comparison point against SVM, not three independent confirmations. The seed SD is smaller than the test-sample bootstrap SD (~0.018), but it is based on only three seeds and is not a population interval.

## 3. Perfect Spam precision: exact uncertainty

All D1 models produced **zero false positives among 265 Ham**. Perfect precision is based on only the predicted Spam messages, not on all 299 test rows:

| Model | TP | FP | Predicted Spam | Recall denominator | Precision CP 95% | Precision Wilson 95% |
|---|---:|---:|---:|---:|---|---|
| Logistic Regression | 29 | 0 | **29** | 34 | **[0.8806, 1.0000]** | [0.8830, 1.0000] |
| Linear SVM | 30 | 0 | **30** | 34 | **[0.8843, 1.0000]** | [0.8865, 1.0000] |
| MuRIL 42/44 | 30 | 0 | 30 | 34 | [0.8843, 1.0000] | [0.8865, 1.0000] |
| MuRIL 43 | 29 | 0 | 29 | 34 | [0.8806, 1.0000] | [0.8830, 1.0000] |

- **False-positive rate:** 0/265; exact 95% upper bound **1.382%**; Wilson upper bound **1.429%**. The old report’s “3/299 ≈ 1.0%” used the wrong denominator and is corrected.
- **Recall, exact:** SVM 30/34 = 0.8824 [0.7255, 0.9670]; LR 29/34 = 0.8529 [0.6894, 0.9505].
- **Independent duplicate groups among predicted Spam:** 30 (SVM/42/44) or 29 (LR/43); every predicted-Spam group is distinct. There is no within-test duplicate dependence among positives.
- **Campaign dependence remains:** 29 of the SVM’s 30 predicted Spam are in block 6001–7000; LR predicts 29 there and none in block 4001–5000. Perfect precision is therefore a within-campaign observation, not evidence of zero false-positive risk on new sources.
- The exact and Wilson intervals assume exchangeable errors. They are descriptive, not a guarantee for deployment.

## 4. Dataset 1 — pooled leave-one-row-block-out stress test

Blocks are consecutive workbook rows: 4001–5000 (630: 618 Ham/12 Spam), 5001–6000 (991: 991 Ham/0 Spam), 6001–7000 (371: 158 Ham/213 Spam). Corrected membership, not the stale 631/370 counts.

| Model | Pooled accuracy | Pooled Macro-F1 | Spam P | Spam R | Pooled CM |
|---|---:|---:|---:|---:|---|
| Logistic Regression | 0.8865 | **0.5448** | 0.4878 | 0.0889 | `[[1746,21],[205,20]]` |
| Linear SVM | 0.8901 | **0.5378** | 0.6071 | 0.0756 | `[[1756,11],[208,17]]` |
| MuRIL seed 42 | 0.8845 | 0.4979 | 0.3684 | 0.0311 | `[[1755,12],[218,7]]` |
| MuRIL seed 43 | 0.8896 | 0.5006 | 0.7778 | 0.0311 | `[[1765,2],[218,7]]` |
| MuRIL seed 44 | 0.8855 | 0.5098 | 0.4348 | 0.0444 | `[[1754,13],[215,10]]` |
| **MuRIL mean ± SD** | **0.8865** | **0.5028 ± 0.0062** | 0.5270 ± 0.2197 | **0.0356 ± 0.0077** | — |

Per-fold results:

| Fold | LR | SVM | MuRIL mean | Spam support |
|---|---:|---:|---:|---:|
| 4001–5000 | 0.6964 | 0.6964 | 0.8306 | 12 |
| 5001–6000 | 0.4946* | 0.4972* | 0.4987* | 0 |
| 6001–7000 | 0.3825 | **0.3685** | 0.2987 | 213 |

\*The 5001–6000 fold has no Spam; assigning F1=0 to an absent class makes its Macro-F1 an artefact. It is retained only through its Ham false-positive count. The 6001 fold is the decisive failure: MuRIL predicts Ham for all 213 Spam in every seed; LR detects 17/213, SVM 14/213.

**Interpretation limit:** this is a three-block stress test, not a source-population estimate and not proof of failure on “unseen real-world sources.” It shows that the random-split score depends heavily on sharing the dominant Spam block.

## 5. Dataset 2 — secondary English/Latin experiment

Original corpus: **5,971** = 4,844 Ham / 489 Spam / 638 Smishing. After excluding **37 conflicting-label groups / 76 records**: **5,895** = 4,844 Ham / 450 Spam / 601 Smishing. Split: 4,127 train / 885 validation / 883 test (726 Ham / 67 Spam / 90 Smishing). All headline metrics use **5,895**, not 5,971. D2 has no source/collection metadata, so no block-held-out result is defined.

| Model | Accuracy (95% CI) | Macro-F1 (95% CI) | Ham F1 | Spam P / R / F1 | Smishing P / R / F1 | CM |
|---|---|---|---|---|---|---|
| Logistic Regression | **0.9638 [0.9513, 0.9762]** | **0.8877 [0.8482, 0.9239]** | 0.9897 | 0.7857 / 0.8209 / 0.8029 | 0.9250 / 0.8222 / 0.8706 | `[[722,0,4],[10,55,2],[1,15,74]]` |
| Linear SVM | **0.9638 [0.9513, 0.9762]** | 0.8825 [0.8408, 0.9196] | 0.9904 | 0.7761 / 0.7761 / 0.7761 | 0.9487 / 0.8222 / 0.8810 | `[[725,0,1],[12,52,3],[1,15,74]]` |

D2 Spam exact intervals (supplementary): LR precision 55/70 = 0.7857 [0.6713, 0.8748], recall 55/67 = 0.8209 [0.7080, 0.9039]; SVM precision 52/67 = 0.7761 [0.6578, 0.8689], recall 52/67 = 0.7761 [0.6578, 0.8689]. LR is the better D2 point estimate; the paired Macro-F1 difference 0.0052 [−0.0121, 0.0244] includes zero, so superiority is not established.

## 6. Denominators and traceability

| Item | Value | Source |
|---|---|---|
| D1 original usable corpus | 7,714 (7,717 raw; 1 invalid label, 2 empty) | `subset_audit.json`; `DATASET_AUDIT_REPORT.md` |
| D1 Malayalam-containing | 1,992 (1,767/225) | `d1_malayalam.csv` |
| D1 Malayalam-only script | 1,489 (1,429/60) | `d1_malayalam.csv`; `subset_audit.json` |
| D1 Malayalam + Latin | 503 (338/165) | `d1_malayalam.csv` |
| D1 test | 299 (265/34) | `d1_malayalam_test.csv` |
| D2 original | 5,971 (4,844/489/638) | `Dataset_5971.csv`; `d2_all_records.csv` |
| D2 experimental | 5,895 (4,844/450/601) | `d2_grouped.csv`; `split_manifest.json` |
| D2 test | 883 (726/67/90) | `d2_test.csv` |

All values above are traceable to `Research Work/phase2/metrics/final_verification.json` and the frozen prediction CSVs. The independent verifier also confirms that the five D1 prediction files contain the same 299 record IDs in the same label order and that the two D2 files contain the same 883 IDs.

## 7. Claims this table supports

Supported: within-corpus, duplicate-group-controlled comparison; a large drop under row-block holdout; no evidence of a MuRIL advantage; D2 three-class separability with a weak Spam/Smishing boundary.

Not supported: field performance; zero future false positives; generalisation to new sources; Malayalam phishing/smishing detection; Manglish detection; that row blocks are verified collection sources; that 1,489 Malayalam-only records are language-identified Malayalam rather than Malayalam-script-containing.
