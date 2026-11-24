# Base Paper Selection

**Question:** is Mahmood & Hameed (2023) a suitable base paper, and if not, what should replace it?

---

## 1. Candidate base paper — verified record

| Field | Value |
|---|---|
| Title | A Smishing Detection Method Based on SMS Contents Analysis and URL Inspection Using Google Engine and VirusTotal |
| Authors | Ameen R. Mahmood, Sarab M. Hameed (University of Baghdad) |
| Journal | Iraqi Journal of Science, vol. 64, no. 10 |
| Date | 30 October 2023 |
| DOI | 10.24996/ijs.2023.64.10.41 |
| Pages | Publisher citation: 6276–6291; PDF running header: 5376–5391 — **discrepancy noted** |
| Full text | Read (official PDF) |

**Reported method:** two stages — (1) URL inspection using Google Search plus the VirusTotal API; (2) SMS content analysis with "UTF-IDF" (TF-IDF computed over label-split vocabularies) plus Chi-square top-1000 feature selection, classified by SVM (RBF), Random Forest, AdaBoost and XGBoost, evaluated with stratified 3-fold CV.

**Reported results:** best SVM — accuracy 98.5%, precision 96.9%, detection rate 93.1%, F1 95.05%. URL inspection detected 156 smishing messages vs 145 for VirusTotal alone.

---

## 2. Suitability assessment

| Criterion | Assessment | Verdict |
|---|---|---|
| **Is the dataset public?** | No. The paper states the smishing dataset is not published. UCI is public, but the 867 smishing messages are not released. | ❌ Fails reproducibility |
| **Are the labels reliable?** | Weak. Smishing messages come from 120 Pinterest images converted to text plus extraction from the UCI spam set. This is not a naturally collected, independently annotated smishing corpus. | ❌ Weak ground truth |
| **Does the language match?** | No. English only. No Malayalam, Tamil, Manglish or code-mixing. | ❌ Fails language match |
| **Are the methods reproducible?** | Partially. Preprocessing and classifiers are described in enough detail to re-implement, but the data are unavailable and the URL stage depends on live Google and VirusTotal APIs (rate limits, keys, changing results). | ⚠️ Partial |
| **Is it a fair performance reference?** | No. 98.5% on a corpus whose smishing class is partly derived from the same spam pool cannot be compared with results on a different dataset. | ❌ Not comparable |
| **Does it define the task well?** | Yes. It clearly separates smishing from spam, documents preprocessing, and reports precision/recall/F1 separately. | ✅ Useful |
| **Does it support the project's method choice?** | Partially. It supports TF-IDF + SVM + Chi-square for SMS text, but its "UTF-IDF" variant is bespoke and unvalidated outside this paper. | ⚠️ Partial |

**Overall: NOT SUITABLE as a direct baseline.** It can be cited as a **methodological reference** for smishing framing and metric reporting, but its dataset, language and results cannot anchor this project.

---

## 3. Why no single paper is a direct baseline

This project has **two tasks on two datasets**:

| Task | Data | What a baseline would need |
|---|---|---|
| Malayalam-script SMS spam | D1 (1,992 Malayalam records) | A Dravidian-language SMS spam study on the same corpus or a comparable Malayalam corpus |
| English SMS smishing | D2 (5,971 records) | An English smishing study on D2 with a released split |

No paper satisfies either fully:
- **E01 (Elangovan & Abirami 2025)** uses D1, but for feature selection with handcrafted features; its splits and full method are not available (paywalled), and it does not report the exact protocol needed to reproduce a baseline.
- **B01 (Mahmood & Hameed 2023)** is English and does not use D2.
- **P05 (PhishNet 2026)** uses D2, but its test set is enriched with synthetic samples and its splits are not released; its 92%/100% figures are not a clean baseline.
- **P01 (Almeida 2011)** is the cleanest classical text baseline, but it is English spam only.

**Conclusion: the project should use two reference papers, not one base paper.**

---

## 4. Recommended reference set

| Role | Paper | Justification |
|---|---|---|
| **Primary base paper (framing)** | **B01 Mahmood & Hameed (2023)** | Closest published smishing methodology with a full-text-verified protocol; defines the two-stage idea the project deliberately does not reproduce (text-only). Use for task framing and metric reporting, not for expected numbers. |
| **Classical baseline reference** | **P01 Almeida et al. (2011)** | Public UCI corpus, linear SVM baseline, MCC/accuracy reported; supports the TF-IDF + linear SVM choice as a standard short-text baseline (note: P01 itself used token counts, not TF-IDF). |
| **Dataset reference (D1)** | **E01 Elangovan & Abirami (2025)** + IEEE DataPort record | Establishes that D1 exists, is published, and has been used for spam classification. |
| **Dataset reference (D2)** | **D2 Mendeley record + SoCPaR 2022 paper** | Authoritative provenance, licence and label definitions. |
| **Transformer reference** | **P13 MuRIL**, **P14 XLM-R** | Justify the multilingual model choice; no Manglish performance claim. |
| **Cautionary reference** | **P05 PhishNet (2026)**, **P04 Hassan et al. (2026)** | Document the spam/smishing confusion and the label-relabelling problem. |

If the department requires exactly one "base paper", use **B01** and state in the report:

> "Mahmood & Hameed (2023) is adopted as the methodological base paper for smishing framing. Its dataset is not public, its smishing labels are image-derived, and it is English-only; therefore its reported 98.5% accuracy is not treated as an expected result, and the present work does not reproduce its URL-inspection stage."

---

## 5. What must not be claimed

- That the project "extends" B01 to Malayalam (the data cannot support it).
- That B01's 98.5% is a target or a comparison point.
- That B01's UTF-IDF is validated; it is a single-paper variant.
- That B01's URL stage is reproduced; it requires Google/VirusTotal APIs and is out of scope.
- That E01 provides a reproducible baseline; its full protocol is not available.

---

## 6. Decision

| Question | Answer |
|---|---|
| Is Mahmood & Hameed (2023) suitable as the primary baseline? | **No — methodological reference only.** |
| Is there a single suitable direct baseline? | **No.** The project uses two tasks and two datasets. |
| Recommended base paper for framing | **B01 Mahmood & Hameed (2023)**, with explicit caveats. |
| Recommended classical baseline reference | **P01 Almeida et al. (2011)**. |
| Recommended dataset/prior-work reference | **E01 Elangovan & Abirami (2025)** for D1; **D2 record** for D2. |
| Approval needed | Yes — the guide should confirm the two-reference approach. |
