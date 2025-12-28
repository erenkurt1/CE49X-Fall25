# Quick Fix Pathway - Only Chat Working

## Step 1: Quick Diagnosis (2 minutes)

Run the test script to see what's failing:
```bash
cd final_project
python scripts\test_endpoints.py
```

**OR manually test in browser:**
- Open http://localhost:8002
- Open browser DevTools (F12) → Console tab
- Try each feature and check for errors

## Step 2: Check Server Logs

Look at the terminal where the server is running. Look for:
- Import errors
- Database connection errors
- Missing method errors
- Traceback errors

## Step 3: Common Issues & Quick Fixes

### Issue A: Server Not Running
**Fix:** Start the server
```bash
python scripts\view_articles_hybrid_llm.py
```

### Issue B: Database Connection Failed
**Fix:** Check Docker is running
```bash
docker-compose ps
docker-compose up -d
```

### Issue C: Import Errors
**Fix:** Check if all modules are accessible
```bash
python -c "from scripts.database import DatabaseManager; print('OK')"
python -c "from scripts.view_articles_hybrid_llm import *; print('OK')"
```

### Issue D: Missing Method Errors
**Fix:** The `fetch_all_articles()` method should exist now. If not, check database.py

### Issue E: JSON Serialization Errors
**Fix:** Already fixed in code, but ensure server restarted

## Step 4: Rapid Fixes (5 minutes)

### If Search Not Working:
1. Check if `/api/search` endpoint exists
2. Check if database has articles
3. Check server console for errors when searching

### If QA Not Working:
1. Check if Gemini API key is set
2. Check server console for errors
3. Verify database connection

### If Other Endpoints Not Working:
1. Check server console for import errors
2. Check if models are loaded
3. Verify endpoint paths match frontend

## Step 5: Nuclear Option - Restart Everything

```bash
# 1. Stop server (Ctrl+C)

# 2. Restart Docker
docker-compose down
docker-compose up -d

# 3. Wait 10 seconds for DB to be ready

# 4. Start server
python scripts\view_articles_hybrid_llm.py

# 5. Test in browser
```

## Most Likely Issues

1. **Server not restarted** after code changes - RESTART IT
2. **Database not running** - Check Docker
3. **Missing imports** - Check Python path
4. **Frontend calling wrong endpoints** - Check browser console

## Quick Verification

After fixes, test each:
- ✅ Chat - should work (user confirmed)
- ❓ Search - test with "AI construction"
- ❓ QA - test with a question
- ❓ Classify - test with text
- ❓ Insights - click button

---

**RUN THE TEST SCRIPT FIRST TO IDENTIFY THE SPECIFIC ISSUES!**


