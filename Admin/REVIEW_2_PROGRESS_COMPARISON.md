# Review 2 Progress Comparison — Phase 2

> **AUDIT WORKING DOCUMENT.** This comparison records an earlier review stage, not the final statistical record. Authoritative sources: `CANONICAL_FINAL_RESULTS.md`, `FINAL_STATISTICAL_AUDIT.md` and `VERIFICATION_REPORT.md`.


> **CORRECTION NOTICE (6 Nov 2026):** Historical comparison preserved. The transformer row is **COMPLETED**, not “NOT STARTED”; MuRIL seeds 42/43/44 were run. Read block results as a **leave-one-row-block-out stress test** on row-order proxies. See `Admin/CANONICAL_FINAL_RESULTS.md`.

**Project:** SMS Spam and Smishing Detection in Malayalam-Script and English Text  
**Date:** 5 November 2026  
**Basis:** verified audit + actual Phase 2 runs. No figure below is projected.

| Component | Planned work | Completed | Evidence | Status | Remaining work |
|---|---|---|---|---|---|
| **Workspace audit** | Locate/verify files | Both datasets hashed; unrelated ZIP excluded | `DATASET_AUDIT_REPORT.md` §4 | **COMPLETED** | — |
| **Dataset audit (D1)** | Records, labels, scripts, duplicates | 7,717; 6,322/1,394/1; 1,154 exact + 1,245 near groups; 28 conflicts; 5-language census | Audit scripts/JSON | **COMPLETED** | Access authorisation proof |
| **Dataset audit (D2)** | Same | 5,971; 4,844/489/638; 22 exact + 179 near; 37 conflicts; English-only | Audit scripts + Mendeley | **COMPLETED** | — |
| **Scope decision** | Decide what data supports | Two-task Scope A adopted: D1 Malayalam spam, D2 3-class smishing | Phase 2 direction; scope doc | **COMPLETED — ADOPTED** | Guide sign-off for record |
| **Literature identification** | ~15 relevant papers | 20 records (15 core + base + 4) | `LITERATURE_COMPARISON_MATRIX.csv` | **COMPLETED** | — |
| **Literature verification** | Verify metadata/claims | P06 resolved (no Malayalam), P10 excluded, FSSHAP abstract-only, 14 bibliographic-only | `LITERATURE_REVIEW_VERIFICATION.md` | **PARTIALLY COMPLETED** | Full-text access or formal acceptance |
| **Literature synthesis/gap** | Connected review + defensible gap | Spam/smishing/offensive separated; Elangovan series cited; no first-claims | Gap analysis | **COMPLETED** | — |
| **Malayalam subset** | Extract and audit | 1,992 (1,767/225); 503 Latin; 1,489 mono; 0 other Indic; 1,824 groups; 0 conflicts | `phase2/data/d1_malayalam.csv` | **COMPLETED** | — |
| **Preprocessing** | Normalise, preserve traceability | NFKC/zero-width cleanup; no stemming/stopwords; source rows retained | `phase2/p2_extract.py` | **COMPLETED** | — |
| **Duplicates/conflicts** | Group exact/near/template | D1 1,824 groups; D2 **5,663 experimental groups** (5,700 before excluding 37 conflict groups) | `phase2/metrics/duplicates.json` | **COMPLETED** | — |
| **Splits + hashes** | 70/15/15 grouped, seed 42 | D1 1,394/299/299; D2 4,127/885/883; zero overlap; SHA-256 manifest | `phase2/splits/split_manifest.json` | **COMPLETED** | — |
| **Classical models** | LR + Linear SVM, word/char | 4 saved pipelines; validation-selected | `phase2/models/` | **COMPLETED** | — |
| **D1 evaluation** | Macro-F1, per-class, errors | SVM char 2–4: acc .9866, macro-F1 .9650, Spam R .882, 4 FN | `d1_malayalam_results.json` | **COMPLETED** | — |
| **D2 evaluation** | 3-class metrics | LR char 2–4: acc .9638, macro-F1 .8877, Smishing R .822 | `d2_results.json` | **COMPLETED** | — |
| **Block robustness** | Test row-order optimism | Macro-F1 .696/.497/.368 held-out blocks vs .965 random | `d1_block_robustness.json` | **COMPLETED** | Block-aware/external confirmation |
| **Transformers** | MuRIL/XLM-R | MuRIL seeds 42/43/44 completed | `metrics/muril_results.json` | **COMPLETED** | Retained as comparator |
| **Documentation** | Progress/evidence updated | Phase 2 sections + evidence §7 | `Admin/` | **COMPLETED** | — |

---

## Status summary

| Status | Count | Components |
|---|---|---|
| **COMPLETED** | 14 | Workspace, D1/D2 audits, scope, literature identification/synthesis/gap, subset, preprocessing, duplicates, splits, classical models, D1/D2 evaluation, block robustness, documentation |
| **PARTIALLY COMPLETED** | 1 | Literature verification (14 bibliographic-only) |
| **COMPLETED (MuRIL)** | 1 | Transformers |

**Readiness gates:** 6 of 8 pass (G1 scope, G4 split, G5 preprocessing, G6 compute, G7 baselines, G8 sealed test). **G2/G3 — D1 access authorisation and provenance — remain open.** Training proceeded at project direction with that caveat; formal sign-off does not.

---

## Key numbers

| Metric | D1 | D2 |
|---|---|---|
| Records | 7,717 (1,992 Malayalam) | 5,971 |
| Classes | Ham 1,767 / Spam 225 (Malayalam) | ham 4,844 / spam 489 / smishing 638 |
| Scripts | Malayalam + Latin; no other Indic in subset | Latin 5,969; **0 Indic** |
| Exact/near duplicates | 1,154 / 1,245 (full corpus) | 22 / 179 |
| Conflicts | 28 groups (0 in Malayalam subset) | 37 groups / 76 records |
| Licence | Research use permitted; **access unverified** | CC BY 4.0 |
| Phishing labels | **None** | Smishing only |

---

## Honest assessment

**Strengths:** the data foundation is verified; duplicate and conflict handling is explicit; splits are hashed and overlap-free; classical baselines are reproducible; the source-block confound is quantified rather than hidden.

**Weaknesses:** the D1 random-split score is optimistic; cross-block generalization is poor; 34 Spam test rows give wide confidence intervals; 14 literature records remain bibliographic-only; D1 access authorisation is still undocumented; no transformer has been run.

**What to tell the reviewer:** the project now has working classical baselines and an honest leakage story. The D1 headline must always be reported with the block-held-out result. The transformer comparison is the next experiment, not a replacement for fixing the evaluation design.
