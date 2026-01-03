# ⚠️ NewsAPI Key Issue

## Problem
Your API key `a9c84cf1-0af7-4560-8408-3325c00abf3a` is being rejected by NewsAPI as invalid.

## Possible Causes

1. **Key Not Activated**
   - New accounts need to verify email
   - Check your email for activation link

2. **Incorrect Key**
   - Double-check you copied the full key
   - Make sure there are no extra spaces

3. **Key Expired/Revoked**
   - Free tier keys can expire
   - Check your NewsAPI dashboard

4. **Account Issues**
   - Account may be suspended
   - Check NewsAPI account status

## Solutions

### Option 1: Verify Your Key
1. Go to https://newsapi.org
2. Log in to your account
3. Check your API key in the dashboard
4. Copy the key again (make sure it matches exactly)

### Option 2: Get a New Key
1. Go to https://newsapi.org/register
2. Create a new account (or use existing)
3. Verify your email
4. Get your new API key
5. Update the script with the new key

### Option 3: Use Alternative Data Sources
Since NewsAPI has issues, consider:
- **Web Scraping**: Scrape construction news sites directly
- **RSS Feeds**: Use RSS feeds from engineering news sites
- **Other APIs**: Look for alternative news APIs

## Update the Key

Once you have a valid key, update it in:

1. **Script** (hardcoded): `scripts/newsapi_collector_csv.py`
   - Line 28: Change the fallback API_KEY value

2. **Environment file**: `final_project/.env`
   - Update NEWSAPI_KEY value

## Test Your Key

Run the test script:
```bash
python scripts/test_api_key.py
```

If it shows "SUCCESS", your key is working!

---

**Next Steps:**
1. Verify/get a new API key from NewsAPI
2. Update the key in the script
3. Run the test script to verify
4. Then run the collection script





