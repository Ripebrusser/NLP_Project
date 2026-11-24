# Evidence Register

> **CORRECTION NOTICE (6 Nov 2026):** E74’s 0.3677 is superseded by **0.368470**; block counts are **630/991/371**. See `Admin/CANONICAL_FINAL_RESULTS.md` and `Admin/VERIFICATION_REPORT.md`. The D1 access conclusion is **unresolved**, not a resolved licence; see `Admin/DATASET_PROVENANCE_AND_PERMISSIONS.md`.

Every material claim in the Review 2 materials, with its source and verification level.  
**Levels:** A = directly computed/read this audit; B = official record read; C = workbook/secondary record; D = unverified.

---

## 1. Dataset statistics

| # | Claim | Evidence source | Location | Level | Limitation |
|---|---|---|---|---|---|
| E01 | D1 contains **7,717** data records | `Datasets/Spam Message Collection.xlsx` | Computed: 101,173 `<row>` elements − 93,456 blank − 1 header | A | Sheet has heavy blank-row formatting |
| E02 | D1 labels: Ham 6,322 / Spam 1,394 / `Spa,` 1 | same | Computed over `Type` column | A | — |
| E03 | D1 has 2 empty messages, 0 empty labels, 1 invalid label | same | Rows 5121, 5212 empty; row 3749 `Spa,` | A | — |
| E04 | D1 usable after exclusions: **7,714** (6,320 Ham / 1,394 Spam) | same | Computation | A | 3 records excluded, documented |
| E05 | D1 exact duplicates: 1,154 groups / 1,224 excess | same | Computation | A | — |
| E06 | D1 near-duplicates: 1,245 groups / 1,375 excess | same | Normalisation defined in audit report §1A | A | Definition-dependent |
| E07 | D1 conflicting labels: 28 groups / 58 records | same | Computation | A | — |
| E08 | D1 script mix: Malayalam 1,992; Tamil 1,175; Telugu 1,068; Kannada 1,345; Latin-only 2,130 | same | Unicode block census | A | Script ≠ language |
| E09 | D1 spam rate by script: 2.4%–65.4% | same | Cross-tab | A | Confound evidence |
| E10 | Manglish heuristic screen: 34 records (0.44%) | same | 100-word Romanised-Malayalam lexicon | A | Lower bound, not annotation |
| E11 | D1 row blocks: rows 5,000–5,999 are 100% Ham | same | Row-order analysis | A | Source-block evidence |
| E12 | D2 contains **5,971** records | `Datasets/Dataset_5971.csv` | `csv` parse | A | — |
| E13 | D2 raw labels: ham 4,844 / Smishing 616 / spam 466 / Spam 23 / smishing 22 | same | Computation | A | Case inconsistency |
| E14 | D2 normalised: 4,844 / 489 / 638 | same | Lowercase + strip | A | Analysis-only |
| E15 | D2 has 0 missing text/labels | same | Computation | A | — |
| E16 | D2 exact duplicates 22 groups; near-duplicates 179 groups / 270 excess; conflicts 37 groups / 76 records | same | Computation | A | — |
| E17 | D2 is English-only: 5,969 Latin, 1 Han+Latin, 2 no-letter, **0 Indic** | same | Unicode census | A | — |
| E18 | D2 metadata are binary flags: URL 207 yes, EMAIL 19 yes, PHONE 844 yes | same | Column value counts | A | Shortcut risk |
| E19 | D2 encoding damage: 185 U+FFFD | same | Character scan | A | Source defect |
| E20 | Cross-dataset overlap: 773 keys; 1,555 D1 / 831 D2 records | Both datasets | Normalised-key intersection | A | Proves non-independence |
| E21 | Overlap label pairs: D1 Spam↔D2 smishing 189; ↔spam 87; ↔ham 51 | Both | Cross-tab | A | Label semantics differ |
| E22 | No duplicate dataset files on disk | Workspace | SHA-256 comparison | A | — |

## 2. Dataset provenance and licence

| # | Claim | Source | Location | Level | Limitation |
|---|---|---|---|---|---|
| E23 | D1 is "Spam SMS in Dravidian Languages", Elangovan & Abirami, IEEE DataPort, 2 Jun 2023, DOI 10.21227/dcym-pd69 | IEEE DataPort page | Title/citation block | B | — |
| E24 | D1 languages: English, Tamil, Telugu, Kannada, Malayalam; "nearly 7700 messages"; two columns | IEEE DataPort abstract/instructions | Abstract | B | — |
| E25 | D1 spam definition: "business, annoying, and unnecessary messages"; **no phishing labels** | IEEE DataPort abstract | Abstract | B | — |
| E26 | D1 file access requires an IEEE DataPort subscription; licence not displayed | IEEE DataPort page | "Subscription Required" | B | **Licence unresolved** |
| E27 | Local D1 file matches listed name and size (1.26 MB) and described language mix | Local file vs page | Hashing + census | A/B | Download path undocumented |
| E28 | D2 is "SMS Phishing Dataset...", Mishra & Soni, Mendeley V1, 20 Jun 2022, DOI 10.17632/f45bkkt8pr.1, **CC BY 4.0** | Mendeley page | Description/licence | B | — |
| E29 | D2 composition 5,971 = 4,844 ham + 489 spam + 638 smishing | Mendeley page + local file | Description + computation | A/B | Exact match |
| E30 | D2 links to UCI SMS Spam Collection as related dataset | Mendeley page | Related datasets | B | Explains UCI derivation |
| E31 | D2 companion paper SoCPaR 2022, DOI 10.1007/978-3-031-27524-1_57 | Springer record | Chapter page | B | — |

## 3. Literature

| # | Claim | Source | Location | Level | Limitation |
|---|---|---|---|---|---|
| E32 | B01 reports 98.5/96.9/93.1/95.05 (SVM) | Iraqi J. Science PDF + journal page | Abstract, results tables | A | English, unreleased data |
| E33 | B01 uses UCI 5,772 + 120 Pinterest images → 867 smishing / 4,825 ham | B01 full text | Dataset section | A | Image-derived labels |
| E34 | B01 page numbers: 6276–6291 (publisher) vs 5376–5391 (PDF header) | Journal page + PDF | Citation/header | A | Discrepancy documented |
| E35 | P01 SVM accuracy 97.64%, MCC 0.893 | Workbook record | Sheet1 P01 | C | Full text not re-read |
| E36 | P04 relabels UCI spam as "smish" | Workbook record | Sheet1 P04 | C | Label conflation |
| E37 | P05 reports spam/smishing confusion; Dataset2 spam synthetic | Workbook record | Sheet1 P05 | C | Full text not re-read |
| E38 | P12 has sentiment/offensive labels only | Workbook + Springer record | Sheet1 P12 | C | Not a threat corpus |
| E39 | MuRIL transliterated test sets are derived | Workbook record | Sheet1 P13 | C | Not natural Manglish |
| E40 | E01 uses the D1 corpus | IEEE MultiMedia metadata | Abstract/references | B | Full text paywalled |
| E41 | No Malayalam/Manglish smishing study found | Searches 5 Nov 2026 | Queries logged in gap analysis §1 | C | Absence of evidence, not proof |
| E42 | Low-resource smishing exists for Bemba, Bangla, Filipino | Search results | Cited in gap analysis §3 | C | Metadata-level |
| E43 | P06 and P10 unresolved *(superseded — see §6)* | Workbook + failed access | Sheet1 P06/P10 | D | Historical only |

## 4. Scope and method decisions

| # | Decision | Evidence | Level |
|---|---|---|---|
| E44 | Original title is unsupported | No Malayalam phishing labels; 5-language corpus; 34 Manglish hits | A |
| E45 | Manglish removed from scope | 34 heuristic records; no annotation | A |
| E46 | Datasets cannot be combined | 773 shared keys; 189/87/51 label conflicts | A |
| E47 | `Spa,` record excluded, not relabelled | Malformed label; content Telugu promo | A |
| E48 | D2 spam and smishing kept separate | Official three-class definition; 37 conflicts | A/B |
| E49 | Grouped 70/15/15 split, seed 42 | Simulation with assertion | A |
| E50 | Malayalam-only-script subset descriptive only | 9 spam in test (<30 threshold) | A |
| E51 | Text-only primary; metadata as ablation | Flags are text-derivable | A |
| E52 | Macro-F1 primary metric | Class imbalance (D1 18.1%, D2 8.1%/10.7%) | A |

---

## 5. Reproduction commands

```bash
py "Research Work/audit_datasets.py"        # counts, labels, duplicates, scripts
py "Research Work/audit_forensics.py"       # conflicts, blocks, cross-dataset
py "Research Work/audit_scripts.py"         # corrected script census
py "Research Work/split_plan_simulation.py" # split feasibility + leakage asserts
py "Research Work/build_lit_matrix.py"      # literature CSV
```

All outputs are written under `Research Work/audit_output/`. The scripts read the original datasets read-only.

---

## 6. Blocker-closure evidence (5 November 2026)

| # | Claim | Source | Location | Level | Limitation |
|---|---|---|---|---|---|
| E53 | IEEE DataPort permits research use of its datasets, with citation | IEEE DataPort FAQ | "Can I use datasets available on IEEE DataPort in my research?" | B | Platform-level statement, not dataset-specific |
| E54 | Uploaded content is made available for reuse under CC BY 3.0 US by default | IEEE DataPort Terms of Use §2(g) | Terms page | B | Dataset page displays no licence field; default inferred from Terms |
| E55 | Standard Datasets require a subscription; access is not open | IEEE DataPort FAQ on Standard vs Open Access | FAQ page | B | — |
| E56 | Access licence is personal and non-transferable; public sharing is misuse | IEEE DataPort Terms of Use §2(a), §5(a)(vii) | Terms page | B | — |
| E57 | No subscription receipt, download log or author permission exists in the project | Workspace scan | `Admin/`, project files | A | Absence of evidence, not evidence of absence |
| E58 | D1 is a Standard Dataset with files behind a login | IEEE DataPort dataset page | "Subscription Required" | B | — |
| E59 | P06 exists; authors S. Sanjay, N. Krishna, G. Paramesh, K. V. Kiran Kumar; IC-AIDA 2026, p. 168 | IC-AIDA 2026 proceedings TOC; IEEE Xplore 11564455; Semantic Scholar | TOC entry; Xplore record | B | DOI taken from workbook; not independently resolved |
| E60 | P06 covers English, Hindi, Kannada, Tamil, Telugu, Bengali — **no Malayalam** | Semantic Scholar abstract; RACELit record | Abstract | B | Secondary academic portal, not publisher page |
| E61 | P06 reports F1 0.975 and ROC-AUC 0.997 | RACELit academic portal | Record summary | C | Not confirmed on publisher page |
| E62 | P10 has no confirmable authors, volume or pages | Searches 5 Nov 2026 | Title/DOI queries | A | Excluded from active literature |
| E63 | FSSHAP: IEEE MultiMedia 32(1):92–103, 2025; DOI 10.1109/MMUL.2024.3508765; authors Elangovan, Abirami, Thirumalai | IEEE Computer Society CSDL; ACM DL | Article record | B | Abstract only; full text paywalled |
| E64 | FSSHAP method: SHAP-based global feature selection + Random Forest; three datasets including Dravidian SMS in Tamil, Kannada, Telugu, Malayalam | CSDL abstract | Abstract | B | Dataset names not stated in abstract |
| E65 | FSSHAP references the D1 dataset DOI | CSDL reference list | Reference to `10.21227/dcym-pd69` | B | D1 use probable, not explicitly confirmed in abstract |
| E66 | FSSHAP reports no numeric results in its abstract; an author LinkedIn post claims >90% accuracy | CSDL abstract; author post | Abstract/post | C | LinkedIn is not a citable source |
| E67 | Related Dravidian SMS spam work exists: ICITIIT 2024 (10.1109/ICITIIT61487.2024.10580065), Springer 2023 (10.1007/978-981-99-6755-1_1), NCMDFE 2025 (10.1007/s41870-025-02635-5), Evolving Systems 2026 (10.1007/s12530-025-09761-2) | ORCID, Springer, search records | Publication lists | B/C | Metadata-level |
| E68 | No peer-reviewed Malayalam or Manglish smishing study was found | Searches 5 Nov 2026 | Query log in gap analysis | C | Absence of evidence, not proof |
| E69 | Splits were not executed at blocker closure; no `splits/` directory or hash existed on 5 Nov 2026 (superseded by E70–E76) | Workspace scan | `Research Work/` | A | Historical |

---

## 7. Phase 2 implementation evidence (5 November 2026)

| # | Claim | Source | Location | Level | Limitation |
|---|---|---|---|---|---|
| E70 | D1 Malayalam subset: **1,992** records, Ham 1,767 / Spam 225; 503 also Latin; 1,489 Malayalam-only script; **0** Tamil/Telugu/Kannada co-occurrence | `phase2/p2_extract.py` | `phase2/data/d1_malayalam.csv`, `metrics/subset_audit.json` | A | Script ≠ language |
| E71 | Exclusive D1 script buckets sum to 7,717; the earlier “discrepancy” was inclusive vs exclusive counting | same | `subset_audit.json` | A | — |
| E72 | D1 split: 1,394 / 299 / 299 (Spam 157/34/34); D2: 4,127 / 885 / 883; zero group/normalised overlap; SHA-256 manifest | `phase2/p2_split.py` | `phase2/splits/split_manifest.json` | A | Random split is not block-safe |
| E73 | D1 selected Linear SVM (char 2–4, C=0.5): accuracy 0.9866, macro-F1 0.9650, Spam P 1.000, R 0.8824, 4 FN / 0 FP | `phase2/p2_train_d1.py` | `metrics/d1_malayalam_results.json` | A | 34 Spam test rows; single split |
| E74 | D1 block-held-out macro-F1: 0.6964 (block 4001–5000), 0.4972 (5001–6000, no Spam in test), 0.368470 (6001–7000, only 12 train Spam); random split 0.9650 | `phase2/p2_robustness.py` | `metrics/d1_block_robustness.json` | A | Diagnostic; blocks are coarse |
| E75 | D2 selected Logistic Regression (char 2–4, C=1.0): accuracy 0.9638, macro-F1 0.8877; Ham F1 0.990, Spam F1 0.803, Smishing F1 0.871; 37 conflict groups / 76 records excluded | `phase2/p2_train_d2.py` | `metrics/d2_results.json` | A | Not comparable with D1 |
| E76 | Four models saved and reloadable; test evaluated once after validation-only selection; all artifacts reproducible from `phase2/README.md` | `phase2/models/`, `metrics/` | Joblib + prediction CSVs | A | No transformer yet |
| E77 | Literature status unchanged: 19 retained, P10 excluded, P06 verified but no Malayalam, FSSHAP abstract-only, 14 bibliographic-only | `Literature Review/LITERATURE_REVIEW_VERIFICATION.md` | §5 | B/C | Full texts paywalled |
