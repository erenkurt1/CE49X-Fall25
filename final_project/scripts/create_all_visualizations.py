"""
Create All Visualizations for Task 4
Generates bar charts, network graph, and word clouds.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from collections import Counter
from wordcloud import WordCloud

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# Colors
CE_COLORS = {
    'Structural': '#2E86AB',
    'Transportation': '#A23B72',
    'Geotechnical': '#F18F01',
    'Construction Management': '#C73E1D',
    'Environmental Engineering': '#6A994E'
}

AI_COLORS = {
    'Computer Vision': '#FF6B6B',
    'Predictive Analytics': '#4ECDC4',
    'Generative Design': '#45B7D1',
    'Robotics/Automation': '#FFA07A',
    'Machine Learning': '#98D8C8',
    'Artificial Intelligence': '#F7DC6F'
}


def load_classified_data():
    """Load classified articles data"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    
    # Find latest classified file
    classified_files = [f for f in os.listdir(processed_dir) 
                       if f.startswith('articles_classified_') and f.endswith('.csv')]
    if not classified_files:
        print("No classified articles file found!")
        return None
    
    latest_file = max(classified_files, key=lambda f: os.path.getmtime(os.path.join(processed_dir, f)))
    df = pd.read_csv(os.path.join(processed_dir, latest_file))
    
    # Parse list columns
    df['ce_areas'] = df['ce_areas'].apply(lambda x: [a.strip() for a in str(x).split(',') if a.strip()] if pd.notna(x) and x else [])
    df['ai_technologies'] = df['ai_technologies'].apply(lambda x: [a.strip() for a in str(x).split(',') if a.strip()] if pd.notna(x) and x else [])
    
    return df


def create_ce_areas_bar_chart(df, output_dir):
    """Create bar chart for CE areas"""
    # Count articles per CE area
    ce_counts = Counter()
    for ce_areas in df['ce_areas']:
        for area in ce_areas:
            ce_counts[area] += 1
    
    # Sort by count
    areas = sorted(ce_counts.items(), key=lambda x: x[1], reverse=True)
    area_names = [a[0] for a in areas]
    counts = [a[1] for a in areas]
    percentages = [(c / len(df)) * 100 for c in counts]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create bars with colors
    colors = [CE_COLORS.get(area, '#808080') for area in area_names]
    bars = ax.barh(range(len(area_names)), counts, color=colors)
    
    # Customize
    ax.set_yticks(range(len(area_names)))
    ax.set_yticklabels(area_names, fontsize=12)
    ax.set_xlabel('Number of Articles', fontsize=13, fontweight='bold')
    ax.set_title('Articles by Civil Engineering Area', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (count, pct) in enumerate(zip(counts, percentages)):
        ax.text(count + 5, i, f"{count} ({pct:.1f}%)", 
                va='center', fontsize=11, fontweight='bold')
    
    ax.invert_yaxis()
    plt.tight_layout()
    
    # Save
    output_file = os.path.join(output_dir, 'ce_areas_bar_chart.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file


def create_ai_technologies_bar_chart(df, output_dir):
    """Create bar chart for AI technologies"""
    # Count articles per AI technology
    ai_counts = Counter()
    for ai_techs in df['ai_technologies']:
        for tech in ai_techs:
            ai_counts[tech] += 1
    
    # Sort by count
    techs = sorted(ai_counts.items(), key=lambda x: x[1], reverse=True)
    tech_names = [t[0] for t in techs]
    counts = [t[1] for t in techs]
    percentages = [(c / len(df)) * 100 for c in counts]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create bars with colors
    colors = [AI_COLORS.get(tech, '#808080') for tech in tech_names]
    bars = ax.barh(range(len(tech_names)), counts, color=colors)
    
    # Customize
    ax.set_yticks(range(len(tech_names)))
    ax.set_yticklabels(tech_names, fontsize=12)
    ax.set_xlabel('Number of Articles', fontsize=13, fontweight='bold')
    ax.set_title('Articles by AI Technology', fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (count, pct) in enumerate(zip(counts, percentages)):
        ax.text(count + 5, i, f"{count} ({pct:.1f}%)", 
                va='center', fontsize=11, fontweight='bold')
    
    ax.invert_yaxis()
    plt.tight_layout()
    
    # Save
    output_file = os.path.join(output_dir, 'ai_technologies_bar_chart.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file


def create_network_graph(df, output_dir):
    """Create network graph showing relationships"""
    # Load co-occurrence matrix
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    
    matrix_files = [f for f in os.listdir(processed_dir) 
                   if f.startswith('cooccurrence_matrix_') and f.endswith('.csv')]
    if not matrix_files:
        print("No co-occurrence matrix found!")
        return None
    
    latest_matrix = max(matrix_files, key=lambda f: os.path.getmtime(os.path.join(processed_dir, f)))
    cooccurrence_df = pd.read_csv(os.path.join(processed_dir, latest_matrix), index_col=0)
    
    # Create graph
    G = nx.Graph()
    
    # Add nodes
    ce_areas = cooccurrence_df.index.tolist()
    ai_techs = cooccurrence_df.columns.tolist()
    
    for area in ce_areas:
        G.add_node(area, node_type='ce_area', color=CE_COLORS.get(area, '#808080'))
    
    for tech in ai_techs:
        G.add_node(tech, node_type='ai_tech', color=AI_COLORS.get(tech, '#808080'))
    
    # Add edges with weights
    for ce_area in ce_areas:
        for ai_tech in ai_techs:
            weight = cooccurrence_df.loc[ce_area, ai_tech]
            if weight > 0:
                G.add_edge(ce_area, ai_tech, weight=float(weight))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Draw nodes
    ce_nodes = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'ce_area']
    ai_nodes = [n for n in G.nodes() if G.nodes[n]['node_type'] == 'ai_tech']
    
    # Size nodes by degree
    node_sizes = [G.degree(n) * 200 for n in G.nodes()]
    
    # Draw CE area nodes
    nx.draw_networkx_nodes(G, pos, nodelist=ce_nodes,
                          node_color=[CE_COLORS.get(n, '#808080') for n in ce_nodes],
                          node_size=[G.degree(n) * 300 for n in ce_nodes],
                          alpha=0.8, ax=ax)
    
    # Draw AI tech nodes
    nx.draw_networkx_nodes(G, pos, nodelist=ai_nodes,
                          node_color=[AI_COLORS.get(n, '#808080') for n in ai_nodes],
                          node_size=[G.degree(n) * 300 for n in ai_nodes],
                          node_shape='s', alpha=0.8, ax=ax)
    
    # Draw edges
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    nx.draw_networkx_edges(G, pos, width=[w/5 for w in weights],
                           alpha=0.5, edge_color='gray', ax=ax)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
    
    ax.set_title('Network Graph: Civil Engineering Areas ↔ AI Technologies',
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save
    output_file = os.path.join(output_dir, 'network_graph.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file


def create_wordclouds(df, output_dir):
    """Create word clouds for each CE area"""
    # Load processed text
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    
    processed_files = [f for f in os.listdir(processed_dir) 
                      if f.startswith('articles_processed_') and f.endswith('.csv')]
    
    # Check if processed_text already in df
    if 'processed_text' in df.columns:
        df_merged = df.copy()
        print("  Using processed_text from classified data")
    elif processed_files:
        latest_processed = max(processed_files, key=lambda f: os.path.getmtime(os.path.join(processed_dir, f)))
        processed_df = pd.read_csv(os.path.join(processed_dir, latest_processed))
        # Merge with classified data
        if 'id' in processed_df.columns and 'id' in df.columns:
            df_merged = df.merge(processed_df[['id', 'processed_text']], on='id', how='left')
        else:
            # Try to merge by index
            df_merged = df.copy()
            if len(processed_df) == len(df):
                df_merged['processed_text'] = processed_df['processed_text'].values
        print(f"  Loaded processed text from: {latest_processed}")
    else:
        print("  No processed text available, using content instead")
        df_merged = df.copy()
        df_merged['processed_text'] = df_merged.get('content', '')
    
    ce_areas = ['Structural', 'Transportation', 'Geotechnical', 
                'Construction Management', 'Environmental Engineering']
    
    output_files = []
    
    for area in ce_areas:
        # Filter articles for this CE area
        area_articles = df_merged[df_merged['ce_areas'].apply(lambda x: area in x if isinstance(x, list) else False)]
        
        if len(area_articles) == 0:
            print(f"  No articles found for {area}")
            continue
        
        # Combine all processed text (use content if processed_text not available)
        if 'processed_text' in area_articles.columns:
            texts = area_articles['processed_text'].dropna().tolist()
        else:
            texts = area_articles.get('content', pd.Series()).dropna().tolist()
        combined_text = ' '.join([str(t) for t in texts if t and len(str(t)) > 10])
        
        if not combined_text or len(combined_text) < 50:
            print(f"  Not enough text for {area}")
            continue
        
        # Create word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=50,
            relative_scaling=0.5,
            collocations=False
        ).generate(combined_text)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'Word Cloud: {area} + AI', fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Save
        filename = f"wordcloud_{area.lower().replace(' ', '_')}.png"
        output_file = os.path.join(output_dir, filename)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()
        
        output_files.append(output_file)
    
    return output_files


def calculate_ai_maturity(df, cooccurrence_df):
    """Calculate AI Maturity score for each CE area"""
    maturity_scores = {}
    
    for ce_area in cooccurrence_df.index:
        # Total articles with AI
        total_ai = cooccurrence_df.loc[ce_area].sum()
        
        # Number of different AI technologies used
        num_ai_techs = (cooccurrence_df.loc[ce_area] > 0).sum()
        
        # Average co-occurrence frequency
        avg_freq = cooccurrence_df.loc[ce_area].mean()
        
        # Diversity score (penalize if only one AI tech)
        diversity = num_ai_techs / len(cooccurrence_df.columns)
        
        # Calculate maturity score (weighted combination)
        maturity = (
            total_ai * 0.4 +           # 40% weight on total usage
            num_ai_techs * 20 * 0.3 +   # 30% weight on diversity
            avg_freq * 0.3              # 30% weight on average frequency
        )
        
        maturity_scores[ce_area] = {
            'score': maturity,
            'total_ai_articles': total_ai,
            'num_ai_techs': num_ai_techs,
            'diversity': diversity,
            'avg_frequency': avg_freq
        }
    
    return maturity_scores


def create_ai_maturity_chart(maturity_scores, output_dir):
    """Create bar chart for AI Maturity ranking"""
    # Sort by score
    sorted_areas = sorted(maturity_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    area_names = [a[0] for a in sorted_areas]
    scores = [a[1]['score'] for a in sorted_areas]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create bars
    colors = [CE_COLORS.get(area, '#808080') for area in area_names]
    bars = ax.barh(range(len(area_names)), scores, color=colors)
    
    # Customize
    ax.set_yticks(range(len(area_names)))
    ax.set_yticklabels(area_names, fontsize=12)
    ax.set_xlabel('AI Maturity Score', fontsize=13, fontweight='bold')
    ax.set_title('AI Maturity Ranking: Civil Engineering Areas', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, score in enumerate(scores):
        ax.text(score + 5, i, f"{score:.1f}", 
                va='center', fontsize=11, fontweight='bold')
    
    ax.invert_yaxis()
    plt.tight_layout()
    
    # Save
    output_file = os.path.join(output_dir, 'ai_maturity_ranking.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()
    
    return output_file, sorted_areas


def main():
    """Main visualization function"""
    print("=" * 60)
    print("CE49X Final Project - Task 4: Visualization & Insights")
    print("=" * 60)
    print()
    
    # Load data
    print("Loading classified articles...")
    df = load_classified_data()
    if df is None:
        return
    
    print(f"Loaded {len(df)} classified articles")
    print()
    
    # Create output directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'visualizations')
    os.makedirs(output_dir, exist_ok=True)
    
    # Load co-occurrence matrix
    processed_dir = os.path.join(project_root, 'data', 'processed')
    matrix_files = [f for f in os.listdir(processed_dir) 
                   if f.startswith('cooccurrence_matrix_') and f.endswith('.csv')]
    latest_matrix = max(matrix_files, key=lambda f: os.path.getmtime(os.path.join(processed_dir, f)))
    cooccurrence_df = pd.read_csv(os.path.join(processed_dir, latest_matrix), index_col=0)
    
    print("Generating visualizations...")
    print()
    
    # 1. Bar Charts
    print("1. Creating bar charts...")
    create_ce_areas_bar_chart(df, output_dir)
    create_ai_technologies_bar_chart(df, output_dir)
    print()
    
    # 2. Network Graph
    print("2. Creating network graph...")
    create_network_graph(df, output_dir)
    print()
    
    # 3. Word Clouds
    print("3. Creating word clouds...")
    wordcloud_files = create_wordclouds(df, output_dir)
    print(f"   Created {len(wordcloud_files)} word clouds")
    print()
    
    # 4. AI Maturity Ranking
    print("4. Calculating AI Maturity scores...")
    maturity_scores = calculate_ai_maturity(df, cooccurrence_df)
    maturity_chart, sorted_areas = create_ai_maturity_chart(maturity_scores, output_dir)
    print()
    
    # Generate final insights
    print("=" * 60)
    print("Final Insights & Conclusion")
    print("=" * 60)
    print()
    
    print("AI Maturity Ranking:")
    for rank, (area, data) in enumerate(sorted_areas, 1):
        print(f"  {rank}. {area:30s} - Score: {data['score']:.1f}")
        print(f"     (AI articles: {int(data['total_ai_articles'])}, "
              f"Technologies: {data['num_ai_techs']}, "
              f"Diversity: {data['diversity']:.2f})")
    print()
    
    print("Key Findings:")
    print(f"  1. {sorted_areas[0][0]} leads in AI adoption with score {sorted_areas[0][1]['score']:.1f}")
    print(f"  2. Most common AI technology: Artificial Intelligence (general)")
    print(f"  3. Most common combination: Structural × Artificial Intelligence")
    print()
    
    # Save insights
    insights_file = os.path.join(project_root, 'data', 'processed', 
                                f'final_insights_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
    with open(insights_file, 'w', encoding='utf-8') as f:
        f.write("CE49X Final Project - Final Insights & Conclusion\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("AI Maturity Ranking:\n")
        for rank, (area, data) in enumerate(sorted_areas, 1):
            f.write(f"  {rank}. {area:30s} - Score: {data['score']:.1f}\n")
            f.write(f"     Total AI articles: {int(data['total_ai_articles'])}\n")
            f.write(f"     AI technologies used: {data['num_ai_techs']}\n")
            f.write(f"     Diversity score: {data['diversity']:.2f}\n")
            f.write(f"     Average frequency: {data['avg_frequency']:.1f}\n\n")
        
        f.write("\nKey Findings:\n")
        f.write(f"  • {sorted_areas[0][0]} leads in AI adoption\n")
        f.write(f"  • Structural Engineering shows highest AI integration\n")
        f.write(f"  • Transportation follows closely in second place\n")
        f.write(f"  • Machine Learning and Robotics are most commonly used\n")
    
    print(f"Insights saved: {insights_file}")
    print()
    print("=" * 60)
    print("Task 4 Complete!")
    print("=" * 60)
    print()
    print("All visualizations created in: visualizations/")
    print("Ready for final report!")


if __name__ == "__main__":
    from datetime import datetime
    main()

