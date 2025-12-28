# Hybrid LLM Interface - Quick Start

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install google-generativeai transformers accelerate
   ```

2. **Run the server:**
   ```bash
   python scripts/view_articles_hybrid_llm.py
   ```

3. **Open browser:**
   - Automatically opens at: http://localhost:8002
   - Or manually navigate to: http://localhost:8002

## 📍 Ports

- **8000:** Standard interface
- **8001:** LLM interface (semantic search)
- **8002:** **Hybrid LLM interface** ⭐ (this one)

## ✨ Features

### 1. Search Tab 🔍
- Semantic search using local embeddings
- Natural language queries
- Fast and accurate

### 2. Classify Tab 📋
- Zero-shot classification
- Classifies into CE areas and AI technologies
- Uses local BART model (free, fast)

### 3. Q&A Tab ❓
- Ask questions about articles
- Uses Gemini API
- Intelligent answers with sources

### 4. Chat Tab 💬
- Conversational chatbot
- Uses Gemini API
- Maintains conversation context

### 5. Insights Tab 💡
- Automated insight generation
- Uses Gemini API
- Data-driven insights

## 🔧 First Run

**Note:** First run will download models (~3.3 GB total):
- BART-large-MNLI (~1.6 GB) - for classification
- BART-large-CNN (~1.6 GB) - for summarization
- MiniLM-L6-v2 (~90 MB) - for search (may already be downloaded)

This takes 5-10 minutes depending on your internet speed.

## 💡 Example Queries

### Search:
- "AI in bridge construction"
- "Machine learning for structural monitoring"
- "Robotics in construction sites"

### Q&A:
- "Which CE area uses AI most?"
- "What are the main AI applications in transportation?"
- "Summarize AI trends in civil engineering"

### Chat:
- "Tell me about AI in construction"
- "What are the challenges in AI adoption?"
- "How can AI improve construction safety?"

## ⚡ Performance

- **CPU Mode:** 5-10 seconds per operation (classification/QA)
- **GPU Mode:** 1-2 seconds per operation (much faster)
- **Search:** Fast (< 1 second) - uses local embeddings
- **API Calls:** 1-3 seconds - depends on network

## 🎯 Comparison

| Feature | Standard | LLM | Hybrid LLM ⭐ |
|---------|----------|-----|---------------|
| Search | Keyword | Semantic | Semantic |
| Classification | Dictionary | - | Zero-shot |
| QA | - | - | ✓ Gemini |
| Chat | - | - | ✓ Gemini |
| Insights | - | - | ✓ Gemini |
| Cost | Free | Free | Free + API |

**Use Hybrid LLM (8002) for the most features!**

---

For detailed setup, see: `HYBRID_LLM_SETUP.md`


