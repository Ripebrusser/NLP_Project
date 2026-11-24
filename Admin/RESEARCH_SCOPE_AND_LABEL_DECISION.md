# Research Scope and Label Decision

> **HISTORICAL / SUPERSEDED.** This document records an earlier project state. It is retained for audit provenance and must not be cited for current scope, counts, model status or conclusions. The authoritative documents are `CANONICAL_FINAL_RESULTS.md`, `FINAL_METHODOLOGY_AND_OBJECTIVE.md`, `DATASET_PROVENANCE_AND_PERMISSIONS.md`, `LITERATURE_AUDIT_STATUS.md` and `VERIFICATION_REPORT.md`.


**Status:** proposed, awaiting approval. This document replaces the scope implied by the original project title.  
**Evidence base:** `DATASET_AUDIT_REPORT.md`; raw counts in `Research Work/audit_output/`.

---

## 1. Why the original title cannot stand

Original title: *"NLP-Based Cybersecurity Threat Detection in Malayalam and Malayalam-English Code-Mixed Text."*

It implies four things the data do not support:

| Implied claim | Evidence against |
|---|---|
| Malayalam **phishing/threat** labels exist | Dataset 1 has only Ham/Spam; its creators define spam as "business, annoying, and unnecessary messages". No phishing, smishing, scam or credential-theft label exists anywhere in the Malayalam data. |
| A **Malayalam-English code-mixed** corpus is available | Dataset 1 is a **five-language** Dravidian corpus (Malayalam 1,992; Tamil 1,175; Telugu 1,068; Kannada 1,345; Latin-only 2,130). Only 503 messages mix Malayalam script with Latin characters. |
| **Manglish** can be studied | A documented Romanised-Malayalam screen finds **34 records (0.44%)**. This is too few to train or evaluate a Manglish condition, and the screen is a heuristic, not annotation. |
| The two datasets form one system | They overlap on **773 normalised messages** (1,555 D1 / 831 D2 records), and 189 overlapping D1 "Spam" messages are D2 "smishing" while 51 are D2 "ham". Joint training would leak and inject contradictory labels. |

Keeping the title would force the project to either invent labels or overstate what was measured. Both are prohibited.

---

## 2. Final recommended title

> **Classical and Multilingual Transformer Models for SMS Spam and Smishing Detection in Malayalam-Script and English Text**

**Subtitle (for the report cover):** *A reproducible two-dataset study with duplicate-grouped evaluation*

Why each phrase is defensible:

- **"SMS Spam and Smishing"** — exactly the two label sets that exist (D1 spam/ham; D2 ham/spam/smishing).
- **"Malayalam-Script"**, not "Malayalam" — the unit of analysis is messages containing Malayalam script (1,992), not a verified language label.
- **"and English Text"** — D2 is English-only; D1's Latin-only component is English.
- **"Classical and Multilingual Transformer Models"** — TF-IDF linear models vs MuRIL/XLM-R, the actual planned comparison.
- No "cybersecurity threat detection" umbrella: spam is not a cybersecurity threat, and the only phishing-adjacent class (smishing) exists in English only.

**Alternative if the guide requires a "cybersecurity" framing:**

> *Smishing Detection in English SMS and Spam Classification in Malayalam-Script SMS: A Comparative Model Study*

This is narrower but keeps "cybersecurity" attached only to smishing, where it is accurate.

**Titles that must not be used:** any title claiming Malayalam phishing detection, Malayalam-English code-mixed phishing detection, Manglish threat detection, or a unified multilingual model.

---

## 3. Final problem statement

> SMS spam and SMS phishing (smishing) are widely studied in English, but the evidence base for Dravidian-language SMS is limited to spam/ham corpora with no phishing ground truth, and no verified Malayalam or Manglish phishing dataset exists. This project therefore asks two separate, answerable questions on the only two approved datasets: (i) how well classical TF-IDF models and multilingual transformers detect **spam in Malayalam-script SMS**, and (ii) how well the same model families separate **ham, spam and smishing in English SMS**, including whether spam and smishing are distinguishable at all. The project does not claim Malayalam phishing detection or Manglish coverage, because the approved data cannot support either.

---

## 4. Research objectives

1. **O1 — Reproducible data foundation.** Document, audit and freeze both datasets (counts, labels, scripts, duplicates, provenance) and produce leakage-safe splits. *(Audit complete; splits specified, not yet executed.)*
2. **O2 — Malayalam-script spam baseline.** Establish majority-class and TF-IDF (word + character n-gram) linear baselines for Ham/Spam on the Malayalam subset (1,992 records; 225 spam).
3. **O3 — Multilingual transformer comparison.** Fine-tune one multilingual transformer (MuRIL preferred; XLM-R as fallback) on the same splits and compare with O2 under identical evaluation.
4. **O4 — English three-class smishing task.** Repeat O2–O3 on D2 (5,971 records; ham 4,844 / spam 489 / smishing 638) with per-class precision, recall and F1.
5. **O5 — Script-mixing and confound analysis.** Quantify performance for Malayalam-only vs Malayalam+Latin messages, and measure how much a script-only classifier can predict the label (confound check).
6. **O6 — Cross-dataset domain-shift probe.** Train on one dataset's English/spam component and test on the other, to test whether performance survives domain shift. Reported as an exploratory probe, never as a combined system.
7. **O7 — Error analysis.** Characterise spam↔smishing confusion in English and false positives/negatives in Malayalam, with examples and support counts.

*Out of scope:* dataset creation, manual annotation, synthetic data, augmentation, SMOTE, Malayalam phishing detection, Manglish modelling, URL/APK analysis, deployment.

---

## 5. Research questions

| ID | Question | Dataset | Primary metric |
|---|---|---|---|
| RQ1 | How well do TF-IDF linear models detect Malayalam-script SMS spam against a majority baseline? | D1 Malayalam subset | Macro-F1, spam recall/precision |
| RQ2 | Does a multilingual transformer (MuRIL/XLM-R) outperform TF-IDF on Malayalam-script spam? | D1 Malayalam subset | Macro-F1 difference with CI |
| RQ3 | Does script mixing (Malayalam-only vs Malayalam+Latin) change performance? | D1 | Macro-F1 by stratum |
| RQ4 | How separable are ham, spam and smishing in English SMS? | D2 | Per-class F1; spam↔smishing confusion |
| RQ5 | Do classical and transformer models rank the same way on the English three-class task as on Malayalam spam? | D1 + D2 | Metric comparison |
| RQ6 | Does a model trained on one dataset transfer to the other's English spam component? | D1↔D2 | Cross-dataset macro-F1 vs in-domain |
| RQ7 | How much of the D1 label is predictable from script/language alone? | D1 | Script-only classifier macro-F1 |

RQ7 is a **validity check**, not a contribution: if script alone predicts spam well, content-based results must be interpreted cautiously.

---

## 6. Approved classification tasks

| Task | Dataset | Classes | Records | Notes |
|---|---|---|---|---|
| **T1** | D1 Malayalam subset | Ham / Spam (binary) | 1,992 (1,767 / 225) | Primary Malayalam task |
| **T1b** | D1 Malayalam-only script | Ham / Spam | 1,489 (1,429 / 60) | Secondary; report support, no strong claim |
| **T2** | D2 | Ham / Spam / Smishing (3-class) | 5,971 (4,844 / 489 / 638) | Primary English task |
| **T2b** | D2 | Ham / Smishing (binary) | 5,482 | Secondary; tests the cybersecurity-relevant boundary |
| **T3** | D1 all languages | Ham / Spam | 7,714 | Optional multilingual comparison across Tamil/Telugu/Kannada/Malayalam |
| **T4** | D1↔D2 | Binary spam transfer | — | Exploratory domain-shift probe only |

**Not approved:** any task that merges D1 and D2 into one training set.

---

## 7. Label definitions (authoritative for this project)

| Label | Dataset | Definition | Source |
|---|---|---|---|
| `Ham` | D1 | Normal, legitimate message | Dataset creator (IEEE DataPort record) |
| `Spam` | D1 | "Business, annoying, and unnecessary messages an anonymous user sends" | Dataset creator |
| `ham` | D2 | Legitimate message | Mishra & Soni (Mendeley record) |
| `spam` | D2 | Unsolicited/junk message; UCI-derived | Mishra & Soni |
| `smishing` | D2 | SMS phishing message intended to deceive the recipient | Mishra & Soni |

**Rules:**
- D1 `Spam` **must not** be described as phishing, smishing or a cybersecurity threat.
- D2 `Spam` and `smishing` **must not** be merged in the primary experiment; they are separate classes.
- D1 `Spam` and D2 `spam` share a name but not a verified definition; they are never pooled.
- No label is inferred from message content.

---

## 8. Dataset-to-task mapping

| Dataset | Task | Permitted | Not permitted |
|---|---|---|---|
| D1 | T1, T1b, T3, T4 | Malayalam-script spam detection; Dravidian language comparison; confound analysis | Phishing; Manglish; "Malayalam-English corpus" |
| D2 | T2, T2b, T4 | English 3-class smishing; spam/smishing separability | Malayalam/Manglish; multilingual claims; URL/APK behaviour |
| D1 + D2 | T4 only | Train-on-one/test-on-other probe | Joint training; pooled metrics |

---

## 9. Can the datasets be combined? — **No**

**Verdict: NO-GO for combined training.** Reasons, in order of severity:

1. **Direct leakage.** 773 normalised messages appear in both datasets; 1,555 D1 records and 831 D2 records are involved. A combined random split would put the same message in train and test.
2. **Label contradiction.** Among overlaps: 189 D1-Spam = D2-smishing, 87 = D2-spam, **51 = D2-ham**, 6 D1-Ham = D2-spam. The same message is labelled differently by the two sources.
3. **Different label spaces.** D1 has 2 classes, D2 has 3. Mapping D1-Spam→smishing would fabricate labels; mapping D2-smishing→spam would erase the only phishing class.
4. **Source artefacts.** D1 is organised in contiguous source blocks (one block of 1,000 records is 100% Ham); D2 is UCI-derived. A combined model can learn "which file am I from".
5. **Language confound.** D1's spam rate ranges from 2.4% (Tamil-only) to 65.4% (Tamil+Latin) by script. Adding D2's English-only distribution worsens this.

**What remains permitted:** T4 cross-dataset evaluation (train on D2 ham/spam → test on D1 Latin-only ham/spam, and the reverse), reported as a domain-shift probe with an explicit warning that label semantics differ. This is an experiment, not a combined model.

---

## 10. Language limitations

1. **No verified Manglish subset.** 34 heuristic hits (0.44%); no annotation; Latin-script ≠ Manglish. Manglish is removed from the scope and the title.
2. **Script ≠ language.** Malayalam Unicode indicates Malayalam-script content, not Malayalam-language content; messages may contain English words in Malayalam script or vice versa.
3. **Malayalam-only spam support is small** (60 records). A test split yields ~9 spam messages; per-class F1 will have wide confidence intervals.
4. **Four Dravidian languages are present**, so "Dravidian" results are not "Malayalam" results.
5. **Dataset 2 has zero Indic-script records.** No cross-lingual claim is possible from it.

---

## 11. Cybersecurity limitations

1. **No Malayalam phishing/smishing ground truth exists in the approved data.** The project cannot detect Malayalam phishing and must not say it does.
2. **Smishing exists only in English (D2).** Any cybersecurity claim is confined to English SMS.
3. **Text-only.** D2 provides only presence flags for URL/EMAIL/PHONE; no URL content, no APK, no sender reputation. URL-behaviour methods (e.g. Mahmood & Hameed 2023) cannot be reproduced.
4. **Spam ≠ cyber threat.** D1 spam is promotional/annoying content, not an attack.
5. **Small smishing class** (638) and noisy boundary with spam (37 conflicting groups).
6. **Dataset overlap with UCI** means D2's ham/spam portion is a benchmark already near ceiling in prior work; gains there are not evidence of real-world robustness.

---

## 12. Claims the project must avoid

- "First work on Malayalam phishing / smishing detection."
- "Detects cybersecurity threats in Malayalam / Manglish."
- "Malayalam-English code-mixed phishing dataset."
- "Manglish performance" of any kind.
- "Multilingual model" claims based on D1's five languages when evaluating only Malayalam, unless the multilingual experiment (T3) is actually run.
- "State-of-the-art" or comparisons with papers that used different data/splits.
- Any F1/accuracy number before training and evaluation.
- "The dataset contains X% phishing" for D1.
- "Combined dataset" results.
- Treating D1 `Spam` and D2 `smishing` as the same class.
- Presenting the audit's script counts as language labels.

---

## 12A. Dataset 1 availability condition (added 5 Nov 2026)

D1's **licence** question is resolved: IEEE DataPort permits research use with citation, and its Terms apply CC BY 3.0 US by default. D1's **access provenance** is not resolved: the dataset is a subscription-gated Standard Dataset, credentials are non-transferable, and no subscription receipt or author permission exists in the project.

**Therefore two scope variants are defined:**

| | Scope A (preferred) | Scope B (fallback) |
|---|---|---|
| Datasets | D1 + D2, kept separate | D2 only |
| Malayalam arm | Yes (1,992 records; 225 spam) | No |
| English arm | Yes (5,971) | Yes (5,971) |
| Title | "…in Malayalam-Script and English Text" | "…in English SMS" |
| Condition | D1 access proof required | D1 dropped |
| Manglish | Out of scope | Out of scope |
| Pooling | Prohibited | Not applicable |

No third scope is permitted. D2 contains **zero Indic-script records**; this is a hard limitation in both variants.

---

## 13. Decision record

| Decision | Value | Status |
|---|---|---|
| Project title | *Classical and Multilingual Transformer Models for SMS Spam and Smishing Detection in Malayalam-Script and English Text* | **Awaiting approval** |
| Primary Malayalam task | D1 Ham/Spam, Malayalam subset (1,992) | Proposed |
| Primary English task | D2 Ham/Spam/Smishing (5,971) | Proposed |
| Manglish | Removed from scope | Decided by evidence |
| Malayalam phishing | Removed from scope | Decided by evidence |
| Dataset combination | NO-GO (cross-dataset probe only) | Decided by evidence |
| D1 `Spa,` record | Excluded, not relabelled | Decided |
| D1 empty messages (2) | Excluded | Decided |
| D2 label case | Normalised for analysis, file unchanged | Decided |
| D1 availability | **Blocked pending access proof**; Scope B if unavailable | **Open** |

**Approval required before any preprocessing or training begins.**
