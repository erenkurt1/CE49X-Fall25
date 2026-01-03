# Hybrid LLM System Setup Guide

**New Enhanced Interface:** Port 8002  
**Combines:** Local models (HuggingFace) + Gemini API

---

## Features

✅ **Semantic Search** - Local sentence-transformers model  
✅ **Article Classification** - Zero-shot classification with BART  
✅ **Question Answering** - Gemini API  
✅ **Chatbot** - Conversational interface with Gemini  
✅ **Automated Insights** - Generate insights using Gemini  
✅ **Summarization** - Local BART model

---

## Installation

### Step 1: Install Required Packages

```bash
pip install google-generativeai transformers accelerate sentence-transformers
```

Or update from requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Download Models (Automatic)

The models will download automatically on first run:
- `facebook/bart-large-mnli` (classification) - ~1.6 GB
- `facebook/bart-large-cnn` (summarization) - ~1.6 GB
- `all-MiniLM-L6-v2` (search) - ~90 MB (already downloaded)

**Note:** First run may take 5-10 minutes to download models.

### Step 3: API Key Configuration

The Gemini API key is currently hardcoded in the script. For production, move it to `.env`:

1. Add to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

2. Update script to read from environment (optional):
```python
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
```

---

## Running the Interface

### Start the Server

```bash
cd final_project
python scripts/view_articles_hybrid_llm.py
```

The interface will open automatically at: **http://localhost:8002**

### Ports

- **Port 8000:** Standard interface (`view_articles_web.py`)
- **Port 8001:** LLM interface (`view_articles_llm.py`)  
- **Port 8002:** **Hybrid LLM interface** (this one) ⭐

---

## Usage Guide

### 1. Search Tab 🔍

- **Semantic Search:** Uses local embeddings for fast, accurate search
- Type natural language queries like:
  - "AI in bridge construction"
  - "Machine learning for structural health monitoring"
  - "Robotics in construction sites"

### 2. Classify Tab 📋

- **Zero-Shot Classification:** Classify articles into CE areas and AI technologies
- Paste article text
- Click "Classify Article"
- Get instant classification results

### 3. Q&A Tab ❓

- **Question Answering:** Ask questions about your articles
- Uses Gemini API for intelligent answers
- Example questions:
  - "Which CE area uses AI most?"
  - "What are the main applications of computer vision in construction?"
  - "Summarize the trends in AI adoption"

### 4. Chat Tab 💬

- **Conversational Chatbot:** Chat about AI in Civil Engineering
- Natural conversation flow
- Uses Gemini API
- Maintains conversation context

### 5. Insights Tab 💡

- **Automated Insights:** Generate insights from your data
- Analyzes statistics and trends
- Creates data-driven insights automatically
- Uses Gemini API

---

## Performance Notes

### Local Models

- **CPU:** Slower (5-10 seconds per classification)
- **GPU:** Much faster (1-2 seconds per classification)
- Models run entirely locally (privacy, no API costs)

### Gemini API

- **Speed:** Fast (1-3 seconds per request)
- **Cost:** Free tier available
- **Rate Limits:** Check Gemini API documentation

### Hybrid Approach Benefits

✅ **Fast Search:** Local embeddings (no API calls)  
✅ **Free Classification:** Local zero-shot model  
✅ **Intelligent QA:** Gemini for better understanding  
✅ **Cost Effective:** Only use API for interactive features  
✅ **Privacy:** Most processing stays local

---

## Troubleshooting

### Models Not Downloading

```bash
# Install with proper permissions
pip install --upgrade transformers accelerate

# Or download manually
python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='facebook/bart-large-mnli')"
```

### Gemini API Errors

- Check API key is correct
- Verify internet connection
- Check API quota/limits

### Out of Memory Errors

- Use smaller models
- Process articles in batches
- Use CPU instead of GPU (slower but less memory)

### Slow Performance

- **CPU Mode:** Expected (5-10 seconds per operation)
- **GPU Mode:** Install CUDA and PyTorch with GPU support
- **API Calls:** Network latency (~1-3 seconds)

---

## Model Information

### Local Models Used

1. **all-MiniLM-L6-v2** (Semantic Search)
   - Size: ~90 MB
   - Speed: Fast
   - Purpose: Embedding generation

2. **facebook/bart-large-mnli** (Classification)
   - Size: ~1.6 GB
   - Speed: Medium (CPU) / Fast (GPU)
   - Purpose: Zero-shot classification

3. **facebook/bart-large-cnn** (Summarization)
   - Size: ~1.6 GB
   - Speed: Medium (CPU) / Fast (GPU)
   - Purpose: Text summarization

### API Models Used

- **Gemini Pro:** For QA, chat, and insights
- Model: `gemini-pro`
- Provider: Google AI

---

## Next Steps

1. ✅ Start the server: `python scripts/view_articles_hybrid_llm.py`
2. ✅ Try each tab and feature
3. ✅ Compare with other interfaces (ports 8000, 8001)
4. ✅ Use the best interface for your needs

---

## Comparison with Other Interfaces

| Feature | Standard (8000) | LLM (8001) | Hybrid LLM (8002) ⭐ |
|---------|----------------|------------|---------------------|
| Search | Keyword | Semantic | Semantic |
| Classification | Dictionary | - | Zero-shot LLM |
| QA | - | - | Gemini API |
| Chat | - | - | Gemini API |
| Insights | - | - | Gemini API |
| Summarization | Basic | - | BART LLM |
| Cost | Free | Free | Free (local) + API (limited) |
| Speed | Fast | Fast | Medium-Fast |

**Recommendation:** Use Hybrid LLM (8002) for the most advanced features!

---

Enjoy your enhanced LLM-powered interface! 🚀





