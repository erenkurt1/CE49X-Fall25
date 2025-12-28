"""
Article Summarization Module
Uses extractive summarization to reduce article content size
"""

import re
from typing import List
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.summarizers.text_rank import TextRankSummarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words
    SUMY_AVAILABLE = True
except ImportError:
    SUMY_AVAILABLE = False

try:
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


def summarize_with_sumy(text: str, sentences_count: int = 3, language: str = 'english') -> str:
    """
    Summarize text using Sumy library (LSA method)
    
    Args:
        text: Full article text
        sentences_count: Number of sentences in summary
        language: Language code
    
    Returns:
        Summarized text
    """
    if not SUMY_AVAILABLE:
        return summarize_simple(text, sentences_count)
    
    try:
        # Parse the text
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        stemmer = Stemmer(language)
        
        # Use LSA summarizer (faster than TextRank)
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)
        
        # Generate summary
        summary = summarizer(parser.document, sentences_count)
        
        # Join sentences
        return ' '.join([str(sentence) for sentence in summary])
    
    except Exception as e:
        print(f"  Warning: Sumy summarization failed: {e}")
        return summarize_simple(text, sentences_count)


def summarize_simple(text: str, sentences_count: int = 3) -> str:
    """
    Simple extractive summarization using first N sentences
    
    Args:
        text: Full article text
        sentences_count: Number of sentences to keep
    
    Returns:
        Summarized text
    """
    if not text:
        return ""
    
    # Split into sentences (simple approach)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]  # Filter very short sentences
    
    if len(sentences) <= sentences_count:
        return text  # Return original if too short
    
    # Take first N sentences (often contain main points)
    summary = '. '.join(sentences[:sentences_count])
    if summary and not summary.endswith('.'):
        summary += '.'
    
    return summary


def summarize_with_tfidf(text: str, sentences_count: int = 3) -> str:
    """
    Summarize using TF-IDF scoring (requires NLTK)
    
    Args:
        text: Full article text
        sentences_count: Number of sentences in summary
    
    Returns:
        Summarized text
    """
    if not NLTK_AVAILABLE:
        return summarize_simple(text, sentences_count)
    
    try:
        # Download required NLTK data if not present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        # Tokenize sentences
        sentences = sent_tokenize(text)
        if len(sentences) <= sentences_count:
            return text
        
        # Tokenize words and remove stopwords
        stop_words = set(stopwords.words('english'))
        word_freq = {}
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            for word in words:
                if word.isalnum() and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score sentences
        sentence_scores = {}
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            score = sum([word_freq.get(word, 0) for word in words if word.isalnum() and word not in stop_words])
            sentence_scores[sentence] = score
        
        # Get top N sentences
        sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_sentences = [s[0] for s in sorted_sentences[:sentences_count]]
        
        # Maintain original order
        summary_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                summary_sentences.append(sentence)
                if len(summary_sentences) >= sentences_count:
                    break
        
        return ' '.join(summary_sentences)
    
    except Exception as e:
        print(f"  Warning: TF-IDF summarization failed: {e}")
        return summarize_simple(text, sentences_count)


def summarize_article(content: str, method: str = 'sumy', max_sentences: int = 3, 
                     max_length: int = 500) -> str:
    """
    Summarize article content
    
    Args:
        content: Full article content
        method: 'sumy', 'tfidf', or 'simple'
        max_sentences: Maximum sentences in summary
        max_length: Maximum character length (if content is shorter, return original)
    
    Returns:
        Summarized content
    """
    if not content:
        return ""
    
    # If content is already short, return as-is
    if len(content) <= max_length:
        return content
    
    # Choose summarization method
    if method == 'sumy' and SUMY_AVAILABLE:
        summary = summarize_with_sumy(content, max_sentences)
    elif method == 'tfidf' and NLTK_AVAILABLE:
        summary = summarize_with_tfidf(content, max_sentences)
    else:
        summary = summarize_simple(content, max_sentences)
    
    # Ensure summary doesn't exceed max_length
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit('.', 1)[0] + '.'
    
    return summary


if __name__ == "__main__":
    # Test summarization
    test_text = """
    Artificial intelligence is revolutionizing the construction industry in unprecedented ways. 
    Machine learning algorithms are being used to predict structural failures before they occur, 
    saving millions in potential damages. Computer vision systems can now inspect construction sites 
    in real-time, identifying safety hazards and ensuring compliance with building codes. 
    Generative AI is helping architects design more efficient structures by exploring thousands 
    of design variations in minutes. Robotics and automation are transforming how buildings are 
    constructed, with autonomous machines capable of laying bricks and pouring concrete. 
    These technologies are not just improving efficiency but also making construction safer 
    and more sustainable. The integration of AI in civil engineering represents a fundamental 
    shift in how infrastructure is designed, built, and maintained.
    """
    
    print("Original length:", len(test_text))
    print("\nOriginal text:")
    print(test_text)
    
    print("\n" + "="*60)
    print("Summarized (Sumy):")
    summary = summarize_article(test_text, method='sumy', max_sentences=3)
    print(summary)
    print(f"Summary length: {len(summary)}")


