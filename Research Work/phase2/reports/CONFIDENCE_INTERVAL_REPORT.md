# Confidence Interval Report — Complete

> **HISTORICAL / SUPERSEDED.** Retained for experiment provenance. Do not cite for current numbers or claims. Current authority: `Admin/CONFIDENCE_INTERVAL_REPORT.corrected.md` and `Admin/CANONICAL_FINAL_RESULTS.md`.


> **CORRECTION NOTICE (6 Nov 2026):** This historical version is preserved. The zero-FP “3/299 ≈ 1.0%” statement below is wrong: the denominator is 265 Ham, and the exact 95% upper bound is **1.382%**. The degenerate precision interval is replaced by exact lower bounds **0.8806/0.8843**, and a conditional MuRIL three-seed mean interval **[0.9211, 0.9909]** is added. See `Admin/CONFIDENCE_INTERVAL_REPORT.corrected.md` and `Admin/CANONICAL_FINAL_RESULTS.md`. Other point estimates are unchanged.

**Phase 2.3, Part A.** Frozen test predictions only. No model was retrained, no split was changed, and no test label was used for model or threshold selection.

## 1. Method

- **Nonparametric percentile bootstrap** over duplicate groups (`group_id`).
- **2,000 replicates**, fixed seed **42** (`numpy.random.default_rng(42)`).
- Resampling unit: duplicate group. Every group in both frozen test sets contains exactly one row (D1 299 rows / 299 groups; D2 883 / 883), so the result is numerically equivalent to a message-level bootstrap. The group-aware implementation is retained so the procedure stays correct if duplicates are present.
- 95% interval = 2.5th and 97.5th percentiles.
- Metrics use a fixed label order. When a class is absent from a replicate, its F1 is 0.
- D1 and D2 are separate tasks with different label spaces and are never pooled.
- MuRIL is treated in two separate ways:
  1. **Within-seed test-sample uncertainty:** a group bootstrap for each seed's frozen predictions.
  2. **Across-seed training variation:** mean, SD, min and max of the three seed-level point values. These are **not** combined into one interval, because three seeds do not estimate a population of training runs.

This report supersedes the Phase 2.2 version; that file is preserved as `CONFIDENCE_INTERVAL_REPORT.phase22.md`. The Phase 2.2 version had no MuRIL intervals and did not report per-class precision/recall. No earlier value changed.

## 2. D1 — Logistic Regression (random grouped test)

Test rows 299 (265 Ham / 34 Spam); groups 299.

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9833 | 0.9666 | 0.9967 | 0.0074 |
| Macro-F1 | 0.9556 | 0.9121 | 0.9903 | 0.0201 |
| Ham F1 | 0.9907 | 0.9813 | 0.9981 | 0.0042 |
| Spam F1 | 0.9206 | 0.8387 | 0.9825 | 0.0365 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8529 | 0.7222 | 0.9655 | 0.0617 |
| Ham precision | 0.9815 | 0.9634 | 0.9963 | 0.0083 |
| Ham recall | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

## 3. D1 — Linear SVM (random grouped test)

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9866 | 0.9732 | 0.9967 | 0.0066 |
| Macro-F1 | 0.9650 | 0.9250 | 0.9922 | 0.0178 |
| Ham F1 | 0.9925 | 0.9846 | 0.9982 | 0.0037 |
| Spam F1 | 0.9375 | 0.8636 | 0.9863 | 0.0321 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8824 | 0.7600 | 0.9730 | 0.0560 |
| Ham precision | 0.9851 | 0.9697 | 0.9964 | 0.0068 |
| Ham recall | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

The observed precision is 1.000 because there are zero false positives, but the exact 95% lower bound is only **0.8843** (30/30) or **0.8806** (29/29). This does **not** prove zero false-positive risk: zero FP in 265 Ham has an exact 95% upper bound of **1.382%**, not 3/299 ≈ 1.0%. See the correction notice.

## 4. D1 — MuRIL, within-seed uncertainty

Model: `google/muril-base-cased`; test rows 299 each. Each seed's predictions are bootstrapped separately.

### Seed 42

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9866 | 0.9732 | 0.9967 | 0.0066 |
| Macro-F1 | 0.9650 | 0.9250 | 0.9922 | 0.0178 |
| Ham F1 | 0.9925 | 0.9846 | 0.9982 | 0.0037 |
| Spam F1 | 0.9375 | 0.8636 | 0.9863 | 0.0321 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8824 | 0.7600 | 0.9730 | 0.0560 |

### Seed 43

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9833 | 0.9666 | 0.9967 | 0.0074 |
| Macro-F1 | 0.9556 | 0.9099 | 0.9903 | 0.0205 |
| Ham F1 | 0.9907 | 0.9813 | 0.9981 | 0.0042 |
| Spam F1 | 0.9206 | 0.8364 | 0.9825 | 0.0375 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8529 | 0.7188 | 0.9655 | 0.0632 |

### Seed 44

Identical predictions to seed 42, so every interval is identical.

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9866 | 0.9732 | 0.9967 | 0.0066 |
| Macro-F1 | 0.9650 | 0.9250 | 0.9922 | 0.0178 |
| Ham F1 | 0.9925 | 0.9846 | 0.9982 | 0.0037 |
| Spam F1 | 0.9375 | 0.8636 | 0.9863 | 0.0321 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8824 | 0.7600 | 0.9730 | 0.0560 |

### Across-seed variation (not a confidence interval)

| Metric | Mean | SD | Min | Max |
|---|---|---|---|---|
| Accuracy | 0.9855 | 0.0019 | 0.9833 | 0.9866 |
| Macro-F1 | 0.9619 | 0.0054 | 0.9556 | 0.9650 |
| Ham F1 | 0.9919 | 0.0011 | 0.9907 | 0.9925 |
| Spam F1 | 0.9319 | 0.0097 | 0.9206 | 0.9375 |
| Spam precision | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| Spam recall | 0.8725 | 0.0170 | 0.8529 | 0.8824 |

The within-seed intervals overlap almost completely. Seed variation (Macro-F1 SD 0.0054) is much smaller than the test-sample uncertainty (bootstrap SD about 0.018–0.021). Neither source of variation is combined into a single interval; that would conflate sampling noise with training-run variation.

## 5. D2 — Logistic Regression

Test rows 883 (726 Ham / 67 Spam / 90 Smishing); groups 883.

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9638 | 0.9513 | 0.9762 | 0.0063 |
| Macro-F1 | 0.8877 | 0.8482 | 0.9239 | 0.0191 |
| Ham F1 | 0.9897 | 0.9841 | 0.9947 | 0.0027 |
| Spam F1 | 0.8029 | 0.7244 | 0.8722 | 0.0379 |
| Spam precision | 0.7857 | 0.6885 | 0.8784 | 0.0482 |
| Spam recall | 0.8209 | 0.7222 | 0.9130 | 0.0481 |
| Smishing F1 | 0.8706 | 0.8138 | 0.9223 | 0.0274 |
| Smishing precision | 0.9250 | 0.8611 | 0.9759 | 0.0298 |
| Smishing recall | 0.8222 | 0.7400 | 0.9000 | 0.0410 |
| Ham precision | 0.9850 | 0.9757 | 0.9932 | 0.0045 |
| Ham recall | 0.9945 | 0.9884 | 0.9986 | 0.0026 |

## 6. D2 — Linear SVM

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9638 | 0.9513 | 0.9762 | 0.0063 |
| Macro-F1 | 0.8825 | 0.8408 | 0.9196 | 0.0198 |
| Ham F1 | 0.9904 | 0.9853 | 0.9952 | 0.0026 |
| Spam F1 | 0.7761 | 0.6897 | 0.8493 | 0.0404 |
| Spam precision | 0.7761 | 0.6735 | 0.8710 | 0.0501 |
| Spam recall | 0.7761 | 0.6721 | 0.8750 | 0.0513 |
| Smishing F1 | 0.8810 | 0.8252 | 0.9290 | 0.0265 |
| Smishing precision | 0.9487 | 0.8928 | 0.9880 | 0.0245 |
| Smishing recall | 0.8222 | 0.7412 | 0.8989 | 0.0400 |
| Ham precision | 0.9824 | 0.9727 | 0.9917 | 0.0049 |
| Ham recall | 0.9986 | 0.9958 | 1.0000 | 0.0015 |

## 7. Block-held-out results — no population-level CI

Each source block is reported separately. There are only three blocks, one with no Spam; a narrow interval would imply an independent source sample that does not exist. The range is descriptive.

| Model | Held-out block | n | Ham/Spam | Accuracy | Macro-F1 | Spam P | Spam R |
|---|---|---|---|---|---|---|---|
| LR | 4001–5000 | 630 | 618/12 | 0.9857 | 0.6964 | 1.0000 | 0.2500 |
| LR | 5001–6000 | 991 | 991/0 | 0.9788 | 0.4946* | — | — |
| LR | 6001–7000 | 371 | 158/213 | 0.4717 | 0.3825 | 1.0000 | 0.0798 |
| SVM | 4001–5000 | 630 | 618/12 | 0.9857 | 0.6964 | 1.0000 | 0.2500 |
| SVM | 5001–6000 | 991 | 991/0 | 0.9889 | 0.4972* | — | — |
| SVM | 6001–7000 | 371 | 158/213 | 0.4636 | 0.3685 | 1.0000 | 0.0657 |
| MuRIL 42 | 4001–5000 | 630 | 618/12 | 0.9873 | 0.8150 | 0.7000 | 0.5833 |
| MuRIL 42 | 5001–6000 | 991 | 991/0 | 0.9909 | 0.4977* | — | — |
| MuRIL 42 | 6001–7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 |
| MuRIL 43 | 4001–5000 | 630 | 618/12 | 0.9905 | 0.8476 | 0.8750 | 0.5833 |
| MuRIL 43 | 5001–6000 | 991 | 991/0 | 0.9990 | 0.4997* | — | — |
| MuRIL 43 | 6001–7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 |
| MuRIL 44 | 4001–5000 | 630 | 618/12 | 0.9841 | 0.8293 | 0.5556 | 0.8333 |
| MuRIL 44 | 5001–6000 | 991 | 991/0 | 0.9950 | 0.4987* | — | — |
| MuRIL 44 | 6001–7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 |

\* The 5001–6000 block contains no Spam. Spam F1 is assigned 0, so macro-F1 is not a balanced performance estimate; Spam precision/recall are undefined. The real error signal is the Ham false-positive count.

Observed ranges across blocks: LR macro-F1 0.3825–0.6964, Spam recall 0.0798–0.2500; SVM 0.3685–0.6964, 0.0657–0.2500; MuRIL 0.2987–0.8476, 0.0–0.8333. These ranges are descriptive, not a confidence interval.

## 8. Interpretation

- The D1 random-test intervals describe uncertainty **within the existing source distribution**, not generalisation to new Malayalam SMS sources.
- D1 has three source blocks and 94.7% of Spam in one block. The block results, not the narrow random-split interval, are the relevant evidence about source shift.
- D2 has no recorded source-block structure. Its intervals are appropriate for this corpus but still say nothing about new SMS sources.
- MuRIL's seed-to-seed spread is small relative to test-sample noise, so seed choice cannot explain its block-6001 collapse.
- Every interval here is from frozen predictions; no test set was re-evaluated to obtain a narrower interval.

*Generated by `p2_stats.py`; raw values in `metrics/confidence_intervals.json` and `.csv`; machine tables in `reports/statistical_tables.md`.*
