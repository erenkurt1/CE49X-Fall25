# CE49X Final Project - AI in Civil Engineering Article Analysis System

## Overview

This project is a comprehensive system for collecting, analyzing, and exploring news articles about the intersection of Artificial Intelligence and Civil Engineering. The system uses PostgreSQL for data storage, Python for data processing, and provides multiple web interfaces for different use cases.

## System Architecture

### Main Components

1. **Data Collection**: Google News API integration for article collection
2. **Data Storage**: PostgreSQL database (Docker container)
3. **Data Processing**: NLP preprocessing, categorization, visualization
4. **Web Interfaces**: Multiple interfaces for different purposes

### Web Interfaces

- **localhost:8000/8001**: Basic article viewer (`view_articles_web.py`)
- **localhost:8002**: Hybrid LLM-powered interface (`view_articles_hybrid_llm.py`) ⭐ **Main Interface**
- **localhost:8003**: Article collector interface (`article_collector_web.py`)

---

## Localhost:8002 - Hybrid LLM-Powered Interface

### Purpose

The hybrid LLM interface (localhost:8002) is the main interface for exploring articles using advanced AI capabilities. It combines local machine learning models with cloud-based AI APIs to provide semantic search, intelligent summarization, and conversational interactions.

### Features

#### 1. Semantic Article Search
- **Technology**: Local sentence-transformers model (`all-MiniLM-L6-v2`)
- **Functionality**: 
  - Converts article text into vector embeddings
  - Performs semantic similarity search (not just keyword matching)
  - Understands meaning and context, not just exact words
  - Falls back to keyword search if embeddings fail

**Logic Behind Semantic Search:**
```
1. User enters a query (e.g., "AI in bridge construction")
2. System generates embeddings for all articles (cached for performance)
3. Query is converted to an embedding vector
4. Cosine similarity is calculated between query and all article embeddings
5. Top-K most similar articles are returned, ranked by similarity score
```

**Why This Works Better:**
- Traditional keyword search: Only finds articles with exact words
- Semantic search: Finds articles with similar meaning, even if they use different words
- Example: Query "machine learning in infrastructure" will find articles about "AI in construction" even if they don't contain the exact phrase

#### 2. Chatbot Interface
- **Technology**: Google Gemini API (`models/gemini-2.5-flash`)
- **Functionality**:
  - Conversational AI assistant
  - Maintains conversation history
  - Answers questions about AI in Civil Engineering
  - Context-aware responses

**Logic Behind Chatbot:**
```
1. User sends a message
2. System builds context: "You are an assistant for AI in Civil Engineering..."
3. Previous conversation history is included (last 5 messages)
4. Message is sent to Gemini API
5. Response is parsed and displayed
6. Conversation history is updated
```

**Why Gemini API:**
- Advanced language understanding
- Can answer complex questions
- Maintains context across conversation
- No need to train our own model

#### 3. Article Summarization
- **Technology**: Local BART model (`facebook/bart-large-cnn`)
- **Functionality**:
  - Generates concise summaries of articles
  - Uses extractive and abstractive summarization
  - Handles long articles by truncating to model limits

**Logic Behind Summarization:**
```
1. Article text is truncated to 1024 tokens (BART limit)
2. BART model processes the text
3. Generates summary with max_length=150 words
4. Returns human-readable summary
```

**Why Local Model:**
- No API costs
- Fast processing
- Privacy (data doesn't leave local machine)
- Works offline

### Technical Architecture

#### Frontend (HTML/CSS/JavaScript)
- **Design**: Modern slate gray theme (minimal and professional)
- **Layout**: Tab-based interface (Search and Chat tabs)
- **Real-time Updates**: JavaScript fetch API for async operations
- **Responsive**: Grid layout for article cards

#### Backend (Python HTTP Server)
- **Server**: Python's `http.server.HTTPServer`
- **Handler**: Custom `HybridLLMHandler` class
- **Endpoints**:
  - `GET /` - Main HTML page
  - `GET /api/articles` - Get all articles
  - `GET /api/stats` - Get database statistics
  - `POST /api/search` - Semantic search
  - `POST /api/chat` - Chat with Gemini
  - `POST /api/summarize` - Summarize article text

#### Data Flow

**Search Flow:**
```
User Query → JavaScript → POST /api/search
  ↓
Backend receives query
  ↓
Fetch all articles from database
  ↓
Generate embeddings (if not cached)
  ↓
Calculate semantic similarity
  ↓
Return top-K results with scores
  ↓
JavaScript displays results in grid
```

**Chat Flow:**
```
User Message → JavaScript → POST /api/chat
  ↓
Backend receives message + history
  ↓
Build prompt with context
  ↓
Call Gemini API
  ↓
Parse response
  ↓
Return to frontend
  ↓
Display in chat interface
```

### Model Caching Strategy

**Why Caching is Important:**
- Embedding generation is computationally expensive
- Models take time to load
- Reduces API calls (cost and latency)

**Implementation:**
```python
# Global cache variables
article_embeddings_cache = None
articles_data_cache = None
gemini_model_cache = None

# Check cache before generating embeddings
if article_embeddings_cache is not None and articles_data_cache == articles:
    return article_embeddings_cache, articles  # Use cached version
```

### Error Handling

**Robust Error Handling Strategy:**
1. **Database Errors**: Graceful fallback, clear error messages
2. **Model Loading Errors**: Falls back to keyword search
3. **API Errors**: Detailed error logging, user-friendly messages
4. **JSON Serialization**: Handles datetime, numpy types automatically

**Example:**
```python
try:
    embeddings = search_model.encode(texts)
    results = semantic_search(query, articles, embeddings)
except Exception as e:
    # Fallback to keyword search
    results = keyword_search(query, articles)
```

### Design Decisions

#### Why Hybrid Approach?
- **Local Models**: Fast, free, private (for search and summarization)
- **Cloud API**: Advanced capabilities (for chat and complex reasoning)
- **Best of Both Worlds**: Performance + Advanced Features

#### Why Remove Some Features?
- **Classify Tab**: Removed - was causing errors, not essential
- **QA Tab**: Removed - similar to chat, redundant
- **Insights Tab**: Removed - was unreliable
- **Result**: Simpler, more focused interface

#### Why Modern Slate Gray Design?
- Professional appearance
- Minimal and clean
- Good contrast for readability
- Modern aesthetic

### Database Integration

**Connection Management:**
```python
db = DatabaseManager()
if not db.connect():
    return error_response

try:
    articles = db.fetch_all_articles()
    # Process articles
finally:
    db.disconnect()  # Always close connection
```

**Data Conversion:**
- PostgreSQL returns `RealDictRow` objects
- Converted to standard Python dictionaries
- Dates converted to strings for JSON serialization
- Handles None values gracefully

### Performance Optimizations

1. **Embedding Caching**: Avoids regenerating embeddings on every search
2. **Model Caching**: Gemini model loaded once, reused
3. **Batch Processing**: Processes multiple articles at once
4. **Lazy Loading**: Models loaded only when needed
5. **Connection Pooling**: Database connections managed efficiently

### Security Considerations

1. **API Key Management**: 
   - Uses environment variables
   - No hardcoded keys in repository
   - `.env` files excluded from git

2. **Input Validation**:
   - Sanitizes user inputs
   - Prevents SQL injection (parameterized queries)
   - HTML escaping in frontend

3. **Error Messages**:
   - Don't expose sensitive information
   - User-friendly error messages
   - Detailed logging for debugging (server-side only)

### File Structure

```
final_project/
├── scripts/
│   ├── view_articles_hybrid_llm.py  # Main interface (localhost:8002)
│   ├── database.py                   # Database operations
│   ├── add_new_articles.py          # Article collection
│   └── ...
├── data/
│   ├── raw/                          # Raw collected articles
│   └── processed/                    # Processed data
├── visualizations/                   # Generated charts
└── README.md                         # Project documentation
```

### Key Technologies Used

1. **Python 3.x**: Main programming language
2. **PostgreSQL**: Database (via Docker)
3. **sentence-transformers**: Semantic search embeddings
4. **transformers (HuggingFace)**: BART summarization model
5. **google-generativeai**: Gemini API integration
6. **HTTP Server**: Built-in Python web server
7. **JavaScript**: Frontend interactivity

### Usage Instructions

1. **Start Database**: `docker-compose up -d`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Set API Key**: `export GEMINI_API_KEY=your_key`
4. **Run Server**: `python scripts/view_articles_hybrid_llm.py`
5. **Access Interface**: Open `http://localhost:8002`

### Future Improvements

1. **User Authentication**: Add login system
2. **Saved Searches**: Allow users to save favorite searches
3. **Export Functionality**: Export search results to CSV/PDF
4. **Advanced Filters**: Filter by date, source, category
5. **Real-time Updates**: WebSocket for live article updates
6. **Mobile Responsive**: Better mobile experience
7. **Dark Mode**: Theme toggle option

---

## Summary

The localhost:8002 interface represents a modern approach to article exploration, combining:
- **Local AI models** for fast, private semantic search
- **Cloud AI APIs** for advanced conversational capabilities
- **Clean, modern UI** for excellent user experience
- **Robust error handling** for reliability
- **Performance optimizations** for speed

The hybrid approach ensures we get the best of both worlds: the speed and privacy of local models, combined with the advanced capabilities of cloud-based AI services.

---

## Technical Details

### Embedding Generation
- Model: `all-MiniLM-L6-v2` (sentence-transformers)
- Dimensions: 384
- Method: Mean pooling of token embeddings
- Similarity: Cosine similarity

### Summarization
- Model: `facebook/bart-large-cnn`
- Max Input: 1024 tokens
- Max Output: 150 tokens
- Method: Abstractive summarization

### Chat
- API: Google Gemini 2.5 Flash
- Context Window: Maintains last 5 messages
- Response Format: Plain text
- Error Handling: Graceful fallback with user-friendly messages

---

*Documentation created: December 2024*
*Project: CE49X Final Project - AI in Civil Engineering*




