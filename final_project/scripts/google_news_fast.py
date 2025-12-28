"""
Fast Google News Collector - Optimized for Speed
No content fetching, no summarization during collection
Just collects titles, URLs, sources, dates - FAST!
"""

import os
import sys
import pandas as pd
from datetime import datetime
import time

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from GoogleNews import GoogleNews
    GOOGLENEWS_AVAILABLE = True
except ImportError:
    GOOGLENEWS_AVAILABLE = False
    print("Please install: pip install googlenews")

# SPEED OPTIMIZATIONS:
# - No summarization during collection (do it later if needed)
# - No content fetching (just use descriptions from Google News)
# - Reduced delays
# - Batch processing

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

def fetch_articles_fast(query, max_results=15):
    """
    Fast article fetching - just get what Google News provides
    
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
            # Use description as content (no fetching needed!)
            description = result.get('desc', '') or result.get('description', '')
            
            article = {
                'title': result.get('title', '').strip(),
                'url': result.get('link', '') or result.get('url', '') or result.get('href', ''),
                'source': result.get('source', 'Unknown'),
                'publication_date': result.get('date', ''),
                'content': description.strip(),  # Use description as content
            }
            
            if article['title'] and article['url']:  # Only add if has title and URL
                articles.append(article)
        
        googlenews.clear()
        
    except Exception as e:
        print(f"  Exception: {str(e)}")
    
    return articles

def extract_article_data_fast(article, keyword_query=""):
    """
    Fast extraction - no summarization, no processing
    """
    # Parse date
    pub_date = article.get('publication_date', '')
    if pub_date:
        try:
            from dateutil import parser
            pub_date = parser.parse(str(pub_date)).date()
        except:
            pub_date = datetime.now().date()
    else:
        pub_date = datetime.now().date()
    
    return {
        'title': article.get('title', '').strip(),
        'publication_date': pub_date,
        'source': article.get('source', 'Google News'),
        'content': article.get('content', '').strip(),  # Already description, no summarization
        'url': article.get('url', ''),
        'keywords': keyword_query,
    }

def validate_article_fast(article):
    """Fast validation - minimal checks"""
    if not article.get('title') or len(article.get('title', '')) < 10:
        return False
    if not article.get('url'):
        return False
    # Content can be short (just description) - that's OK
    return True

def save_to_csv(articles, filename):
    """Save articles to CSV"""
    if not articles:
        return
    
    df = pd.DataFrame(articles)
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Saved {len(articles)} articles to {filename}")

def main():
    """Fast collection - optimized for speed"""
    if not GOOGLENEWS_AVAILABLE:
        print("Please install: pip install googlenews python-dateutil")
        return
    
    print("=" * 60)
    print("CE49X Final Project - FAST Google News Collector")
    print("Optimized for speed: No content fetching, no summarization")
    print("=" * 60)
    print()
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    queries = create_search_queries()
    print(f"Generated {len(queries)} search queries")
    print("Starting FAST collection...")
    print("(Using descriptions only - no full content fetching)\n")
    
    all_articles = []
    seen_urls = set()
    total_valid = 0
    total_fetched = 0
    
    start_time = time.time()
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Query: {query}", end=' ')
        
        articles = fetch_articles_fast(query, max_results=15)  # Get more per query
        total_fetched += len(articles)
        
        query_valid = 0
        for article in articles:
            url = article.get('url', '')
            if not url or url in seen_urls:
                continue
            
            article_data = extract_article_data_fast(article, query)
            
            if not validate_article_fast(article_data):
                continue
            
            seen_urls.add(url)
            all_articles.append(article_data)
            query_valid += 1
            total_valid += 1
        
        print(f"-> {query_valid} new articles (Total: {total_valid})")
        
        # Minimal delay - just enough to not get blocked
        time.sleep(0.5)  # Reduced from 1-2 seconds to 0.5 seconds
        
        # Save checkpoint every 100 articles (less frequent saves = faster)
        if len(all_articles) % 100 == 0 and len(all_articles) > 0:
            checkpoint = os.path.join(data_dir, f'articles_fast_checkpoint_{len(all_articles)}.csv')
            save_to_csv(all_articles, checkpoint)
            elapsed = time.time() - start_time
            rate = total_valid / elapsed if elapsed > 0 else 0
            print(f"  -> Checkpoint saved ({len(all_articles)} articles, {rate:.1f} articles/sec)")
    
    # Final save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(data_dir, f'articles_google_news_fast_{timestamp}.csv')
    save_to_csv(all_articles, csv_file)
    
    elapsed_time = time.time() - start_time
    rate = total_valid / elapsed_time if elapsed_time > 0 else 0
    
    print("\n" + "=" * 60)
    print("Collection Complete!")
    print("=" * 60)
    print(f"Total articles fetched:     {total_fetched}")
    print(f"Valid articles collected:   {total_valid}")
    print(f"Time elapsed:               {elapsed_time/60:.1f} minutes")
    print(f"Collection rate:            {rate:.1f} articles/second")
    print(f"CSV file:                   {csv_file}")
    
    if total_valid >= 500:
        print(f"\nSUCCESS! Requirement met ({total_valid} >= 500)")
    else:
        needed = 500 - total_valid
        print(f"\nNeed {needed} more articles.")
        print("Suggestions:")
        print("  - Run again (Google News results vary)")
        print("  - Increase MAX_RESULTS_PER_QUERY")
        print("  - Try different time periods")
    
    print("\nNext steps:")
    print("1. Review CSV file")
    print("2. Upload to database: python scripts/upload_csv_to_db.py")
    print("3. (Optional) Summarize later if needed")

if __name__ == "__main__":
    main()

