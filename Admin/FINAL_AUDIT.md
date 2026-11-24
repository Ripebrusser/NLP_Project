# Final Audit — PASS / FAIL / NEEDS DECISION

> **HISTORICAL / SUPERSEDED.** This document records an earlier project state. It is retained for audit provenance and must not be cited for current scope, counts, model status or conclusions. The authoritative documents are `CANONICAL_FINAL_RESULTS.md`, `FINAL_METHODOLOGY_AND_OBJECTIVE.md`, `DATASET_PROVENANCE_AND_PERMISSIONS.md`, `LITERATURE_AUDIT_STATUS.md` and `VERIFICATION_REPORT.md`.


**Date:** 5 November 2026 (blocker-closure revision)  
**Verdict: CLASSICAL BASELINES COMPLETE — NOT READY FOR FORMAL SIGN-OFF (B1, B7, B8 OPEN)**

Only requirements verified by evidence receive PASS. A document existing is not evidence.

---

## 1. Category results

| # | Category | Status | Basis |
|---|---|---|---|
| 1 | Correct project scope | **PASS** | Scope A adopted by the 5 Nov Phase 2 direction: D1 Malayalam spam (primary) + D2 English smishing (secondary) |
| 2 | Dataset availability | **PASS** | Both files present, readable, hashed; no duplicate copies |
| 3 | Dataset provenance and licence | **FAIL** | D2 verified (CC BY 4.0). D1: research use permitted by IEEE DataPort FAQ/Terms (CC BY 3.0 US default), but **the team's authorised access is undocumented** and the file is subscription-gated |
| 4 | Dataset integrity | **PASS** | Counts, encoding defects, whitespace and duplicates quantified; originals unmodified |
| 5 | Label validity | **PASS** | Raw/normalised labels separated; 1 invalid D1 label excluded, not relabelled; D2 case variants mapped in analysis only |
| 6 | Duplicate and conflict resolution | **PASS** | 1,154/22 exact and 1,245/179 near-duplicate groups quantified; 28/37 conflicts reported; grouping enforced in plan |
| 7 | Language identification | **FAIL** | Only Unicode script detection possible; no verified Malayalam/Manglish language-ID tool; no language labels produced |
| 8 | Manglish feasibility | **PASS** | Determined **not feasible** (34 heuristic records, 0.44%) and removed from scope |
| 9 | Label harmonisation | **PASS** | No merging of spam/smishing; no dataset pooling; mapping fixed |
| 10 | Literature verification | **FAIL** | P06 resolved and P10 excluded, FSSHAP verified to abstract level; **14 retained records remain bibliographic-only** because publishers block full text |
| 11 | Literature coverage | **NEEDS DECISION** | 10 of 11 required areas covered; language identification has no verified source |
| 12 | Research-gap evidence | **PASS** | Searches logged; Elangovan/Abirami series, P05, P06, P08 and low-resource smishing work cited |
| 13 | Novelty defensibility | **PASS** | Corrected: no dataset/first claims; only "no verified Malayalam/Manglish smishing study" and "no verified transformer evaluation of D1" |
| 14 | Leakage prevention | **PASS** | Splits executed and hashed; group/normalised overlap zero; block-order confound quantified (macro-F1 0.696/0.368 held-out) |
| 15 | Experimental design | **PASS** | Tasks, models, metrics, thresholds, CI and error analysis specified |
| 16 | Model-training readiness | **FAIL** | Baselines complete; G2/G3 (D1 access authorisation/provenance) still open |
| 17 | Documentation consistency | **PASS** | All affected documents updated in this closure; root duplicates removed |
| 18 | Evidence traceability | **PASS** | `EVIDENCE_REGISTER.md` maps claims to files, sections and computation methods |

**Tally: 13 PASS · 4 FAIL · 1 NEEDS DECISION.**

---

## 2. Blockers and exact actions

| Blocker | Why it blocks | Exact action required | Owner |
|---|---|---|---|
| **B1 — D1 access provenance** | Research use is permitted by IEEE DataPort's FAQ and Terms, but the dataset is a subscription-gated Standard Dataset; credentials are non-transferable and public sharing is prohibited. No subscription receipt, download log or author permission exists in the project. | Produce **one** of: (a) IEEE DataPort subscription confirmation covering the download, (b) written author permission, (c) institutional library confirmation. Store it in `Admin/`. If none, **drop D1** and adopt Scope B. | Team / guide |
| **B2 — Scope approval** | The revised title and two-task scope are not yet approved. | Guide sign-off on **Scope A** (D1+D2) or **Scope B** (D2 only). | Team |
| **B7 — Literature full texts** | 14 retained records are bibliographic-only; results are reported as authors' claims, not independently read. | Obtain institutional access to the paywalled papers, or formally accept bibliographic-only status and label every such result as "reported, not verified". | Team |
| **B8 — Language identification** | No verified Malayalam/Manglish LID source; the review cannot claim language-level labels. | Add one verified LID paper, or explicitly accept script-only analysis as a limitation. | Guide |
| **B4 — Split execution** | The split is simulated, not written. No training may start from an unwritten split. | After B1 and B2: run the split script, write `splits/*.csv` + `manifest.json` with hashes, re-run leakage assertions. | Team |

**Closed since the previous audit:** B3 compute — NVIDIA RTX 4050 Laptop, 6,141 MiB confirmed. Fine-tuning must fit 6 GB (batch 8, max_len 128, gradient accumulation).

---

## 3. What is genuinely complete

1. **Both datasets audited from actual bytes**: 7,717 and 5,971 records, labels, scripts, duplicates, conflicts, encoding defects.
2. **All earlier figures corrected** (7,980 / 7,718 / 7,715 / Malayalam 1,996 / Tamil 1,241).
3. **D2 provenance verified** (CC BY 4.0, exact counts); **D1 licence question resolved** in principle, access authorisation still open.
4. **Language finding**: D1 is a five-language Dravidian corpus; D2 has zero Indic script.
5. **Manglish finding**: not isolatable (34/7,717 heuristic hits).
6. **Cross-dataset finding**: 773 shared messages, 189 D1-spam ↔ D2-smishing — combination rejected.
7. **Literature finding**: P06 is real but excludes Malayalam; P10 is excluded; D1 already has an active publication line (FSSHAP and related work).
8. **Leakage-safe split designed and simulated**, assertions passing, deliberately **not executed**.
9. **No model trained, no data modified, no synthetic data created.**

---

## 4. What remains before training

| Step | Depends on |
|---|---|
| Document D1 access or drop D1 | B1 |
| Approve Scope A or B | B2 |
| Resolve literature full-text status | B7 |
| Accept or close LID limitation | B8 |
| Write and hash splits | B1, B2 |
| Produce preprocessing log | Split files |
| Fit majority + TF-IDF baselines | Preprocessing |
| Fine-tune transformer | GPU confirmed (done) |
| Seal test set, single final evaluation | All above |

---

## 5. Verdict

> **CLASSICAL BASELINES COMPLETE — NOT READY FOR FORMAL SIGN-OFF**

Phase 2 was executed at project direction: Scope A adopted, D1/D2 splits generated and hashed, and four classical models trained. The test sets were evaluated once after validation-only selection.

B2 (scope) and B4 (split execution) are closed. **B1 (D1 access provenance), B7 (literature full texts) and B8 (language identification) remain open.** B1 blocks submission and any claim that reuse permission is formally documented; B7/B8 block a complete literature claim. The D1 random-split score must always be reported with the block-held-out result (macro-F1 0.696/0.368).
