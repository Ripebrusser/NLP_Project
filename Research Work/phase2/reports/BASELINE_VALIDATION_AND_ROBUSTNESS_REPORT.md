# Baseline Validation and Robustness Report

**Phase:** 2.1 — validation of the Phase 2 classical baselines
**Date:** 5 November 2026
**Scope:** Dataset 1 (Malayalam-script SMS, Ham vs Spam) primary; Dataset 2 (English SMS, Ham/Spam/Smishing) secondary
**Status:** validation complete. No transformer was trained, no hyperparameter search was extended, no synthetic data was created, and the original datasets were not modified.

All numbers below are produced by `Research Work/phase2/p2_validate.py` from the frozen Phase 2 artifacts. The machine-generated tables are in `reports/baseline_validation_tables.md`; the full JSON is `metrics/validation_summary.json`.

---

## 1. What was verified

| Check | Result |
|---|---|
| D1 Logistic Regression model present and loadable | Yes — `d1_malayalam_logreg.joblib` |
| D1 Linear SVM model present and loadable | Yes — `d1_malayalam_linear_svm.joblib` |
| D2 Logistic Regression model present and loadable | Yes — `d2_logreg.joblib` |
| D2 Linear SVM model present and loadable | Yes — `d2_linear_svm.joblib` |
| Saved test predictions reproduce exactly | Yes for all four models |
| Recorded accuracy reproduces from the loaded pipeline | Yes for all four models (difference < 1e-12) |
| Split files match the hashes in `split_manifest.json` | Yes (rechecked after the manifest fix, §3.3) |
| Group/normalised overlap between splits | 0 in every pair, both datasets |

No missing experiment had to be run. The four Phase 2 models were reused unchanged.

### Consolidated model comparison

**Dataset 1 — Ham vs Spam** (test n = 299; 265 Ham / 34 Spam)

| Model | Features | C | Val macro-F1 | Accuracy | Precision (macro) | Recall (macro) | Macro-F1 | Per-class F1 | Errors |
|---|---|---|---|---|---|---|---|---|---|
| Linear SVM | TF-IDF char_wb 2–4, min_df 2, sublinear, class-weighted | 0.5 | 0.9830 | 0.9866 | 0.9926 | 0.9412 | **0.9650** | Ham 0.993 / Spam 0.938 | 4 |
| Logistic Regression | same vectoriser | 1.0 | 0.9748 | 0.9833 | 0.9907 | 0.9265 | 0.9556 | Ham 0.991 / Spam 0.921 | 5 |

Both models were selected on validation macro-F1 only, refit on train+validation, and evaluated once on test. SVM confusion matrix: `[[265, 0], [4, 30]]` (rows Ham, Spam). LR: `[[265, 0], [5, 29]]`.

**Dataset 2 — Ham / Spam / Smishing** (test n = 883; 726 / 67 / 90)

| Model | Features | C | Val macro-F1 | Accuracy | Precision (macro) | Recall (macro) | Macro-F1 | Per-class F1 | Errors |
|---|---|---|---|---|---|---|---|---|---|
| Logistic Regression | TF-IDF char_wb 2–4, min_df 2, sublinear, class-weighted | 1.0 | 0.9048 | 0.9638 | 0.8986 | 0.8792 | **0.8877** | Ham 0.990 / Spam 0.803 / Smishing 0.871 | 32 |
| Linear SVM | same vectoriser | 0.5 | 0.9030 | 0.9638 | 0.9024 | 0.8657 | 0.8825 | Ham 0.990 / Spam 0.776 / Smishing 0.881 | 32 |

Training configuration for every model: word/char TF-IDF with `min_df=2`, `sublinear_tf=True`, `max_features=300,000`, `class_weight="balanced"`, `max_iter` 5,000 (LR) or 10,000 (SVM). Four TF-IDF configurations and C ∈ {0.5, 1.0, 2.0} were compared on validation only; the full grids are preserved in `metrics/*_validation_grid.csv`.

D2 and D1 are separate experiments with different label spaces; their scores are **not** pooled or compared as if they measured the same task.

---

## 2. Dataset 1 source-block audit

### 2.1 Blocks and class distribution

D1's Malayalam records occupy source rows **4146–6371**, inside three 1,000-row blocks. `source_row` is the Excel row number (header = row 1).

| Source rows | n | Ham | Spam | Spam rate | Malayalam-only | Latin also | Mean chars | Spam median chars | URL rate | Digit rate |
|---|---|---|---|---|---|---|---|---|---|---|
| 4001–5000 | 630 | 618 | 12 | 1.9% | 570 | 60 | 129.3 | 174.5 | 0.16% | 4.4% |
| 5001–6000 | 991 | 991 | 0 | 0.0% | 739 | 252 | 96.7 | — | 0.00% | 7.8% |
| 6001–7000 | 371 | 158 | 213 | **57.4%** | 180 | 191 | 100.5 | 138.0 | 17.3% | 52.3% |

There are no Malayalam records before row 4146 or after row 6371. **94.7% of all Spam (213/225) sits in block 6001–7000.** Block 5001–6000 contains no Spam at all.

> **Block definition correction.** Phase 2's `p2_robustness.py` derived blocks with `((source_row-1)-1)//1000+1`, which labelled its blocks one row low (its "4001–5000" actually held source rows 4002–5001). Phase 2.1 uses `(source_row-1)//1000+1`. The membership change is two Ham rows (source rows 5001 and 6001), so counts move from 631/991/370 to 630/991/371. All results in this report use the corrected definition; the effect on the SVM fold scores is at most 0.0008 macro-F1.

### 2.2 Labels follow source order, not message content

Sorted by source row, the 1,992 Malayalam records form only **13 label runs** where about 400 would be expected if labels were independent of position (runs test z = **−43.2**). The probability that the next Malayalam record has the same label as the previous one is **0.9935**.

The run structure is:

| Run | Source rows | n |
|---|---|---|
| Ham | 4146 | 1 |
| Spam bursts interleaved with Ham | 4371–4395 | 3, 1, 2, 3 |
| Ham | 4396–4454 | 58 |
| Spam | 4455–4456 | 2 |
| Ham | 4457–4486 | 30 |
| Spam | 4487 | 1 |
| **Ham** | **4488–6158** | **1,662** |
| **Spam** | **6159–6371** | **213** |

At 100-row resolution, 17 of the 22 populated bins are 100% Ham, 2 are 100% Spam (6201–6300 and 6301–6400), and 3 are mixed. The transition at rows 6158/6159 is abrupt and complete. This is the footprint of contiguous collection batches, not of messages independently sampled from one population.

Block explains a large share of label variance: χ²(2) = 969.15, p < 0.001, **Cramér's V = 0.6975**. A rule that predicts the majority label of each block, with no text at all, reaches **91.5% accuracy and 0.832 macro-F1** on the full corpus (0.923 / 0.842 on the frozen random test). That is the floor any text model must beat to demonstrate linguistic learning rather than batch recognition.

### 2.3 Length and formatting differ by block

| Block | Mean chars | Ham median chars | Spam median chars | URL rate (Ham / Spam) | Digit rate (Ham / Spam) | Latin rate (Ham / Spam) |
|---|---|---|---|---|---|---|
| 4001–5000 | 129.3 | 124 | 174.5 | 0.0% / 8.3% | 2.6% / 100% | 7.9% / 91.7% |
| 5001–6000 | 96.7 | — | — | 0.0% / — | 7.8% / — | 25.4% / — |
| 6001–7000 | 100.5 | — | 138.0 | 23.4% / 30.0% | — / 84.5% | 23.4% / 72.3% |

The two spam populations are formatted differently: the 12 spam in block 4001–5000 are long (median 174.5 characters), almost all contain Latin and digits, but few contain URLs; the 213 spam in block 6001–7000 are shorter (median 138), with a 30% URL rate and 84.5% digit rate.

Formatting alone is highly predictive. A logistic regression using **only** length, token count, digit count, URL presence, Latin presence and Malayalam-only status — no words, no characters, no block ID — reaches **0.9465 accuracy and 0.8706 macro-F1** on the random test (Spam P 0.750, R 0.794). Adding block identity raises it to **0.9009 macro-F1**. The full text model reaches 0.9650. Most of the headline score is therefore recoverable from non-linguistic metadata correlated with the batch.

### 2.4 Vocabulary and character patterns differ by block

| Pair | Token Jaccard | Char-trigram JS divergence |
|---|---|---|
| 4001–5000 vs 5001–6000 | 0.352 | 0.110 |
| 4001–5000 vs 6001–7000 | 0.217 | 0.390 |
| 5001–6000 vs 6001–7000 | 0.207 | 0.368 |

The two spam populations are lexically almost unrelated: the cosine between their char-TF-IDF centroids is **0.282**. Block 6001–7000's distinctive tokens include Latin fragments such as `in` and `com`, consistent with operator/product names and URLs; blocks 4001–5000 and 5001–6000 are dominated by Malayalam literary vocabulary. A model trained on one spam "dialect" has little lexical basis for recognising the other.

### 2.5 Templates and source artefacts

Normalising URLs and digits leaves 1,867 distinct message skeletons. **1,839 of them (98.5%) occur in only one block**, covering 1,924 records (96.6%). The most frequent skeleton in each block is label-pure:

- block 4001–5000: 3 records, 0 Spam (a personal message);
- block 5001–6000: 3 records, 0 Spam (a film/music message);
- block 6001–7000: 4 records, 4 Spam (a cricket/DTH promotion), 4/4 Spam (a Tamil combo pack offer), 3/3 Spam (an Airtel DTH offer).

Skeleton confinement is partly a consequence of near-unique SMS text, so it is descriptive rather than causal. But together with the formatting result and the label runs, it shows that label-correlated collection artefacts are present and strong.

### 2.6 Conclusion of the block audit

D1 is not a random sample of Malayalam SMS. It is a concatenation of at least three source batches, one of which supplies 213 of the 225 Spam messages and is separated from the preceding 1,662-message Ham run at a single row boundary. Message length, script mixing, URL/digit usage and vocabulary all shift at the same boundaries. **Row position and source batch predict the label to a degree that makes a random row split unable to distinguish linguistic learning from batch memorisation.**

---

## 3. Block-held-out validation

Design: for each source block, train on the other two blocks and test on the held-out block. No validation split, no threshold tuning and no test-time adaptation. Model configuration and C are exactly those selected in Phase 2 on the random validation split, so the folds are not tuned.

### 3.1 Per-fold results (corrected block boundaries)

| Model | Held-out rows | Train n | Train Spam | Test n | Test Ham | Test Spam | Accuracy | Macro-F1 | Spam P | Spam R | Spam PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LR | 4001–5000 | 1,362 | 213 | 630 | 618 | 12 | 0.9857 | 0.6964 | 1.000 | 0.250 | 0.633 |
| LR | 5001–6000 | 1,001 | 225 | 991 | 991 | **0** | 0.9788 | 0.4946* | — | — | — |
| LR | 6001–7000 | 1,621 | **12** | 371 | 158 | 213 | 0.4717 | 0.3825 | 1.000 | 0.080 | 0.980 |
| SVM | 4001–5000 | 1,362 | 213 | 630 | 618 | 12 | 0.9857 | 0.6964 | 1.000 | 0.250 | 0.635 |
| SVM | 5001–6000 | 1,001 | 225 | 991 | 991 | **0** | 0.9889 | 0.4972* | — | — | — |
| SVM | 6001–7000 | 1,621 | **12** | 371 | 158 | 213 | 0.4636 | 0.3685 | 1.000 | 0.066 | 0.980 |

\* The macro-F1 for the block with no Spam is **not a balanced performance estimate**. Spam F1 is undefined with zero support; `sklearn` assigns 0, which halves the macro average. The macro-F1 over classes actually present is **0.9893 (LR) / 0.9944 (SVM)**; Spam precision and recall are undefined and are reported as "—". The 11–21 Ham messages predicted as Spam in that fold are the real error signal.

Confusion matrices (rows Ham, Spam):

- block 4001–5000: LR `[[618, 0], [9, 3]]`; SVM `[[618, 0], [9, 3]]`
- block 5001–6000: LR `[[970, 21], [0, 0]]`; SVM `[[980, 11], [0, 0]]`
- block 6001–7000: LR `[[158, 0], [196, 17]]`; SVM `[[158, 0], [199, 14]]`

The last fold is the clearest failure: when the 213-message spam batch is held out, the model has only 12 spam messages to learn from and recovers **6.6–8.0%** of held-out Spam. Its PR-AUC of 0.980 shows the *ranking* is good — most spam score above most ham — but the decision threshold learned from 12 examples is badly placed, so almost everything is predicted Ham. This is a calibration failure on top of a representation problem, and it cannot be fixed by tuning on the held-out block.

### 3.2 Pooled result

| Model | Evaluation | Accuracy | Macro-F1 | Spam P | Spam R |
|---|---|---|---|---|---|
| Logistic Regression | random grouped split (all blocks in every split) | 0.9833 | 0.9556 | 1.000 | 0.853 |
| Logistic Regression | pooled leave-one-block-out | 0.8865 | 0.5448 | 0.488 | 0.089 |
| Linear SVM | random grouped split (all blocks in every split) | **0.9866** | **0.9650** | 1.000 | 0.882 |
| Linear SVM | pooled leave-one-block-out | 0.8901 | **0.5378** | 0.607 | 0.076 |

Pooled block-held-out confusion matrix (SVM): `[[1756, 11], [208, 17]]`; LR: `[[1746, 21], [205, 20]]`.

### 3.3 Why the random split and block-held-out results differ

The random split is grouped with respect to duplicates but random with respect to collection batch. Consequently **every split contains all three blocks**:

| Split | Rows from 4001–5000 | Rows from 5001–6000 | Rows from 6001–7000 | Spam from 6001–7000 |
|---|---|---|---|---|
| Train | 457 (450 H / 7 S) | 679 | 258 (108 H / 150 S) | 150 / 157 = **95.5%** |
| Validation | 84 | 153 | 62 (30 H / 32 S) | 32 / 34 = 94.1% |
| Test | 89 (86 H / 3 S) | 159 | 51 (20 H / 31 S) | 31 / 34 = **91.2%** |

The random test is therefore mostly a **within-batch** test: 91.2% of its Spam comes from the same block that supplied 95.5% of training Spam. A char n-gram model can memorise that batch's vocabulary, offer wording and formatting and score highly without learning transferable Malayalam spam cues. The no-text structural model reaching 0.871 macro-F1 confirms that much of this signal is metadata.

Block-held-out evaluation removes the batch. It then faces one of two impossible situations:

1. **Block 6001–7000 held out:** only 12 Spam remain for training. No model can learn or calibrate a spam boundary from 12 examples, especially when the held-out spam has different vocabulary (centroid cosine 0.282 to the other spam block).
2. **Block 4001–5000 held out:** training spam comes entirely from block 6001–7000, a different spam dialect. Recall on the 12 held-out spam is 25%.
3. **Block 5001–6000 held out:** there is no Spam to detect. Only false positives are measurable.

The gap (0.965 random vs 0.538 pooled block-held-out) is therefore not a bug in either protocol. It measures the difference between interpolating within a batch and transferring across batches, and the latter is what deployment would require.

---

## 4. Is a scientifically valid source-aware evaluation possible?

**Partially, and only as a stress test.** The corpus contains three source blocks, but only two contain Spam, and one of those contains 94.7% of all Spam. Leave-one-block-out is the correct source-aware design for this data, and it is reproducible, but it is severely underpowered: the training set either lacks a usable spam sample (12 examples) or lacks the spam dialect being tested.

What can legitimately be claimed:

- **Within-source performance:** the grouped random split estimates performance on new messages from the same collection batches. This is a valid but narrow claim, and it must be labelled as such.
- **Cross-source stress performance:** pooled leave-one-block-out is a conservative lower bound under batch shift. It is valid as a stress test, not as an estimate of real-world accuracy.
- **No protocol in this project can estimate performance on genuinely new Malayalam SMS sources.** That requires an independently collected external test set, which the project is not permitted to create.

Recommended evaluation protocol for the transformer phase and the final report:

1. **Keep the frozen grouped split** (`splits/`, seed 42) for comparability with the baselines. Call it "within-source" and never present it as generalisation to new sources.
2. **Run leave-one-source-block-out as a mandatory secondary protocol** with the same pipeline and no per-fold tuning. Report every fold and the pooled result; never average folds silently.
3. **Report both numbers side by side** and treat them as an upper and lower bound, not as one point estimate. The honest headline is a range with the batch caveat.
4. **Do not tune thresholds or hyperparameters on the held-out block.** If threshold calibration is studied, calibrate on a separate within-training batch and say so.
5. **Never create a new split to improve the score**, and never merge Spam with Smishing or with Ham.
6. **Add an external corpus before any real-world claim.** Until then, the strongest defensible statement is about method behaviour on this corpus, not about Malayalam SMS spam detection in general.

---

## 5. Dataset 2 validation

### 5.1 Complete comparison

| Model | Accuracy | Macro-F1 | Ham P/R/F1 | Spam P/R/F1 | Smishing P/R/F1 |
|---|---|---|---|---|---|
| Logistic Regression | 0.9638 | **0.8877** | 0.985 / 0.994 / 0.990 | 0.786 / 0.821 / 0.803 | 0.925 / 0.822 / 0.871 |
| Linear SVM | 0.9638 | 0.8825 | 0.982 / 0.999 / 0.990 | 0.776 / 0.776 / 0.776 | 0.949 / 0.822 / 0.881 |

Confusion matrices (rows Ham, Spam, Smishing; columns the same):

- LR: `[[722, 0, 4], [10, 55, 2], [1, 15, 74]]`
- SVM: `[[725, 0, 1], [12, 52, 3], [1, 15, 74]]`

Both models make 32 errors. Error pairs (LR): smishing→spam **15**, spam→ham **10**, ham→smishing **4**, spam→smishing **2**, smishing→ham **1**. SVM: smishing→spam 15, spam→ham 12, spam→smishing 3, smishing→ham 1, ham→smishing 1.

### 5.2 Why Spam is the weakest class

1. **Smallest support.** Train: 3,391 Ham, 421 Smishing, 315 Spam. Test: 726 / 90 / 67. Spam has the fewest examples and the widest per-example variance.
2. **Spam and Smishing are nearly the same genre.** Their char-TF-IDF centroids are the most similar pair: **0.751** (ham–spam 0.695, ham–smishing 0.627). They also have almost identical surface statistics: mean length 133.9 vs 139.6 characters, URL rate 17.4% vs 15.1%, digit rate 91.6% vs 96.6%, both 100% Latin. The distinction is one of intent (fraudulent credential/account solicitation vs ordinary promotional spam), which is not reliably encoded in character n-grams.
3. **The confusion is symmetric at the boundary.** 15 Smishing messages are predicted Spam (costing Spam precision) while 10 Spam messages fall to Ham and 2 to Smishing (costing Spam recall). Spam is squeezed from both sides.
4. **Some Spam labels look like ordinary text.** The highest-margin spam→ham errors are jokes and conversational one-liners ("Do you ever notice that when you're driving…"), which carry no promotional or fraudulent cue. This is source label noise or a very broad Spam definition, not a model failure that more capacity would fix.

Merging Spam and Smishing would raise the headline macro-F1 but destroy the only distinction the dataset was chosen to study. It was not done, and it should not be done in the transformer phase.

---

## 6. Error analysis

### Dataset 1

All four SVM errors are Spam→Ham; there are zero false positives. The messages are:

- `D1-04452` (row 4455): an Onam festival greeting.
- `D1-04453` (row 4456): a second Onam greeting.
- `D1-06180` (row 6183): "മദ്യപിച്ച് വാഹനമോടിക്കരുത്" — a road-safety public-service message.
- `D1-06194` (row 6197): "* പ്രാർത്ഥന - മധുര" — a short prayer/invocation.

These are not messages a human would confidently call spam. They sit inside or immediately after the large Spam batch, which suggests batch-level labelling rather than message-level judgement. Duplicate grouping cannot detect semantic mislabelling; D1 had zero conflicting groups because the conflict is between batch labels, not between duplicate texts.

This also means the 0.882 random-split Spam recall is partly limited by label noise. The block-held-out collapse is a separate and much larger problem.

### Dataset 2

- Most costly: smishing→spam (15), e.g. "CALL to No: 86888 & claim your reward of 3 hours talk time…" and a premium-rate subscription message. Both are fraudulent in intent but use the same promotional surface form as spam.
- Second: spam→ham (10), e.g. a driving joke. The model sees no spam cue because there may be none.
- Ham is essentially solved (0.990 F1); the remaining errors are boundary cases between the two non-Ham classes.

---

## 7. Limitations

1. **One corpus, three source batches, 225 Spam messages.** No external test set is permitted, so external validity cannot be measured.
2. **The random split is within-batch.** Its 0.9866/0.9650 must always be reported as such.
3. **Block-held-out is underpowered.** Only two blocks contain Spam; one contains 94.7% of it. The pooled 0.538 macro-F1 is a lower bound under severe batch shift, not a fair estimate of the model's linguistic ability.
4. **Threshold calibration is confounded with representation** in the block-6001 fold: ranking is good (PR-AUC 0.980) but the default threshold is wrong. This report does not tune it, because tuning on the held-out block would leak.
5. **The structural model is diagnostic, not causal.** It shows that formatting carries label information; it does not prove that the text model uses only formatting.
6. **Skeleton confinement is descriptive.** Unique SMS text makes most skeletons block-specific by construction.
7. **D1 labels were not re-annotated.** The four errors suggest some Spam labels are questionable, but no manual relabelling was performed and none is claimed.
8. **D2 is English and secondary.** Its results are not comparable with D1 and are not pooled.
9. **No transformer results.** This phase deliberately stops at the classical baselines.
10. **Test sets were evaluated once.** No confidence intervals or repeated splits were added in this phase; the block folds provide the robustness evidence instead.

---

## 8. Recommendation: is Dataset 1 reliable enough for transformer experiments?

**Yes for method development and within-source benchmarking; no for generalisation or deployment claims.**

The corpus is large enough (1,992 Malayalam records) and clean enough in its duplicate structure to train and compare models. It is not a representative sample of Malayalam SMS: 213 of 225 Spam messages come from one contiguous batch, labels track row position almost perfectly, and non-linguistic formatting alone reproduces 0.871 of the 0.965 text-model macro-F1. A transformer trained on the random split will exploit the same batch cues and will probably score at least as high as the SVM; that score will not mean what it appears to mean.

Therefore:

- **Proceed with the transformer experiment only as a within-source benchmark**, using the frozen split, and report the block-held-out folds alongside it.
- **Do not claim transformer superiority over the baselines on generalisation** unless the advantage survives the block-held-out protocol.
- **Do not claim real-world Malayalam SMS spam performance at all.** That requires an independently collected, source-diverse test set.
- **Report a range, not a point estimate:** random grouped split as the optimistic within-source bound, pooled block-held-out as the conservative cross-batch bound.
- **Before any publication claim, resolve B1 (D1 access provenance)** and consider adding an external corpus. The block confound is a property of the data, not something a better model can remove.

If the project requires a generalisation claim and no external corpus can be obtained, the honest conclusion is that D1 supports a **case study**, not a benchmark.

---

## 9. Reproducibility and changes to prior artifacts

New in Phase 2.1:

| Path | Contents |
|---|---|
| `Research Work/phase2/p2_validate.py` | verification, block audit, block CV, D2 diagnostics |
| `metrics/validation_summary.json` | every computed table and number in this report |
| `metrics/baseline_comparison.csv` | flat comparison table, all four models |
| `metrics/block_cv_predictions.csv` | row-level predictions for all six folds |
| `reports/baseline_validation_tables.md` | machine-generated markdown tables |

Two corrections were made, both preserving the previous files:

1. **`p2_split.py` exclusion accounting.** The manifest counted conflict groups *after* filtering them out, so it recorded 0 for D2 instead of 37 groups / 76 records. The bug is fixed and the manifest regenerated. All split file hashes are byte-identical to the pre-fix values (`bd4f5edb…`, `5bcc228f…`, `3922f037…` for D1; `ad19a6e8…`, `2fc68c05…`, `44409491…` for D2). The pre-fix manifest is retained as `splits/split_manifest.before_validation.json`.
2. **Block-boundary labelling.** The corrected `(source_row-1)//1000+1` definition is used in this report. The Phase 2 `d1_block_robustness.json` is retained unchanged as the historical record; its fold membership differs by two Ham rows and its conclusions are unchanged.

Original dataset hashes remain `24ca099a…` (D1 workbook) and `649844f1…` (D2 CSV). No original file was modified.

Reproduce:

```bash
./.venv/Scripts/python.exe "Research Work/phase2/p2_validate.py"
```

---

## 10. Bottom line

- All four Phase 2 models are present, load correctly, and reproduce their saved predictions exactly.
- D1's 0.965 random-split macro-F1 is real for the frozen split but is largely a **within-batch** result: 91.2% of test Spam comes from the same batch as 95.5% of training Spam, and formatting without words already reaches 0.871.
- Under leave-one-block-out, pooled macro-F1 falls to **0.538** (SVM) / **0.545** (LR), with Spam recall **7.6%** / **8.9%**. One fold has no Spam and its macro-F1 is not a balanced estimate.
- D2 is stable at **0.888** macro-F1 (LR); Spam is weakest (0.803) because it is the smallest class and is nearly indistinguishable in surface form from Smishing (centroid cosine 0.751).
- The correct protocol is a dual report: frozen grouped split for within-source comparison, leave-one-source-block-out for cross-batch stress, both reported in full. No new split was invented and no score was tuned to look better.
- Dataset 1 is adequate for a transformer case study with that dual protocol, but not for a generalisation claim.

---

*Computed from `metrics/validation_summary.json`; tables in `reports/baseline_validation_tables.md`. No value in this report was hand-entered or estimated.*
