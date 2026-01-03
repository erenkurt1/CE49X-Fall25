"""
Visualize N-grams
Creates visualizations for bigrams and trigrams from preprocessing results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

def load_ngrams_data(ngrams_file=None):
    """Load n-grams data from CSV"""
    if ngrams_file is None:
        # Find latest ngrams file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        processed_dir = os.path.join(project_root, 'data', 'processed')
        ngrams_files = list(Path(processed_dir).glob('ngrams_*.csv'))
        if not ngrams_files:
            print("No ngrams file found!")
            return None
        ngrams_file = max(ngrams_files, key=lambda p: p.stat().st_mtime)
        print(f"Using: {ngrams_file.name}")
    
    df = pd.read_csv(ngrams_file)
    return df

def visualize_bigrams(df, top_n=20, output_dir=None):
    """Create visualization for top bigrams"""
    # Filter bigrams
    bigrams = df[df['type'] == 'bigram'].copy()
    bigrams = bigrams.nlargest(top_n, 'frequency')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create horizontal bar chart
    colors = sns.color_palette("viridis", len(bigrams))
    bars = ax.barh(range(len(bigrams)), bigrams['frequency'].values, color=colors)
    
    # Customize
    ax.set_yticks(range(len(bigrams)))
    ax.set_yticklabels(bigrams['phrase'].values, fontsize=11)
    ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Bigrams in Civil Engineering & AI Articles', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(bigrams.iterrows()):
        ax.text(row['frequency'] + 1, i, f"{int(row['frequency'])}", 
                va='center', fontsize=10, fontweight='bold')
    
    # Invert y-axis to show highest at top
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    # Save
    if output_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'top_bigrams.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file

def visualize_trigrams(df, top_n=20, output_dir=None):
    """Create visualization for top trigrams"""
    # Filter trigrams
    trigrams = df[df['type'] == 'trigram'].copy()
    trigrams = trigrams.nlargest(top_n, 'frequency')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create horizontal bar chart
    colors = sns.color_palette("plasma", len(trigrams))
    bars = ax.barh(range(len(trigrams)), trigrams['frequency'].values, color=colors)
    
    # Customize
    ax.set_yticks(range(len(trigrams)))
    ax.set_yticklabels(trigrams['phrase'].values, fontsize=10)
    ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Trigrams in Civil Engineering & AI Articles', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(trigrams.iterrows()):
        ax.text(row['frequency'] + 0.3, i, f"{int(row['frequency'])}", 
                va='center', fontsize=9, fontweight='bold')
    
    # Invert y-axis to show highest at top
    ax.invert_yaxis()
    
    plt.tight_layout()
    
    # Save
    if output_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'top_trigrams.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file

def visualize_bigrams_wordcloud(df, top_n=30, output_dir=None):
    """Create word cloud for bigrams"""
    try:
        from wordcloud import WordCloud
    except ImportError:
        print("WordCloud not available. Install with: pip install wordcloud")
        return None
    
    # Filter bigrams
    bigrams = df[df['type'] == 'bigram'].copy()
    bigrams = bigrams.nlargest(top_n, 'frequency')
    
    # Create frequency dictionary
    freq_dict = dict(zip(bigrams['phrase'], bigrams['frequency']))
    
    # Create word cloud
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        colormap='viridis',
        max_words=top_n,
        relative_scaling=0.5,
        collocations=False
    ).generate_from_frequencies(freq_dict)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Top Bigrams Word Cloud', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save
    if output_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'bigrams_wordcloud.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file

def visualize_combined_ngrams(df, output_dir=None):
    """Create combined visualization showing both bigrams and trigrams"""
    bigrams = df[df['type'] == 'bigram'].nlargest(15, 'frequency')
    trigrams = df[df['type'] == 'trigram'].nlargest(15, 'frequency')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10))
    
    # Bigrams
    colors1 = sns.color_palette("viridis", len(bigrams))
    ax1.barh(range(len(bigrams)), bigrams['frequency'].values, color=colors1)
    ax1.set_yticks(range(len(bigrams)))
    ax1.set_yticklabels(bigrams['phrase'].values, fontsize=10)
    ax1.set_xlabel('Frequency', fontsize=12, fontweight='bold')
    ax1.set_title('Top 15 Bigrams', fontsize=13, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    # Add labels
    for i, (idx, row) in enumerate(bigrams.iterrows()):
        ax1.text(row['frequency'] + 1, i, f"{int(row['frequency'])}", 
                va='center', fontsize=9, fontweight='bold')
    
    # Trigrams
    colors2 = sns.color_palette("plasma", len(trigrams))
    ax2.barh(range(len(trigrams)), trigrams['frequency'].values, color=colors2)
    ax2.set_yticks(range(len(trigrams)))
    ax2.set_yticklabels(trigrams['phrase'].values, fontsize=9)
    ax2.set_xlabel('Frequency', fontsize=12, fontweight='bold')
    ax2.set_title('Top 15 Trigrams', fontsize=13, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    ax2.invert_yaxis()
    
    # Add labels
    for i, (idx, row) in enumerate(trigrams.iterrows()):
        ax2.text(row['frequency'] + 0.3, i, f"{int(row['frequency'])}", 
                va='center', fontsize=8, fontweight='bold')
    
    plt.suptitle('N-grams Analysis: Civil Engineering & AI Articles', 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Save
    if output_dir is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, 'ngrams_combined.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file

def main():
    """Main visualization function"""
    print("=" * 60)
    print("N-grams Visualization Generator")
    print("=" * 60)
    print()
    
    # Load data
    df = load_ngrams_data()
    if df is None:
        return
    
    print(f"Loaded n-grams data:")
    print(f"  Bigrams: {len(df[df['type'] == 'bigram'])}")
    print(f"  Trigrams: {len(df[df['type'] == 'trigram'])}")
    print()
    
    # Create output directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating visualizations...")
    print()
    
    # Generate visualizations
    try:
        visualize_bigrams(df, top_n=20, output_dir=output_dir)
        visualize_trigrams(df, top_n=20, output_dir=output_dir)
        visualize_combined_ngrams(df, output_dir=output_dir)
        visualize_bigrams_wordcloud(df, top_n=30, output_dir=output_dir)
    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=" * 60)
    print("Visualization Complete!")
    print("=" * 60)
    print()
    print("Generated files:")
    print(f"  1. top_bigrams.png - Bar chart of top 20 bigrams")
    print(f"  2. top_trigrams.png - Bar chart of top 20 trigrams")
    print(f"  3. ngrams_combined.png - Side-by-side comparison")
    print(f"  4. bigrams_wordcloud.png - Word cloud of bigrams")
    print()
    print(f"All files saved to: {output_dir}")

if __name__ == "__main__":
    main()





