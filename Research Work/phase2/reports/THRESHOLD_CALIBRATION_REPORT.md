# Decision-Threshold Calibration and Source-Shift Diagnosis

**Phase 2.3, Part C.** Test labels were never used to select a threshold. Every selected threshold comes from data separate from the evaluation rows; the held-out block is used only to report the consequence.

## 1. Question and method

The question is whether the poor block-6001–7000 Spam recall is a **decision-threshold** problem or a **representation/source-shift** problem.

Two distinct analyses were run:

1. **Random split.** Models were refitted on the frozen training split only. The threshold was selected on the frozen validation split, then applied to the saved test scores of the final model. This avoids using the contaminated train+validation refit to choose a threshold.
2. **Leave-one-block-out.** For each fold, an 80/20 stratified inner split was drawn from the **two training blocks only**. The model was fitted on 80%, the threshold selected on 20%, and that threshold applied to the held-out block's saved out-of-fold scores. This was repeated for 20 inner splits (seeds 42–61) to measure threshold stability. The held-out block never entered fitting or threshold selection.

**Selection rule:** maximise Spam macro-F1 on the validation rows; ties are broken by the widest margin to the nearest validation score (a stable threshold, not the first grid point). A secondary rule maximises macro-F1 subject to validation Spam precision ≥ 0.90.

No new architecture, hyperparameter search or test-set tuning was performed.

## 2. Random split — validation-selected thresholds

| Model | Default t | Selected t | Test default Macro-F1 | Test selected Macro-F1 | Test default R | Test selected R | Test default P | Test selected P | Predictions changed |
|---|---|---|---|---|---|---|---|---|---|
| Logistic Regression | 0.5000 | 0.4764 | 0.9556 | **0.9650** | 0.8529 | 0.8824 | 1.0000 | 1.0000 | 1 |
| Linear SVM | 0.0000 | −0.2370 | 0.9650 | **0.9659** | 0.8824 | **0.9118** | 1.0000 | 0.9688 | 2 |
| MuRIL seed 42 | 0.5000 | 0.4664 | 0.9650 | 0.9650 | 0.8824 | 0.8824 | 1.0000 | 1.0000 | 0 |

Selected-threshold confusion matrices (rows Ham, Spam):

- LR default `[[265, 0], [5, 29]]` → selected `[[265, 0], [4, 30]]`.
- SVM default `[[265, 0], [4, 30]]` → selected `[[264, 1], [3, 31]]`.
- MuRIL unchanged `[[265, 0], [4, 30]]`.

The LR and SVM gains are one and two messages respectively. SVM buys one extra Spam detection at the cost of one false positive; LR recovers one Spam with no false positive. These are **sensitivity results**, not a new headline: the random test has only 34 Spam, and the threshold was chosen on 34 validation Spam. The default-threshold results remain the primary benchmark for comparability.

MuRIL's validation scores are perfectly separated (Ham ≈ 0.055, Spam ≥ 0.7), so any threshold in a wide interval gives the same test predictions. Its threshold is identifiable but irrelevant to the observed errors.

## 3. Block folds — selected thresholds and held-out consequences

Primary inner split (seed 42). “Selected” is the threshold chosen on the inner validation rows; “default” is the model's original boundary.

| Model | Held-out block | Train Spam | Inner-val Spam | Default t | Selected t | Default Macro-F1 | Selected Macro-F1 | Default R | Selected R | Default P | Selected P |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LR | 4001–5000 | 213 | 43 | 0.000 | 0.4414 | 0.6964 | 0.6388 | 0.2500 | 0.1667 | 1.0000 | 1.0000 |
| LR | 5001–6000 | 225 | 45 | 0.000 | 0.5835 | 0.4946 | 0.4997 | — | — | — | — |
| LR | 6001–7000 | **12** | **2** | 0.000 | 0.2219 | 0.3825 | 0.3541 | 0.0798 | 0.0516 | 1.0000 | 1.0000 |
| SVM | 4001–5000 | 213 | 43 | 0.000 | −0.1907 | 0.6964 | **0.7913** | 0.2500 | **0.4167** | 1.0000 | 1.0000 |
| SVM | 5001–6000 | 225 | 45 | 0.000 | 0.0244 | 0.4972 | 0.4977 | — | — | — | — |
| SVM | 6001–7000 | **12** | **2** | 0.000 | −0.5853 | 0.3685 | **0.7694** | 0.0657 | **0.6009** | 1.0000 | 1.0000 |

Confusion matrices (rows Ham, Spam; default → selected):

- LR 4001: `[[618, 0], [9, 3]]` → `[[618, 0], [10, 2]]`.
- LR 5001: `[[970, 21], [0, 0]]` → `[[990, 1], [0, 0]]` — false positives fall from 21 to 1.
- LR 6001: `[[158, 0], [196, 17]]` → `[[158, 0], [202, 11]]` — recall falls.
- SVM 4001: `[[618, 0], [9, 3]]` → `[[618, 0], [7, 5]]`.
- SVM 5001: `[[980, 11], [0, 0]]` → `[[982, 9], [0, 0]]`.
- SVM 6001: `[[158, 0], [199, 14]]` → `[[158, 0], [85, 128]]` — recall rises from 6.6% to 60.1%, with zero false positives.

The SVM result is the strongest evidence that block-6001 recall is partly a **threshold/calibration** problem: the ranking already places many Spam above most Ham (PR-AUC 0.980), but the default boundary sits above the Spam mass. Lowering it recovers 128 of 213 Spam without a false positive.

LR shows the opposite response despite a similar PR-AUC (0.980): its inner validation has only 2 Spam, and the selected threshold (0.222) is too high for the held-out block, so recall falls. The model-specific difference is itself evidence that the choice is not stable.

## 4. Threshold stability — 20 inner splits per fold

| Model | Fold | Threshold mean ± SD (range) | Held Macro-F1 mean ± SD | Held recall mean ± SD | Held precision mean | Share of splits improving on default Macro-F1 |
|---|---|---|---|---|---|---|
| LR | 4001 | 0.4895 ± 0.0491 (0.3949–0.6230) | 0.6417 ± 0.0129 | 0.1708 ± 0.0186 | 1.0000 | 0% |
| LR | 5001 | 0.5032 ± 0.0531 (0.4098–0.6111) | 0.4996 ± 0.0002 | — | — | 100% (FP 21→~1) |
| LR | 6001 | 0.2534 ± 0.0577 (0.1698–0.4283) | 0.3536 ± 0.0035 | 0.0512 ± 0.0034 | 1.0000 | 0% |
| SVM | 4001 | −0.1033 ± 0.0648 (−0.2149–0.0278) | 0.7554 ± 0.0240 | 0.3500 ± 0.0436 | 1.0000 | 95% |
| SVM | 5001 | −0.0631 ± 0.0671 (−0.1830–0.0598) | 0.4949 ± 0.0032 | — | — | 20% |
| SVM | 6001 | −0.4972 ± 0.1052 (−0.6753–−0.3152) | 0.6640 ± 0.1111 | **0.4434 ± 0.1679** | 0.9994 | **100%** |

The SVM-6001 threshold is consistently beneficial in direction but **not stable in value**: the selected threshold ranges from −0.675 to −0.315, and held-out recall is 44.3% ± 16.8. With only two Spam rows in the inner validation split, there is no reliable way to choose a precise operating point. The honest conclusion is that a lower threshold can recover much of the missing recall, but the exact calibration cannot be trusted from 12 training Spam.

LR-5001 is a real specificity gain (21 false positives to about 1) with no Spam present; it does not establish Spam recall. LR-6001 calibration fails.

## 5. MuRIL block-6001 — not a threshold problem

MuRIL block folds were not saved as models, and the saved held-out probabilities can be analysed but not used to select a threshold. More importantly, their scores are degenerate:

| Seed | Held-out block | Spam score min / median / max | Ham score median / max | PR-AUC | ROC-AUC |
|---|---|---|---|---|---|
| 42 | 6001–7000 | 0.1081 / 0.1081 / 0.1083 | 0.1081 / 0.1086 | 0.5976 | 0.5423 |
| 43 | 6001–7000 | 0.2980 / 0.2980 / 0.2980 | 0.2980 / 0.2990 | 0.5378 | 0.3962 |
| 44 | 6001–7000 | 0.2920 / 0.2920 / 0.2930 | 0.2920 / 0.2950 | 0.5758 | 0.5125 |

Every Spam message in each seed receives essentially the same probability as every Ham message. The score distributions are separated by less than 0.004. Consequently:

- A threshold below ≈0.108 (seed 42) labels **all 371 rows Spam**: recall 100%, precision 57.4%, 158 false positives, and a macro-F1 around 0.36.
- A threshold above ≈0.109 labels **all 371 rows Ham**: recall 0%, macro-F1 0.299.
- There is no intermediate operating point, because there are no intermediate scores.

Transferring the seed-42 random-validation threshold (0.466) to block 6001 also predicts every row Ham (`[[158, 0], [213, 0]]`). The failure is **representation/source shift**, not a boundary placed slightly too high. The PR-AUC is near the 0.574 Spam prevalence, consistent with no usable ranking.

The same pattern explains the other MuRIL folds: block 4001 has usable spread (PR-AUC 0.845, ROC 0.996) and 58–83% recall after thresholding; block 6001 has none.

## 6. Interpretation

- **Classical models:** block-6001 *ranking* is strong (PR-AUC ≈ 0.980) but the default decision boundary is badly placed for the held-out source. A validation-selected threshold can raise SVM recall from 6.6% to 60.1% at 100% precision in the primary split. However, the threshold varies widely across inner splits and the LR variant fails. **The cause is partly threshold miscalibration, but it cannot be fixed reliably with 12 training Spam and no target-source validation.**
- **MuRIL:** the failure is not threshold-related. Its probabilities collapse to a constant for the held-out block, so no threshold can separate Spam from Ham. This is source/representation failure.
- **Do not deploy a block-6001-specific threshold.** It would be selected on the held-out source, which is exactly the leakage this project forbids. A real deployment must calibrate on messages from the target source before use, and must report the calibration sample size.
- **Primary results remain at the default thresholds** so that all models are compared under the same pre-specified rule. Threshold-calibrated numbers are a sensitivity analysis, not a replacement headline.

## 7. Artifacts

| Path | Contents |
|---|---|
| `p2_threshold.py` | threshold selection, stability, MuRIL diagnosis, figures |
| `metrics/threshold_calibration.json` | all selected thresholds, metrics, stability, sweeps |
| `metrics/threshold_calibration.csv` | flat default/selected summary |
| `metrics/threshold_calibration_splits.csv` | all 120 inner-split results |
| `reports/threshold_tables.md` | machine-generated tables |
| `reports/figures/pr_random_d1.png` | random-test PR curves |
| `reports/figures/pr_block6001.png` | block-6001 PR curves |
| `reports/figures/scores_block6001.png` | score distributions by true class |

*All values generated from frozen predictions and the fixed inner splits. No held-out label was used to select a threshold.*
