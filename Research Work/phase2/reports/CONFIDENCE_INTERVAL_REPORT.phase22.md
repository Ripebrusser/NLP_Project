# Confidence Interval Report — classical baselines

> **CORRECTION NOTICE (6 Nov 2026):** Historical version preserved. Its “3/299 ≈ 1.0%” zero-FP bound is wrong: the denominator is 265 Ham and the exact 95% upper bound is **1.382%**. The degenerate precision interval should be read with exact lower bounds **0.8806/0.8843**. See `Admin/CONFIDENCE_INTERVAL_REPORT.corrected.md`.

**Phase 2.2, Part A.** Frozen test predictions only; no retraining and no split changes.

## Method

- Nonparametric **percentile bootstrap** over duplicate groups (`group_id`).
- **2,000 replicates**, fixed seed **42** (`numpy.random.default_rng`).
- Resampling unit: duplicate group. Every group in both frozen test sets contains exactly one row, so this is numerically equivalent to a message-level bootstrap; the group-aware implementation is used so the procedure remains correct if the test files ever contain duplicates.
- 95% interval = 2.5th and 97.5th percentiles of the replicate distribution.
- Metrics use a fixed label order; when a class is absent from a replicate, its F1 is 0 (no class disappeared in practice).

## D1 — Linear SVM

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9866 | 0.9732 | 0.9967 | 0.0066 |
| Macro-F1 | 0.9650 | 0.9250 | 0.9922 | 0.0178 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8824 | 0.7600 | 0.9730 | 0.0560 |
| Ham F1 | 0.9925 | 0.9846 | 0.9982 | 0.0037 |
| Spam F1 | 0.9375 | 0.8636 | 0.9863 | 0.0321 |

Test rows: 299; groups: 299; replicates predicting Spam: 2000.

## D1 — Logistic Regression

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9833 | 0.9666 | 0.9967 | 0.0074 |
| Macro-F1 | 0.9556 | 0.9121 | 0.9903 | 0.0201 |
| Spam precision | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| Spam recall | 0.8529 | 0.7222 | 0.9655 | 0.0617 |
| Ham F1 | 0.9907 | 0.9813 | 0.9981 | 0.0042 |
| Spam F1 | 0.9206 | 0.8387 | 0.9825 | 0.0365 |

Test rows: 299; groups: 299; replicates predicting Spam: 2000.

## D2 — Logistic Regression

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9638 | 0.9513 | 0.9762 | 0.0063 |
| Macro-F1 | 0.8877 | 0.8482 | 0.9239 | 0.0191 |
| Spam precision | 0.7857 | 0.6885 | 0.8784 | 0.0482 |
| Spam recall | 0.8209 | 0.7222 | 0.9130 | 0.0481 |
| ham F1 | 0.9897 | 0.9841 | 0.9947 | 0.0027 |
| spam F1 | 0.8029 | 0.7244 | 0.8722 | 0.0379 |
| smishing F1 | 0.8706 | 0.8138 | 0.9223 | 0.0274 |

Test rows: 883; groups: 883; replicates predicting Spam: 2000.

## D2 — Linear SVM

| Metric | Point | 95% low | 95% high | Bootstrap SD |
|---|---|---|---|---|
| Accuracy | 0.9638 | 0.9513 | 0.9762 | 0.0063 |
| Macro-F1 | 0.8825 | 0.8408 | 0.9196 | 0.0198 |
| Spam precision | 0.7761 | 0.6735 | 0.8710 | 0.0501 |
| Spam recall | 0.7761 | 0.6721 | 0.8750 | 0.0513 |
| ham F1 | 0.9904 | 0.9853 | 0.9952 | 0.0026 |
| spam F1 | 0.7761 | 0.6897 | 0.8493 | 0.0404 |
| smishing F1 | 0.8810 | 0.8252 | 0.9290 | 0.0265 |

Test rows: 883; groups: 883; replicates predicting Spam: 2000.

## Block-held-out results (no narrow CI)

Each source block is reported separately. With only three blocks — one of which has no Spam — a conventional confidence interval would imply an independent sample that does not exist. The observed range is descriptive.

| Model | Held-out rows | Test n | Ham | Spam | Accuracy | Macro-F1 | Spam P | Spam R |
|---|---|---|---|---|---|---|---|---|
| linear_svm | 4001-5000 | 630 | 618 | 12 | 0.9857 | 0.6964 | 1.0000 | 0.2500 |
| linear_svm | 5001-6000 | 991 | 991 | 0 | 0.9889 | 0.4972 | — | — |
| linear_svm | 6001-7000 | 371 | 158 | 213 | 0.4636 | 0.3685 | 1.0000 | 0.0657 |
| logreg | 4001-5000 | 630 | 618 | 12 | 0.9857 | 0.6964 | 1.0000 | 0.2500 |
| logreg | 5001-6000 | 991 | 991 | 0 | 0.9788 | 0.4946 | — | — |
| logreg | 6001-7000 | 371 | 158 | 213 | 0.4717 | 0.3825 | 1.0000 | 0.0798 |

### Observed range across the three blocks

| Model | Macro-F1 min | Macro-F1 max | Spam R min | Spam R max | Acc. min | Acc. max |
|---|---|---|---|---|---|---|
| linear_svm | 0.3685 | 0.6964 | 0.0657 | 0.2500 | 0.4636 | 0.9889 |
| logreg | 0.3825 | 0.6964 | 0.0798 | 0.2500 | 0.4717 | 0.9857 |

The 5001–6000 fold contains no Spam: its macro-F1 (~0.495) is an artefact of assigning zero F1 to an absent class, and Spam precision/recall are undefined. The 6001–7000 fold has only 12 Spam in training.

## Interpretation and limitations

- These intervals describe uncertainty **within the existing test distribution**. They do not estimate generalisation to unseen sources.
- D1 has only three source blocks, with 94.7% of Spam in one of them. The block results above, not the bootstrap interval, are the relevant evidence about source shift.
- D1's Spam precision is 1.000 with zero observed false positives, so its percentile interval is degenerate at 1.000. That does not prove zero risk: the exact 95% upper bound on the false-positive rate is **1.382%** (0/265 Ham), not 3/299 ≈ 1.0%.
- D2 has no source-block structure recorded, so its bootstrap intervals are the appropriate uncertainty estimate for this corpus. They still say nothing about new SMS sources.

*Generated by `p2_ci.py`; raw values in `metrics/confidence_intervals.json`.*
