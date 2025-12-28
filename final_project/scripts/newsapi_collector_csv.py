"""
NewsAPI Data Collector - CSV First Approach
Collects articles and saves to CSV for review before uploading to PostgreSQL.
Includes article summarization to reduce storage space.

Before running:
1. Sign up at https://newsapi.org to get a free API key
2. Create a .env file in the project root with: NEWSAPI_KEY=your_api_key_here
3. Install summarization library: pip install sumy (optional but recommended)
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv
import time

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from article_summarizer import summarize_article

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
# Try to get from environment, otherwise use hardcoded key
API_KEY = os.getenv('NEWSAPI_KEY', 'ba491fda-eb90-4580-800c-328263da2dfb')
if not API_KEY or API_KEY == 'YOUR_API_KEY_HERE':
    # Fallback to hardcoded key
    API_KEY = 'ba491fda-eb90-4580-800c-328263da2dfb'

print(f"Using NewsAPI key: {API_KEY[:8]}...{API_KEY[-4:]}")  # Show partial key for verification
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

# Summarization settings
SUMMARIZE_ARTICLES = True  # Set to False to keep full content
SUMMARY_METHOD = 'sumy'  # Options: 'sumy', 'tfidf', 'simple'
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_LENGTH = 500  # characters

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
            # Handle different error types
            error_code = response.get('code', '')
            error_msg = response.get('message', 'Unknown error')
            
            if error_code == 'apiKeyInvalid':
                print(f"  ERROR: API key is invalid!")
                print(f"  Please verify your API key at https://newsapi.org")
                # Don't continue if key is invalid
                raise ValueError(f"Invalid API key: {error_msg}")
            elif 'rate limit' in error_msg.lower() or error_code == 'rateLimited':
                print(f"  Warning: Rate limit reached. Please wait or try again later.")
            else:
                print(f"  Error ({error_code}): {error_msg}")
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
    
    # Summarize content if enabled
    original_content = content.strip()
    if SUMMARIZE_ARTICLES and original_content:
        try:
            content = summarize_article(
                original_content, 
                method=SUMMARY_METHOD,
                max_sentences=MAX_SUMMARY_SENTENCES,
                max_length=MAX_SUMMARY_LENGTH
            )
        except Exception as e:
            print(f"  Warning: Summarization failed, using original content: {e}")
            content = original_content
    
    return {
        'title': article.get('title', '').strip(),
        'publication_date': pub_date,
        'source': article.get('source', {}).get('name', 'Unknown'),
        'content': content,
        'url': article.get('url', ''),
        'keywords': keyword_query,
        'content_length': len(content),
        'original_length': len(original_content) if SUMMARIZE_ARTICLES else len(content)
    }

def validate_article(article):
    """Validate article has required fields and minimum content"""
    if not article.get('title'):
        return False, "Missing title"
    if not article.get('url'):
        return False, "Missing URL"
    content = article.get('content', '')
    if not content or len(content.split()) < 30:  # Reduced from 50 to 30 for summaries
        return False, "Content too short or missing"
    return True, "Valid"

def save_to_csv(articles, filename):
    """Save articles to CSV file"""
    if not articles:
        print("No articles to save")
        return
    
    df = pd.DataFrame(articles)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    # Save to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\nSaved {len(articles)} articles to {filename}")

def main():
    """Main data collection function"""
    print("=" * 60)
    print("CE49X Final Project - Task 1: Data Collection")
    print("NewsAPI Collector - CSV Output (with Summarization)")
    print("=" * 60)
    print()
    
    if SUMMARIZE_ARTICLES:
        print(f"Summarization: ENABLED ({SUMMARY_METHOD} method, max {MAX_SUMMARY_SENTENCES} sentences)")
    else:
        print("Summarization: DISABLED (full content will be saved)")
    print()
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate search queries
    queries = create_search_queries()
    print(f"Generated {len(queries)} search queries")
    print("Starting collection...\n")
    
    # Collection settings
    DAYS_BACK = 90  # Search articles from last 90 days
    MAX_RESULTS_PER_QUERY = 20  # Limit per query to avoid rate limits
    
    all_articles = []
    total_fetched = 0
    total_valid = 0
    total_invalid = 0
    seen_urls = set()  # Track duplicates
    
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
        query_valid = 0
        for article in articles:
            article_data = extract_article_data(article, query)
            
            # Check for duplicate URL
            if article_data['url'] in seen_urls:
                continue
            
            # Validate article
            is_valid, reason = validate_article(article_data)
            if not is_valid:
                total_invalid += 1
                continue
            
            # Add to collection
            seen_urls.add(article_data['url'])
            all_articles.append(article_data)
            query_valid += 1
            total_valid += 1
        
        print(f"  Fetched: {len(articles)}, Valid: {query_valid}, Total: {total_valid}")
        
        # Save checkpoint every 50 articles
        if len(all_articles) % 50 == 0 and len(all_articles) > 0:
            checkpoint_file = os.path.join(data_dir, f'articles_checkpoint_{len(all_articles)}.csv')
            save_to_csv(all_articles, checkpoint_file)
            print(f"  → Checkpoint saved: {len(all_articles)} articles")
        
        # Be respectful - add delay between requests
        time.sleep(1)  # 1 second delay to respect rate limits
    
    # Final save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(data_dir, f'articles_collected_{timestamp}.csv')
    
    save_to_csv(all_articles, csv_file)
    
    # Statistics
    print("\n" + "=" * 60)
    print("Collection Summary")
    print("=" * 60)
    print(f"Articles fetched from API:     {total_fetched}")
    print(f"Valid articles collected:      {total_valid}")
    print(f"Invalid articles filtered:     {total_invalid}")
    print(f"Duplicate articles skipped:    {total_fetched - total_valid - total_invalid}")
    print()
    
    if SUMMARIZE_ARTICLES:
        avg_original = sum(a['original_length'] for a in all_articles) / len(all_articles) if all_articles else 0
        avg_summary = sum(a['content_length'] for a in all_articles) / len(all_articles) if all_articles else 0
        reduction = ((avg_original - avg_summary) / avg_original * 100) if avg_original > 0 else 0
        print(f"Content Statistics:")
        print(f"  Average original length:   {int(avg_original)} characters")
        print(f"  Average summary length:    {int(avg_summary)} characters")
        print(f"  Space reduction:           {reduction:.1f}%")
        print()
    
    # Check if requirement is met
    if total_valid >= 500:
        print(f"Requirement met! ({total_valid} articles >= 500)")
    else:
        needed = 500 - total_valid
        print(f"Warning: Need {needed} more articles to meet requirement (500)")
        print("   Suggestions:")
        print("   - Increase MAX_RESULTS_PER_QUERY")
        print("   - Extend DAYS_BACK parameter")
        print("   - Run collection multiple times (different date ranges)")
        print("   - Add more data sources")
    
    print(f"\nCSV file saved: {csv_file}")
    print("\nNext steps:")
    print("1. Review the CSV file")
    print("2. Upload to PostgreSQL: python scripts/upload_csv_to_db.py")

if __name__ == "__main__":
    main()

