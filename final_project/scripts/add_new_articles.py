"""
Add New Articles to System
Collects new articles, filters them, checks for duplicates, and adds to database
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import time
from urllib.parse import urlparse, parse_qs
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

try:
    from GoogleNews import GoogleNews
    GOOGLENEWS_AVAILABLE = True
except ImportError:
    GOOGLENEWS_AVAILABLE = False
    print("Please install: pip install googlenews")

# Keywords for article collection
CIVIL_ENG_KEYWORDS = [
    "construction", "structural engineering", "geotechnical", 
    "transportation", "infrastructure", "concrete", "bridge", "tunnel",
    "civil engineering", "building design", "construction management"
]

AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "computer vision",
    "generative AI", "neural networks", "robotics", "automation",
    "deep learning", "AI", "ML"
]

def clean_url(url):
    """Remove tracking parameters from URL"""
    if not url:
        return None
    
    # Remove Google News tracking
    if '&ved=' in url:
        url = url.split('&ved=')[0]
    if '?ved=' in url:
        url = url.split('?ved=')[0]
    if '&usg=' in url:
        url = url.split('&usg=')[0]
    
    # Remove other tracking parameters
    url = re.sub(r'[&?]utm_[^&?]*', '', url)
    url = re.sub(r'[&?]ref=[^&?]*', '', url)
    
    # Fix malformed URLs
    if '&' in url and '?' not in url:
        url = url.split('&')[0]
    
    return url.strip()

def create_search_queries():
    """Generate search query combinations"""
    queries = []
    for ce_term in CIVIL_ENG_KEYWORDS:
        for ai_term in AI_KEYWORDS:
            queries.append(f"{ce_term} {ai_term}")
    return queries

def fetch_articles_from_google_news(query, max_results=20, days_back=7):
    """Fetch articles from Google News"""
    if not GOOGLENEWS_AVAILABLE:
        return []
    
    try:
        googlenews = GoogleNews(lang='en', region='US')
        googlenews.set_time_range(f'{days_back}d', '1d')
        googlenews.search(query)
        results = googlenews.results()
        
        articles = []
        for result in results[:max_results]:
            try:
                url = clean_url(result.get('link', ''))
                if not url or not url.startswith('http'):
                    continue
                
                # Parse date
                pub_date = result.get('date', None)
                if pub_date:
                    try:
                        from dateutil import parser
                        pub_date = parser.parse(str(pub_date)).date()
                    except:
                        pub_date = datetime.now().date()
                else:
                    pub_date = datetime.now().date()
                
                article = {
                    'title': result.get('title', '').strip(),
                    'url': url,
                    'source': result.get('media', 'Unknown'),
                    'publication_date': pub_date,
                    'content': result.get('desc', '').strip(),
                    'keywords': f"{query}"
                }
                
                if article['title'] and article['url']:
                    articles.append(article)
            except Exception as e:
                print(f"Error processing article: {e}")
                continue
        
        return articles
    except Exception as e:
        print(f"Error fetching articles for query '{query}': {e}")
        return []

def filter_article(article):
    """Filter articles for relevance"""
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    text = f"{title} {content}"
    
    # Must contain at least one CE term
    ce_terms = ['construction', 'structural', 'geotechnical', 'transportation', 
                'infrastructure', 'concrete', 'bridge', 'tunnel', 'civil', 'building']
    has_ce = any(term in text for term in ce_terms)
    
    # Must contain at least one AI term
    ai_terms = ['ai', 'artificial intelligence', 'machine learning', 'ml', 
                'computer vision', 'neural', 'robotics', 'automation', 'deep learning']
    has_ai = any(term in text for term in ai_terms)
    
    # Filter out irrelevant content
    exclude_terms = ['job', 'career', 'hiring', 'recruitment', 'salary', 'resume']
    has_exclude = any(term in text for term in exclude_terms)
    
    return has_ce and has_ai and not has_exclude

def check_duplicates(articles, db):
    """Check which articles are already in database"""
    if not db.connect():
        return articles, []
    
    try:
        # Get all existing URLs
        with db.conn.cursor() as cur:
            cur.execute("SELECT url FROM articles")
            existing_urls = {row[0] for row in cur.fetchall() if row[0]}
        
        new_articles = []
        duplicate_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in existing_urls:
                new_articles.append(article)
            else:
                duplicate_articles.append(article)
        
        return new_articles, duplicate_articles
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return articles, []
    finally:
        db.disconnect()

def add_articles_to_database(articles, db):
    """Add articles to database"""
    if not articles:
        return {'added': 0, 'failed': 0, 'errors': []}
    
    if not db.connect():
        return {'added': 0, 'failed': len(articles), 'errors': ['Database connection failed']}
    
    results = {'added': 0, 'failed': 0, 'errors': []}
    
    for article in articles:
        try:
            if db.insert_article(article):
                results['added'] += 1
            else:
                results['failed'] += 1
        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Error adding {article.get('title', 'Unknown')}: {str(e)}")
    
    db.disconnect()
    return results

def collect_and_add_articles(max_queries=10, max_results_per_query=20, days_back=7):
    """Main function to collect, filter, check duplicates, and add articles"""
    print("=" * 60)
    print("Collecting New Articles")
    print("=" * 60)
    print()
    
    # Step 1: Collect articles
    print(f"Step 1: Collecting articles from last {days_back} days...")
    queries = create_search_queries()[:max_queries]
    all_articles = []
    
    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] Searching: '{query}'...")
        articles = fetch_articles_from_google_news(query, max_results_per_query, days_back)
        all_articles.extend(articles)
        print(f"    Found {len(articles)} articles")
        time.sleep(1)  # Be nice to Google News
    
    print(f"\nTotal articles collected: {len(all_articles)}")
    
    # Step 2: Filter articles
    print("\nStep 2: Filtering articles for relevance...")
    filtered_articles = [a for a in all_articles if filter_article(a)]
    print(f"Articles after filtering: {len(filtered_articles)}")
    
    # Step 3: Check for duplicates
    print("\nStep 3: Checking for duplicates...")
    db = DatabaseManager()
    new_articles, duplicates = check_duplicates(filtered_articles, db)
    print(f"New articles: {len(new_articles)}")
    print(f"Duplicates (skipped): {len(duplicates)}")
    
    # Step 4: Add to database
    if new_articles:
        print("\nStep 4: Adding new articles to database...")
        results = add_articles_to_database(new_articles, db)
        print(f"\nResults:")
        print(f"  Added: {results['added']}")
        print(f"  Failed: {results['failed']}")
        if results['errors']:
            print(f"  Errors: {len(results['errors'])}")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"    - {error}")
    else:
        print("\nNo new articles to add!")
        results = {'added': 0, 'failed': 0, 'errors': []}
    
    print("\n" + "=" * 60)
    print("Collection Complete!")
    print("=" * 60)
    
    return {
        'collected': len(all_articles),
        'filtered': len(filtered_articles),
        'duplicates': len(duplicates),
        'new': len(new_articles),
        'added': results['added'],
        'failed': results['failed']
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect and add new articles to the system')
    parser.add_argument('--queries', type=int, default=10, help='Number of search queries to use')
    parser.add_argument('--results', type=int, default=20, help='Max results per query')
    parser.add_argument('--days', type=int, default=7, help='Days back to search')
    
    args = parser.parse_args()
    
    results = collect_and_add_articles(
        max_queries=args.queries,
        max_results_per_query=args.results,
        days_back=args.days
    )
    
    print(f"\nSummary:")
    print(f"  Collected: {results['collected']}")
    print(f"  Filtered: {results['filtered']}")
    print(f"  Duplicates: {results['duplicates']}")
    print(f"  New: {results['new']}")
    print(f"  Added: {results['added']}")
    print(f"  Failed: {results['failed']}")

