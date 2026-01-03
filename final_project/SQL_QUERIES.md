# Useful SQL Queries for Your Database

## Basic Queries

### 1. See All Articles (Basic)
```sql
SELECT * FROM articles;
```

### 2. See All Articles (Limited - First 50)
```sql
SELECT * FROM articles 
ORDER BY id 
LIMIT 50;
```

### 3. See All Articles (With Content Preview)
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    LEFT(content, 200) as content_preview,
    url
FROM articles
ORDER BY publication_date DESC;
```

## Useful Queries

### 4. Count Total Articles
```sql
SELECT COUNT(*) as total_articles FROM articles;
```

### 5. Count Articles by Source
```sql
SELECT 
    source,
    COUNT(*) as article_count
FROM articles
GROUP BY source
ORDER BY article_count DESC;
```

### 6. Articles by Date (Most Recent First)
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    url
FROM articles
ORDER BY publication_date DESC
LIMIT 100;
```

### 7. Search Articles by Keyword in Title
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    url
FROM articles
WHERE title ILIKE '%AI%' OR title ILIKE '%machine learning%'
ORDER BY publication_date DESC;
```

### 8. Search Articles by Keyword in Content
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    LEFT(content, 300) as content_preview,
    url
FROM articles
WHERE content ILIKE '%structural engineering%'
ORDER BY publication_date DESC;
```

### 9. Articles from Specific Source
```sql
SELECT 
    id,
    title,
    publication_date,
    url
FROM articles
WHERE source = 'Engineering News-Record'
ORDER BY publication_date DESC;
```

### 10. Articles Published in Last 30 Days
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    url
FROM articles
WHERE publication_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY publication_date DESC;
```

### 11. Articles with Longest Content
```sql
SELECT 
    id,
    title,
    source,
    LENGTH(content) as content_length,
    publication_date
FROM articles
ORDER BY content_length DESC
LIMIT 20;
```

### 12. Unique Sources List
```sql
SELECT DISTINCT source
FROM articles
ORDER BY source;
```

### 13. Articles Statistics Summary
```sql
SELECT 
    COUNT(*) as total_articles,
    COUNT(DISTINCT source) as unique_sources,
    MIN(publication_date) as oldest_article,
    MAX(publication_date) as newest_article,
    AVG(LENGTH(content)) as avg_content_length
FROM articles;
```

### 14. Articles by Month
```sql
SELECT 
    DATE_TRUNC('month', publication_date) as month,
    COUNT(*) as article_count
FROM articles
GROUP BY month
ORDER BY month DESC;
```

### 15. Find Duplicate URLs (Should be 0 if unique constraint works)
```sql
SELECT url, COUNT(*) as count
FROM articles
GROUP BY url
HAVING COUNT(*) > 1;
```

## Advanced Queries

### 16. Full Article Details (One Article)
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    content,
    url,
    keywords
FROM articles
WHERE id = 1;  -- Change ID to see different article
```

### 17. Articles with Keywords Field
```sql
SELECT 
    id,
    title,
    source,
    keywords
FROM articles
WHERE keywords IS NOT NULL AND keywords != ''
ORDER BY id;
```

### 18. Search Multiple Terms
```sql
SELECT 
    id,
    title,
    source,
    publication_date,
    url
FROM articles
WHERE 
    title ILIKE '%AI%' 
    OR title ILIKE '%machine learning%'
    OR title ILIKE '%computer vision%'
ORDER BY publication_date DESC;
```

## Quick Reference

**Table Name**: `articles`

**Columns**:
- `id` - Primary key (auto-increment)
- `title` - Article title
- `publication_date` - Date article was published
- `source` - News source/publication name
- `content` - Full article content (text)
- `url` - Article URL (unique)
- `keywords` - Associated keywords (text)

**Common Patterns**:
- `ILIKE` - Case-insensitive search (PostgreSQL)
- `LEFT(content, 200)` - Get first 200 characters
- `LENGTH(content)` - Get content length
- `ORDER BY publication_date DESC` - Newest first
- `LIMIT 50` - Show only 50 results



