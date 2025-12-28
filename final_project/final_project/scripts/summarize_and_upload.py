"""
Summarize and Upload Articles to PostgreSQL
Summarizes articles and uploads them to the database in one step.
"""

import os
import sys
import pandas as pd

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager
from article_summarizer import summarize_article

# Summarization settings
SUMMARIZE = True
SUMMARY_METHOD = 'simple'  # Use 'simple' for faster processing
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_LENGTH = 500

def summarize_and_upload(csv_file, db, batch_size=100):
    """
    Summarize articles and upload to database
    
    Args:
        csv_file: Path to CSV file
        db: DatabaseManager instance
        batch_size: Batch size for uploads
    """
    print(f"Loading articles from: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        print(f"Loaded {len(df)} articles")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return False
    
    # Validate data
    required_columns = ['title', 'source', 'content', 'url']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"Missing required columns: {', '.join(missing)}")
        return False
    
    # Remove duplicates in CSV
    initial_count = len(df)
    df = df.drop_duplicates(subset=['url'], keep='first')
    if len(df) < initial_count:
        print(f"Removed {initial_count - len(df)} duplicates from CSV")
    
    print()
    if SUMMARIZE:
        print(f"Summarizing articles ({SUMMARY_METHOD} method)...")
        print("(This may take a few minutes)")
    else:
        print("Skipping summarization (using original content)")
    
    print()
    
    # Process articles
    articles = []
    total_original_length = 0
    total_summarized_length = 0
    
    for idx, row in df.iterrows():
        # Get content
        content = str(row.get('content', '')).strip()
        
        # Summarize if enabled and content is long enough
        if SUMMARIZE and content and len(content) > 100:
            try:
                original_length = len(content)
                content = summarize_article(
                    content,
                    method=SUMMARY_METHOD,
                    max_sentences=MAX_SUMMARY_SENTENCES,
                    max_length=MAX_SUMMARY_LENGTH
                )
                total_original_length += original_length
                total_summarized_length += len(content)
            except Exception as e:
                # If summarization fails, use original
                pass
        
        # Prepare article data
        article = {
            'title': str(row.get('title', '')).strip(),
            'publication_date': row.get('publication_date'),
            'source': str(row.get('source', 'Unknown')).strip(),
            'content': content,
            'url': str(row.get('url', '')).strip(),
            'keywords': str(row.get('keywords', '')).strip()
        }
        
        # Handle date
        if pd.notna(article['publication_date']):
            try:
                if isinstance(article['publication_date'], str):
                    from datetime import datetime
                    article['publication_date'] = pd.to_datetime(article['publication_date']).date()
            except:
                article['publication_date'] = None
        else:
            article['publication_date'] = None
        
        articles.append(article)
        
        # Show progress
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} articles...")
    
    print(f"Processed {len(articles)} articles")
    
    if SUMMARIZE and total_original_length > 0:
        reduction = ((total_original_length - total_summarized_length) / total_original_length * 100)
        print(f"Space reduction: {reduction:.1f}%")
        print(f"  Original: {total_original_length:,} characters")
        print(f"  Summarized: {total_summarized_length:,} characters")
        print(f"  Saved: {total_original_length - total_summarized_length:,} characters")
    
    print()
    print("Uploading to database...")
    
    # Upload in batches
    total_inserted = 0
    total_duplicates = 0
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        stats = db.insert_articles_batch(batch)
        
        total_inserted += stats['inserted']
        total_duplicates += stats['duplicates']
        
        print(f"  Batch {i//batch_size + 1}: {stats['inserted']} inserted, {stats['duplicates']} duplicates")
    
    print()
    print("=" * 60)
    print("Upload Complete!")
    print("=" * 60)
    print(f"Total articles processed:  {len(articles)}")
    print(f"New articles inserted:     {total_inserted}")
    print(f"Duplicate articles:        {total_duplicates}")
    
    final_count = db.get_article_count()
    print(f"Total articles in database: {final_count}")
    
    return True

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Summarize and upload articles to PostgreSQL')
    parser.add_argument('csv_file', nargs='?', help='CSV file path (or auto-detect latest)')
    parser.add_argument('--no-summarize', action='store_true', help='Skip summarization')
    parser.add_argument('--method', choices=['sumy', 'tfidf', 'simple'], 
                       default='simple', help='Summarization method')
    
    args = parser.parse_args()
    
    # Update settings
    global SUMMARIZE, SUMMARY_METHOD
    SUMMARIZE = not args.no_summarize
    SUMMARY_METHOD = args.method
    
    # Get CSV file
    if args.csv_file:
        csv_file = args.csv_file
    else:
        # Find latest combined file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data', 'raw')
        
        import glob
        combined_files = glob.glob(os.path.join(data_dir, 'articles_combined_*.csv'))
        if not combined_files:
            print("No combined CSV file found.")
            print("Usage: python summarize_and_upload.py <csv_file>")
            return
        
        csv_file = max(combined_files, key=os.path.getmtime)
        print(f"Using: {os.path.basename(csv_file)}")
    
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return
    
    print("=" * 60)
    print("Summarize and Upload to PostgreSQL")
    print("=" * 60)
    print()
    
    # Connect to database
    db = DatabaseManager()
    print("Connecting to PostgreSQL database...")
    if not db.connect():
        print("\nFailed to connect to database.")
        print("Make sure Docker container is running: docker-compose up -d")
        return
    
    initial_count = db.get_article_count()
    print(f"Current articles in database: {initial_count}")
    print()
    
    # Confirm (skip in non-interactive mode)
    try:
        response = input(f"Ready to process {csv_file}.\nContinue? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            db.disconnect()
            return
    except EOFError:
        # Non-interactive mode, proceed automatically
        print(f"Processing {csv_file}...")
        print()
    
    # Process and upload
    success = summarize_and_upload(csv_file, db)
    
    if success:
        print("\nSUCCESS! Articles uploaded to database.")
    else:
        print("\nUpload failed. Please check errors above.")
    
    db.disconnect()

if __name__ == "__main__":
    main()

