# Literature Audit Status

**Date:** 8 November 2026.  
**Authoritative detail:** `Admin/LITERATURE_VERIFICATION_REGISTER.md`.  
**Machine-readable matrix:** `Admin/FINAL_LITERATURE_COMPARISON_MATRIX.xlsx`.

## 1. Verification levels actually achieved

| Source | Access level | What may be cited |
|---|---|---|
| Almeida, Hidalgo & Yamakami (2011), DocEng, DOI 10.1145/2034691.2034742 | **Full text** | 5,574 messages (4,827/747); linear SVM tok1 97.64% accuracy, MCC 0.893, Spam caught 83.10%, Ham blocked 0.18%; token-count study, not a TF-IDF validation |
| Mahmood & Hameed (2023), Iraqi J. Science, DOI 10.24996/ijs.2023.64.10.41 | **Full text** | 5,692 final; UCI + Pinterest-derived smishing; 3-fold; 98.5/96.9/93.1/95.05; English-only; URL inspection |
| Khanuja et al. (2021), MuRIL, arXiv 2103.10730 | **Full text** | 17 Indian languages; native + transliterated pretraining; XTREME evaluation; no SMS spam claim |
| Alhuzali et al. (2026), PhishNet, DOI 10.32604/cmc.2025.069491 | **Full text** | English-only three-class; synthetic spam in Dataset2; authors acknowledge Spam/Smishing confusion |
| Filali et al. (2026), Scientific Reports 16:7128 | **Full text** | UCI + machine-translated French/German/Hindi; 97.61% monolingual F1 / 94.44% multilingual F1; translation artifacts acknowledged |
| Amaral Cejas, Guo & Tang (2026), NLPAICS | **Full text** | ~86K proprietary multilingual SMS; English/French/German/Italian/Hindi/Other; no per-language results; Malayalam not confirmed |
| Hassan et al. (2026), AI&A, DOI 10.47852/bonviewAIA62028760 | **Full text** | UCI Spam relabelled “smish”; label conflation; BERT-based high in-dataset scores |
| FSSHAP / Elangovan et al. (2025), IEEE MultiMedia 32(1):92–103, DOI 10.1109/MMUL.2024.3508765 | **Abstract + metadata only; full text paywalled** | SHAP + handcrafted features + Random Forest framing; three Dravidian SMS datasets; D1 DOI in references. **No numeric result may be cited. Exact D1 subset unconfirmed.** |
| Elangovan & Abirami (2023), D1 dataset record | Official record | Provenance, languages, Ham/Spam definition, subscription access |
| Mishra & Soni (2022), D2 dataset record | Official record + CC BY 4.0 | 5,971 = 4,844/489/638; UCI relation |
| P02, P06, P09, P12, T02 | Abstract + metadata | Only abstract-level claims; no unverified numbers |
| P03, P11, P14, P15, T01, S01, E02–E05 | Metadata only | Bibliographic/context use only; no methods or numeric claims |
| P10 | Excluded | No confirmable record; do not cite |

The old statement that “only B01 was read in full” is false. Seven records were full-text examined, but several secondary records remain incomplete. The register, not this summary, controls individual citations.

## 2. What the literature supports

- English SMS spam is mature; linear SVM on sparse features is a strong baseline [1].
- English smishing is a distinct task; URL/domain behaviour matters, and text-only detection is incomplete [2], [3].
- Dravidian SMS **spam** is an active line, and D1 has been used before [4]–[9].
- FSSHAP is the closest Dravidian SMS spam paper, but its full text is unavailable; exact overlap and results cannot be asserted [5].
- Malayalam/Manglish NLP exists mainly for sentiment and offensive language, not spam or phishing [13], [14].
- MuRIL is a multilingual encoder, not an SMS spam model [10].
- Large multilingual SMS work can omit per-language results; multilingual scale is not Malayalam transfer evidence [17].
- Translated and synthetic data are common, but cannot substitute for natural Malayalam SMS [15], [16].
- No verified peer-reviewed Malayalam or Manglish **smishing** study was found. This is absence of evidence, not proof of priority.

## 3. Claims that must not appear

- “First Malayalam/Dravidian SMS spam detector.”
- “First use of D1.”
- “First transformer evaluation of D1” unless phrased as “we found no verified published transformer evaluation.”
- “FSSHAP reports X%” or “FSSHAP ignored duplicate leakage/row order.”
- “D1 is a phishing/smishing corpus.”
- “D2 validates Malayalam performance” or “D2 is independent external validation.”
- “Manglish is covered.”
- “State of the art” or a direct numeric comparison with B01/FSSHAP on non-comparable data.
- Any P06 F1/ROC-AUC value from a secondary portal.
- Any P03 99.58% value from a preprint as if it were the final article.

## 4. Strongest defensible contribution

A reproducible, duplicate-group-controlled **within-corpus** comparison of character n-gram models and MuRIL on Malayalam-containing SMS, plus a quantified **pooled leave-one-row-block-out** stress test showing the random-split score is not portable across the corpus’s own row ordering, and a bounded English three-class secondary analysis. This is an evaluation/validity contribution, not a new detector or dataset.

## 5. Remaining literature work

1. Obtain FSSHAP full text through institutional access or author contact; otherwise retain abstract-only status and no numeric claim.
2. Obtain P03, P06, P09 and P11 full texts before citing methods or results.
3. Keep P10 excluded.
4. Update the final bibliography from `LITERATURE_VERIFICATION_REGISTER.md`; every citation must resolve and every reference must be cited.
5. Do not use the LinkedIn “>90%” FSSHAP claim.
