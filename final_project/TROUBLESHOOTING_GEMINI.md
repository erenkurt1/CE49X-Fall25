# Troubleshooting Gemini API Issues

## Status

✅ **API Key:** Valid and working  
✅ **Model:** `models/gemini-2.5-flash` works when tested directly  
✅ **Code:** Updated to use correct model names  
✅ **Error Handling:** Improved with better logging  

## Changes Made

1. ✅ Updated model names to newer versions (`models/gemini-2.5-flash`)
2. ✅ Added model caching to avoid recreating model instances
3. ✅ Improved error handling and response parsing
4. ✅ Added detailed error logging

## If You're Still Getting Errors

### Step 1: Check Server Logs

When you start the server, you should see:
```
✓ Gemini API configured
Using Gemini model: models/gemini-2.5-flash
```

If you see error messages, note what they say.

### Step 2: Test Directly

Run this to verify the API works:
```bash
python scripts/debug_gemini.py
```

This should show "=== SUCCESS ===" at the end.

### Step 3: Check Browser Console

1. Open the interface: http://localhost:8002
2. Open browser developer tools (F12)
3. Go to Console tab
4. Try Q&A or Chat
5. Check for JavaScript errors

### Step 4: Check Network Tab

1. In browser developer tools, go to Network tab
2. Try Q&A or Chat
3. Find the API request (should be `/api/qa` or `/api/chat`)
4. Click on it and check:
   - Response status (should be 200)
   - Response body (check for error messages)

## Common Issues

### Issue 1: "undefined" Response

**Check:**
- Browser console for JavaScript errors
- Network tab for API response
- Server console for Python errors

**Solution:**
- Make sure server was restarted after code changes
- Check that response handling code is correct (already fixed)

### Issue 2: Model Not Found Error

**Check:**
- Server startup logs - should show "Using Gemini model: models/gemini-2.5-flash"
- If not, check API key is correct

**Solution:**
- Code already updated to use correct model
- Restart server if needed

### Issue 3: Quota Exceeded

**Check:**
- Server logs for "quota" error messages

**Solution:**
- Check your Google Cloud Console for API usage
- The code tries alternative models automatically
- Consider upgrading your API plan

### Issue 4: Server Not Responding

**Check:**
- Is server running? Check: `netstat -ano | findstr :8002`
- Server console for error messages

**Solution:**
- Restart server: `python scripts/view_articles_hybrid_llm.py`
- Check for port conflicts

## Debugging Steps

1. **Verify API works:**
   ```bash
   python scripts/debug_gemini.py
   ```

2. **Check server logs:**
   - Start server and watch console output
   - Look for error messages

3. **Test from browser:**
   - Open http://localhost:8002
   - Check browser console (F12)
   - Try Q&A or Chat
   - Check Network tab for API calls

4. **Check specific error:**
   - What exact error message do you see?
   - Where does it appear? (browser, server console, etc.)
   - When does it happen? (immediately, after clicking, etc.)

## Current Configuration

- **Model:** `models/gemini-2.5-flash` (tested and working)
- **API Key:** Configured (tested and working)
- **Fallback Models:** Code tries multiple models automatically
- **Caching:** Model instance is cached (created once, reused)

## Next Steps

If issues persist:

1. **Share the exact error message** you see
2. **Check server console** for error logs
3. **Check browser console** for JavaScript errors
4. **Run debug script:** `python scripts/debug_gemini.py`

The API works when tested directly, so the issue is likely:
- Server needs restart (done)
- Browser cache (try hard refresh: Ctrl+F5)
- JavaScript error handling
- Network/proxy issues

---

**Server has been restarted with all fixes. Please test again and let me know what specific error you see.**





