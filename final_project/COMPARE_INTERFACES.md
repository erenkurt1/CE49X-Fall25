# Compare Article Viewer Interfaces

## Two Interfaces Available

### 1. Standard Interface (Port 8000)
**URL:** http://localhost:8000

**Features:**
- ✅ Browse all articles
- ✅ Keyword search
- ✅ Sort by ID, date, or title
- ✅ Statistics dashboard
- ✅ Export to CSV
- ✅ Simple, fast interface

**Best for:**
- Quick browsing
- Known keywords
- Exporting data
- Simple searches

**Run:**
```bash
python scripts/view_articles_web.py
```

---

### 2. LLM-Powered Interface (Port 8001)
**URL:** http://localhost:8001

**Features:**
- ✅ Natural language search
- ✅ Semantic similarity matching
- ✅ Relevance scores (0-100%)
- ✅ Example queries
- ✅ AI-powered article discovery
- ✅ Understands context and meaning

**Best for:**
- Natural language queries
- Finding related articles
- Exploring topics
- Semantic understanding

**Run:**
```bash
python scripts/view_articles_llm.py
```

---

## Comparison

| Feature | Standard (8000) | LLM-Powered (8001) |
|---------|----------------|-------------------|
| **Search Type** | Keyword matching | Semantic similarity |
| **Query Style** | Exact keywords | Natural language |
| **Speed** | Very fast | Fast (with model loading) |
| **Relevance** | Exact matches | Contextual understanding |
| **Example** | "construction AI" | "articles about AI in bridge construction" |
| **Results** | All matching keywords | Most semantically similar |
| **Scores** | No | Yes (similarity %) |
| **Best Use** | Known terms | Exploring topics |

---

## How to Test Both

### Step 1: Start Standard Interface
```bash
python scripts/view_articles_web.py
```
Open: http://localhost:8000

### Step 2: Start LLM Interface (in new terminal)
```bash
python scripts/view_articles_llm.py
```
Open: http://localhost:8001

### Step 3: Compare

**Test Query 1:** "construction"
- Standard: Finds all articles with word "construction"
- LLM: Finds articles about construction, building, infrastructure, etc.

**Test Query 2:** "AI safety monitoring"
- Standard: Finds articles with "AI" AND "safety" AND "monitoring"
- LLM: Finds articles about AI safety, monitoring systems, automated safety checks, etc.

**Test Query 3:** "machine learning for bridges"
- Standard: May miss articles that say "ML" or "bridges" separately
- LLM: Finds articles about ML, bridges, structural analysis, etc.

---

## Installation for LLM Interface

If you get an error about missing packages:

```bash
pip install sentence-transformers torch
```

The first run will download the AI model (~90MB), which may take a minute.

---

## Recommendation

**Use Standard Interface (8000) if:**
- You know exact keywords
- You want fast, simple search
- You need to export data

**Use LLM Interface (8001) if:**
- You want to explore topics naturally
- You're looking for related concepts
- You want AI-powered discovery

**Best of Both Worlds:**
- Use LLM interface for discovery
- Use Standard interface for specific searches and exports

---

## Which One to Choose?

Try both and see which fits your workflow better!

1. **For quick searches:** Standard Interface
2. **For exploration:** LLM Interface
3. **For both:** Keep both running on different ports





