"""
View Articles in Database
Interactive script to view and query articles from PostgreSQL database.
"""

import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

def view_articles(limit=10, ce_area=None, ai_tech=None):
    """View articles from database"""
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        print("Make sure Docker container is running: docker-compose up -d")
        return
    
    # Build query
    query = "SELECT id, title, source, publication_date, url, keywords FROM articles"
    conditions = []
    
    if ce_area or ai_tech:
        # Need to check content for keywords
        # For now, just filter by keywords column
        if ce_area:
            conditions.append(f"keywords ILIKE '%{ce_area}%'")
        if ai_tech:
            conditions.append(f"keywords ILIKE '%{ai_tech}%'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" ORDER BY publication_date DESC LIMIT {limit}"
    
    try:
        df = pd.read_sql_query(query, db.conn)
        
        if len(df) == 0:
            print("No articles found matching criteria.")
        else:
            print(f"\nShowing {len(df)} articles:\n")
            for idx, row in df.iterrows():
                print(f"[{row['id']}] {row['title']}")
                print(f"    Source: {row['source']} | Date: {row['publication_date']}")
                print(f"    Keywords: {row['keywords']}")
                print(f"    URL: {row['url'][:80]}...")
                print()
    
    except Exception as e:
        print(f"Error querying database: {e}")
    
    db.disconnect()

def view_statistics():
    """View database statistics"""
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        return
    
    # Get article count
    count = db.get_article_count()
    print(f"\nTotal articles in database: {count}")
    
    # Get statistics
    stats = db.get_article_stats()
    if stats:
        print(f"\nDatabase Statistics:")
        print(f"  Unique sources: {stats.get('unique_sources', 0)}")
        print(f"  Date range: {stats.get('earliest_date', 'N/A')} to {stats.get('latest_date', 'N/A')}")
        avg_length = stats.get('avg_content_length', 0)
        if avg_length:
            print(f"  Average content length: {int(avg_length)} characters")
    
    # Articles by source
    query = """
        SELECT source, COUNT(*) as count
        FROM articles
        GROUP BY source
        ORDER BY count DESC
        LIMIT 10
    """
    try:
        df = pd.read_sql_query(query, db.conn)
        print(f"\nTop Sources:")
        for _, row in df.iterrows():
            print(f"  {row['source']:30s}: {row['count']} articles")
    except Exception as e:
        print(f"Error: {e}")
    
    db.disconnect()

def export_to_csv(output_file=None):
    """Export all articles to CSV"""
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        return
    
    if output_file is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(project_root, 'data', 'raw', 'articles_from_database.csv')
    
    success = db.export_to_csv(output_file)
    
    if success:
        print(f"\nArticles exported to: {output_file}")
    
    db.disconnect()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='View articles in PostgreSQL database')
    parser.add_argument('--limit', type=int, default=10, help='Number of articles to show')
    parser.add_argument('--ce-area', help='Filter by CE area')
    parser.add_argument('--ai-tech', help='Filter by AI technology')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', help='Export to CSV file')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("View Articles in Database")
    print("=" * 60)
    
    if args.stats:
        view_statistics()
    elif args.export:
        export_to_csv(args.export)
    else:
        view_articles(limit=args.limit, ce_area=args.ce_area, ai_tech=args.ai_tech)

if __name__ == "__main__":
    # If run without arguments, show interactive menu
    if len(sys.argv) == 1:
        print("=" * 60)
        print("Database Article Viewer")
        print("=" * 60)
        print()
        print("Options:")
        print("  1. View articles (last 10)")
        print("  2. View statistics")
        print("  3. Export to CSV")
        print()
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            limit = input("How many articles? (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            view_articles(limit=limit)
        elif choice == '2':
            view_statistics()
        elif choice == '3':
            export_to_csv()
        else:
            print("Invalid choice")
    else:
        main()





