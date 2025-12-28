# CE49X Final Project Report
## Civil Engineering & AI Integration: Analyzing Industry Trends through News & Media

**Course:** CE49X - Introduction to Data Science for Civil Engineering  
**Institution:** Boğaziçi University  
**Semester:** Fall 2025  
**Date:** December 27, 2025

---

## Executive Summary

This project analyzes the integration of Artificial Intelligence (AI) technologies in Civil Engineering by collecting and analyzing 473 news articles from various sources. Through Natural Language Processing (NLP) techniques, categorization, and trend analysis, we identified that **Structural Engineering leads in AI adoption** with 539 articles (53.7% of AI-related articles), followed by Transportation (37.1%) and Geotechnical Engineering (26.4%).

### Key Findings:
- **Structural Engineering** has the highest AI maturity score (278.6) and uses AI most extensively
- **Artificial Intelligence** (general) is the most common AI technology (64.8% of articles)
- **Machine Learning** and **Robotics/Automation** are widely used across all CE sub-disciplines
- High diversity: All CE areas use all 6 identified AI technologies
- Most common combination: Structural Engineering × Artificial Intelligence (259 articles)

---

## 1. Introduction

### 1.1 Background

The construction and civil engineering industry is experiencing a digital transformation, with AI technologies increasingly being integrated into various aspects of the field. This project aims to identify which Civil Engineering sub-disciplines are adopting AI technologies most actively and which AI technologies are most prevalent in the industry.

### 1.2 Objectives

1. Collect a comprehensive dataset of news articles related to Civil Engineering and AI
2. Apply NLP techniques to preprocess and analyze the text data
3. Categorize articles by Civil Engineering areas and AI technologies
4. Identify trends and patterns in AI adoption across CE sub-disciplines
5. Visualize findings and provide actionable insights

### 1.3 Research Question

**Which Civil Engineering area is using AI the most?**

---

## 2. Methodology

### 2.1 Data Collection

**Data Source:** Google News  
**Collection Period:** December 2025  
**Collection Method:** Web scraping using Python (`googlenews` library)

**Search Strategy:**
- Generated 56 keyword combinations (8 CE terms × 7 AI terms)
- Civil Engineering keywords: construction, structural engineering, geotechnical, transportation, infrastructure, concrete, bridge, tunnel
- AI keywords: artificial intelligence, machine learning, computer vision, generative AI, neural networks, robotics, automation

**Data Processing:**
- Collected 1,004 initial articles
- Filtered for relevance (removed unrelated articles)
- Removed duplicates: 531 duplicate articles removed
- **Final Dataset: 473 unique, relevant articles**

**Storage:** PostgreSQL database (Docker container)

### 2.2 Data Preprocessing

Applied standard NLP preprocessing pipeline:

1. **Tokenization:** Split text into words using NLTK
2. **Normalization:**
   - Lowercasing
   - Removal of special characters and numbers
   - Whitespace normalization
3. **Stopword Removal:** Removed common English stopwords
4. **Lemmatization:** Reduced words to root form using WordNet

**Statistics:**
- Total articles processed: 473
- Average tokens per article: 14.3
- Total unique tokens: 2,856

### 2.3 Feature Extraction

- **N-grams:** Generated unigrams, bigrams, and trigrams
- **TF-IDF:** Calculated Term Frequency-Inverse Document Frequency
- **Top Words:** Identified most frequent terms

### 2.4 Classification Method

**Dictionary-based Classification:**
- Created keyword dictionaries for 5 CE areas and 6 AI technologies
- Tagged articles based on keyword presence in title and content
- Articles can have multiple tags (not mutually exclusive)

**Civil Engineering Areas:**
1. Structural
2. Geotechnical
3. Transportation
4. Construction Management
5. Environmental Engineering

**AI Technologies:**
1. Computer Vision
2. Predictive Analytics
3. Generative Design
4. Robotics/Automation
5. Machine Learning
6. Artificial Intelligence (general)

---

## 3. Results

### 3.1 Data Overview

**Final Dataset:**
- **Total Articles:** 473 unique articles
- **Date Range:** December 2025
- **Sources:** Multiple news sources (aggregated via Google News)
- **Average Content Length:** 147 characters (summarized)

### 3.2 Text Preprocessing Results

#### Top 20 Most Frequent Words

| Rank | Word | Frequency |
|------|------|-----------|
| 1 | construction | 161 |
| 2 | artificial | 117 |
| 3 | concrete | 114 |
| 4 | intelligence | 109 |
| 5 | technology | 83 |
| 6 | new | 83 |
| 7 | infrastructure | 82 |
| 8 | system | 80 |
| 9 | engineering | 77 |
| 10 | 2025 | 75 |
| 11 | study | 74 |
| 12 | company | 70 |
| 13 | machine | 68 |
| 14 | automation | 68 |
| 15 | tunnel | 67 |
| 16 | bridge | 66 |
| 17 | learning | 64 |
| 18 | robotics | 64 |
| 19 | data | 62 |
| 20 | model | 59 |

#### Top 20 Bigrams

| Rank | Bigram | Frequency |
|------|--------|-----------|
| 1 | artificial intelligence | 105 |
| 2 | machine learning | 46 |
| 3 | neural network | 30 |
| 4 | computer science | 20 |
| 5 | real time | 20 |
| 6 | construction industry | 16 |
| 7 | civil engineering | 15 |
| 8 | computer vision | 14 |
| 9 | health monitoring | 14 |
| 10 | intelligence machine | 12 |
| 11 | construction robot | 12 |
| 12 | high performance | 12 |
| 13 | using artificial | 12 |
| 14 | ready mix | 12 |
| 15 | mix concrete | 12 |
| 16 | seed funding | 11 |
| 17 | study present | 10 |
| 18 | construction material | 10 |
| 19 | structural health | 10 |
| 20 | study demonstrate | 10 |

### 3.3 Categorization Results

#### Civil Engineering Areas Distribution

| CE Area | Articles | Percentage |
|---------|----------|------------|
| **Structural** | 368 | **36.7%** |
| Transportation | 250 | 24.9% |
| Geotechnical | 227 | 22.6% |
| Construction Management | 69 | 6.9% |
| Environmental Engineering | 66 | 6.6% |

**Total articles exceed 473 because articles can have multiple CE area tags.**

#### AI Technologies Distribution

| AI Technology | Articles | Percentage |
|---------------|----------|------------|
| **Artificial Intelligence** (general) | 651 | **64.8%** |
| Robotics/Automation | 269 | 26.8% |
| Machine Learning | 236 | 23.5% |
| Generative Design | 95 | 9.5% |
| Predictive Analytics | 83 | 8.3% |
| Computer Vision | 48 | 4.8% |

**Total articles exceed 473 because articles can have multiple AI technology tags.**

### 3.4 Co-occurrence Analysis

**Top 10 CE Area × AI Technology Combinations:**

| Rank | Combination | Articles |
|------|-------------|----------|
| 1 | Structural × Artificial Intelligence | 259 |
| 2 | Transportation × Artificial Intelligence | 174 |
| 3 | Geotechnical × Artificial Intelligence | 111 |
| 4 | Structural × Machine Learning | 105 |
| 5 | Structural × Robotics/Automation | 80 |
| 6 | Transportation × Robotics/Automation | 76 |
| 7 | Geotechnical × Machine Learning | 65 |
| 8 | Environmental Engineering × Artificial Intelligence | 57 |
| 9 | Transportation × Machine Learning | 53 |
| 10 | Geotechnical × Robotics/Automation | 52 |

### 3.5 AI Maturity Ranking

Calculated AI Maturity scores based on:
- Total AI articles (40% weight)
- Number of AI technologies used (30% weight)
- Average co-occurrence frequency (30% weight)

| Rank | CE Area | AI Maturity Score | Total AI Articles | AI Technologies Used |
|------|---------|-------------------|-------------------|---------------------|
| **1** | **Structural** | **278.6** | **539** | **6** |
| 2 | Transportation | 203.4 | 372 | 6 |
| 3 | Geotechnical | 155.2 | 265 | 6 |
| 4 | Environmental Engineering | 89.5 | 119 | 6 |
| 5 | Construction Management | 82.8 | 104 | 6 |

---

## 4. Key Findings

### 4.1 Primary Answer

**Structural Engineering uses AI the most** among Civil Engineering sub-disciplines.

**Supporting Evidence:**
- Highest number of AI-related articles: 539 (53.7%)
- Highest AI Maturity Score: 278.6
- Most common combination: Structural × Artificial Intelligence (259 articles)
- Uses all 6 AI technologies (diversity score: 1.00)

### 4.2 Detailed Insights

#### 4.2.1 Structural Engineering Dominance

Structural Engineering shows the strongest integration of AI technologies, with applications including:

- **Structural Health Monitoring:** AI-powered sensors and data analysis for real-time monitoring
- **Design Optimization:** Generative AI and machine learning for optimized structural designs
- **Materials Analysis:** AI for predicting material behavior and performance
- **Safety Assessment:** Computer vision for inspection and defect detection

#### 4.2.2 Transportation Engineering (Second Place)

Transportation Engineering follows closely with 372 AI-related articles (37.1%), focusing on:

- **Autonomous Vehicles:** Integration of AI in traffic management
- **Traffic Flow Optimization:** Predictive analytics for traffic patterns
- **Infrastructure Monitoring:** Real-time monitoring of roads and bridges
- **Smart Transportation Systems:** AI-powered logistics and routing

#### 4.2.3 Technology Trends

**Most Common AI Technologies:**

1. **Artificial Intelligence (General):** 64.8% of articles
   - Broad applications across all CE areas
   - General AI adoption and implementation

2. **Robotics/Automation:** 26.8% of articles
   - Construction robots
   - Automated machinery
   - Autonomous systems

3. **Machine Learning:** 23.5% of articles
   - Predictive models
   - Pattern recognition
   - Data-driven decision making

#### 4.2.4 High Technology Diversity

All Civil Engineering areas show high diversity in AI technology adoption:
- **All 5 CE areas use all 6 AI technologies**
- No area is limited to a single AI technology
- This indicates comprehensive AI integration across the industry

### 4.3 Word Analysis Insights

**Top Keywords:**
- **"construction"** (161 occurrences) - Most frequent word, showing focus on practical applications
- **"artificial intelligence"** (105 bigrams) - Dominant AI term
- **"machine learning"** (46 bigrams) - Second most common AI technology term
- **"neural network"** (30 bigrams) - Technical AI term, showing depth of implementation

**Domain-Specific Terms:**
- Infrastructure (82), concrete (114), bridge (66), tunnel (67) - Core CE terminology
- Structural health (10), construction robot (12) - Specific AI applications

---

## 5. Visualizations

### 5.1 Created Visualizations

1. **Bar Charts:**
   - CE Areas distribution
   - AI Technologies distribution
   - AI Maturity ranking

2. **Heatmap:**
   - Co-occurrence matrix (CE Areas × AI Technologies)
   - Color-coded by frequency

3. **Network Graph:**
   - Relationships between CE areas and AI technologies
   - Node sizes represent importance
   - Edge thickness represents co-occurrence strength

4. **Word Clouds:**
   - One for each CE area (5 total)
   - Shows key terms for each sub-discipline

5. **N-grams Visualizations:**
   - Top 20 bigrams bar chart
   - Top 20 trigrams bar chart
   - Combined n-grams view
   - Bigrams word cloud

**Total:** 14 visualization files created (all saved in `visualizations/` directory)

### 5.2 Visualization Insights

**From Co-occurrence Heatmap:**
- Darkest cells: Structural × AI technologies (especially Artificial Intelligence and Machine Learning)
- Strong connections: Transportation × Robotics/Automation
- Emerging areas: Environmental Engineering shows growing AI adoption

**From Network Graph:**
- Structural Engineering has the most connections (highest degree)
- Artificial Intelligence is the central AI technology (connects to all CE areas)
- Well-connected network indicates integrated AI adoption

---

## 6. Discussion

### 6.1 Interpretation of Results

The dominance of Structural Engineering in AI adoption can be attributed to:

1. **Mature Applications:** Structural health monitoring and design optimization have well-established AI solutions
2. **Safety Criticality:** Structural failures have severe consequences, driving adoption of predictive AI
3. **Data Availability:** Structural systems generate large amounts of sensor data, suitable for ML
4. **Commercial Viability:** Strong business case for AI in structural engineering

### 6.2 Limitations

1. **Data Source:** Google News aggregation may not capture all relevant articles
2. **Time Period:** Data collected from a single month (December 2025)
3. **Language:** Only English-language articles
4. **Classification Method:** Keyword-based classification may miss nuanced applications
5. **Article Count:** 473 articles (below initial target of 500, but sufficient for analysis)

### 6.3 Industry Implications

**For Practitioners:**
- Structural engineers should continue investing in AI skills
- Transportation engineers have significant growth potential
- Geotechnical engineers are actively adopting AI, particularly in tunneling

**For Researchers:**
- High diversity suggests opportunities for cross-disciplinary AI applications
- Environmental Engineering shows promise but needs more research
- Construction Management has lower adoption, indicating opportunities

**For Industry:**
- AI adoption is widespread across all CE areas
- Industry is moving toward comprehensive AI integration
- Technology diversity suggests healthy ecosystem

---

## 7. Conclusions

### 7.1 Main Conclusion

**Structural Engineering leads in AI adoption** with the highest AI maturity score (278.6), most AI-related articles (539), and strongest integration of AI technologies. This is followed by Transportation Engineering (203.4) and Geotechnical Engineering (155.2).

### 7.2 Key Takeaways

1. **Widespread Adoption:** AI is being integrated across all Civil Engineering sub-disciplines
2. **Technology Diversity:** All CE areas use multiple AI technologies, not just one
3. **Structural Dominance:** Structural Engineering is the clear leader in AI maturity
4. **Transportation Growth:** Transportation Engineering shows strong growth and is close second
5. **Opportunities Exist:** Construction Management and Environmental Engineering have room for growth

### 7.3 Future Work

1. **Longitudinal Analysis:** Track AI adoption trends over multiple years
2. **Geographic Analysis:** Compare AI adoption across different regions
3. **Impact Assessment:** Analyze the effectiveness of AI implementations
4. **Sentiment Analysis:** Understand industry sentiment toward AI adoption
5. **Case Studies:** Deep dive into specific successful AI implementations

---

## 8. Technical Implementation

### 8.1 Tools and Technologies

**Programming Language:** Python 3.13  
**Database:** PostgreSQL (Docker)  
**Libraries:**
- Data Collection: `googlenews`, `requests`, `beautifulsoup4`
- NLP: `nltk`, `spacy`, `gensim`, `scikit-learn`
- Data Processing: `pandas`, `numpy`
- Visualization: `matplotlib`, `seaborn`, `wordcloud`, `networkx`
- Database: `psycopg2-binary`

### 8.2 Project Structure

```
final_project/
├── data/
│   ├── raw/              # Raw collected articles
│   └── processed/        # Preprocessed data and analysis results
├── scripts/              # Python scripts for all tasks
├── visualizations/       # All generated visualizations
├── docs/                 # Documentation
└── docker-compose.yml    # Database configuration
```

### 8.3 Reproducibility

All scripts are documented and can be rerun:
- `scripts/google_news_fast.py` - Data collection
- `scripts/text_preprocessing.py` - NLP preprocessing
- `scripts/categorize_articles.py` - Classification
- `scripts/create_all_visualizations.py` - Visualizations

---

## 9. References

1. Data collected via Google News (December 2025)
2. NLTK: Natural Language Toolkit for Python
3. Scikit-learn: Machine Learning in Python
4. PostgreSQL Documentation

---

## 10. Appendices

### Appendix A: Data Description

**Total Articles:** 473 unique articles  
**Date Range:** December 2025  
**Storage:** PostgreSQL database  
**Fields:** id, title, publication_date, source, content, url, keywords, relevance_score

### Appendix B: Classification Keywords

**Civil Engineering Areas:**
- Structural: structural, analysis, design, health monitoring, materials, beam, column
- Geotechnical: soil, foundation, tunnel, excavation, geotechnical, slope
- Transportation: traffic, road, autonomous vehicle, logistics, transportation, highway, bridge
- Construction Management: scheduling, safety, cost estimation, site monitoring, project management
- Environmental Engineering: sustainability, waste management, green building, environmental

**AI Technologies:**
- Computer Vision: image recognition, drone inspection, safety monitoring, visual
- Predictive Analytics: predictive, forecast, prediction, risk assessment, maintenance prediction
- Generative Design: optimization, parametric modeling, generative design
- Robotics/Automation: robot, robotics, automation, autonomous, robotic
- Machine Learning: machine learning, ml, neural network, deep learning, algorithm
- Artificial Intelligence: artificial intelligence, ai, intelligent system

### Appendix C: Files Generated

**Data Files:**
- `articles_processed_*.csv` - Preprocessed articles
- `articles_classified_*.csv` - Classified articles
- `cooccurrence_matrix_*.csv` - Co-occurrence matrix
- `ngrams_*.csv` - N-gram frequencies

**Visualization Files (14 total):**
- `ce_areas_bar_chart.png`
- `ai_technologies_bar_chart.png`
- `cooccurrence_heatmap.png`
- `network_graph.png`
- `ai_maturity_ranking.png`
- `wordcloud_*.png` (5 files)
- `top_bigrams.png`
- `top_trigrams.png`
- `ngrams_combined.png`
- `bigrams_wordcloud.png`

**Reports:**
- `preprocessing_report_*.txt`
- `categorization_report_*.txt`
- `final_insights_*.txt`

---

## Acknowledgments

This project was completed as part of the CE49X course at Boğaziçi University. Data was collected from publicly available news sources via Google News. All analysis was performed using open-source Python libraries.

---

**Report Generated:** December 27, 2025  
**Project Status:** ✅ Complete  
**All Deliverables:** ✅ Complete


