"""
Web Viewer for Articles in Database
Creates a simple HTML interface to view articles from PostgreSQL.
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager

class ArticleViewerHandler(SimpleHTTPRequestHandler):
    """HTTP handler for article viewer"""
    
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
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_articles_json(self):
        """Get articles as JSON"""
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
            
            # Convert to list of dicts
            articles = df.to_dict('records')
            
            # Convert dates to strings
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
    
    def get_html(self):
        """Get HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CE49X Final Project - Article Viewer</title>
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
        .controls {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        input, select, button {
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
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
        }
        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 CE49X Final Project - Article Database Viewer</h1>
        <p style="color: #666; margin-bottom: 20px;">Viewing articles from PostgreSQL database</p>
        
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
        
        <div class="controls">
            <input type="text" id="search" placeholder="Search articles..." style="flex: 1;">
            <select id="sort">
                <option value="id">Sort by ID</option>
                <option value="date">Sort by Date</option>
                <option value="title">Sort by Title</option>
            </select>
            <button onclick="loadArticles()">Refresh</button>
            <button onclick="exportCSV()">Export CSV</button>
        </div>
        
        <div id="articles-container">
            <div class="loading">Loading articles...</div>
        </div>
    </div>
    
    <script>
        let allArticles = [];
        
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
        
        async function loadArticles() {
            const container = document.getElementById('articles-container');
            container.innerHTML = '<div class="loading">Loading articles...</div>';
            
            try {
                const response = await fetch('/api/articles');
                const data = await response.json();
                
                if (data.error) {
                    container.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                    return;
                }
                
                allArticles = data.articles || [];
                displayArticles(allArticles);
            } catch (error) {
                container.innerHTML = `<div class="error">Error loading articles: ${error.message}</div>`;
            }
        }
        
        function displayArticles(articles) {
            const container = document.getElementById('articles-container');
            
            if (articles.length === 0) {
                container.innerHTML = '<div class="loading">No articles found.</div>';
                return;
            }
            
            const sortBy = document.getElementById('sort').value;
            let sorted = [...articles];
            
            if (sortBy === 'date') {
                sorted.sort((a, b) => {
                    const dateA = a.publication_date || '';
                    const dateB = b.publication_date || '';
                    return dateB.localeCompare(dateA);
                });
            } else if (sortBy === 'title') {
                sorted.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
            }
            
            const searchTerm = document.getElementById('search').value.toLowerCase();
            if (searchTerm) {
                sorted = sorted.filter(article => 
                    (article.title || '').toLowerCase().includes(searchTerm) ||
                    (article.content || '').toLowerCase().includes(searchTerm) ||
                    (article.keywords || '').toLowerCase().includes(searchTerm)
                );
            }
            
            container.innerHTML = `
                <div style="margin-bottom: 15px; color: #666;">
                    Showing ${sorted.length} of ${allArticles.length} articles
                </div>
                <div class="articles-grid">
                    ${sorted.map(article => `
                        <div class="article-card">
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
            // These appear as &ved= or ?ved= or sometimes just & at wrong position
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
        
        function exportCSV() {
            if (allArticles.length === 0) {
                alert('No articles to export. Please load articles first.');
                return;
            }
            
            // Create CSV
            const headers = ['ID', 'Title', 'Source', 'Publication Date', 'Content', 'URL', 'Keywords'];
            const rows = allArticles.map(a => [
                a.id || '',
                `"${(a.title || '').replace(/"/g, '""')}"`,
                a.source || '',
                a.publication_date || '',
                `"${(a.content || '').replace(/"/g, '""')}"`,
                a.url || '',
                a.keywords || ''
            ]);
            
            const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
            
            // Download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'articles_export.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        // Event listeners
        document.getElementById('search').addEventListener('input', () => displayArticles(allArticles));
        document.getElementById('sort').addEventListener('change', () => displayArticles(allArticles));
        
        // Load on page load
        loadStats();
        loadArticles();
    </script>
</body>
</html>"""

def run_server(port=8000):
    """Run web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ArticleViewerHandler)
    
    url = f'http://localhost:{port}'
    print("=" * 60)
    print("Article Viewer Web Server")
    print("=" * 60)
    print()
    print(f"Server running at: {url}")
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
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            pass
    
    run_server(port)

