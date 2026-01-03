# Google News Collection Guide

Since NewsAPI had issues, we've switched to **Google News scraping** - no API key required!

## 🚀 Quick Start

### Option 1: Simple Method (Recommended)

Uses the `googlenews` library - easier and more reliable.

```bash
cd final_project

# Install the library
pip install googlenews python-dateutil

# Run collection
python scripts/google_news_simple.py
```

### Option 2: Web Scraping Method

Uses BeautifulSoup to scrape Google News directly.

```bash
cd final_project

# Run collection
python scripts/google_news_collector.py
```

## 📊 What It Does

- ✅ Searches Google News for Civil Engineering + AI keywords
- ✅ Collects article titles, URLs, sources, dates
- ✅ Summarizes articles automatically (saves space)
- ✅ Saves to CSV for review
- ✅ No API key required!

## 📝 Output

Creates CSV file: `data/raw/articles_google_news_YYYYMMDD_HHMMSS.csv`

Columns:
- `title` - Article headline
- `publication_date` - Publication date
- `source` - News source
- `content` - Summarized article content
- `url` - Article URL
- `keywords` - Search query used
- `content_length` - Summary length
- `original_length` - Original length (if summarized)

## ⚙️ Configuration

Edit the script to customize:

```python
# In google_news_simple.py or google_news_collector.py

# Summarization
SUMMARIZE_ARTICLES = True      # Enable/disable
SUMMARY_METHOD = 'simple'       # 'sumy', 'tfidf', or 'simple'
MAX_SUMMARY_SENTENCES = 3       # Sentences in summary
MAX_SUMMARY_LENGTH = 500       # Max characters

# Collection
MAX_RESULTS_PER_QUERY = 10     # Articles per search query
```

## 🔄 Workflow

1. **Collect Data:**
   ```bash
   python scripts/google_news_simple.py
   ```

2. **Review CSV:**
   - Open `data/raw/articles_google_news_*.csv`
   - Check data quality

3. **Upload to Database:**
   ```bash
   python scripts/upload_csv_to_db.py
   ```

## 💡 Tips

- **Run multiple times** - Google News results vary, so running multiple times can get more articles
- **Adjust queries** - Modify keyword combinations in the script if needed
- **Be patient** - Collection may take 30-60 minutes for 500+ articles
- **Check rate limits** - Google may temporarily block if too many requests

## 🆘 Troubleshooting

**Problem:** `googlenews` library not found
- **Solution:** `pip install googlenews python-dateutil`

**Problem:** Getting blocked by Google
- **Solution:** 
  - Increase delays between requests (change `time.sleep(2)` to higher)
  - Run collection in smaller batches
  - Use VPN or different IP

**Problem:** Not enough articles
- **Solution:**
  - Run multiple times
  - Increase `MAX_RESULTS_PER_QUERY`
  - Add more keyword combinations
  - Try different date ranges

**Problem:** Articles missing content
- **Solution:** This is normal - Google News often only provides titles/descriptions. The URLs are included so you can fetch full content later if needed.

## 📈 Expected Results

- **Collection time:** 30-60 minutes for 500+ articles
- **Success rate:** ~60-80% of found articles will be valid
- **May need multiple runs** to reach 500 articles

## ✅ Next Steps

Once you have 500+ articles in CSV:
1. Review the data
2. Upload to PostgreSQL: `python scripts/upload_csv_to_db.py`
3. Proceed to Task 2: Text Preprocessing

---

**Ready?** Run: `python scripts/google_news_simple.py`





