"""
Fix URLs in Database
Attempts to fix malformed URLs in the database.
"""

import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

def fix_url(url):
    """Fix common URL issues, especially Google News tracking parameters"""
    if not url or pd.isna(url):
        return None
    
    url = str(url).strip()
    
    # If empty, return None
    if not url:
        return None
    
    # Remove Google News tracking parameters
    # These usually start with &ved= or ?ved=
    if '&ved=' in url:
        url = url.split('&ved=')[0]
    if '?ved=' in url:
        url = url.split('?ved=')[0]
    if '&usg=' in url:
        url = url.split('&usg=')[0]
    
    # Remove other common tracking parameters
    tracking_params = ['&utm_', '?utm_', '&ref=', '?ref=', '&source=', '?source=']
    for param in tracking_params:
        if param in url:
            url = url.split(param)[0]
    
    # Fix malformed URLs (sometimes Google News URLs have & instead of ?)
    # If URL has & but no ?, it might be malformed
    if '&' in url and '?' not in url:
        # Check if it's a valid URL structure
        parts = url.split('&')
        if len(parts) > 1:
            # Take the base URL (before first &)
            url = parts[0]
    
    # Remove trailing slashes and clean up
    url = url.rstrip('/')
    
    # If already a valid URL, return as is
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    # Fix common issues
    # If starts with //, add https:
    if url.startswith('//'):
        url = 'https:' + url
    # If starts with www., add https://
    elif url.startswith('www.'):
        url = 'https://' + url
    # If looks like a domain (has dots and no leading slash)
    elif '.' in url and not url.startswith('/'):
        # Check if it looks like a domain name
        if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}', url):
            url = 'https://' + url
        else:
            # Probably invalid
            return None
    else:
        # Probably invalid/relative URL
        return None
    
    return url

def update_urls_in_database():
    """Update URLs in database"""
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        return
    
    print("Fetching articles...")
    query = "SELECT id, url FROM articles WHERE url IS NOT NULL"
    import pandas as pd
    df = pd.read_sql_query(query, db.conn)
    
    print(f"Found {len(df)} articles with URLs")
    print("Fixing URLs...")
    
    fixed_count = 0
    invalid_count = 0
    
    for idx, row in df.iterrows():
        original_url = row['url']
        fixed_url = fix_url(original_url)
        
        if fixed_url != original_url:
            if fixed_url:
                # Update URL in database
                update_query = "UPDATE articles SET url = %s WHERE id = %s"
                try:
                    db.cursor.execute(update_query, (fixed_url, row['id']))
                    fixed_count += 1
                    if fixed_count % 100 == 0:
                        print(f"  Fixed {fixed_count} URLs...")
                except Exception as e:
                    print(f"Error updating URL for article {row['id']}: {e}")
            else:
                invalid_count += 1
                # Mark as invalid by prefixing with [INVALID]
                update_query = "UPDATE articles SET url = %s WHERE id = %s"
                try:
                    db.cursor.execute(update_query, (f"[INVALID] {original_url}", row['id']))
                except:
                    pass
    
    db.conn.commit()
    db.disconnect()
    
    print(f"\nDone!")
    print(f"  Fixed URLs: {fixed_count}")
    print(f"  Invalid URLs: {invalid_count}")
    print(f"  Total processed: {len(df)}")

if __name__ == "__main__":
    import pandas as pd
    print("=" * 60)
    print("Fix URLs in Database")
    print("=" * 60)
    print()
    update_urls_in_database()

