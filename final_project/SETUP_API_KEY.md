# ✅ NewsAPI Key Configured

Your NewsAPI key has been set up in the `.env` file.

**API Key:** `a9c84cf1-0af7-4560-8408-3325c00abf3a`

## Next Steps

### 1. Verify Setup
```bash
cd final_project
python scripts/check_setup.py
```

This will verify:
- ✅ Docker container is running
- ✅ Python packages are installed
- ✅ Environment file is configured
- ✅ Database connection works

### 2. Start Data Collection

**Option A: Collect to CSV (Recommended)**
```bash
python scripts/newsapi_collector_csv.py
```

**Option B: Collect directly to Database**
```bash
python scripts/newsapi_collector.py
```

## Important Notes

- **Rate Limits:** Free tier allows 100 requests/day
- **Collection Time:** May take 1-2 hours depending on rate limits
- **Target:** Collect ≥500 articles

## If Collection is Slow

Due to rate limits, you may need to:
1. Run collection over multiple days
2. Or upgrade to paid NewsAPI tier
3. Or combine with web scraping from other sources

---

**Ready to start?** Run: `python scripts/newsapi_collector_csv.py`





