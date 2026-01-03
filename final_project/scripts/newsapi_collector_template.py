"""
NewsAPI Data Collector Template
Collects articles related to Civil Engineering and AI using NewsAPI.

Before running:
1. Sign up at https://newsapi.org to get a free API key
2. Create a .env file in the project root with: NEWSAPI_KEY=your_api_key_here
3. Or replace API_KEY below with your key (not recommended for production)
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
API_KEY = os.getenv('NEWSAPI_KEY', 'YOUR_API_KEY_HERE')
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
            print(f"Error fetching articles: {response.get('message', 'Unknown error')}")
            return []
    
    except Exception as e:
        print(f"Exception while fetching articles for '{keyword}': {str(e)}")
        return []

def extract_article_data(article):
    """
    Extract required fields from article dictionary
    
    Returns:
        Dictionary with: title, publication_date, source, content, url
    """
    return {
        'title': article.get('title', ''),
        'publication_date': article.get('publishedAt', ''),
        'source': article.get('source', {}).get('name', 'Unknown'),
        'content': article.get('content', article.get('description', '')),
        'url': article.get('url', ''),
        'keywords': ''  # Will be filled later
    }

def save_to_json(data, filename):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} articles to {filename}")

def save_to_csv(data, filename):
    """Save data to CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Saved {len(data)} articles to {filename}")

def main():
    """Main data collection function"""
    print("Starting data collection...")
    print("=" * 50)
    
    # Get project root directory (adjust path as needed)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    all_articles = []
    queries = create_search_queries()
    
    print(f"Generated {len(queries)} search queries")
    print(f"Collecting articles...\n")
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Searching: {query}")
        
        articles = fetch_articles(query, days_back=90, max_results=20)
        
        for article in articles:
            article_data = extract_article_data(article)
            article_data['keywords'] = query
            
            # Check for duplicates (by URL)
            if not any(a['url'] == article_data['url'] for a in all_articles):
                all_articles.append(article_data)
        
        print(f"  Collected {len(articles)} articles (Total unique: {len(all_articles)})")
        
        # Be respectful - add delay between requests
        # Note: Free tier has rate limits, so this delay helps
        time.sleep(1)
        
        # Save checkpoint every 50 articles
        if len(all_articles) % 50 == 0 and len(all_articles) > 0:
            checkpoint_file = os.path.join(data_dir, f'articles_checkpoint_{len(all_articles)}.json')
            save_to_json(all_articles, checkpoint_file)
    
    # Final save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = os.path.join(data_dir, f'articles_raw_{timestamp}.json')
    csv_file = os.path.join(data_dir, f'articles_raw_{timestamp}.csv')
    
    save_to_json(all_articles, json_file)
    save_to_csv(all_articles, csv_file)
    
    print("\n" + "=" * 50)
    print(f"Collection complete!")
    print(f"Total unique articles collected: {len(all_articles)}")
    print(f"Minimum requirement: 500 articles")
    
    if len(all_articles) < 500:
        print(f"⚠️  Warning: Only {len(all_articles)} articles collected. Consider:")
        print("   - Increasing max_results per query")
        print("   - Extending days_back parameter")
        print("   - Adding more data sources")
    else:
        print("✓ Requirement met!")

if __name__ == "__main__":
    main()






