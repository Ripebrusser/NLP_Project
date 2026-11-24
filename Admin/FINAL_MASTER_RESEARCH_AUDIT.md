# Final Master Research Audit

**Audit date:** 8 November 2026  
**Scope:** complete workspace, frozen D1/D2 artifacts, statistical recomputation, paper-by-paper literature verification, provenance and paper readiness.  
**Status:** completed adversarial audit. This is not a claim that no weakness remains.

---

## 1. Direct verdict

The frozen experiments are technically reproducible and the headline arithmetic is internally consistent after correction. The project is **not yet ready for final IEEE submission** because:

1. D1 access authorisation and publication permission are **not evidenced**.
2. FSSHAP has been verified only at abstract/metadata level; its exact use of D1 and its numerical results cannot be asserted.
3. Several secondary literature records remain abstract-only or metadata-only.
4. The D1 result is a within-corpus result with a severe row-order confound; it does not establish transfer to another source.
5. No source-diverse Malayalam test set exists, and none can be manufactured from the frozen data.

The project **is ready for supervisor review as a bounded evaluation study**, provided the paper reports the random-split and row-block results together and makes no deployment, phishing, Manglish, or external-validation claim.

---

## 2. What was independently inspected

- All six frozen split files and their hashes.
- All five D1 prediction files, both D2 prediction files, and all nine MuRIL block prediction files.
- `p2_final_verification.py`, `p2_final_audit_stats.py`, `p2_stats.py`, `p2_validate.py`, the saved metric JSON files, the block comparison CSV and the duplicate/split manifests.
- The original D1 workbook and D2 CSV by hashes, row counts, labels, script categories and source-row blocks.
- `Admin/`, `Research Work/phase2/`, `Research Work/prototype/`, `Literature Review/`, and the existing audit reports.
- Official records and accessible full texts for the directly relevant literature, including Almeida et al. (2011), Mahmood and Hameed (2023), MuRIL (2021), PhishNet (2026), Filali et al. (2026), Amaral Cejas et al. (2026), DravidianCodeMix (2022), and the D1/D2 dataset records.

No model was retrained, no split was regenerated, no label was changed and no frozen prediction was rewritten.

---

## 3. Authoritative document map

| Information type | Authoritative document |
|---|---|
| Final metrics and denominators | `Admin/CANONICAL_FINAL_RESULTS.md` |
| One objective, scope and method | `Admin/FINAL_METHODOLOGY_AND_OBJECTIVE.md`; `Admin/FINAL_OBJECTIVE_AND_SCOPE.md` |
| Statistical calculations and interpretation | `Admin/FINAL_STATISTICAL_AUDIT.md` |
| Technical reproduction | `Admin/FINAL_TECHNICAL_VERIFICATION.md`; `Admin/VERIFICATION_REPORT.md` |
| Dataset permission and provenance | `Admin/DATASET_PROVENANCE_AND_PERMISSIONS.md`; `Admin/D1_PERMISSION_REQUEST_AND_CHECKLIST.md` |
| Literature verification | `Admin/LITERATURE_VERIFICATION_REGISTER.md`; `Admin/LITERATURE_AUDIT_STATUS.md` |
| Connected literature review | `Admin/FINAL_LITERATURE_REVIEW.md` |
| Claims permitted in the paper | `Admin/FINAL_CLAIM_EVIDENCE_LEDGER.md` |
| Remaining actions | `Admin/FINAL_ACTION_REGISTER.md` |
| Submission verdict | `Admin/FINAL_PAPER_READINESS_REPORT.md` |

`RESEARCH_SCOPE_AND_LABEL_DECISION.md`, `FINAL_AUDIT.md` and `BLOCKER_CLOSURE_REPORT.md` are now explicitly marked **historical/superseded**. They are retained for provenance, not current citation.

---

## 4. Findings and resolutions

Severity: **Critical** = blocks submission or invalidates a headline claim; **High** = reviewer-visible error or unsupported claim; **Medium** = misleading or inconsistent record; **Low** = housekeeping.

| ID | Finding | Severity | Evidence | Resolution | Status |
|---|---|---|---|---|---|
| F01 | `FINAL_MODEL_SELECTION.corrected.md` reported `SVM vs LR: +0.0094 [−0.0321, 0.0000]`. The point estimate is SVM−LR but the interval is LR−SVM. | **Critical** | `paired_model_comparison.json`; independent recomputation | Replaced with **SVM−LR +0.0093601 [0.0000, 0.0321432]** and the separate LR−SVM negative direction. Added to canonical results. | Fixed |
| F02 | The interval looked as though the observed difference lay outside it. | **High** | 2,000 shared group-bootstrap draws | Explained: 36.85% of resamples contain neither member of the single discordant pair and are exactly tied at zero; 63.15% are negative; none are positive. The point is inside. This is discrete bootstrap behaviour, not a biased interval. | Fixed by explanation |
| F03 | The LR–SVM “difference” could be read as model superiority. | **High** | Frozen predictions | The models disagree on **one** test message. Exact two-sided discordance p = 1.0. Report as no evidence of superiority. | Fixed |
| F04 | MuRIL seeds 42 and 44 were treated in places as independent confirmations of a transformer advantage. | **High** | Seed prediction CSVs | Their predictions are identical to the SVM; seed 43 is one Spam false negative worse. The three seeds provide one distinct comparison, not three independent ones. | Fixed |
| F05 | Multiple objective structures survive across documents (seven objectives in the historical scope file, three research questions elsewhere). | **High** | `RESEARCH_SCOPE_AND_LABEL_DECISION.md`; `FINAL_METHODOLOGY_AND_OBJECTIVE.md` | Historical file marked superseded. One objective adopted in the authoritative methodology and objective/scope documents; three RQs remain explicitly separate. | Fixed |
| F06 | D1 permission had earlier been called “resolved” from platform-level terms. | **Critical** | `BLOCKER_CLOSURE_REPORT.md`; no receipt, invoice, download log or author letter | Withdrawn. D1 remains **PENDING**. A request/checklist and provenance status are supplied. | **Open — external** |
| F07 | FSSHAP’s dataset use and results were at risk of being inferred from its abstract. | **High** | IEEE Computer Society and ACM records; full text paywalled | Recorded as **abstract/metadata only**. Do not assert exact D1 use, per-dataset counts or numerical results. | **Open — access** |
| F08 | Stale block counts 631/370 and the old 0.3677 fold value persisted in historical artifacts. | **High** | `source_row` recomputation | Correct counts are **630 / 991 / 371**; the critical SVM block-6001 fold is **0.3685**. Historical artifact retained but identified as stale. | Fixed in active record |
| F09 | The Malayalam-only count 1,486 appeared in one report. | **Medium** | `subset_audit.json`; `d1_malayalam.csv` | Correct value **1,489**; 503 Malayalam+Latin; 1,992 total. The 1,486 entry was a table typo. | Fixed |
| F10 | D2’s original and experimental denominators were sometimes conflated. | **High** | `Dataset_5971.csv`; `d2_grouped.csv` | Always distinguish **5,971 original** from **5,895 experimental** after 37 conflicting groups/76 records. All metrics use 5,895. | Fixed |
| F11 | “3/299 ≈ 1.0%” was used for false-positive rate. | **High** | Confusion matrices | FPR denominator is the 265 Ham, not all 299 rows. Correct zero-FP upper bound is **1.382%** exact, **1.429%** Wilson. | Fixed |
| F12 | Structure-only and block-only diagnostics could be mistaken for competing classifiers or causal explanations. | **Medium** | `validation_summary.json`; `p2_validate.py` | Reported as **leakage diagnostics** at 0.8706 and 0.8423 Macro-F1; they show association, not causation. Arithmetic verified from saved confusion matrices; not refitted. | Qualified |
| F13 | “Source-block” and “block-held-out” implied verified collection sources. | **Medium** | Workbook row numbers only | Renamed **pooled leave-one-row-block-out stress test**; blocks are row-order proxies. | Fixed |
| F14 | The prototype README pointed to a local `VERIFICATION_REPORT.md` without distinguishing it from the project-wide report. | **Low** | `Research Work/prototype/README.md` | Clarified that the project-wide verification is `Admin/VERIFICATION_REPORT.md`. | Fixed |
| F15 | Literature verification status was inconsistent: some documents said only one paper had been read in full. | **High** | `LITERATURE_AUDIT_STATUS.md`; `VERIFIED_REFERENCES.md` | Rebuilt paper-by-paper register with explicit full-text / abstract / metadata status. Almeida 2011, Mahmood, MuRIL, PhishNet, Filali, Amaral Cejas and Hassan are now full-text verified where applicable. | Fixed |
| F16 | Several recent records (P03, P06, P09, P11, T01, S01) have only partial access, but some drafts imply otherwise. | **High** | Publisher/index records | Downgraded to abstract-only or metadata-only. No numerical result is quoted for an unread source. | Fixed by qualification |
| F17 | “First Malayalam/Dravidian spam detector” and similar priority claims are contradicted by the Elangovan/Abirami line. | **Critical** | FSSHAP; D1 record; related series | Removed. The contribution is an evaluation/validity study, not a first detector. | Fixed |
| F18 | D2 could be mistaken for external validation of D1. | **Critical** | 773 shared normalised keys; different languages and labels | Explicitly prohibited in all authoritative documents; D2 remains a separate secondary experiment only. | Fixed by scope |
| F19 | Perfect precision could be presented as deployment safety. | **Critical** | 29–30 predicted positives; campaign concentration | Reinterpreted as a within-campaign observation with exact lower bounds of 88.06–88.43% and an FPR upper bound of 1.382%. Not a guarantee. | Fixed |
| F20 | No source-diverse external Malayalam test set exists. | **Critical** | Frozen D1 corpus only | Documented as an unresolvable limitation. No synthetic or newly collected test set was created. | **Open — cannot fix with current data** |

---

## 5. Statistical result of the audit

The authoritative paired results are:

| Comparison | Metric | Difference | 95% percentile interval | Interpretation |
|---|---|---:|---|---|
| LR − SVM | Macro-F1 | −0.0093601 | [−0.0321432, 0.0000] | LR lower by one message |
| SVM − LR | Macro-F1 | +0.0093601 | [0.0000, 0.0321432] | Not significant; p = 1.0 |
| SVM − LR | Spam recall | +0.0294118 | [0.0000, 0.0975610] | One message |
| SVM − LR | Accuracy | +0.0033445 | [0.0000, 0.0100334] | One message |
| SVM − mean(MuRIL 42/43/44) | Macro-F1 | +0.0031200 | [0.0000, 0.0101002] | Not distinguishable |
| SVM − mean(MuRIL) | Spam recall | +0.0098039 | [0.0000, 0.0303030] | Not distinguishable |
| LR − SVM (D2) | Macro-F1 | +0.0052393 | [−0.0120572, 0.0244165] | Not distinguishable |

The D1 row-block result is the substantive finding, not a footnote:

| Model | Grouped random Macro-F1 | Pooled row-block Macro-F1 | Pooled Spam recall |
|---|---:|---:|---:|
| LR | 0.9556 | 0.5448 | 8.89% |
| SVM | 0.9650 | 0.5378 | 7.56% |
| MuRIL mean | 0.9619 | 0.5028 | 3.56% |

The random split is not a source-held-out estimate. The block test is a three-block stress test, not a population estimate.

---

## 6. Literature verdict

**FSSHAP.** Exact title: *FS_SHAP: Global Interpretable Feature Selection Using XAI for the Classification of Spam SMS in Dravidian Languages*. Authors: Ramanujam Elangovan, Abirami A. M., K. G. Thirumalai. *IEEE MultiMedia*, vol. 32, no. 1, pp. 92–103, 2025, DOI `10.1109/MMUL.2024.3508765`. The abstract reports SHAP-based global selection over handcrafted features, a Random Forest model, and three Dravidian-language SMS datasets including Tamil, Kannada, Telugu and Malayalam. It cites the D1 DOI. **The full text is paywalled.** Therefore:

- It is legitimate to say the paper belongs to the same dataset lineage and reports a Random-Forest/SHAP feature-selection study.
- It is **not** legitimate to say FSSHAP used this exact 1,992-row Malayalam subset, reported a specific accuracy, compared transformers, or ignored duplicate leakage, unless the full text is obtained.
- Our differentiation must be framed as **the evaluation question we study** (duplicate-group control, MuRIL comparison, row-block stress, exact uncertainty), not as an assertion about what FSSHAP did not do.

**Elangovan/Abirami line.** D1 is not new. Related work includes the 2023 dataset record, a 2023 hand-crafted-feature study, a 2024 XAI feature-selection conference paper, FSSHAP (2025), NCMDFE (2025), a 2026 *Evolving Systems* paper and the SMSDHL preprint. The defensible novelty is therefore narrow and evaluation-oriented. It is **not** “first Dravidian SMS spam study,” “first use of D1,” or “first Malayalam spam detector.”

**MuRIL.** Khanuja et al. (2021) is a representation-learning paper evaluated on XTREME tasks, with translated/transliterated pretraining signals. It does not establish SMS spam performance. Our MuRIL result is an experiment on D1, not a reproduction of the MuRIL paper and not independent validation of its claims.

**Smishing.** Mahmood and Hameed (2023) report 98.5% accuracy, 96.9% precision, 93.1% detection and 95.05% F1 on an English UCI-derived corpus plus Pinterest-derived smishing text, with URL inspection. Those values are not comparable to D1: different language, labels, source construction and task. PhishNet (2026) is English-only and explicitly acknowledges spam/smishing confusion. P04 relabels UCI spam as “smish” and cannot be treated as a smishing corpus.

**Research-gap verdict:** the gap is defensible only as an **evaluation and validity gap**: a reproducible, duplicate-group-controlled comparison with a row-order stress test and a separate English three-class analysis. It is not a dataset gap, a first-detector gap, or a proven Malayalam smishing gap.

---

## 7. Residual weaknesses that cannot be eliminated with current data

1. **D1 accession evidence is absent.** No subscription receipt, institutional confirmation, download log, invoice or author letter exists in the workspace.
2. **No source labels.** Row blocks are workbook-order proxies. The cause of the label-block association cannot be established.
3. **Only three blocks and 225 Spam records.** The critical fold trains on 12 Spam messages. No resampling can create source diversity.
4. **No independent Malayalam test corpus.** D2 shares 773 normalised keys with D1 and is English/Latin; it cannot validate D1.
5. **No Manglish evaluation.** Malayalam script presence is not language identification; 503 records also contain Latin characters.
6. **Perfect precision is fragile.** It is based on 29–30 predicted positives concentrated in one block.
7. **MuRIL seed uncertainty is conditional.** Three seeds cannot estimate training-run variance in a population sense.
8. **FSSHAP is not full-text verified.** Its exact datasets, splits and results remain unknown.
9. **Secondary literature is incomplete.** P02, P03, P06, P09, P11, T01, T02 and S01 are not full-text verified.
10. **No production validation.** There is no external deployment, adversarial test, URL verification, or live traffic evaluation.

---

## 8. Final audit conclusion

The defensible paper is a **negative/limiting result about evaluation validity**, not a detector-success paper:

> On a frozen Malayalam-containing SMS corpus, strong character n-gram models and MuRIL all achieve high within-corpus random-split scores, but performance collapses when a complete workbook row block is held out, and MuRIL offers no reliable advantage. The result demonstrates how row-order and script composition can inflate apparent SMS spam performance in a small low-resource corpus.

That claim is supported. “Malayalam smishing detection,” “state of the art,” “first detector,” “unseen-source generalisation,” and “deployment-ready filter” are not.
