# CE49X Final Project - Results & Progress Tracker

**Project:** Civil Engineering & AI Integration: Analyzing Industry Trends through News & Media  
**Course:** CE49X - Introduction to Data Science for Civil Engineering  
**Institution:** Boğaziçi University  
**Semester:** Fall 2025

---

## Project Status

- [ ] Task 1: Data Collection (30 points)
- [ ] Task 2: Text Preprocessing & NLP (25 points)
- [ ] Task 3: Categorization & Trend Analysis (30 points)
- [ ] Task 4: Visualization & Insights (15 points)

---

## Task 1: Data Collection - Results

### Database Information
- **Database Type:** PostgreSQL (Docker)
- **Container Name:** ce49x_postgres
- **Database Name:** ce49x_articles
- **Connection:** localhost:5432

### Collection Statistics
- **Total Articles Collected:** [To be updated after collection]
- **Collection Start Date:** [Date]
- **Collection End Date:** [Date]
- **Unique Sources:** [Number]
- **Date Range of Articles:** [Start Date] to [End Date]

### Data Sources Used

| Source | Method | Articles | Date Range | Notes |
|--------|--------|----------|------------|-------|
| NewsAPI | API | [Count] | [Range] | [Notes] |
| [Source 2] | [Method] | [Count] | [Range] | [Notes] |
| [Source 3] | [Method] | [Count] | [Range] | [Notes] |

### Search Queries Executed

| Query | Articles Found | Status |
|-------|----------------|--------|
| construction AND artificial intelligence | [Count] | ✓ |
| structural engineering AND machine learning | [Count] | ✓ |
| [Add more...] | | |

### Data Quality Metrics
- **Articles with all required fields:** [Number] / [Total]
- **Duplicate articles removed:** [Number]
- **Articles filtered (too short):** [Number]
- **Average article length:** [Number] words
- **Minimum article length:** [Number] words
- **Maximum article length:** [Number] words

### Database Queries

**Check article count:**
```sql
SELECT COUNT(*) FROM articles;
```

**View statistics:**
```sql
SELECT * FROM article_stats;
```

**Articles by source:**
```sql
SELECT source, COUNT(*) as count 
FROM articles 
GROUP BY source 
ORDER BY count DESC;
```

**Articles by date:**
```sql
SELECT DATE(publication_date) as date, COUNT(*) as count
FROM articles
WHERE publication_date IS NOT NULL
GROUP BY DATE(publication_date)
ORDER BY date DESC;
```

---

## Task 2: Text Preprocessing & NLP - Results

*[To be completed]*

### Preprocessing Statistics
- **Total articles processed:** [Number]
- **Average tokens per article:** [Number]
- **Top 20 most frequent words:** [List]
- **Top 20 bi-grams:** [List]

---

## Task 3: Categorization & Trend Analysis - Results

*[To be completed]*

### Classification Results

**Civil Engineering Areas:**
- Structural: [Count] articles
- Geotechnical: [Count] articles
- Transportation: [Count] articles
- Construction Management: [Count] articles
- Environmental Engineering: [Count] articles

**AI Technologies:**
- Computer Vision: [Count] articles
- Predictive Analytics: [Count] articles
- Generative Design: [Count] articles
- Robotics/Automation: [Count] articles

### Co-occurrence Matrix
*[Heatmap data to be added]*

---

## Task 4: Visualization & Insights - Results

*[To be completed]*

### Visualizations Created
- [ ] Bar Charts: Articles per Civil Engineering Area
- [ ] Network Graph: Term relationships
- [ ] Word Clouds: Per sub-discipline
- [ ] Heatmap: CE Area vs AI Technology

### Key Insights
*[To be completed]*

---

## Notes & Observations

### Challenges Encountered
- [List any challenges]

### Lessons Learned
- [List lessons learned]

### Future Improvements
- [List potential improvements]

---

## File Locations

### Data Files
- **Database:** PostgreSQL container `ce49x_postgres`
- **Backup exports:** `data/raw/` (if exported)

### Scripts
- **Data Collection:** `scripts/newsapi_collector.py`
- **Database Operations:** `scripts/database.py`
- **Preprocessing:** `scripts/` (Task 2)
- **Analysis:** `scripts/` (Task 3)
- **Visualization:** `scripts/` (Task 4)

### Documentation
- **Data Description:** `docs/data_description.md`
- **Final Report:** `docs/final_report.pdf` (to be created)

---

**Last Updated:** [Date]  
**Last Updated By:** [Your Name]





