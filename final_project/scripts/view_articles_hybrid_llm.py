"""
Hybrid LLM-Powered Article System
Combines local models (HuggingFace) and Gemini API for enhanced features.

Features:
- Semantic search (local sentence-transformers)
- Chatbot interface (Gemini API)
- Summarization (local BART model)
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
import numpy as np
from pathlib import Path
from datetime import datetime
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

# Gemini API setup
# Try to get API key from environment variable first, fallback to hardcoded
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
try:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
    print("[OK] Gemini API configured")
except ImportError:
    print("[WARNING] google-generativeai not installed. Install with: pip install google-generativeai")
    GEMINI_AVAILABLE = False
except Exception as e:
    print(f"[WARNING] Could not configure Gemini API: {e}")
    GEMINI_AVAILABLE = False

# Local models setup
try:
    from sentence_transformers import SentenceTransformer
    from transformers import pipeline
    LOCAL_MODELS_AVAILABLE = True
    print("[OK] Loading local models...")
    
    # Load semantic search model
    try:
        search_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("  [OK] Semantic search model loaded")
    except Exception as e:
        print(f"  [WARNING] Could not load search model: {e}")
        search_model = None
    
    # Load summarizer
    try:
        summarizer_model = pipeline("summarization", 
                                   model="facebook/bart-large-cnn",
                                   device=-1)
        print("  [OK] Summarization model loaded")
    except Exception as e:
        print(f"  [WARNING] Could not load summarizer: {e}")
        summarizer_model = None
        
except ImportError:
    print("[WARNING] transformers not installed. Install with: pip install transformers accelerate")
    LOCAL_MODELS_AVAILABLE = False
    search_model = None
    summarizer_model = None

# Cache for embeddings
article_embeddings_cache = None
articles_data_cache = None

# Cache for Gemini model (avoid creating it multiple times)
gemini_model_cache = None

def get_article_embeddings(articles):
    """Generate embeddings for all articles using local model"""
    global article_embeddings_cache, articles_data_cache
    
    if not LOCAL_MODELS_AVAILABLE or search_model is None:
        return None, articles
    
    # Cache embeddings
    if article_embeddings_cache is not None and articles_data_cache == articles:
        return article_embeddings_cache, articles
    
    print("Generating article embeddings...")
    texts = []
    for article in articles:
        title = article.get('title', '') if article.get('title') else ''
        content = article.get('content', '') if article.get('content') else ''
        text = f"{title} {content}".strip()
        if not text:
            text = "No content"  # Ensure we always have some text
        texts.append(text)
    
    try:
        embeddings = search_model.encode(texts, show_progress_bar=False)
        article_embeddings_cache = embeddings
        articles_data_cache = articles
        print(f"Generated embeddings for {len(articles)} articles")
        return embeddings, articles
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        import traceback
        traceback.print_exc()
        return None, articles  # Return None embeddings, articles still usable

def semantic_search(query, articles, embeddings, top_k=10):
    """Perform semantic search using local embeddings"""
    if not LOCAL_MODELS_AVAILABLE or search_model is None or embeddings is None:
        return keyword_search(query, articles, top_k)
    
    if not query or not articles or len(articles) == 0:
        return []
    
    try:
        query_embedding = search_model.encode([query], show_progress_bar=False)[0]
        
        # Calculate similarities safely
        norms = np.linalg.norm(embeddings, axis=1)
        query_norm = np.linalg.norm(query_embedding)
        
        # Avoid division by zero
        if query_norm == 0:
            return keyword_search(query, articles, top_k)
        
        similarities = np.dot(embeddings, query_embedding) / (norms * query_norm)
        
        # Handle NaN or inf values
        similarities = np.nan_to_num(similarities, nan=0.0, posinf=1.0, neginf=-1.0)
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            try:
                article = dict(articles[idx])  # Make a copy as dict
                article['similarity_score'] = float(similarities[idx])
                results.append(article)
            except Exception as e:
                print(f"Error processing article at index {idx}: {e}")
                continue
        
        return results
    except Exception as e:
        print(f"Error in semantic_search: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to keyword search
        return keyword_search(query, articles, top_k)

def keyword_search(query, articles, top_k=10):
    """Fallback keyword-based search"""
    if not query or not articles:
        return []
    
    try:
        query_lower = str(query).lower().strip()
        if not query_lower:
            return []
        
        query_words = set([w for w in query_lower.split() if len(w) > 1])  # Filter out single character words
        if not query_words:
            return []
        
        scored_articles = []
        for article in articles:
            try:
                title = str(article.get('title', '') or '').lower()
                content = str(article.get('content', '') or '').lower()
                text = f"{title} {content}"
                
                score = sum(1 for word in query_words if word in text)
                if score > 0:
                    article_copy = dict(article)  # Make a copy as dict
                    article_copy['similarity_score'] = float(score) / len(query_words)
                    scored_articles.append(article_copy)
            except Exception as e:
                print(f"Error processing article in keyword search: {e}")
                continue
        
        scored_articles.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return scored_articles[:top_k]
    except Exception as e:
        print(f"Error in keyword_search: {e}")
        import traceback
        traceback.print_exc()
        return []

def classify_article_llm(article_text):
    """Classify article using local zero-shot model"""
    if not LOCAL_MODELS_AVAILABLE or classifier_model is None:
        return [], []
    
    # Truncate if too long
    if len(article_text) > 512:
        article_text = article_text[:512]
    
    ce_labels = [
        "Structural Engineering",
        "Geotechnical Engineering",
        "Transportation Engineering",
        "Construction Management",
        "Environmental Engineering"
    ]
    
    ai_labels = [
        "Artificial Intelligence",
        "Machine Learning",
        "Computer Vision",
        "Generative Design",
        "Predictive Analytics",
        "Robotics and Automation"
    ]
    
    try:
        # Classify CE areas
        ce_result = classifier_model(article_text, ce_labels)
        ce_areas = [label for label, score in zip(ce_result['labels'], ce_result['scores']) 
                   if score > 0.3]  # Lower threshold for multi-label
        
        # Classify AI technologies
        ai_result = classifier_model(article_text, ai_labels)
        ai_techs = [label for label, score in zip(ai_result['labels'], ai_result['scores']) 
                   if score > 0.3]
        
        return ce_areas, ai_techs
    except Exception as e:
        print(f"Error in classification: {e}")
        return [], []

def summarize_article_llm(article_text, max_length=150):
    """Generate summary using local BART model"""
    if not LOCAL_MODELS_AVAILABLE or summarizer_model is None:
        return article_text[:200] + "..." if len(article_text) > 200 else article_text
    
    # Truncate if too long (BART has token limits)
    if len(article_text) > 1024:
        article_text = article_text[:1024]
    
    try:
        summary = summarizer_model(
            article_text,
            max_length=max_length,
            min_length=50,
            do_sample=False
        )
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error in summarization: {e}")
        return article_text[:200] + "..."

def get_gemini_model():
    """Get available Gemini model (cached)"""
    global gemini_model_cache
    
    if not GEMINI_AVAILABLE:
        return None
    
    # Return cached model if available
    if gemini_model_cache is not None:
        return gemini_model_cache
    
    # Use newer model names (tested and working)
    # Order: newest stable models first, then fallbacks
    model_names_to_try = [
        'models/gemini-2.5-flash',      # Latest stable flash (recommended - tested and works!)
        'models/gemini-2.5-pro',        # Latest stable pro
        'models/gemini-2.0-flash-001',  # Stable 2.0 flash
        'models/gemini-flash-latest',   # Latest flash
        'models/gemini-pro-latest',     # Latest pro
        'models/gemini-2.0-flash',      # Alternative 2.0
    ]
    
    # Try each model name
    for model_name in model_names_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"Using Gemini model: {model_name}")
            gemini_model_cache = model  # Cache it
            return model
        except Exception as e:
            error_msg = str(e).lower()
            # Print error for debugging
            if 'quota' not in error_msg:
                print(f"Model {model_name} failed: {e}")
            continue
    
    print("ERROR: No available Gemini model found!")
    return None

def answer_question_gemini(question, articles_context):
    """Answer questions using Gemini API"""
    if not GEMINI_AVAILABLE:
        return {"answer": "Gemini API not available", "sources": []}
    
    try:
        model = get_gemini_model()
        if model is None:
            return {"answer": "No available Gemini model found. Please check your API key and model availability.", "sources": []}
        
        # Prepare context from articles (safely handle missing fields)
        context_parts = []
        for a in articles_context[:5]:  # Use top 5 articles
            title = a.get('title', 'No title') if a.get('title') else 'No title'
            content = a.get('content', '') if a.get('content') else ''
            # Truncate content safely
            if content and len(content) > 500:
                content = content[:500] + "..."
            context_parts.append(f"Article: {title}\n{content}")
        context = "\n\n".join(context_parts) if context_parts else "No articles available."
        
        prompt = f"""You are an expert assistant analyzing articles about AI in Civil Engineering.

Context from articles:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If the answer isn't in the context, say so clearly.
Be specific and cite which articles (by title) support your answer."""

        response = model.generate_content(prompt)
        
        # Handle response properly
        answer_text = ""
        try:
            if hasattr(response, 'text'):
                answer_text = response.text if response.text else ""
            elif hasattr(response, 'candidates') and response.candidates:
                if hasattr(response.candidates[0], 'content') and response.candidates[0].content:
                    if hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts:
                        answer_text = response.candidates[0].content.parts[0].text
                    else:
                        answer_text = str(response.candidates[0].content)
                else:
                    answer_text = str(response.candidates[0])
            else:
                answer_text = str(response)
        except Exception as parse_error:
            print(f"Error parsing response: {parse_error}")
            answer_text = f"Error parsing response: {str(parse_error)}"
        
        if not answer_text or answer_text == "":
            answer_text = "Sorry, I couldn't generate a response. Please try again."
        
        # Safely get sources
        sources = []
        for a in articles_context[:5]:
            title = a.get('title', '') if a.get('title') else ''
            if title and title.strip():
                sources.append(title)
        
        return {
            "answer": answer_text,
            "sources": sources
        }
    except Exception as e:
        import traceback
        error_msg = f"Error in answer_question_gemini: {str(e)}"
        full_trace = traceback.format_exc()
        print(error_msg)
        print(full_trace)  # Debug print
        return {
            "answer": f"Error: {str(e)}",
            "sources": []
        }

def chat_with_gemini(user_message, chat_history):
    """Chat with Gemini API"""
    if not GEMINI_AVAILABLE:
        return "Gemini API not available. Please install google-generativeai."
    
    try:
        model = get_gemini_model()
        if model is None:
            return "No available Gemini model found. Please check your API key and model availability."
        
        # Build conversation context
        context = "You are a helpful assistant answering questions about AI in Civil Engineering. "
        context += "You have access to a database of news articles about this topic. "
        context += "Be concise, accurate, and helpful.\n\n"
        
        # Add chat history
        if chat_history:
            context += "Previous conversation:\n"
            for msg in chat_history[-5:]:  # Last 5 messages
                context += f"User: {msg.get('user', '')}\n"
                context += f"Assistant: {msg.get('assistant', '')}\n"
        
        context += f"\nUser: {user_message}\nAssistant:"
        
        response = model.generate_content(context)
        
        # Handle response properly
        try:
            if hasattr(response, 'text'):
                return response.text if response.text else "Sorry, I couldn't generate a response."
            elif hasattr(response, 'candidates') and response.candidates:
                if hasattr(response.candidates[0], 'content') and response.candidates[0].content:
                    if hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts:
                        return response.candidates[0].content.parts[0].text
                    else:
                        return str(response.candidates[0].content)
                else:
                    return str(response.candidates[0])
            else:
                return str(response) if response else "Sorry, I couldn't generate a response."
        except Exception as parse_error:
            print(f"Error parsing chat response: {parse_error}")
            return f"Error parsing response: {str(parse_error)}"
    except Exception as e:
        import traceback
        error_msg = f"Error in chat_with_gemini: {str(e)}"
        full_trace = traceback.format_exc()
        print(error_msg)
        print(full_trace)  # Debug print
        return f"Error: {str(e)}"

def generate_insights_gemini(data_summary):
    """Generate insights using Gemini API"""
    if not GEMINI_AVAILABLE:
        return "Gemini API not available for insight generation."
    
    try:
        model = get_gemini_model()
        if model is None:
            return "No available Gemini model found. Please check your API key and model availability."
        
        prompt = f"""Analyze the following data about AI adoption in Civil Engineering and generate 5-7 key insights.

Data Summary:
- Total Articles: {data_summary.get('total_articles', 0)}
- CE Area Distribution: {data_summary.get('ce_distribution', {})}
- AI Technology Distribution: {data_summary.get('ai_distribution', {})}
- Top Combinations: {data_summary.get('top_combinations', [])}

Generate insights that are:
1. Data-driven and specific
2. Actionable
3. Clear and concise
4. Based on the statistics provided

Format as bullet points."""
        
        response = model.generate_content(prompt)
        
        # Handle response properly
        answer_text = ""
        try:
            if hasattr(response, 'text') and response.text:
                answer_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                if hasattr(response.candidates[0], 'content') and response.candidates[0].content:
                    if hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts:
                        answer_text = response.candidates[0].content.parts[0].text
                    else:
                        answer_text = str(response.candidates[0].content)
                else:
                    answer_text = str(response.candidates[0])
            else:
                answer_text = str(response)
        except Exception as parse_error:
            print(f"Error parsing insights response: {parse_error}")
            answer_text = f"Error parsing response: {str(parse_error)}"
        
        if not answer_text or answer_text == "":
            answer_text = "Sorry, I couldn't generate insights. Please try again."
        
        return answer_text
    except Exception as e:
        import traceback
        error_msg = f"Error generating insights: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Debug print
        return f"Error generating insights: {str(e)}"

class HybridLLMHandler(SimpleHTTPRequestHandler):
    """HTTP handler for hybrid LLM-powered interface"""
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_api(self):
        """Handle API requests"""
        try:
            print(f"[API] Handling request: {self.path}")
            if self.path == '/api/articles':
                self.handle_get_articles()
            elif self.path == '/api/stats':
                self.handle_get_stats()
            elif self.path == '/api/search':
                self.handle_search()
            elif self.path == '/api/chat':
                try:
                    self.handle_chat()
                except Exception as e:
                    print(f"[ERROR] Exception in handle_chat: {e}")
                    import traceback
                    traceback.print_exc()
                    self.send_json_response({"response": f"Server error: {str(e)}"}, 500)
            elif self.path == '/api/summarize':
                try:
                    self.handle_summarize()
                except Exception as e:
                    print(f"[ERROR] Exception in handle_summarize: {e}")
                    import traceback
                    traceback.print_exc()
                    self.send_json_response({"summary": f"Error generating summary: {str(e)}"}, 500)
            else:
                print(f"[WARNING] Unknown endpoint: {self.path}")
                self.send_json_response({"error": f"Unknown endpoint: {self.path}"}, 404)
        except Exception as e:
            print(f"[ERROR] Unhandled exception in handle_api: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.send_json_response({"error": str(e)}, 500)
            except:
                pass  # Can't send response if headers already sent
    
    def handle_get_articles(self):
        """Get all articles"""
        db = DatabaseManager()
        if not db.connect():
            self.send_json_response({"error": "Database connection failed"}, 500)
            return
        
        try:
            articles = db.fetch_all_articles()
            
            # Convert dates to strings for JSON serialization
            for article in articles:
                if article.get('publication_date'):
                    article['publication_date'] = str(article['publication_date'])
            
            db.disconnect()
            self.send_json_response({"articles": articles, "count": len(articles)})
        except Exception as e:
            db.disconnect()
            print(f"Error in handle_get_articles: {e}")
            import traceback
            traceback.print_exc()
            self.send_json_response({"error": str(e), "articles": [], "count": 0}, 500)
    
    def handle_get_stats(self):
        """Get statistics"""
        db = DatabaseManager()
        if not db.connect():
            self.send_json_response({"error": "Database connection failed"}, 500)
            return
        
        try:
            count = db.get_article_count()
            stats = db.get_article_stats()
            db.disconnect()
            self.send_json_response({"count": count, "stats": stats})
        except Exception as e:
            db.disconnect()
            print(f"Error in handle_get_stats: {e}")
            import traceback
            traceback.print_exc()
            self.send_json_response({"error": str(e), "count": 0, "stats": {}}, 500)
    
    def handle_search(self):
        """Handle semantic search"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            query = data.get('query', '')
            top_k = data.get('top_k', 10)
            
            if not query:
                self.send_json_response({
                    "results": [],
                    "query": "",
                    "search_type": "none",
                    "count": 0,
                    "error": "Please provide a search query"
                })
                return
            
            db = DatabaseManager()
            if not db.connect():
                self.send_json_response({
                    "results": [],
                    "query": query,
                    "search_type": "error",
                    "count": 0,
                    "error": "Database connection failed"
                }, 500)
                return
            
            try:
                articles_raw = db.fetch_all_articles()
                if not articles_raw:
                    db.disconnect()
                    self.send_json_response({
                        "results": [],
                        "query": query,
                        "search_type": "none",
                        "count": 0,
                        "error": "No articles found in database"
                    })
                    return
                
                # Convert RealDictRow to regular dict for easier handling
                articles = []
                for article in articles_raw:
                    try:
                        if hasattr(article, 'keys'):
                            # It's a dict-like object (RealDictRow)
                            article_dict = dict(article)
                        else:
                            article_dict = article
                        articles.append(article_dict)
                    except Exception as e:
                        print(f"Error converting article: {e}")
                        continue
                
                if not articles:
                    db.disconnect()
                    self.send_json_response({
                        "results": [],
                        "query": query,
                        "search_type": "none",
                        "count": 0,
                        "error": "No valid articles found"
                    })
                    return
                
                try:
                    embeddings, articles = get_article_embeddings(articles)
                    
                    if embeddings is not None and len(embeddings) > 0:
                        results = semantic_search(query, articles, embeddings, top_k)
                        search_type = "semantic"
                    else:
                        results = keyword_search(query, articles, top_k)
                        search_type = "keyword"
                except Exception as search_error:
                    print(f"Error in search: {search_error}")
                    import traceback
                    traceback.print_exc()
                    # Fallback to keyword search
                    try:
                        results = keyword_search(query, articles, top_k)
                        search_type = "keyword"
                    except:
                        results = []
                        search_type = "error"
                
                db.disconnect()
                
                # Ensure results are serializable
                serializable_results = []
                for result in results:
                    try:
                        # Convert to dict and ensure all values are serializable
                        if isinstance(result, dict):
                            clean_result = {}
                            for key, value in result.items():
                                # Convert non-serializable types
                                if key == 'publication_date' and value:
                                    clean_result[key] = str(value) if value else None
                                elif key == 'similarity_score':
                                    clean_result[key] = float(value) if value else 0.0
                                else:
                                    clean_result[key] = value if value is not None else ''
                            serializable_results.append(clean_result)
                        else:
                            serializable_results.append(str(result))
                    except Exception as e:
                        print(f"Error serializing result: {e}")
                        continue
                
                self.send_json_response({
                    "results": serializable_results,
                    "query": query,
                    "search_type": search_type,
                    "count": len(serializable_results)
                })
            except Exception as db_error:
                db.disconnect()
                print(f"Error in search handler: {db_error}")
                import traceback
                traceback.print_exc()
                self.send_json_response({
                    "results": [],
                    "query": query,
                    "search_type": "error",
                    "count": 0,
                    "error": str(db_error)
                }, 500)
        except Exception as e:
            print(f"Error in handle_search: {e}")
            import traceback
            traceback.print_exc()
            self.send_json_response({
                "results": [],
                "query": "",
                "search_type": "error",
                "count": 0,
                "error": str(e)
            }, 500)
    
    def handle_chat(self):
        """Handle chat messages"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            chat_history = data.get('history', [])
            
            if not message:
                self.send_json_response({"response": "Please provide a message"})
                return
            
            response = chat_with_gemini(message, chat_history)
            self.send_json_response({"response": response})
        except Exception as e:
            print(f"Error in handle_chat: {e}")
            import traceback
            traceback.print_exc()
            self.send_json_response({"response": f"Error: {str(e)}"}, 500)
    
    def handle_summarize(self):
        """Summarize article text"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            article_text = data.get('text', '')
            max_length = data.get('max_length', 150)
            
            if not article_text:
                self.send_json_response({"summary": "No text provided to summarize"})
                return
            
            summary = summarize_article_llm(article_text, max_length)
            self.send_json_response({"summary": summary})
        except Exception as e:
            print(f"Error in handle_summarize: {e}")
            import traceback
            traceback.print_exc()
            self.send_json_response({"summary": f"Error generating summary: {str(e)}"}, 500)
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        try:
            # Ensure data is JSON serializable
            json_str = json.dumps(data, ensure_ascii=False)
            self.send_response(status)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_str.encode('utf-8'))
        except Exception as e:
            print(f"Error sending JSON response: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: send error as plain text
            try:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = json.dumps({"error": f"JSON serialization error: {str(e)}"})
                self.wfile.write(error_response.encode('utf-8'))
            except:
                pass  # If even this fails, we're out of options
    
    def get_html(self):
        """Get HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #7f8c8d 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: #34495e;
            color: white;
            padding: 30px;
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 1.1em; }
        .tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 2px solid #ddd;
        }
        .tab {
            flex: 1;
            padding: 15px 20px;
            cursor: pointer;
            background: #f5f5f5;
            border: none;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s;
        }
        .tab:hover { background: #e0e0e0; }
        .tab.active {
            background: white;
            border-bottom: 3px solid #34495e;
            color: #34495e;
        }
        .tab-content {
            display: none;
            padding: 30px;
        }
        .tab-content.active { display: block; }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"], textarea {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #34495e;
        }
        button {
            padding: 12px 24px;
            background: #34495e;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: background 0.3s;
        }
        button:hover { background: #2c3e50; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .results {
            margin-top: 20px;
        }
        .article-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: white;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(52, 73, 94, 0.15);
        }
        .article-title {
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.4;
        }
        .article-meta {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 10px;
        }
        .article-content {
            color: #555;
            font-size: 0.9em;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .score {
            display: inline-block;
            background: #34495e;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .chat-container {
            height: 500px;
            border: 2px solid #ddd;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            max-width: 70%;
        }
        .message.user {
            background: #34495e;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .message.assistant {
            background: white;
            border: 2px solid #ddd;
        }
        .chat-input {
            display: flex;
            padding: 15px;
            border-top: 2px solid #ddd;
        }
        .badge {
            display: inline-block;
            background: #34495e;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            margin: 5px 5px 5px 0;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .controls {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        select {
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        select:focus {
            outline: none;
            border-color: #34495e;
        }
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        .article-keywords {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }
        .keyword-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
        }
        .article-url {
            margin-top: 10px;
        }
        .article-url a {
            color: #34495e;
            text-decoration: none;
            font-size: 0.85em;
        }
        .article-url a:hover {
            text-decoration: underline;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Article System</h1>
            <div class="subtitle">CE49X Final Project</div>
        </header>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('search')">🔍 Search</button>
            <button class="tab" onclick="switchTab('chat')">💬 Chat</button>
        </div>
        
        <!-- Search Tab -->
        <div id="search" class="tab-content active">
            <h2>Article Search</h2>
            <p style="color: #666; margin-bottom: 20px;">Semantic search powered by LLM + keyword filtering</p>
            
            <div class="controls">
                <input type="text" id="search-query" placeholder="Search articles..." style="flex: 1;">
                <select id="sort">
                    <option value="id">Sort by ID</option>
                    <option value="date">Sort by Date</option>
                    <option value="title">Sort by Title</option>
                    <option value="relevance">Sort by Relevance</option>
                </select>
                <button onclick="loadArticles()">Refresh</button>
            </div>
            
            <div id="search-results" class="results"></div>
        </div>
        
        <!-- Chat Tab -->
        <div id="chat" class="tab-content">
            <h2>Chatbot</h2>
            <div class="chat-container">
                <div class="chat-messages" id="chat-messages">
                    <div class="message assistant">
                        <strong>Assistant:</strong> Hello! I'm your AI assistant for CE49X project. Ask me anything about AI in Civil Engineering!
                    </div>
                </div>
                <div class="chat-input">
                    <input type="text" id="chat-input" placeholder="Type your message..." style="flex: 1;">
                    <button onclick="sendChatMessage()">Send</button>
                </div>
            </div>
        </div>
        
    </div>
    
    <script>
        let chatHistory = [];
        let allArticles = [];
        let searchResults = [];
        let useSemanticSearch = false;
        
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function loadArticles() {
            const container = document.getElementById('search-results');
            container.innerHTML = '<div class="loading">Loading articles...</div>';
            
            try {
                const response = await fetch('/api/articles');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                    return;
                }
                
                allArticles = data.articles || [];
                searchResults = [];
                useSemanticSearch = false;
                displayArticles(allArticles);
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading articles: ${error.message}</div>`;
            }
        }
        
        async function performSearch() {
            const query = document.getElementById('search-query').value.trim();
            const resultsDiv = document.getElementById('search-results');
            
            if (!query) {
                // If no query, show all articles
                searchResults = [];
                useSemanticSearch = false;
                displayArticles(allArticles);
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading">Searching...</div>';
            
            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, top_k: 100})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                    return;
                }
                
                if (data.results && data.results.length > 0) {
                    searchResults = data.results;
                    useSemanticSearch = true;
                    displayArticles(data.results);
                } else {
                    // No results from semantic search, fall back to keyword search
                    searchResults = [];
                    useSemanticSearch = false;
                    displayArticles(allArticles); // Will filter by keyword in displayArticles
                }
            } catch (error) {
                console.error('Search error:', error);
                // Fall back to keyword search
                searchResults = [];
                useSemanticSearch = false;
                displayArticles(allArticles);
            }
        }
        
        function displayArticles(articles) {
            const container = document.getElementById('search-results');
            
            if (!articles || articles.length === 0) {
                container.innerHTML = '<div class="loading">No articles found.</div>';
                return;
            }
            
            let articlesToDisplay = [...articles];
            
            // Apply keyword filtering if we're not using semantic search results
            if (!useSemanticSearch) {
                const searchTerm = document.getElementById('search-query').value.toLowerCase();
                if (searchTerm) {
                    articlesToDisplay = articlesToDisplay.filter(article => 
                        (article.title || '').toLowerCase().includes(searchTerm) ||
                        (article.content || '').toLowerCase().includes(searchTerm) ||
                        (article.keywords || '').toLowerCase().includes(searchTerm)
                    );
                }
            }
            
            // Apply sorting
            const sortBy = document.getElementById('sort').value;
            if (sortBy === 'date') {
                articlesToDisplay.sort((a, b) => {
                    const dateA = a.publication_date || '';
                    const dateB = b.publication_date || '';
                    return dateB.localeCompare(dateA);
                });
            } else if (sortBy === 'title') {
                articlesToDisplay.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
            } else if (sortBy === 'relevance' && useSemanticSearch) {
                articlesToDisplay.sort((a, b) => {
                    const scoreA = a.similarity_score || 0;
                    const scoreB = b.similarity_score || 0;
                    return scoreB - scoreA;
                });
            }
            
            const totalCount = useSemanticSearch ? articlesToDisplay.length : allArticles.length;
            
            container.innerHTML = `
                <div style="margin-bottom: 15px; color: #666;">
                    Showing ${articlesToDisplay.length} of ${totalCount} articles
                    ${useSemanticSearch ? '<span style="margin-left: 10px; background: #e3f2fd; padding: 3px 8px; border-radius: 12px; font-size: 0.85em;">Semantic Search</span>' : ''}
                </div>
                <div class="articles-grid">
                    ${articlesToDisplay.map(article => `
                        <div class="article-card">
                            <div class="article-title">${escapeHtml(article.title || 'No title')}</div>
                            <div class="article-meta">
                                <strong>Source:</strong> ${escapeHtml(article.source || 'Unknown')} | 
                                <strong>Date:</strong> ${article.publication_date || 'N/A'} | 
                                <strong>ID:</strong> ${article.id}
                            </div>
                            <div class="article-content">${escapeHtml((article.content || '').substring(0, 200))}${(article.content || '').length > 200 ? '...' : ''}</div>
                            ${article.similarity_score !== undefined ? `
                                <div style="margin-top: 10px;">
                                    <span class="score">Relevance: ${(article.similarity_score * 100).toFixed(1)}%</span>
                                </div>
                            ` : ''}
                            ${article.keywords ? `
                                <div class="article-keywords">
                                    ${article.keywords.split(',').slice(0, 5).map(k => `<span class="keyword-tag">${escapeHtml(k.trim())}</span>`).join('')}
                                </div>
                            ` : ''}
                            ${article.url ? `
                                <div class="article-url">
                                    <a href="${escapeHtml(article.url)}" target="_blank" onclick="return checkUrl(event, '${escapeHtml(article.url)}')">View Original Article →</a>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function fixUrl(url) {
            if (!url) return null;
            
            url = url.trim();
            
            if (url.startsWith('[INVALID]')) {
                return null;
            }
            
            if (url.includes('&ved=')) {
                url = url.split('&ved=')[0];
            }
            if (url.includes('?ved=')) {
                url = url.split('?ved=')[0];
            }
            if (url.includes('&usg=')) {
                url = url.split('&usg=')[0];
            }
            
            if (url.includes('&') && !url.includes('?')) {
                const parts = url.split('&');
                url = parts[0];
            }
            
            url = url.replace(/[&?]utm_[^&?]*/g, '');
            url = url.replace(/[&?]ref=[^&?]*/g, '');
            url = url.replace(/[&?]source=[^&?]*/g, '');
            url = url.replace(/[&?\/]+$/, '');
            
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                if (url.startsWith('//')) {
                    url = 'https:' + url;
                } else if (url.startsWith('www.')) {
                    url = 'https://' + url;
                } else {
                    if (url.includes('.') && !url.startsWith('/')) {
                        url = 'https://' + url;
                    } else {
                        return null;
                    }
                }
            }
            
            return url;
        }
        
        function checkUrl(event, url) {
            const fixedUrl = fixUrl(url);
            
            if (!fixedUrl) {
                event.preventDefault();
                alert('This article URL appears to be invalid or broken.\\n\\nURL: ' + url + '\\n\\nThe article may have been removed from the source or the URL is malformed.');
                return false;
            }
            
            if (fixedUrl !== url) {
                event.currentTarget.href = fixedUrl;
            }
            
            window.open(fixedUrl, '_blank');
            return false;
        }
        
        async function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            const messagesDiv = document.getElementById('chat-messages');
            
            // Add user message
            messagesDiv.innerHTML += `
                <div class="message user">
                    <strong>You:</strong> ${message}
                </div>
            `;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            input.value = '';
            chatHistory.push({user: message});
            
            // Add loading message
            messagesDiv.innerHTML += '<div class="message assistant loading">Thinking...</div>';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message, history: chatHistory})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Handle response properly
                const botResponse = data.response || data.answer || "Sorry, I couldn't generate a response.";
                
                // Remove loading, add response
                messagesDiv.innerHTML = messagesDiv.innerHTML.replace(
                    '<div class="message assistant loading">Thinking...</div>',
                    `<div class="message assistant"><strong>Assistant:</strong> ${botResponse}</div>`
                );
                
                chatHistory[chatHistory.length - 1].assistant = botResponse;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            } catch (error) {
                messagesDiv.innerHTML = messagesDiv.innerHTML.replace(
                    '<div class="message assistant loading">Thinking...</div>',
                    `<div class="message assistant" style="color: red;">Error: ${error.message}</div>`
                );
                console.error('Chat Error:', error);
            }
        }
        
        // Event listeners
        document.getElementById('search-query').addEventListener('input', () => {
            const query = document.getElementById('search-query').value.trim();
            if (query) {
                performSearch();
            } else {
                searchResults = [];
                useSemanticSearch = false;
                displayArticles(allArticles);
            }
        });
        document.getElementById('search-query').addEventListener('keypress', e => {
            if (e.key === 'Enter') performSearch();
        });
        document.getElementById('sort').addEventListener('change', () => {
            const articles = useSemanticSearch ? searchResults : allArticles;
            displayArticles(articles);
        });
        document.getElementById('chat-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') sendChatMessage();
        });
        
        // Load on page load
        loadArticles();
    </script>
</body>
</html>"""

def run_server(port=8002):
    """Run web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, HybridLLMHandler)
    
    url = f'http://localhost:{port}'
    print("=" * 60)
    print("Hybrid LLM-Powered Article System")
    print("=" * 60)
    print()
    print(f"Server running at: {url}")
    print()
    print("Features:")
    print("  [OK] Semantic Search (Local: sentence-transformers)")
    print("  [OK] Chatbot (Gemini API)")
    print("  [OK] Summarization (Local: BART)")
    print()
    print("Status:")
    print(f"  Gemini API: {'[OK] Available' if GEMINI_AVAILABLE else '[X] Not available'}")
    print(f"  Local Models: {'[OK] Available' if LOCAL_MODELS_AVAILABLE else '[X] Not available'}")
    print()
    print("Opening browser...")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        webbrowser.open(url)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.shutdown()

if __name__ == "__main__":
    run_server(port=8002)

