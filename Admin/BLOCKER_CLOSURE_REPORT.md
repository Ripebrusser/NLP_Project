# Blocker Closure Report

> **HISTORICAL / SUPERSEDED.** This document records an earlier project state. It is retained for audit provenance and must not be cited for current scope, counts, model status or conclusions. The authoritative documents are `CANONICAL_FINAL_RESULTS.md`, `FINAL_METHODOLOGY_AND_OBJECTIVE.md`, `DATASET_PROVENANCE_AND_PERMISSIONS.md`, `LITERATURE_AUDIT_STATUS.md` and `VERIFICATION_REPORT.md`.


**Date:** 5 November 2026  
**Scope:** closure of the Dataset 1 licence blocker, re-verification of the literature record, scope revision, and readiness re-assessment.  
**Constraints honoured:** no model training, no dataset download, no synthetic data, no modification of original datasets, **no split execution**.

---

## 1. Dataset 1 — licence and reuse determination

### 1.1 What was checked

| Source | What it says |
|---|---|
| Dataset record — https://ieee-dataport.org/documents/spam-sms-dravidian-languages | "Standard Dataset". Files: `Spam Message Collection.xlsx` (1.26 MB). "**LOGIN TO ACCESS DATASET FILES**" and "**Subscription Required**". No licence field is displayed on the public record. |
| IEEE DataPort FAQ — "Can I use datasets available on IEEE DataPort in my research?" | "**Yes.** IEEE DataPort is intended to facilitate research and expedite the process of proving reproducibility of research. Data used in research **must be cited** in accordance with the citation guidelines on the site." |
| IEEE DataPort FAQ — Standard vs Open Access | "Standard Datasets … will be available only to those IEEE DataPort users who have a subscription." Open Access datasets are free to all. |
| IEEE DataPort Terms of Use §2(a) | IEEE grants Authorized Users a "non-exclusive, **personal, non-transferable** license" to use IEEE DataPort. |
| IEEE DataPort Terms of Use §2(g) | Uploaded Content "will be made available to any users of IEEE DataPort … for viewing, downloading, and/or **reuse** including … proving reproducibility and performing data analysis." "Except as otherwise specifically permitted by IEEE in its sole discretion, Authorized Users agree that Content will be made available subject to the terms of the **Creative Commons Attribution (CC-BY) License** [CC BY 3.0 US]." |
| IEEE DataPort Terms of Use §5(a)(vii) | Misuse includes "Use of IEEE DataPort to facilitate **unauthorized public sharing of Content**." |
| IEEE DataPort Terms of Use §3 | Users must "review the licensing terms of any Content … prior to use" and are "solely responsible for compliance with any licensing obligations." |

### 1.2 What is established

1. **Research use is permitted in principle.** IEEE DataPort's own FAQ answers "Yes" and requires citation.
2. **The default content licence is CC BY 3.0 US**, which permits reuse with attribution — subject to any dataset-specific terms.
3. **Access is gated.** D1 is a Standard Dataset; only subscribers may download it.
4. **Credentials are personal and non-transferable**, and public sharing of the file is explicitly listed as misuse.
5. **The dataset page itself does not display a licence**, so the CC BY default is inferred from the platform Terms, not stated on the record.

### 1.3 What remains uncertain

| Question | Status |
|---|---|
| Did the team obtain the file through a valid IEEE DataPort subscription? | **No evidence in the project.** No subscription receipt, institutional login record, or download log exists. |
| Did the authors grant the file directly? | **No evidence.** No permission e-mail or licence statement. |
| Is the local file byte-identical to the published file? | File name and size (1.26 MB) match; content matches the described languages and ~7,700 count. Byte-identity cannot be checked without the official download. |
| May the file be redistributed (e.g. committed to a public repository)? | **No.** Subscription access plus the prohibition on unauthorised public sharing means redistribution is not permitted without explicit permission. |
| May derived statistics/results be published? | Yes, with citation of the dataset DOI. Publishing the raw messages is not permitted. |

### 1.4 Verdict

> **Dataset 1: BLOCKED — access provenance unverified.**

This is **not** a finding that research use is forbidden. It is a finding that the project cannot demonstrate it obtained the file under the platform's terms. The licence question is resolved; the **authorisation evidence** question is not.

### 1.5 Exact evidence needed to close

One of the following, stored in `Admin/`:

1. **Institutional subscription proof** — IEEE DataPort subscription confirmation (individual or institutional) covering the download date, with the account holder named; or
2. **Written author permission** — an e-mail from Ramanujam Elangovan or Abirami A. M. permitting research use of `Spam Message Collection.xlsx`; or
3. **Institutional library confirmation** that the dataset was accessed under a covered subscription.

If none can be produced, **D1 must be dropped**.

### 1.6 Consequences

| If D1 is cleared | If D1 is dropped |
|---|---|
| Two-task scope proceeds: Malayalam-script spam (D1) + English three-class smishing (D2). | Project becomes **English-only** (D2). The Malayalam contribution disappears, and the title must drop "Malayalam-Script". |
| Malayalam arm has 1,992 records (225 spam); no phishing claim. | No Malayalam/Manglish claim of any kind; only English ham/spam/smishing. |
| Derived statistics may be published with citation; raw messages must not be redistributed. | No D1-derived tables or examples. |
| Splits may be generated after scope approval. | Splits only for D2. |

---

## 2. Literature re-verification

### 2.1 The 20 records — final disposition

| ID | Disposition | Evidence |
|---|---|---|
| P01 Almeida 2011 | Retained, bibliographic-level | Workbook record; UCI dataset DOI confirmed via citing paper |
| P02 Mishra & Soni 2020 | Retained, bibliographic-level | FGCS DOI; dataset record cross-reference |
| P03 Xu 2025 | Retained, partial | DOI recorded; publisher inaccessible |
| P04 Hassan 2026 | Retained, partial | Workbook; label relabelling noted |
| P05 PhishNet 2026 | Retained, partial | Workbook + repository |
| **P06 Sanjay 2026** | **RESOLVED — verified, but no Malayalam** | See §2.2 |
| P07 Filali 2026 | Retained, partial | Workbook |
| P08 Amaral Cejas 2026 | Retained, partial | ACL Anthology record; abstract only |
| P09 Phap 2026 | Retained, partial | Publisher 403 |
| **P10 unnamed pipeline** | **EXCLUDED** | No authors, no resolvable record; see §2.3 |
| P11 Birthriya 2026 | Retained, partial | Workbook |
| P12 DravidianCodeMix 2022 | Retained, partial | Workbook + Springer record |
| P13 MuRIL 2021 | Retained, partial | arXiv |
| P14 XLM-R 2020 | Retained, partial | ACL Anthology |
| P15 BERT 2019 | Retained, background | ACL Anthology |
| B01 Mahmood & Hameed 2023 | **Full text read** | Official PDF |
| **E01 FSSHAP 2025** | **Abstract + metadata verified; full text paywalled** | See §2.4 |
| T01 Timko & Rahman 2024 | Metadata only | ACM record |
| T02 Thara & Poornachandran 2022 | Metadata + abstract | Springer |
| S01 SMSDHL 2025 | Metadata + abstract | TechRxiv |

**Result:** 19 retained, 1 excluded. 14 retained records remain bibliographic-only because the publishers (Elsevier, Taylor & Francis, IEEE, Springer) block full-text access. The literature review is therefore **not complete**; it is honest about its levels.

### 2.2 P06 — resolved

The paper exists and is verifiable:

- **Title:** An LLM-Based Multilingual Phishing Detection Framework for Regional Languages
- **Authors:** S. Sanjay, Nishant Krishna, G. Paramesh, K. V. Kiran Kumar
- **Venue:** 2026 International Conference on AI-Driven Innovations & Applications (IC-AIDA), Bangalore, 10–11 April 2026, paper p. 168
- **IEEE Xplore:** document 11564455
- **Method:** XLM-RoBERTa + feedback-driven continual learning
- **Languages:** English, Hindi, Kannada, Tamil, Telugu, Bengali — **Malayalam is not included**
- **Reported results:** F1 0.975, ROC-AUC 0.997 (from an academic portal record, not the publisher page)

**Consequence:** P06 is usable as evidence that multilingual phishing detection exists for *some* Indian languages. It is **not** evidence of Malayalam coverage, and it does not close the project's gap. The earlier workbook note ("Malayalam not listed") is confirmed.

### 2.3 P10 — excluded

No author list, volume or page range could be confirmed. Searches for the exact title return only a ResearchGate citation stub and unrelated pipeline papers. A reference without authors cannot be cited. **Removed from the active literature set.**

### 2.4 FSSHAP (E01) — verified as far as the paywall allows

| Field | Verified value |
|---|---|
| Title | *FS_SHAP: Global Interpretable Feature Selection Using XAI for the Classification of Spam SMS in Dravidian Languages* |
| Authors | Ramanujam Elangovan; Abirami A. M.; K. G. Thirumalai |
| Venue | IEEE MultiMedia, vol. 32, no. 1, pp. 92–103 |
| Published | Online 3 December 2024; issue Jan.–Mar. 2025 |
| DOI | 10.1109/MMUL.2024.3508765 |
| Method | SHAP-based global feature selection over handcrafted features; **Random Forest** classifier |
| Data | "Three datasets, including the short message services in Dravidian languages like Tamil, Kannada, Telugu, and Malayalam" |
| Results | Abstract states traditional feature-selection techniques were compared "in various performance metrics"; **no numeric results appear in the abstract**. An author LinkedIn post claims "over 90% accuracy" — not peer-reviewed, not citable as a result. |
| Relationship to D1 | The paper's reference list includes the D1 IEEE DataPort DOI (`10.21227/dcym-pd69`). The abstract does not name the datasets, so **D1 use is highly probable but not confirmed** without the full text. |
| Full text | Paywalled (IEEE Computer Society / ACM DL). |

**Related Dravidian SMS spam work by the same group** (found during this audit):

| Work | Venue / DOI | Relevance |
|---|---|---|
| XAI-based Feature Selection for SMS Spam Classification in Dravidian Languages | ICITIIT 2024, DOI 10.1109/ICITIIT61487.2024.10580065 | Another prior use of Dravidian SMS spam data |
| Evaluation of Hand-Crafted Features for the Classification of Spam SMS in Dravidian Languages | Springer LNNS, 2023, pp. 3–15, DOI 10.1007/978-981-99-6755-1_1 | Earlier feature study |
| NCMDFE: performance evaluation of non-contextual meta-data feature extraction | Int. J. Information Technology, 2025, DOI 10.1007/s41870-025-02635-5 | Metadata features for Indian-language SMS |
| Efficient extraction and evaluation of hand-crafted meta-data features for Dravidian spam SMS classification | Evolving Systems, 2026, DOI 10.1007/s12530-025-09761-2 | Latest in the series |

**Consequence:** D1 is **not an unused corpus**. It has an active publication line. Any novelty claim must be about the *evaluation* (transformer vs classical, grouped splits), not about the dataset or the task.

### 2.5 Competing-work search

| Search focus | Result |
|---|---|
| Malayalam smishing / phishing SMS | **No peer-reviewed study found** |
| Manglish spam/phishing | **None**; Manglish work remains offensive-language/sentiment |
| Dravidian SMS spam | Active: Elangovan/Abirami series (above); MDPI *Electronics* 2026 mentions metadata-enriched Dravidian SMS features |
| Multilingual SMS fraud/smishing | P08 (proprietary, languages unnamed); NLPAICS 2026 multilingual fraud paper (English/Spanish/Valencian) |
| Indian-language scam SMS | Non-peer-reviewed HuggingFace 14-language dataset; outside approved scope and unverified |

**Corrected novelty statement:** there is **no verified Malayalam or Manglish smishing study**, and **no peer-reviewed transformer-based evaluation of D1 that this audit could verify**. There *is* a substantial Dravidian SMS spam literature using classical/handcrafted methods. Claims of "first Dravidian SMS spam work" or "first use of this dataset" are **false and must not appear**.

---

## 3. Revised research scope

The two-task scope in `RESEARCH_SCOPE_AND_LABEL_DECISION.md` is retained, with one condition:

| Element | Status |
|---|---|
| Datasets kept separate | Unchanged — no pooling |
| Manglish | Out of experimental scope (34 heuristic records, 0.44%) |
| Spam vs smishing | Kept distinct; never merged |
| D1 called a phishing dataset | Prohibited — it is spam/ham only |
| D2 Indic-script records | **Zero** — stated as a hard limitation; D2 supports English only |
| **D1 availability** | **Conditional on access proof**; if dropped, the Malayalam arm is removed and the title loses "Malayalam-Script" |

**Two scope variants, both pre-approved in structure:**

- **Scope A (preferred):** D1 Malayalam-script spam + D2 English three-class smishing.
- **Scope B (fallback):** D2 English three-class smishing only.

No third scope is permitted (no pooling, no Manglish, no synthetic data).

---

## 4. Split execution — held

Per instruction, no split was executed or saved.

- The leakage-control plan is unchanged: grouped by normalised text, stratified by class × script, 70/15/15, seed 42, test sealed and hashed.
- Simulated sizes remain as recorded (Malayalam 1,394/299/299; D2 4,180/897/894).
- Execution requires: **D1 access proof + scope approval**. Until then, no `splits/` directory exists and no hash is recorded.

---

## 5. Readiness re-assessment

| # | Category | Status | Change |
|---|---|---|---|
| 1 | Correct project scope | **NEEDS DECISION** | Scope variants defined; approval outstanding |
| 2 | Dataset availability | **PASS** | — |
| 3 | Provenance and licence | **FAIL** | Licence resolved in principle; **access authorisation unverified** |
| 4 | Dataset integrity | **PASS** | — |
| 5 | Label validity | **PASS** | — |
| 6 | Duplicate/conflict resolution | **PASS** | — |
| 7 | Language identification | **FAIL** | No verified Malayalam/Manglish LID tool |
| 8 | Manglish feasibility | **PASS** | Determined not feasible |
| 9 | Label harmonisation | **PASS** | — |
| 10 | Literature verification | **FAIL** | P06 resolved, P10 excluded, FSSHAP verified; **14 records remain bibliographic-only** |
| 11 | Literature coverage | **NEEDS DECISION** | LID area still lacks a verified source |
| 12 | Research-gap evidence | **PASS** | Competing work documented |
| 13 | Novelty defensibility | **PASS** | Corrected; no first-claims |
| 14 | Leakage prevention | **PASS** | Plan unchanged, not executed |
| 15 | Experimental design | **PASS** | — |
| 16 | Model-training readiness | **FAIL** | Gates G1, G2, G4, G5 open |
| 17 | Documentation consistency | **PASS** | Updated in this closure |
| 18 | Evidence traceability | **PASS** | Register extended |

**Tally: 12 PASS · 4 FAIL · 2 NEEDS DECISION.**

### Remaining blockers

| Blocker | Evidence needed |
|---|---|
| **B1 — D1 access provenance** | Subscription receipt or written author permission (or drop D1) |
| **B2 — Scope approval** | **CLOSED** — Scope A adopted in the Phase 2 direction; guide sign-off still advisable for the record |
| **B7 — Literature full texts** | Institutional access to Elsevier/T&F/IEEE/Springer, or accept bibliographic-only status explicitly |
| **B8 — Language identification** | One verified Malayalam/Manglish LID source, or explicit acceptance of script-only analysis |
| **B4 — Split execution** | **CLOSED** — splits executed and hashed in `Research Work/phase2/splits/` |

### Verdict

> **BASELINES COMPLETE — B1, B7 AND B8 REMAIN OPEN**

The licence *question* is closed; the *authorisation evidence* is not. Scope A was adopted and splits were executed under the 5 November Phase 2 direction, and classical baselines were trained. D1 access provenance (B1), literature full texts (B7) and language identification (B8) remain open. B1 blocks submission/publication and any claim of formally documented reuse permission; it does not block local experimentation under the project direction.
