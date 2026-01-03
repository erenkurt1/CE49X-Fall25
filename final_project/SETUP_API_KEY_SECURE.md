# Setting Up Gemini API Key Securely

## Important: API Key Security

**Never hardcode API keys in your code!** Always use environment variables.

## How to Set API Key

### Windows (PowerShell)
```powershell
$env:GEMINI_API_KEY="your_new_api_key_here"
```

### Windows (Command Prompt)
```cmd
set GEMINI_API_KEY=your_new_api_key_here
```

### Linux/Mac
```bash
export GEMINI_API_KEY="your_new_api_key_here"
```

## Get a New API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the new key
4. Set it as an environment variable (see above)
5. **Never commit it to git!**

## Verify It's Set

### Windows (PowerShell)
```powershell
echo $env:GEMINI_API_KEY
```

### Linux/Mac
```bash
echo $GEMINI_API_KEY
```

## Running the Server

After setting the environment variable, run:
```bash
python scripts/view_articles_hybrid_llm.py
```

The server will automatically use the environment variable.

## Permanent Setup (Optional)

To make it permanent on Windows:
1. Open System Properties → Environment Variables
2. Add new User variable:
   - Name: `GEMINI_API_KEY`
   - Value: `your_api_key_here`




