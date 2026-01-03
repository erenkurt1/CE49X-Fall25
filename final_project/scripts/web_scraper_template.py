"""
Web Scraping Template for Civil Engineering & AI Articles
This is a template for scraping articles from websites.

IMPORTANT: 
- Always check robots.txt before scraping (e.g., https://website.com/robots.txt)
- Respect rate limits (add delays between requests)
- Check website's Terms of Service
- Some sites may require Selenium for JavaScript-rendered content
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import re

def get_page_content(url, headers=None):
    """
    Fetch webpage content
    
    Args:
        url: URL to fetch
        headers: Optional headers dictionary (recommended to include User-Agent)
    
    Returns:
        BeautifulSoup object or None if error
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def parse_article(soup, base_url=""):
    """
    Parse article content from BeautifulSoup object
    
    This is a template - you'll need to customize selectors based on the target website
    Use browser developer tools to inspect the HTML structure
    
    Args:
        soup: BeautifulSoup object
        base_url: Base URL for resolving relative links
    
    Returns:
        Dictionary with article data or None
    """
    try:
        # Example selectors (adjust based on actual website structure)
        title = soup.find('h1')  # Adjust selector
        if not title:
            title = soup.find('title')
        title = title.get_text(strip=True) if title else ""
        
        # Date (try multiple common patterns)
        date_elem = soup.find('time') or soup.find(class_='date') or soup.find(class_='published')
        pub_date = ""
        if date_elem:
            pub_date = date_elem.get('datetime') or date_elem.get_text(strip=True)
        
        # Content
        content_div = soup.find('article') or soup.find(class_='content') or soup.find('main')
        content = ""
        if content_div:
            # Remove script and style elements
            for script in content_div(["script", "style"]):
                script.decompose()
            content = content_div.get_text(separator=' ', strip=True)
        
        # Source
        source = base_url.split('//')[1].split('/')[0] if base_url else "Unknown"
        
        return {
            'title': title,
            'publication_date': pub_date,
            'source': source,
            'content': content,
            'url': base_url
        }
    except Exception as e:
        print(f"Error parsing article: {str(e)}")
        return None

def get_article_links(search_url, keyword):
    """
    Get list of article URLs from a search or listing page
    
    This is a template - customize based on the website structure
    
    Args:
        search_url: URL of search results or article listing page
        keyword: Search keyword (may be used to build search URL)
    
    Returns:
        List of article URLs
    """
    soup = get_page_content(search_url)
    if not soup:
        return []
    
    article_links = []
    # Example: Find all links with 'article' in class or href
    # Adjust selectors based on actual website
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        # Convert relative URLs to absolute
        if href.startswith('/'):
            base = '/'.join(search_url.split('/')[:3])
            href = base + href
        
        # Filter for article links (adjust pattern as needed)
        if any(keyword.lower() in href.lower() for keyword in ['article', 'news', 'post']):
            article_links.append(href)
    
    return list(set(article_links))  # Remove duplicates

def scrape_site(base_url, keywords, max_articles=50):
    """
    Main scraping function
    
    Args:
        base_url: Base URL of the website
        keywords: List of keywords to search for
        max_articles: Maximum number of articles to collect
    
    Returns:
        List of article dictionaries
    """
    all_articles = []
    
    for keyword in keywords:
        print(f"Searching for: {keyword}")
        
        # Build search URL (customize based on website's search functionality)
        search_url = f"{base_url}/search?q={keyword.replace(' ', '+')}"
        
        # Get article links
        article_urls = get_article_links(search_url, keyword)
        print(f"  Found {len(article_urls)} potential articles")
        
        # Scrape each article
        for url in article_urls[:max_articles]:
            print(f"  Scraping: {url}")
            soup = get_page_content(url)
            
            if soup:
                article = parse_article(soup, url)
                if article and article['content']:  # Only add if content exists
                    article['keywords'] = keyword
                    all_articles.append(article)
            
            # Be respectful - add delay
            time.sleep(2)  # 2 second delay between requests
        
        if len(all_articles) >= max_articles:
            break
    
    return all_articles

def save_articles(articles, filename):
    """Save articles to CSV file"""
    df = pd.DataFrame(articles)
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Saved {len(articles)} articles to {filename}")

# Example usage
if __name__ == "__main__":
    # Example: Scraping a hypothetical construction news site
    # Replace with actual URLs and customize selectors
    
    base_url = "https://example-construction-news.com"
    keywords = ["construction", "AI", "infrastructure"]
    
    articles = scrape_site(base_url, keywords, max_articles=50)
    save_articles(articles, "data/raw/scraped_articles.csv")
    
    print(f"\nTotal articles collected: {len(articles)}")






