# Model and Dataset Notes

This prototype is an inference-only layer over the frozen Phase 2 experiments. It
does not create data, retrain models, fit a new vectorizer or tune thresholds.

## Dataset 1 — primary Malayalam task

- Source: `Datasets/Spam Message Collection.xlsx` (accessed through the Phase 2
  frozen artifacts).
- Selection: messages containing at least one Malayalam Unicode character
  (U+0D00–U+0D7F).
- Size: **1,992** records; **1,767 Ham / 225 Spam**.
- Split: grouped 70/15/15, seed 42, duplicate groups never cross splits.
  - train 1,394; validation 299; test 299.
- Final selected model: **Linear SVM**, char_wb TF-IDF 2–4, `min_df=2`,
  `sublinear_tf=True`, `max_features=300,000`, `C=0.5`, `class_weight="balanced"`,
  default decision boundary 0.
- Saved artifact: `Research Work/phase2/models/d1_malayalam_linear_svm.joblib`.
- Test result: accuracy 0.9866; Macro-F1 0.9650 [0.9250, 0.9922]; Spam recall
  0.8824 [0.7600, 0.9730]; 4 errors, no false positives.

### Source-block caveat

The source rows form three blocks:

| Block | Records | Spam |
|---|---:|---:|
| 4001–5000 | 630 | 12 |
| 5001–6000 | 991 | 0 |
| 6001–7000 | 371 | 213 |

94.7% of Spam is in the final block. The random split is a within-source
benchmark. Pooled leave-one-block-out Macro-F1 is **0.5378**, and block
6001–7000 has only 12 training Spam. The prototype must not be described as
validated on unseen Malayalam SMS sources.

## Dataset 2 — secondary English/Latin task

- Source: `Datasets/Dataset_5971.csv`.
- 5,971 original rows; 37 duplicate groups / 76 records with conflicting labels
  were excluded, leaving **5,895** records: 4,844 Ham / 450 Spam / 601 Smishing.
- Split: grouped 70/15/15, seed 42.
  - train 4,127; validation 885; test 883.
- Final selected model: **Logistic Regression**, char_wb TF-IDF 2–4, `min_df=2`,
  `sublinear_tf=True`, `max_features=300,000`, `C=1.0`,
  `class_weight="balanced"`.
- Saved artifact: `Research Work/phase2/models/d2_logreg.joblib`.
- Test result: accuracy 0.9638; Macro-F1 0.8877 [0.8482, 0.9239]; Spam recall
  0.8209; Smishing recall 0.8222.
- Dataset 2 is English/Latin-script and is **not** Malayalam detection. It has no
  source-block experiment.

## Preprocessing used at inference

Both saved pipelines receive text cleaned with exactly the Phase 2 function in
`p2_common.clean_text`:

1. Unicode NFKC normalisation.
2. Remove zero-width characters (`U+200B`, `U+200C`, `U+200D`, `U+FEFF`).
3. Replace NBSP with a space; replace control characters with a space.
4. Collapse whitespace and strip ends.
5. Preserve Malayalam Unicode, URLs, digits, punctuation and emoji.

The saved `TfidfVectorizer` is then applied by the pipeline; **no new vectorizer is
fitted**. D1 input without Malayalam characters and D2 input without Latin
characters are blocked by the application rather than silently routed.

## MuRIL comparator

`google/muril-base-cased` was fine-tuned for Dataset 1 as a Phase 2 comparator. It
is not selected for the prototype. Across three seeds it reaches random-split
Macro-F1 0.9619 ± 0.0054, but block-held-out Macro-F1 0.5028 and Spam recall
3.56%. Seed-42 and seed-44 predictions match the selected SVM exactly; the
transformer does not add within-source value and collapses under source holdout.

## Results provenance

Dashboard values are read from:

- `Research Work/phase2/metrics/d1_malayalam_results.json`
- `Research Work/phase2/metrics/d2_results.json`
- `Research Work/phase2/metrics/muril_results.json`
- `Research Work/phase2/metrics/validation_summary.json`
- `Research Work/phase2/metrics/final_model_comparison.csv`
- `Research Work/phase2/metrics/confidence_intervals.json`

Full methodology: `Research Work/phase2/reports/FINAL_EXPERIMENTAL_METHODOLOGY.md`.
Selection rationale: `Research Work/phase2/reports/FINAL_MODEL_SELECTION.md`.
Threshold analysis: `Research Work/phase2/reports/THRESHOLD_CALIBRATION_REPORT.md`.

## Unresolved limitations

- D1 access provenance is still undocumented.
- No source-diverse external Malayalam test set exists.
- Block 6001–7000 has only 12 training Spam and cannot support a stable local
  calibration.
- D2 is English-only; no Malayalam or Manglish smishing claim is supported.
- The models classify the original dataset labels; they do not validate links or
  establish that a message is safe.
