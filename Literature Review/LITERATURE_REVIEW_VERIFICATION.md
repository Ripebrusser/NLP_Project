# Literature Review Verification

**Audit date:** 5 November 2026  
**Scope:** 20 records — 15 core papers from the project workbook, the base paper, and 4 additional primary sources found during this audit.  
**Rule applied:** a paper is only described at the level actually inspected. "Abstract/metadata only" is stated explicitly. No result is cited from a paper whose full text was not read.

---

## 1. Verification levels used

| Level | Meaning | Count |
|---|---|---|
| **A — Full text read** | The paper's methods and results were read directly. | **1** (B01 base paper) |
| **B — Metadata verified today** | Title, authors, venue and identifier checked against a publisher/index record today; methods/results taken from the workbook or abstract. | **4** (P06, E01, T02, S01) |
| **C — Bibliographic record only** | DOI/venue confirmed previously; full text not re-read this audit. | **14** (P01–P05, P07–P09, P11–P15, T01) |
| **D — Excluded** | Record could not be confirmed; no findings may be cited. | **1** (P10) |
| | | **20 total** |

Only **B01 (base paper)** and **P01** have been read at method level. Everything else is reported as the authors' claims, not as independently reproduced facts.

---

## 2. What was independently confirmed today

| Item | Confirmation |
|---|---|
| **B01** Mahmood & Hameed (2023) | Iraqi Journal of Science, vol. 64, no. 10, DOI 10.24996/ijs.2023.64.10.41. Journal page and PDF both retrieved. Abstract reports 98.5 / 96.9 / 93.1 / 95.05. **Page-number discrepancy:** publisher "How to Cite" and Google Scholar give pp. 6276–6291, while the PDF running header gives pp. 5376–5391. Both refer to the same DOI. |
| **D2 provenance** | Mendeley Data V1, DOI 10.17632/f45bkkt8pr.1, published 20 June 2022, CC BY 4.0, Mishra & Soni (JIIT Noida), exactly 5,971 = 4,844 ham + 489 spam + 638 smishing. Companion SoCPaR 2022 paper DOI 10.1007/978-3-031-27524-1_57. |
| **D1 provenance** | IEEE DataPort, DOI 10.21227/dcym-pd69, 2 June 2023, Elangovan & Abirami; English/Tamil/Telugu/Kannada/Malayalam; "nearly 7700"; two columns; `Spam Message Collection.xlsx` 1.26 MB; subscription required; licence not displayed. |
| **E01** Elangovan & Abirami (2025) | "FS_SHAP: Global Interpretable Feature Selection Using XAI for the Classification of Spam SMS in Dravidian Languages", IEEE MultiMedia, vol. 32, no. 1, pp. 92–103, DOI 10.1109/MMUL.2024.3508765. Uses the D1 dataset — **prior work on this exact corpus exists.** |
| **S01** SMSDHL preprint | TechRxiv, 5 Jan 2025, DOI 10.36227/techrxiv.173603655.53756505, CC BY 4.0, Elangovan & Abirami; describes English/Tamil/Telugu/Malayalam/Kannada/Hindi spam SMS. |
| **T02** Thara & Poornachandran (2022) | "Social media text analytics of Malayalam–English code-mixed using deep learning", Journal of Big Data, DOI 10.1186/s40537-022-00594-3. Handles Romanised Malayalam (Manglish) for **offensive language and sentiment**, not spam/phishing. |
| **T01** Timko & Rahman (2024) | "Smishing Dataset I: Phishing SMS Dataset from Smishtank.com", CODASPY '24; community-sourced smishing corpus (1,062 samples). DOI not captured on the ACM record; metadata only. |
| **P06** Sanjay et al. (2026) | IC-AIDA 2026, p. 168; IEEE Xplore 11564455; XLM-RoBERTa + continual learning; English, Hindi, Kannada, Tamil, Telugu, Bengali — **no Malayalam**; F1 0.975 / ROC-AUC 0.997 per a secondary portal. |
| **E01** Elangovan, Abirami & Thirumalai (2025) | IEEE MultiMedia 32(1):92–103, DOI 10.1109/MMUL.2024.3508765; SHAP feature selection + Random Forest; three Dravidian SMS datasets; abstract reports metric comparisons but no numbers; full text paywalled. |

---

## 3. Confirmed landscape (what the literature actually contains)

### 3.1 SMS spam detection

- **P01 Almeida et al. (2011)** released the UCI SMS Spam Collection (5,574 English messages) and showed linear SVM is a strong baseline (97.64% accuracy, MCC 0.893). It is a **spam** study: no phishing labels, no Malayalam.
- **P07 Filali et al. (2026)** and **P10 (2026)** extend English spam pipelines with augmentation and systematic component ablations. P07's "multilingual" data are **machine-translated** French/German/Hindi copies of the English corpus — not natural multilingual text, and no Malayalam.
- **P03 Xu et al. (2025)** combine SVM + Random Forest with SMOTE; the 99.58% figure comes from a preprint abstract and is not confirmed in the final article.

**Synthesis:** English SMS spam is a mature, near-ceiling benchmark. New English-only spam results are unlikely to be informative. The open question is Dravidian-language spam, which is exactly what D1 supports.

### 3.2 Smishing detection (SMS phishing)

- **P02 Mishra & Soni (2020)** define smishing as content + URL behaviour + source code + APK, with a Naive Bayes content module. **DSmishSMS** (Neural Computing and Applications, DOI 10.1007/s00521-021-06305-y) reports 97.93% accuracy using domain checking + SMS classification.
- **P04 Hassan et al. (2026)** take the UCI **spam** corpus and rename the spam label "smish". This is label relabelling, not smishing data, and it is the clearest example of the spam/smishing conflation problem.
- **P05 PhishNet (2026)** uses a genuine three-class dataset (D2) but adds a synthetic spam class in Dataset2 and reports that **all models struggle to separate spam from smishing**. This is consistent with the 37 conflicting spam/smishing groups found in D2.
- **B01 Mahmood & Hameed (2023)** combine Google + VirusTotal URL inspection with a UTF-IDF + Chi-square + SVM/RF/AdaBoost/XGBoost content classifier; best SVM 98.5% accuracy / 95.05% F1. English only; smishing labels derived from 120 Pinterest images plus UCI spam extraction; dataset not released.

**Synthesis:** smishing detection is well studied in English, typically with URL/domain signals. **No paper in this set detects smishing in Malayalam or Manglish.** The only multilingual smishing work is either proprietary (P08), unreleased/preprint (P09), translated (P07), or unverified (P06).

### 3.3 Multilingual and low-resource cybersecurity NLP

- **P08 Amaral Cejas et al. (2026)** is the closest framing: three-class HAM/SPAM/SMISHING on a **proprietary** multilingual telecom corpus. Languages are not named in the abstract; Malayalam is not confirmed. Not reproducible.
- **P06 Sanjay et al. (2026)** is now **resolved**: IC-AIDA 2026, p. 168, authors S. Sanjay, Nishant Krishna, G. Paramesh, K. V. Kiran Kumar, IEEE Xplore 11564455. Method: XLM-RoBERTa + continual learning. Languages: English, Hindi, Kannada, Tamil, Telugu, Bengali — **Malayalam is not included**. Reported F1 0.975 / ROC-AUC 0.997 comes from a secondary academic portal, not the publisher. It is usable as evidence of multilingual phishing work, **not** as Malayalam evidence.
- **P09 Phap (2026)** targets cost-sensitive edge smishing detection; dataset and language unverified (publisher 403).
- Outside the workbook, the audit found **low-resource smishing work in other languages**: Bemba/English (Zimba & Phiri, Research Square preprint, DOI 10.21203/rs.3.rs-7521286/v1), Filipino-English code-switching (Corpuz et al., WCTP 2025), Bangla (BERT + Char-CNN). This **weakens any claim that "low-resource smishing" itself is a novel gap** — the gap is language-specific, not generic.

### 3.4 Malayalam and Malayalam-English NLP

- **P12 DravidianCodeMix (2022)** provides ~20,000 Malayalam-English YouTube comments with **sentiment and offensive-language** labels. It is the standard Malayalam code-mixed resource and has **no phishing, spam or scam labels**.
- **T02 Thara & Poornachandran (2022)** handle Manglish explicitly (selective transliteration/translation) for offensive language and sentiment.
- The DravidianLangTech shared tasks (2021–2025) repeatedly study **offensive/abusive language** in Malayalam and Manglish, with strong transformer results. This is a crowded area.
- **Dravidian SMS spam already has an active literature.** Elangovan and Abirami have published a series using Dravidian SMS data: FSSHAP (IEEE MultiMedia 2025), XAI-based feature selection (ICITIIT 2024), hand-crafted feature evaluation (Springer 2023), NCMDFE (2025) and a metadata-feature study (Evolving Systems 2026). This is **spam** work with handcrafted features and Random Forest, not smishing and not a transformer comparison.
- **P13 MuRIL** and **P14 XLM-R** are the standard multilingual backbones; MuRIL's transliterated evaluation data are **derived by transliterating native-script text**, not naturally typed Manglish.

**Synthesis:** Malayalam/Manglish NLP is active, but almost entirely for sentiment, offensive language, hate speech and fake news. **No peer-reviewed Malayalam or Manglish *smishing* study was found.** Dravidian SMS *spam* is not unstudied — the Elangovan/Abirami series covers it with classical and handcrafted-feature methods — but **no verified transformer-based evaluation of D1** was found. The gap is therefore narrow: Malayalam/Manglish **smishing** has no data at all, and the Dravidian spam corpus lacks a transformer comparison.

### 3.5 Language identification and Romanisation

No dedicated Malayalam/Manglish language-identification tool was verified in this audit. Script detection (Unicode blocks) is reliable for **script**, not language. The project therefore reports **script composition**, never "language labels", and treats Latin-script messages as unresolved between English and Romanised Malayalam.

---

## 4. Coverage check against the required areas

| Required area | Covered by | Status |
|---|---|---|
| SMS spam detection | P01, P03, P07, P10 | Covered |
| SMS phishing / smishing | P02, P04, P05, P09, B01, T01 | Covered |
| ML for malicious SMS | P03, P10, P11 | Covered |
| DL / transformers for SMS | P04, P05, P07, P09 | Covered |
| Multilingual cybersecurity | P06, P08 | Covered; P06 verified but excludes Malayalam; P08 proprietary |
| Low-resource NLP | P07, P08, P09, T01 (Bemba/Bangla/Filipino cited in §3.3) | Covered |
| Malayalam NLP | P12, T02 | Covered |
| Malayalam-English code-mixed | P12, T02 | Covered |
| Romanised / Manglish processing | T02 (+ P12 context) | Partially covered |
| Multilingual language identification | — | **Not covered by a verified paper; documented as a limitation** |
| Multilingual transformers | P13, P14, P15 | Covered |

The language-identification gap is a genuine limitation of the review, not something to paper over. The project compensates by using **Unicode script detection only** and by refusing language-level claims.

---

## 5. Verification table

| ID | Short reference | Verification | Can its numbers be cited? |
|---|---|---|---|
| P01 | Almeida et al. 2011 | Partial — metadata + workbook method record | Yes, as authors' reported values |
| P02 | Mishra & Soni 2020 | Partial — bibliographic + dataset record | Methods only; numbers not extracted |
| P03 | Xu et al. 2025 | Partial — DOI via citing paper | No (preprint abstract only) |
| P04 | Hassan et al. 2026 | Partial — workbook | Yes, flagged as reported |
| P05 | Alhuzali et al. 2026 | Partial — workbook + repository | Yes, flagged as reported |
| P06 | Sanjay et al. 2026 | **Verified metadata + abstract; no Malayalam** | Yes, as multilingual context only |
| P07 | Filali et al. 2026 | Partial — workbook | Yes, flagged |
| P08 | Amaral Cejas et al. 2026 | Partial — ACL record | Abstract claims only |
| P09 | Phap 2026 | Partial — 403 | No |
| P10 | Unknown authors 2026 | **Excluded** | **No** |
| P11 | Birthriya et al. 2026 | Partial | No |
| P12 | Chakravarthi et al. 2022 | Partial | Yes, flagged |
| P13 | Khanuja et al. 2021 | Partial | Yes, flagged |
| P14 | Conneau et al. 2020 | Partial | Yes, flagged |
| P15 | Devlin et al. 2019 | Partial | Background only |
| B01 | Mahmood & Hameed 2023 | **Full text read** | Yes |
| E01 | Elangovan & Abirami 2025 | Metadata verified today | Dataset-use claim only |
| T01 | Timko & Rahman 2024 | Metadata only | Dataset existence only |
| T02 | Thara & Poornachandran 2022 | Metadata verified today | Task-scope claim only |
| S01 | SMSDHL preprint 2025 | Metadata verified today | Dataset description only |

---

## 6. Errors and weaknesses found in the existing literature record

1. **P06 is resolved but frequently misused.** It exists (IC-AIDA 2026, p. 168) and covers six Indian languages — **not Malayalam**. It cannot be cited as Malayalam or as evidence that Malayalam phishing detection exists.
2. **P10 is excluded.** No author list, volume or pages could be confirmed; the title/DOI return only a citation stub. It must not appear in the report.
3. **P01 does not validate TF-IDF.** The 2011 paper used token-count features with WEKA defaults; the earlier project presentation implied TF-IDF support that the paper does not provide.
4. **P04's "smish" label is UCI spam renamed.** It must never be described as a smishing dataset.
5. **P05's Dataset2 spam is synthetic** (Faker). Its 100% result is not evidence of real-world performance.
6. **P12's labels are sentiment/offensive, not phishing.** Any use as a threat corpus is invalid.
7. **MuRIL transliterated test sets are derived, not natural Manglish.** No Manglish performance may be inferred.
8. **B01's page numbers conflict** between the publisher's citation (6276–6291) and the PDF header (5376–5391). Use the DOI and note the discrepancy.

---

## 7. Consequence for the project

The literature supports **two claims only**:

1. English SMS smishing is well studied, and spam/smishing separation is a known hard boundary (P05, B01).
2. Malayalam/Manglish NLP exists for offensive language and sentiment (P12, T02) but **not for SMS spam or smishing**.

It does **not** support:
- a claim that Malayalam phishing detection is an open problem solved here;
- a claim that Manglish is covered;
- a claim that D1 has been unused (E01 uses it);
- a claim that low-resource smishing is untouched (Bemba, Bangla, Filipino work exists).
