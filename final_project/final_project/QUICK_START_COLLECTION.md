# 🚀 Quick Start: Collect Data to CSV

## What Changed?

✅ **New CSV-first workflow** - Review data before uploading to database  
✅ **Automatic summarization** - Articles are summarized to save space (~70% reduction)  
✅ **Separate upload script** - Upload CSV to PostgreSQL when ready

---

## ⚡ Quick Start (3 Commands)

### 1. Collect Data to CSV
```bash
cd final_project
python scripts/newsapi_collector_csv.py
```

**Output:** `data/raw/articles_collected_YYYYMMDD_HHMMSS.csv`

### 2. Review CSV (Optional)
Open the CSV file in Excel/Google Sheets to review the data.

### 3. Upload to Database
```bash
python scripts/upload_csv_to_db.py
```

**Done!** Your articles are now in PostgreSQL.

---

## 📊 What You Get

### CSV File Contains:
- **Title** - Article headline
- **Publication Date** - When article was published
- **Source** - News source name
- **Content** - **Summarized** article (3 sentences, ~500 chars)
- **URL** - Link to full article
- **Keywords** - Search query that found it
- **Content Length** - Size of summary vs original

### Summarization Benefits:
- ✅ **70% space reduction** - Store more articles
- ✅ **Faster processing** - Less data to analyze
- ✅ **Key information preserved** - Important points retained
- ✅ **Original available** - Full article at URL if needed

---

## 📝 Example Output

After running collection, you'll see:

```
[1/56] Query: construction AND artificial intelligence
  Fetched: 15, Valid: 12, Total: 12
[2/56] Query: structural engineering AND machine learning
  Fetched: 18, Valid: 15, Total: 27
...

Collection Summary
============================================================
Articles fetched from API:     850
Valid articles collected:      523
Invalid articles filtered:     45
Duplicate articles skipped:    282

Content Statistics:
  Average original length:   1245 characters
  Average summary length:    387 characters
  Space reduction:           68.9%

✓ Requirement met! (523 articles >= 500)

📄 CSV file saved: data/raw/articles_collected_20241201_143022.csv

Next steps:
1. Review the CSV file
2. Upload to PostgreSQL: python scripts/upload_csv_to_db.py
```

---

## 🔧 Configuration

Edit `scripts/newsapi_collector_csv.py` to customize:

```python
# Summarization settings
SUMMARIZE_ARTICLES = True      # Set False to keep full content
SUMMARY_METHOD = 'sumy'        # 'sumy', 'tfidf', or 'simple'
MAX_SUMMARY_SENTENCES = 3      # Number of sentences
MAX_SUMMARY_LENGTH = 500       # Max characters

# Collection settings
DAYS_BACK = 90                 # How far back to search
MAX_RESULTS_PER_QUERY = 20     # Articles per query
```

---

## 📚 More Information

- **Full Workflow:** See `COLLECTION_WORKFLOW.md`
- **Docker Setup:** See `DOCKER_SETUP.md`
- **Troubleshooting:** See `COLLECTION_WORKFLOW.md` (bottom section)

---

## ✅ Checklist

- [ ] Docker container running (`docker-compose up -d`)
- [ ] `.env` file with `NEWSAPI_KEY`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Run collection script
- [ ] Review CSV file
- [ ] Upload to database
- [ ] Verify: ≥500 articles collected

---

**Ready?** Run: `python scripts/newsapi_collector_csv.py`


