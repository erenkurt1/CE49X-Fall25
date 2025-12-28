# Article Filtering Guide

## ✅ Filtering Results

Your articles have been filtered! Here's what happened:

- **Initial articles:** 491
- **Articles kept:** 446 (relevant)
- **Articles removed:** 45 (unrelated)
- **Retention rate:** 90.8%

## 📊 Filtered Files

1. **Filtered articles:** `data/raw/articles_checkpoint_491_filtered.csv`
   - Contains 446 relevant articles
   - Ready to use for analysis

2. **Removed articles:** `data/raw/articles_checkpoint_491_removed.csv`
   - Contains 45 unrelated articles
   - Review if needed to adjust filters

## 🎯 How Filtering Works

The filter uses **relevance scoring** based on:

### ✅ Must Have:
- **At least 1 Civil Engineering keyword** (construction, structural, infrastructure, etc.)
- **At least 1 AI/ML keyword** (AI, machine learning, computer vision, etc.)

### ❌ Excludes:
- Medical/healthcare articles (patient, disease, cancer, etc.)
- General AI articles (data centers, software, startups)
- Finance/accounting articles
- Education articles (unless construction-related)
- Articles with exclusion phrases

### 📈 Scoring:
- **Base score:** 50 (if has both CE and AI keywords)
- **Bonus:** +5 per additional keyword (up to 25 points each)
- **Bonus:** +10 if both keywords appear in title
- **Penalty:** -20 for very short content

**Minimum score to keep:** 30 (default, adjustable)

## 🔧 Usage

### Basic Filtering:
```bash
python scripts/filter_articles.py data/raw/articles_checkpoint_491.csv
```

### Custom Score Threshold:
```bash
# Lower threshold (keep more articles, but may include less relevant ones)
python scripts/filter_articles.py data/raw/articles_checkpoint_491.csv 20

# Higher threshold (keep only highly relevant articles)
python scripts/filter_articles.py data/raw/articles_checkpoint_491.csv 50
```

## 📝 Next Steps

### 1. Review Filtered Articles
Open `articles_checkpoint_491_filtered.csv` and check:
- Are the articles actually relevant?
- Do they discuss Civil Engineering AND AI?

### 2. Review Removed Articles
Open `articles_checkpoint_491_removed.csv` and check:
- Were any relevant articles incorrectly removed?
- If yes, you may need to adjust the filter keywords

### 3. Collect More Articles
You have 446 articles, need 54 more to reach 500:
```bash
# Run collection again
python scripts/google_news_fast.py

# Then filter the new collection
python scripts/filter_articles.py data/raw/articles_google_news_fast_*.csv
```

### 4. Combine and Upload
Once you have 500+ filtered articles:
```bash
# Combine multiple filtered CSV files if needed
# Then upload to database
python scripts/upload_csv_to_db.py
```

## ⚙️ Customizing Filters

Edit `scripts/filter_articles.py` to adjust:

### Add More CE Keywords:
```python
CE_KEYWORDS = [
    'construction', 'structural', ...
    'your_new_keyword',  # Add here
]
```

### Add More AI Keywords:
```python
AI_KEYWORDS = [
    'artificial intelligence', 'ai', ...
    'your_new_keyword',  # Add here
]
```

### Adjust Exclusions:
```python
EXCLUSION_KEYWORDS = [
    'patient', 'disease', ...
    # Add or remove exclusion keywords
]
```

## 📈 Current Status

- ✅ **446 relevant articles** collected
- ⚠️ **Need 54 more** to reach 500
- 💡 **Solution:** Run collection 1-2 more times, then filter

## 🎯 Quick Command Reference

```bash
# Filter existing collection
python scripts/filter_articles.py data/raw/articles_checkpoint_491.csv

# Collect more articles (fast)
python scripts/google_news_fast.py

# Filter new collection
python scripts/filter_articles.py data/raw/articles_google_news_fast_*.csv

# Upload to database (when ready)
python scripts/upload_csv_to_db.py
```

---

**Tip:** The filter is conservative - it keeps articles that are clearly relevant. If you need more articles, either:
1. Collect more (run collection script again)
2. Lower the score threshold (e.g., 20 instead of 30)


