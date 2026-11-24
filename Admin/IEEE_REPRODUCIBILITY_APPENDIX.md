# Appendix: Reproducibility of the Malayalam and English SMS Spam–Smishing Study

**Status of this document.** This is the single authoritative reproducibility appendix for the frozen codebase. `Admin/REPRODUCIBILITY_APPENDIX.md` is a condensed manuscript version that defers to this document. Every figure, hash and command below was taken from the artifacts named beside it, not from earlier narrative reports; where evidence does not exist, the text says so explicitly.

**Evidence date.** 8 November 2026. Frozen audit run `20261108T171120Z`.

**What is reproducible.** The verification layer is fully reproducible from the frozen artifacts in this repository. The experimental layer (training) is reproducible only under the conditions stated in Section E and is subject to the limitations in Section K. No model was retrained, no split regenerated, no dataset modified, and no prediction changed during the preparation of this appendix.

---

## A. Experimental environment

All experiments and all verification checks were executed on a single machine under one project-local virtual environment.

| Item | Verified value | Source |
|---|---|---|
| Operating system | Windows 11, build 10.0.26300 | `full_audit_results.json` (`platform`), `FINAL_TEST_REPORT.md` |
| Python interpreter | CPython 3.14.3, MSC v.1944, 64-bit | `full_audit_results.json` (`python`) |
| Processor | Intel64 Family 6 Model 191 Stepping 2 (GenuineIntel), 16 logical processors | `platform`/`os.cpu_count()` at verification time |
| System memory | Not recoverable from available project records | — |
| Discrete GPU | NVIDIA GeForce RTX 4050 Laptop GPU, 6,141 MiB, driver 617.42 | `nvidia-smi` at verification time; GPU model also recorded in `phase2/metrics/muril_results.json` (`versions.gpu`) |
| CUDA runtime used for MuRIL | CUDA 12.8 (`torch 2.11.0+cu128`) | `muril_results.json` (`versions.cuda`) |
| Peak MuRIL training memory | 4,779.3 MiB (seed 42, random split) | `muril_results.json` |
| MuRIL training wall time | 167.09 s for seed 42, random split | `muril_results.json` |

**Main packages, verification and modelling stack.**

| Package | Version |
|---|---|
| numpy | 2.5.4 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| joblib | 1.6.0 |
| openpyxl | 3.1.5 |
| streamlit (prototype only) | 1.67.0 |
| torch (MuRIL only) | 2.11.0+cu128 |
| transformers (MuRIL only) | 5.22.1 |
| accelerate (MuRIL only) | 1.15.0 |

The test framework is the standard-library `unittest` module; `pytest` is not installed in this environment. Test discovery and reporting are therefore performed by `Research Work/tests/run_tests.py`.

**Dependency pinning.** Verification and prototype dependencies are pinned exactly in `Research Work/requirements-verification.txt` (six packages, listed above) and `Research Work/prototype/requirements.txt` (five packages). MuRIL training dependencies are separated from the verification stack because they are not required to re-verify any frozen result. The saved `joblib` pipelines were produced with scikit-learn 1.9.1; a different major version raises `InconsistentVersionWarning` on load and is not supported by this release.

**Verification environment.** The audit runs inside the same project-local `.venv` and asserts the pinned versions at run time (check `environment`). A clean-environment installation was **not** performed: the pinned versions were verified in the existing environment, so the pins are asserted rather than proven by a from-scratch build. This limitation is carried into Section K.

---

## B. Dataset provenance and access

Two datasets were used. They are never pooled, never jointly trained, and neither serves as external validation for the other. They share 773 normalised keys; 1,555 D1 records and 831 D2 records have a counterpart in the other corpus, so the corpora are not independent.

### B.1 Dataset 1 (D1) — Malayalam-containing subset of the Dravidian SMS corpus

| Field | Value |
|---|---|
| Dataset title | Spam SMS in Dravidian Languages (Spam Message Collection) |
| Authors | Ramanujam Elangovan; Abirami A. M. |
| Publisher | IEEE DataPort |
| Publication date | 2 June 2023 |
| DOI | `10.21227/dcym-pd69` |
| Languages in source | English, Tamil, Telugu, Kannada, Malayalam |
| Labels | Ham / Spam only; "Spam" denotes unsolicited commercial or nuisance messages, **not** phishing or smishing |
| Local file | `Datasets/Spam Message Collection.xlsx`, SHA-256 `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b` |
| Access route | IEEE DataPort, Standard Dataset, subscription-gated, login required |
| Licence displayed on the dataset page | None |
| Recorded permission | **PENDING** |

**Composition of the experiment.** The workbook contains 7,718 physical spreadsheet rows, one of which is entirely blank, leaving 7,717 candidate records. Of these, 1 record carries an invalid label (`Spa,`) and 2 have empty message text, giving 7,714 usable records; the audit counts are 6,322 Ham and 1,394 Spam plus the one malformed Spam label (`subset_audit.json`). The Malayalam-containing subset used in every D1 experiment contains **1,992 records: 1,767 Ham and 225 Spam** (11.30% Spam). Script composition of that subset is **1,489 Malayalam-only records (1,429 Ham / 60 Spam)** and **503 Malayalam-plus-Latin records (338 Ham / 165 Spam)**; no Malayalam record contains Tamil, Telugu or Kannada (`subset_audit.json`).

**Access and permission status.** The local file is consistent with the official record (name, size, two-column layout, language mix, approximate count), and the team holds a local copy. No subscription receipt, institutional access confirmation, download log, invoice or written author permission exists in the project record. As of 8 November 2026 a departmental lecturer has stated an intention to contact the D1 author; no contact and no reply are evidenced. The status is therefore **PENDING** for every separate question: access authorisation, research use, publication of aggregate derived statistics, reproduction of short examples, and redistribution of raw records.

This appendix and the paper it supports report **aggregate derived statistics only**. No raw D1 message, message fragment, screenshot, sample row or workbook extract appears in this document or in any public artifact listed in Section J and the artifact index. D1 has not been redistributed and must not be redistributed until written permission is on file.

### B.2 Dataset 2 (D2) — English/Latin SMS phishing corpus

| Field | Value |
|---|---|
| Dataset title | SMS Phishing Dataset for Machine Learning and Deep Learning |
| Authors | Sandhya Mishra; Devpriya Soni |
| Publisher | Mendeley Data, version 1 |
| Publication date | 20 June 2022 |
| DOI | `10.17632/f45bkkt8pr.1` |
| Licence | CC BY 4.0 (displayed on the record) |
| Local file | `Datasets/Dataset_5971.csv`, SHA-256 `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e` |
| Original composition | 5,971 records: 4,844 Ham / 489 Spam / 638 Smishing |
| Source relation | Ham/Spam portion derives from the UCI SMS Spam Collection, linked on the record |

**Experimental subset.** Duplicate control (Section C) identified 37 duplicate groups whose members carry conflicting labels, comprising 76 records. Excluding them yields the experimental corpus of **5,895 records: 4,844 Ham / 450 Spam / 601 Smishing**. All D2 results in this appendix use 5,895, not 5,971. D2 carries no source or collection metadata, so no block-held-out analysis is defined for it.

CC BY 4.0 permits reuse with attribution, but it does not by itself make publication of raw personal SMS content ethically appropriate. No raw D2 message is reproduced here; only aggregate counts and metrics are reported.

### B.3 Distinction between permission categories

Four permissions are distinct and must not be conflated. For D1, all four are **pending or not established**. For D2, availability is public and reuse is licensed, but redistribution of raw message content remains subject to privacy and ethics review.

| Permission | D1 | D2 |
|---|---|---|
| Availability of the dataset | Public record, subscription-gated | Public, open download |
| Permission for research use | Pending | Granted by CC BY 4.0 |
| Permission to publish aggregate derived statistics | Pending | Granted by CC BY 4.0 |
| Permission to reproduce or redistribute raw messages | Not established | Licensed, but withheld here for privacy reasons |

---

## C. Data preprocessing and duplicate control

Preprocessing is implemented once, in `clean_text()` (`Research Work/phase2/p2_common.py`), and the prototype reuses the identical function so that inference cannot drift from training. A test asserts element-wise agreement between the two implementations on all 7,887 frozen rows.

**Unicode and whitespace handling.** Text is normalised to Unicode NFKC. Zero-width space (U+200B), zero-width non-joiner (U+200C), zero-width joiner (U+200D) and the byte-order mark (U+FEFF) are deleted. Non-breaking space (U+00A0) becomes an ordinary space. C0 control characters other than tab, newline and carriage return are replaced by a space; runs of whitespace are collapsed and the result is stripped.

**What is preserved.** Malayalam code points and combining marks are preserved exactly. No transliteration, stemming, stop-word removal or case folding is applied at the cleaning stage (lower-casing is performed by the TF-IDF vectorizer). URLs are preserved. Punctuation, digits and emoji are preserved because they carry signal in SMS spam. Cleaning is idempotent, and the frozen maximum message length is 910 characters.

**Script detection.** Malayalam is detected by the Unicode block U+0D00–U+0D7F, Tamil by U+0B80–U+0BFF, Telugu by U+0C00–U+0C7F, Kannada by U+0C80–U+0CFF and Latin by `[A-Za-z]`. A record is "Malayalam-only script" when it contains Malayalam, contains no Latin and contains no other Indic script; "mixed script" means Malayalam plus Latin. Script detection is **not** language identification: the 1,489 "Malayalam-only" records are records containing Malayalam script, and the corpus is not language-labelled. Romanised Malayalam (Manglish) is **not** identified, and neither model is trained or validated on it; no Manglish claim is made anywhere in this work.

**Exact duplicate grouping.** Identical message strings are grouped first.

**Normalised duplicate grouping.** A normalisation key lower-cases NFKC text, substitutes URLs with the literal token `url`, substitutes digit runs with the literal token `num`, removes punctuation, and collapses whitespace (`norm_key` in `audit_datasets.py`). Because the substitution markers are subsequently stripped of angle brackets, the key contains the ordinary tokens `url` and `num`; this is documented, verified by test, and deliberately not changed because altering it would move frozen group identifiers and therefore the splits.

**Fuzzy duplicate grouping (D1 only).** Within D1, candidate pairs are generated by a character n-gram TF-IDF index (`char_wb`, 3–5 grams, `min_df=2`, sublinear term frequency) and merged when cosine similarity is at least 0.90 **and** token Jaccard similarity is at least 0.60, or when cosine similarity is at least 0.97. Merging is transitive, implemented with a union–find structure. This threshold is a documented heuristic (Section K).

**D2 grouping.** D2 uses exact and normalised grouping only. Fuzzy matching over short English texts risks merging generic templates, and D2 is the secondary experiment.

**Conflicting labels.** A group is conflicting when its members do not share one label. D1 has no conflicting groups (0 groups, 0 records). D2 has 37 conflicting groups covering 76 records; these are excluded before splitting, so no record with an internally inconsistent label reaches training or evaluation. After grouping, D1 contains 1,824 groups over 1,992 records and D2 contains 5,663 groups over 5,895 records. Re-running the D1 pipeline reproduces all 1,824 group identifiers exactly, and the test suite asserts this.

---

## D. Split and leakage prevention

Both datasets use one protocol: a duplicate-group-aware, label-stratified 70/15/15 assignment with NumPy `default_rng(42)`. Within each label stratum, groups are shuffled, sorted by decreasing size, and assigned to the split with the largest remaining record deficit relative to its target. This keeps class ratios close to the requested proportions while never dividing a group.

| Dataset | Train | Validation | Test | Total |
|---|---:|---:|---:|---:|
| D1 (Ham / Spam) | 1,394 (1,237 / 157) | 299 (265 / 34) | 299 (265 / 34) | 1,992 |
| D2 (Ham / Spam / Smishing) | 4,127 (3,391 / 315 / 421) | 885 (727 / 68 / 90) | 883 (726 / 67 / 90) | 5,895 |

D1 test groups number 299 with a maximum group size of 1; D2 test groups number 883 with a maximum group size of 1. The descriptive Malayalam-only subset (1,489 records) is reported separately and was never a training target.

**Model selection and evaluation protocol.** All hyperparameter selection used validation macro-F1 only. After selection, each pipeline was refit on training plus validation and evaluated exactly once on the frozen test split. The test split was not used for selection, early stopping, threshold tuning or model choice.

**Leakage controls.** For every split pair in both datasets, group overlap and normalised-key overlap are zero. Record identifiers are disjoint across splits. TF-IDF is a pipeline step, so its vocabulary and inverse document frequencies are estimated on training data only and refit on training plus validation at the final refit stage; no test text, label-derived feature or row identifier enters fitting. Standardisation is not used. Duplicate-aware grouping prevents the same message template from appearing in both training and test.

**What these controls do and do not prevent.** They prevent duplicate-message and near-duplicate-message leakage, and they prevent label information from crossing the split boundary through the grouping key. They do **not** prevent a corpus-level confound: messages collected from the same campaign, sender or collection batch are not identified as such, because no source labels exist. D1 contains three populated consecutive row blocks, and 94.7% of its Spam lies in one of them. The split therefore shares the dominant spam campaign between training and test even though it shares no duplicate. This is quantified in Section G and is the principal scientific limitation of the design.

**Hashes.** The six split files and the split manifest are frozen; their SHA-256 values are recorded in `phase2/splits/split_manifest.json` and re-asserted on every audit run:

| Split file | SHA-256 |
|---|---|
| `d1_malayalam_train.csv` | `bd4f5edb59ce2579f21a2ac9eca4a3b9968b499f15780cfa9a3bee306204ddc1` |
| `d1_malayalam_val.csv` | `5bcc228f338b2685e2d5887f48815ba80579b670a71b4a0df6c0989243487f1f` |
| `d1_malayalam_test.csv` | `3922f037a2f52045ffc1d682e799880a06311dec9017ff33abef3fdd3d40be0b` |
| `d2_train.csv` | `ad19a6e8042dd4036331cf6920cd77da9cafe16787cd946dd821b3f0b2598499` |
| `d2_val.csv` | `2fc68c050731e90a3e511a8817796a4f3c639d00f0e8dad9a9d0268aa230400f` |
| `d2_test.csv` | `44409491ebb1c4e22d3aa65b76ca6f4e18ad2eb6af1f58380ab7f19236b46c79` |

---

## E. Models and configurations

Two model families were evaluated on D1 and D2, and one transformer on D1 only.

### E.1 Classical pipelines

Both classical models are scikit-learn `Pipeline` objects with a TF-IDF vectoriser followed by a linear classifier.

**Vectoriser.** `TfidfVectorizer(min_df=2, sublinear_tf=True, lowercase=True, max_features=300_000)` with `analyzer="char_wb"` and `ngram_range=(2, 4)` for every selected model. Four configurations were compared on validation (`word` 1–1, `word` 1–2, `char_wb` 2–4, `char_wb` 2–5) crossed with C ∈ {0.5, 1.0, 2.0} for each family, giving 24 fits per task; the full grids are preserved in `phase2/metrics/d1_malayalam_validation_grid.csv` and `d2_validation_grid.csv`.

**Logistic Regression.** `C` as selected, `class_weight="balanced"`, `max_iter=5000`, `solver="liblinear"` for the binary D1 task and `"lbfgs"` for the three-class D2 task.

**Linear SVM.** `LinearSVC`, `C` as selected, `class_weight="balanced"`, `max_iter=10000`, `dual="auto"`, squared-hinge loss (the scikit-learn default).

**Selected configurations.**

| Task | Family | Configuration | C | Validation macro-F1 | Test role |
|---|---|---|---:|---:|---|
| D1 | Linear SVM | `char_wb` 2–4 | 0.5 | 0.9830 | Primary D1 model; deployed in the prototype |
| D1 | Logistic Regression | `char_wb` 2–4 | 1.0 | 0.9748 | Comparison model |
| D2 | Logistic Regression | `char_wb` 2–4 | 1.0 | 0.9048 | Primary D2 model; deployed in the prototype |
| D2 | Linear SVM | `char_wb` 2–4 | 0.5 | 0.9030 | Comparison model |

Feature counts observed in the prototype model cards are 20,629 (D1 SVM) and 24,293 (D2 LR). Saved artifacts: `d1_malayalam_linear_svm.joblib` (`9ba1dcd62655bf501f4b0297d543bd232ad1348ab476c2efca9b07e0b97225cd`), `d1_malayalam_logreg.joblib` (`fd4a1542436fc81890b117cdeba6cd1e3753bb1f0e832875068908a117af6e69`), `d2_linear_svm.joblib` (`5de720cfcc7fe7179e976b6e2bb3e0410d1ca04145003dfcb8cb3ce5c5ea042e`), `d2_logreg.joblib` (`6f8cd0e5498f672bd71ddeaf494284f3c7aad6315bc39dbfb449f0cf388dc856`).

### E.2 MuRIL (D1 only)

Fine-tuning used the pre-trained checkpoint `google/muril-base-cased` with a sequence-classification head (`BertForSequenceClassification`: 12 layers, 768 hidden units, 12 attention heads, 197,285-token vocabulary, dropout 0.1).

| Setting | Value |
|---|---|
| Maximum sequence length | 128 tokens (mean 32.53, median 31, 99th percentile 90.09, 100% coverage) |
| Optimiser | AdamW, weight decay 0.01 |
| Learning rate | 2 × 10⁻⁵ |
| Schedule | Linear warm-up over 10% of steps, then linear decay |
| Batch size | 4 with gradient accumulation 2 (effective batch 8) |
| Maximum epochs | 6, early stopping patience 2 on validation macro-F1 |
| Loss | Class-weighted cross-entropy, weights capped at 10 (seed 42: 0.5635 Ham / 4.4395 Spam) |
| Precision | Mixed precision (FP16 with gradient scaling) |
| Evaluation batch | 32 |
| Seeds | 42, 43, 44 |
| Saved reference artifact | `phase2/models/muril_d1_seed42/` (config, tokenizer, 913 MB `model.safetensors`) |

Early stopping used validation macro-F1 only, per seed. For the block experiments, each seed reused the epoch count selected on the random validation split; the held-out block was never used for stopping or tuning. Test and held-out predictions were produced once per seed. Seed 42 required 4 epochs and selected epoch 2.

**Saved MuRIL artifact hashes.** `config.json` `e4fa4dc7d8ddc0733add99d10c19403d1d5ebf5ff43d3d22bdf8ef1a9d1ae972`; `model.safetensors` `88a459fedef334dbc203e7e8dcd344aa10f59711c8d313578156b1727ad14e8b`; `tokenizer.json` `2c404b60e22d168964a9a133d043002311a1049cfa9f2663a7a23e9fcd8e1cf8`; `tokenizer_config.json` `a9a744fdd6a0788619337f5ce2447e70eb92c9efb30f8570ecac929069709816`.

**MuRIL on D2.** MuRIL was **not** trained or evaluated on D2. No transformer result is reported for the English corpus.

**Partially unrecoverable MuRIL settings.** The exact revision of the pre-trained checkpoint on the model hub, the training-time GPU driver and CUDA library versions beyond `torch 2.11.0+cu128` and CUDA 12.8, the `tokenizers` version, cuDNN determinism flags, the optimiser state, and the per-epoch random state are **not recoverable from available project records**. The three seeds were set with `torch.manual_seed` and `torch.cuda.manual_seed_all`, but full bitwise reproducibility of the fine-tuning run cannot be claimed and is not claimed here. Only the frozen predictions and metrics of the MuRIL runs are verified.

---

## F. Evaluation metrics and statistical uncertainty

**Metrics.** Accuracy, per-class precision, recall and F1, macro-F1 (the unweighted mean over the fixed class set), and confusion matrices. Precision, recall and F1 use `zero_division=0`. For D1, Macro-F1 is the unweighted mean over Ham and Spam; for D2, over Ham, Spam and Smishing.

### F.1 D1 grouped-random test (299 records: 265 Ham / 34 Spam)

| Model | Accuracy [95% CI] | Macro-F1 [95% CI] | Ham P / R / F1 | Spam P / R / F1 | Confusion matrix |
|---|---|---|---|---|---|
| Logistic Regression | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9121, 0.9903] | 0.9815 / 1.0000 / 0.9907 | 1.0000 / 0.8529 / 0.9206 | `[[265, 0], [5, 29]]` |
| Linear SVM | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.8824 / 0.9375 | `[[265, 0], [4, 30]]` |
| MuRIL seed 42 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.8824 / 0.9375 | `[[265, 0], [4, 30]]` |
| MuRIL seed 43 | 0.9833 [0.9666, 0.9967] | 0.9556 [0.9099, 0.9903] | 0.9815 / 1.0000 / 0.9907 | 1.0000 / 0.8529 / 0.9206 | `[[265, 0], [5, 29]]` |
| MuRIL seed 44 | 0.9866 [0.9732, 0.9967] | 0.9650 [0.9250, 0.9922] | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.8824 / 0.9375 | `[[265, 0], [4, 30]]` |
| MuRIL mean ± SD | 0.9855 ± 0.0019 | 0.9619 ± 0.0054 | 0.9919 ± 0.0009 | 0.9319 ± 0.0097 (recall 0.8725 ± 0.0170) | — |

Precision intervals are percentile group-bootstrap intervals unless stated otherwise. Exact and Wilson intervals are reported separately below.

### F.2 D2 test (883 records: 726 Ham / 67 Spam / 90 Smishing)

| Model | Accuracy [95% CI] | Macro-F1 [95% CI] | Spam P / R / F1 | Smishing P / R / F1 | Confusion matrix |
|---|---|---|---|---|---|
| Logistic Regression | 0.9638 [0.9513, 0.9762] | 0.8877 [0.8482, 0.9239] | 0.7857 / 0.8209 / 0.8029 | 0.9250 / 0.8222 / 0.8706 | `[[722, 0, 4], [10, 55, 2], [1, 15, 74]]` |
| Linear SVM | 0.9638 [0.9513, 0.9762] | 0.8825 [0.8408, 0.9196] | 0.7761 / 0.7761 / 0.7761 | 0.9487 / 0.8222 / 0.8810 | `[[725, 0, 1], [12, 52, 3], [1, 15, 74]]` |

### F.3 Exact and Wilson intervals

Interval estimation uses both the exact Clopper–Pearson method and the Wilson score method, because the test sets are small and several proportions are at a boundary.

| Quantity | Count | Clopper–Pearson 95% | Wilson 95% |
|---|---|---|---|
| SVM Spam precision | 30/30 | [0.8843, 1.0000] | [0.8865, 1.0000] |
| LR Spam precision | 29/29 | [0.8806, 1.0000] | [0.8830, 1.0000] |
| SVM Spam recall | 30/34 | [0.7255, 0.9670] | — |
| LR Spam recall | 29/34 | [0.6894, 0.9505] | — |
| False-positive rate, 0/265 Ham | 0/265 | upper bound 1.382% | upper bound 1.429% |

Perfect observed precision is therefore reported with its lower bound, never as certainty. Zero observed false positives among 265 Ham is compatible with a true false-positive rate as high as 1.382%. Nearly all predicted Spam messages fall in one row block crowded with Spam, so this is a within-campaign observation and not a deployment guarantee; the denominator for precision is predicted positives (29 or 30), not the full test set.

### F.4 Bootstrap procedure

Confidence intervals for accuracy, macro-F1 and per-class metrics use a percentile bootstrap with 2,000 replicates, seed 42, 2.5% and 97.5% limits. The resampling unit is the duplicate group, and one shared sequence of resamples is used for every model within a paired comparison, so paired differences are computed on identical resamples. No replicate lost the Spam class in D1 or D2. Because every frozen test group is a singleton (299/299 and 883/883), the procedure is numerically a message-level bootstrap; this was verified rather than assumed. It captures sampling variability of messages from the same frozen test set. It does **not** capture variation across collection sources, campaign or template clustering beyond exact duplicates, temporal drift, annotation uncertainty or model-selection uncertainty. It is therefore not a source-cluster bootstrap and is never described as one.

### F.5 Paired comparisons

| Comparison | Metric | Difference [95% CI] | Interpretation |
|---|---|---|---|
| SVM − LR | Macro-F1 | +0.0093601 [0.0000, 0.0321432] | One test message; not significant |
| SVM − LR | Spam recall | +0.0294118 [0.0000, 0.0975610] | Same single message |
| SVM − LR | Accuracy | +0.0033445 [0.0000, 0.0100334] | Same single message |
| LR − SVM | Macro-F1 | −0.0093601 [−0.0321432, 0.0000] | Exact negation of the above |
| SVM − mean(MuRIL) | Macro-F1 | +0.0031200 [0.0000, 0.0101002] | Interval includes zero |
| SVM − mean(MuRIL) | Accuracy | +0.0011148 [0.0000, 0.0033445] | Interval includes zero |
| SVM − mean(MuRIL) | Spam recall | +0.0098039 [0.0000, 0.0303030] | Interval includes zero |
| LR − SVM (D2) | Macro-F1 | +0.0052393 [−0.0120572, 0.0244165] | Interval includes zero |

The LR–SVM comparison is supplied in both directions because an earlier report displayed the SVM−LR point estimate beside the LR−SVM interval, which produced an apparent contradiction. The paired file defines the difference as LR − SVM; the reverse comparison is the exact negation of both the point estimate and the interval bounds. The two models disagree on exactly one test message (LR wrong, SVM correct). Consequently, 36.85% of shared bootstrap resamples contain neither member of the discordant pair and are exactly tied, no resample favours SVM, and the percentile upper bound is exactly 0. The exact two-sided discordance test gives p = 1.0. Linear SVM is not statistically superior to Logistic Regression; the preferred model is chosen for deterministic simplicity, not proven accuracy.

### F.6 Seed variation and the three-seed mean

MuRIL was fine-tuned with seeds 42, 43 and 44. Macro-F1 values are 0.9650, 0.9556 and 0.9650; mean 0.9619, across-seed SD 0.0054. Seeds 42 and 44 produce predictions identical to the Linear SVM; seed 43 differs by one Spam false negative. The three seeds therefore provide a stability check, not three independent replications of a transformer advantage, and they supply only one distinct comparison point against the SVM.

Three uncertainty quantities are distinguished and must not be conflated:

| Quantity | Value | Meaning |
|---|---|---|
| Across-seed SD | 0.0054 | Variation among three fitted seeds only; not a confidence interval |
| Individual-seed bootstrap SD | ≈ 0.018 | Test-sample uncertainty for a single frozen prediction set |
| Conditional three-seed mean interval | Macro-F1 [0.9211, 0.9909]; accuracy [0.9710, 0.9967]; Spam recall [0.7500, 0.9678] | Test-sample uncertainty for the average of these three frozen predictions |

The conditional interval is not an expected-performance interval for a future training run; three seeds cannot estimate that. None of these intervals measures uncertainty across unseen collection sources.

---

## G. Row-block robustness experiment

Because D1 carries no source labels, consecutive workbook rows were used as a proxy for collection batches. Rows are partitioned into 1,000-row blocks by the authoritative formula `block_number(source_row) = (source_row − 1) // 1000 + 1`. Three blocks contain the 1,992 Malayalam records:

| Block (workbook rows) | Records | Ham | Spam |
|---|---:|---:|---:|
| 4001–5000 | 630 | 618 | 12 |
| 5001–6000 | 991 | 991 | 0 |
| 6001–7000 | 371 | 158 | 213 |

**Method.** Pooled leave-one-row-block-out stress test: hold out one complete block, train on the other two, predict the held-out block, concatenate all held-out predictions, then compute one metric over the concatenated predictions. The reported value is not an average of fold scores. Each MuRIL seed reuses the epoch count selected on the random validation split.

| Model | Pooled accuracy | Pooled Macro-F1 | Spam precision | Spam recall |
|---|---:|---:|---:|---:|
| Logistic Regression | 0.8865 | 0.5448 | 0.4878 | 0.0889 |
| Linear SVM | 0.8901 | 0.5378 | 0.6071 | 0.0756 |
| MuRIL seed 42 | 0.8845 | 0.4979 | 0.3684 | 0.0311 |
| MuRIL seed 43 | 0.8896 | 0.5006 | 0.7778 | 0.0311 |
| MuRIL seed 44 | 0.8855 | 0.5098 | 0.4348 | 0.0444 |
| MuRIL mean ± SD | 0.8865 | 0.5028 ± 0.0062 | 0.5270 ± 0.2197 | 0.0356 ± 0.0077 |

Per-block Macro-F1: block 4001–5000 — LR 0.6964, SVM 0.6964, MuRIL mean 0.8306 (12 Spam); block 5001–6000 — LR 0.4946, SVM 0.4972, MuRIL mean 0.4987 (0 Spam); block 6001–7000 — LR 0.3825, SVM 0.3685, MuRIL mean 0.2987 (213 Spam). The pooled LR − SVM difference is +0.00695 [−0.00425, 0.02170], which includes zero; no model is claimed superior under block holdout.

**Interpretation and limitations.** The random split shares the Spam-dense block 6001–7000, which contains 213 of the 225 D1 Spam, between training and test; holding that block out leaves only 12 Spam in training, and every model collapses on its 213 Spam. Row blocks are **row-order proxies, not verified collection sources**. Only three blocks exist, one contains no Spam, its per-fold Macro-F1 is an artefact of an absent class and is not averaged as if balanced, and the critical block leaves only 12 Spam in training. This experiment quantifies sensitivity to corpus order and campaign concentration; it is **not external validation** and does not establish behaviour on unseen real-world sources. A supplementary structure-only diagnostic (message length, digits, URL presence, Latin characters and script) reached Macro-F1 0.8706 on the random split without using text content, and block identity alone reached 0.8423, confirming that metadata and row order carry substantial label information in this corpus.

---

## H. Final verification procedure

All verification is executed by one script, which runs every check independently and never stops at the first failure.

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/run_full_audit.py"
```

The single command is required to be run from the project root inside the pinned environment. `PYTHONIOENCODING=utf-8` prevents a console-encoding error when Malayalam text reaches standard output on a non-UTF-8 Windows console; the script also sets UTF-8 for its child processes. A `--write-baseline` flag records the 39 frozen-artifact hashes before a change window, and `--skip-tests` omits the regression suite for diagnosis only.

**Verified result of the frozen run** (`Research Work/phase2/metrics/full_audit_results.json`, run `20261108T171120Z`):

| Check | Result | Duration |
|---|---|---:|
| `environment` | All pinned versions importable | 3.79 s |
| `required_files` | 26 required files present and non-empty | 0.00 s |
| `dataset_integrity` | Source hashes and row counts match | 0.92 s |
| `split_hashes` | 6/6 frozen splits match the manifest | 0.01 s |
| `model_hashes` | 4/4 classical models match the manifest | 0.01 s |
| `baseline_hashes` | 39/39 frozen artifacts byte-identical to baseline | 0.87 s |
| `regression_tests` | 125/125 tests pass, exit 0 | 12.86 s |
| `frozen_predictions` | Independent metric recomputation, exit 0 | 4.82 s |
| `statistical_audit` | Intervals, paired comparisons and blocks recomputed, exit 0 | 6.19 s |
| `prototype_verification` | 4/4 model hashes, 6/6 split hashes, parity, exit 0 | 4.16 s |
| `literature_validation` | 24 records / 23 active, workbook = CSV = register | 1.21 s |
| `browser_ui_evidence` | 16 recorded browser cases, all PASS (informational) | 0.00 s |
| `code_risk_checks` | 10 static invariants | 0.02 s |
| `verification_stability` | Frozen metrics identical before and after the run | 0.03 s |
| `post_run_hash_stability` | All frozen artifacts identical to the baseline afterwards | 0.00 s |

**Summary: 15 checks, 15 passed, 0 failed, exit code 0, 34.9 s.** Fourteen checks are required and decide the exit status; the browser-evidence check is informational because it validates a recorded pass rather than launching a browser. Durations are machine-dependent and are not a performance claim. The regression suite comprises 125 tests with 0 failures, 0 errors and 0 skipped.

**What the audit establishes.** It establishes that the environment matches its pins, that both source datasets and all six splits hash-match their manifests, that all four classical models and the four MuRIL files are unmodified, that every frozen prediction file aligns to its split by record identifier, that the published metrics and intervals recompute from the frozen predictions, that the prototype reproduces all 1,182 frozen test predictions through both its batch and public interfaces, that the literature workbook agrees with its verification register, and that no frozen artifact changed during the run. The three verification JSON files rewritten by their own child scripts are restored byte-for-byte afterwards, and that restoration is itself hash-checked.

**What the audit cannot establish.** It cannot establish dataset permission, source independence, field performance, or the correctness of MuRIL training hyperparameters; it checks the MuRIL artifacts by hash only and never loads or retrains the transformer. It proves internal consistency and artifact stability, not external validity.

---

## I. Prototype reproducibility

A local Streamlit application (Streamlit 1.67.0) exposes the frozen models for interactive inspection.

**Selected models.** D1 uses the Linear SVM pipeline (`char_wb` 2–4, C = 0.5); D2 uses the Logistic Regression pipeline (`char_wb` 2–4, C = 1.0). Model cards display the selected configuration, feature count and the frozen within-corpus and block-held-out scores.

**Public inference interface.** `inference.py` exposes batch and single-message prediction for both tasks. Before `joblib.load`, the loader computes the SHA-256 of the artifact and refuses to deserialise it unless the digest matches `prototype/model_manifest.json`; a mismatch is reported as an error rather than executing a tampered pickle. Text is cleaned with the same `clean_text()` used in training, so inference cannot drift from the frozen preprocessing.

**Input validation.** Inputs are rejected when they are `None`, empty or whitespace, bytes, control-character-only, or longer than 5,000 characters. D1 requires Malayalam script; D2 requires Latin characters. Mixed-script input in D1 is accepted with an explicit warning that the model was trained mostly on Malayalam-script text; Malayalam-only input in D2 is rejected. The 5,000-character cap is far above the longest frozen message (910 characters) and does not alter behaviour on observed inputs. No user text is logged, written to disk or transmitted.

**Prediction parity.** `verify_prototype.py` reproduces **299/299** D1 and **883/883** D2 frozen test predictions through the saved pipelines and again through the public single-message functions, with **299/299** and **883/883** cleaning parity. All four model hashes and all six split hashes match their manifests. These results are regenerated on every audit run.

**Interface testing.** Eleven widget-level tests drive the application through `streamlit.testing.v1.AppTest`, covering both detector pages, Malayalam and Latin predictions, wrong-script rejection in both directions, mixed script, empty input, the 5,000-character widget cap, control characters, dashboard tabs and tables, and the missing-artifact path, which now renders an inline error instead of a blank page. A separate live browser pass over 16 cases was recorded on a loopback server (Section H, `browser_ui_test_results.json`): D1 Spam and Ham predictions, D1 Latin rejection, empty-input warning, D2 Ham prediction with score table, mixed-script warning, dashboard rendering with five tabs, six metrics, ten tables and eleven charts, the block-holdout tab, and an inline model-loading failure. Console errors were zero, and outbound network requests were zero after Streamlit usage statistics were disabled in `.streamlit/config.toml`.

**Scope.** All testing was local, bound to `127.0.0.1`. The application was never deployed or exposed beyond the loopback interface. The browser pass used the packaged Chromium driver; native pointer events at page coordinates proved unreliable in that panel, so interactions were dispatched as DOM events on the same widgets, and the widget runtime is additionally covered by the framework's own test driver. Prototype parity establishes that the saved predictions are reproducible through the application. It does **not** establish field performance, and the interface has not received a visual/CSS, mobile-viewport, concurrency or accessibility-tooling audit.

---

## J. Artifact integrity and preservation

**Policy.** Every artifact that participates in a reported result is frozen and hash-verified. A SHA-256 baseline of 39 artifacts was recorded before the engineering-closure change window (`phase2/metrics/audit_hash_baseline.json`, created 2026-11-08T16:16:45Z). Every audit run recomputes all 39 digests before and after its checks, and the run fails if any digest differs. No artifact may be regenerated to make a check pass, and no reported metric may be recomputed and silently overwritten. Verification outputs that scripts necessarily rewrite are copied beforehand and restored byte-for-byte afterwards.

**Tracked categories.** 2 source datasets; 7 split files (6 experimental splits plus 1 descriptive Malayalam-only split); 4 classical `joblib` pipelines; 4 MuRIL files (config, tokenizer, tokenizer configuration, 913 MB weight file); 17 frozen prediction files (5 D1 test, 2 D2 test, 9 block-held-out MuRIL, 1 block cross-validation); 2 manifests (split manifest, model manifest); 3 verification outputs.

**Result.** All **39/39** artifacts were byte-identical to the pre-change baseline at the end of the final run, and the audit's `post_run_hash_stability` check confirms this after the checks themselves executed. No dataset, label, split, model, prediction or headline metric was modified during the engineering closure or during preparation of this appendix. The complete per-artifact hash list, with purpose and sharing restrictions, is given in `Admin/IEEE_REPRODUCIBILITY_ARTIFACT_INDEX.md`.

**Key digests.**

| Artifact | SHA-256 |
|---|---|
| D1 workbook | `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b` |
| D2 CSV | `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e` |
| `split_manifest.json` | `4c67a5cce2a3b1982e0aa64a49bfe80ad6cde9b7194fa3062d1eae384f9653a7` |
| `model_manifest.json` | `f36ec570855adec7b0975c5ba8b8ffe0d71f33c2b558572f4d91e2d9bbf8a4b3` |
| D1 Linear SVM | `9ba1dcd62655bf501f4b0297d543bd232ad1348ab476c2efca9b07e0b97225cd` |
| D1 Logistic Regression | `fd4a1542436fc81890b117cdeba6cd1e3753bb1f0e832875068908a117af6e69` |
| D2 Linear SVM | `5de720cfcc7fe7179e976b6e2bb3e0410d1ca04145003dfcb8cb3ce5c5ea042e` |
| D2 Logistic Regression | `6f8cd0e5498f672bd71ddeaf494284f3c7aad6315bc39dbfb449f0cf388dc856` |
| MuRIL `model.safetensors` | `88a459fedef334dbc203e7e8dcd344aa10f59711c8d313578156b1727ad14e8b` |

---

## K. Known reproducibility limitations

1. **D1 author permission is pending.** No accession record or written permission exists. Access authorisation, research use, publication of aggregate statistics, example reproduction and raw redistribution are all unresolved. Only aggregate derived statistics may be published, and D1 content must not be redistributed.
2. **No external, source-diverse Malayalam test set exists.** All D1 intervals are within-corpus, message-level intervals. No claim of generalisation to other senders, campaigns or collection routes is supported, and none is made.
3. **Row blocks are not verified collection sources.** The three-block experiment is a stress test over row-order proxies; it has one block without Spam and one block with only 12 training Spam, and it is not external validation.
4. **Some MuRIL training settings are partially unrecoverable.** The pre-trained checkpoint revision, training-time GPU driver and CUDA library versions beyond torch/CUDA 12.8, the tokenizers version, cuDNN determinism settings and optimiser state are not recorded. Bitwise reproduction of the fine-tuning run is therefore not claimed; only its frozen predictions and metrics are verified.
5. **The fuzzy duplicate threshold is heuristic.** Cosine similarity ≥ 0.90 with token Jaccard ≥ 0.60 (or cosine ≥ 0.97) is a documented rule, not a validated optimum. A different threshold would move a small number of groups and could shift borderline metrics; sensitivity was not tested because it would require regrouping frozen data.
6. **URL normalisation collapses different URLs to a common placeholder.** `norm_key` replaces every URL with the token `url` and every digit run with `num`. Grouping is deterministic and duplicate control remains effective, but the key is less discriminative than the raw text. It was deliberately not changed because it would move frozen group identifiers and splits.
7. **Historical manifest and robustness outputs are preserved rather than rewritten.** The descriptive block table inside `split_manifest.json` records 631/991/370, whereas recomputation from the frozen splits gives 630/991/371 (one training record at a block boundary). The historical `d1_block_robustness.json` was produced with the superseded block formula. Both are retained unmodified for artifact integrity, are labelled historical, and are pinned by tests; the corrected values in this appendix come from `p2_validate.py` output and the authoritative `block_number()` formula.
8. **The user interface has not received a full visual, responsive or accessibility audit.** Widget behaviour, both detector pages, warnings, error states and the dashboard are tested, but CSS quality, mobile viewports, two concurrent sessions and accessibility tooling are unverified.
9. **No clean environment was rebuilt.** Dependencies are pinned and their versions are asserted at run time, but the pins were verified in the existing project environment rather than through a from-scratch installation; the MuRIL/CUDA stack was not reinstalled.
10. **The two corpora are not independent.** They share 773 normalised keys and overlap in content; no pooled training, pooled test or cross-corpus validation claim is made, and D2 is not external validation for D1.
11. **Manglish (Romanised Malayalam) is unsupported.** Neither model is trained or validated on it, and script detection is not language identification.
12. **Threshold and calibration analyses are descriptive.** No deployment threshold was selected or validated, and the prototype uses the default decision boundary.

---

## L. Reproduction classification

Three distinct levels of reproducibility are supported to different degrees.

**Level 1 — Verification reproducibility: SUPPORTED.** A researcher holding this repository, both source datasets and the frozen artifacts can execute the single command in Section H and obtain the same 15/15 check results, the same 125 test outcomes, the same hashes and the same metric values, without retraining anything. This is the level exercised and evidenced in this appendix.

**Level 2 — Computational reproduction: PARTIALLY SUPPORTED.** Predictions and metrics are fully reproducible from the frozen splits, models and code (Level 1 covers this). Retraining the four classical pipelines is reproducible in principle, because the splits, seed, grids and library versions are pinned and the estimators are deterministic given those inputs, but it was not re-executed here because doing so would overwrite frozen model artifacts. Re-running the D1 duplicate pipeline and the split algorithm reproduces group identifiers and split membership exactly. MuRIL fine-tuning is **not** fully reproducible, because the checkpoint revision and several run-time settings are unrecoverable; only its frozen outputs are verified.

**Level 3 — External validation: NOT AVAILABLE.** No independent, source-diverse Malayalam SMS corpus was used. The row-block experiment is an internal stress test, not external validation, and no result in this work should be described as external validation.

---

## M. Minimal reproduction checklist

1. Install Python 3.14 and create a project-local virtual environment.
2. Install `Research Work/requirements-verification.txt` and `Research Work/prototype/requirements.txt`.
3. Place both datasets at their recorded paths and confirm their SHA-256 digests against Section J.
4. Run the single audit command from Section H and confirm 15/15 checks, 125 tests and exit code 0.
5. Compare the regenerated `full_audit_results.json` with the preserved copy under `metrics/audit_runs/20261108T171120Z/`.
6. For the prototype, launch Streamlit on `127.0.0.1` and confirm 299/299 and 883/883 parity via `verify_prototype.py`.
7. Do not run the split, training or MuRIL scripts unless a new experiment is intended; they overwrite frozen artifacts.
