# Final Literature Review

**Project:** Duplicate-controlled evaluation of character n-gram and MuRIL models for Malayalam-script SMS spam, with a separate English spam–smishing study.  
**Date:** 8 November 2026.  
**Rule:** citations marked abstract-only support only abstract-level statements. No number is attributed to an unread full text.

---

## 1. Introduction

SMS remains a short, informal and adversarial channel. Spam filtering is a mature text-classification problem in English, but smishing — fraudulent SMS that attempts to induce a reply, click or disclosure — is a distinct security task with different labels, features and error costs. The two are frequently conflated in datasets and papers. This review separates them, then examines Dravidian-language SMS spam, Malayalam low-resource NLP, multilingual transformers, and the dataset/evaluation problems that motivate this project.

The central argument is that the literature establishes strong **within-corpus** baselines but does not establish that those scores transfer across collection sources in a small, row-ordered low-resource corpus. That is the gap this project addresses.

## 2. SMS spam classification

The UCI SMS Spam Collection, introduced by Almeida, Hidalgo and Yamakami [1], remains the canonical English benchmark: 5,574 messages (4,827 Ham / 747 Spam). The authors evaluated a large set of classical classifiers and reported a linear SVM with token unigrams at 97.64% accuracy, MCC 0.893, 83.10% of spam caught and 0.18% of ham blocked [1]. Two cautions follow. First, the paper is a token-count study; it does not validate TF-IDF, and it must not be cited as doing so. Second, its Ham and Spam portions were assembled from different sources, so source is confounded with label even in the foundational benchmark.

Later English work has added ensemble learning, synthetic minority oversampling, feature selection and deep architectures. Xu, Qadir and Sadiq [23] combine an SVM/RF ensemble with SMOTE, but the final publisher record could not be verified in this audit; its widely quoted 99.58% figure is therefore not used here. Filali et al. [16] combine BERT embeddings, BiLSTM and GAN-based embedding augmentation, reporting 97.61% F1 on the monolingual UCI data and 94.44% F1 on a “multilingual” extension. The extension is machine-translated French/German/Hindi from English, with the translation method unspecified. It therefore demonstrates augmentation on translated text, not natural multilingual SMS. Amaral Cejas, Guo and Tang [17] move closer to operational multilingual SMS with a proprietary telecom corpus of about 86,000 messages and four compact embedding models; their best overall F1 is 80.23%, with SPAM F1 62.96% and SMISHING F1 83.66%. They explicitly do not analyse per-language performance, so the result cannot be used as evidence for Malayalam.

The English literature therefore supports two limited conclusions: linear models on sparse lexical features are strong short-text baselines, and reported high scores are sensitive to dataset construction and label definition. It does not supply a Malayalam baseline.

## 3. Smishing and the spam/smishing boundary

Smishing detection is usually defined by the social-engineering intent of the message, not merely by unsolicited content. Mishra and Soni [2] propose a multi-module detector combining SMS content analysis, URL filtering, source-code analysis and APK-download detection. The full text was not obtained in this audit, so only its architecture and task framing are used. The important lesson is architectural: a text-only classifier does not cover the URL, attachment or application-installation behaviour that defines much real smishing.

Mahmood and Hameed [3] combine SMS content with URL inspection through Google and VirusTotal. They report 98.5% accuracy, 96.9% precision, 93.1% detection and 95.05% F1 on a corpus built from UCI messages plus 120 Pinterest-derived smishing images, with 5,692 records in the final modelling set. Those numbers are not comparable with D1: the language is English, the labels are Ham/Smishing rather than Ham/Spam, the smishing examples are image-derived, and the feature set includes external URL reputation. A direct “our model beats/underperforms Mahmood” statement would be invalid.

PhishNet [15] is a recent English-only three-class system using BERT, RoBERTa, DistilBERT and LLMs. It reports strong in-dataset accuracy but also documents that all models struggle to separate Spam from Smishing and that the dataset has only a few sources. The authors acknowledge the spam/smishing confusion and the English-only limitation. Their work supports the three-class framing of D2, but it does not provide a Malayalam baseline. Cost-sensitive designs and operating-threshold calibration are a partial response to asymmetric error costs [21], while fuzzy-logic and handcrafted-feature pipelines offer another engineering route whose dataset and language coverage remain unverified here [22]. Neither supplies a validated Malayalam SMS result.

Two dataset papers sharpen the label problem. Timko and Rahman [19] release 1,062 community-sourced smishing messages; this is a smishing corpus, not a balanced Ham/Spam/Smishing benchmark. Hassan et al. [18] use the UCI SMS Spam Collection with the Spam label renamed “smish,” and report very high BERT-based scores. Renaming spam as smishing does not create phishing behaviour labels. P04 is therefore a cautionary example of label conflation, not evidence of smishing detection capability.

D2 in this project is the Mishra–Soni SMS Phishing Dataset [24], with 5,971 original records (4,844 Ham / 489 Spam / 638 Smishing), reduced to 5,895 after excluding 37 conflicting-label groups. The corpus is English/Latin and is not independent of D1: 773 normalised keys overlap. It is a secondary three-class experiment, not external validation.

## 4. Dravidian-language SMS spam

D1 is the Malayalam-containing subset of the IEEE DataPort corpus “Spam SMS in Dravidian Languages” [4]. The official record lists English, Tamil, Telugu, Kannada and Malayalam and defines binary Ham/Spam, with spam described as business, annoying or unnecessary messages. It does **not** provide phishing labels. The local Malayalam subset contains 1,992 records (1,767 Ham / 225 Spam), of which 1,489 contain Malayalam script only and 503 contain Malayalam plus Latin characters.

D1 is not a new resource. The Elangovan/Abirami line includes a 2023 study of hand-crafted features [6], a 2024 XAI feature-selection conference paper [7], the 2025 FSSHAP article [5], a 2025 NCMDFE study [8], a 2026 *Evolving Systems* paper [9], and the SMSDHL preprint [not separately cited here]. These works establish that Dravidian SMS spam has an active publication line. They also make “first Dravidian SMS spam study” and “first use of D1” indefensible.

FSSHAP is the closest paper. Its exact title is *FS_SHAP: Global Interpretable Feature Selection Using XAI for the Classification of Spam SMS in Dravidian Languages*, by Ramanujam Elangovan, Abirami A. M. and K. G. Thirumalai, *IEEE MultiMedia*, vol. 32, no. 1, pp. 92–103, 2025, DOI `10.1109/MMUL.2024.3508765` [5]. The abstract describes SHAP-based global selection over handcrafted features, a Random Forest classifier, three SMS datasets, and Tamil, Kannada, Telugu and Malayalam. Its reference list includes the D1 DOI. The full text is paywalled; the IEEE Computer Society and ACM records provide abstract and metadata only. Consequently:

- It is defensible to say FSSHAP is a Dravidian SMS spam study in the same dataset lineage and uses SHAP with Random Forest.
- It is **not** defensible to say it used this exact 1,992-row Malayalam subset, reported a particular accuracy, evaluated transformers, ignored duplicate leakage, or ignored row order. Those facts are not established by the abstract.
- The author’s LinkedIn claim of “>90%” accuracy is not a peer-reviewed result and is not cited.

Sanjay et al. [20] propose a multilingual phishing framework, but their listed languages are English, Hindi, Kannada, Tamil, Telugu and Bengali — **no Malayalam**. The paper therefore cannot support a Malayalam gap claim. Its reported F1 0.975 / ROC-AUC 0.997 is from a secondary source, not confirmed on the publisher page, and is not used.

The Dravidian literature therefore establishes a **dataset and feature-engineering lineage**, not a duplicate-controlled evaluation literature. That distinction is the opening for this project.

## 5. Malayalam and low-resource NLP

Malayalam NLP resources are concentrated in sentiment analysis, offensive-language identification and code-mixed social media. DravidianCodeMix [13] provides more than 60,000 YouTube comments across Tamil–English, Kannada–English and Malayalam–English, annotated for sentiment and offensive language. Thara and Poornachandran [14] study Malayalam–English code-mixed social media with deep learning and explicitly handle Romanised Malayalam. Both are relevant to tokenisation, script mixing and code-switching, but neither provides spam, smishing or cybersecurity labels.

This matters for two reasons. First, “Malayalam–English code-mixed” is not equivalent to “Manglish SMS.” Romanised Malayalam in YouTube comments differs from SMS spam campaigns in length, domain and orthography. Second, offensive language is not a cybersecurity threat category. A review that cites offensive-language datasets as evidence of threat-detection capability would be conceptually invalid.

The project therefore uses “Malayalam-containing” and “Malayalam-script-containing,” not “Malayalam language identified.” Unicode-script detection is not language identification. The 503 Malayalam+Latin records are a mixed-script condition, not a validated Manglish corpus. No Manglish performance is claimed.

## 6. Multilingual transformers and MuRIL

BERT [12] established bidirectional masked-language pretraining and fine-tuning for English. XLM-R [11] extended multilingual pretraining to 100 languages and showed cross-lingual transfer on XNLI, MLQA and NER. MuRIL [10] was designed for 17 Indian languages, with native-script and transliterated data and translated/transliterated pretraining pairs, and was evaluated on XTREME tasks. It is a plausible encoder for Malayalam script and transliteration.

But MuRIL’s foundation paper does **not** evaluate SMS spam, smishing, class imbalance, row-order leakage or deployment false-positive costs. Citing it as proof that MuRIL is effective for SMS spam is a category error. The present MuRIL experiment is a new fine-tuning experiment on D1; it is not a reproduction of Khanuja et al. and it does not validate their model on this task.

The transformer literature also does not resolve the small-data problem. MuRIL has far more parameters than a character n-gram linear model, while D1 has only 225 Spam records, 34 in the test set and 12 in the critical block-training fold. A high-capacity model can fit campaign-specific cues or collapse to the majority class. That is an empirical question for this corpus, not an assumption imported from multilingual benchmarks.

## 7. Dataset and evaluation problems

Four evaluation problems recur across the literature and directly shape this project.

**Source and label confounding.** The UCI corpus combines Ham and Spam from different collection routes [1]. D1 is more extreme: 213 of 225 Malayalam-subset Spam records lie in one consecutive workbook block, 6001–7000, while block 5001–6000 contains no Spam. A random split shares that block between training and test. The result is a within-batch estimate, not a source-held-out estimate. The present row-block stress test is an attempt to quantify this, not to identify the true source.

**Translated and synthetic data.** Filali et al. [16] use machine-translated “multilingual” data and acknowledge translation artifacts. PhishNet [15] uses synthetic Faker spam in its second dataset. Neither can substitute for naturally occurring Malayalam SMS. This project therefore does not augment D1 with synthetic or translated messages.

**Label conflation.** Hassan et al. [18] rename UCI Spam as “smish.” PhishNet [15] documents that Spam and Smishing are hard to separate. D2 preserves three labels and reports the confusion rather than merging classes. The weak D2 Spam/Smishing boundary is a finding, not a nuisance to hide.

**Duplicate and near-duplicate leakage.** SMS corpora contain repeated templates and forwarded messages. If duplicates cross splits, test scores are inflated. The present project groups exact, normalised and conservative fuzzy duplicates before splitting. D1 has 1,824 groups and 168 duplicate excess; D2 has 5,700 groups before conflict exclusion, 37 conflicting groups / 76 records excluded, and 5,663 experimental groups. Every frozen test group is a singleton, so the group bootstrap is numerically a message bootstrap. This is a methodological strength, but it does not solve source confounding.

Amaral Cejas et al. [17] is a useful counter-example: it has a large proprietary multilingual corpus, tenfold re-splitting and per-class results, but no per-language analysis and no Malayalam confirmation. Scale alone does not establish transfer to a new language or source.

## 8. Critical comparison and research gap

| Dimension | English spam [1] | Smishing [3], [15] | Dravidian spam [4]–[9] | This project |
|---|---|---|---|---|
| Language | English | English | Tamil, Telugu, Kannada, Malayalam (+English) | Malayalam-script subset; separate English |
| Labels | Ham/Spam | Ham/Smishing or Ham/Spam/Smishing | Ham/Spam | Ham/Spam (D1); Ham/Spam/Smishing (D2) |
| Data | UCI 5,574 | UCI-derived + Pinterest / multi-source | D1 lineage | Frozen D1 subset; D2 |
| Models | Classical, linear SVM | Transformers, LLMs, URL features | Handcrafted features, RF, SHAP | Char n-gram LR/SVM; MuRIL 3 seeds |
| Evaluation | Single split | In-dataset / few sources | Abstract does not specify | Duplicate-group split + row-block stress |
| Main limitation | Source confound; English | English; label confusion; few sources | Full text unavailable; no verified duplicate/row-order analysis | No source labels; no external Malayalam test |

The honest gap is **not** “no one has studied Dravidian SMS spam.” The Elangovan/Abirami series disproves that. It is also **not** “no one has used D1.” The dataset record and FSSHAP citation disprove that. The defensible gap is:

> There is no verified, reproducible evaluation of this Malayalam-containing corpus that (a) controls duplicate groups, (b) compares strong character n-gram baselines with a multilingual transformer under the same frozen split, (c) quantifies sensitivity to holding out a complete workbook row block, and (d) reports exact uncertainty for the resulting perfect-precision/zero-false-positive observation.

That is an **evaluation and validity** contribution. It is narrower than a new detector, but it is testable and supported by the artifacts. FSSHAP’s abstract does not report these analyses; the full text is needed before making any stronger claim about what it omitted.

## 9. Justification for the methodology

Character `char_wb` 2–4 TF-IDF is appropriate for short, noisy, morphologically rich text and script mixing: it does not require a Malayalam word segmenter, and it captures suffixes and transliterated fragments. Logistic Regression and a linear SVM provide strong, interpretable, deterministic baselines. MuRIL provides a contextual multilingual comparison with the same frozen split and three seeds.

The duplicate-group split prevents template leakage. The shared 2,000-replicate bootstrap preserves pairing and gives percentile intervals for differences. Exact Clopper–Pearson intervals are used where observed precision is 1.0, because a Wald or normal interval is degenerate at the boundary. The row-block stress test is deliberately called **pooled leave-one-row-block-out**, not source-held-out: the blocks are consecutive workbook rows, not verified collection sources. The pooled calculation avoids averaging unstable per-fold Macro-F1 when a fold has no Spam.

D2 is kept separate because it is English/Latin, has different labels and overlaps D1. It is analysed with the same duplicate-group protocol to test whether the three classes are separable, not to validate the Malayalam result.

## 10. Defensible contribution statement

> This study provides a reproducible, duplicate-controlled evaluation of character n-gram and MuRIL models on a Malayalam-containing SMS corpus, and shows that high grouped-random-split performance falls sharply under a pooled leave-one-row-block-out stress test. It further shows that MuRIL does not provide a statistically reliable advantage over a linear SVM on this corpus, and that a separate English three-class corpus exhibits a weak Spam/Smishing boundary. The contribution is an evaluation of measured performance and its fragility, not a new detector, dataset, or claim of Malayalam smishing capability.

This statement is supported by the frozen artifacts. It does not claim priority, state of the art, source generalisation, or deployment safety.

---

## References

[1] T. A. Almeida, J. M. G. Hidalgo, and A. Yamakami, “Contributions to the study of SMS spam filtering: New collection and results,” in *Proc. 11th ACM Symp. Document Engineering (DocEng)*, Mountain View, CA, USA, Sep. 2011, pp. 259–262, doi: 10.1145/2034691.2034742.

[2] S. Mishra and D. Soni, “Smishing detector: A security model to detect smishing through SMS content analysis and URL behavior analysis,” *Future Generation Computer Systems*, vol. 108, pp. 803–815, 2020, doi: 10.1016/j.future.2020.03.021.

[3] A. R. Mahmood and S. M. Hameed, “A smishing detection method based on SMS contents analysis and URL inspection using Google engine and VirusTotal,” *Iraqi Journal of Science*, vol. 64, no. 10, pp. 6276–6291, 2023, doi: 10.24996/ijs.2023.64.10.41.

[4] R. Elangovan and A. M. Abirami, “Spam SMS in Dravidian Languages,” IEEE DataPort, Jun. 2023, doi: 10.21227/dcym-pd69.

[5] R. Elangovan, A. M. Abirami, and K. G. Thirumalai, “FS_SHAP: Global interpretable feature selection using XAI for the classification of spam SMS in Dravidian languages,” *IEEE MultiMedia*, vol. 32, no. 1, pp. 92–103, 2025, doi: 10.1109/MMUL.2024.3508765.

[6] E. Ramanujam, K. S. Prakash, and A. M. Abirami, “Evaluation of hand-crafted features for the classification of spam SMS in Dravidian languages,” in *Proc. Int. Conf. Data Science and Network Engineering*, Singapore, 2023, pp. 3–15, doi: 10.1007/978-981-99-6755-1_1.

[7] K. G. Thirumalai, K. S. Prakash, A. M. Abirami, E. Ramanujam, and S. Sumitra, “XAI-based feature selection for SMS spam classification in Dravidian languages,” in *Proc. 5th Int. Conf. Innovative Trends in Information Technology (ICITIIT)*, Kottayam, India, Mar. 2024, p. 215, doi: 10.1109/ICITIIT61487.2024.10580065.

[8] E. Ramanujam and A. M. Abirami, “NCMDFE: Performance evaluation of non-contextual meta-data feature extraction for spam SMS classification in Indian languages,” *International Journal of Information Technology*, 2025, doi: 10.1007/s41870-025-02635-5.

[9] E. Ramanujam, A. M. Abirami, K. Sakthiprakash, and S. Sumitra, “Efficient extraction and evaluation of hand-crafted meta-data features for Dravidian spam SMS classification,” *Evolving Systems*, 2026, doi: 10.1007/s12530-025-09761-2.

[10] S. Khanuja et al., “MuRIL: Multilingual representations for Indian languages,” arXiv:2103.10730, 2021, doi: 10.48550/arXiv.2103.10730.

[11] A. Conneau et al., “Unsupervised cross-lingual representation learning at scale,” in *Proc. 58th Annu. Meeting Assoc. Comput. Linguistics (ACL)*, Online, Jul. 2020, pp. 8440–8451, doi: 10.18653/v1/2020.acl-main.747.

[12] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training of deep bidirectional transformers for language understanding,” in *Proc. NAACL-HLT*, Minneapolis, MN, USA, Jun. 2019, vol. 1, pp. 4171–4186, doi: 10.18653/v1/N19-1423.

[13] B. R. Chakravarthi, R. Priyadharshini, V. Muralidaran, N. Jose, S. Suryawanshi, E. Sherly, and J. P. McCrae, “DravidianCodeMix: Sentiment analysis and offensive language identification dataset for Dravidian languages in code-mixed text,” *Language Resources and Evaluation*, vol. 56, no. 3, pp. 765–806, 2022, doi: 10.1007/s10579-022-09583-7.

[14] S. Thara and P. Poornachandran, “Social media text analytics of Malayalam–English code-mixed using deep learning,” *Journal of Big Data*, vol. 9, Art. no. 45, 2022, doi: 10.1186/s40537-022-00594-3.

[15] A. Alhuzali, Q. Al-Qahtani, A. Niyazi, L. Alshehri, and F. Alharbi, “PhishNet: A real-time, scalable ensemble framework for smishing attack detection using transformers and LLMs,” *Computers, Materials & Continua*, vol. 86, no. 1, pp. 1–19, 2026, doi: 10.32604/cmc.2025.069491.

[16] A. Filali et al., “Cross-lingual SMS spam detection using GAN-based augmentation for imbalanced datasets,” *Scientific Reports*, vol. 16, Art. no. 7128, 2026, doi: 10.1038/s41598-026-37769-4.

[17] O. Amaral Cejas, Y. Guo, and Q. Tang, “Large-scale multilingual SMS fraud detection for telecom networks,” in *Proc. 2nd Int. Conf. Natural Language Processing and AI for Cyber Security (NLPAICS)*, Alicante, Spain, Jun. 2026, pp. 64–73. [Online]. Available: https://aclanthology.org/2026.nlpaics-1.7/

[18] Z. L. Hassan, N. F. Mohd Sani, M. D. H. Abdullah, and N. Mustapha, “Transformer attention-driven concept extraction for efficient smishing detection,” *Artificial Intelligence and Applications*, pp. 1–9, 2026, doi: 10.47852/bonviewAIA62028760.

[19] D. Timko and M. L. Rahman, “Smishing dataset I: Phishing SMS dataset from Smishtank.com,” in *Proc. 14th ACM Conf. Data and Application Security and Privacy (CODASPY)*, 2024, pp. 289–294.

[20] S. Sanjay, N. Krishna, G. Paramesh, and K. V. Kiran Kumar, “An LLM-based multilingual phishing detection framework for regional languages,” in *Proc. 2026 Int. Conf. AI-Driven Innovations and Applications (IC-AIDA)*, Bangalore, India, Apr. 2026, p. 168, doi: 10.1109/IC-AIDA68291.2026.11564455.

[21] H. C. Phap, “Edge-AI enabled smishing and suspicious SMS detection: A cost-sensitive and lightweight deep learning architecture,” *Journal of Information and Telecommunication*, pp. 1–15, 2026, doi: 10.1080/24751839.2026.2713250.

[22] S. K. Birthriya, P. Ahlawat, and A. K. Jain, “Machine learning-based smishing detection using fuzzy logic and TF-IDF feature engineering,” *Franklin Open*, vol. 14, Art. no. 100506, 2026, doi: 10.1016/j.fraope.2026.100506.

[23] H. Xu, A. Qadir, and S. Sadiq, “Malicious SMS detection using ensemble learning and SMOTE to improve mobile cybersecurity,” *Computers & Security*, vol. 154, Art. no. 104443, 2025, doi: 10.1016/j.cose.2025.104443.

[24] S. Mishra and D. Soni, “SMS phishing dataset for machine learning and pattern recognition,” Mendeley Data, V1, 2022, doi: 10.17632/f45bkkt8pr.1.
