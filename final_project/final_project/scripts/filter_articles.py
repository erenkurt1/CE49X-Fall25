"""
Article Filtering Script
Filters out unrelated articles based on keyword matching and relevance scoring.
Keeps only articles that are actually about Civil Engineering AND AI/ML.
"""

import pandas as pd
import re
from typing import List, Tuple

# Civil Engineering keywords (must have at least one)
CE_KEYWORDS = [
    # Core terms
    'construction', 'structural', 'geotechnical', 'transportation', 
    'infrastructure', 'concrete', 'bridge', 'tunnel', 'highway', 'road',
    'building', 'civil engineering', 'construction management',
    'construction site', 'construction project', 'construction industry',
    'structural engineering', 'structural design', 'structural analysis',
    'geotechnical engineering', 'foundation', 'soil', 'excavation',
    'transportation engineering', 'traffic', 'logistics',
    'infrastructure project', 'infrastructure development',
    'construction safety', 'construction technology', 'construction equipment',
    'architect', 'architecture', 'building design', 'building materials',
    'construction waste', 'construction cost', 'construction planning',
    'site management', 'project management', 'construction automation',
]

# AI/ML keywords (must have at least one)
AI_KEYWORDS = [
    'artificial intelligence', 'ai', 'machine learning', 'ml',
    'computer vision', 'deep learning', 'neural network', 'neural networks',
    'generative ai', 'generative design', 'predictive analytics',
    'robotics', 'automation', 'automated', 'autonomous',
    'data science', 'data analytics', 'algorithm', 'algorithms',
    'intelligent', 'smart', 'digital twin', 'iot', 'internet of things',
    'bim', 'building information modeling', 'parametric design',
    'optimization', 'predictive', 'forecast', 'modeling', 'simulation',
]

# Exclusion keywords (if these appear prominently, likely unrelated)
EXCLUSION_KEYWORDS = [
    # Medical/healthcare
    'patient', 'disease', 'cancer', 'leukemia', 'medical', 'healthcare',
    'hospital', 'clinical', 'treatment', 'therapy', 'diagnosis',
    # General AI (not construction-related)
    'data center', 'datacenter', 'server', 'cloud computing', 'software',
    'app', 'application', 'platform', 'startup', 'venture capital',
    # Unrelated topics
    'accounting', 'finance', 'investment', 'stock', 'market',
    'education', 'student', 'school', 'university', 'course',
    'game', 'gaming', 'entertainment', 'movie', 'film',
]

# Context-specific exclusions (phrases that indicate unrelated content)
EXCLUSION_PHRASES = [
    'data center construction',  # Usually about tech infrastructure, not civil engineering
    'ai construction cost',  # Often about accounting/finance
    'construction of a model',  # Often about ML models, not buildings
    'risk prediction model',  # Often medical
    'construction and validation',  # Often about ML model validation
]

def count_keywords(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in text"""
    if not text or pd.isna(text):
        return 0
    
    text_lower = str(text).lower()
    count = 0
    for keyword in keywords:
        if keyword.lower() in text_lower:
            count += 1
    return count

def has_exclusion_keywords(text: str, threshold: int = 2) -> bool:
    """Check if text has too many exclusion keywords"""
    if not text or pd.isna(text):
        return False
    
    text_lower = str(text).lower()
    exclusion_count = 0
    
    # Check exclusion phrases first (stronger signal)
    for phrase in EXCLUSION_PHRASES:
        if phrase.lower() in text_lower:
            return True  # Immediate exclusion
    
    # Count exclusion keywords
    for keyword in EXCLUSION_KEYWORDS:
        if keyword.lower() in text_lower:
            exclusion_count += 1
            if exclusion_count >= threshold:
                return True
    
    return False

def calculate_relevance_score(row: pd.Series) -> Tuple[float, str]:
    """
    Calculate relevance score for an article
    
    Returns:
        (score, reason): Score (0-100) and reason for score
    """
    title = str(row.get('title', '')).lower()
    content = str(row.get('content', '')).lower()
    keywords = str(row.get('keywords', '')).lower()
    
    # Combine all text
    all_text = f"{title} {content} {keywords}"
    
    # Check exclusions first
    if has_exclusion_keywords(all_text):
        return 0.0, "Contains exclusion keywords/phrases"
    
    # Count CE keywords
    ce_count = count_keywords(all_text, CE_KEYWORDS)
    
    # Count AI keywords
    ai_count = count_keywords(all_text, AI_KEYWORDS)
    
    # Must have at least one CE keyword
    if ce_count == 0:
        return 0.0, "No Civil Engineering keywords found"
    
    # Must have at least one AI keyword
    if ai_count == 0:
        return 0.0, "No AI/ML keywords found"
    
    # Calculate score based on keyword density
    # Base score: 50 if has both CE and AI
    score = 50.0
    
    # Bonus for multiple keywords
    score += min(ce_count * 5, 25)  # Up to 25 points for CE keywords
    score += min(ai_count * 5, 25)  # Up to 25 points for AI keywords
    
    # Bonus if keywords appear in title (more relevant)
    title_ce = count_keywords(title, CE_KEYWORDS)
    title_ai = count_keywords(title, AI_KEYWORDS)
    if title_ce > 0 and title_ai > 0:
        score += 10  # Both in title = very relevant
    
    # Penalty for very short content
    if len(content) < 50:
        score -= 20
    
    # Ensure score is between 0 and 100
    score = max(0, min(100, score))
    
    reason = f"CE keywords: {ce_count}, AI keywords: {ai_count}"
    if title_ce > 0 and title_ai > 0:
        reason += " (both in title)"
    
    return score, reason

def filter_articles(df: pd.DataFrame, min_score: float = 30.0) -> Tuple[pd.DataFrame, List[float], List[str]]:
    """
    Filter articles based on relevance score
    
    Args:
        df: DataFrame with articles
        min_score: Minimum relevance score to keep (0-100)
    
    Returns:
        (filtered_df, scores, reasons): Filtered DataFrame, scores list, reasons list
    """
    print(f"Filtering {len(df)} articles...")
    print(f"Minimum score threshold: {min_score}")
    print()
    
    # Calculate scores
    scores = []
    reasons = []
    
    for idx, row in df.iterrows():
        score, reason = calculate_relevance_score(row)
        scores.append(score)
        reasons.append(reason)
    
    # Add scores to dataframe
    df_filtered = df.copy()
    df_filtered['relevance_score'] = scores
    df_filtered['filter_reason'] = reasons
    
    # Filter by score
    initial_count = len(df_filtered)
    df_filtered = df_filtered[df_filtered['relevance_score'] >= min_score]
    filtered_count = len(df_filtered)
    removed_count = initial_count - filtered_count
    
    print(f"Results:")
    print(f"  Initial articles:     {initial_count}")
    print(f"  Articles kept:        {filtered_count}")
    print(f"  Articles removed:     {removed_count}")
    print(f"  Retention rate:      {filtered_count/initial_count*100:.1f}%")
    print()
    
    # Show score distribution
    if len(scores) > 0:
        print(f"Score distribution:")
        print(f"  Average score:       {sum(scores)/len(scores):.1f}")
        print(f"  Min score:           {min(scores):.1f}")
        print(f"  Max score:           {max(scores):.1f}")
        print(f"  Articles with score >= 50: {sum(1 for s in scores if s >= 50)}")
        print(f"  Articles with score >= 70: {sum(1 for s in scores if s >= 70)}")
        print()
    
    # Show some removed articles (for review)
    if removed_count > 0:
        print("Sample of removed articles (low scores):")
        # Create a dataframe with all articles and their scores
        df_with_scores = df.copy()
        df_with_scores['relevance_score'] = scores
        df_with_scores['filter_reason'] = reasons
        
        # Get removed articles (those not in filtered)
        removed_articles = df_with_scores[df_with_scores['relevance_score'] < min_score]
        removed_articles = removed_articles.sort_values('relevance_score', ascending=True)
        
        for idx, row in removed_articles.head(5).iterrows():
            print(f"  [{row['relevance_score']:.1f}] {row['title'][:80]}...")
            print(f"      Reason: {row['filter_reason']}")
        print()
    
    return df_filtered, scores, reasons

def main():
    """Main filtering function"""
    import sys
    import os
    
    # Get input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Find latest CSV file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, 'data', 'raw')
        
        import glob
        csv_files = glob.glob(os.path.join(data_dir, 'articles*.csv'))
        if not csv_files:
            print("No CSV files found in data/raw/")
            print("Usage: python filter_articles.py <input_csv_file>")
            return
        
        # Get most recent
        input_file = max(csv_files, key=os.path.getmtime)
        print(f"Using most recent file: {os.path.basename(input_file)}")
    
    # Get min score threshold
    min_score = 30.0
    if len(sys.argv) > 2:
        try:
            min_score = float(sys.argv[2])
        except:
            pass
    
    print("=" * 60)
    print("Article Filtering Tool")
    print("=" * 60)
    print()
    print(f"Input file:  {input_file}")
    print(f"Min score:   {min_score}")
    print()
    
    # Load data
    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        print(f"Loaded {len(df)} articles")
    except Exception as e:
        print(f"Error loading file: {e}")
        return
    
    # Filter
    df_filtered, scores, reasons = filter_articles(df, min_score=min_score)
    
    # Save filtered data
    output_file = input_file.replace('.csv', '_filtered.csv')
    if '_filtered' in input_file:
        output_file = input_file  # Don't double-filter
    
    df_filtered.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Filtered data saved to: {output_file}")
    
    # Save removed articles (for review)
    df_with_scores = df.copy()
    df_with_scores['relevance_score'] = scores
    df_with_scores['filter_reason'] = reasons
    removed = df_with_scores[df_with_scores['relevance_score'] < min_score]
    
    if len(removed) > 0:
        removed_file = input_file.replace('.csv', '_removed.csv')
        removed.to_csv(removed_file, index=False, encoding='utf-8')
        print(f"Removed articles saved to: {removed_file}")
    
    print()
    print("=" * 60)
    if len(df_filtered) >= 500:
        print(f"SUCCESS! {len(df_filtered)} relevant articles (>= 500)")
    else:
        print(f"Need {500 - len(df_filtered)} more articles")
        print("Suggestions:")
        print("  - Lower min_score threshold (currently {min_score})")
        print("  - Collect more articles")
        print("  - Review removed articles to adjust filters")

if __name__ == "__main__":
    main()

