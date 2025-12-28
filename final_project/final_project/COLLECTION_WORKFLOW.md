# Data Collection Workflow - CSV First Approach

This workflow allows you to **review collected data in CSV format** before uploading to PostgreSQL.

## 📋 Workflow Overview

1. **Collect Data** → Save to CSV (with summarization)
2. **Review CSV** → Check data quality
3. **Upload to Database** → Import CSV to PostgreSQL

---

## Step 1: Collect Data to CSV

### Run the CSV Collector

```bash
cd final_project
python scripts/newsapi_collector_csv.py
```

### What It Does:
- ✅ Fetches articles from NewsAPI
- ✅ **Summarizes articles** to reduce storage (saves ~70% space)
- ✅ Validates and filters articles
- ✅ Saves to CSV file in `data/raw/`
- ✅ Creates checkpoints every 50 articles

### Output:
- CSV file: `data/raw/articles_collected_YYYYMMDD_HHMMSS.csv`
- Checkpoint files: `data/raw/articles_checkpoint_N.csv`

### Summarization Settings

The script automatically summarizes articles to save space. You can modify these in `newsapi_collector_csv.py`:

```python
SUMMARIZE_ARTICLES = True      # Enable/disable summarization
SUMMARY_METHOD = 'sumy'         # Options: 'sumy', 'tfidf', 'simple'
MAX_SUMMARY_SENTENCES = 3       # Number of sentences in summary
MAX_SUMMARY_LENGTH = 500        # Maximum characters
```

**Methods:**
- **sumy** (recommended): Uses LSA algorithm for extractive summarization
- **tfidf**: Uses TF-IDF scoring (requires NLTK)
- **simple**: Takes first N sentences (fallback)

---

## Step 2: Review CSV Data

### Open CSV File

```bash
# View in Excel, Google Sheets, or any CSV viewer
# Or use pandas in Python:
python -c "import pandas as pd; df = pd.read_csv('data/raw/articles_collected_*.csv'); print(df.head())"
```

### Check Data Quality

Verify:
- ✅ All required fields present (title, date, source, content, url)
- ✅ No obvious duplicates
- ✅ Content is meaningful (not just "[Removed]")
- ✅ Article count meets requirement (≥500)

### CSV Columns

| Column | Description |
|--------|-------------|
| title | Article title |
| publication_date | Publication date (YYYY-MM-DD) |
| source | News source name |
| content | **Summarized** article content |
| url | Article URL (unique identifier) |
| keywords | Search query that found this article |
| content_length | Length of summarized content |
| original_length | Length of original content (if summarized) |

---

## Step 3: Upload CSV to PostgreSQL

### Option A: Upload Latest CSV (Automatic)

```bash
python scripts/upload_csv_to_db.py
```

This will automatically find the most recent CSV file in `data/raw/` and upload it.

### Option B: Upload Specific CSV File

```bash
python scripts/upload_csv_to_db.py data/raw/articles_collected_20241201_120000.csv
```

### What It Does:
- ✅ Reads CSV file
- ✅ Validates data structure
- ✅ Removes duplicates (by URL)
- ✅ Uploads to PostgreSQL in batches
- ✅ Shows progress and statistics
- ✅ Skips articles that already exist in database

### Upload Statistics

The script will show:
- Total articles in CSV
- New articles inserted
- Duplicate articles (already in database)
- Final database count

---

## 📊 Monitoring Progress

### Check CSV File

```bash
# Count articles in CSV
python -c "import pandas as pd; df = pd.read_csv('data/raw/articles_collected_*.csv'); print(f'Articles: {len(df)}')"
```

### Check Database (After Upload)

```bash
# Count articles in database
python -c "from scripts.database import DatabaseManager; db = DatabaseManager(); db.connect(); print(f'Articles: {db.get_article_count()}')"
```

### View Database Statistics

```bash
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles -c "SELECT * FROM article_stats;"
```

---

## 🔄 Complete Workflow Example

```bash
# 1. Collect data (saves to CSV)
python scripts/newsapi_collector_csv.py

# 2. Review CSV file (open in Excel/editor)
# File location: data/raw/articles_collected_*.csv

# 3. Upload to database
python scripts/upload_csv_to_db.py

# 4. Verify in database
python -c "from scripts.database import DatabaseManager; db = DatabaseManager(); db.connect(); print(f'Total: {db.get_article_count()}')"
```

---

## 💡 Tips

### If You Need More Articles
- Run collection multiple times (different date ranges)
- Increase `MAX_RESULTS_PER_QUERY` in the script
- Extend `DAYS_BACK` parameter
- Add more data sources

### If Summarization Fails
- Install sumy: `pip install sumy`
- Or use fallback method: Change `SUMMARY_METHOD = 'simple'`
- Or disable: Set `SUMMARIZE_ARTICLES = False`

### If Upload Fails
- Check database is running: `docker ps`
- Verify CSV file exists and is readable
- Check for duplicate URLs in CSV
- Review error messages

---

## 📝 Notes

- **Summarization saves space** but keeps key information
- **Original content is not stored** in CSV (only summary)
- **Full content** can be retrieved from URL if needed
- **Duplicates are automatically handled** during upload
- **Checkpoints** are saved every 50 articles during collection

---

## 🆘 Troubleshooting

**Problem:** Summarization not working
- **Solution:** Install sumy: `pip install sumy`
- Or use simple method: Change `SUMMARY_METHOD = 'simple'`

**Problem:** CSV file not found
- **Solution:** Check `data/raw/` directory exists
- Verify collection script completed successfully

**Problem:** Upload shows many duplicates
- **Solution:** This is normal if you've uploaded before
- Duplicates are automatically skipped

**Problem:** Not enough articles
- **Solution:** Run collection multiple times
- Try different date ranges
- Add more keyword combinations


