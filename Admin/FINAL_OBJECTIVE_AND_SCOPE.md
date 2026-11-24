# Final Objective and Scope

**Status:** authoritative. Replaces all earlier multi-objective formulations.  
**Date:** 8 November 2026

## 1. Recommended title

> **Duplicate-Controlled Evaluation of Character N-Gram and MuRIL Models for Malayalam-Script SMS Spam Classification, with a Separate English Spam–Smishing Study**

This title names the two experiments without implying that MuRIL was evaluated on smishing. A shorter cover title may be used:

> *Classical and Multilingual Transformer Models for Malayalam-Script SMS Spam and English SMS Smishing: A Reproducible Evaluation*

The short form is acceptable only if the abstract immediately states that the transformer was evaluated on D1 spam only.

**Titles that must not be used:** any title claiming Malayalam phishing detection, Malayalam–English code-mixed phishing detection, Manglish threat detection, a unified Malayalam–English model, or a validated production filter.

## 2. Exactly one research objective

> **To evaluate, under duplicate-group-controlled splitting and a row-order stress test, how well classical character n-gram models and a fine-tuned multilingual transformer classify Malayalam-containing SMS spam, and to conduct a separate three-class English SMS spam/smishing analysis, without claiming cross-dataset or source transfer.**

This is one objective. It has two experimental components, not two objectives:

1. **Primary:** D1 Malayalam-containing binary Ham/Spam classification, with LR, linear SVM and MuRIL seeds 42/43/44, plus a pooled leave-one-row-block-out stress test.
2. **Secondary:** D2 English/Latin three-class Ham/Spam/Smishing classification with LR and SVM.

D2 is not an external validation set for D1. The two datasets are never pooled.

## 3. Problem statement

Malayalam-script SMS spam is under-resourced. The available Dravidian SMS workbook contains 1,992 Malayalam-containing messages, but 94.7% of its Spam lies in one consecutive 1,000-row workbook block. A conventional random split can therefore yield a high score by sharing campaign and row-order structure between training and test, without demonstrating transfer to another collection source. At the same time, it is unclear whether a multilingual transformer such as MuRIL offers a real advantage over strong character n-gram baselines on a small, imbalanced corpus. This project quantifies both the within-corpus comparison and the sensitivity of the result to holding out a complete row block, while keeping a separate English three-class corpus for a bounded secondary analysis.

## 4. Scope

### In scope

- D1: 1,992 Malayalam-containing records; 1,767 Ham / 225 Spam.
- 1,489 Malayalam-only-script records; 503 Malayalam+Latin records.
- Duplicate-group-aware 70/15/15 split, seed 42; test 299 (265 Ham / 34 Spam).
- Character `char_wb` 2–4 TF-IDF; Logistic Regression; Linear SVM.
- `google/muril-base-cased`, seeds 42/43/44, same frozen split.
- 2,000-replicate duplicate-group percentile bootstrap, seed 42.
- Pooled leave-one-row-block-out stress test over three workbook blocks.
- D2: 5,971 original; 5,895 experimental after 37 conflicting groups / 76 records; 883 test; English/Latin Ham/Spam/Smishing; LR and SVM only.

### Out of scope

- Malayalam or Manglish phishing/smishing detection.
- A unified Malayalam–English model.
- Pooling D1 and D2.
- External validation of D1 by D2.
- Unseen-source or field generalisation.
- URL reputation, malware, APK or credential-theft detection.
- Production deployment or a validated cybersecurity filter.
- New data collection, synthetic SMS, LLM-generated SMS, relabelling or new training runs.

## 5. Research questions

These are separate from the objective and do not create additional objectives.

**RQ1.** On the duplicate-grouped test set of 299 Malayalam-containing messages, how do character n-gram LR, linear SVM and fine-tuned MuRIL compare on Macro-F1, Spam recall and accuracy, and is any MuRIL difference reproducible across seeds 42, 43 and 44?

**RQ2.** How much does measured performance change when each complete 1,000-row workbook block is held out in turn, and what does that change show about the dependence of the random-split result on row order and script composition?

**RQ3.** In the separate English three-class corpus, how separable are Ham, Spam and Smishing under the same duplicate-group protocol, and what does the Spam/Smishing confusion imply for the limits of a text-only three-class claim?

## 6. Main contributions

1. A reproducible, duplicate-group-aware comparison of strong character n-gram baselines and MuRIL on a Malayalam-containing SMS subset.
2. A quantified negative/limiting result: SVM Macro-F1 falls from **0.9650** under the grouped random split to **0.5378** under pooled leave-one-row-block-out; MuRIL mean falls to **0.5028** with **3.56%** Spam recall.
3. Evidence that the apparent MuRIL advantage is not robust: seeds 42 and 44 are prediction-identical to SVM, seed 43 is one Spam false negative worse, and the paired interval includes zero.
4. A transparent uncertainty treatment: exact intervals for perfect precision and zero observed false positives, plus a clear distinction between across-seed variation and conditional test-sample uncertainty.
5. A separate, bounded English three-class analysis showing a weak Spam/Smishing boundary, without merging labels or claiming Malayalam smishing capability.

**Not contributions:** a new dataset, a new algorithm, first Malayalam/Dravidian spam detection, first use of D1, state-of-the-art performance, a transformer superiority claim, or a validated phishing detector.

## 7. What the research can claim

- Within the frozen D1 test set, all three model families achieve high random-split Macro-F1 (0.9556–0.9650).
- The pooled row-block result is much lower (0.5378 SVM, 0.5448 LR, 0.5028 MuRIL mean), with very low Spam recall.
- SVM and MuRIL are not statistically distinguishable; LR and SVM are not statistically distinguishable.
- D2 LR achieves 0.8877 Macro-F1 and D2 SVM 0.8825, but the paired interval includes zero.
- The D1 corpus exhibits a strong association between row-block membership and label, and between script composition and label.

## 8. What the research cannot claim

- That it detects Malayalam or Manglish phishing/smishing.
- That it generalises to unseen real-world sources.
- That the row blocks are verified collection sources or that the block result estimates a source population.
- That perfect observed precision implies zero future false positives.
- That a 0.0094 or 0.0031 difference establishes model superiority.
- That MuRIL is validated for SMS spam by its foundation paper.
- That FSSHAP reports a particular accuracy or ignored leakage, without its full text.
- That D2 is independent external validation of D1.

## 9. Limitations

D1 permission is unresolved; D1 has no phishing labels; “Malayalam” means Malayalam Unicode script presence, not verified language identification; 503 records also contain Latin; no Manglish test set; only three row blocks, one with no Spam and one with 12 training Spam; no source metadata; no independent Malayalam test corpus; 29–30 predicted Spam support perfect precision; only three MuRIL seeds; D2 is English/Latin, overlaps D1 on 773 normalised keys, and excludes 76 conflicting-label records; FSSHAP and several secondary papers are not full-text verified; the prototype is a demonstration only.
