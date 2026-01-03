"""
Text Preprocessing Pipeline for CE49X Final Project - Task 2
Implements complete NLP preprocessing: tokenization, normalization, 
stopword removal, lemmatization, n-grams, and TF-IDF.
"""

import os
import sys
import pandas as pd
import numpy as np
import re
from collections import Counter
from datetime import datetime

# NLP Libraries
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

# Download NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK stopwords...")
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading NLTK wordnet...")
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    print("Downloading NLTK POS tagger...")
    try:
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        print("Warning: Could not download POS tagger. Using simple lemmatization.")
        POS_TAGGING_AVAILABLE = False
else:
    POS_TAGGING_AVAILABLE = True

# Initialize components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Domain-specific stopwords (add construction/AI noise words)
domain_stopwords = {
    'subscribe', 'click', 'here', 'read', 'more', 'article', 'news',
    'website', 'com', 'www', 'http', 'https', 'html', 'amp',
    'said', 'says', 'according', 'also', 'would', 'could', 'may',
    'might', 'must', 'shall', 'should', 'will', 'can', 'get', 'got'
}
stop_words.update(domain_stopwords)


class TextPreprocessor:
    """Text preprocessing pipeline"""
    
    def __init__(self):
        self.lemmatizer = lemmatizer
        self.stop_words = stop_words
    
    def normalize(self, text):
        """
        Normalize text: lowercase, remove punctuation, special chars
        
        Args:
            text: Input text string
        
        Returns:
            Normalized text
        """
        if not text or pd.isna(text):
            return ""
        
        text = str(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep spaces and alphanumeric
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text):
        """
        Tokenize text into words
        
        Args:
            text: Input text string
        
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        try:
            tokens = word_tokenize(text)
            return tokens
        except Exception as e:
            print(f"Tokenization error: {e}")
            return text.split()
    
    def remove_stopwords(self, tokens):
        """
        Remove stopwords from tokens
        
        Args:
            tokens: List of tokens
        
        Returns:
            List of tokens without stopwords
        """
        return [token for token in tokens if token not in self.stop_words and len(token) > 2]
    
    def lemmatize(self, tokens, use_pos_tagging=True):
        """
        Lemmatize tokens (reduce to root form)
        
        Args:
            tokens: List of tokens
            use_pos_tagging: Use POS tagging for better accuracy (slower)
        
        Returns:
            List of lemmatized tokens
        """
        lemmatized = []
        
        # Try POS tagging if available, otherwise use simple lemmatization
        if use_pos_tagging and POS_TAGGING_AVAILABLE:
            try:
                pos_tagged = pos_tag(tokens)
                for token, pos in pos_tagged:
                    # Map POS tag to wordnet format
                    if pos.startswith('J'):
                        pos = 'a'  # adjective
                    elif pos.startswith('V'):
                        pos = 'v'  # verb
                    elif pos.startswith('N'):
                        pos = 'n'  # noun
                    elif pos.startswith('R'):
                        pos = 'r'  # adverb
                    else:
                        pos = 'n'  # default to noun
                    
                    lemma = self.lemmatizer.lemmatize(token, pos=pos)
                    lemmatized.append(lemma)
            except:
                # Fallback to simple lemmatization
                for token in tokens:
                    lemma = self.lemmatizer.lemmatize(token)
                    lemmatized.append(lemma)
        else:
            # Simple lemmatization (faster)
            for token in tokens:
                lemma = self.lemmatizer.lemmatize(token)
                lemmatized.append(lemma)
        
        return lemmatized
    
    def preprocess(self, text):
        """
        Complete preprocessing pipeline
        
        Args:
            text: Raw text string
        
        Returns:
            Preprocessed text (as string of tokens)
        """
        # Normalize
        normalized = self.normalize(text)
        
        # Tokenize
        tokens = self.tokenize(normalized)
        
        # Remove stopwords
        tokens = self.remove_stopwords(tokens)
        
        # Lemmatize (use simple method for speed)
        tokens = self.lemmatize(tokens, use_pos_tagging=False)
        
        # Filter out very short tokens
        tokens = [t for t in tokens if len(t) > 2]
        
        return ' '.join(tokens)


def generate_ngrams(tokens, n=2, min_freq=2):
    """
    Generate n-grams and calculate frequencies
    
    Args:
        tokens: List of token lists (one per document)
        n: N-gram size (2 for bigrams, 3 for trigrams)
        min_freq: Minimum frequency to include
    
    Returns:
        Dictionary of n-gram frequencies
    """
    from nltk.util import ngrams
    
    all_ngrams = []
    
    for doc_tokens in tokens:
        if len(doc_tokens) >= n:
            doc_ngrams = list(ngrams(doc_tokens, n))
            all_ngrams.extend([' '.join(ng) for ng in doc_ngrams])
    
    # Count frequencies
    ngram_counts = Counter(all_ngrams)
    
    # Filter by minimum frequency
    filtered_ngrams = {ng: count for ng, count in ngram_counts.items() if count >= min_freq}
    
    return filtered_ngrams


def calculate_tfidf(documents):
    """
    Calculate TF-IDF scores for documents
    
    Args:
        documents: List of preprocessed text strings
    
    Returns:
        TF-IDF matrix and feature names
    """
    vectorizer = TfidfVectorizer(
        max_features=1000,  # Top 1000 features
        ngram_range=(1, 2),  # Unigrams and bigrams
        min_df=2,  # Minimum document frequency
        max_df=0.95  # Maximum document frequency (remove very common words)
    )
    
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()
    
    return tfidf_matrix, feature_names, vectorizer


def main():
    """Main preprocessing function"""
    print("=" * 60)
    print("CE49X Final Project - Task 2: Text Preprocessing & NLP")
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
        SELECT id, title, content, keywords
        FROM articles
        ORDER BY id
    """
    
    df = pd.read_sql_query(query, db.conn)
    db.disconnect()
    
    print(f"Loaded {len(df)} articles")
    print()
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor()
    
    # Preprocess articles
    print("Preprocessing articles...")
    print("(This may take a few minutes for large datasets)")
    print()
    
    processed_texts = []
    tokenized_texts = []
    
    for idx, row in df.iterrows():
        text = str(row.get('content', ''))
        
        # Preprocess
        processed = preprocessor.preprocess(text)
        processed_texts.append(processed)
        
        # Tokenize for n-grams
        tokens = processed.split()
        tokenized_texts.append(tokens)
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(df)} articles...")
    
    print(f"Preprocessed {len(processed_texts)} articles")
    print()
    
    # Add processed text to dataframe
    df['processed_text'] = processed_texts
    df['tokens'] = tokenized_texts
    df['token_count'] = df['tokens'].apply(len)
    
    # Generate n-grams
    print("Generating n-grams...")
    
    # Unigrams (single words)
    all_tokens = [token for tokens in tokenized_texts for token in tokens]
    unigram_counts = Counter(all_tokens)
    top_unigrams = dict(unigram_counts.most_common(20))
    
    # Bigrams
    bigram_counts = generate_ngrams(tokenized_texts, n=2, min_freq=2)
    top_bigrams = dict(Counter(bigram_counts).most_common(20))
    
    # Trigrams (optional)
    trigram_counts = generate_ngrams(tokenized_texts, n=3, min_freq=2)
    top_trigrams = dict(Counter(trigram_counts).most_common(20))
    
    print(f"  Top unigrams: {len(top_unigrams)}")
    print(f"  Top bigrams: {len(top_bigrams)}")
    print(f"  Top trigrams: {len(top_trigrams)}")
    print()
    
    # Calculate TF-IDF
    print("Calculating TF-IDF scores...")
    tfidf_matrix, feature_names, vectorizer = calculate_tfidf(processed_texts)
    print(f"  TF-IDF matrix shape: {tfidf_matrix.shape}")
    print(f"  Features: {len(feature_names)}")
    print()
    
    # Save processed data
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save processed dataframe
    processed_file = os.path.join(processed_dir, f'articles_processed_{timestamp}.csv')
    # Save without token lists (they're not JSON serializable easily)
    df_save = df.drop(columns=['tokens'])
    df_save.to_csv(processed_file, index=False, encoding='utf-8')
    print(f"Saved processed data: {processed_file}")
    
    # Save n-gram frequencies
    ngrams_file = os.path.join(processed_dir, f'ngrams_{timestamp}.csv')
    ngrams_df = pd.DataFrame([
        {'type': 'unigram', 'phrase': phrase, 'frequency': count}
        for phrase, count in top_unigrams.items()
    ] + [
        {'type': 'bigram', 'phrase': phrase, 'frequency': count}
        for phrase, count in top_bigrams.items()
    ] + [
        {'type': 'trigram', 'phrase': phrase, 'frequency': count}
        for phrase, count in top_trigrams.items()
    ])
    ngrams_df.to_csv(ngrams_file, index=False, encoding='utf-8')
    print(f"Saved n-grams: {ngrams_file}")
    
    # Generate report
    print()
    print("=" * 60)
    print("Preprocessing Report")
    print("=" * 60)
    print()
    print(f"Total articles processed: {len(df)}")
    print(f"Average tokens per article: {df['token_count'].mean():.1f}")
    print(f"Total unique tokens: {len(unigram_counts)}")
    print()
    
    print("Top 20 Most Frequent Words (excluding stopwords):")
    for i, (word, count) in enumerate(top_unigrams.items(), 1):
        print(f"  {i:2d}. {word:20s} ({count:,})")
    print()
    
    print("Top 20 Bigrams:")
    for i, (bigram, count) in enumerate(top_bigrams.items(), 1):
        print(f"  {i:2d}. {bigram:40s} ({count:,})")
    print()
    
    # Save report
    report_file = os.path.join(processed_dir, f'preprocessing_report_{timestamp}.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("CE49X Final Project - Task 2: Text Preprocessing Report\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total articles processed: {len(df)}\n")
        f.write(f"Average tokens per article: {df['token_count'].mean():.1f}\n")
        f.write(f"Total unique tokens: {len(unigram_counts)}\n\n")
        
        f.write("Top 20 Most Frequent Words (excluding stopwords):\n")
        for i, (word, count) in enumerate(top_unigrams.items(), 1):
            f.write(f"  {i:2d}. {word:20s} ({count:,})\n")
        f.write("\n")
        
        f.write("Top 20 Bigrams:\n")
        for i, (bigram, count) in enumerate(top_bigrams.items(), 1):
            f.write(f"  {i:2d}. {bigram:40s} ({count:,})\n")
        f.write("\n")
        
        f.write("Top 20 Trigrams:\n")
        for i, (trigram, count) in enumerate(top_trigrams.items(), 1):
            f.write(f"  {i:2d}. {trigram:50s} ({count:,})\n")
    
    print(f"Report saved: {report_file}")
    print()
    print("=" * 60)
    print("Preprocessing Complete!")
    print("=" * 60)
    print()
    print("Deliverables created:")
    print(f"  1. Processed dataset: {processed_file}")
    print(f"  2. N-grams data: {ngrams_file}")
    print(f"  3. Preprocessing report: {report_file}")
    print()
    print("Next step: Task 3 - Categorization & Trend Analysis")


if __name__ == "__main__":
    main()

