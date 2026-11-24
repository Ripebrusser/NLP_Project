# Final Model Selection

> **HISTORICAL / SUPERSEDED.** Retained for experiment provenance. Do not cite for current numbers or claims. Current authority: `Admin/FINAL_MODEL_SELECTION.corrected.md` and `Admin/CANONICAL_FINAL_RESULTS.md`.


> **CORRECTION NOTICE (6 Nov 2026):** Historical version preserved. Read “Random Macro-F1” as **grouped random-split test Macro-F1** and “Block-held-out” as **pooled leave-one-row-block-out Macro-F1** on row-order proxies, not verified sources. Model choices stand, but superiority is not established: SVM−MuRIL mean Macro-F1 is +0.0031 [0.0000, 0.0101]. D2 has no block-held-out result because source metadata are absent. See `Admin/FINAL_MODEL_SELECTION.corrected.md`.

**Phase 2.3, Part D.** Selection uses actual saved results. Random-split scores are the primary within-source benchmark; block-held-out scores are a robustness test, not a second headline.

## 1. Consolidated comparison

| Model | Dataset | Random Macro-F1 | Spam Recall | Block-held-out Macro-F1 |
|---|---|---|---|---|
| Logistic Regression | D1 | 0.9556 | 0.8529 | 0.5448 |
| Linear SVM | D1 | **0.9650** | **0.8824** | 0.5378 |
| MuRIL (3-seed mean) | D1 | 0.9619 ± 0.0054 | 0.8725 ± 0.0170 | 0.5028 ± 0.0062 |
| Logistic Regression | D2 | **0.8877** | **0.8209** | N/A |
| Linear SVM | D2 | 0.8825 | 0.7761 | N/A |

Supporting D1 values: SVM accuracy 0.9866 [0.9732, 0.9967], Spam precision 1.000, 4 errors, no false positives; LR accuracy 0.9833 [0.9666, 0.9967], Spam precision 1.000, 5 errors; MuRIL accuracy 0.9855 ± 0.0019, Spam precision 1.000 in all seeds, 4–5 errors.

D2: LR accuracy 0.9638, Spam F1 0.8029, Smishing F1 0.8706; SVM accuracy 0.9638, Spam F1 0.7761, Smishing F1 0.8810. D2 has no source-block structure, so no block-held-out result exists.

## 2. Evidence behind the decision

### D1 — Linear SVM is the primary model

- **Random split:** SVM has the highest Macro-F1 (0.9650) and Spam recall (0.8824), with zero false positives. MuRIL's mean (0.9619) is lower, and its seed-42 and seed-44 predictions are **identical** to the SVM's: the paired difference is exactly 0.0000 [0.0000, 0.0000] on both Macro-F1 and Spam recall.
- **Against LR:** SVM is better by 0.0094 Macro-F1 [−0.0321, 0.0000] and 0.0294 Spam recall [−0.0976, 0.0000]. This is one Spam message and below the pre-specified practical threshold (0.01 Macro-F1 / 0.05 recall). It is a weak preference, not proof of superiority.
- **Block-held-out:** LR is 0.0070 higher [−0.0043, 0.0217], which is negligible and includes zero; SVM's pooled 0.5378 vs LR's 0.5448 is not a basis for choosing LR. Both collapse relative to the random split. MuRIL is 0.0350 lower than SVM and 0.0420 lower than LR, with 3.56% pooled Spam recall.
- **Calibration:** SVM's validation-selected threshold improves random-test Macro-F1 from 0.9650 to 0.9659 and recall from 0.8824 to 0.9118, at precision 0.9688. This is a sensitivity result (one extra Spam, one false positive), not the primary headline. The block-6001 threshold is unstable (recall 44.3% ± 16.8 across inner splits), so no single block-specific threshold is recommended.
- **Operational:** char-TF-IDF SVM is small, CPU-only and deterministic; MuRIL requires a 913 MB checkpoint and GPU-class compute for no measured gain.

**Recommendation: Linear SVM, char_wb 2–4, C = 0.5, default decision boundary 0.** Report 0.9650 Macro-F1 / 0.8824 Spam recall as the primary within-source result. Do not describe it as state of the art or as cross-source performance.

### D2 — Logistic Regression is the secondary model

LR has the higher Macro-F1 (0.8877 vs 0.8825) and Spam F1 (0.8029 vs 0.7761), with a 4.48-point Spam-recall advantage (three messages). The paired Macro-F1 difference is 0.0052 [−0.0121, 0.0244]; the Spam-recall interval is [0.0000, 0.1000]. This is not a decisive separation, but LR is the better point estimate on the primary metric and on the weakest class. SVM has a slightly higher Smishing F1 (0.8810 vs 0.8706); that does not outweigh LR's Macro-F1 and Spam advantage.

**Recommendation: Logistic Regression, char_wb 2–4, C = 1.0.** D2 is English-only and secondary; its result is not pooled with D1.

### MuRIL — retain as evidence, not as the selected model

MuRIL is **not selected** for either task. It adds no random-split benefit, is worse under source holdout, and its block-6001 probabilities collapse to a constant. The checkpoint and predictions should be retained in the research artifact so the negative result is reproducible; they need not be shipped in a prototype. Keeping MuRIL in the final project is defensible as a **benchmark/comparator**, but not as the production classifier.

## 3. What is primary and what is robustness

| Result | Status |
|---|---|
| D1 SVM random grouped test: 0.9650 Macro-F1, 0.8824 Spam recall, 0 false positives | **Primary within-source result** |
| D2 LR random test: 0.8877 Macro-F1, 0.8209 Spam recall | **Primary secondary-task result** |
| D1 leave-one-block-out: SVM 0.5378, LR 0.5448, MuRIL 0.5028 | **Robustness test** — always report alongside the random score |
| Per-fold block 6001: 0.3685 SVM, 0.3825 LR, 0.2987 MuRIL | **Robustness test** — the decisive source-shift failure |
| Validation-selected thresholds: SVM 0.9659/0.9118 | **Sensitivity analysis** — not the headline |
| Bootstrap CIs and paired intervals | **Uncertainty quantification** — do not convert into a significance claim |
| Any statement about new Malayalam SMS sources | **Not supported** — requires external validation |

The D1 headline must always be written as a pair: **0.9650 within-source, 0.5378 under leave-one-block-out**. Reporting only the first is misleading; reporting only the second hides that the model learns useful within-batch structure.

## 4. Remaining issues

1. **D1 access provenance** is still undocumented. This is an administrative/publication blocker, not a statistical one.
2. **No source-diverse external test set.** The block folds are a stress test, not an estimate of field performance.
3. **Block 6001 has only 12 training Spam.** Its fold cannot distinguish model quality from an impossible calibration regime.
4. **Label inconsistency** is visible in block 4001, where the same Onam campaign carries both labels. This limits the achievable ceiling.
5. **Three source blocks.** No population-level interval or generalisation claim is possible from them.
6. **D2 is English-only.** No Malayalam/Manglish smishing claim is made.

None of these invalidates the completed statistical work; they constrain the claims that may be made from it.

## 5. Decision

**STATISTICAL VALIDATION COMPLETE — READY FOR PROTOTYPE DEVELOPMENT**

The prototype should use the D1 Linear SVM and the D2 Logistic Regression at their default thresholds, expose the source-robustness caveat, and treat any probability/score calibration as source-specific and provisional. The unresolved D1 provenance and the absence of external validation must remain visible before publication or field deployment.
