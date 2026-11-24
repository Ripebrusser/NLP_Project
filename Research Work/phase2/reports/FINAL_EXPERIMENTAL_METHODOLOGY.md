# Final Experimental Methodology

**Phase 2.3, Part E.** Reproducible description of the completed study. This document records what was actually done; it does not propose new experiments.

## 1. Scope and claim boundary

The study has two separate tasks:

1. **Primary — D1 Malayalam-script SMS: Ham vs Spam.** 1,992 Malayalam-containing messages. D1 has **no phishing label**; no phishing claim is made.
2. **Secondary — D2 English SMS: Ham / Spam / Smishing.** 5,895 records after exclusions. D2 contains no Indic-script messages.

No synthetic data, new dataset, manual annotation, augmentation, dataset pooling or new architecture was used. D1 and D2 are never merged or label-mapped into one another.

**Claim boundary:** all D1 results are within-source unless explicitly labelled block-held-out. The random split measures performance on new messages from the same collection batches, not on new Malayalam SMS sources. No generalisation claim is made.

## 2. Dataset selection and language/script filtering

### D1

- Source: `Datasets/Spam Message Collection.xlsx`, read without modifying the original (SHA-256 `24ca099a…`).
- Selection: messages containing at least one Malayalam character in the Unicode block U+0D00–U+0D7F.
- Result: **1,992 records**, **1,767 Ham / 225 Spam** (11.3% Spam).
- Script composition: 1,489 Malayalam-only, 503 Malayalam + Latin, **0** containing Tamil, Telugu or Kannada.
- `source_row` preserves the Excel row number; `record_id` is `D1-xxxxx`.
- Source blocks use the corrected definition `(source_row − 1) // 1000 + 1`:
  - 4001–5000: 630 records, 12 Spam;
  - 5001–6000: 991 records, 0 Spam;
  - 6001–7000: 371 records, 213 Spam.
- 94.7% of Spam is in 6001–7000. This is a property of the corpus, not a modelling choice.

### D2

- Source: `Datasets/Dataset_5971.csv`, read without modifying the original (SHA-256 `649844f1…`).
- Original rows 5,971; 37 duplicate groups / 76 records had conflicting labels and were excluded → **5,895 records**.
- Labels: 4,844 Ham / 450 Spam / 601 Smishing.
- Script: English/Latin; zero Indic-script rows. D2 is secondary and is not used for Malayalam claims.

## 3. Text preprocessing

- Unicode **NFKC** normalisation.
- Removal of zero-width characters (`U+200B`, `U+200C`, `U+200D`, `U+FEFF`), NBSP → space, control characters → space.
- Whitespace collapsed; leading/trailing whitespace removed.
- **No** Malayalam transliteration, stemming, stop-word removal, script stripping or manual spelling correction.
- URLs, phone numbers, punctuation and emoji are retained. They are part of the message and are not silently deleted.
- The TF-IDF vectoriser uses `lowercase=True` for the classical models only. MuRIL uses its own **cased** tokenizer and receives the cleaned text with Malayalam Unicode intact.

## 4. Duplicate handling

- Duplicate groups are formed by a union of:
  1. exact message matches;
  2. the audit's aggressive normalised key (URLs, digits and punctuation normalised);
  3. a conservative fuzzy pass for D1.
- Duplicate groups never cross train/validation/test.
- Label-conflicting groups are excluded: D1 **0 groups / 0 records**; D2 **37 groups / 76 records**.
- D1 has 1,824 groups for 1,992 records (168 duplicate excess); D2 has 5,663 groups for 5,895 records.
- Group overlap and normalised-text overlap between every split pair are **0** in both datasets.

## 5. Split methodology

- Group-stratified **70/15/15** assignment, seed **42**, `numpy.random.default_rng(42)`.
- Within each label stratum, groups are shuffled, sorted by size and assigned to the split with the largest record deficit.
- D1: train **1,394** (157 Spam), validation **299** (34 Spam), test **299** (34 Spam).
- D2: train **4,127** (315 Spam / 421 Smishing), validation **885** (68 / 90), test **883** (67 / 90).
- Frozen SHA-256 values:
  - D1: `bd4f5edb…`, `5bcc228f…`, `3922f037…`;
  - D2: `ad19a6e8…`, `2fc68c05…`, `44409491…`.
- Every test split was evaluated once per model/seed. No split was regenerated for Phase 2.3.

### Source-block confound

The random split is grouped with respect to duplicates but random with respect to collection batch. Every split contains all three blocks: 95.5% of training Spam and 91.2% of test Spam come from block 6001–7000. Labels track source position: only 13 label runs occur where about 400 would be expected under independence (z = −43.2), including a 1,662-row Ham run followed by a 213-row Spam run. A block-majority rule with no text reaches 0.832 Macro-F1, and a structure-only model reaches 0.871. These facts make the random split a **within-source** benchmark.

## 6. Classical models

- Features: TF-IDF `char_wb`, n-grams 2–4, `min_df=2`, `sublinear_tf=True`, `lowercase=True`, `max_features=300,000`.
- Class weight: `balanced`.
- Logistic Regression: `C=1.0`, `liblinear` for binary D1, `lbfgs` for D2, `max_iter=5,000`.
- Linear SVM: `C=0.5`, squared hinge, `max_iter=10,000`, `dual="auto"`.
- Selection: 4 vectoriser configurations × C ∈ {0.5, 1.0, 2.0}, chosen on **validation Macro-F1 only**. Four configurations were word 1–1, word 1–2, char 2–4, char 2–5.
- Final model: refit on **train + validation**, evaluated once on test. The test set never entered configuration selection.
- Saved artifacts: `models/d1_malayalam_logreg.joblib`, `d1_malayalam_linear_svm.joblib`, `d2_logreg.joblib`, `d2_linear_svm.joblib`; test scores are in `metrics/*_test_predictions.csv`.

## 7. MuRIL

- Checkpoint: `google/muril-base-cased` (BERT-base, 237,557,762 parameters; 197,258-token vocabulary).
- Saved reference: `models/muril_d1_seed42/` (913 MB, model + tokenizer).
- Maximum sequence length **128**: token median 31, p95 63, p99 90.09, max 127; 100% coverage, no truncation.
- Training: AdamW, learning rate 2e-5, weight decay 0.01, linear warm-up 10%, gradient clipping 1.0.
- Batch 4 with 2-step gradient accumulation (effective batch 8); fp16 autocast.
- Maximum 6 epochs, early stopping with patience 2 on **validation Macro-F1**; best state restored.
- Class-weighted cross-entropy, inverse-frequency weights 0.5635 Ham / 4.4395 Spam, capped at 10 (cap binds only in the block-6001 fold).
- Seeds: 42, 43, 44. Every seed is reported; no best-seed selection.
- Test evaluated once per seed after the best validation epoch. Block folds use the epoch count selected for that seed on the random validation split and never use the held-out block for stopping or tuning.
- Hardware: NVIDIA RTX 4050 Laptop GPU, 6 GB; peak 4,779 MB; 114–167 s per random run.

## 8. Evaluation metrics

- Accuracy.
- **Macro-F1** over the fixed label set (primary summary metric).
- Ham F1, Spam F1, Spam precision, Spam recall.
- D2 additionally: Smishing F1, precision and recall.
- Confusion matrices for every model/seed/fold.
- PR-AUC and ROC-AUC as diagnostics for the threshold analysis, not as headline selection metrics.
- Block 5001–6000 has no Spam: its Spam precision/recall are undefined and its Macro-F1 is an artefact of assigning zero to the absent class. It is never presented as a balanced score.

## 9. Confidence intervals

- Nonparametric **percentile bootstrap** over duplicate groups (`group_id`).
- **2,000 replicates**, fixed seed **42**.
- 95% interval = 2.5th/97.5th percentiles.
- D1 test: 299 rows / 299 groups; D2 test: 883 / 883. The grouped implementation is used even though it is numerically equivalent to a message bootstrap here.
- MuRIL is reported in two separate ways:
  - **within-seed test-sample uncertainty** for each seed's frozen predictions;
  - **across-seed training variation** as mean, SD, min and max of the three seed-level point values.
- The two are never combined into one interval.
- Block-held-out results are reported as three separate folds plus a pooled descriptive result. No narrow confidence interval is presented for three source blocks.

## 10. Paired comparisons

- Paired percentile bootstrap, 2,000 replicates, seed 42, same group resample for both models.
- Metrics: difference in Macro-F1, Spam recall, accuracy and Spam precision.
- D1 primary pair: seed-42 MuRIL vs each classical model on the common 299 test rows. Seeds 43 and 44 are reported separately as sensitivity.
- D2: LR vs SVM on the common 883 test rows.
- Block-pooled and block-6001-only paired differences are reported as robustness, not as population estimates.
- No p-values are used. Intervals including zero are not interpreted as proof of no difference; intervals excluding zero are not interpreted as proof of practical importance.
- Pre-specified practical threshold: 0.01 Macro-F1 and 0.05 Spam recall. On 34 Spam this is only 1.7 messages, so random-test differences are interpreted with that limitation.

## 11. Threshold calibration

- **Random split:** fit on the frozen training split only; select the threshold on the frozen validation split; apply to the saved final-model test scores. The train+validation refit is never used to choose a threshold (it has seen the validation rows).
- **Block folds:** for each fold, draw a stratified 80/20 inner split from the two training blocks only; select the threshold on the inner 20%; apply to the held-out block's saved out-of-fold scores. Repeat over 20 inner splits (seeds 42–61) to measure stability. The held-out block is never used for fitting or selection.
- Rule: maximum validation Macro-F1; ties broken by the widest margin to the nearest validation score. A secondary rule requires validation Spam precision ≥ 0.90.
- MuRIL block-fold models were not saved. Their held-out scores are analysed descriptively (PR-AUC, score ranges, threshold sweep); the seed-42 random-validation threshold is transferred only as a labelled sensitivity check.
- No test-set threshold tuning was performed.

## 12. Robustness testing

- Leave-one-source-block-out with the corrected block definition; no validation split, no per-fold tuning.
- Train on the other two blocks, test on the held-out block; for MuRIL, fixed epoch count from the random validation run.
- Report every fold separately and the pooled out-of-fold result. Never average fold scores silently.
- Report the 5001–6000 no-Spam caveat and the 12-training-Spam caveat for 6001–7000.
- Do not tune on, select on, or calibrate against the held-out block.

## 13. Limitations

1. **One corpus, three source blocks, 225 Spam.** There is no source-diverse Malayalam test set.
2. **The random split is within-batch.** 95.5% of training Spam and 91.2% of test Spam come from block 6001–7000. Its 0.9650 cannot be read as field performance.
3. **Block-held-out is underpowered.** The critical fold has only 12 Spam in training; another contains no Spam. Pooled 0.5378 is a stress result, not a fair estimate of linguistic capability.
4. **Label inconsistency.** Block 4001 contains the same Onam campaign under both labels; no manual relabelling was performed.
5. **MuRIL is not a solution here.** It ties the SVM within-source and collapses under block holdout.
6. **Threshold calibration is not stable** with 12 training Spam. The SVM's improved block-6001 recall is a sensitivity finding, not a deployable operating point.
7. **D2 is English-only.** It provides no Malayalam/Manglish smishing evidence.
8. **D1 access provenance is still undocumented.** This is a publication blocker independent of the statistics.
9. **No external validation.** No claim about unseen Malayalam SMS sources is supported.

## 14. Reproducibility

Run order, from the project root:

```bash
./.venv/Scripts/python.exe "Research Work/phase2/p2_extract.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_duplicates.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_split.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_train_d1.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_train_d2.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_robustness.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_validate.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_ci.py"          # Phase 2.2 CI (superseded; see note)
./.venv/Scripts/python.exe "Research Work/phase2/p2_muril.py" --seeds 42 43 44
./.venv/Scripts/python.exe "Research Work/phase2/p2_muril_report.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_stats.py"      # Phase 2.3 CIs + paired
./.venv/Scripts/python.exe "Research Work/phase2/p2_threshold.py"  # threshold calibration
```

Phase 2.3 numbers come from `p2_stats.py` and `p2_threshold.py`; `p2_ci.py` is retained as the Phase 2.2 implementation and is not the source of the final CI report. The original datasets and frozen splits are read-only.

*This methodology describes the completed experiments. No result in it was estimated or fabricated.*
