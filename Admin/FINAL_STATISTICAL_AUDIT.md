# Final Statistical Audit

**Date:** 8 November 2026  
**Inputs:** frozen D1/D2 prediction CSVs, frozen test manifests, split manifests, saved block predictions.  
**Independent script:** `Research Work/phase2/p2_final_audit_stats.py`  
**Machine output:** `Research Work/phase2/metrics/final_audit_stats.json`

---

## 1. Executive summary

1. The historical LR–SVM interval contradiction is a **direction/interval mismatch**, not a bug in the bootstrap. The saved paired file computes **LR − SVM**; the report displayed the **SVM − LR** point estimate beside the **LR − SVM** interval.
2. Correct results: **LR − SVM = −0.0093601 [−0.0321432, 0]**, and therefore **SVM − LR = +0.0093601 [0, +0.0321432]**. The observed difference is inside its interval.
3. The difference is **one test message**. Exact two-sided discordance p = 1.0. There is no statistical evidence that SVM is better than LR.
4. The MuRIL mean is not statistically distinguishable from SVM: **+0.0031200 [0, 0.0101002]**. Seeds 42 and 44 produce predictions identical to SVM; seed 43 is one Spam false negative worse. The seeds are not three independent comparisons.
5. Perfect precision is real in the frozen test set but fragile: 30/30 and 29/29, exact lower bounds 0.8843 and 0.8806; zero FP among 265 Ham gives an exact upper FPR bound of 1.382%.
6. The group bootstrap is numerically a message bootstrap because every frozen test group is a singleton. It does not represent source-population uncertainty.
7. The row-block result is a **pooled leave-one-row-block-out stress test**, not source-held-out validation.

## 2. LR–SVM paired comparison

### 2.1 Source definition

`p2_stats.py` defines the paired difference as `A − B`. In `paired_model_comparison.json`, the D1 LR/SVM entry is:

- `a_model = Logistic Regression`
- `b_model = Linear SVM`
- `difference = −0.009360118526741346`
- `ci_low = −0.03214315072560611`
- `ci_high = 0.0`

Therefore the file is **LR − SVM**, not SVM − LR. The report `FINAL_MODEL_SELECTION.corrected.md` printed `SVM vs LR: +0.0094 [−0.0321, 0.0000]`, taking the sign from one direction and the interval from the other. That is the source of the apparent “point outside interval” contradiction.

### 2.2 Independent recomputation

`p2_final_audit_stats.py` independently rebuilds the 299 test rows, encodes labels in fixed order, creates 2,000 group resamples with seed 42, and applies the **same resample** to both models. It obtains:

| Quantity | LR − SVM | SVM − LR |
|---|---:|---:|
| Observed Macro-F1 difference | −0.0093601185 | +0.0093601185 |
| 95% percentile interval | [−0.0321431507, 0.0000000000] | [0.0000000000, 0.0321431507] |
| Bootstrap mean | −0.0094708859 | +0.0094708859 |
| Bootstrap median | −0.0088672652 | +0.0088672652 |
| Bootstrap SD | 0.0095022675 | 0.0095022675 |
| Share of draws > 0 | 0.0000 | 0.6315 |
| Share of draws exactly 0 | 0.3685 | 0.3685 |
| Share of draws < 0 | 0.6315 | 0.0000 |

The distribution is discrete. The models disagree on exactly one message: LR wrong / SVM right. If a bootstrap resample contains that message, LR is worse; if it does not, the two models tie exactly. It can never be better. Thus no positive replicate exists, 36.85% of replicates tie, and the percentile lower bound for SVM − LR is exactly zero. This is correct percentile behaviour, not a biased interval.

### 2.3 Other metrics and exact discordance

| Metric | LR − SVM | SVM − LR |
|---|---:|---:|
| Spam recall | −0.0294118 [−0.0975610, 0] | +0.0294118 [0, 0.0975610] |
| Accuracy | −0.0033445 [−0.0100334, 0] | +0.0033445 [0, 0.0100334] |

Discordant pairs: 1. Exact two-sided McNemar/binomial p = 1.0. Reporting a “significant” SVM advantage from this is indefensible.

### 2.4 Correct interpretation

> Linear SVM and Logistic Regression are statistically indistinguishable on the frozen D1 test. SVM is one message better on Macro-F1 and Spam recall, and that single message is the entire observed difference. Model selection may prefer SVM for deterministic simplicity, but not because it is proven more accurate.

## 3. SVM–MuRIL paired comparison

### 3.1 Estimand

The MuRIL estimand is the **mean of the three seed metrics**, not a majority vote of the three seed predictions. The audit computes, on each shared resample, the metric for each seed and then averages the three metrics. This matches the reported 0.9619 mean.

### 3.2 Results

| Metric | SVM | MuRIL mean | SVM − MuRIL mean | 95% interval | Includes 0? |
|---|---:|---:|---:|---|---|
| Macro-F1 | 0.9650047 | 0.9618846 | +0.0031200 | [0.0000, 0.0101002] | Yes |
| Accuracy | 0.9866221 | 0.9855072 | +0.0011148 | [0.0000, 0.0033445] | Yes |
| Spam recall | 0.8823529 | 0.8725490 | +0.0098039 | [0.0000, 0.0303030] | Yes |

The Macro-F1 interval has 69.45% positive draws, 23.80% exact ties and 6.75% negative draws. The lower bound is numerically −1.11×10⁻¹⁶ and should be reported as 0.0000.

### 3.3 Seed dependence

- Seed 42 predictions are identical to SVM.
- Seed 44 predictions are identical to SVM.
- Seed 43 is one Spam false negative worse than SVM.

Therefore two of three seeds are not independent evidence of transformer performance; they reproduce the SVM exactly. The seed 43 comparison is one message. The “three seeds” provide a stability check, not three independent replications of a transformer advantage.

### 3.4 Across-seed versus test-sample uncertainty

| Quantity | Value | Meaning |
|---|---|---|
| Across-seed Macro-F1 SD | 0.0054 | Variation among three fitted seeds only |
| Conditional three-seed mean interval | [0.9211, 0.9909] | Test-sample uncertainty for the average of these three frozen predictions |
| Bootstrap SD for MuRIL mean | ~0.0181 | Test-sample uncertainty, not training-run variance |

The interval [0.9211, 0.9909] is **not** an expected-performance interval for a future training run. Three seeds cannot estimate that. The correct statement is: “conditional on seeds 42/43/44, the average prediction has this test-sample interval.”

## 4. Perfect precision and zero false positives

### 4.1 Observed values

| Model | TP | FP | Predicted Spam | Precision | Exact 95% CP | Wilson 95% |
|---|---:|---:|---:|---:|---|---|
| LR | 29 | 0 | 29 | 1.000 | [0.8806, 1.0000] | [0.8830, 1.0000] |
| SVM | 30 | 0 | 30 | 1.000 | [0.8843, 1.0000] | [0.8865, 1.0000] |
| MuRIL 42/44 | 30 | 0 | 30 | 1.000 | [0.8843, 1.0000] | [0.8865, 1.0000] |
| MuRIL 43 | 29 | 0 | 29 | 1.000 | [0.8806, 1.0000] | [0.8830, 1.0000] |

The exact interval is one-sided in effect at the boundary: it does not say precision is certainly 1.0. It says the data are compatible with true precision as low as ~88%.

### 4.2 False-positive rate

Zero false positives among 265 Ham:

- Exact 95% upper bound: \(1 - 0.025^{1/265} = 0.01382386\) = **1.382%**.
- Wilson 95% upper bound: **1.429%**.
- The old “3/299 ≈ 1.0%” used the wrong denominator. The denominator for FPR is Ham, not all test rows.

### 4.3 Why this is not deployment safety

1. The precision interval is conditional on the 29–30 messages the model chose to call Spam. A different threshold or prevalence changes the denominator.
2. All or nearly all predicted Spam are in block 6001–7000. The observation is campaign-concentrated.
3. The 265 Ham are not a random sample of future Ham; they share corpus construction.
4. Errors may be dependent within campaigns/templates, so the binomial exchangeability assumption is optimistic.
5. A 1.382% upper bound is not zero risk; at SMS scale it is material.

**Permitted:** “Observed precision was 1.00 (30/30; exact 95% lower bound 0.8843), with 0/265 Ham false positives (exact 95% upper FPR bound 1.382%). This is a within-corpus observation, not a deployment guarantee.”

## 5. Bootstrap methodology

### 5.1 Verified procedure

- 2,000 replicates, seed 42.
- Resampling unit: duplicate group.
- D1 test: 299 rows / 299 groups / max group size 1.
- D2 test: 883 rows / 883 groups / max group size 1.
- Shared resample for all models in a paired comparison.
- Percentile limits 2.5% / 97.5%.
- Fixed label order; Macro-F1 uses the unweighted mean over the fixed class set.
- `zero_division=0` for undefined precision/recall.
- No replicate lost Spam in D1 or D2.

### 5.2 What the interval means

Because every test group is a singleton, the bootstrap is **numerically message-level**. It captures sampling variability of messages from the same frozen test set. It does **not** capture:

- variation across collection sources;
- campaign or template clustering beyond exact duplicates;
- temporal drift;
- annotation uncertainty;
- model-selection uncertainty.

The grouped implementation is still correct and necessary for generality, but the user must not describe it as a source-cluster bootstrap.

### 5.3 Discrete boundary behaviour

At perfect precision, the bootstrap distribution can have a large point mass at 1.0. At a one-message paired difference, it can have a large mass at 0.0. Percentile intervals are still valid descriptive intervals, but they are discrete and can have a bound exactly at the observed value. This is why the LR–SVM interval ends at 0 rather than crossing it.

## 6. Row-block methodology

### 6.1 Correct membership

Block definition: `(source_row - 1) // 1000 + 1`, using the Excel row number.

| Block | Records | Ham | Spam |
|---|---:|---:|---:|
| 4001–5000 | 630 | 618 | 12 |
| 5001–6000 | 991 | 991 | 0 |
| 6001–7000 | 371 | 158 | 213 |

The old 631/370 counts are stale. The block is a row-order proxy, not a verified source.

### 6.2 Pooled results

| Model | Accuracy | Macro-F1 | Spam precision | Spam recall | CM |
|---|---:|---:|---:|---:|---|
| LR | 0.8865 | 0.5448 | 0.4878 | 0.0889 | [[1746,21],[205,20]] |
| SVM | 0.8901 | 0.5378 | 0.6071 | 0.0756 | [[1756,11],[208,17]] |
| MuRIL 42 | 0.8845 | 0.4979 | 0.3684 | 0.0311 | [[1755,12],[218,7]] |
| MuRIL 43 | 0.8896 | 0.5006 | 0.7778 | 0.0311 | [[1765,2],[218,7]] |
| MuRIL 44 | 0.8855 | 0.5098 | 0.4348 | 0.0444 | [[1754,13],[215,10]] |

Pooled means: LR 0.5448, SVM 0.5378, MuRIL 0.5028. Spam recall 8.89%, 7.56%, 3.56%.

### 6.3 Interpretation

- The random split shares block 6001–7000, which contains 213/225 Spam, between train and test.
- Holding out 6001 leaves only 12 Spam in training; all models collapse on its 213 Spam.
- The 5001 fold has no Spam; its per-fold Macro-F1 is an absent-class artefact and should not be averaged as if balanced.
- The pooled calculation concatenates held-out predictions and computes one metric; it is not the mean of unstable fold scores.
- LR and SVM pooled difference is +0.00695 [−0.00425, 0.02170], which includes zero. Do not claim LR is better under block holdout.
- This is a **three-block stress test**. It does not estimate performance on “unseen real-world sources” and does not prove the cause of the row-order association.

## 7. Script composition and structural confounds

### 7.1 Composition

| Script category | Ham | Spam | Total | Spam rate |
|---|---:|---:|---:|---:|
| Malayalam-only script | 1,429 | 60 | 1,489 | 4.03% |
| Malayalam + Latin | 338 | 165 | 503 | 32.80% |
| Total | 1,767 | 225 | 1,992 | 11.30% |

The association is substantial: mixed-script messages are about eight times more likely to be Spam in this corpus. This does **not** establish that Latin characters cause Spam. Script mix may proxy campaign, sender, content type or collection route.

### 7.2 Structure-only diagnostics

From the saved `validation_summary.json`, with arithmetic checked against the saved confusion matrices:

| Diagnostic | Macro-F1 | Accuracy | Spam P/R | CM |
|---|---:|---:|---|---|
| Structure only (length, digits, URL, Latin, script) | 0.8706 | 0.9465 | 0.7500 / 0.7941 | [[256,9],[7,27]] |
| Block identity only | 0.8423 | 0.9231 | 0.6078 / 0.9118 | [[245,20],[3,31]] |
| Structure + block | 0.9009 | 0.9565 | 0.7561 / 0.9118 | [[255,10],[3,31]] |

These are **leakage diagnostics**, not competing classifiers. They show that metadata and row order carry substantial label information. They do not prove that the text model is “really” learning only metadata. The text models outperform them, but the margin is not a clean estimate of linguistic learning.

No structural model was refitted in this audit. Refitting would be a new experiment and would not change the frozen text-model results.

### 7.3 What can be concluded

Supported:

- Script mix, message length, URL/digit presence and block membership are associated with the label.
- A no-text model can achieve a high random-split score.
- The random-split score cannot be interpreted as purely linguistic generalisation.

Not supported:

- “The model learned nothing but metadata.”
- “Latin characters cause spam.”
- “Row block is the collection source.”
- “The corpus is fraudulent.”

## 8. D2 statistics

D2 LR Macro-F1 0.8877 [0.8482, 0.9239]; SVM 0.8825 [0.8408, 0.9196]. Paired LR − SVM = +0.0052393 [−0.0120572, 0.0244165]; interval includes zero. D2 Spam/Smishing confusion remains: LR Smishing F1 0.8706, Spam F1 0.8029; SVM Smishing F1 0.8810, Spam F1 0.7761. D2 is English/Latin only and is not external validation for D1.

## 9. Statistical claims that must be removed

- “SVM significantly outperforms LR.”
- “MuRIL is worse than SVM” as a population claim.
- “100% precision” without the exact lower bound.
- “Zero false positives” without the 1.382% upper bound and campaign caveat.
- “The bootstrap shows uncertainty across sources.”
- “The block test proves failure on unseen sources.”
- “The three seeds are three independent validations.”
- Any p-value or interval not traceable to `final_audit_stats.json` or `final_verification.json`.

## 10. Final statistical verdict

The arithmetic is reproducible and the paired comparisons are correctly implemented. The substantive statistical conclusion is **not** that one model wins. It is that:

1. All models achieve high within-corpus random-split scores.
2. LR, SVM and MuRIL are not reliably separated at this sample size.
3. The measured performance collapses under a row-block stress test.
4. Perfect precision is a fragile, campaign-concentrated observation.
5. The corpus’s row-order and script composition are serious confounds that the paper must report, not hide.

That is a defensible, if less flattering, result.
