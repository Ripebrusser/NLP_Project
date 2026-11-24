# Baseline Paper Analysis

## Mahmood, A. R., and Hameed, S. M. (2023)
**"A Smishing Detection Method Based on SMS Contents Analysis and URL Inspection Using Google Engine and VirusTotal"**

- **Journal:** Iraqi Journal of Science
- **Volume/Year:** Vol. 64, No. 10, October 2023
- **Pages:** publisher "How to Cite" and Google Scholar give **6276–6291**; the PDF running header gives **5376–5391**. Same DOI; discrepancy noted.
- **DOI:** 10.24996/ijs.2023.64.10.41
- **URL:** https://doi.org/10.24996/ijs.2023.64.10.41
- **Full text read:** YES — PDF accessed from ijs.uobaghdad.edu.iq

---

## 1. Problem

Smishing (SMS phishing) is the delivery of phishing content to mobile users via SMS. Attackers use low-cost SMS subscriptions to reach large numbers of victims with messages containing links to malware or phishing websites that solicit sensitive information.

The paper identifies limitations in prior work:
- Many prior methods rely only on content analysis or only on URL checking
- APK download checking is underexplored
- Feature selection is not always applied
- URL inspection using Google engine combined with VirusTotal is novel (claimed as first use)

---

## 2. Dataset

| Aspect | Detail |
|--------|--------|
| **Primary dataset** | UCI SMS Spam Collection (5,772 messages: 4,825 ham, 747 spam) |
| **Phishing supplement** | Pinterest's 120 phishing SMS images |
| **Final dataset** | 867 smishing + 4,825 ham = 5,692 messages |
| **How phishing labels created** | Pinterest smishing images were converted to text; smishing messages extracted from UCI spam collection |
| **Language** | English only |
| **Label definition** | Ham (legitimate) vs Smishing (phishing SMS) |
| **Source of smishing labels** | Images from Pinterest + extraction from spam corpus — **not independently verified ground truth** |

### Dataset concerns
- The "smishing" labels are derived from images converted to text, not from naturally occurring labeled SMS
- The paper itself acknowledges "the smishing dataset isn't published"
- The final dataset combines two different sources, which may introduce source-confound bias

---

## 3. Preprocessing

The paper describes a 4-step SMS content preprocessing pipeline:

1. **Token identification** — split message by spaces
2. **Stopword exclusion** — remove stopwords; remove all punctuation; generate keyword list
3. **Stemming** — reduce tokens to origin word (e.g., "studying" → "study") to increase word frequency
4. **Token normalization** — convert currency symbols, numbers, phone numbers, email IDs, and URLs to specific placeholder tokens:
   - Currency symbols ($/€) → `moneysymb`
   - Numbers → `number`
   - Email addresses → `Emailaddr`
   - Phone numbers → `Phonenumber`
   - http/www → `httpaddr`

### Relevance to our project
- The preprocessing is designed for English text
- Stemming approach is language-specific (English Porter stemmer implied)
- No handling of Malayalam script, Manglish romanization, or code-switching
- Stopword lists would not transfer to Malayalam

---

## 4. Algorithms

### Two-stage detection architecture

**Stage 1: URL Inspection** (if URL present in SMS)
- Extract URL from SMS
- Extract domain name
- Extract nouns from SMS message
- Concatenate domain name + nouns
- Google Search with concatenated query
- Check if domain name appears in top 5 Google results
- If not found, check via VirusTotal API
- URL classified as legitimate or malicious

**Stage 2: SMS Content Analysis** (if no URL, or as parallel path)
1. Preprocessing (4 steps above)
2. **Feature extraction** — proposed "UTF-IDF" approach:
   - Split dataset into ham set (Sh) and smishing set (Ss)
   - Compute word unigram and bigram frequencies separately for each set
   - Take top 1000 terms from each set → Fh and Fs
   - Combine: Fhs = Fh ∪ Fs
   - Compute TF-IDF scores per message using this combined vocabulary
   - Claim: splitting by label preserves feature importance relative to message type
3. **Feature selection** — Chi-square test to select top 1000 features from the TF-IDF vectors
4. **Classification** — Four classifiers:
   - SVM (RBF kernel, C=1)
   - Random Forest (2000 trees)
   - AdaBoost (100 trees, learning rate=1)
   - XGBoost (5000 trees, max depth=5, learning rate=0.01)

### Novelty claimed by authors
- "UTF-IDF" — TF-IDF computed on label-split subsets rather than the whole corpus
- Combination of Google engine + VirusTotal for URL inspection
- Feature selection with Chi-square

---

## 5. Evaluation

| Aspect | Detail |
|--------|--------|
| **Cross-validation** | Stratified 3-fold cross-validation |
| **Train/test split** | 2 folds train, 1 fold test; iterated until all folds used as test |
| **Metrics** | Accuracy, Precision, Detection Rate (Recall), F1-score |
| **Hardware** | Intel Core 7 Duo 2.90 GHz, 8 GB RAM, Windows 10 |
| **Language** | Python 3.9 |

### Results (from paper)

**URL inspection comparison:**
| Technique | Smishing detected |
|-----------|-------------------|
| VirusTotal alone (from [17]) | 145 |
| Proposed (Google + VirusTotal) | 156 |

**UTF-IDF vs standard TF-IDF (accuracy):**
- UTF-IDF consistently outperforms standard TF-IDF for unigram, bigram, and combined
- Figure 2-4 show accuracy comparisons per classifier

**Best results (proposed method, UTF-IDF + Chi-square):**
| Classifier | Accuracy | Precision | Detection Rate | F1-Score |
|------------|----------|-----------|----------------|----------|
| **SVM** | **98.5%** | **96.9%** | **93.1%** | **95.05%** |
| RF | 98.0% | 98.0% | 88.8% | 93.1% |
| AdaBoost | 98.0% | 96.0% | 90.8% | 93.3% |
| XGBoost | 97.9% | 96.7% | 89.5% | 92.8% |

**Comparison with prior work [15]:**
| Model | Features | Acc | P | DR | F1 |
|-------|----------|-----|-----|----|-----|
| [15] SVM | 4123 | 0.973 | 0.908 | 0.922 | 0.915 |
| Proposed SVM | 1000 | 0.985 | 0.969 | 0.931 | 0.9505 |

---

## 6. Limitations

### Authors' acknowledged limitations
- Dataset is not published (smishing dataset)
- Deep learning could be explored for feature extraction
- More smishing messages could improve the model

### Independent assessment of limitations

1. **English-only**: No handling of non-English scripts or code-mixing
2. **Dataset construction concerns**: Smishing labels derived from Pinterest images + spam corpus extraction — not naturally occurring labeled smishing messages
3. **Source confound**: Combining two different sources (UCI spam + Pinterest images) may allow classifier to learn source artifacts rather than smishing content
4. **URL dependency**: The two-stage architecture requires URL presence; purely text-based smishing without URLs would only use Stage 2
5. **Small phishing sample**: Only 867 smishing messages total, derived from 120 Pinterest images
6. **No monolingual non-English evaluation**: The paper does not address multilingual or code-mixed text
7. **3-fold CV**: Relatively low number of folds; variance not reported
8. **Google API dependency**: URL inspection requires live Google Search API access, which may have rate limits and cost implications
9. **VirusTotal API dependency**: Requires VirusTotal API access

---

## 7. Relevance to Our Project

### What this paper supports
- **Smishing is a valid cybersecurity threat category** distinct from general spam
- **Two-stage architecture** (URL inspection + content analysis) is a reasonable design pattern
- **TF-IDF + classical classifiers (especially SVM)** can be effective for SMS text classification
- **Feature selection** (Chi-square) can improve performance and reduce dimensionality
- **Reporting precision, recall, F1 separately** is good practice (not just accuracy)

### What this paper does NOT support for our project
- **No Malayalam or Manglish evidence** — entirely English
- **No code-mixed text handling** — no transliteration, no script switching
- **No phishing-specific labels in Dravidian languages** — the paper's smishing dataset is English
- **The "UTF-IDF" novelty** is a specific implementation choice, not a general method validated across languages
- **The URL inspection stage** depends on Google/VirusTotal APIs, which may not be appropriate for all deployments

### Suitability as our PRIMARY baseline paper

**Assessment: NOT IDEAL as primary baseline, but usable as a method reference.**

Reasons:
1. **Language mismatch**: Our project targets Malayalam/Manglish; this paper is English-only
2. **Task mismatch**: The paper is smishing (SMS phishing) which is closer to our goal than spam detection, but still English
3. **Dataset concern**: The paper's smishing labels come from Pinterest images, not naturally labeled SMS — this is weaker ground truth than we would want
4. **Architecture dependency**: The URL inspection stage requires external APIs (Google, VirusTotal) — may not fit our text-only scope
5. **Better baselines exist in our review**: P01 (Almeida et al. 2011) is a cleaner baseline for text-only SVM with a well-documented public dataset; P05 (PhishNet) provides a more modern three-class taxonomy

### Recommended role in our literature review
- Cite as **methodological reference** for smishing detection architecture
- Use the two-stage concept (URL + content) as a discussion point for what our text-only system will NOT cover
- Use the evaluation metric reporting style (precision, recall, F1 separately)
- Do NOT cite as validation of TF-IDF + SVM for Malayalam/Manglish
- Do NOT cite the 98.5% accuracy as an expected result for our task

---

## 8. Comparison with Other Papers in Our Review

| Aspect | Mahmood & Hameed (2023) | Almeida et al. (2011) [P01] | PhishNet (Alhuzali et al. 2026) [P05] |
|--------|------------------------|-----------------------------|--------------------------------------|
| **Task** | Smishing (SMS phishing) | Spam (unsolicited SMS) | Three-class: ham/spam/smishing |
| **Language** | English | English | English |
| **Dataset** | UCI + Pinterest images | UCI SMS Spam Collection | Mishra-Soni + synthetic |
| **Features** | UTF-IDF (custom) + Chi-square | Token-based (WEKA defaults) | BERT embeddings + LLM ensemble |
| **Classifiers** | SVM, RF, AdaBoost, XGBoost | 14 classifiers (NB, SVM, C4.5, etc.) | BERT, RoBERTa, DistilBERT, LLMs |
| **URL handling** | Google + VirusTotal API | None | None (content only in Dataset1) |
| **Best F1** | 95.05% (SVM) | 0.893 MCC (SVM) | Not directly comparable |
| **Multilingual** | No | No | No (English only) |
| **Code-mixed** | No | No | No |
| **Dataset public** | No (smishing part) | Yes (UCI) | Partially (Dataset1 yes, Dataset2 mixed) |

---

## 9. Conclusion

Mahmood & Hameed (2023) is a legitimate smishing detection paper with a novel two-stage architecture and reported strong results (98.5% accuracy, 95.05% F1 with SVM). However, it is **English-only, uses a weakly-constructed smishing dataset, and relies on external URL APIs**. It is suitable as a methodological reference but **not as a direct baseline for our Malayalam/Manglish cybersecurity threat detection project**, because:

1. No Malayalam/Manglish evidence exists in this paper
2. The dataset construction (Pinterest images → text) is weaker than naturally labeled data
3. The URL inspection stage is outside a text-only scope
4. Better baseline choices exist in our reviewed literature (P01 for classical SVM; P05 for three-class taxonomy)

**Recommendation:** Use this paper as a citation for smishing detection methodology, but do not treat it as the primary baseline for our work. The primary baseline for our project should be determined after the dataset question is resolved.

---

*Analysis based on full text read from: https://ijs.uobaghdad.edu.iq/index.php/eijs/article/download/8119/4149/104396*

---

**Note:** this document records the full reading of the base paper. The final base-paper decision, including the two-reference recommendation (B01 for smishing framing, P01 for the classical text baseline), is in `BASE_PAPER_SELECTION.md`. This analysis is consistent with that decision: B01 is a methodological reference, not a direct baseline.
