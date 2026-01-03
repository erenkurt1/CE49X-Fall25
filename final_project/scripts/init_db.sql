-- Database initialization script for CE49X Final Project
-- This script runs automatically when the PostgreSQL container is first created

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    publication_date DATE,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    keywords TEXT,
    collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on URL for faster duplicate checking
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);

-- Create index on publication_date for temporal analysis
CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(publication_date);

-- Create index on source for source-based queries
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);

-- Create index on keywords for keyword-based queries
CREATE INDEX IF NOT EXISTS idx_articles_keywords ON articles(keywords);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_articles_updated_at 
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create a view for article statistics
CREATE OR REPLACE VIEW article_stats AS
SELECT 
    COUNT(*) as total_articles,
    COUNT(DISTINCT source) as unique_sources,
    MIN(publication_date) as earliest_date,
    MAX(publication_date) as latest_date,
    AVG(LENGTH(content)) as avg_content_length,
    COUNT(DISTINCT keywords) as unique_keyword_combinations
FROM articles;

-- Grant permissions (if needed for multiple users)
-- GRANT ALL PRIVILEGES ON TABLE articles TO ce49x_user;
-- GRANT ALL PRIVILEGES ON SEQUENCE articles_id_seq TO ce49x_user;





