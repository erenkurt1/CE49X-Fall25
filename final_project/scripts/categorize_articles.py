"""
Article Categorization - Task 3
Classifies articles by Civil Engineering areas and AI technologies.
Creates co-occurrence matrix and generates heatmap visualization.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from datetime import datetime

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

# Civil Engineering Areas - Keywords
CE_AREAS = {
    'Structural': [
        'structural', 'structure', 'beam', 'column', 'frame', 'load',
        'analysis', 'design', 'health monitoring', 'structural health',
        'materials', 'steel', 'concrete structure', 'building structure',
        'structural engineering', 'structural analysis', 'structural design'
    ],
    'Geotechnical': [
        'geotechnical', 'soil', 'foundation', 'tunnel', 'excavation',
        'slope', 'retaining wall', 'earth', 'ground', 'subsoil',
        'geotechnical engineering', 'foundation design', 'soil mechanics',
        'tunneling', 'excavation', 'slope stability'
    ],
    'Transportation': [
        'transportation', 'traffic', 'road', 'highway', 'bridge',
        'autonomous vehicle', 'logistics', 'transport', 'roadway',
        'transportation engineering', 'traffic management', 'road design',
        'bridge design', 'highway design', 'transportation system'
    ],
    'Construction Management': [
        'construction management', 'scheduling', 'safety', 'cost estimation',
        'site monitoring', 'project management', 'construction site',
        'construction project', 'construction planning', 'construction safety',
        'project scheduling', 'cost control', 'site management'
    ],
    'Environmental Engineering': [
        'environmental', 'sustainability', 'waste management', 'green building',
        'environmental engineering', 'sustainable', 'waste', 'recycling',
        'environmental impact', 'green construction', 'sustainable design',
        'environmental sustainability'
    ]
}

# AI Technologies - Keywords
AI_TECHNOLOGIES = {
    'Computer Vision': [
        'computer vision', 'image recognition', 'drone inspection',
        'safety monitoring', 'visual', 'image', 'video', 'camera',
        'visual inspection', 'image processing', 'visual recognition',
        'drone', 'aerial', 'photogrammetry'
    ],
    'Predictive Analytics': [
        'predictive', 'forecast', 'prediction', 'risk assessment',
        'maintenance prediction', 'predictive maintenance', 'forecasting',
        'predictive model', 'risk prediction', 'failure prediction'
    ],
    'Generative Design': [
        'generative design', 'optimization', 'parametric modeling',
        'generative', 'optimize', 'parametric', 'design optimization',
        'generative ai', 'design generation', 'automated design'
    ],
    'Robotics/Automation': [
        'robot', 'robotics', 'automation', 'autonomous', 'robotic',
        'automated', 'automate', 'robotic system', 'autonomous system',
        'construction robot', 'automated construction', 'robotic construction'
    ],
    'Machine Learning': [
        'machine learning', 'ml', 'neural network', 'deep learning',
        'algorithm', 'model training', 'supervised learning',
        'unsupervised learning', 'reinforcement learning'
    ],
    'Artificial Intelligence': [
        'artificial intelligence', 'ai', 'intelligent system',
        'ai system', 'intelligent', 'ai technology', 'ai application'
    ]
}


def match_keywords(text, keywords):
    """
    Check if any keywords match in text (case-insensitive)
    
    Args:
        text: Text to search in
        keywords: List of keywords to search for
    
    Returns:
        Number of matching keywords
    """
    if not text or pd.isna(text):
        return 0
    
    text_lower = str(text).lower()
    matches = 0
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matches += 1
    
    return matches


def classify_article(row):
    """
    Classify an article into CE areas and AI technologies
    
    Args:
        row: DataFrame row with article data
    
    Returns:
        Dictionary with classifications
    """
    # Combine title and content for matching
    text = f"{row.get('title', '')} {row.get('content', '')} {row.get('processed_text', '')}"
    
    # Classify CE areas
    ce_tags = []
    ce_scores = {}
    for area, keywords in CE_AREAS.items():
        score = match_keywords(text, keywords)
        if score > 0:
            ce_tags.append(area)
            ce_scores[area] = score
    
    # Classify AI technologies
    ai_tags = []
    ai_scores = {}
    for tech, keywords in AI_TECHNOLOGIES.items():
        score = match_keywords(text, keywords)
        if score > 0:
            ai_tags.append(tech)
            ai_scores[tech] = score
    
    return {
        'ce_areas': ce_tags,
        'ai_technologies': ai_tags,
        'ce_scores': ce_scores,
        'ai_scores': ai_scores,
        'num_ce_tags': len(ce_tags),
        'num_ai_tags': len(ai_tags)
    }


def create_cooccurrence_matrix(df):
    """
    Create co-occurrence matrix: CE Areas × AI Technologies
    
    Args:
        df: DataFrame with classified articles
    
    Returns:
        Co-occurrence matrix as DataFrame
    """
    # Initialize matrix
    ce_areas = list(CE_AREAS.keys())
    ai_techs = list(AI_TECHNOLOGIES.keys())
    
    matrix = np.zeros((len(ce_areas), len(ai_techs)))
    
    # Count co-occurrences
    for idx, row in df.iterrows():
        ce_tags = row.get('ce_areas', [])
        ai_tags = row.get('ai_technologies', [])
        
        for ce_area in ce_tags:
            for ai_tech in ai_tags:
                ce_idx = ce_areas.index(ce_area)
                ai_idx = ai_techs.index(ai_tech)
                matrix[ce_idx, ai_idx] += 1
    
    # Create DataFrame
    cooccurrence_df = pd.DataFrame(
        matrix,
        index=ce_areas,
        columns=ai_techs
    )
    
    return cooccurrence_df


def visualize_heatmap(cooccurrence_df, output_file=None):
    """
    Create heatmap visualization of co-occurrence matrix
    
    Args:
        cooccurrence_df: Co-occurrence matrix DataFrame
        output_file: Output file path
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create heatmap
    sns.heatmap(
        cooccurrence_df,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Number of Articles'},
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    ax.set_title(
        'Co-occurrence Matrix: Civil Engineering Areas vs AI Technologies',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    ax.set_xlabel('AI Technologies', fontsize=12, fontweight='bold')
    ax.set_ylabel('Civil Engineering Areas', fontsize=12, fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save
    if output_file is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'visualizations')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'cooccurrence_heatmap.png')
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved heatmap: {output_file}")
    plt.close()
    
    return output_file


def main():
    """Main categorization function"""
    print("=" * 60)
    print("CE49X Final Project - Task 3: Categorization & Trend Analysis")
    print("=" * 60)
    print()
    
    # Load data from database
    print("Loading articles from PostgreSQL...")
    db = DatabaseManager()
    
    if not db.connect():
        print("Failed to connect to database.")
        print("Make sure Docker container is running: docker-compose up -d")
        return
    
    # Query articles
    query = """
        SELECT id, title, content, keywords, publication_date
        FROM articles
        ORDER BY id
    """
    
    df = pd.read_sql_query(query, db.conn)
    db.disconnect()
    
    print(f"Loaded {len(df)} articles")
    print()
    
    # Try to load processed text if available
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    processed_files = [f for f in os.listdir(processed_dir) if f.startswith('articles_processed_') and f.endswith('.csv')]
    
    if processed_files:
        latest_processed = max(processed_files, key=lambda f: os.path.getmtime(os.path.join(processed_dir, f)))
        processed_df = pd.read_csv(os.path.join(processed_dir, latest_processed))
        # Merge processed text
        df = df.merge(processed_df[['id', 'processed_text']], on='id', how='left')
        print(f"Loaded processed text from: {latest_processed}")
    else:
        df['processed_text'] = ''
    
    print()
    print("Classifying articles...")
    print("(This may take a minute)")
    print()
    
    # Classify articles
    classifications = []
    for idx, row in df.iterrows():
        classification = classify_article(row)
        classifications.append(classification)
        
        if (idx + 1) % 100 == 0:
            print(f"  Classified {idx + 1}/{len(df)} articles...")
    
    # Add classifications to dataframe
    df['ce_areas'] = [c['ce_areas'] for c in classifications]
    df['ai_technologies'] = [c['ai_technologies'] for c in classifications]
    df['num_ce_tags'] = [c['num_ce_tags'] for c in classifications]
    df['num_ai_tags'] = [c['num_ai_tags'] for c in classifications]
    
    print(f"Classified {len(df)} articles")
    print()
    
    # Calculate statistics
    print("Calculating statistics...")
    print()
    
    # CE Areas statistics
    ce_counts = defaultdict(int)
    for ce_tags in df['ce_areas']:
        for area in ce_tags:
            ce_counts[area] += 1
    
    # AI Technologies statistics
    ai_counts = defaultdict(int)
    for ai_tags in df['ai_technologies']:
        for tech in ai_tags:
            ai_counts[tech] += 1
    
    # Create co-occurrence matrix
    cooccurrence_df = create_cooccurrence_matrix(df)
    
    # Save results
    results_dir = os.path.join(project_root, 'data', 'processed')
    os.makedirs(results_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save classified articles
    classified_file = os.path.join(results_dir, f'articles_classified_{timestamp}.csv')
    # Convert lists to strings for CSV
    df_save = df.copy()
    df_save['ce_areas'] = df_save['ce_areas'].apply(lambda x: ', '.join(x) if x else '')
    df_save['ai_technologies'] = df_save['ai_technologies'].apply(lambda x: ', '.join(x) if x else '')
    df_save.to_csv(classified_file, index=False, encoding='utf-8')
    print(f"Saved classified articles: {classified_file}")
    
    # Save co-occurrence matrix
    matrix_file = os.path.join(results_dir, f'cooccurrence_matrix_{timestamp}.csv')
    cooccurrence_df.to_csv(matrix_file, encoding='utf-8')
    print(f"Saved co-occurrence matrix: {matrix_file}")
    
    # Generate heatmap
    print()
    print("Generating heatmap visualization...")
    visualize_heatmap(cooccurrence_df)
    
    # Print statistics
    print()
    print("=" * 60)
    print("Classification Results")
    print("=" * 60)
    print()
    
    print("Civil Engineering Areas:")
    for area, count in sorted(ce_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {area:30s}: {count:4d} articles ({percentage:5.1f}%)")
    print()
    
    print("AI Technologies:")
    for tech, count in sorted(ai_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        print(f"  {tech:30s}: {count:4d} articles ({percentage:5.1f}%)")
    print()
    
    print("Co-occurrence Matrix (Top combinations):")
    # Flatten matrix and get top combinations
    top_combinations = []
    for ce_area in cooccurrence_df.index:
        for ai_tech in cooccurrence_df.columns:
            count = cooccurrence_df.loc[ce_area, ai_tech]
            if count > 0:
                top_combinations.append((ce_area, ai_tech, count))
    
    top_combinations.sort(key=lambda x: x[2], reverse=True)
    for ce_area, ai_tech, count in top_combinations[:10]:
        print(f"  {ce_area:25s} × {ai_tech:30s}: {int(count):3d} articles")
    print()
    
    # Answer the main question
    print("=" * 60)
    print("ANSWER: Which CE Area Uses AI Most?")
    print("=" * 60)
    print()
    
    # Calculate total AI usage per CE area
    ce_ai_usage = {}
    for ce_area in CE_AREAS.keys():
        total = cooccurrence_df.loc[ce_area].sum()
        ce_ai_usage[ce_area] = total
    
    sorted_areas = sorted(ce_ai_usage.items(), key=lambda x: x[1], reverse=True)
    
    print("Ranking by AI usage:")
    for rank, (area, count) in enumerate(sorted_areas, 1):
        print(f"  {rank}. {area:30s}: {int(count):4d} articles with AI technologies")
    
    print()
    print(f"Winner: {sorted_areas[0][0]} with {int(sorted_areas[0][1])} articles!")
    print()
    
    # Save report
    report_file = os.path.join(results_dir, f'categorization_report_{timestamp}.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("CE49X Final Project - Task 3: Categorization Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total articles analyzed: {len(df)}\n\n")
        
        f.write("Civil Engineering Areas:\n")
        for area, count in sorted(ce_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(df)) * 100
            f.write(f"  {area:30s}: {count:4d} articles ({percentage:5.1f}%)\n")
        f.write("\n")
        
        f.write("AI Technologies:\n")
        for tech, count in sorted(ai_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(df)) * 100
            f.write(f"  {tech:30s}: {count:4d} articles ({percentage:5.1f}%)\n")
        f.write("\n")
        
        f.write("CE Area AI Usage Ranking:\n")
        for rank, (area, count) in enumerate(sorted_areas, 1):
            f.write(f"  {rank}. {area:30s}: {int(count):4d} articles\n")
        f.write("\n")
        
        f.write("Top 10 CE Area × AI Technology Combinations:\n")
        for ce_area, ai_tech, count in top_combinations[:10]:
            f.write(f"  {ce_area:25s} × {ai_tech:30s}: {int(count):3d} articles\n")
    
    print(f"Report saved: {report_file}")
    print()
    print("=" * 60)
    print("Task 3 Complete!")
    print("=" * 60)
    print()
    print("Deliverables created:")
    print(f"  1. Classified articles: {classified_file}")
    print(f"  2. Co-occurrence matrix: {matrix_file}")
    print(f"  3. Heatmap visualization: visualizations/cooccurrence_heatmap.png")
    print(f"  4. Analysis report: {report_file}")
    print()
    print("Next step: Task 4 - Visualization & Insights")


if __name__ == "__main__":
    main()





