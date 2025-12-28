# Task 2: Text Preprocessing & NLP - Summary

## ✅ What's Running

The preprocessing pipeline is currently processing all 1,004 articles from PostgreSQL.

## 🔄 Processing Steps

1. **Loading Data** - Articles from PostgreSQL database
2. **Normalization** - Lowercase, remove URLs, emails, special characters
3. **Tokenization** - Split text into words
4. **Stopword Removal** - Remove common words and domain-specific noise
5. **Lemmatization** - Reduce words to root form (e.g., "building" → "build")
6. **N-gram Generation** - Extract unigrams, bigrams, trigrams
7. **TF-IDF Calculation** - Calculate term importance scores

## 📊 Expected Outputs

### Files Created:
- `data/processed/articles_processed_YYYYMMDD_HHMMSS.csv` - Preprocessed articles
- `data/processed/ngrams_YYYYMMDD_HHMMSS.csv` - N-gram frequencies
- `data/processed/preprocessing_report_YYYYMMDD_HHMMSS.txt` - Analysis report

### Report Contents:
- Top 20 most frequent words (excluding stopwords)
- Top 20 bigrams
- Top 20 trigrams
- Statistics (average tokens, unique tokens, etc.)

## ⏱️ Processing Time

- **Estimated time:** 5-10 minutes for 1,004 articles
- Processing includes:
  - Text normalization
  - Tokenization
  - Stopword removal
  - Lemmatization (with POS tagging)
  - N-gram extraction
  - TF-IDF calculation

## 📝 What the Script Does

### Preprocessing Pipeline:
1. **Normalize:** Convert to lowercase, remove URLs/emails, clean special chars
2. **Tokenize:** Split into words using NLTK
3. **Remove Stopwords:** Filter common English words + domain-specific noise
4. **Lemmatize:** Reduce to root form using WordNet lemmatizer with POS tagging

### Feature Extraction:
1. **N-grams:** 
   - Unigrams (single words)
   - Bigrams (2-word phrases like "machine learning")
   - Trigrams (3-word phrases)
2. **TF-IDF:** 
   - Term Frequency-Inverse Document Frequency
   - Identifies important words per document
   - Creates feature matrix for analysis

## 🎯 Deliverables Status

- [x] Preprocessing script created
- [ ] Processing in progress...
- [ ] Cleaned dataset (will be saved)
- [ ] Report with Top 20 words and bigrams (will be generated)

## 📚 Next Steps

After preprocessing completes:
1. Review the generated report
2. Check processed data files
3. Proceed to **Task 3: Categorization & Trend Analysis**

---

**Status:** Processing articles... Check back in a few minutes!


