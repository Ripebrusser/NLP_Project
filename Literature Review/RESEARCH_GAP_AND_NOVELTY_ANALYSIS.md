# Research Gap and Novelty Analysis

**Rule:** a gap claim must survive a search for prior work that closes it. This document records what was searched, what was found, and what the project may therefore claim.

---

## 1. Searches performed (5 November 2026)

| Query | Purpose | Result |
|---|---|---|
| Malayalam phishing SMS detection dataset | Find Malayalam phishing work | No peer-reviewed Malayalam phishing/smishing SMS study found |
| Manglish phishing detection / Manglish SMS spam | Find Manglish cybersecurity work | No Manglish spam/phishing study; Manglish work is offensive language/sentiment |
| Malayalam spam SMS classification | Find Dravidian spam work | D1 dataset and its derivatives (E01, SMSDHL) |
| Dravidian code-mixed SMS spam classification | Find code-mixed spam work | Nothing specific; offensive-language shared tasks dominate |
| Malayalam cyber threat text classification | Find Malayalam CTI work | Nothing specific |
| Low-resource smishing | Test whether "low-resource" is novel | **Bemba, Bangla, Filipino studies exist** — not novel in general |

---

## 2. Gap that is supported by evidence

> **There is no verified, peer-reviewed SMS spam or smishing dataset or detection study for Malayalam script or Malayalam-English code-mixed (Manglish) text. Existing Dravidian SMS resources provide spam/ham labels only, and existing Malayalam/Manglish NLP resources provide sentiment/offensive-language labels only.**

Supporting evidence:

1. **D1** (the only Malayalam-containing SMS corpus in scope) has **Ham/Spam only**; the creators define spam as "business, annoying, and unnecessary messages", not phishing.
2. **D2** (the only smishing corpus in scope) contains **zero Indic-script records**.
3. **P12 DravidianCodeMix** (the standard Malayalam-English corpus) has **sentiment/offensive labels only**.
4. **T02 Thara & Poornachandran (2022)** handle Manglish for offensive language/sentiment, not spam.
5. Searches found **no** Malayalam/Manglish phishing or smishing detection paper.

This gap is **narrow and honest**: it is a gap in *langage-specific spam data and evaluation*, not a claim that no one has ever studied smishing.

---

## 3. Work that narrows the novelty (must be cited, not hidden)

| Work | Why it narrows the claim |
|---|---|
| **E01 Elangovan & Abirami (2025), IEEE MultiMedia** | Uses Dravidian SMS data and cites the **D1 DOI**; SHAP + Random Forest. The dataset is not new, and "first use of this corpus" is false. |
| **Elangovan/Abirami series (2023–2026)** | FSSHAP (IEEE MultiMedia 2025), XAI feature selection (ICITIIT 2024), hand-crafted features (Springer 2023), NCMDFE (2025), metadata features (Evolving Systems 2026). Dravidian SMS spam is an **active** line of work, not an open field. |
| **MDPI Electronics 2026, "Revisiting SMS Spam Detection"** | Confirms metadata-enriched features on Dravidian SMS datasets; another sign that classical Dravidian spam work is established. |
| **NLPAICS 2026 multilingual fraud work** | MrBERT/mROBERTa across English, Spanish, Valencian for spam/phishing/fake jobs — multilingual phishing is active beyond English. |
| **S01 SMSDHL preprint (2025)** | Describes the same dataset family across Dravidian languages + Hindi. Dataset construction is not a contribution. |
| **P05 PhishNet (2026)** | Already performs three-class ham/spam/smishing on D2 and reports spam↔smishing confusion. The three-class task is not new. |
| **P01 Almeida (2011)** | Established linear SVM on UCI SMS spam; the classical baseline is not new. |
| **Low-resource smishing studies** (Bemba/English — Zimba & Phiri 2025 preprint; Filipino-English — Corpuz et al. 2025; Bangla — BERT+Char-CNN) | "Smishing in a low-resource language" is already done for other languages. The gap is Malayalam-specific, not generic. |
| **HuggingFace `scam_ham_india_14_languages`** (non-peer-reviewed, 14,000 samples, 14 Indian languages) | An Indian multilingual scam/SMS resource exists publicly. Its provenance, annotation method and licence are unverified, and it is **outside the approved two-dataset scope**, but it means "no Indian-language scam data exists" is false. |
| **DravidianLangTech 2021–2025** | Malayalam/Manglish offensive-language work is crowded; only the *task* (spam/phishing) is open. |

---

## 4. Gap claims that are NOT supported

| Unsupported claim | Why |
|---|---|
| "First work on Malayalam phishing detection." | No Malayalam phishing data exists here; the project does not detect Malayalam phishing. Also, absence of evidence from a limited search is not proof of priority. |
| "First Malayalam-English code-mixed cybersecurity dataset." | The project creates no dataset and has no Manglish labels. |
| "No one has studied low-resource smishing." | Bemba, Bangla, Filipino studies exist. |
| "Dravidian SMS spam is unstudied." | E01, the Elangovan/Abirami series and SMSDHL exist. |
| "First transformer evaluation of Dravidian SMS spam." | Not established. No verified transformer study was found, but absence in this search is not priority; phrase as "we found no verified transformer evaluation" rather than "first". |
| "The dataset is new." | D1 is published (2023) and already used. |
| "Transformer models have not been applied to Dravidian SMS." | E01 and FSSHAP use Dravidian SMS; transformers are used across Dravidian NLP. |
| "Multilingual models solve Manglish." | MuRIL's transliterated evaluation is derived, not natural Manglish. |
| "98.5% is the state of the art to beat." | B01's dataset is unreleased and not comparable. |

---

## 5. Defensible contribution statement

The project's contribution is **empirical and methodological**, not a priority claim:

> This project provides a reproducible, leakage-controlled comparison of classical TF-IDF models and multilingual transformers for (i) Malayalam-script SMS spam detection and (ii) English three-class SMS smishing detection, using two public datasets with explicit duplicate-group splitting, per-class reporting, and a quantified language/script confound. It also documents, with evidence, why Malayalam and Manglish smishing detection cannot be claimed from the available data.

**Scope note (5 Nov 2026):** the Malayalam arm is conditional on documented access to D1. If D1 access cannot be evidenced, the project falls back to an English-only three-class smishing study.

**What this contributes:**
1. A verified audit of both datasets (counts, labels, scripts, duplicates, provenance) that corrects the published/working figures.
2. A grouped, script-stratified evaluation protocol that avoids the leakage present in random splits.
3. A direct classical-vs-transformer comparison on Malayalam-script SMS. The existing D1 literature (E01 and related work) uses handcrafted features and Random Forest; **no verified transformer evaluation of D1 was found**, but this is stated as an observed gap, not a priority claim.
4. A measurement of spam/smishing separability in D2, including the label-noise ceiling.
5. A negative/limiting result: script composition alone predicts D1's label to a substantial degree, which constrains how content-based results may be interpreted.

**What it does not contribute:** new data, new labels, a new language resource, a new model architecture, or a solved phishing problem.

---

## 6. Novelty statement (choose one, with guide approval)

**Option A — conservative, recommended:**
> "We present a reproducible, duplicate-grouped comparison of classical and multilingual transformer models for Malayalam-script SMS spam and English SMS smishing, with an explicit analysis of script-label confounding. We do not claim Malayalam phishing detection, because no such ground truth exists in the approved data."

**Option B — methods-focused:**
> "We quantify how much of Dravidian SMS spam classification is explained by script composition rather than message content, and we show the effect of duplicate-group splitting on reported performance."

**Option C — not permitted:**
> Any statement claiming first Malayalam/Manglish phishing detection, a new dataset, or state-of-the-art performance.

---

## 7. Required citations for the gap section

At minimum: D1 record, D2 record, E01, S01, P01, P05, P12, T02, plus one low-resource smishing study from another language (Bemba/Bangla/Filipino). This prevents the gap statement from looking like an unsearched assertion.

---

## 8. Conclusion

A real but **narrow** gap exists: Malayalam-script SMS spam has one published corpus and limited reproducible evaluation; Malayalam/Manglish smishing has **no** data at all. The project can contribute a careful comparative evaluation and a documented negative result about data availability. It cannot claim to detect phishing in Malayalam, cannot claim Manglish coverage, and cannot claim dataset or task novelty.

---

## 9. Phase 2.3 empirical update (5 November 2026)

**No new literature search was run for this update.** The statements below connect the completed experiments to the matrix in §4; they do not add references or novelty claims.

### 9.1 What the results change in the gap argument

1. **The evaluation gap is confirmed, not filled.** The D1 corpus has three source blocks and one dominant Spam batch; the random split scores 0.9650 Macro-F1 for the SVM, but leave-one-block-out falls to 0.5378. This is direct evidence that a single-corpus random split is not a source-diverse benchmark. It strengthens the case that the field lacks a reproducible, source-diverse Malayalam SMS evaluation; it does not supply one.
2. **The transformer result is a limiting negative result.** MuRIL ties the SVM within-source (identical seed-42/44 predictions) and collapses under block holdout (0.5028 pooled Macro-F1, 3.56% Spam recall, near-constant block-6001 probabilities). This is consistent with the matrix's general observation that multilingual transformer evidence for Indic SMS is thin; it does not establish a new method or a new literature finding.
3. **Threshold calibration is not a substitute for source coverage.** Block-6001 ranking is strong (PR-AUC ≈ 0.980), and a validation-selected SVM threshold raises recall from 6.6% to 60.1% at precision 1.0 in one split. But the threshold is unstable across inner splits (recall 44.3% ± 16.8) because training has only 12 Spam. The practical gap is target-source calibration data, not another classifier.
4. **No dataset or task novelty.** The project reuses an existing Malayalam corpus and an existing English SMS dataset. The contribution is a leakage-controlled comparative evaluation, complete uncertainty reporting and a documented boundary condition. The thesis should say that plainly.
5. **No phishing/Manglish claim.** D1 has no phishing label; D2 is English-only. The earlier finding that Malayalam/Manglish smishing has no usable data is unchanged by these experiments.

### 9.2 Most important unresolved references

These are bibliographic/verification gaps only; no new search was attempted.

| Ref | Status | Consequence for the write-up |
|---|---|---|
| P10 | **EXCLUDED — no confirmable record** | Do not cite. Do not use as related work. |
| T01 | No DOI captured | Cite only with the stable URL actually verified; flag the missing DOI in the reference audit. |
| P08 | No DOI; ACL Anthology URL available | Use the ACL URL as the stable identifier; do not invent a DOI. |
| P09 | Publisher returned 403; author names unconfirmed | Do not attribute claims to unverified authors; either re-verify before submission or drop the row. |
| P01, P02, P13, P14, P15 | Only partially verified (metadata/abstract, not full text) | Restrict citations to the verified metadata; do not attribute detailed methods or findings. |
| P13 (MuRIL) | Metadata verified; used as the model source | Cite for the checkpoint only, not for claims about Malayalam SMS performance. |

### 9.3 Consequence

The supported contribution remains **a careful comparative evaluation and a documented negative result about data availability**, now with stronger evidence: within-source classical performance is high, source holdout is poor, MuRIL adds no within-source gain and fails under source shift, and calibration cannot be trusted with 12 training Spam. The thesis must not describe this as a new detection method, a new dataset, or evidence of generalisation to unseen Malayalam SMS sources.
