"""
NewsAPI Data Collector with PostgreSQL Storage
Collects articles related to Civil Engineering and AI using NewsAPI and stores in PostgreSQL.

Before running:
1. Start PostgreSQL Docker container: docker-compose up -d
2. Sign up at https://newsapi.org to get a free API key
3. Create a .env file in the project root with:
   - NEWSAPI_KEY=your_api_key_here
   - DB_HOST=localhost
   - DB_PORT=5432
   - DB_NAME=ce49x_articles
   - DB_USER=ce49x_user
   - DB_PASSWORD=ce49x_password
"""

import os
import sys
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv
import time

# Add scripts directory to path to import database module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
API_KEY = os.getenv('NEWSAPI_KEY', 'YOUR_API_KEY_HERE')
if API_KEY == 'YOUR_API_KEY_HERE':
    print("⚠️  Warning: Please set NEWSAPI_KEY in .env file")
    print("   Get your API key from: https://newsapi.org")

newsapi = NewsApiClient(api_key=API_KEY)

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
            queries.append(f"{ce_term} AND {ai_term}")
    return queries

def fetch_articles(keyword, days_back=30, max_results=100):
    """
    Fetch articles from NewsAPI
    
    Args:
        keyword: Search query string
        days_back: How many days back to search
        max_results: Maximum number of results to fetch
    
    Returns:
        List of article dictionaries
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Fetch articles
        response = newsapi.get_everything(
            q=keyword,
            language='en',
            sort_by='relevancy',
            from_param=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d'),
            page_size=min(max_results, 100)  # API max is 100 per page
        )
        
        if response['status'] == 'ok':
            return response['articles']
        else:
            error_msg = response.get('message', 'Unknown error')
            if 'rate limit' in error_msg.lower():
                print(f"  ⚠️  Rate limit reached. Please wait or try again later.")
            else:
                print(f"  Error: {error_msg}")
            return []
    
    except Exception as e:
        print(f"  Exception while fetching articles: {str(e)}")
        return []

def extract_article_data(article, keyword_query=""):
    """
    Extract required fields from article dictionary
    
    Returns:
        Dictionary with: title, publication_date, source, content, url, keywords
    """
    # Parse publication date
    pub_date = article.get('publishedAt', '')
    if pub_date:
        try:
            # Convert ISO format to date only
            pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00')).date()
        except:
            pub_date = None
    
    # Get content (prefer full content, fallback to description)
    content = article.get('content', '') or article.get('description', '')
    
    # Remove [Removed] or similar markers
    if content and '[Removed]' in content:
        content = article.get('description', '')
    
    return {
        'title': article.get('title', '').strip(),
        'publication_date': pub_date,
        'source': article.get('source', {}).get('name', 'Unknown'),
        'content': content.strip(),
        'url': article.get('url', ''),
        'keywords': keyword_query
    }

def validate_article(article):
    """Validate article has required fields and minimum content"""
    if not article.get('title'):
        return False, "Missing title"
    if not article.get('url'):
        return False, "Missing URL"
    if not article.get('content') or len(article.get('content', '').split()) < 50:
        return False, "Content too short or missing"
    return True, "Valid"

def main():
    """Main data collection function"""
    print("=" * 60)
    print("CE49X Final Project - Task 1: Data Collection")
    print("NewsAPI Collector with PostgreSQL Storage")
    print("=" * 60)
    print()
    
    # Initialize database connection
    db = DatabaseManager()
    
    print("Connecting to PostgreSQL database...")
    if not db.connect():
        print("\n✗ Failed to connect to database.")
        print("  Make sure Docker container is running:")
        print("  docker-compose up -d")
        return
    
    # Get initial article count
    initial_count = db.get_article_count()
    print(f"Current articles in database: {initial_count}")
    print()
    
    # Generate search queries
    queries = create_search_queries()
    print(f"Generated {len(queries)} search queries")
    print("Starting collection...\n")
    
    # Collection settings
    DAYS_BACK = 90  # Search articles from last 90 days
    MAX_RESULTS_PER_QUERY = 20  # Limit per query to avoid rate limits
    BATCH_SIZE = 50  # Insert in batches
    
    articles_to_insert = []
    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0
    total_invalid = 0
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Query: {query}")
        
        # Fetch articles from NewsAPI
        articles = fetch_articles(query, days_back=DAYS_BACK, max_results=MAX_RESULTS_PER_QUERY)
        total_fetched += len(articles)
        
        if not articles:
            print(f"  No articles found or error occurred")
            time.sleep(1)  # Small delay even on no results
            continue
        
        # Process each article
        for article in articles:
            article_data = extract_article_data(article, query)
            
            # Validate article
            is_valid, reason = validate_article(article_data)
            if not is_valid:
                total_invalid += 1
                continue
            
            # Check for duplicate URL
            if db.check_duplicate(article_data['url']):
                total_duplicates += 1
                continue
            
            articles_to_insert.append(article_data)
        
        print(f"  Fetched: {len(articles)}, Valid: {len(articles_to_insert)}, "
              f"Duplicates: {total_duplicates}, Invalid: {total_invalid}")
        
        # Insert in batches
        if len(articles_to_insert) >= BATCH_SIZE:
            stats = db.insert_articles_batch(articles_to_insert)
            total_inserted += stats['inserted']
            total_duplicates += stats['duplicates']
            articles_to_insert = []
            print(f"  → Batch inserted: {stats['inserted']} new articles")
        
        # Be respectful - add delay between requests
        time.sleep(1)  # 1 second delay to respect rate limits
        
        # Show progress
        current_count = db.get_article_count()
        if i % 10 == 0:
            print(f"  Progress: {current_count} total articles in database")
    
    # Insert remaining articles
    if articles_to_insert:
        stats = db.insert_articles_batch(articles_to_insert)
        total_inserted += stats['inserted']
        total_duplicates += stats['duplicates']
        print(f"  → Final batch inserted: {stats['inserted']} new articles")
    
    # Final statistics
    final_count = db.get_article_count()
    new_articles = final_count - initial_count
    
    print("\n" + "=" * 60)
    print("Collection Summary")
    print("=" * 60)
    print(f"Articles fetched from API:     {total_fetched}")
    print(f"New articles inserted:        {total_inserted}")
    print(f"Duplicate articles skipped:   {total_duplicates}")
    print(f"Invalid articles filtered:    {total_invalid}")
    print(f"Initial database count:        {initial_count}")
    print(f"Final database count:          {final_count}")
    print(f"Net new articles added:        {new_articles}")
    print()
    
    # Check if requirement is met
    if final_count >= 500:
        print(f"✓ Requirement met! ({final_count} articles >= 500)")
    else:
        needed = 500 - final_count
        print(f"⚠️  Need {needed} more articles to meet requirement (500)")
        print("   Suggestions:")
        print("   - Increase MAX_RESULTS_PER_QUERY")
        print("   - Extend DAYS_BACK parameter")
        print("   - Add more data sources")
        print("   - Run collection multiple times (different date ranges)")
    
    # Show database statistics
    stats = db.get_article_stats()
    if stats:
        print("\nDatabase Statistics:")
        print(f"  Unique sources: {stats.get('unique_sources', 'N/A')}")
        print(f"  Date range: {stats.get('earliest_date', 'N/A')} to {stats.get('latest_date', 'N/A')}")
        print(f"  Avg content length: {int(stats.get('avg_content_length', 0))} characters")
    
    # Close database connection
    db.disconnect()
    print("\n✓ Collection complete!")

if __name__ == "__main__":
    main()


