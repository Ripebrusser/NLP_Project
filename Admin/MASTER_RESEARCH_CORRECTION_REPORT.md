# Master Research Correction Report

> **AUDIT WORKING DOCUMENT.** This correction report records earlier fixes. Current numbers are controlled by `CANONICAL_FINAL_RESULTS.md`. Authoritative sources: `CANONICAL_FINAL_RESULTS.md`, `FINAL_STATISTICAL_AUDIT.md` and `VERIFICATION_REPORT.md`.


**Date:** 6 November 2026  
**Scope:** complete statistical, methodological and documentation correction of the existing Malayalam-script SMS spam project.  
**Constraints honoured:** no dataset was added or altered; no label was changed; no split was changed; no model was retrained; no model was tuned on test; no old result was deleted; no deployment was performed.

## 1. Bottom line

The arithmetic is now reproducible and the documentation is internally consistent. The research is **defensible as a constrained student paper** only if it is written as a **within-corpus benchmark and validity study**, not as a field-ready Malayalam spam detector, not as smishing/phishing detection, and not as evidence that MuRIL improves performance.

The most important scientific finding is not 0.9650 Macro-F1. It is that the same model falls to **0.5378** under leave-one-row-block-out, and that MuRIL falls to **0.5028** and detects **3.56%** of Spam. That is a useful negative/limiting result. The 0.9650 number alone is a within-batch result.

## 2. Corrections performed

| # | Finding | Evidence | Correction | Severity |
|---:|---|---|---|---|
| 1 | Perfect D1 Spam precision was presented without exact uncertainty | 29/29 or 30/30 positives; 0 FP among 265 Ham | Added exact Clopper–Pearson and Wilson intervals: lower bounds 0.8806/0.8843; FPR upper bound 1.382% | Major |
| 2 | Old FPR statement used 299 as denominator | “3/299 ≈ 1.0%” in CI report | Denominator corrected to 265 Ham; 0/265 → 1.382% exact upper bound | Major |
| 3 | MuRIL three-seed mean had no interval | Mean 0.9619; seed SD 0.0054 | Added conditional test-sample interval [0.9211, 0.9909], explicitly not a new-training-run interval | Major |
| 4 | MuRIL accuracy uncertainty missing from tables | Mean 0.9855 | Added [0.9710, 0.9967] conditional interval and seed-level values | Major |
| 5 | SVM vs MuRIL superiority was not established | Paired Δ Macro-F1 +0.0031 [0.0000, 0.0101] | Text now says “not statistically distinguishable”; no transformer advantage claim | Major |
| 6 | Row-block test was called “block-held-out” / “source-block” | Blocks are consecutive workbook rows; no source IDs | Renamed **leave-one-row-block-out stress test**; documented that blocks are row-order proxies, not verified sources | Critical |
| 7 | Random-split score was reported without its block context | 213/225 Spam in block 6001–7000; χ²=969.15, p≈3.56×10⁻²¹¹, V=0.6975 | Canonical results require the pair 0.9650 (grouped random) and 0.5378 (pooled block) | Critical |
| 8 | Stale block counts 631/991/370 | Off-by-one/positional slicing | Corrected to 630/991/371 using source Excel rows; fold 6001 SVM corrected to 0.368470 | Major |
| 9 | Stale fold 0.3677 | `p2_robustness.py` | Corrected to 0.368470; old value preserved with notice | Minor |
| 10 | 1,486 vs 1,489 Malayalam-only | Documentation typo in `DATASET_AUDIT_REPORT.md`; machine output already 1,489 | Resolved as typo; 1,489 + 503 = 1,992; no filtering change | Major |
| 11 | “Transformers — NOT STARTED” | MuRIL seeds 42/43/44 completed | Corrected status to completed; MuRIL retained as comparator | Minor |
| 12 | D2 denominator ambiguity | 5,971 original vs 5,895 after 37 conflict groups/76 records | Every canonical table states both; all D2 metrics use n=883 test from 5,895 | Major |
| 13 | “Random Macro-F1” / “Block-held-out” terminology | Old reports | Replaced with “Grouped random-split test Macro-F1” and “Pooled leave-one-row-block-out Macro-F1” | Minor |
| 14 | D1/D2 overlap not visible in model reports | 773 shared normalised keys; 1,555 D1 / 831 D2 twins | Documented as non-independence; no pooled training or external-validation claim | Major |
| 15 | Prototype could be read as validation | 299/299 and 883/883 parity | Docs now say “artifact parity / demonstration,” not generalisation or production validation | Minor |
| 16 | Literature status inconsistent | FSSHAP abstract-only; MuRIL/Almeida full text; prior note said only B01 | Corrected status is recorded in `VERIFICATION_REPORT.md` and the action list; no numeric FSSHAP claim | Minor |

Every metric now traces to `Research Work/phase2/metrics/final_verification.json`, generated from frozen predictions by `p2_final_verification.py`. The 14/14 classical metric comparison passed at ≤1.11×10⁻¹⁶.

## 3. What is fully resolved

- D1 and D2 point metrics, per-class metrics, confusion matrices and denominators.
- All five D1 models use the same 299 frozen test IDs; all labels agree.
- All test duplicate groups are singletons; no within-test duplicate dependence.
- Perfect precision is correctly bounded and no longer presented as zero future risk.
- MuRIL seed-level uncertainty, cross-seed SD and conditional three-seed mean interval.
- SVM–MuRIL paired comparison uses shared bootstrap draws; no difference is established.
- Block counts, fold scores and pooled block metrics.
- Malayalam-only count: 1,489, not 1,486.
- D2 5,971 vs 5,895 denominator.
- D1 prediction parity (299/299), D2 parity (883/883), six split hashes.
- Stale artifacts are identified and either corrected or explicitly superseded.

## 4. What remains unresolved

1. **D1 access authorisation/provenance.** IEEE DataPort requires a subscription; no receipt, download log or author permission is in the workspace. Redistribution rights are not established. This is a publication blocker.
2. **No source-diverse external test set.** The three row blocks are not independent sources; the row-block test cannot establish field generalisation.
3. **Cause of row-order association is unknown.** Campaign structure, collection order, language sectioning and labelling workflow are all plausible; the data cannot distinguish them.
4. **“Malayalam” is script presence, not language identification.** 503 records also contain Latin; there is no verified Manglish subset.
5. **Only three MuRIL seeds.** No population interval over training runs.
6. **D2 has no source metadata and 76 ambiguous records were excluded.** D2 is secondary and not independent external validation.
7. **FSSHAP full text is paywalled.** No numeric FSSHAP result is verified.
8. **No full Almeida 2011 four-page text; values are from the expanded 2013 article/dataset record.**
9. **No Git history.** The exact historical nine-file prototype diff cannot be proven.

## 5. Reviewer risk assessment

| Risk | Likelihood of rejection-level criticism | Mitigation now possible |
|---|---|---|
| D1 used without documented permission | High | Obtain receipt/permission before submission; otherwise use D2-only or aggregate-only reporting with explicit constraint |
| Claims of “98.66% accurate Malayalam spam detection” without block caveat | High | Always pair 0.9650 with 0.5378; rewrite abstract/title claims |
| “100% precision” presented as deployment safety | Medium–High | Use exact lower bounds 88.0–88.4% and FPR upper 1.38% |
| Row blocks called “sources” or “generalisation failure” | High | Use “row-order proxy” and “stress test”; remove external-source language |
| No external validation | High for a strong generalisation claim; acceptable for a bounded case study | Narrow the contribution; do not claim field performance |
| MuRIL claimed to improve | Medium | Current evidence shows no improvement; report as negative/comparator |
| D2 denominator/conflict handling unclear | Medium | State 5,971 original → 5,895 experimental → 883 test |
| Literature novelty overclaim | Medium | No “first Malayalam” claim; strongest contribution is evaluation/validity, not detection novelty |
| Small positive count / unstable intervals | Medium | Exact intervals, seed table, no p-value theatre |
| Script-only “Malayalam” definition | Medium | Rename to Malayalam-containing; no Manglish claim |

## 6. Literature position

Supported statements: Dravidian SMS spam research exists; character n-gram baselines are established; MuRIL is a legitimate multilingual encoder; dataset bias/duplicate leakage is a known evaluation problem.

Not supported: that this is the first Malayalam or Dravidian SMS spam study; that it detects phishing/smishing; that it outperforms FSSHAP or any published system; that workbook row blocks are collection sources.

The strongest honest contribution is: **a reproducible, duplicate-controlled within-corpus comparison plus a quantified row-block validity stress test that shows the headline score is not portable across the corpus’s own row ordering.**

## 7. Prototype verdict

The Streamlit demo is a **reproducible artifact demonstration**. It reproduces 299/299 D1 and 883/883 D2 frozen predictions and handles Malayalam/Latin input. It is not a validated product, does not load MuRIL, does not prove generalisation, and must not be deployed publicly while D1 provenance is unresolved. Its documentation should state the supported input, the two-model scope, the non-probability nature of SVM scores, privacy limits (messages are processed locally; no logging promise should be made unless verified), and the source-shift caveat.

## 8. Final verdict

### 8.1 What is now fully resolved?

The calculational and documentary layer: traceability, metric reproduction, denominators, confusion matrices, duplicate/split controls, exact precision uncertainty, MuRIL uncertainty, block counts, script counts, D2 conflict count, terminology and stale-value reconciliation.

### 8.2 What remains unresolved?

D1 permission/provenance; external-source validity; causal explanation of the row-order confound; true language/Manglish identification; FSSHAP full text; the small number of seeds/blocks; D2 independence.

### 8.3 What could still cause an IEEE reviewer to reject the paper?

1. No evidence of permission to use/redistribute D1.
2. A title/abstract that claims generalisable Malayalam spam detection from a single workbook with one Spam-heavy block.
3. Calling row blocks “sources” or claiming “generalisation failure on unseen real-world sources.”
4. Claiming 100% precision or state-of-the-art performance.
5. No independent test set, while claiming field relevance.
6. An unclear D2 denominator or treating D2 as external validation.
7. Overclaiming novelty against FSSHAP/Dravidian work.

### 8.4 Is the current research defensible as a student research paper?

**Yes, conditionally.** It is defensible as a **within-corpus, leakage-controlled benchmark and a negative/limiting result about source/row-order dependence**, with a secondary English three-class experiment. It is not defensible as a deployed Malayalam spam filter, a phishing detector, or a generalisation study. The conditional is important: D1 permission must be resolved before submission, and the abstract must lead with the block caveat, not hide it.

### 8.5 Exact work required before the final IEEE paper

1. **Resolve D1 permission** (subscription receipt, author permission, or institutional written confirmation); if impossible, remove redistributed examples and state the constraint, or pivot the paper to D2 plus a methods/validity contribution.
2. **Lock the claim scope** in one sentence: within-corpus benchmark + row-block stress test; no field performance, no phishing, no Manglish.
3. **Rewrite title/abstract/results** around the paired result (0.9650 grouped random vs 0.5378 pooled block; MuRIL 0.5028).
4. **Decide whether an external source-diverse test set is feasible.** If not, remove all generalisation language; if yes, obtain approval, document provenance/consent, pre-register source-stratified evaluation and use clustered intervals.
5. **Add a statistical appendix**: exact precision/FPR intervals, seed-level MuRIL table, conditional mean interval, paired shared-bootstrap method, block support and absent-class handling.
6. **Finish literature verification**: FSSHAP full text or cite abstract only; Almeida 2011/2013 distinction; no numeric claim not read.
7. **Revise the prototype documentation** to demonstration-only language; keep it non-public until permission is resolved.
8. **Freeze artifacts and hashes** for the submission supplement; no further model selection on the test set.

## 9. Prioritized action list

| Priority | Action | Owner | Completion criterion |
|---:|---|---|---|
| P0 | Resolve D1 access/redistribution permission | Author/institution | Written receipt or permission on file |
| P0 | Approve final claim scope | Supervisor | Signed one-paragraph scope, no field/phishing/Manglish claim |
| P1 | Rewrite abstract/results around block caveat | Author | Every headline paired with block result |
| P1 | Insert canonical tables and exact intervals | Author | No stale 0.3677/631/1,486/“100% safe” text |
| P1 | Statistical appendix and reproducibility supplement | Author | Commands, hashes, prediction files, verifier output included |
| P2 | External validation decision | Supervisor | Either approved protocol or explicit “not claimed” statement |
| P2 | Literature full-text/abstract status table | Author | Every numeric claim marked full-text/abstract/secondary |
| P2 | Prototype documentation audit | Author | Demonstration-only wording; no deployment claim |
| P3 | Optional new source-diverse corpus | Author | Only with ethics/consent/annotation approval; not required for current paper |

## 10. Documents that supersede old values

- `Admin/CANONICAL_FINAL_RESULTS.md` — authoritative numbers.
- `Admin/VERIFICATION_REPORT.md` — reproduction and checks.
- `Admin/RESEARCH_LOOPHOLE_REGISTER.md` — reviewer risks and resolutions.
- `Admin/FINAL_METHODOLOGY_AND_OBJECTIVE.md` — objective, RQs, method, limitations.
- `Admin/CONFIDENCE_INTERVAL_REPORT.corrected.md`
- `Admin/D1_RESULTS.corrected.md`
- `Admin/FINAL_MODEL_SELECTION.corrected.md`
- `Admin/MODEL_COMPARISON.corrected.md`

Old reports are preserved with correction notices; nothing was deleted.
