# Literature Verification Register

**Date:** 8 November 2026.  
**Status definitions:** **FULL** = full text independently examined; **ABSTRACT** = abstract and metadata examined, full text unavailable; **METADATA** = bibliographic record only; **EXCLUDED** = not citable.

No numerical result is attributed to an ABSTRACT- or METADATA-level record unless it is explicitly described as an author-reported abstract value.

| ID | Paper | Access | What was verified | Missing evidence | Next action |
|---|---|---|---|---|---|
| P01 | Almeida, Hidalgo & Yamakami (2011), *Contributions to the Study of SMS Spam Filtering*, DocEng, pp. 259–262, DOI 10.1145/2034691.2034742 | **FULL** | 5,574 messages (4,827/747); linear SVM tok1 97.64% accuracy, MCC 0.893, Spam caught 83.10%, Ham blocked 0.18%; token-count study, not TF-IDF validation | Exact table-level hyperparameters beyond the reported best configuration | Use for English baseline and source-confound point only |
| P02 | Mishra & Soni (2020), *Smishing Detector*, FGCS 108:803–815, DOI 10.1016/j.future.2020.03.021 | **ABSTRACT** | Four-module architecture: content, URL, source code, APK; smishing boundary includes behaviour beyond text | Dataset, sample size, numeric performance, splits | Do not quote numbers; obtain full text if a direct comparison is needed |
| P03 | Xu, Qadir & Sadiq (2025), *Malicious SMS Detection Using Ensemble Learning and SMOTE*, Computers & Security 154:104443, DOI 10.1016/j.cose.2025.104443 | **METADATA** | Bibliographic record and topic | Final publisher methods, dataset, split, exact 99.58% status | Do not use the preprint 99.58% figure in the paper; obtain final PDF |
| P04 | Hassan, Mohd Sani, Abdullah & Mustapha (2026), *Transformer Attention-Driven Concept Extraction*, AI&A, DOI 10.47852/bonviewAIA62028760 | **FULL** | UCI SMS Spam Collection with Spam relabelled “smish”; BERT+FC reported 99.32% accuracy / 98.71% F1; label conflation confirmed | None material for the cited claim | Cite only as cautionary label-conflation example |
| P05 | Alhuzali et al. (2026), *PhishNet*, CMC 86(1):1–19, DOI 10.32604/cmc.2025.069491 | **FULL** | English-only three-class dataset; Dataset1 5,971; Dataset2 2,997 with synthetic Faker spam; strong in-dataset scores; authors acknowledge Spam/Smishing confusion and few sources | Exact reproducible per-class table extraction for a numeric comparison | Use for label-boundary and English-only limitation, not as a baseline |
| P06 | Sanjay, Krishna, Paramesh & Kiran Kumar (2026), *LLM-Based Multilingual Phishing Detection*, IC-AIDA, p. 168, DOI 10.1109/IC-AIDA68291.2026.11564455 | **ABSTRACT** | Six languages listed; **Malayalam absent**; XLM-R/continual-learning framing | Dataset and publisher-confirmed F1/ROC-AUC | Do not use the secondary-source F1 0.975 / ROC-AUC 0.997; cite only language exclusion |
| P07 | Filali et al. (2026), *Cross-Lingual SMS Spam Detection Using GAN-Based Augmentation*, Scientific Reports 16:7128, DOI 10.1038/s41598-026-37769-4 | **FULL** | UCI 5,572; multilingual extension is machine-translated French/German/Hindi from English; method unspecified; reported 97.61% monolingual F1 and 94.44% multilingual F1; translation-artifact limitation acknowledged | Cross-split duplicate control for translated copies | Use as an example of translated-data limits; no Malayalam evidence |
| P08 | Amaral Cejas, Guo & Tang (2026), *Large-Scale Multilingual SMS Fraud Detection*, NLPAICS, pp. 64–73 | **FULL** | DS4 ≈86K: English ≈36K, French ≈13K, German ≈11K, Italian ≈5K, Hindi ≈2K, Other ≈19K (Arabic/Chinese/Spanish examples); four compact multilingual embedding models; best overall F1 80.23%, SPAM 62.96%, SMISHING 83.66%; no per-language results; Malayalam not confirmed | Per-language metrics; public data | Use for scale and per-language limitation; never as Malayalam evidence |
| P09 | Phap (2026), *Edge-AI Enabled Smishing and Suspicious SMS Detection*, J. Information and Telecommunication, DOI 10.1080/24751839.2026.2713250 | **ABSTRACT** | Cost-sensitive BiGRU/masked-pooling architecture; threshold-calibration argument | Dataset, language, exact metrics | Cite architecture/recall-cost point only; no numbers |
| P10 | Unnamed “systematic ML pipeline” (2026), DOI 10.1016/j.jer.2026.05.020 | **EXCLUDED** | No confirmable author list, volume or pages | Complete bibliographic record | Do not cite |
| P11 | Birthriya, Ahlawat & Jain (2026), *ML-Based Smishing Detection Using Fuzzy Logic and TF-IDF*, Franklin Open 14:100506, DOI 10.1016/j.fraope.2026.100506 | **METADATA** | Title, authors, venue, DOI | Dataset, language, methods, results | Do not cite for numbers; optional background only |
| P12 | Chakravarthi et al. (2022), *DravidianCodeMix*, LRE 56(3):765–806, DOI 10.1007/s10579-022-09583-7 | **ABSTRACT** | >60,000 YouTube comments; Tamil/Kannada/Malayalam–English; sentiment and offensive labels; public release | Exact per-class baseline table | Cite only for code-mixing/sentiment context; never as threat corpus |
| P13 | Khanuja et al. (2021), *MuRIL*, arXiv:2103.10730 | **FULL** | 17 Indian languages; native and transliterated data; translated/transliterated pretraining pairs; XTREME evaluation; no SMS spam claim | None material | Cite model design only; not as SMS spam validation |
| P14 | Conneau et al. (2020), *XLM-R*, ACL, pp. 8440–8451, DOI 10.18653/v1/2020.acl-main.747 | **METADATA** | Bibliographic record and 100-language framing | Exact result table | Background only; do not quote fine-grained numbers |
| P15 | Devlin et al. (2019), *BERT*, NAACL-HLT, pp. 4171–4186, DOI 10.18653/v1/N19-1423 | **METADATA** | Bibliographic record and pretraining/fine-tuning framing | Exact benchmark table | Background only |
| B01 | Mahmood & Hameed (2023), *A Smishing Detection Method…*, Iraqi J. Science 64(10), DOI 10.24996/ijs.2023.64.10.41 | **FULL** | English; UCI plus 120 Pinterest smishing images; 5,692 final; UTF-IDF + Chi-square; SVM/RF/AdaBoost/XGBoost; 3-fold CV; 98.5% accuracy, 96.9% precision, 93.1% detection, 95.05% F1; URL inspection | Dataset release; exact page-range discrepancy (publisher 6276–6291 vs PDF header 5376–5391) | Use for task distinction, not direct comparison |
| E01 | Elangovan, Abirami & Thirumalai (2025), *FS_SHAP*, IEEE MultiMedia 32(1):92–103, DOI 10.1109/MMUL.2024.3508765 | **ABSTRACT** | Exact title and authors; SHAP-based global feature selection; handcrafted features; Random Forest; three Dravidian SMS datasets; Tamil/Kannada/Telugu/Malayalam; D1 DOI in references | Full text: exact D1 subset, splits, per-dataset counts, numerical results, duplicate/row-order treatment | Obtain full text; until then no numeric or negative claim about its methods |
| T01 | Timko & Rahman (2024), *Smishing Dataset I*, CODASPY, pp. 289–294 | **METADATA** | 1,062 community-sourced smishing samples; dataset paper | DOI and full methods | Use only as alternative-source context; not in the frozen experiment |
| T02 | Thara & Poornachandran (2022), *Social Media Text Analytics of Malayalam–English Code-Mixed*, J. Big Data 9:45, DOI 10.1186/s40537-022-00594-3 | **ABSTRACT** | Malayalam–English code-mixed social media; deep learning; Romanised Malayalam handling | Exact corpus size, labels, metrics | Cite for Manglish/code-mix context only |
| S01 | Elangovan & Abirami (2025), *SMSDHL*, TechRxiv, DOI 10.36227/techrxiv.173603655.53756505 | **METADATA** | Preprint record; multilingual SMS dataset description | Full text and version-specific counts | Do not use counts; cite only as related dataset lineage if needed |
| E02 | Ramanujam, Prakash & Abirami (2023), *Evaluation of Hand-Crafted Features…*, Springer, pp. 3–15, DOI 10.1007/978-981-99-6755-1_1 | **METADATA** | Title, authors, venue, pages, DOI | Full text | Cite as related Dravidian feature-engineering work only |
| E03 | Thirumalai et al. (2024), *XAI-Based Feature Selection…*, ICITIIT, p. 215, DOI 10.1109/ICITIIT61487.2024.10580065 | **METADATA** | Title, authors, venue, page, DOI | Full text | Cite as related XAI work only |
| E04 | Ramanujam & Abirami (2025), *NCMDFE*, Int. J. Information Technology, DOI 10.1007/s41870-025-02635-5 | **METADATA** | Bibliographic record | Full text | Cite as related lineage only |
| E05 | Ramanujam et al. (2026), *Efficient Extraction…*, Evolving Systems, DOI 10.1007/s12530-025-09761-2 | **METADATA** | Bibliographic record | Full text | Cite as related lineage only |

## Verification summary

- **Full text independently examined:** P01, P04, P05, P07, P08, P13, B01 (7).
- **Abstract + metadata:** P02, P06, P09, P12, E01, T02 (6).
- **Metadata only:** P03, P11, P14, P15, T01, S01, E02–E05 (10).
- **Excluded:** P10 (1).

The seven full-text records are sufficient to support the paper’s core comparisons and the FSSHAP limitation. The remaining records must not be used to supply numerical claims.

## Specific unresolved verification questions

1. **FSSHAP:** exact dataset version, Malayalam subset size, split protocol, classifier results, duplicate handling and row-order treatment.
2. **P03:** whether the final *Computers & Security* article reports 99.58% and how SMOTE was applied relative to the split.
3. **P06:** publisher-confirmed dataset and metrics; the current F1/ROC-AUC figures are secondary-source only.
4. **P09/P11:** dataset, language and exact results.
5. **T01:** DOI and whether the 1,062 samples are unique.
6. **S01:** version-specific counts and relationship to the D1 workbook.
