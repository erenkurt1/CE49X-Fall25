# Data Description Document

## Dataset Overview

- **Total Number of Articles:** [To be filled]
- **Collection Date Range:** [To be filled] (e.g., 2024-01-01 to 2024-12-01)
- **Date Range of Articles:** [To be filled] (e.g., 2023-06-01 to 2024-12-01)
- **Number of Unique Sources:** [To be filled]
- **Average Article Length:** [To be filled] words
- **Data Format:** [CSV/JSON/SQLite]

---

## Data Sources

### Source 1: [Source Name]

- **Website URL:** [URL]
- **Collection Method:** [API/Web Scraping/RSS Feed]
- **Number of Articles Collected:** [Number]
- **Date Range:** [Start Date] to [End Date]
- **Keywords/Queries Used:** [List of search queries]
- **Limitations/Notes:** 
  - [Any rate limits encountered]
  - [Any data quality issues]
  - [Any specific filters applied]

### Source 2: [Source Name]

[Repeat structure above for each source]

---

## Search Queries

### Keyword Combinations Used

| Civil Engineering Term | AI Term | Search Query | Articles Found |
|----------------------|---------|--------------|----------------|
| Construction | Artificial Intelligence | "construction AND artificial intelligence" | [Number] |
| Structural | Machine Learning | "structural engineering AND machine learning" | [Number] |
| [Add more rows...] | | | |

### Query Statistics

- **Total Queries Executed:** [Number]
- **Average Articles per Query:** [Number]
- **Most Successful Query:** [Query with most results]

---

## Data Structure

### Data Format: [CSV/JSON/SQLite]

#### Schema/Column Descriptions:

1. **title** (TEXT, REQUIRED)
   - Article title
   - Example: "AI Revolutionizes Bridge Inspection Methods"

2. **publication_date** (DATE/TEXT, REQUIRED)
   - Date when article was published
   - Format: YYYY-MM-DD or ISO 8601 format
   - Example: "2024-03-15"

3. **source** (TEXT, REQUIRED)
   - Name of the publisher/source
   - Example: "Engineering News-Record"

4. **content** (TEXT, REQUIRED)
   - Full text content of the article (or detailed abstract if full text unavailable)
   - Should be at least 200 words for meaningful analysis
   - Example: "Artificial intelligence is transforming..."

5. **url** (TEXT, REQUIRED, UNIQUE)
   - URL of the original article
   - Used for deduplication
   - Example: "https://example.com/article/123"

6. **keywords** (TEXT, OPTIONAL)
   - Search keywords that led to this article
   - Can be comma-separated if multiple
   - Example: "construction, artificial intelligence"

7. **collected_date** (TIMESTAMP, OPTIONAL)
   - Timestamp when article was collected
   - Format: YYYY-MM-DD HH:MM:SS

### Sample Data Entry

```json
{
  "title": "Machine Learning Predicts Concrete Strength with 95% Accuracy",
  "publication_date": "2024-11-20",
  "source": "Construction Dive",
  "content": "Researchers at MIT have developed a machine learning model that...",
  "url": "https://www.constructiondive.com/news/machine-learning-concrete/650123/",
  "keywords": "concrete, machine learning"
}
```

---

## Data Quality Assessment

### Completeness
- [ ] All required fields present in all articles
- [ ] Missing data percentage: [Percentage]
- **Missing Data Notes:** [Any patterns in missing data]

### Duplicates
- **Total Duplicates Found:** [Number]
- **Deduplication Method:** [Method used, e.g., "By URL", "By title similarity"]
- **Final Unique Articles:** [Number]

### Content Quality
- **Articles with < 200 words:** [Number]
- **Articles filtered out:** [Number]
- **Reason for filtering:** [e.g., "Too short", "Not relevant"]

### Source Distribution

| Source | Number of Articles | Percentage |
|--------|-------------------|------------|
| Source 1 | [Number] | [%] |
| Source 2 | [Number] | [%] |
| [Add more...] | | |

---

## Data Collection Timeline

- **Collection Start Date:** [Date]
- **Collection End Date:** [Date]
- **Total Collection Time:** [Days/Hours]
- **Collection Frequency:** [e.g., "Daily", "One-time batch"]

---

## Files and Storage

### Raw Data Files

1. **File:** `data/raw/articles_raw.csv`
   - **Format:** CSV
   - **Size:** [Size in MB/KB]
   - **Number of Rows:** [Number]
   - **Encoding:** UTF-8

2. **File:** `data/raw/articles_raw.json` (if applicable)
   - **Format:** JSON
   - **Size:** [Size in MB/KB]
   - **Number of Records:** [Number]

3. **File:** `data/raw/articles.db` (if applicable)
   - **Format:** SQLite Database
   - **Size:** [Size in MB/KB]
   - **Table Name:** articles
   - **Number of Records:** [Number]

### Backup Files
- Location: [Path]
- Last Backup: [Date]

---

## Notes and Observations

- **Challenges Encountered:**
  - [List any technical challenges, API limits, scraping difficulties, etc.]

- **Data Biases or Limitations:**
  - [Any known biases in the data, e.g., "Mostly English-language sources", "Recency bias towards recent articles"]

- **Future Improvements:**
  - [Suggestions for improving data collection in future iterations]

---

**Last Updated:** [Date]
**Prepared By:** [Your Name/Team Name]



