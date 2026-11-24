#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the final literature comparison matrix (XLSX + CSV).

Values are restricted to what was verified in the audit. Abstract-only and
metadata-only records carry that status and no unverified numbers.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

BASE = Path(__file__).resolve().parents[1]
XLSX = BASE / "Admin" / "FINAL_LITERATURE_COMPARISON_MATRIX.xlsx"
CSV = BASE / "Literature Review" / "FINAL_LITERATURE_COMPARISON_MATRIX.csv"

COLS = ["ID", "Paper", "Authors", "Year", "Venue", "DOI / official link",
        "Dataset", "Language(s)", "Task / labels", "Models / method",
        "Evaluation", "Verified results", "Limitations", "Relevance",
        "Verification", "Source note"]

ROWS = [
 ["P01", "Contributions to the Study of SMS Spam Filtering: New Collection and Results",
  "Tiago A. Almeida; Jose Maria Gomez Hidalgo; Akebo Yamakami", 2011,
  "Proc. 11th ACM Symp. Document Engineering (DocEng), pp. 259-262",
  "10.1145/2034691.2034742",
  "UCI SMS Spam Collection v.1 (introduced); 5,574 messages", "English (Latin script)",
  "Ham / Spam", "14 classical classifiers incl. linear SVM, naive Bayes variants, kNN, C4.5, PART",
  "Classifier comparison on the SMS Spam Collection; exact resampling protocol not re-derived in this audit",
  "Linear SVM tok1: 97.64% accuracy, MCC 0.893, Spam caught 83.10%, Ham blocked 0.18%",
  "English only; no phishing labels; Ham and Spam assembled from different sources; token-count study, not a TF-IDF validation",
  "Foundational English baseline and source-confound precedent; not a direct Malayalam baseline",
  "FULL TEXT", "ACM PDF; values confirmed"],

 ["P02", "Smishing Detector: A Security Model to Detect Smishing through SMS Content Analysis and URL Behavior Analysis",
  "Sandhya Mishra; Devpriya Soni", 2020,
  "Future Generation Computer Systems, vol. 108, pp. 803-815",
  "10.1016/j.future.2020.03.021",
  "SMS datasets not verified", "Not verified",
  "Smishing vs legitimate", "Content analysis + URL filter + source-code analyzer + APK download detector",
  "Multi-module system evaluation; details not retrieved",
  "No numerical result extracted",
  "URL/APK behaviour beyond text; dataset and metrics not verified",
  "Defines the smishing boundary and why a text-only classifier is incomplete",
  "ABSTRACT", "Publisher abstract/metadata only"],

 ["P03", "Malicious SMS Detection Using Ensemble Learning and SMOTE to Improve Mobile Cybersecurity",
  "Hongsheng Xu; Akeel Qadir; Saima Sadiq", 2025,
  "Computers & Security, vol. 154, Art. no. 104443",
  "10.1016/j.cose.2025.104443",
  "Imbalanced SMS dataset; final dataset not verified", "Not verified",
  "Malicious/smishing vs legitimate", "SVM + Random Forest ensemble; LR, SVM, RF, ETC, NB, SGD; TF/TF-IDF; SMOTE",
  "Final publisher protocol not verified",
  "Do not cite 99.58%: final article not verified; preprint-level value only",
  "SMOTE timing relative to split unverified; English evidence unverified",
  "Classical imbalanced-pipeline context only",
  "METADATA", "Bibliographic record only"],

 ["P04", "Transformer Attention-Driven Concept Extraction for Efficient Smishing Detection",
  "Zahriya Lawal Hassan; Nor Fazlida Mohd Sani; Muhammad Daniel Hafiz Abdullah; Norwati Mustapha", 2026,
  "Artificial Intelligence and Applications, pp. 1-9",
  "10.47852/bonviewAIA62028760",
  "UCI SMS Spam Collection with Spam relabelled 'smish'; ~5,572 messages", "English",
  "Ham / 'smish' (relabelled spam)", "Regex concept signatures; BERT [CLS] embeddings; FC classifier; LR/RF/SVM baselines",
  "Single stratified train/test evaluation reported",
  "BERT+FC: 99.32% accuracy, 98.01% precision, 99.42% recall, 98.71% F1, 99.95% ROC-AUC",
  "Single split; label relabelling; behavioural-only variant exceeds full model; English only",
  "Cautionary label-conflation example; not a smishing corpus",
  "FULL TEXT", "Open publisher PDF"],

 ["P05", "PhishNet: A Real-Time, Scalable Ensemble Framework for Smishing Attack Detection Using Transformers and LLMs",
  "Abeer Alhuzali; Qamar Al-Qahtani; Asmaa Niyazi; Lama Alshehri; Fatemah Alharbi", 2026,
  "Computers, Materials & Continua, vol. 86, no. 1, pp. 1-19",
  "10.32604/cmc.2025.069491",
  "Dataset1: 5,971 SMS; Dataset2: 2,997 (997 SmishTank + 1,000 UCI Ham + 1,000 synthetic Faker Spam)",
  "English only (stated)",
  "Ham / Spam / Smishing", "BERT, RoBERTa, DistilBERT; GPT-OSS 120B, LLaMA3.3 70B, Qwen3 32B; confidence-weighted voting; T5 augmentation",
  "In-dataset evaluation with cross-validation and held-out comparisons; exact split details vary by experiment",
  "Strong in-dataset accuracy; ensemble reported 98%/99%; all models struggled to separate Spam from Smishing",
  "Few sources; English only; Dataset2 spam synthetic; authors acknowledge spam/smishing confusion",
  "Three-class taxonomy and label-boundary caution; not a Malayalam baseline",
  "FULL TEXT", "Open publisher PDF"],

 ["P06", "An LLM-Based Multilingual Phishing Detection Framework for Regional Languages",
  "S. Sanjay; Nishant Krishna; G. Paramesh; K. V. Kiran Kumar", 2026,
  "Proc. 2026 Int. Conf. AI-Driven Innovations and Applications (IC-AIDA), Bangalore, p. 168",
  "10.1109/IC-AIDA68291.2026.11564455",
  "Not verified", "English, Hindi, Kannada, Tamil, Telugu, Bengali; NO Malayalam",
  "Phishing vs safe", "XLM-RoBERTa + feedback-driven continual learning",
  "Not verified",
  "Do not cite F1 0.975 / ROC-AUC 0.997: secondary-source values only",
  "Full text and dataset not verified; Malayalam excluded",
  "Evidence against a broad 'all Indian languages covered' claim; not Malayalam evidence",
  "ABSTRACT", "IEEE record/abstract only"],

 ["P07", "Cross-Lingual SMS Spam Detection Using GAN-Based Augmentation for Imbalanced Datasets",
  "Adnane Filali; Mohammad Shorfuzzaman; El Arbi Abdellaoui Alaoui; Mostafa Merras; Mohammed Es-Sabry; Achraf Berrajaa; Roobaea Alroobaea; Amr Yousef", 2026,
  "Scientific Reports, vol. 16, Art. no. 7128",
  "10.1038/s41598-026-37769-4",
  "UCI 5,572; multilingual extension machine-translated French/German/Hindi from English",
  "English; French, German, Hindi (machine-translated)",
  "Ham / Spam", "SVM, LR, KNN, DT, SGD, RF, LSTM, BiLSTM; BoW, TF-IDF, Word2Vec, GloVe, BERT; WGAN-GP, SMOTE, ADASYN",
  "Train/test evaluation with augmentation; cross-split duplicate control for translated copies not established",
  "Best BERT+BiLSTM+GAN: 97.61% F1 monolingual, 94.44% multilingual",
  "Machine-translated data; method unspecified; translation artifacts acknowledged; no Malayalam",
  "Shows why translated data cannot substitute for natural Malayalam SMS",
  "FULL TEXT", "Open access Scientific Reports PDF"],

 ["P08", "Large-Scale Multilingual SMS Fraud Detection For Telecom Networks",
  "Orlando Amaral Cejas; Yuejun Guo; Qiang Tang", 2026,
  "Proc. 2nd Int. Conf. NLP and AI for Cyber Security (NLPAICS), pp. 64-73",
  "https://aclanthology.org/2026.nlpaics-1.7/",
  "DS4 proprietary telecom corpus ~86K: English ~36K, French ~13K, German ~11K, Italian ~5K, Hindi ~2K, Other ~19K",
  "English, French, German, Italian, Hindi, Other (Arabic/Chinese/Spanish examples); Malayalam not confirmed",
  "Ham / Spam / Smishing", "Four compact multilingual embedding models (M1-M4), fine-tuned; tenfold experiments",
  "Tenfold re-splitting; per-class precision/recall/accuracy/F1",
  "Best M1: overall F1 80.23%; Ham 96.86%; Spam 62.96%; Smishing 83.66%",
  "Proprietary data; no per-language analysis; no confirmed Malayalam; static evaluation; no concept drift",
  "Closest large-scale multilingual spam/smishing framing; proves multilingual scale does not establish Malayalam transfer",
  "FULL TEXT", "ACL Anthology PDF"],

 ["P09", "Edge-AI Enabled Smishing and Suspicious SMS Detection: A Cost-Sensitive and Lightweight Deep Learning Architecture",
  "H. C. Phap", 2026,
  "Journal of Information and Telecommunication, pp. 1-15",
  "10.1080/24751839.2026.2713250",
  "Not verified", "Not verified",
  "Smishing / suspicious vs legitimate", "BiGRU encoder with masked global pooling; weighted binary cross-entropy",
  "Not verified",
  "No numerical result extracted",
  "Dataset, language, metrics and deployment claims unverified",
  "Cost-sensitive/recall framing only; no Malayalam evidence",
  "ABSTRACT", "Publisher access blocked; abstract only"],

 ["P10", "SMS Spam Detection via a Systematic Machine Learning Pipeline: Feature Engineering, Hyperparameter Optimizing, Scaling, and Ensemble Learning",
  "Not retrieved", 2026,
  "Journal of Engineering Research (volume/pages not retrieved)",
  "10.1016/j.jer.2026.05.020 (workbook only)",
  "Not verified", "Not verified", "Not verified", "Not verified", "Not verified", "Not verified",
  "No confirmable author list, volume or pages", "Excluded; do not cite",
  "EXCLUDED", "Unresolvable record"],

 ["P11", "Machine Learning-Based Smishing Detection Using Fuzzy Logic and TF-IDF Feature Engineering",
  "Santosh Kumar Birthriya; Priyanka Ahlawat; Ankit Kumar Jain", 2026,
  "Franklin Open, vol. 14, Art. no. 100506",
  "10.1016/j.fraope.2026.100506",
  "Not verified", "Not verified", "Smishing vs legitimate",
  "TF-IDF plus fuzzy linguistic/structural features; ML classifiers",
  "Not verified", "No numerical result extracted",
  "Dataset, language and methods unverified", "Optional background only",
  "METADATA", "DOI/bibliographic record only"],

 ["P12", "DravidianCodeMix: Sentiment Analysis and Offensive Language Identification Dataset for Dravidian Languages in Code-Mixed Text",
  "Bharathi Raja Chakravarthi; Ruba Priyadharshini; Vigneshwaran Muralidaran; Navya Jose; Shardul Suryawanshi; Elizabeth Sherly; John P. McCrae", 2022,
  "Language Resources and Evaluation, vol. 56, no. 3, pp. 765-806",
  "10.1007/s10579-022-09583-7",
  ">60,000 YouTube comments: ~44,000 Tamil-English, ~7,000 Kannada-English, ~20,000 Malayalam-English",
  "Tamil, Kannada, Malayalam, each mixed with English",
  "Sentiment; offensive language ONLY", "Manual annotation; Krippendorff's alpha; ML/DL baselines",
  "Annotator agreement and baseline classification",
  "High inter-annotator agreement; public release",
  "YouTube comments, not SMS; no spam/phishing labels",
  "Code-mixing and Malayalam NLP context; cannot be a threat corpus",
  "ABSTRACT", "Open-access abstract/metadata; full baseline table not re-extracted"],

 ["P13", "MuRIL: Multilingual Representations for Indian Languages",
  "Simran Khanuja et al. (14 authors)", 2021,
  "arXiv preprint arXiv:2103.10730",
  "10.48550/arXiv.2103.10730",
  "Wikipedia and OSCAR monolingual text plus translated/transliterated pairs",
  "17 Indian languages; native scripts and Latin transliteration",
  "None (language model)", "BERT-style MLM plus translation language modelling on translated/transliterated pairs",
  "XTREME task evaluation",
  "Outperforms mBERT on evaluated XTREME tasks; reports transliterated test results",
  "No SMS spam, smishing or deployment evaluation; transliterated test sets are derived, not naturally typed Manglish",
  "Model-design citation only; using MuRIL on D1 is a new experiment, not a reproduction",
  "FULL TEXT", "arXiv PDF"],

 ["P14", "Unsupervised Cross-Lingual Representation Learning at Scale (XLM-R)",
  "Alexis Conneau; Kartikay Khandelwal; Naman Goyal; Vishrav Chaudhary; Guillaume Wenzek; Francisco Guzman; Edouard Grave; Myle Ott; Luke Zettlemoyer; Veselin Stoyanov", 2020,
  "Proc. 58th Annual Meeting of the ACL, pp. 8440-8451",
  "10.18653/v1/2020.acl-main.747",
  "CommonCrawl (>2 TB)", "100 languages", "None (language model)",
  "Transformer MLM at scale; XNLI, MLQA, NER, GLUE",
  "Cross-lingual benchmark evaluation",
  "No fine-grained result re-extracted in this audit",
  "Capacity dilution; no SMS, phishing or transliteration evidence",
  "Background on multilingual pretraining only",
  "METADATA", "Bibliographic record only"],

 ["P15", "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
  "Jacob Devlin; Ming-Wei Chang; Kenton Lee; Kristina Toutanova", 2019,
  "Proc. NAACL-HLT 2019, vol. 1, pp. 4171-4186",
  "10.18653/v1/N19-1423",
  "BookCorpus + English Wikipedia", "English", "None (language model)",
  "Masked language modelling + next-sentence prediction; fine-tuning",
  "GLUE, SQuAD and other benchmarks",
  "No fine-grained result re-extracted in this audit",
  "English pretraining; not designed for code-mixed text",
  "Background citation for fine-tuning only",
  "METADATA", "Bibliographic record only"],

 ["B01", "A Smishing Detection Method Based on SMS Contents Analysis and URL Inspection Using Google Engine and VirusTotal",
  "Ameen R. Mahmood; Sarab M. Hameed", 2023,
  "Iraqi Journal of Science, vol. 64, no. 10 (publisher pp. 6276-6291; PDF header 5376-5391)",
  "10.24996/ijs.2023.64.10.41",
  "UCI SMS Spam Collection (5,772) + 120 Pinterest smishing images; final 5,692",
  "English only", "Ham / Smishing",
  "UTF-IDF (label-split TF-IDF) + Chi-square top-1000; SVM (RBF), RF, AdaBoost, XGBoost; URL inspection via Google/VirusTotal",
  "3-fold stratified cross-validation",
  "Best SVM: 98.5% accuracy, 96.9% precision, 93.1% detection, 95.05% F1; URL inspection found 156 vs 145 for VirusTotal alone",
  "English; image-derived smishing; unreleased data; external URL APIs; not comparable to D1",
  "Task and metric reference; not a direct baseline",
  "FULL TEXT", "Official journal PDF"],

 ["E01", "FS_SHAP: Global Interpretable Feature Selection Using XAI for the Classification of Spam SMS in Dravidian Languages",
  "Ramanujam Elangovan; Abirami A. M.; K. G. Thirumalai", 2025,
  "IEEE MultiMedia, vol. 32, no. 1, pp. 92-103 (online 3 Dec 2024)",
  "10.1109/MMUL.2024.3508765",
  "Three SMS datasets; Dravidian languages; D1 DOI in references; exact subset not confirmed",
  "Tamil, Kannada, Telugu, Malayalam (and English per dataset)",
  "Ham / Spam", "SHAP-based global feature selection over handcrafted features; Random Forest",
  "Abstract does not state split or duplicate protocol",
  "No numeric result in abstract; do not cite a number",
  "Full text paywalled; exact D1 use, counts, splits and results unknown; no confirmed transformer comparison",
  "Closest paper; necessitates a narrow evaluation-gap contribution",
  "ABSTRACT", "IEEE Computer Society + ACM records; full text paywalled"],

 ["T01", "Smishing Dataset I: Phishing SMS Dataset from Smishtank.com",
  "Daniel Timko; Muhammad Lutfor Rahman", 2024,
  "Proc. 14th ACM Conf. Data and Application Security and Privacy (CODASPY), pp. 289-294",
  "ACM DL record (DOI not captured)",
  "SmishTank community submissions; 1,062 smishing samples", "English",
  "Smishing (and benign comparisons)", "Dataset construction and descriptive analysis",
  "Descriptive", "1,062 smishing samples released",
  "Community-sourced; not a balanced benchmark; DOI not captured",
  "Alternative smishing source context; not used in the frozen experiment",
  "METADATA", "ACM record only"],

 ["T02", "Social Media Text Analytics of Malayalam-English Code-Mixed Using Deep Learning",
  "S. Thara; Prabaharan Poornachandran", 2022,
  "Journal of Big Data, vol. 9, Art. no. 45",
  "10.1186/s40537-022-00594-3",
  "Malayalam-English code-mixed social media corpus; size not extracted",
  "Malayalam-English, including Romanised Malayalam", "Offensive language; sentiment",
  "Selective transliteration/translation of Romanised text; deep learning baselines",
  "Not extracted", "No numerical result re-extracted in this audit",
  "Social media, not SMS; no spam/phishing labels",
  "Manglish/code-mix context only; not threat detection",
  "ABSTRACT", "Open-access abstract; full methods not re-read"],

 ["S01", "SMSDHL: Spam SMS in Dravidian and Hindi Languages",
  "Ramanujam Elangovan; A. M. Abirami", 2025,
  "TechRxiv preprint, 5 January 2025",
  "10.36227/techrxiv.173603655.53756505",
  "SMSDHL; counts vary by version/subset", "English, Tamil, Telugu, Malayalam, Kannada, Hindi",
  "Ham / Spam", "Dataset description", "Descriptive", "No count used; version-specific counts not verified",
  "Preprint; counts vary; no phishing labels", "Related dataset lineage only",
  "METADATA", "TechRxiv record only"],

 ["E02", "Evaluation of Hand-Crafted Features for the Classification of Spam SMS in Dravidian Languages",
  "E. Ramanujam; K. Sakthi Prakash; A. M. Abirami", 2023,
  "Proc. Int. Conf. Data Science and Network Engineering, Singapore, pp. 3-15",
  "10.1007/978-981-99-6755-1_1",
  "Dravidian SMS; details not verified", "Dravidian languages", "Ham / Spam",
  "Hand-crafted feature evaluation", "Not verified", "No result extracted",
  "Metadata only", "Establishes the feature-engineering lineage; no priority claim",
  "METADATA", "Springer/ORCID record only"],

 ["E03", "XAI-Based Feature Selection for SMS Spam Classification in Dravidian Languages",
  "K. G. Thirumalai; K. S. Prakash; A. M. Abirami; E. Ramanujam; S. Sumitra", 2024,
  "Proc. 5th Int. Conf. Innovative Trends in Information Technology (ICITIIT), p. 215",
  "10.1109/ICITIIT61487.2024.10580065",
  "Dravidian SMS; details not verified", "Dravidian languages", "Ham / Spam",
  "XAI-based feature selection", "Not verified", "No result extracted",
  "Metadata only", "Related XAI lineage; no priority claim",
  "METADATA", "IEEE proceedings/ORCID record only"],

 ["E04", "NCMDFE: Performance Evaluation of Non-Contextual Meta-Data Feature Extraction for Spam SMS Classification in Indian Languages",
  "E. Ramanujam; A. M. Abirami", 2025,
  "International Journal of Information Technology",
  "10.1007/s41870-025-02635-5",
  "Indian-language SMS; details not verified", "Indian languages", "Ham / Spam",
  "Non-contextual metadata feature extraction", "Not verified", "No result extracted",
  "Metadata only", "Related feature-engineering lineage",
  "METADATA", "Crossref/ORCID record only"],

 ["E05", "Efficient Extraction and Evaluation of Hand-Crafted Meta-Data Features for Dravidian Spam SMS Classification",
  "E. Ramanujam; A. M. Abirami; K. Sakthiprakash; S. Sumitra", 2026,
  "Evolving Systems",
  "10.1007/s12530-025-09761-2",
  "Dravidian SMS; details not verified", "Dravidian languages", "Ham / Spam",
  "Hand-crafted metadata feature extraction", "Not verified", "No result extracted",
  "Metadata only", "Related feature-engineering lineage",
  "METADATA", "Springer/ORCID record only"],
]


def main():
    df = pd.DataFrame(ROWS, columns=COLS)
    XLSX.parent.mkdir(parents=True, exist_ok=True)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV, index=False, encoding="utf-8-sig")
    with pd.ExcelWriter(XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Paper Matrix", index=False)
        summary = (
            df.groupby("Verification").size().reset_index(name="Count")
            .sort_values(["Verification", "Count"], ascending=[True, False])
        )
        summary.to_excel(writer, sheet_name="Verification Summary", index=False)

    wb = load_workbook(XLSX)
    ws = wb["Paper Matrix"]
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    fills = {
        "FULL TEXT": "C6EFCE",
        "ABSTRACT": "FFEB9C",
        "METADATA": "FCE4D6",
        "EXCLUDED": "D9D9D9",
    }
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    widths = {"A": 7, "B": 48, "C": 42, "D": 7, "E": 40, "F": 34,
              "G": 46, "H": 30, "I": 24, "J": 46, "K": 38,
              "L": 48, "M": 46, "N": 42, "O": 14, "P": 32}
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        status = row[14].value
        if status in fills:
            row[14].fill = PatternFill("solid", fgColor=fills[status])
    for r in range(2, ws.max_row + 1):
        ws.row_dimensions[r].height = 76
    wb.save(XLSX)
    print(f"Wrote {XLSX} ({len(df)} records)")
    print(f"Wrote {CSV}")
    print(df.groupby("Verification").size().to_string())


if __name__ == "__main__":
    main()
