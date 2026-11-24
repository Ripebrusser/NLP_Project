# Final Methodology and Objective

## 1. One objective

> **To evaluate, under duplicate-group-controlled splitting and a row-order stress test, how well classical character n-gram models and a fine-tuned multilingual transformer classify Malayalam-containing SMS spam, and to conduct a separate three-class English SMS spam/smishing analysis, without claiming cross-dataset or source transfer.**

This is exactly **one** objective with two coupled parts: a Malayalam-containing SMS spam evaluation and a separate English spam/smishing evaluation. The second dataset is not an external validation of the first. The objective is descriptive and comparative; it is not a claim of field deployment, source generalisation, or Malayalam phishing detection.

## 2. Problem statement

Malayalam-script SMS spam is under-resourced, and the available Dravidian SMS workbook has a strong row-order label confound: 94.7% of its Malayalam-subset Spam lies in one consecutive 1,000-row block. A conventional random split can therefore produce a high within-batch score without establishing transfer to another collection source. It is also unclear whether a multilingual transformer such as MuRIL offers a real advantage over strong character n-gram baselines on a small, imbalanced corpus. This project evaluates both model families on one frozen, duplicate-group-aware split and measures the change under a leave-one-row-block-out stress test, while keeping a separate English three-class corpus for a bounded secondary analysis.

## 3. Three research questions

**RQ1.** On the duplicate-grouped, label-stratified test set of 1,992 Malayalam-containing messages, how do character n-gram Logistic Regression and Linear SVM compare with fine-tuned MuRIL on Macro-F1, Spam recall and accuracy, and is any MuRIL difference reproducible across seeds 42, 43 and 44?

**RQ2.** How much does performance change when one complete 1,000-row workbook block is held out, and what does that change show about row-order/source-proxy bias and the limits of the random-split result?

**RQ3.** In the separate English three-class corpus, how separable are Ham, Spam and Smishing under the same duplicate-group protocol, and what does the Spam/Smishing confusion imply for the project’s scope?

The questions deliberately do **not** ask for Malayalam phishing detection, Manglish detection, or generalisation to unseen real-world sources.

## 4. Methodology sequence

1. **Data audit.** Verify counts, labels, scripts, duplicates, conflicts and provenance. Preserve originals. D1 raw 7,717; usable 7,714; Malayalam-containing 1,992 (1,767 Ham/225 Spam). D2 5,971 (4,844/489/638).
2. **Scope lock.** D1 binary Ham/Spam primary; D2 three-class secondary; never pool. No phishing claim for D1.
3. **Grouping.** Exact, normalised and conservative fuzzy duplicates are grouped with union-find. Conflicting-label groups are excluded (D2: 37 groups/76 records). D1 Malayalam subset: 0 conflicts.
4. **Split.** Duplicate-group-aware, label-stratified 70/15/15, seed 42. D1 1,394/299/299; D2 4,127/885/883. Assert zero group and normalised-key overlap.
5. **Classical models.** Character `char_wb` 2–4 TF-IDF, `min_df=2`, `sublinear_tf`, `max_features=300,000`; LR C=1.0 and Linear SVM C=0.5, balanced class weights. Select by validation Macro-F1 only, refit train+validation, evaluate frozen test once.
6. **Transformer.** Fine-tune `google/muril-base-cased` seeds 42/43/44 on the same split, early-stop on validation Macro-F1, evaluate the same frozen test. No test-based tuning.
7. **Uncertainty.** Group bootstrap, 2,000 replicates, seed 42. Every test group is singleton, so this is numerically a message bootstrap. Use shared draws for paired comparisons. Report exact precision/FPR intervals where perfect precision occurs.
8. **Robustness.** Leave-one-row-block-out stress test: blocks 4001–5000 (630 rows), 5001–6000 (991), 6001–7000 (371). Pool held-out predictions before scoring. Mark the no-Spam fold as an absent-class artefact.
9. **Sensitivity.** Threshold calibration and paired comparisons are reported as exploratory; no deployment threshold is selected.
10. **Prototype.** Read-only Streamlit demo using the two selected classical models. 299/299 and 883/883 parity; not a generalisation test.
11. **Reporting.** One canonical results table; claims limited to within-corpus and row-block stress; provenance and external validation remain open.

## 5. Contributions

1. A reproducible duplicate-group-aware evaluation of classical char n-gram models and MuRIL on a Malayalam-containing SMS subset.
2. A quantified row-block stress test: SVM Macro-F1 falls from **0.9650** on the grouped random test to **0.5378** pooled leave-one-row-block-out; MuRIL falls to **0.5028** and detects 3.56% of Spam.
3. A clear negative/limiting result: MuRIL does not improve on the classical baseline within source and collapses on the dominant held-out Spam block.
4. A separate, bounded English three-class analysis showing a weak Spam/Smishing boundary (5,895 experimental records, 883 test).
5. A transparent uncertainty audit, including the distinction between perfect observed precision and its exact lower bound.

**Not contributions:** a new dataset, a new algorithm, first Malayalam/Dravidian spam detection, state-of-the-art performance, or a validated phishing detector.

## 6. Limitations

- D1 access authorisation is undocumented; redistribution is not established.
- No external/source-diverse test set; block holdout is a three-block stress test, not field validation.
- Row blocks are row-order proxies, not verified collection sources; the cause of the label association is unknown.
- Only three blocks; one has no Spam; the critical fold has 12 training Spam.
- “Malayalam” means Malayalam Unicode script presence; 503 records also contain Latin; no Manglish coverage.
- D1 has no phishing/smishing labels.
- D2 is English/Latin-only, has no source metadata, and excludes 76 conflicting-label records; it overlaps with D1/UCI and is not independent external validation.
- Perfect precision is based on 29–30 predicted positives; exact lower bounds are 88.0–88.4%, not proof of zero future false positives.
- Structure-only diagnostics reach 0.8706 Macro-F1; script/length/URL/digit shortcuts may inflate apparent performance.
- Only three MuRIL seeds; the three-seed mean interval is conditional on those seeds.
