# Final Model Selection — Corrected

**Correction date:** 8 November 2026. Supersedes `Research Work/phase2/reports/FINAL_MODEL_SELECTION.md` for terminology and strength of claim. Original preserved. The 6 November LR–SVM interval typo is corrected below.

## 1. Consolidated comparison

| Model | Dataset | Grouped random-split test Macro-F1 | Spam recall | Pooled leave-one-row-block-out Macro-F1 |
|---|---|---:|---:|---:|
| Logistic Regression | D1 | 0.9556 | 0.8529 | 0.5448 |
| Linear SVM | D1 | **0.9650** | **0.8824** | 0.5378 |
| MuRIL (3-seed mean) | D1 | 0.9619 ± 0.0054 | 0.8725 ± 0.0170 | 0.5028 ± 0.0062 |
| Logistic Regression | D2 | **0.8877** | **0.8209** | Not defined |
| Linear SVM | D2 | 0.8825 | 0.7761 | Not defined |

D1 test = 299 (265/34). D2 test = 883 (726/67/90), from 5,895 records after 37 conflicting groups / 76 records were excluded from the original 5,971.

## 2. D1 decision

**Select Linear SVM (char_wb 2–4, C=0.5, default boundary 0)** as the primary D1 model, with an explicit weak-preference caveat.

- SVM and MuRIL seeds 42/44 produce identical predictions: Δ Macro-F1 = 0.0000. Seed 43 differs by one Spam message.
- **SVM − LR:** +0.0093601 Macro-F1 **[0.0000, 0.0321432]**; +0.0294118 Spam recall **[0.0000, 0.0975610]**; +0.0033445 accuracy **[0.0000, 0.0100334]**. The earlier line `+0.0094 [−0.0321, 0.0000]` was directionally invalid: it attached the SVM−LR point estimate to the LR−SVM interval. This is one discordant test message; exact two-sided p = 1.0. It is not proof of superiority.
- Pooled block: LR is 0.0070 higher [−0.0043, 0.0217]; negligible and includes zero. SVM is selected on simplicity, deterministic CPU inference, and random-split point estimate—not on a significant difference.
- MuRIL is **not** selected. It has no random-split advantage and is worse under block holdout (0.5028; 3.56% Spam recall).
- The D1 headline is a pair: **0.9650 grouped random / 0.5378 pooled row-block**. Reporting only one is misleading.

## 3. D2 decision

**Select Logistic Regression (char_wb 2–4, C=1.0)** as the secondary English model. LR has the higher Macro-F1 (0.8877 vs 0.8825) and Spam F1 (0.8029 vs 0.7761), but the paired Macro-F1 difference is 0.0052 [−0.0121, 0.0244] and the Spam-recall difference is 0.0448 [0.0000, 0.1000]. This is a weak point-estimate preference, not a decisive statistical separation. D2 is English/Latin-only, has no source metadata, and is not external validation for D1.

## 4. What may be claimed

| Claim | Status |
|---|---|
| D1 SVM grouped random test: 0.9650 Macro-F1, 0.8824 recall, 0 FP | Supported within corpus |
| D1 pooled row-block: 0.5378, 3.56% MuRIL recall | Supported as a three-block stress test |
| MuRIL does not improve on SVM here | Supported, with seed-level caveat |
| D2 LR 0.8877 Macro-F1 | Supported within D2 |
| Perfect precision means safe deployment | **Not supported** |
| Generalisation to new Malayalam sources | **Not supported** |
| Malayalam phishing/smishing detection | **Not supported** |
| State of the art / first Malayalam detector | **Not supported** |

## 5. Decision

**Statistical validation and model selection are complete for a bounded student paper.** The prototype should use D1 SVM and D2 LR at their default thresholds, display the row-block caveat, and call itself a demonstration. D1 permission and external validation remain publication blockers.
