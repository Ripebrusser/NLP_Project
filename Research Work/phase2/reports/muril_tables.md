# MuRIL D1 — machine-generated tables

Source: `metrics/muril_results.json`; do not edit by hand.

## Configuration and data

| Item | Value |
|---|---|
| Model | `google/muril-base-cased` |
| Max sequence length | 128 (covers 100.0% of rows) |
| Token length median / p95 / p99 / max | 31 / 63 / 90.09 / 127 |
| Learning rate | 2e-05 |
| Batch / accumulation / effective | 4 / 2 / 8 |
| Max epochs / patience | 6 / 2 |
| Class weights (train) | 0.5635 Ham / 4.4395 Spam |
| Package versions | torch 2.11.0+cu128, transformers 5.22.1, CUDA 12.8 |
| GPU | NVIDIA GeForce RTX 4050 Laptop GPU |
| Saved reference model reproduces predictions | True (max prob diff 0.00e+00) |

## Random grouped split — per seed

| Seed | Selected epoch | Accuracy | Macro-F1 | Ham F1 | Spam P | Spam R | Spam F1 | Train s | Peak GPU MB |
|---|---|---|---|---|---|---|---|---|---|
| 42 | 2 | 0.9866 | 0.9650 | 0.9925 | 1.0000 | 0.8824 | 0.9375 | 167 | 4779 |
| 43 | 1 | 0.9833 | 0.9556 | 0.9907 | 1.0000 | 0.8529 | 0.9206 | 114 | 4778 |
| 44 | 1 | 0.9866 | 0.9650 | 0.9925 | 1.0000 | 0.8824 | 0.9375 | 115 | 4778 |
| **Mean ± SD** | — | 0.9855 ± 0.0019 | **0.9619 ± 0.0054** | 0.9919 ± 0.0011 | 1.0000 ± 0.0000 | 0.8725 ± 0.0170 | 0.9319 ± 0.0097 | — | — |

Confusion matrices (rows Ham, Spam; columns Ham, Spam):

- seed 42: `[[265, 0], [4, 30]]`
- seed 43: `[[265, 0], [5, 29]]`
- seed 44: `[[265, 0], [4, 30]]`

## Block-held-out — every fold and seed

Fixed epochs per seed from random validation; held-out block never used for stopping or tuning.

| Seed | Held-out block | Test n | Ham/Spam | Accuracy | Macro-F1 | Spam P | Spam R | Confusion |
|---|---|---|---|---|---|---|---|---|
| 42 | 4001-5000 | 630 | 618/12 | 0.9873 | 0.8150 | 0.7000 | 0.5833 | `[[615, 3], [5, 7]]` |
| 42 | 5001-6000 | 991 | 991/0 | 0.9909 | 0.4977 | — | — | `[[982, 9], [0, 0]]` |
| 42 | 6001-7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 | `[[158, 0], [213, 0]]` |
| 43 | 4001-5000 | 630 | 618/12 | 0.9905 | 0.8476 | 0.8750 | 0.5833 | `[[617, 1], [5, 7]]` |
| 43 | 5001-6000 | 991 | 991/0 | 0.9990 | 0.4997 | — | — | `[[990, 1], [0, 0]]` |
| 43 | 6001-7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 | `[[158, 0], [213, 0]]` |
| 44 | 4001-5000 | 630 | 618/12 | 0.9841 | 0.8293 | 0.5556 | 0.8333 | `[[610, 8], [2, 10]]` |
| 44 | 5001-6000 | 991 | 991/0 | 0.9950 | 0.4987 | — | — | `[[986, 5], [0, 0]]` |
| 44 | 6001-7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 | `[[158, 0], [213, 0]]` |

## Block-held-out — pooled per seed

| Seed | Accuracy | Macro-F1 | Spam P | Spam R | Spam F1 | Confusion |
|---|---|---|---|---|---|---|
| 42 | 0.8845 | 0.4979 | 0.3684 | 0.0311 | 0.0574 | `[[1755, 12], [218, 7]]` |
| 43 | 0.8896 | 0.5006 | 0.7778 | 0.0311 | 0.0598 | `[[1765, 2], [218, 7]]` |
| 44 | 0.8855 | 0.5098 | 0.4348 | 0.0444 | 0.0806 | `[[1754, 13], [215, 10]]` |
| **Mean ± SD** | 0.8865 ± 0.0027 | **0.5028 ± 0.0062** | 0.5270 ± 0.2197 | 0.0356 ± 0.0077 | 0.0660 ± 0.0128 | — |

## Classical versus MuRIL (actual saved results)

| Model | Random-split Macro-F1 | Random-split Spam recall | Block-held-out Macro-F1 (pooled) | Block-held-out Spam recall |
|---|---|---|---|---|
| Logistic Regression | 0.9556 | 0.8529 | 0.5448 | 0.0889 |
| Linear SVM | 0.9650 | 0.8824 | 0.5378 | 0.0756 |
| MuRIL (3-seed mean) | 0.9619 | 0.8725 | 0.5028 | 0.0356 |
