"""
Database utility module for PostgreSQL connection and operations
Handles connection to PostgreSQL database running in Docker
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import os
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        """Initialize database connection parameters"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'ce49x_articles'),
            'user': os.getenv('DB_USER', 'ce49x_user'),
            'password': os.getenv('DB_PASSWORD', 'ce49x_password')
        }
        self.conn = None
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("Connected to PostgreSQL database")
            return True
        except psycopg2.Error as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def check_connection(self):
        """Check if database connection is active"""
        if self.conn is None:
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except:
            return False
    
    def insert_article(self, article: Dict) -> bool:
        """
        Insert a single article into the database
        
        Args:
            article: Dictionary with keys: title, publication_date, source, content, url, keywords
        
        Returns:
            True if inserted successfully, False otherwise
        """
        if not self.check_connection():
            if not self.connect():
                return False
        
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                    INSERT INTO articles (title, publication_date, source, content, url, keywords)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                    RETURNING id
                """
                cur.execute(insert_query, (
                    article.get('title', ''),
                    article.get('publication_date'),
                    article.get('source', 'Unknown'),
                    article.get('content', ''),
                    article.get('url', ''),
                    article.get('keywords', '')
                ))
                
                result = cur.fetchone()
                if result:
                    self.conn.commit()
                    return True
                else:
                    # Article already exists (duplicate URL)
                    return False
                    
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error inserting article: {e}")
            return False
    
    def insert_articles_batch(self, articles: List[Dict]) -> Dict:
        """
        Insert multiple articles in a batch
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Dictionary with counts: {'inserted': X, 'duplicates': Y, 'errors': Z}
        """
        if not self.check_connection():
            if not self.connect():
                return {'inserted': 0, 'duplicates': 0, 'errors': len(articles)}
        
        stats = {'inserted': 0, 'duplicates': 0, 'errors': 0}
        
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                    INSERT INTO articles (title, publication_date, source, content, url, keywords)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING
                """
                
                data_to_insert = []
                for article in articles:
                    data_to_insert.append((
                        article.get('title', ''),
                        article.get('publication_date'),
                        article.get('source', 'Unknown'),
                        article.get('content', ''),
                        article.get('url', ''),
                        article.get('keywords', '')
                    ))
                
                cur.executemany(insert_query, data_to_insert)
                inserted_count = cur.rowcount
                self.conn.commit()
                
                stats['inserted'] = inserted_count
                stats['duplicates'] = len(articles) - inserted_count
                
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Error in batch insert: {e}")
            stats['errors'] = len(articles)
        
        return stats
    
    def get_article_count(self) -> int:
        """Get total number of articles in database"""
        if not self.check_connection():
            if not self.connect():
                return 0
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM articles")
                return cur.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Error getting article count: {e}")
            return 0
    
    def get_article_stats(self) -> Dict:
        """Get statistics about articles in database"""
        if not self.check_connection():
            if not self.connect():
                return {}
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM article_stats")
                return dict(cur.fetchone())
        except psycopg2.Error as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def check_duplicate(self, url: str) -> bool:
        """Check if an article with given URL already exists"""
        if not self.check_connection():
            if not self.connect():
                return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1 FROM articles WHERE url = %s", (url,))
                return cur.fetchone() is not None
        except psycopg2.Error as e:
            print(f"Error checking duplicate: {e}")
            return False
    
    def export_to_csv(self, filename: str) -> bool:
        """
        Export all articles to CSV file
        
        Args:
            filename: Path to output CSV file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.check_connection():
            if not self.connect():
                return False
        
        try:
            import pandas as pd
            
            query = """
                SELECT id, title, publication_date, source, content, url, keywords, 
                       collected_date, created_at
                FROM articles
                ORDER BY publication_date DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"✓ Exported {len(df)} articles to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def fetch_all_articles(self) -> List[Dict]:
        """Fetch all articles from database"""
        if not self.check_connection():
            if not self.connect():
                return []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT id, title, publication_date, source, content, url, keywords
                    FROM articles
                    ORDER BY id
                """
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]
        except psycopg2.Error as e:
            print(f"Error fetching articles: {e}")
            return []
    
    def get_articles_by_keyword(self, keyword: str, limit: int = 100) -> List[Dict]:
        """Get articles containing a specific keyword"""
        if not self.check_connection():
            if not self.connect():
                return []
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT * FROM articles 
                    WHERE keywords ILIKE %s OR title ILIKE %s OR content ILIKE %s
                    ORDER BY publication_date DESC
                    LIMIT %s
                """
                pattern = f"%{keyword}%"
                cur.execute(query, (pattern, pattern, pattern, limit))
                return [dict(row) for row in cur.fetchall()]
        except psycopg2.Error as e:
            print(f"Error querying articles: {e}")
            return []


def test_connection():
    """Test database connection"""
    db = DatabaseManager()
    if db.connect():
        count = db.get_article_count()
        print(f"Current articles in database: {count}")
        stats = db.get_article_stats()
        if stats:
            print(f"Database statistics: {stats}")
        db.disconnect()
        return True
    return False


if __name__ == "__main__":
    # Test the database connection
    print("Testing database connection...")
    test_connection()

