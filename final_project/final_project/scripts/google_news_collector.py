"""
Google News Scraper - CSV Output
Collects articles from Google News using web scraping.
Saves to CSV for review before uploading to PostgreSQL.
Includes article summarization to reduce storage space.

No API key required - uses free Google News search.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin, urlparse
import re

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from article_summarizer import summarize_article

# Summarization settings
SUMMARIZE_ARTICLES = True
SUMMARY_METHOD = 'sumy'  # Options: 'sumy', 'tfidf', 'simple'
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

def get_google_news_url(query, days_back=30):
    """
    Build Google News search URL
    
    Args:
        query: Search query string
        days_back: How many days back to search
    
    Returns:
        Google News search URL
    """
    # Google News search URL
    base_url = "https://news.google.com/search"
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format query for URL
    query_encoded = quote(query)
    
    # Google News URL with time range
    url = f"{base_url}?q={query_encoded}&hl=en&gl=US&ceid=US:en"
    
    # Add when parameter for date range (if supported)
    # Note: Google News doesn't have direct date filtering in URL, but we can try
    return url

def fetch_google_news_articles(query, max_results=20):
    """
    Scrape articles from Google News search results
    
    Args:
        query: Search query string
        max_results: Maximum number of articles to fetch
    
    Returns:
        List of article dictionaries with Google News data
    """
    articles = []
    
    try:
        # Build search URL
        search_url = get_google_news_url(query, days_back=90)
        
        # Headers to mimic browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # Fetch Google News page
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Google News structure: articles are in <article> tags or <div> with specific classes
        # Find article links
        article_links = []
        
        # Try multiple selectors for Google News
        selectors = [
            'article a[href^="./"]',  # Relative links
            'article h3 a',
            'div[data-nir] a',
            'a[href*="/articles/"]',
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links[:max_results * 2]:  # Get more to account for filtering
                href = link.get('href', '')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('./'):
                        href = 'https://news.google.com' + href[1:]
                    elif href.startswith('/'):
                        href = 'https://news.google.com' + href
                    
                    # Extract actual article URL from Google News redirect
                    if '/articles/' in href or '/stories/' in href:
                        article_links.append({
                            'url': href,
                            'title': link.get_text(strip=True) or link.get('aria-label', '')
                        })
            
            if len(article_links) >= max_results:
                break
        
        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link_info in article_links:
            url = link_info['url']
            if url not in seen_urls and url:
                seen_urls.add(url)
                unique_links.append(link_info)
                if len(unique_links) >= max_results:
                    break
        
        # For each link, try to get article details
        for link_info in unique_links[:max_results]:
            article = {
                'title': link_info.get('title', ''),
                'url': link_info['url'],
                'source': 'Google News',
                'publication_date': None,  # Will try to extract
                'content': '',  # Will try to fetch
            }
            articles.append(article)
        
        return articles
    
    except Exception as e:
        print(f"  Exception while fetching from Google News: {str(e)}")
        return []

def fetch_article_content(url):
    """
    Try to fetch full article content from URL
    
    Args:
        url: Article URL
    
    Returns:
        Article content text or empty string
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.article-body',
            '.content',
            '.post-content',
            'div.article',
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text(separator=' ', strip=True) for elem in elements])
                if len(content) > 200:  # If we got substantial content
                    break
        
        # If no main content found, get body text
        if not content or len(content) < 200:
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content)  # Multiple spaces to single
        content = content[:5000]  # Limit length
        
        return content
    
    except Exception as e:
        # Silently fail - we'll use title/description only
        return ""

def extract_article_data(article, keyword_query=""):
    """
    Extract and process article data
    
    Returns:
        Dictionary with: title, publication_date, source, content, url, keywords
    """
    # Try to get content if not already present
    content = article.get('content', '')
    if not content and article.get('url'):
        # Try to fetch content
        content = fetch_article_content(article['url'])
        time.sleep(0.5)  # Be respectful
    
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
            content = original_content
    
    # Try to extract date
    pub_date = article.get('publication_date')
    if not pub_date:
        # Try to parse from URL or set to today
        pub_date = datetime.now().date()
    
    return {
        'title': article.get('title', '').strip(),
        'publication_date': pub_date,
        'source': article.get('source', 'Google News'),
        'content': content.strip(),
        'url': article.get('url', ''),
        'keywords': keyword_query,
        'content_length': len(content),
        'original_length': len(original_content) if SUMMARIZE_ARTICLES and original_content else len(content)
    }

def validate_article(article):
    """Validate article has required fields and minimum content"""
    if not article.get('title'):
        return False, "Missing title"
    if not article.get('url'):
        return False, "Missing URL"
    content = article.get('content', '')
    if not content or len(content.split()) < 20:  # Reduced threshold for summaries
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
    print("Google News Scraper - CSV Output (with Summarization)")
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
    print("Starting collection from Google News...")
    print("Note: This may take a while as we fetch article content...\n")
    
    # Collection settings
    MAX_RESULTS_PER_QUERY = 10  # Reduced to be faster and avoid rate limits
    
    all_articles = []
    total_fetched = 0
    total_valid = 0
    total_invalid = 0
    seen_urls = set()  # Track duplicates
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Query: {query}")
        
        # Fetch articles from Google News
        articles = fetch_google_news_articles(query, max_results=MAX_RESULTS_PER_QUERY)
        total_fetched += len(articles)
        
        if not articles:
            print(f"  No articles found")
            time.sleep(1)
            continue
        
        # Process each article
        query_valid = 0
        for article in articles:
            # Check for duplicate URL
            if article.get('url') in seen_urls:
                continue
            
            article_data = extract_article_data(article, query)
            
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
        
        print(f"  Found: {len(articles)}, Valid: {query_valid}, Total: {total_valid}")
        
        # Save checkpoint every 50 articles
        if len(all_articles) % 50 == 0 and len(all_articles) > 0:
            checkpoint_file = os.path.join(data_dir, f'articles_checkpoint_{len(all_articles)}.csv')
            save_to_csv(all_articles, checkpoint_file)
            print(f"  -> Checkpoint saved: {len(all_articles)} articles")
        
        # Be respectful - add delay between requests
        time.sleep(2)  # 2 second delay to avoid being blocked
        
        # Show progress
        if i % 10 == 0:
            print(f"  Progress: {total_valid} total articles collected")
    
    # Final save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = os.path.join(data_dir, f'articles_google_news_{timestamp}.csv')
    
    save_to_csv(all_articles, csv_file)
    
    # Statistics
    print("\n" + "=" * 60)
    print("Collection Summary")
    print("=" * 60)
    print(f"Articles found:                {total_fetched}")
    print(f"Valid articles collected:      {total_valid}")
    print(f"Invalid articles filtered:     {total_invalid}")
    print(f"Duplicate articles skipped:    {total_fetched - total_valid - total_invalid}")
    print()
    
    if SUMMARIZE_ARTICLES and all_articles:
        avg_original = sum(a['original_length'] for a in all_articles) / len(all_articles)
        avg_summary = sum(a['content_length'] for a in all_articles) / len(all_articles)
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
        print("   - Run collection multiple times")
        print("   - Try different search terms")
        print("   - Combine with other data sources")
    
    print(f"\nCSV file saved: {csv_file}")
    print("\nNext steps:")
    print("1. Review the CSV file")
    print("2. Upload to PostgreSQL: python scripts/upload_csv_to_db.py")

if __name__ == "__main__":
    main()


