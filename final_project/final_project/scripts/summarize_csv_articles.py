"""
Summarize Articles in CSV File
Adds summaries to articles in a CSV file to reduce storage space.
"""

import pandas as pd
import os
import sys
from tqdm import tqdm

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from article_summarizer import summarize_article

# Summarization settings
SUMMARY_METHOD = 'sumy'  # Options: 'sumy', 'tfidf', 'simple'
MAX_SUMMARY_SENTENCES = 3
MAX_SUMMARY_LENGTH = 500

def summarize_articles_in_csv(input_file, output_file=None, batch_size=50):
    """
    Summarize articles in a CSV file
    
    Args:
        input_file: Input CSV file path
        output_file: Output CSV file path (if None, adds _summarized suffix)
        batch_size: Process in batches to show progress
    """
    print("=" * 60)
    print("Article Summarization Tool")
    print("=" * 60)
    print()
    print(f"Input file:  {input_file}")
    print(f"Method:      {SUMMARY_METHOD}")
    print(f"Max sentences: {MAX_SUMMARY_SENTENCES}")
    print(f"Max length:    {MAX_SUMMARY_LENGTH} characters")
    print()
    
    # Load CSV
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"Loaded {len(df)} articles")
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Check if already has summarized content
    if 'content_summarized' in df.columns:
        print("Warning: File already has 'content_summarized' column")
        response = input("Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
    
    # Output file
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_summarized.csv"
    
    print(f"Output file: {output_file}")
    print()
    print("Summarizing articles...")
    print("(This may take a while for large files)")
    print()
    
    # Process articles
    original_lengths = []
    summarized_lengths = []
    failed_count = 0
    
    # Create progress bar
    tqdm.pandas(desc="Summarizing")
    
    def summarize_row(row):
        """Summarize a single row"""
        nonlocal failed_count
        
        content = str(row.get('content', ''))
        if not content or len(content.strip()) < 50:
            # Too short to summarize, return as-is
            return content
        
        original_length = len(content)
        original_lengths.append(original_length)
        
        try:
            # Summarize
            summary = summarize_article(
                content,
                method=SUMMARY_METHOD,
                max_sentences=MAX_SUMMARY_SENTENCES,
                max_length=MAX_SUMMARY_LENGTH
            )
            
            summarized_length = len(summary)
            summarized_lengths.append(summarized_length)
            
            return summary
        
        except Exception as e:
            failed_count += 1
            # Return original if summarization fails
            return content
    
    # Apply summarization
    df['content_summarized'] = df.progress_apply(summarize_row, axis=1)
    
    # Calculate statistics
    print()
    print("=" * 60)
    print("Summarization Complete!")
    print("=" * 60)
    
    if original_lengths and summarized_lengths:
        avg_original = sum(original_lengths) / len(original_lengths)
        avg_summarized = sum(summarized_lengths) / len(summarized_lengths)
        reduction = ((avg_original - avg_summarized) / avg_original * 100) if avg_original > 0 else 0
        
        print(f"Articles processed:        {len(df)}")
        print(f"Successfully summarized:   {len(summarized_lengths)}")
        print(f"Failed/skipped:           {failed_count}")
        print()
        print(f"Average original length:   {int(avg_original)} characters")
        print(f"Average summary length:    {int(avg_summarized)} characters")
        print(f"Space reduction:           {reduction:.1f}%")
        print()
        
        # Calculate total space saved
        total_original = sum(original_lengths)
        total_summarized = sum(summarized_lengths)
        total_saved = total_original - total_summarized
        print(f"Total space saved:        {total_saved:,} characters")
        print(f"                          ({total_saved/1024:.1f} KB)")
    
    # Save summarized file
    df.to_csv(output_file, index=False, encoding='utf-8')
    print()
    print(f"Summarized file saved: {output_file}")
    
    # Option to replace original content with summary
    print()
    response = input("Replace 'content' column with summaries? (y/n): ").strip().lower()
    if response == 'y':
        df['content'] = df['content_summarized']
        df = df.drop(columns=['content_summarized'])
        df.to_csv(output_file, index=False, encoding='utf-8')
        print("Original content replaced with summaries.")
    
    return output_file

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Summarize articles in CSV file')
    parser.add_argument('input_file', help='Input CSV file path')
    parser.add_argument('--output', '-o', default=None, help='Output file path')
    parser.add_argument('--method', choices=['sumy', 'tfidf', 'simple'], 
                       default='sumy', help='Summarization method')
    parser.add_argument('--sentences', type=int, default=3, 
                       help='Maximum sentences in summary')
    parser.add_argument('--length', type=int, default=500,
                       help='Maximum characters in summary')
    
    args = parser.parse_args()
    
    # Update global settings
    global SUMMARY_METHOD, MAX_SUMMARY_SENTENCES, MAX_SUMMARY_LENGTH
    SUMMARY_METHOD = args.method
    MAX_SUMMARY_SENTENCES = args.sentences
    MAX_SUMMARY_LENGTH = args.length
    
    # Summarize
    summarize_articles_in_csv(args.input_file, args.output)

if __name__ == "__main__":
    # If run without arguments, use interactive mode
    if len(sys.argv) == 1:
        # Find the combined file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data', 'raw')
        
        import glob
        combined_files = glob.glob(os.path.join(data_dir, 'articles_combined_*.csv'))
        if combined_files:
            # Get most recent
            latest_file = max(combined_files, key=os.path.getmtime)
            print(f"Found combined file: {os.path.basename(latest_file)}")
            print()
            summarize_articles_in_csv(latest_file)
        else:
            print("No combined CSV file found.")
            print("Usage: python summarize_csv_articles.py <input_file.csv>")
    else:
        main()


