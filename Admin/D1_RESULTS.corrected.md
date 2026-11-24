# Dataset 1 — Corrected Results

**Correction date:** 6 November 2026. Supersedes `Research Work/phase2/reports/D1_RESULTS.md` for block counts, the 6001 fold, precision uncertainty and terminology. Original preserved unchanged.

## 1. Data and split

D1 is the **Malayalam-containing** subset of the five-language Dravidian workbook: **1,992** records (1,767 Ham / 225 Spam). “Malayalam” means the message contains at least one Malayalam Unicode character, not that a language identifier classified it as Malayalam.

- Malayalam-only script: **1,489** (1,429 Ham / 60 Spam).
- Malayalam + Latin: **503** (338 Ham / 165 Spam).
- Other Indic scripts co-occurring: 0.
- Duplicate groups: 1,824; 0 label conflicts in this subset.
- Grouped 70/15/15 split, seed 42: **1,394 / 299 / 299**; test 265 Ham / 34 Spam.
- Test groups: 299, all singletons.

## 2. Grouped random-split test (primary within-source result)

| Model | Accuracy | Macro-F1 | Ham P/R/F1 | Spam P/R/F1 | CM |
|---|---|---|---|---|---|
| Linear SVM | 0.9866 [0.9732, 0.9967] | **0.9650 [0.9250, 0.9922]** | 0.9851/1.0000/0.9925 | 1.0000/0.8824/0.9375 | `[[265,0],[4,30]]` |
| Logistic Regression | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9121, 0.9903] | 0.9815/1.0000/0.9907 | 1.0000/0.8529/0.9206 | `[[265,0],[5,29]]` |
| MuRIL seed 42 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851/1.0000/0.9925 | 1.0000/0.8824/0.9375 | `[[265,0],[4,30]]` |
| MuRIL seed 43 | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9099, 0.9903] | 0.9815/1.0000/0.9907 | 1.0000/0.8529/0.9206 | `[[265,0],[5,29]]` |
| MuRIL seed 44 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851/1.0000/0.9925 | 1.0000/0.8824/0.9375 | `[[265,0],[4,30]]` |

**Precision correction:** 30/30 (SVM) and 29/29 (LR) are perfect observed counts. Exact 95% lower bounds are **0.8843** and **0.8806**; the zero-FP upper bound over 265 Ham is **1.382%**. Do not write “100% precision” without these bounds. The old “3/299 ≈ 1.0%” FPR statement is wrong; 299 is not the Ham denominator.

**Test composition:** block 4001–5000 = 86 Ham/3 Spam; 5001–6000 = 159 Ham/0 Spam; 6001–7000 = 20 Ham/31 Spam. SVM predicts 1 Spam in block 4001 and 29 in block 6001; LR predicts 0 and 29. Perfect precision is therefore a within-campaign observation.

## 3. Leave-one-row-block-out stress test (corrected counts)

Blocks are consecutive source Excel rows. They are **row-order proxies**, not documented collection sources.

| Block | n | Ham | Spam |
|---|---:|---:|---:|
| 4001–5000 | 630 | 618 | 12 |
| 5001–6000 | 991 | 991 | 0 |
| 6001–7000 | 371 | 158 | 213 |

The stale 631/370 counts and the 0.3677 fold are superseded. Corrected per-fold results:

| Fold | LR Macro-F1 | SVM Macro-F1 | MuRIL mean Macro-F1 | Spam support |
|---|---:|---:|---:|---:|
| 4001–5000 | 0.6964 | 0.6964 | 0.8306 | 12 |
| 5001–6000 | 0.4946* | 0.4972* | 0.4987* | 0 |
| 6001–7000 | 0.3825 | **0.3685** | 0.2987 | 213 |

\*No Spam in the held-out block; Macro-F1 is an absent-class artefact. Do not interpret it as balanced performance.

**Pooled held-out predictions:** LR 0.5448 (CM `[[1746,21],[205,20]]`), SVM 0.5378 (CM `[[1756,11],[208,17]]`), MuRIL mean 0.5028 ± 0.0062. The 6001 fold detects 17/213 (LR), 14/213 (SVM), 0/213 (MuRIL in every seed).

## 4. Correct interpretation

The random-split result is a **within-batch** result: 94.7% of Spam is in block 6001–7000. The pooled block result is the relevant stress test, but with only three blocks it is not a source-population estimate and does not prove failure on “unseen real-world sources.” The defensible statement is: **performance is highly dependent on sharing the dominant Spam row block.**

The Malayalam-only subgroup (221 test rows, 11 Spam) is descriptive only; it is not a separately trained model and is too small for a stable claim.

## 5. Reproduction

Frozen predictions and metrics: `Research Work/phase2/metrics/`. Independent check: `p2_final_verification.py`; 299/299 IDs and labels align; 14/14 classical metrics reproduce to ≤1.11×10⁻¹⁶.
