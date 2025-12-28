"""
Combine Multiple CSV Files
Combines multiple article CSV files, removes duplicates, and optionally filters.
"""

import pandas as pd
import os
import sys
import glob
from pathlib import Path

def combine_csv_files(csv_files, output_file, remove_duplicates=True, filter_articles=False):
    """
    Combine multiple CSV files into one
    
    Args:
        csv_files: List of CSV file paths
        output_file: Output file path
        remove_duplicates: Remove duplicate articles (by URL)
        filter_articles: Apply filtering (requires filter_articles module)
    """
    print("=" * 60)
    print("Combining CSV Files")
    print("=" * 60)
    print()
    
    all_articles = []
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"Warning: File not found: {csv_file}")
            continue
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            print(f"Loaded {len(df)} articles from {os.path.basename(csv_file)}")
            all_articles.append(df)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    if not all_articles:
        print("No articles to combine!")
        return
    
    # Combine all dataframes
    combined = pd.concat(all_articles, ignore_index=True)
    print(f"\nTotal articles before deduplication: {len(combined)}")
    
    # Remove duplicates by URL
    if remove_duplicates:
        initial_count = len(combined)
        combined = combined.drop_duplicates(subset=['url'], keep='first')
        duplicates_removed = initial_count - len(combined)
        print(f"Duplicates removed: {duplicates_removed}")
        print(f"Unique articles: {len(combined)}")
    
    # Filter if requested
    if filter_articles:
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from filter_articles import filter_articles
            combined, scores, reasons = filter_articles(combined, min_score=30.0)
            print(f"After filtering: {len(combined)} articles")
        except Exception as e:
            print(f"Warning: Could not filter articles: {e}")
    
    # Save combined file
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    combined.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\nCombined file saved: {output_file}")
    print(f"Total articles: {len(combined)}")
    
    if len(combined) >= 500:
        print(f"\nSUCCESS! {len(combined)} articles (>= 500)")
    else:
        print(f"\nNeed {500 - len(combined)} more articles")
    
    return combined

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Combine multiple CSV files')
    parser.add_argument('files', nargs='*', help='CSV files to combine (or use --auto to find all)')
    parser.add_argument('--auto', action='store_true', help='Automatically find all CSV files in data/raw/')
    parser.add_argument('--output', default=None, help='Output file path')
    parser.add_argument('--no-dedup', action='store_true', help='Do not remove duplicates')
    parser.add_argument('--filter', action='store_true', help='Apply filtering after combining')
    
    args = parser.parse_args()
    
    # Get files
    if args.auto:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data', 'raw')
        csv_files = glob.glob(os.path.join(data_dir, 'articles*.csv'))
        csv_files = [f for f in csv_files if '_combined' not in f and '_filtered' not in f]
        csv_files.sort(key=os.path.getmtime, reverse=True)  # Most recent first
    else:
        csv_files = args.files
    
    if not csv_files:
        print("No CSV files found!")
        print("Usage: python combine_csv_files.py file1.csv file2.csv ...")
        print("   or: python combine_csv_files.py --auto")
        return
    
    print(f"Found {len(csv_files)} files to combine:")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")
    print()
    
    # Output file
    if args.output:
        output_file = args.output
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data', 'raw')
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(data_dir, f'articles_combined_{timestamp}.csv')
    
    # Combine
    combine_csv_files(
        csv_files,
        output_file,
        remove_duplicates=not args.no_dedup,
        filter_articles=args.filter
    )

if __name__ == "__main__":
    main()


