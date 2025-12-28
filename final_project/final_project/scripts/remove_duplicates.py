"""
Remove Duplicates from Database
Removes duplicate articles based on cleaned URLs.
"""

import os
import sys
import re
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

def clean_url_for_comparison(url):
    """Clean URL for duplicate detection"""
    if not url or pd.isna(url):
        return None
    
    url = str(url).strip()
    
    # Remove Google tracking parameters
    if '&ved=' in url:
        url = url.split('&ved=')[0]
    if '?ved=' in url:
        url = url.split('?ved=')[0]
    if '&usg=' in url:
        url = url.split('&usg=')[0]
    
    # Fix malformed URLs
    if '&' in url and '?' not in url:
        url = url.split('&')[0]
    
    # Remove tracking parameters
    url = re.sub(r'[&?]utm_[^&?]*', '', url)
    url = re.sub(r'[&?]ref=[^&?]*', '', url)
    
    # Clean up
    url = url.rstrip('/').rstrip('&').rstrip('?')
    
    return url

def remove_duplicates():
    """Remove duplicate articles"""
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        return
    
    print("=" * 60)
    print("Remove Duplicate Articles")
    print("=" * 60)
    print()
    
    # Get all articles with URLs
    print("Loading articles...")
    query = "SELECT id, url FROM articles WHERE url IS NOT NULL"
    df = pd.read_sql_query(query, db.conn)
    
    print(f"Found {len(df)} articles with URLs")
    print()
    
    # Clean URLs for comparison
    print("Cleaning URLs for duplicate detection...")
    df['cleaned_url'] = df['url'].apply(clean_url_for_comparison)
    
    # Find duplicates
    print("Finding duplicates...")
    duplicates = df[df.duplicated(subset=['cleaned_url'], keep=False)]
    
    if len(duplicates) == 0:
        print("No duplicates found!")
        db.disconnect()
        return
    
    # Group by cleaned URL
    duplicate_groups = duplicates.groupby('cleaned_url')
    
    print(f"Found {len(duplicate_groups)} groups of duplicate URLs")
    
    total_to_remove = 0
    removed_count = 0
    
    cur = db.conn.cursor()
    
    try:
        for cleaned_url, group in duplicate_groups:
            ids = sorted(group['id'].tolist())
            # Keep first ID (lowest), remove the rest
            ids_to_remove = ids[1:]
            total_to_remove += len(ids_to_remove)
            
            for article_id in ids_to_remove:
                try:
                    cur.execute("DELETE FROM articles WHERE id = %s", (article_id,))
                    removed_count += 1
                    if removed_count % 50 == 0:
                        db.conn.commit()
                        print(f"  Removed {removed_count} duplicates...")
                except Exception as e:
                    db.conn.rollback()
                    print(f"  Error removing article {article_id}: {e}")
                    continue
        
        db.conn.commit()
    finally:
        cur.close()
    
    print()
    print(f"Removed {removed_count} duplicate articles")
    
    # Final count
    final_count = pd.read_sql_query("SELECT COUNT(*) as count FROM articles", db.conn)['count'].iloc[0]
    
    print()
    print("=" * 60)
    print("Duplicate Removal Complete!")
    print("=" * 60)
    print(f"Final article count: {final_count}")
    print()
    
    db.disconnect()

if __name__ == "__main__":
    remove_duplicates()


