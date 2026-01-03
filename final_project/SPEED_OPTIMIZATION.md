# Speed Optimization Guide

## 🚀 Fast Collection Script

Use the **fast collector** for maximum speed:

```bash
python scripts/google_news_fast.py
```

## ⚡ Speed Optimizations Applied

### 1. **No Content Fetching**
- Uses Google News descriptions only
- No HTTP requests to fetch full articles
- **Saves: ~5-10 seconds per article**

### 2. **No Summarization During Collection**
- Summarization is slow (NLP processing)
- Do it later if needed, or skip it
- **Saves: ~1-2 seconds per article**

### 3. **Reduced Delays**
- Changed from 1-2 seconds to 0.5 seconds between queries
- **Saves: ~30-60 seconds total**

### 4. **Batch Processing**
- Less frequent checkpoint saves (every 100 vs every 50)
- **Saves: ~10-20 seconds**

### 5. **More Results Per Query**
- Increased from 10 to 15 articles per query
- **Gets more articles per run**

## 📊 Expected Performance

### Fast Collector (`google_news_fast.py`)
- **Speed:** ~2-5 articles/second
- **Time for 500 articles:** ~2-5 minutes
- **Content:** Descriptions only (from Google News)

### Regular Collector (`google_news_simple.py`)
- **Speed:** ~0.5-1 article/second
- **Time for 500 articles:** ~10-20 minutes
- **Content:** Descriptions (with optional summarization)

## 🎯 Recommendations

### For Maximum Speed:
```bash
python scripts/google_news_fast.py
```

### If You Need Full Content:
1. Use fast collector to get URLs quickly
2. Later, fetch full content from URLs if needed
3. Or use the regular collector (slower but has more content)

## 💡 Additional Speed Tips

### 1. Run Multiple Times
Google News results vary. Running 2-3 times can get different articles:
```bash
python scripts/google_news_fast.py
# Wait a few minutes
python scripts/google_news_fast.py  # Run again
```

### 2. Combine Results
After multiple runs, combine CSV files:
```python
import pandas as pd

# Combine multiple CSV files
df1 = pd.read_csv('articles_google_news_fast_1.csv')
df2 = pd.read_csv('articles_google_news_fast_2.csv')
combined = pd.concat([df1, df2]).drop_duplicates(subset=['url'])
combined.to_csv('articles_combined.csv', index=False)
```

### 3. Skip Summarization
If you don't need summaries:
- Use `google_news_fast.py` (no summarization)
- Or set `SUMMARIZE_ARTICLES = False` in other scripts

### 4. Parallel Processing (Advanced)
For even more speed, you could:
- Split queries across multiple processes
- Use threading (but be careful with rate limits)

## ⚠️ Trade-offs

### Fast Collector:
✅ **Pros:**
- Very fast (2-5 min for 500 articles)
- No API limits
- Simple and reliable

❌ **Cons:**
- Only descriptions (not full articles)
- May need multiple runs to get 500 unique articles

### Regular Collector:
✅ **Pros:**
- More content available
- Can summarize if needed

❌ **Cons:**
- Slower (10-20 min for 500 articles)
- More processing

## 📈 Performance Comparison

| Method | Time (500 articles) | Content Type | Speed |
|--------|-------------------|--------------|-------|
| Fast Collector | 2-5 min | Descriptions | ⚡⚡⚡⚡⚡ |
| Simple Collector | 10-20 min | Descriptions | ⚡⚡⚡ |
| With Summarization | 20-40 min | Summarized | ⚡⚡ |
| With Full Content | 60+ min | Full articles | ⚡ |

## ✅ Recommended Workflow

1. **First Run:** Use fast collector to get 500+ articles quickly
   ```bash
   python scripts/google_news_fast.py
   ```

2. **If Needed:** Run again to get more unique articles
   ```bash
   python scripts/google_news_fast.py
   ```

3. **Review:** Check the CSV file

4. **Upload:** Add to database
   ```bash
   python scripts/upload_csv_to_db.py
   ```

5. **Later (Optional):** If you need full content, fetch from URLs

---

**Bottom Line:** Use `google_news_fast.py` for speed! It's 5-10x faster than other methods.





