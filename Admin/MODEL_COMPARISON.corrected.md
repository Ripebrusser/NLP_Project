# Model Comparison — Corrected

**Correction date:** 6 November 2026. Supersedes `Research Work/phase2/reports/MODEL_COMPARISON.md` where it uses “Random Macro-F1,” “block-held-out,” or implies a transformer advantage. Original preserved.

## 1. D1 — grouped random-split test

Test 299 = 265 Ham / 34 Spam. All models use the same frozen IDs.

| Model | Accuracy | Macro-F1 | Spam P | Spam R | Spam F1 |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.9833 | 0.9556 | 1.0000 | 0.8529 | 0.9206 |
| Linear SVM | **0.9866** | **0.9650** | 1.0000 | **0.8824** | 0.9375 |
| MuRIL 42 | 0.9866 | 0.9650 | 1.0000 | 0.8824 | 0.9375 |
| MuRIL 43 | 0.9833 | 0.9556 | 1.0000 | 0.8529 | 0.9206 |
| MuRIL 44 | 0.9866 | 0.9650 | 1.0000 | 0.8824 | 0.9375 |
| MuRIL mean ± SD | 0.9855 ± 0.0019 | 0.9619 ± 0.0054 | 1.0000 | 0.8725 ± 0.0170 | 0.9319 ± 0.0097 |

Bootstrap 95%: LR Macro-F1 [0.9121, 0.9903]; SVM [0.9250, 0.9922]; MuRIL mean conditional [0.9211, 0.9909]. Exact precision lower bounds 0.8806 (LR) / 0.8843 (SVM); zero-FP upper bound 1.382%.

**No transformer advantage:** SVM − mean(MuRIL) Macro-F1 = +0.0031 [0.0000, 0.0101]; accuracy +0.0011 [0.0000, 0.0033]; Spam recall +0.0098 [0.0000, 0.0303]. All include zero. Seeds 42 and 44 are prediction-identical to SVM; seed 43 differs on one message.

## 2. D1 — pooled leave-one-row-block-out stress test

| Model | Pooled Macro-F1 | Spam recall | Pooled CM |
|---|---:|---:|---|
| LR | **0.5448** | 0.0889 | `[[1746,21],[205,20]]` |
| SVM | 0.5378 | 0.0756 | `[[1756,11],[208,17]]` |
| MuRIL 42 | 0.4979 | 0.0311 | `[[1755,12],[218,7]]` |
| MuRIL 43 | 0.5006 | 0.0311 | `[[1765,2],[218,7]]` |
| MuRIL 44 | 0.5098 | 0.0444 | `[[1754,13],[215,10]]` |

The block fold 6001–7000 contains 213 Spam. LR detects 17, SVM 14, MuRIL 0 in every seed. The 5001 fold has no Spam and its Macro-F1 is an absent-class artefact. Blocks are **row-order proxies**, not verified collection sources; this is a stress test, not external validation.

## 3. D2 — secondary English/Latin experiment

Test 883 = 726 Ham / 67 Spam / 90 Smishing; experimental n = 5,895 (original 5,971 minus 76 conflict-group records).

| Model | Accuracy | Macro-F1 | Spam F1 | Smishing F1 |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.9638 | **0.8877** | **0.8029** | 0.8706 |
| Linear SVM | 0.9638 | 0.8825 | 0.7761 | **0.8810** |

Paired LR − SVM: Macro-F1 +0.0052 [−0.0121, 0.0244]; Spam recall +0.0448 [0.0000, 0.1000]. LR is the better point estimate; superiority is not established. D2 is not an external Malayalam test set and must never be pooled with D1.

## 4. Verdict

- D1: no statistically distinguishable model advantage; SVM is a defensible simple choice, not a proven winner.
- MuRIL: no improvement, and worse under block holdout; retain as comparator/negative result.
- D2: LR weak point-estimate preference.
- No result supports field performance, zero future false positives, or generalisation to new sources.
