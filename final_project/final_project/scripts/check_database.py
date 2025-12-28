"""
Check Database Status
Quick script to check article count and statistics in PostgreSQL
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

def main():
    """Check database status"""
    print("=" * 60)
    print("PostgreSQL Database Status")
    print("=" * 60)
    print()
    
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        print("Make sure Docker container is running: docker-compose up -d")
        return
    
    # Get article count
    count = db.get_article_count()
    print(f"Total articles in database: {count}")
    print()
    
    # Get statistics
    stats = db.get_article_stats()
    if stats:
        print("Database Statistics:")
        print(f"  Unique sources:              {stats.get('unique_sources', 0)}")
        print(f"  Date range:                  {stats.get('earliest_date', 'N/A')} to {stats.get('latest_date', 'N/A')}")
        avg_length = stats.get('avg_content_length', 0)
        if avg_length:
            print(f"  Average content length:      {int(avg_length)} characters")
        print(f"  Unique keyword combinations: {stats.get('unique_keyword_combinations', 0)}")
        print()
    
    # Check requirement
    if count >= 500:
        print(f"SUCCESS! Requirement met ({count} >= 500)")
    else:
        needed = 500 - count
        print(f"Need {needed} more articles to meet requirement (500)")
    
    # Sample articles
    if count > 0:
        print()
        print("Sample articles (first 5):")
        try:
            with db.conn.cursor() as cur:
                cur.execute("SELECT title, source, publication_date FROM articles LIMIT 5")
                for row in cur.fetchall():
                    print(f"  - {row[0][:60]}... ({row[1]}, {row[2]})")
        except Exception as e:
            print(f"  Error fetching samples: {e}")
    
    db.disconnect()

if __name__ == "__main__":
    main()


