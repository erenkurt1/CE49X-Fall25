"""
Simplified Google News Collector using googlenews library
Easier and more reliable than web scraping
"""

import os
import sys
import pandas as pd
from datetime import datetime
import time

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from article_summarizer import summarize_article

try:
    from GoogleNews import GoogleNews
    GOOGLENEWS_AVAILABLE = True
except ImportError:
    GOOGLENEWS_AVAILABLE = False
    print("Warning: googlenews library not installed.")
    print("Install with: pip install googlenews")

# Summarization settings
SUMMARIZE_ARTICLES = True
SUMMARY_METHOD = 'simple'  # Use simple for faster processing
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_LENGTH = 500

# Define keyword combinations
CIVIL_ENG_KEYWORDS = [
    "construction", "structural engineering", "geotechnical", 
    "transportation", "infrastructure", "concrete", "bridge", "tunnel"
]

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "computer vision",
    "generative AI", "neural networks", "robotics", "automation"
]

def create_search_queries():
    """Generate search query combinations"""
    queries = []
    for ce_term in CIVIL_ENG_KEYWORDS:
        for ai_term in AI_KEYWORDS:
            queries.append(f"{ce_term} {ai_term}")
    return queries

def fetch_articles_with_googlenews(query, max_results=10):
    """
    Fetch articles using googlenews library
    
    Args:
        query: Search query string
        max_results: Maximum number of results
    
    Returns:
        List of article dictionaries
    """
    if not GOOGLENEWS_AVAILABLE:
        return []
    
    articles = []
    
    try:
        googlenews = GoogleNews(lang='en', region='US')
        googlenews.search(query)
        results = googlenews.results()
        
        for result in results[:max_results]:
            article = {
                'title': result.get('title', ''),
                'url': result.get('link', '') or result.get('url', ''),
                'source': result.get('source', 'Unknown'),
                'publication_date': result.get('date', ''),
                'description': result.get('desc', '') or result.get('description', ''),
            }
            articles.append(article)
        
        googlenews.clear()
        
    except Exception as e:
        print(f"  Exception: {str(e)}")
    
    return articles

def extract_article_data(article, keyword_query=""):
    """
    Extract and process article data
    
    Returns:
        Dictionary with article fields
    """
    # Get content (use description as content)
    content = article.get('description', '') or article.get('content', '')
    
    # Summarize if enabled
    original_content = content.strip()
    if SUMMARIZE_ARTICLES and original_content:
        try:
            content = summarize_article(
                original_content,
                method=SUMMARY_METHOD,
                max_sentences=MAX_SUMMARY_SENTENCES,
                max_length=MAX_SUMMARY_LENGTH
            )
        except:
            content = original_content
    
    # Parse date
    pub_date = article.get('publication_date')
    if pub_date:
        try:
            # Try to parse date string
            from dateutil import parser
            pub_date = parser.parse(pub_date).date()
        except:
            pub_date = datetime.now().date()
    else:
        pub_date = datetime.now().date()
    
    return {
        'title': article.get('title', '').strip(),
        'publication_date': pub_date,
        'source': article.get('source', 'Google News'),
        'content': content.strip(),
        'url': article.get('url', ''),
        'keywords': keyword_query,
        'content_length': len(content),
        'original_length': len(original_content) if SUMMARIZE_ARTICLES else len(content)
    }

def validate_article(article):
    """Validate article"""
    if not article.get('title'):
        return False, "Missing title"
    if not article.get('url'):
        return False, "Missing URL"
    content = article.get('content', '')
    if not content or len(content.split()) < 15:
        return False, "Content too short"
    return True, "Valid"

def save_to_csv(articles, filename):
    """Save articles to CSV"""
    if not articles:
        return
    
    df = pd.DataFrame(articles)
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Saved {len(articles)} articles to {filename}")

def main():
    """Main collection function"""
    if not GOOGLENEWS_AVAILABLE:
        print("Please install googlenews: pip install googlenews")
        return
    
    print("=" * 60)
    print("CE49X Final Project - Google News Collector")
    print("Using googlenews library")
    print("=" * 60)
    print()
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    queries = create_search_queries()
    print(f"Generated {len(queries)} search queries")
    print("Starting collection...\n")
    
    all_articles = []
    seen_urls = set()
    total_valid = 0
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Query: {query}")
        
        articles = fetch_articles_with_googlenews(query, max_results=15)  # Increased for more articles
        
        for article in articles:
            if article.get('url') in seen_urls:
                continue
            
            article_data = extract_article_data(article, query)
            
            is_valid, _ = validate_article(article_data)
            if not is_valid:
                continue
            
            seen_urls.add(article_data['url'])
            all_articles.append(article_data)
            total_valid += 1
        
        print(f"  Found: {len(articles)}, Total collected: {total_valid}")
        
        time.sleep(0.5)  # Reduced delay for faster collection
        
        if i % 10 == 0 and all_articles:
            checkpoint = os.path.join(data_dir, f'articles_checkpoint_{len(all_articles)}.csv')
            save_to_csv(all_articles, checkpoint)
    
    # Final save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(data_dir, f'articles_google_news_{timestamp}.csv')
    save_to_csv(all_articles, csv_file)
    
    print("\n" + "=" * 60)
    print(f"Collection complete!")
    print(f"Total articles: {total_valid}")
    print(f"CSV file: {csv_file}")
    
    if total_valid < 500:
        print(f"\nNeed {500 - total_valid} more articles. Run again or use other sources.")

if __name__ == "__main__":
    main()

