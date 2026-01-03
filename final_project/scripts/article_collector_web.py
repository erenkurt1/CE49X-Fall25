"""
Web Interface for Article Collection
Runs on localhost:8003 to manage article collection, filtering, and addition
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import webbrowser
import subprocess
import threading
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import DatabaseManager
from add_new_articles import collect_and_add_articles

class ArticleCollectorHandler(SimpleHTTPRequestHandler):
    """HTTP handler for article collection interface"""
    
    collection_status = {
        'running': False,
        'progress': '',
        'results': None,
        'error': None
    }
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/api/status':
            self.send_json_response(self.collection_status)
        elif self.path == '/api/stats':
            self.handle_get_stats()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/collect':
            self.handle_collect()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_get_stats(self):
        """Get database statistics"""
        db = DatabaseManager()
        if not db.connect():
            self.send_json_response({"error": "Database connection failed"}, 500)
            return
        
        try:
            count = db.get_article_count()
            stats = db.get_article_stats()
            db.disconnect()
            self.send_json_response({
                "count": count,
                "stats": stats
            })
        except Exception as e:
            db.disconnect()
            self.send_json_response({"error": str(e)}, 500)
    
    def handle_collect(self):
        """Handle article collection request"""
        if self.collection_status['running']:
            self.send_json_response({
                "error": "Collection already in progress",
                "status": self.collection_status
            }, 400)
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            max_queries = data.get('max_queries', 10)
            max_results = data.get('max_results', 20)
            days_back = data.get('days_back', 7)
            
            # Start collection in background thread
            self.collection_status = {
                'running': True,
                'progress': 'Starting collection...',
                'results': None,
                'error': None
            }
            
            thread = threading.Thread(
                target=self.run_collection,
                args=(max_queries, max_results, days_back)
            )
            thread.daemon = True
            thread.start()
            
            self.send_json_response({
                "message": "Collection started",
                "status": self.collection_status
            })
        except Exception as e:
            self.collection_status['error'] = str(e)
            self.collection_status['running'] = False
            self.send_json_response({"error": str(e)}, 500)
    
    def run_collection(self, max_queries, max_results, days_back):
        """Run article collection in background"""
        try:
            self.collection_status['progress'] = 'Collecting articles...'
            results = collect_and_add_articles(
                max_queries=max_queries,
                max_results_per_query=max_results,
                days_back=days_back
            )
            
            self.collection_status['running'] = False
            self.collection_status['progress'] = 'Complete!'
            self.collection_status['results'] = results
            self.collection_status['error'] = None
        except Exception as e:
            self.collection_status['running'] = False
            self.collection_status['progress'] = 'Error occurred'
            self.collection_status['error'] = str(e)
            self.collection_status['results'] = None
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        try:
            json_str = json.dumps(data, ensure_ascii=False, default=str)
            self.send_response(status)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json_str.encode('utf-8'))
        except Exception as e:
            print(f"Error sending JSON response: {e}")
    
    def get_html(self):
        """Get HTML page"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Article Collector - CE49X</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #7f8c8d 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
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
        .content {
            padding: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #34495e;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input[type="number"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        input:focus {
            outline: none;
            border-color: #34495e;
        }
        button {
            padding: 15px 30px;
            background: #34495e;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
            width: 100%;
        }
        button:hover { background: #2c3e50; }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        .status-box {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #34495e;
        }
        .status-box.running {
            border-left-color: #3498db;
        }
        .status-box.success {
            border-left-color: #27ae60;
        }
        .status-box.error {
            border-left-color: #e74c3c;
        }
        .progress {
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        .results {
            margin-top: 20px;
        }
        .result-item {
            padding: 10px;
            background: white;
            margin: 5px 0;
            border-radius: 5px;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #34495e;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 Article Collector</h1>
            <div class="subtitle">CE49X Final Project - Add New Articles to System</div>
        </header>
        
        <div class="content">
            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-articles">-</div>
                    <div class="stat-label">Total Articles</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="unique-sources">-</div>
                    <div class="stat-label">Unique Sources</div>
                </div>
            </div>
            
            <h2>Collection Settings</h2>
            <form id="collect-form">
                <div class="form-group">
                    <label for="max-queries">Number of Search Queries:</label>
                    <input type="number" id="max-queries" value="10" min="1" max="50">
                </div>
                <div class="form-group">
                    <label for="max-results">Max Results per Query:</label>
                    <input type="number" id="max-results" value="20" min="1" max="50">
                </div>
                <div class="form-group">
                    <label for="days-back">Days Back to Search:</label>
                    <input type="number" id="days-back" value="7" min="1" max="30">
                </div>
                <button type="submit" id="collect-btn">Start Collection</button>
            </form>
            
            <div class="status-box" id="status-box" style="display: none;">
                <div class="progress" id="progress"></div>
                <div class="results" id="results"></div>
            </div>
        </div>
    </div>
    
    <script>
        let statusCheckInterval = null;
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('total-articles').textContent = data.count || 0;
                if (data.stats) {
                    document.getElementById('unique-sources').textContent = data.stats.unique_sources || 0;
                }
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function startCollection() {
            const maxQueries = parseInt(document.getElementById('max-queries').value);
            const maxResults = parseInt(document.getElementById('max-results').value);
            const daysBack = parseInt(document.getElementById('days-back').value);
            
            const btn = document.getElementById('collect-btn');
            btn.disabled = true;
            btn.textContent = 'Collecting...';
            
            const statusBox = document.getElementById('status-box');
            statusBox.style.display = 'block';
            statusBox.className = 'status-box running';
            document.getElementById('progress').innerHTML = '<span class="loading"></span>Starting collection...';
            document.getElementById('results').innerHTML = '';
            
            try {
                const response = await fetch('/api/collect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        max_queries: maxQueries,
                        max_results: maxResults,
                        days_back: daysBack
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Start polling for status
                statusCheckInterval = setInterval(checkStatus, 2000);
                checkStatus();
            } catch (error) {
                statusBox.className = 'status-box error';
                document.getElementById('progress').textContent = `Error: ${error.message}`;
                btn.disabled = false;
                btn.textContent = 'Start Collection';
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                const statusBox = document.getElementById('status-box');
                const progressDiv = document.getElementById('progress');
                const resultsDiv = document.getElementById('results');
                
                if (status.running) {
                    statusBox.className = 'status-box running';
                    progressDiv.innerHTML = `<span class="loading"></span>${status.progress || 'Collecting...'}`;
                } else {
                    clearInterval(statusCheckInterval);
                    statusCheckInterval = null;
                    
                    const btn = document.getElementById('collect-btn');
                    btn.disabled = false;
                    btn.textContent = 'Start Collection';
                    
                    if (status.error) {
                        statusBox.className = 'status-box error';
                        progressDiv.textContent = `Error: ${status.error}`;
                    } else if (status.results) {
                        statusBox.className = 'status-box success';
                        progressDiv.textContent = '✓ Collection Complete!';
                        
                        const results = status.results;
                        resultsDiv.innerHTML = `
                            <h3>Results:</h3>
                            <div class="result-item"><strong>Collected:</strong> ${results.collected || 0} articles</div>
                            <div class="result-item"><strong>Filtered:</strong> ${results.filtered || 0} articles</div>
                            <div class="result-item"><strong>Duplicates:</strong> ${results.duplicates || 0} articles (skipped)</div>
                            <div class="result-item"><strong>New:</strong> ${results.new || 0} articles</div>
                            <div class="result-item"><strong>Added:</strong> ${results.added || 0} articles</div>
                            <div class="result-item"><strong>Failed:</strong> ${results.failed || 0} articles</div>
                        `;
                        
                        // Reload stats
                        loadStats();
                    }
                }
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }
        
        document.getElementById('collect-form').addEventListener('submit', (e) => {
            e.preventDefault();
            startCollection();
        });
        
        // Load stats on page load
        loadStats();
        setInterval(loadStats, 30000); // Refresh stats every 30 seconds
    </script>
</body>
</html>"""

def run_server(port=8003):
    """Run web server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ArticleCollectorHandler)
    
    url = f'http://localhost:{port}'
    print("=" * 60)
    print("Article Collector Web Interface")
    print("=" * 60)
    print()
    print(f"Server running at: {url}")
    print()
    print("Features:")
    print("  [OK] Collect new articles from Google News")
    print("  [OK] Filter articles for relevance")
    print("  [OK] Check for duplicates")
    print("  [OK] Add new articles to database")
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
    run_server(port=8003)




