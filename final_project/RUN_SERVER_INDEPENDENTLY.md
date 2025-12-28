# Running the Hybrid LLM Server Independently

## ✅ Yes, the Server Runs Completely Independently!

Once you start the server, it runs on your computer and doesn't need any AI assistant to keep working. You can close this chat, close your IDE, and the server will keep running until you stop it.

---

## How to Start the Server

### Step 1: Open Terminal/Command Prompt

Open PowerShell or Command Prompt on Windows.

### Step 2: Navigate to Project Directory

```bash
cd C:\Users\erenb\PycharmProjects\pythonProject1\final_project
```

### Step 3: Start the Server

```bash
python scripts\view_articles_hybrid_llm.py
```

### Step 4: Server Starts

You should see output like:
```
[OK] Gemini API configured
[OK] Loading local models...
  [OK] Semantic search model loaded
  [OK] Classification model loaded (if available)
  [OK] Summarization model loaded (if available)
Using Gemini model: models/gemini-2.5-flash
============================================================
Hybrid LLM-Powered Article System
============================================================

Server running at: http://localhost:8002

Features:
  [OK] Semantic Search (Local: sentence-transformers)
  [OK] Article Classification (Local: BART zero-shot)
  [OK] Question Answering (Gemini API)
  [OK] Chatbot (Gemini API)
  [OK] Automated Insights (Gemini API)
  [OK] Summarization (Local: BART)

Status:
  Gemini API: [OK] Available
  Local Models: [OK] Available

Opening browser...
Press Ctrl+C to stop the server
```

### Step 5: Use the Interface

The browser should open automatically. If not, go to: **http://localhost:8002**

You can now:
- ✅ Use Chat - works independently
- ✅ Use QA - works independently  
- ✅ Use Search - works independently
- ✅ Use Classify - works independently
- ✅ Use Insights - works independently

---

## Running in Background (Optional)

### Windows PowerShell (Background Job)

```powershell
Start-Process python -ArgumentList "scripts\view_articles_hybrid_llm.py" -WindowStyle Hidden
```

### Windows Command Prompt (Background)

```cmd
start /B python scripts\view_articles_hybrid_llm.py
```

### Or Keep Terminal Open

Just leave the terminal window open - the server will keep running!

---

## Stopping the Server

Press **Ctrl+C** in the terminal where the server is running.

---

## Troubleshooting

### Server Won't Start?

1. **Check if port 8002 is already in use:**
   ```bash
   netstat -ano | findstr :8002
   ```
   If something is using it, stop that process first.

2. **Check Python is installed:**
   ```bash
   python --version
   ```

3. **Check dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

### Server Crashes?

Check the error messages in the terminal. Common issues:
- Database not running (start Docker: `docker-compose up -d`)
- Missing packages (install: `pip install -r requirements.txt`)
- API key issues (check your Gemini API key)

### Features Not Working?

- **Chat/QA not working:** Check server console for Gemini API errors
- **Search not working:** Check if local models loaded (look for "[OK] Semantic search model loaded")
- **Database errors:** Make sure PostgreSQL is running in Docker

---

## What Happens When You Close This Chat?

**Nothing!** The server continues running independently. It's just a Python script running on your computer.

---

## Daily Usage

1. **Start Docker** (if not already running):
   ```bash
   cd final_project
   docker-compose up -d
   ```

2. **Start Server:**
   ```bash
   python scripts\view_articles_hybrid_llm.py
   ```

3. **Use the Interface:**
   - Go to http://localhost:8002
   - Use Chat, QA, Search, etc.
   - Everything works independently!

4. **Stop Server** (when done):
   - Press Ctrl+C in terminal

---

## Pro Tips

### Run Server on Startup (Optional)

You can create a batch file to start the server automatically:

**`start_server.bat`:**
```batch
@echo off
cd C:\Users\erenb\PycharmProjects\pythonProject1\final_project
python scripts\view_articles_hybrid_llm.py
pause
```

Double-click the batch file to start the server!

### Run Server Automatically with Docker

You could also modify `docker-compose.yml` to include the Python server, but that's more advanced.

---

## Summary

✅ **Server runs completely independently**  
✅ **No AI assistant needed once started**  
✅ **Works until you stop it (Ctrl+C)**  
✅ **Can close browser, IDE, everything - server keeps running**  

Just start it once and use it whenever you want! 🚀


