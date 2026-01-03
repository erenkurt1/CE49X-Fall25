# Fixing Gemini API Errors

## Quick Fix Steps

### Step 1: Test Your API Key

Run this test script to see what models are available:

```bash
python scripts/test_gemini_models.py
```

This will:
- Show all available models
- Test which model names work
- Tell you which model name to use

### Step 2: Check the Output

The script will tell you which model name works. Common model names are:
- `gemini-1.5-flash` (newest, fastest)
- `gemini-1.5-pro` (newest, most capable)
- `gemini-pro` (older)
- `models/gemini-1.5-flash` (with prefix)
- `models/gemini-pro` (with prefix)

### Step 3: Update Code if Needed

The code has been updated to automatically try different model names. However, if the test script shows a specific model name that works, you can hardcode it:

In `view_articles_hybrid_llm.py`, find `get_gemini_model()` and update the model list:

```python
model_names_to_try = ['YOUR_WORKING_MODEL_NAME_HERE']
```

## Common Issues

### Issue 1: "404 models/gemini-pro is not found"

**Solution:** The model name format is wrong. The code now tries multiple formats automatically.

### Issue 2: "undefined" in responses

**Solution:** Already fixed! The code now handles responses properly with fallbacks.

### Issue 3: API Key Invalid

**Solution:** 
1. Check your API key is correct
2. Make sure you've enabled the Gemini API in Google Cloud Console
3. Check your API quota/limits

## If Still Not Working

1. **Run the test script:**
   ```bash
   python scripts/test_gemini_models.py
   ```

2. **Check the output** - it will show:
   - Which models are available
   - Which model name works
   - Any error messages

3. **Update the code** with the working model name

4. **Restart the server:**
   ```bash
   python scripts/view_articles_hybrid_llm.py
   ```

## Alternative: Use Local Models Only

If Gemini API continues to have issues, you can disable it and use only local models:

In the code, set:
```python
GEMINI_AVAILABLE = False
```

Then only these features will work:
- ✅ Semantic Search (local)
- ✅ Classification (local)
- ❌ Q&A (requires Gemini)
- ❌ Chat (requires Gemini)
- ❌ Insights (requires Gemini)





