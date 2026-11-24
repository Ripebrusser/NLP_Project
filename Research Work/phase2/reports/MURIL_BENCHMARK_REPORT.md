# MuRIL Benchmark on Dataset 1 — Malayalam Ham vs Spam

**Phase 2.2, Parts B and C.** Frozen Phase 2 splits; no split regeneration, no synthetic data, no manual annotation, no test-set tuning.

**Verdict in one line:** MuRIL matches the classical SVM on the within-source random split (mean macro-F1 **0.9619** vs **0.9650**) but is **worse** under leave-one-block-out (pooled **0.5028** vs **0.5378**, Spam recall **3.6%** vs **7.6%**). It does not provide a meaningful improvement.

---

## 1. Model and data integrity

| Item | Value |
|---|---|
| Checkpoint | `google/muril-base-cased` (BERT-base architecture, 237,557,762 parameters) |
| Tokenizer | `BertTokenizer`, vocabulary 197,258 |
| Local reference model | `models/muril_d1_seed42/` (907 MB safetensors + tokenizer, 913 MB total) |
| Max sequence length | **128** |
| Train / validation / test | 1,394 (157 Spam) / 299 (34 Spam) / 299 (34 Spam) |
| Test record IDs | exactly those in `splits/d1_malayalam_test.csv` |
| Split SHA-256 | all six files match `split_manifest.json` before training |
| Malayalam preservation | tokenizer round-trip on a Malayalam test string is exact; no lowercasing, script stripping or English-only preprocessing |
| Saved model check | reloaded and re-run on the frozen test set: **299/299 predictions reproduced**, maximum absolute probability difference **0.0** |

Token lengths over all 1,992 records: mean 32.53, median 31, p90 55, p95 63, p99 90.09, max 127. `max_len=128` covers **100%** of records without truncation (96 covers 99.35%, 64 covers 95.38%). No text was dropped.

## 2. Training protocol

| Setting | Value |
|---|---|
| Objective | binary sequence classification, class-weighted cross-entropy |
| Optimiser | AdamW, weight decay 0.01 |
| Learning rate | 2e-5, linear decay, 10% warm-up |
| Batch | 4 with 2-step gradient accumulation (effective batch 8) |
| Max epochs / early stopping | 6 / patience 2 on **validation macro-F1** |
| Precision | fp16 autocast, gradient clipping 1.0 |
| Seeds | 42, 43, 44 (all reported; no best-seed selection) |
| Class weights | Ham 0.5635, Spam 4.4395 (inverse frequency from 157/1,394), capped at 10 |
| GPU | NVIDIA GeForce RTX 4050 Laptop GPU, 6 GB |
| Peak allocated memory | **4,779 MB** (batch 8 at 128 tokens exceeded comfortable headroom at 4.8 GB, so batch 4 × accumulation 2 was used) |

Class weighting is justified by the 11.3% Spam prevalence. The cap only binds in the block-6001 fold (raw Spam weight 67.5), where it limits instability from 12 positive examples. No hyperparameter search was run beyond this single configuration; the epoch count is the only selected quantity, and it is selected on validation macro-F1.

The test set was untouched during training and early stopping. Each seed was evaluated on test once, after its best validation epoch. The reload check in §1 is an artifact-verification pass, not a second model-selection event.

## 3. Random grouped split (within-source)

| Seed | Selected epoch | Accuracy | Macro-F1 | Ham F1 | Spam P | Spam R | Spam F1 | Train s | Peak MB |
|---|---|---|---|---|---|---|---|---|---|
| 42 | 2 | 0.9866 | 0.9650 | 0.9925 | 1.0000 | 0.8824 | 0.9375 | 167 | 4,779 |
| 43 | 1 | 0.9833 | 0.9556 | 0.9907 | 1.0000 | 0.8529 | 0.9206 | 114 | 4,778 |
| 44 | 1 | 0.9866 | 0.9650 | 0.9925 | 1.0000 | 0.8824 | 0.9375 | 115 | 4,778 |
| **Mean ± SD** | — | **0.9855 ± 0.0019** | **0.9619 ± 0.0054** | 0.9919 ± 0.0011 | 1.0000 ± 0.0000 | **0.8725 ± 0.0170** | 0.9319 ± 0.0097 | — | — |

Confusion matrices (rows Ham, Spam):

- seed 42: `[[265, 0], [4, 30]]`
- seed 43: `[[265, 0], [5, 29]]`
- seed 44: `[[265, 0], [4, 30]]`

Seeds 42 and 44 produce **exactly the same four errors** as the classical linear SVM. Seed 43 produces five, the same count as logistic regression. There are **zero false positives** in every seed. The seed-to-seed spread (0.9556–0.9650) is larger than the gap to the SVM, so this split provides no evidence that MuRIL is better.

The selected epoch is 1 for seeds 43 and 44 because their first validation pass was already the best; patience still required running to epoch 3 before stopping. The best state, not the final state, was evaluated.

## 4. Block-held-out evaluation (cross-source stress)

Protocol is identical to the classical baseline: for each of the three source blocks, train on the other two blocks and test on the held-out block. The number of epochs is the one selected for that seed on the random validation split (2 for seed 42, 1 for seeds 43 and 44), fixed before the fold is run. **No held-out block was used for early stopping, threshold choice or tuning.**

| Seed | Held-out block | Test n | Ham/Spam | Accuracy | Macro-F1 | Spam P | Spam R | Confusion (rows Ham, Spam) |
|---|---|---|---|---|---|---|---|---|
| 42 | 4001–5000 | 630 | 618/12 | 0.9873 | 0.8150 | 0.7000 | 0.5833 | `[[615, 3], [5, 7]]` |
| 42 | 5001–6000 | 991 | 991/0 | 0.9909 | 0.4977* | — | — | `[[982, 9], [0, 0]]` |
| 42 | 6001–7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 | `[[158, 0], [213, 0]]` |
| 43 | 4001–5000 | 630 | 618/12 | 0.9905 | 0.8476 | 0.8750 | 0.5833 | `[[617, 1], [5, 7]]` |
| 43 | 5001–6000 | 991 | 991/0 | 0.9990 | 0.4997* | — | — | `[[990, 1], [0, 0]]` |
| 43 | 6001–7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 | `[[158, 0], [213, 0]]` |
| 44 | 4001–5000 | 630 | 618/12 | 0.9841 | 0.8293 | 0.5556 | 0.8333 | `[[610, 8], [2, 10]]` |
| 44 | 5001–6000 | 991 | 991/0 | 0.9950 | 0.4987* | — | — | `[[986, 5], [0, 0]]` |
| 44 | 6001–7000 | 371 | 158/213 | 0.4259 | 0.2987 | 0.0000 | 0.0000 | `[[158, 0], [213, 0]]` |

\* The 5001–6000 block contains **no Spam**. Spam precision/recall are undefined, and `sklearn` assigns Spam F1 = 0, which halves macro-F1. This value is an artefact of the absent class, not a balanced performance estimate. The real error signal in that fold is the 1–9 Ham false positives.

### Pooled leave-one-block-out

| Seed | Accuracy | Macro-F1 | Spam P | Spam R | Spam F1 | Confusion (rows Ham, Spam) |
|---|---|---|---|---|---|---|
| 42 | 0.8845 | 0.4979 | 0.3684 | 0.0311 | 0.0574 | `[[1755, 12], [218, 7]]` |
| 43 | 0.8896 | 0.5006 | 0.7778 | 0.0311 | 0.0598 | `[[1765, 2], [218, 7]]` |
| 44 | 0.8855 | 0.5098 | 0.4348 | 0.0444 | 0.0806 | `[[1754, 13], [215, 10]]` |
| **Mean ± SD** | **0.8865 ± 0.0027** | **0.5028 ± 0.0062** | 0.5270 ± 0.2197 | **0.0356 ± 0.0077** | 0.0660 ± 0.0128 | — |

The pooled result is driven by the 6001–7000 fold: 213 of the 225 Spam messages are there, and MuRIL misses **all 213** in every seed. Only 7–10 of the 12 Spam messages in block 4001 are recovered. Precision varies widely across seeds (0.368–0.778) because it rests on 7–10 true positives against 2–13 false positives.

The 5001–6000 fold is the only place where MuRIL is as clean as the classical models: 1–9 false positives and no Spam to miss. The 4001–5000 fold is where it is genuinely better than the classical models: **0.815–0.848 macro-F1 and 58–83% Spam recall**, against 0.696 and 25% for both classical models.

## 5. Error analysis

### 5.1 Random split — four false negatives (seed 42)

All four are Spam → Ham, each with P(Spam) ≈ 0.055:

| Record | Row | Message | P(Spam) |
|---|---|---|---|
| D1-04452 | 4455 | Onam greeting / festival message with a sender number | 0.0567 |
| D1-04453 | 4456 | Second Onam greeting from the same sender | 0.0555 |
| D1-06180 | 6183 | “മദ്യപിച്ച് വാഹനമോടിക്കരുത്” — a road-safety message | 0.0553 |
| D1-06194 | 6197 | “* പ്രാർത്ഥന - മധുര !!” — a short prayer | 0.0554 |

These are the **same four messages** the SVM misses, at almost exactly the same confidence. They are not messages a human would confidently label Spam. They sit inside label runs that conflict with their content, which points to batch-level labelling rather than a representational failure. No model capacity can recover a label the text does not support.

### 5.2 Block 4001–5000 — near-duplicate campaign labelled both ways

The fold has 5 false negatives and 3 false positives. Two of the false positives (D1-04437, D1-04442) are identical Onam greetings from the **same sender and campaign** (`Nidheesh.mlprm.9539 508108`) as two false negatives (D1-04452, D1-04453), which are themselves near-identical to each other. MuRIL assigns P(Spam) = 0.5836 to the Ham copies and 0.33/0.20 to the Spam copies. The model is responding to the campaign text; the **labels disagree**. This is direct evidence of label inconsistency between source batches, and it inflates the apparent error rate in this fold. The duplicate detector did not merge them because the texts are not exact or normalised duplicates.

### 5.3 Block 5001–6000 — false positives only

9 Ham messages (seed 42) are predicted Spam: a New York Indian Film Festival item, a Ramzan dance post, a World Cup song post, and similar conversational messages, many containing emoji or links. They share surface features with promotional text but have no spam intent. With no Spam in the fold, only this false-positive behaviour is measurable.

### 5.4 Block 6001–7000 — complete collapse

**All 213 Spam messages are predicted Ham in all three seeds**, with P(Spam) ≈ 0.108 for the batch. The training set for this fold contains only **12 Spam messages**, all from a different spam dialect (char-TF-IDF centroid cosine 0.282 to the held-out spam). The model learns the majority class and never crosses the decision boundary.

This is not fixable by tuning on the held-out block. It is the same structural problem the classical models face, expressed more sharply: with 12 positives, a high-capacity transformer has even less incentive to represent the minority class than a linear model with class weights. The class weight is capped at 10, but that is not enough to overcome 1,609 Ham versus 12 Spam.

## 6. Compute

| Quantity | Value |
|---|---|
| Random-split training time | 114–167 s per seed (3 seeds, 483 s total) |
| Block-fold training time | 27–91 s per fold (9 folds) |
| Peak allocated GPU memory | 4,778–4,779 MB |
| GPU | RTX 4050 Laptop, 6 GB, CUDA 12.8 |
| Packages | torch 2.11.0+cu128, transformers 5.22.1 |
| Reference model on disk | 913 MB (`models/muril_d1_seed42/`) |

Total wall-clock time for all 12 runs was about 14 minutes, including model reload per run. The reference checkpoint is seed 42 because it is the first pre-declared seed, **not** because it scored best. All per-seed metrics and predictions are retained.

## 7. Artifacts

| Path | Contents |
|---|---|
| `p2_muril.py` | training/evaluation script (split hash check, 3 seeds, 3 block folds) |
| `p2_muril_report.py` | artifact verification, table generation, error extraction |
| `models/muril_d1_seed42/` | reference model + tokenizer (913 MB) |
| `metrics/muril_results.json` | all runs, histories, metrics, confusion matrices, versions |
| `metrics/muril_random_seed{42,43,44}_predictions.csv` | row-level test predictions |
| `metrics/muril_block{4001,5001,6001}_seed{42,43,44}_predictions.csv` | row-level fold predictions |
| `metrics/muril_artifact_verification.json` | reload and Malayalam round-trip check |
| `metrics/muril_error_examples.json` | error rows with text and probabilities |
| `reports/muril_tables.md` | machine-generated tables |
| `logs/muril_run2.log` | complete training log for the reported run |

## 8. Limitations

1. **One corpus, three source blocks, 225 Spam.** The random split is within-source; the block folds are underpowered by design.
2. **Block 6001 has 12 training Spam**, so its fold measures failure under an impossible training regime, not the model's linguistic ceiling.
3. **Block 5001 has no Spam**, so its macro-F1 is not a balanced metric and Spam precision/recall are undefined.
4. **No external test set.** Nothing here estimates performance on new Malayalam SMS sources.
5. **No threshold tuning.** The default 0.5 boundary is used everywhere, including the block folds. Tuning it on held-out blocks would leak.
6. **Single configuration.** One learning rate, one max length, one class-weight scheme; no extensive search, by design.
7. **The reference checkpoint is not the best seed.** It is the first seed, retained for reproducibility; all seeds are reported.

## 9. Bottom line

- MuRIL is a competent **within-source** classifier: 0.9619 ± 0.0054 macro-F1, 87.25% Spam recall, zero false positives across three seeds.
- It is **not better** than the char-TF-IDF SVM on that split. Two of three seeds make exactly the SVM's four errors; the third matches logistic regression's five. The task appears to be at a label-noise ceiling, not a capacity ceiling.
- Under leave-one-block-out it is **worse**: 0.5028 pooled macro-F1 and 3.6% Spam recall, versus 0.5378/7.6% for the SVM. It wins the 4001 fold, ties the degenerate 5001 fold, and loses the decisive 6001 fold by predicting Ham for all 213 Spam.
- The transformer does not remove the source-block confound. It reproduces it. That is the central result, and it is consistent with the Phase 2.1 finding that the random split largely measures batch recognition.

*All numbers are generated from `metrics/muril_results.json` and `metrics/muril_error_examples.json`; tables in `reports/muril_tables.md`. No value was hand-entered or estimated.*
