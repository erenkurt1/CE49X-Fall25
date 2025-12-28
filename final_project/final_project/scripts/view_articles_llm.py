"""
LLM-Powered Article Viewer
Uses semantic search to find articles based on natural language queries.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
import numpy as np
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

# Try to import sentence transformers for semantic search
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_SEARCH_AVAILABLE = True
    print("Loading semantic search model...")
    # Use a lightweight model for local use
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, fast model
        print("Semantic search model loaded successfully!")
    except Exception as e:
        print(f"Warning: Could not load sentence transformer model: {e}")
        print("Falling back to keyword-based search.")
        SEMANTIC_SEARCH_AVAILABLE = False
        model = None
except ImportError:
    print("Warning: sentence-transformers not installed.")
    print("Install with: pip install sentence-transformers")
    print("Falling back to keyword-based search.")
    SEMANTIC_SEARCH_AVAILABLE = False
    model = None

# Cache for article embeddings
article_embeddings_cache = None
articles_data_cache = None

def get_article_embeddings(articles):
    """Generate embeddings for all articles"""
    global article_embeddings_cache, articles_data_cache
    
    if not SEMANTIC_SEARCH_AVAILABLE or model is None:
        return None, articles
    
    # Cache embeddings
    if article_embeddings_cache is not None and articles_data_cache == articles:
        return article_embeddings_cache, articles
    
    print("Generating article embeddings...")
    # Combine title and content for better search
    texts = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('content', '')}"
        texts.append(text)
    
    embeddings = model.encode(texts, show_progress_bar=False)
    article_embeddings_cache = embeddings
    articles_data_cache = articles
    
    print(f"Generated embeddings for {len(articles)} articles")
    return embeddings, articles

def semantic_search(query, articles, embeddings, top_k=10):
    """Perform semantic search using embeddings"""
    if not SEMANTIC_SEARCH_AVAILABLE or model is None or embeddings is None:
        return keyword_search(query, articles, top_k)
    
    # Encode query
    query_embedding = model.encode([query], show_progress_bar=False)[0]
    
    # Calculate cosine similarity
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    # Get top K articles
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        article = articles[idx].copy()
        article['similarity_score'] = float(similarities[idx])
        results.append(article)
    
    return results

def keyword_search(query, articles, top_k=10):
    """Fallback keyword-based search"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    scored_articles = []
    for article in articles:
        title = (article.get('title', '') or '').lower()
        content = (article.get('content', '') or '').lower()
        keywords = (article.get('keywords', '') or '').lower()
        
        text = f"{title} {content} {keywords}"
        text_words = set(text.split())
        
        # Calculate simple word overlap score
        overlap = len(query_words.intersection(text_words))
        if overlap > 0:
            # Boost score if query words appear in title
            title_boost = sum(1 for word in query_words if word in title) * 2
            score = overlap + title_boost
            scored_articles.append((score, article))
    
    # Sort by score and return top K
    scored_articles.sort(key=lambda x: x[0], reverse=True)
    results = [article for score, article in scored_articles[:top_k]]
    
    return results

class LLMArticleViewerHandler(SimpleHTTPRequestHandler):
    """HTTP handler for LLM-powered article viewer"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/api/articles':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            articles_json = self.get_articles_json()
            self.wfile.write(articles_json.encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            stats_json = self.get_stats_json()
            self.wfile.write(stats_json.encode())
        elif self.path.startswith('/api/search?'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            query = self.path.split('query=')[1].split('&')[0] if 'query=' in self.path else ''
            query = query.replace('%20', ' ').replace('%22', '"')
            search_results = self.search_articles(query)
            self.wfile.write(json.dumps(search_results).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_articles_json(self):
        """Get all articles as JSON"""
        db = DatabaseManager()
        if not db.connect():
            return json.dumps({"error": "Database connection failed"})
        
        try:
            query = """
                SELECT id, title, source, publication_date, content, url, keywords
                FROM articles
                ORDER BY id
                LIMIT 1000
            """
            import pandas as pd
            df = pd.read_sql_query(query, db.conn)
            
            articles = df.to_dict('records')
            
            for article in articles:
                if pd.notna(article.get('publication_date')):
                    article['publication_date'] = str(article['publication_date'])
                else:
                    article['publication_date'] = None
            
            db.disconnect()
            return json.dumps({"articles": articles, "count": len(articles)})
        except Exception as e:
            db.disconnect()
            return json.dumps({"error": str(e)})
    
    def get_stats_json(self):
        """Get statistics as JSON"""
        db = DatabaseManager()
        if not db.connect():
            return json.dumps({"error": "Database connection failed"})
        
        try:
            count = db.get_article_count()
            stats = db.get_article_stats()
            db.disconnect()
            return json.dumps({"count": count, "stats": stats})
        except Exception as e:
            db.disconnect()
            return json.dumps({"error": str(e)})
    
    def search_articles(self, query):
        """Search articles using LLM/semantic search"""
        if not query or len(query.strip()) == 0:
            return {"error": "Query is required", "results": []}
        
        db = DatabaseManager()
        if not db.connect():
            return {"error": "Database connection failed", "results": []}
        
        try:
            import pandas as pd
            query_sql = """
                SELECT id, title, source, publication_date, content, url, keywords
                FROM articles
                ORDER BY id
            """
            df = pd.read_sql_query(query_sql, db.conn)
            articles = df.to_dict('records')
            
            for article in articles:
                if pd.notna(article.get('publication_date')):
                    article['publication_date'] = str(article['publication_date'])
                else:
                    article['publication_date'] = None
            
            # Get embeddings
            embeddings, articles = get_article_embeddings(articles)
            
            # Perform search
            if SEMANTIC_SEARCH_AVAILABLE and embeddings is not None:
                results = semantic_search(query, articles, embeddings, top_k=20)
                search_type = "semantic"
            else:
                results = keyword_search(query, articles, top_k=20)
                search_type = "keyword"
            
            db.disconnect()
            
            return {
                "query": query,
                "search_type": search_type,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            db.disconnect()
            return {"error": str(e), "results": []}
    
    def get_html(self):
        """Get HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CE49X Final Project - LLM-Powered Article Search</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75em;
            margin-left: 10px;
        }
        .badge.keyword {
            background: #FF9800;
        }
        .search-section {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .example-queries {
            margin-top: 15px;
        }
        .example-queries h3 {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }
        .example-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .example-tag {
            background: white;
            border: 1px solid #ddd;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
        }
        .example-tag:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .stats {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .search-results {
            margin-top: 20px;
        }
        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .results-count {
            color: #666;
            font-size: 0.9em;
        }
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
        }
        .article-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: white;
            transition: transform 0.2s, box-shadow 0.2s;
            position: relative;
        }
        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .similarity-score {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: bold;
        }
        .article-title {
            font-size: 1.1em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.4;
            padding-right: 80px;
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
            color: #667eea;
            text-decoration: none;
            font-size: 0.85em;
        }
        .article-url a:hover {
            text-decoration: underline;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .no-results {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 CE49X Final Project - LLM-Powered Article Search</h1>
        <p class="subtitle">
            Describe what you're looking for in natural language, and AI will find the most relevant articles.
            <span class="badge" id="search-type-badge">Semantic Search</span>
        </p>
        
        <div class="stats" id="stats">
            <div class="stat-item">
                <div class="stat-value" id="total-count">-</div>
                <div class="stat-label">Total Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="unique-sources">-</div>
                <div class="stat-label">Unique Sources</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="avg-length">-</div>
                <div class="stat-label">Avg Content Length</div>
            </div>
        </div>
        
        <div class="search-section">
            <div class="search-box">
                <input type="text" id="search-query" placeholder="Describe what you're looking for... (e.g., 'articles about AI in bridge construction' or 'machine learning for structural health monitoring')" />
                <button onclick="performSearch()" id="search-btn">Search</button>
            </div>
            <div class="example-queries">
                <h3>Try these example queries:</h3>
                <div class="example-tags">
                    <span class="example-tag" onclick="setQuery('AI applications in structural engineering')">AI in Structural Engineering</span>
                    <span class="example-tag" onclick="setQuery('machine learning for construction safety')">ML for Construction Safety</span>
                    <span class="example-tag" onclick="setQuery('robotics in tunnel construction')">Robotics in Tunnels</span>
                    <span class="example-tag" onclick="setQuery('predictive analytics for infrastructure')">Predictive Analytics</span>
                    <span class="example-tag" onclick="setQuery('computer vision for bridge inspection')">Computer Vision</span>
                    <span class="example-tag" onclick="setQuery('sustainable construction with AI')">Sustainable Construction</span>
                    <span class="example-tag" onclick="setQuery('autonomous vehicles in transportation')">Autonomous Vehicles</span>
                    <span class="example-tag" onclick="setQuery('geotechnical engineering with machine learning')">Geotechnical ML</span>
                </div>
            </div>
        </div>
        
        <div id="search-results" class="search-results" style="display: none;">
            <div class="results-header">
                <h2>Search Results</h2>
                <div class="results-count" id="results-count"></div>
            </div>
            <div id="articles-container"></div>
        </div>
    </div>
    
    <script>
        let allArticles = [];
        let currentSearchType = 'semantic';
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('total-count').textContent = data.count || 0;
                if (data.stats) {
                    document.getElementById('unique-sources').textContent = data.stats.unique_sources || 0;
                    const avgLen = data.stats.avg_content_length;
                    document.getElementById('avg-length').textContent = avgLen ? Math.round(avgLen) + ' chars' : '-';
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        function setQuery(query) {
            document.getElementById('search-query').value = query;
            performSearch();
        }
        
        async function performSearch() {
            const query = document.getElementById('search-query').value.trim();
            
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            const searchBtn = document.getElementById('search-btn');
            const resultsDiv = document.getElementById('search-results');
            const container = document.getElementById('articles-container');
            
            searchBtn.disabled = true;
            searchBtn.textContent = 'Searching...';
            container.innerHTML = '<div class="loading">Searching articles...</div>';
            resultsDiv.style.display = 'block';
            
            try {
                const encodedQuery = encodeURIComponent(query);
                const response = await fetch(`/api/search?query=${encodedQuery}`);
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                    return;
                }
                
                currentSearchType = data.search_type || 'keyword';
                const badge = document.getElementById('search-type-badge');
                badge.textContent = currentSearchType === 'semantic' ? 'Semantic Search' : 'Keyword Search';
                badge.className = currentSearchType === 'semantic' ? 'badge' : 'badge keyword';
                
                displayResults(data.results || [], data.count || 0);
            } catch (error) {
                container.innerHTML = `<div class="error">Error performing search: ${error.message}</div>`;
            } finally {
                searchBtn.disabled = false;
                searchBtn.textContent = 'Search';
            }
        }
        
        function displayResults(results, count) {
            const container = document.getElementById('articles-container');
            const countDiv = document.getElementById('results-count');
            
            countDiv.textContent = `Found ${count} article${count !== 1 ? 's' : ''}`;
            
            if (results.length === 0) {
                container.innerHTML = '<div class="no-results">No articles found. Try a different query.</div>';
                return;
            }
            
            container.innerHTML = `
                <div class="articles-grid">
                    ${results.map(article => `
                        <div class="article-card">
                            ${article.similarity_score !== undefined ? `
                                <div class="similarity-score">${(article.similarity_score * 100).toFixed(0)}% match</div>
                            ` : ''}
                            <div class="article-title">${escapeHtml(article.title || 'No title')}</div>
                            <div class="article-meta">
                                <strong>Source:</strong> ${escapeHtml(article.source || 'Unknown')} | 
                                <strong>Date:</strong> ${article.publication_date || 'N/A'} | 
                                <strong>ID:</strong> ${article.id}
                            </div>
                            <div class="article-content">${escapeHtml((article.content || '').substring(0, 200))}${(article.content || '').length > 200 ? '...' : ''}</div>
                            ${article.keywords ? `
                                <div class="article-keywords">
                                    ${article.keywords.split(',').map(k => `<span class="keyword-tag">${escapeHtml(k.trim())}</span>`).join('')}
                                </div>
                            ` : ''}
                            ${article.url ? `
                                <div class="article-url">
                                    <a href="${escapeHtml(article.url)}" target="_blank" onclick="return checkUrl(event, '${escapeHtml(article.url)}')">View Original Article →</a>
                                    <span class="url-status" id="url-status-${article.id}" style="display:none; margin-left:10px; font-size:0.8em;"></span>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function fixUrl(url) {
            if (!url) return null;
            
            // Remove any leading/trailing whitespace
            url = url.trim();
            
            // Skip if already marked as invalid
            if (url.startsWith('[INVALID]')) {
                return null;
            }
            
            // Remove Google News tracking parameters (most common issue)
            if (url.includes('&ved=')) {
                url = url.split('&ved=')[0];
            }
            if (url.includes('?ved=')) {
                url = url.split('?ved=')[0];
            }
            if (url.includes('&usg=')) {
                url = url.split('&usg=')[0];
            }
            
            // Fix malformed URLs - if URL has & but no ?, it's malformed
            // This is the main issue: Google News URLs have & instead of ?
            if (url.includes('&') && !url.includes('?')) {
                // Extract base URL (everything before first &)
                const parts = url.split('&');
                url = parts[0];
            }
            
            // Remove other tracking parameters using regex-like approach
            url = url.replace(/[&?]utm_[^&?]*/g, '');
            url = url.replace(/[&?]ref=[^&?]*/g, '');
            url = url.replace(/[&?]source=[^&?]*/g, '');
            
            // Clean up trailing characters
            url = url.replace(/[&?\/]+$/, '');
            
            // If URL doesn't start with http:// or https://, try to fix it
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                // If it starts with //, add https:
                if (url.startsWith('//')) {
                    url = 'https:' + url;
                }
                // If it starts with www., add https://
                else if (url.startsWith('www.')) {
                    url = 'https://' + url;
                }
                // Otherwise, assume it's a relative URL or invalid
                else {
                    // Try to make it absolute by checking if it looks like a domain
                    if (url.includes('.') && !url.startsWith('/')) {
                        url = 'https://' + url;
                    } else {
                        // Probably a broken/invalid URL
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
            
            // If URL was fixed, update the href
            if (fixedUrl !== url) {
                event.currentTarget.href = fixedUrl;
            }
            
            // Open in new tab
            window.open(fixedUrl, '_blank');
            return false; // Prevent default navigation
        }
        
        // Allow Enter key to search
        document.getElementById('search-query').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
        
        // Load stats on page load
        loadStats();
    </script>
</body>
</html>"""

def run_server(port=8001):
    """Run web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, LLMArticleViewerHandler)
    
    url = f'http://localhost:{port}'
    print("=" * 60)
    print("LLM-Powered Article Viewer Web Server")
    print("=" * 60)
    print()
    print(f"Server running at: {url}")
    print()
    print("Features:")
    print("  - Natural language search")
    print("  - Semantic similarity matching")
    print("  - Relevance scores")
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
    import sys
    port = 8001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            pass
    
    run_server(port)

