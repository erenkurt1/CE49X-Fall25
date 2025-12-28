"""
Upload CSV Articles to PostgreSQL Database
Reads articles from CSV file and uploads them to PostgreSQL database.

Usage:
    python upload_csv_to_db.py [csv_file_path]

If no file path is provided, will look for the most recent CSV file in data/raw/
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

def find_latest_csv(data_dir):
    """Find the most recent CSV file in data directory"""
    data_path = Path(data_dir)
    if not data_path.exists():
        return None
    
    csv_files = list(data_path.glob('articles_*.csv'))
    if not csv_files:
        return None
    
    # Sort by modification time, return most recent
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    return str(latest)

def validate_csv_data(df):
    """Validate CSV data has required columns"""
    required_columns = ['title', 'source', 'content', 'url']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        print(f"✗ Missing required columns: {', '.join(missing)}")
        return False
    
    return True

def upload_csv_to_database(csv_file, db):
    """Upload articles from CSV to PostgreSQL database"""
    print(f"\nReading CSV file: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"✓ Loaded {len(df)} articles from CSV")
    except Exception as e:
        print(f"✗ Error reading CSV: {e}")
        return False
    
    # Validate data
    if not validate_csv_data(df):
        return False
    
    # Check for duplicates in CSV
    duplicate_urls = df[df.duplicated(subset=['url'], keep=False)]
    if len(duplicate_urls) > 0:
        print(f"⚠️  Warning: {len(duplicate_urls)} duplicate URLs found in CSV (will be skipped)")
        df = df.drop_duplicates(subset=['url'], keep='first')
        print(f"  After deduplication: {len(df)} unique articles")
    
    # Convert DataFrame to list of dictionaries
    articles = []
    for _, row in df.iterrows():
        article = {
            'title': str(row.get('title', '')).strip(),
            'publication_date': row.get('publication_date'),
            'source': str(row.get('source', 'Unknown')).strip(),
            'content': str(row.get('content', '')).strip(),
            'url': str(row.get('url', '')).strip(),
            'keywords': str(row.get('keywords', '')).strip()
        }
        
        # Handle date conversion
        if pd.notna(article['publication_date']):
            try:
                if isinstance(article['publication_date'], str):
                    from datetime import datetime
                    article['publication_date'] = pd.to_datetime(article['publication_date']).date()
                else:
                    article['publication_date'] = article['publication_date']
            except:
                article['publication_date'] = None
        else:
            article['publication_date'] = None
        
        articles.append(article)
    
    print(f"\nUploading {len(articles)} articles to database...")
    
    # Upload in batches
    BATCH_SIZE = 100
    total_inserted = 0
    total_duplicates = 0
    total_errors = 0
    
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i + BATCH_SIZE]
        stats = db.insert_articles_batch(batch)
        
        total_inserted += stats['inserted']
        total_duplicates += stats['duplicates']
        total_errors += stats.get('errors', 0)
        
        print(f"  Batch {i//BATCH_SIZE + 1}: {stats['inserted']} inserted, {stats['duplicates']} duplicates")
    
    print("\n" + "=" * 60)
    print("Upload Summary")
    print("=" * 60)
    print(f"Total articles in CSV:      {len(df)}")
    print(f"New articles inserted:     {total_inserted}")
    print(f"Duplicate articles:        {total_duplicates}")
    print(f"Errors:                     {total_errors}")
    
    # Get final database count
    final_count = db.get_article_count()
    print(f"\nTotal articles in database: {final_count}")
    
    return True

def main():
    """Main upload function"""
    print("=" * 60)
    print("CSV to PostgreSQL Upload Tool")
    print("=" * 60)
    
    # Get CSV file path
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # Find latest CSV file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data', 'raw')
        csv_file = find_latest_csv(data_dir)
        
        if not csv_file:
            print("\n✗ No CSV file found in data/raw/")
            print("  Please provide CSV file path:")
            print("  python upload_csv_to_db.py <path_to_csv>")
            return
    
    if not os.path.exists(csv_file):
        print(f"\n✗ CSV file not found: {csv_file}")
        return
    
    print(f"\nCSV file: {csv_file}")
    
    # Connect to database
    db = DatabaseManager()
    print("\nConnecting to PostgreSQL database...")
    if not db.connect():
        print("\n✗ Failed to connect to database.")
        print("  Make sure Docker container is running:")
        print("  docker-compose up -d")
        return
    
    # Get initial count
    initial_count = db.get_article_count()
    print(f"Current articles in database: {initial_count}")
    
    # Confirm upload
    print(f"\nReady to upload articles from: {os.path.basename(csv_file)}")
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Upload cancelled.")
        db.disconnect()
        return
    
    # Upload
    success = upload_csv_to_database(csv_file, db)
    
    if success:
        print("\n✓ Upload complete!")
    else:
        print("\n✗ Upload failed. Please check the errors above.")
    
    # Close connection
    db.disconnect()

if __name__ == "__main__":
    main()


