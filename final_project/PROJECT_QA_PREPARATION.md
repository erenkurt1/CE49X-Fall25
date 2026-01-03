# CE49X Final Project - Q&A Preparation Guide

**Project:** Civil Engineering & AI Integration: Analyzing Industry Trends through News & Media  
**Course:** CE49X - Introduction to Data Science for Civil Engineering  
**Institution:** Boğaziçi University  
**Semester:** Fall 2025

---

## Table of Contents

1. [Project Overview & Objectives](#1-project-overview--objectives)
2. [Data Collection Process & Methods](#2-data-collection-process--methods)
3. [Data Preprocessing & NLP Techniques](#3-data-preprocessing--nlp-techniques)
4. [Categorization & Analysis Methods](#4-categorization--analysis-methods)
5. [Visualization Methods](#5-visualization-methods)
6. [Technical Implementation](#6-technical-implementation)
7. [Key Definitions & Concepts](#7-key-definitions--concepts)
8. [Results & Findings](#8-results--findings)
9. [Challenges & Solutions](#9-challenges--solutions)
10. [Database & Storage](#10-database--storage)

---

## 1. Project Overview & Objectives

### Q1.1: What is the main objective of this project?

**Answer:**
The project aims to analyze the integration of Artificial Intelligence (AI) technologies in Civil Engineering by collecting and analyzing news articles. The main research question is: **"Which Civil Engineering area is using AI the most?"**

### Q1.2: What are the specific objectives?

**Answer:**
1. Collect a comprehensive dataset of news articles related to Civil Engineering and AI
2. Apply NLP techniques to preprocess and analyze the text data
3. Categorize articles by Civil Engineering areas and AI technologies
4. Identify trends and patterns in AI adoption across CE sub-disciplines
5. Visualize findings and provide actionable insights

### Q1.3: What is the scope of the project?

**Answer:**
- **Data Source:** Google News articles
- **Collection Period:** December 2025
- **Final Dataset:** 473 unique, relevant articles (after filtering and deduplication)
- **Civil Engineering Areas Analyzed:** 5 areas (Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering)
- **AI Technologies Analyzed:** 6 technologies (Artificial Intelligence, Machine Learning, Computer Vision, Generative Design, Predictive Analytics, Robotics/Automation)

---

## 2. Data Collection Process & Methods

### Q2.1: Why did you choose Google News over other sources?

**Answer:**
- Initially tried NewsAPI but encountered API key authentication issues
- Google News is free, publicly available, and doesn't require API keys
- Provides recent and diverse articles from multiple sources
- Accessible through web scraping using Python libraries

### Q2.2: How did you collect articles from Google News?

**Answer:**
1. **Search Strategy:** Generated 56 keyword combinations (8 CE terms × 7 AI terms)
   - CE keywords: construction, structural engineering, geotechnical, transportation, infrastructure, concrete, bridge, tunnel
   - AI keywords: artificial intelligence, machine learning, computer vision, generative AI, neural networks, robotics, automation

2. **Collection Method:** Used Python `googlenews` library for web scraping
3. **Speed Optimization:** Implemented a fast collector that:
   - Uses Google News descriptions only (no full content fetching)
   - Disables summarization during collection
   - Reduces delays between queries (0.5 seconds)
   - Increases results per query (15 articles)
   - Saves checkpoints every 100 articles

### Q2.3: How did you speed up the data collection process?

**Answer:**
Created `google_news_fast.py` with several optimizations:

1. **No Content Fetching:** Uses Google News descriptions only (~5-10 seconds saved per article)
2. **No Summarization:** Skips NLP processing during collection (~1-2 seconds saved per article)
3. **Reduced Delays:** Changed from 1-2 seconds to 0.5 seconds between queries
4. **Batch Processing:** Less frequent checkpoint saves (every 100 vs every 50)
5. **More Results Per Query:** Increased from 10 to 15 articles per query

**Performance:** ~2-5 articles/second vs ~0.5-1 article/second for regular collector

### Q2.4: How many articles did you collect initially, and how did you reduce this number?

**Answer:**
- **Initial Collection:** 1,004 articles after combining multiple batches
- **After Filtering:** Removed 45 unrelated articles (using keyword-based filtering)
- **After Deduplication:** Removed 531 duplicate articles (based on URL matching)
- **Final Dataset:** 473 unique, relevant articles

### Q2.5: How did you filter articles to ensure relevance?

**Answer:**
Implemented a multi-step filtering process:

1. **Must-Have Keywords:**
   - At least one Civil Engineering keyword (e.g., construction, structural, bridge)
   - At least one AI/ML keyword (e.g., artificial intelligence, machine learning)

2. **Exclusion Keywords:** Removed articles with:
   - Medical/healthcare terms (patient, disease, cancer, hospital)
   - Unrelated AI topics (data center, software, startup)
   - Finance/accounting terms (investment, stock, market)
   - Education/gaming terms

3. **Exclusion Phrases:** Removed articles with specific phrases like:
   - "data center construction" (usually tech infrastructure, not CE)
   - "construction of a model" (often about ML models, not buildings)

4. **Relevance Scoring:** Calculated scores (0-100) based on:
   - Number of CE keywords found
   - Number of AI keywords found
   - Presence of exclusion keywords (negative points)

### Q2.6: How did you handle duplicate articles?

**Answer:**
1. **URL Cleaning:** Removed Google News tracking parameters (`&ved=...&usg=...`) from URLs
2. **Duplicate Detection:** Identified duplicates by matching cleaned URLs
3. **Removal Strategy:** Kept the first occurrence (lowest ID), removed subsequent duplicates
4. **Result:** Removed 531 duplicate articles, leaving 473 unique articles

---

## 3. Data Preprocessing & NLP Techniques

### Q3.1: What is NLTK and why did you use it?

**Answer:**
**NLTK (Natural Language Toolkit)** is a Python library for Natural Language Processing. We used it for:
- **Tokenization:** Splitting text into individual words
- **Stopwords:** Lists of common words to remove (e.g., "the", "a", "is")
- **WordNet:** Dictionary for lemmatization (converting words to root form)
- **Corpora:** Pre-built language data and resources

### Q3.2: What preprocessing steps did you apply? Explain each step.

**Answer:**

#### Step 1: Normalization
**What it is:** Standardizing text to a consistent format.

**Steps:**
- **Lowercasing:** Convert all text to lowercase ("AI" → "ai")
- **Remove Special Characters:** Remove punctuation, numbers, URLs, emails
- **Clean Whitespace:** Remove extra spaces

**Example:**
```
Input: "AI (2025) is transforming construction!"
Output: "ai is transforming construction"
```

**Why:** Ensures consistent matching (e.g., "AI" = "ai" = "Ai")

#### Step 2: Tokenization
**What it is:** Splitting text into individual words (tokens).

**How:** Used NLTK's `word_tokenize()` function.

**Example:**
```
Input: "AI in construction"
Output: ['AI', 'in', 'construction']
```

**Why:** Enables word-by-word analysis and processing.

#### Step 3: Stopword Removal
**What it is:** Removing common words with little meaning.

**Common stopwords:** "the", "a", "is", "in", "at", "and", "or", "but"

**Example:**
```
Before: ["AI", "is", "transforming", "the", "construction"]
After:  ["AI", "transforming", "construction"]
```

**Why:**
- "the" appears everywhere but isn't informative
- Focus on domain-specific terms like "construction" and "AI"
- Reduces noise in analysis

#### Step 4: Lemmatization
**What it is:** Converting words to their base/root form.

**Examples:**
- "machines" → "machine"
- "running" → "run"
- "better" → "good"

**Why:**
- Groups word variants together
- "machine", "machines", "machinery" → all become "machine"
- More accurate frequency counts

**Lemmatization vs Stemming:**
- **Lemmatization:** Returns real words (more accurate, slower)
- **Stemming:** May return non-words like "runn" (faster but less accurate)
- **We used lemmatization** for better accuracy

### Q3.3: What is normalization in NLP?

**Answer:**
Normalization is the process of converting text to a standardized format. It includes:
- **Lowercasing:** All text converted to lowercase
- **Removing special characters:** Punctuation, numbers, URLs removed
- **Whitespace normalization:** Extra spaces removed
- **Character encoding:** Handling Unicode characters

**Purpose:** Ensures consistent text representation for analysis.

### Q3.4: What are N-grams and why are they important?

**Answer:**
**N-grams** are sequences of N consecutive words from text.

**Types:**
- **Unigrams (1-grams):** Single words → ["ai", "construction"]
- **Bigrams (2-grams):** Word pairs → ["artificial intelligence", "machine learning"]
- **Trigrams (3-grams):** Three words → ["artificial intelligence machine"]

**Why Important:**
- Captures phrases and multi-word concepts
- "artificial intelligence" together is more meaningful than separate words
- Helps identify common phrases and terminology

**Example from our data:**
- Top bigram: "artificial intelligence" (46 occurrences)
- Top trigram: "construction management ai"

### Q3.5: What is TF-IDF?

**Answer:**
**TF-IDF (Term Frequency-Inverse Document Frequency)** is a numerical statistic that reflects how important a word is to a document in a collection of documents.

**Components:**
- **TF (Term Frequency):** How often a word appears in a document
- **IDF (Inverse Document Frequency):** How rare a word is across all documents
- **TF-IDF = TF × IDF:** High score = important, unique word

**Purpose:**
- Identifies keywords that distinguish articles
- Filters out common words (they have low TF-IDF)
- Used for feature extraction and document ranking

**Example:**
- Word "construction" appears frequently → High TF
- Word "the" appears in all documents → Low IDF
- "construction" has high TF-IDF = important keyword
- "the" has low TF-IDF = not important

### Q3.6: What preprocessing statistics did you get?

**Answer:**
- **Total articles processed:** 473
- **Average tokens per article:** 14.3 words (after preprocessing)
- **Total unique tokens:** 2,856 words
- **Top word:** "construction" (66 occurrences)
- **Top bigram:** "artificial intelligence" (46 occurrences)
- **Top trigram:** Related to "construction management ai"

---

## 4. Categorization & Analysis Methods

### Q4.1: How did you categorize articles into CE areas and AI technologies?

**Answer:**
Used **dictionary-based classification** with keyword matching:

1. **Created Keyword Dictionaries:**
   - 5 CE area dictionaries (Structural, Geotechnical, Transportation, Construction Management, Environmental Engineering)
   - 6 AI technology dictionaries (AI, ML, Computer Vision, Generative Design, Predictive Analytics, Robotics/Automation)

2. **Classification Process:**
   - For each article, searched for keywords in title and content
   - Counted matching keywords for each category
   - Assigned categories if at least one keyword matched
   - Articles can have multiple categories (not mutually exclusive)

3. **Scoring:**
   - Calculated match scores (number of keywords found)
   - Categories with scores > 0 were assigned to the article

### Q4.2: Why did you use dictionary-based classification instead of machine learning?

**Answer:**
- **Transparency:** Easy to understand and explain
- **Interpretability:** Can see exactly which keywords led to classification
- **No Training Data Needed:** Works immediately without labeled training data
- **Domain-Specific:** Uses domain knowledge (CE and AI terminology)
- **Fast:** Quick to implement and execute
- **Multiple Labels:** Easily handles articles with multiple categories

**Limitations:**
- May miss articles that don't use exact keywords
- Requires manual keyword selection
- Less flexible than ML models

### Q4.3: What is a co-occurrence matrix?

**Answer:**
A **co-occurrence matrix** shows how often two categories appear together in articles.

**Structure:**
- Rows: Civil Engineering areas
- Columns: AI technologies
- Values: Number of articles that belong to both categories

**Example:**
```
                    AI    ML    Computer Vision
Structural         259   187    45
Transportation     175   132    38
```

**Interpretation:**
- 259 articles are about Structural Engineering AND Artificial Intelligence
- 175 articles are about Transportation AND Artificial Intelligence

**Purpose:**
- Identifies which CE areas use which AI technologies most
- Shows relationships and patterns
- Visualized as a heatmap for easy interpretation

### Q4.4: How did you calculate AI maturity scores?

**Answer:**
**AI Maturity Score** = Sum of (Number of articles × Number of AI technologies used)

**Calculation:**
1. For each CE area, count articles
2. For each article, count number of AI technologies assigned
3. Multiply: article_count × avg_ai_technologies_per_article
4. Sum across all articles in that CE area

**Example:**
- Structural Engineering: 254 articles
- Average AI technologies per article: 1.097
- Maturity Score: 254 × 1.097 = 278.6

**Interpretation:**
- Higher score = more AI adoption
- Considers both number of articles and diversity of AI technologies

---

## 5. Visualization Methods

### Q5.1: What visualizations did you create?

**Answer:**
1. **Bar Charts:**
   - CE Areas distribution (horizontal bar chart)
   - AI Technologies distribution (horizontal bar chart)
   - N-grams (bigrams and trigrams)

2. **Word Clouds:**
   - One for each CE area (5 total)
   - Shows most frequent words in that area

3. **Network Graph:**
   - Nodes: CE areas and AI technologies
   - Edges: Connections between them (thickness = strength)
   - Shows relationships between categories

4. **Heatmap:**
   - Co-occurrence matrix visualization
   - Color intensity = number of articles
   - Shows which combinations are most common

5. **AI Maturity Ranking:**
   - Bar chart showing AI maturity scores for each CE area
   - Ranks areas by AI adoption level

### Q5.2: Why did you choose these visualization types?

**Answer:**
- **Bar Charts:** Easy to compare counts and percentages
- **Word Clouds:** Visual representation of frequent terms, intuitive
- **Network Graphs:** Shows complex relationships between multiple categories
- **Heatmaps:** Effective for showing 2D relationships (CE areas × AI technologies)
- **Maturity Ranking:** Clear comparison of adoption levels

### Q5.3: What libraries did you use for visualization?

**Answer:**
- **Matplotlib:** Basic plotting and figure creation
- **Seaborn:** Statistical visualizations (heatmaps, styled plots)
- **WordCloud:** Word cloud generation
- **NetworkX:** Network graph creation and layout algorithms

---

## 6. Technical Implementation

### Q6.1: What technologies and libraries did you use?

**Answer:**

**Core Python Libraries:**
- **pandas:** Data manipulation and analysis
- **numpy:** Numerical computations
- **requests, BeautifulSoup:** Web scraping
- **googlenews:** Google News API wrapper

**NLP Libraries:**
- **nltk:** Tokenization, stopwords, lemmatization
- **sklearn (TfidfVectorizer):** TF-IDF calculation

**Visualization:**
- **matplotlib, seaborn:** Plotting
- **wordcloud:** Word clouds
- **networkx:** Network graphs

**Database:**
- **psycopg2:** PostgreSQL connection
- **Docker:** Containerization

**Web Interface:**
- **Flask:** Web application framework
- **sentence-transformers:** Semantic search (LLM-powered interface)

### Q6.2: How did you store data?

**Answer:**
1. **CSV Files:** Initial storage for review before database upload
2. **PostgreSQL Database:** Final structured storage in Docker container

**Database Schema:**
- Table: `articles`
- Columns: id, title, publication_date, source, content, url, keywords, relevance_score, filter_reason, created_at

### Q6.3: Why did you use Docker and PostgreSQL?

**Answer:**
- **Docker:** Easy setup, reproducible environment, isolated from system
- **PostgreSQL:** 
  - Robust relational database
  - Good for structured data
  - Supports SQL queries for analysis
  - Reliable data storage
  - Easy to integrate with Python (psycopg2)

### Q6.4: What web interfaces did you create?

**Answer:**
1. **Standard Interface (`view_articles_web.py`):**
   - Simple article browser
   - Search and filter by title/keywords
   - Sort by date, relevance
   - View article details

2. **LLM-Powered Interface (`view_articles_llm.py`):**
   - Semantic search using sentence transformers
   - Natural language queries (e.g., "articles about bridge safety")
   - Uses embeddings to find semantically similar articles
   - Shows relevance scores

**Difference:**
- Standard: Keyword-based search (exact matches)
- LLM: Semantic search (understands meaning)

### Q6.5: How does semantic search work?

**Answer:**
1. **Embeddings:** Convert articles and queries to numerical vectors using `sentence-transformers` (all-MiniLM-L6-v2 model)
2. **Similarity Calculation:** Compute cosine similarity between query embedding and article embeddings
3. **Ranking:** Sort articles by similarity score
4. **Return:** Top-K most similar articles

**Advantages:**
- Understands meaning, not just keywords
- Finds related articles even if they don't use exact search terms
- More intuitive for users

---

## 7. Key Definitions & Concepts

### Q7.1: Define the following NLP terms:

**Tokenization:**
Breaking text into individual words or tokens. Example: "AI in construction" → ["AI", "in", "construction"]

**Normalization:**
Standardizing text format (lowercase, remove punctuation, etc.) for consistent processing.

**Stopwords:**
Common words with little meaning (e.g., "the", "a", "is"). Usually removed to focus on important terms.

**Lemmatization:**
Converting words to their base/root form. Example: "machines" → "machine", "running" → "run"

**Stemming:**
Similar to lemmatization but may produce non-words. Example: "running" → "runn"

**N-grams:**
Sequences of N consecutive words. Unigrams (1), bigrams (2), trigrams (3).

**TF-IDF:**
Term Frequency-Inverse Document Frequency. Measures word importance in documents.

**Embeddings:**
Numerical vector representations of text that capture semantic meaning.

### Q7.2: What is Natural Language Processing (NLP)?

**Answer:**
NLP is a field of AI that focuses on enabling computers to understand, interpret, and generate human language. It involves:
- Text preprocessing (tokenization, normalization)
- Feature extraction (TF-IDF, embeddings)
- Text classification and analysis
- Language understanding

### Q7.3: What is a corpus?

**Answer:**
A **corpus** (plural: corpora) is a large collection of text documents used for linguistic research or NLP analysis. In our project, the corpus is the collection of 473 news articles.

### Q7.4: What is feature extraction in NLP?

**Answer:**
Feature extraction is converting text into numerical representations that can be used by machine learning algorithms. Methods include:
- **N-grams:** Word/phrase frequencies
- **TF-IDF:** Term importance scores
- **Embeddings:** Dense vector representations
- **Bag of Words:** Simple word counts

---

## 8. Results & Findings

### Q8.1: What were your main findings?

**Answer:**

1. **Structural Engineering leads in AI adoption:**
   - Highest AI maturity score (278.6)
   - 254 articles (53.7% of total)
   - Uses all 6 AI technologies extensively

2. **Artificial Intelligence (general) is most common:**
   - 307 articles (64.8%)
   - Most widely used AI technology across all CE areas

3. **High diversity:**
   - All CE areas use all 6 AI technologies
   - No single dominant combination

4. **Most common combination:**
   - Structural Engineering × Artificial Intelligence (259 articles)

### Q8.2: Which CE area has the highest AI maturity?

**Answer:**
**Structural Engineering** with a maturity score of 278.6, followed by:
1. Structural Engineering: 278.6
2. Transportation: 192.2
3. Geotechnical: 125.0
4. Construction Management: 124.9
5. Environmental Engineering: 56.7

### Q8.3: What are the most common AI technologies used?

**Answer:**
1. **Artificial Intelligence (general):** 307 articles (64.8%)
2. **Machine Learning:** 239 articles (50.5%)
3. **Robotics/Automation:** 185 articles (39.1%)
4. **Predictive Analytics:** 142 articles (30.0%)
5. **Computer Vision:** 98 articles (20.7%)
6. **Generative Design:** 87 articles (18.4%)

### Q8.4: How many articles did you analyze?

**Answer:**
- **Final Dataset:** 473 unique, relevant articles
- **After Filtering:** Removed 45 unrelated articles
- **After Deduplication:** Removed 531 duplicate articles
- **Initially Collected:** 1,004 articles

---

## 9. Challenges & Solutions

### Q9.1: What challenges did you face during data collection?

**Answer:**

**Challenge 1: NewsAPI Key Issues**
- Problem: API key authentication failures
- Solution: Switched to Google News scraping (no API key needed)

**Challenge 2: Slow Collection Speed**
- Problem: Collecting full articles and summarizing was slow (~10-20 min for 500 articles)
- Solution: Created fast collector that:
  - Uses descriptions only
  - Skips summarization
  - Reduces delays
  - Gets more results per query
- Result: 5-10x faster (~2-5 min for 500 articles)

**Challenge 3: HTTP 429 (Too Many Requests)**
- Problem: Google News rate limiting
- Solution: Added delays between queries, reduced request frequency

**Challenge 4: Unrelated Articles**
- Problem: Many articles not relevant to CE + AI
- Solution: Implemented keyword-based filtering with exclusion lists

**Challenge 5: Duplicate Articles**
- Problem: Same articles appeared multiple times with different URLs (Google News tracking parameters)
- Solution: 
  - Cleaned URLs (removed tracking parameters)
  - Identified duplicates based on cleaned URLs
  - Removed duplicates, keeping first occurrence

### Q9.2: What challenges did you face during preprocessing?

**Answer:**

**Challenge 1: NLTK Data Downloads**
- Problem: Missing NLTK resources (punkt, stopwords, wordnet)
- Solution: Added automatic download checks in preprocessing script

**Challenge 2: POS Tagger Availability**
- Problem: Large resource, sometimes unavailable
- Solution: Made POS tagging optional with fallback to simple lemmatization

**Challenge 3: Text Encoding Issues**
- Problem: Unicode characters causing encoding errors
- Solution: Used UTF-8 encoding consistently

### Q9.3: What challenges did you face during analysis?

**Answer:**

**Challenge 1: Multiple Categories Per Article**
- Problem: Articles can belong to multiple CE areas and AI technologies
- Solution: Used non-exclusive classification (articles can have multiple tags)

**Challenge 2: Data Quality**
- Problem: Some articles had missing or low-quality content
- Solution: Filtered during collection, handled missing values in preprocessing

**Challenge 3: URL Issues in Web Interface**
- Problem: Google News tracking parameters caused "page not found" errors
- Solution: Implemented URL cleaning (client-side and server-side)

---

## 10. Database & Storage

### Q10.1: How did you set up the database?

**Answer:**
1. **Docker Compose:** Created `docker-compose.yml` with PostgreSQL service
2. **Database Schema:** Created `init_db.sql` with articles table structure
3. **Connection Module:** Created `database.py` with DatabaseManager class
4. **Initialization:** Ran `docker-compose up -d` to start container
5. **Connection:** Used environment variables for credentials (.env file)

### Q10.2: What is the database schema?

**Answer:**
Table: `articles`

Columns:
- `id`: Primary key (SERIAL)
- `title`: Article title (VARCHAR)
- `publication_date`: Publication date (DATE)
- `source`: News source (VARCHAR)
- `content`: Article content/summary (TEXT)
- `url`: Article URL (VARCHAR, UNIQUE)
- `keywords`: Search keywords used (TEXT)
- `relevance_score`: Relevance score (0-100) (NUMERIC)
- `filter_reason`: Reason for filtering (VARCHAR)
- `created_at`: Timestamp (TIMESTAMP)

### Q10.3: How did you handle data quality in the database?

**Answer:**
1. **Unique Constraint:** URLs must be unique (prevents exact duplicates)
2. **URL Cleaning:** Removed tracking parameters before insertion
3. **Deduplication:** Identified and removed duplicates based on cleaned URLs
4. **Filtering:** Only relevant articles were uploaded
5. **Validation:** Checked data before insertion (non-null titles, valid URLs)

---

## Quick Reference: Key Numbers

- **Final Dataset:** 473 articles
- **Initial Collection:** 1,004 articles
- **Duplicates Removed:** 531
- **Filtered Out:** 45 unrelated articles
- **CE Areas:** 5 (Structural, Geotechnical, Transportation, Construction Management, Environmental)
- **AI Technologies:** 6 (AI, ML, Computer Vision, Generative Design, Predictive Analytics, Robotics/Automation)
- **Keyword Combinations:** 56 (8 CE × 7 AI)
- **Average Tokens per Article:** 14.3
- **Unique Tokens:** 2,856
- **Top CE Area:** Structural Engineering (254 articles, 53.7%)
- **Top AI Technology:** Artificial Intelligence (307 articles, 64.8%)
- **Highest Maturity Score:** Structural Engineering (278.6)

---

## Tips for Answering Questions

1. **Be Specific:** Use actual numbers from your results
2. **Explain Why:** Always explain the reasoning behind your choices
3. **Show Understanding:** Demonstrate you understand the concepts, not just memorized answers
4. **Mention Challenges:** Discuss challenges you faced and how you solved them
5. **Reference Code:** If asked about implementation, reference specific scripts/files
6. **Discuss Trade-offs:** Explain advantages and limitations of your methods

---

## Common Follow-up Questions

### "Why didn't you use machine learning for classification?"

**Answer:** We used dictionary-based classification because:
- Transparent and interpretable
- No training data needed
- Fast to implement
- Works well with domain-specific keywords
- Articles can have multiple categories easily

### "How would you improve this project?"

**Answer:**
- Collect more articles for better coverage
- Use machine learning for classification (with labeled data)
- Add temporal analysis (trends over time)
- Implement sentiment analysis
- Add more visualization types
- Improve semantic search with larger models

### "What are the limitations of your approach?"

**Answer:**
- Dictionary-based classification may miss articles without exact keywords
- Limited to recent articles (Google News)
- May have language bias (English only)
- Manual keyword selection required
- No temporal analysis
- Limited to news articles (may miss academic papers)

---

**Good luck with your presentation and questions!** 🚀





