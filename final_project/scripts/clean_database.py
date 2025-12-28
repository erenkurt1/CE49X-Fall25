"""
Clean Database: Fix URLs and Remove Duplicates
"""

import os
import sys
import re
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

def clean_url(url):
    """Clean URL by removing Google tracking parameters"""
    if not url or pd.isna(url):
        return None
    
    url = str(url).strip()
    
    if not url:
        return None
    
    # Remove Google News tracking parameters
    # These usually appear as &ved= or ?ved= or sometimes just & at the end
    if '&ved=' in url:
        url = url.split('&ved=')[0]
    if '?ved=' in url:
        url = url.split('?ved=')[0]
    if '&usg=' in url:
        url = url.split('&usg=')[0]
    
    # Remove other tracking parameters
    tracking_patterns = [
        r'&utm_[^&]*',
        r'\?utm_[^&]*',
        r'&ref=[^&]*',
        r'\?ref=[^&]*',
        r'&source=[^&]*',
        r'\?source=[^&]*',
    ]
    
    for pattern in tracking_patterns:
        url = re.sub(pattern, '', url)
    
    # Fix malformed URLs - if URL has & but no ?, it's probably malformed
    # Extract the base URL (everything before first & that's not part of query string)
    if '&' in url and '?' not in url:
        # This is a malformed URL - take everything before first &
        parts = url.split('&')
        url = parts[0]
    
    # Clean up
    url = url.rstrip('/').rstrip('&').rstrip('?')
    
    # Validate URL format
    if not url.startswith('http://') and not url.startswith('https://'):
        # Try to fix
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('www.'):
            url = 'https://' + url
        elif '.' in url and not url.startswith('/'):
            # Might be a domain
            if re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}', url):
                url = 'https://' + url
            else:
                return None
        else:
            return None
    
    return url

def remove_duplicates_and_fix_urls():
    """Remove duplicates and fix URLs in database"""
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        return
    
    print("=" * 60)
    print("Cleaning Database: Fix URLs and Remove Duplicates")
    print("=" * 60)
    print()
    
    # Step 1: Fix URLs
    print("Step 1: Fixing URLs...")
    query = "SELECT id, url FROM articles WHERE url IS NOT NULL"
    df = pd.read_sql_query(query, db.conn)
    
    print(f"Found {len(df)} articles with URLs")
    
    fixed_count = 0
    invalid_count = 0
    
    cur = db.conn.cursor()
    
    try:
        for idx, row in df.iterrows():
            original_url = row['url']
            cleaned_url = clean_url(original_url)
            
            if cleaned_url != original_url:
                if cleaned_url:
                    # Update URL
                    update_query = "UPDATE articles SET url = %s WHERE id = %s"
                    try:
                        cur.execute(update_query, (cleaned_url, row['id']))
                        fixed_count += 1
                        if fixed_count % 100 == 0:
                            db.conn.commit()
                            print(f"  Fixed {fixed_count} URLs...")
                    except Exception as e:
                        db.conn.rollback()
                        print(f"  Error updating URL for article {row['id']}: {e}")
                        continue
                else:
                    invalid_count += 1
                    # Mark as invalid
                    try:
                        cur.execute("UPDATE articles SET url = %s WHERE id = %s", 
                                  (f"[INVALID] {original_url[:100]}", row['id']))
                    except:
                        db.conn.rollback()
                        continue
        
        db.conn.commit()
    finally:
        cur.close()
    
    print(f"  Fixed: {fixed_count} URLs")
    print(f"  Invalid: {invalid_count} URLs")
    print()
    
    # Step 2: Remove duplicates
    print("Step 2: Finding duplicates...")
    
    # Find duplicates by URL (after cleaning) - use a simpler approach
    query = """
        SELECT url, COUNT(*) as count
        FROM articles
        WHERE url IS NOT NULL AND url NOT LIKE '[INVALID]%'
        GROUP BY url
        HAVING COUNT(*) > 1
        ORDER BY count DESC
    """
    
    duplicates_df = pd.read_sql_query(query, db.conn)
    
    print(f"Found {len(duplicates_df)} duplicate URLs")
    
    if len(duplicates_df) > 0:
        total_duplicates = duplicates_df['count'].sum() - len(duplicates_df)
        print(f"Total duplicate articles to remove: {total_duplicates}")
        print()
        
        # Remove duplicates (keep the first one by ID, remove the rest)
        removed_count = 0
        cur = db.conn.cursor()
        
        try:
            for idx, row in duplicates_df.iterrows():
                url = row['url']
                # Get all IDs with this URL, ordered by ID
                cur.execute("""
                    SELECT id FROM articles 
                    WHERE url = %s 
                    ORDER BY id
                """, (url,))
                ids = [r[0] for r in cur.fetchall()]
                
                # Keep first ID, remove the rest
                ids_to_remove = ids[1:]  # Skip first one
                
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
        
        print(f"  Removed {removed_count} duplicate articles")
    else:
        print("  No duplicates found!")
    
    print()
    
    # Final statistics
    final_count = pd.read_sql_query("SELECT COUNT(*) as count FROM articles", db.conn)['count'].iloc[0]
    
    print("=" * 60)
    print("Cleaning Complete!")
    print("=" * 60)
    print(f"Final article count: {final_count}")
    print()
    
    db.disconnect()

if __name__ == "__main__":
    remove_duplicates_and_fix_urls()

