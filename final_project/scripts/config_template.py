"""
Configuration file template
Copy this file to config.py and fill in your API keys and settings

DO NOT commit config.py to version control - it's already in .gitignore
"""

# NewsAPI Configuration
NEWSAPI_KEY = "your_newsapi_key_here"

# Web Scraping Configuration
SCRAPING_DELAY = 2  # Seconds to wait between requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Data Collection Settings
MAX_ARTICLES_PER_QUERY = 100  # Maximum articles to fetch per search query
DAYS_BACK = 90  # How many days back to search (for NewsAPI)
MIN_ARTICLE_LENGTH = 200  # Minimum word count for articles

# File Paths
PROJECT_ROOT = r"C:\Users\erenb\PycharmProjects\pythonProject1\final_project"
DATA_RAW_DIR = f"{PROJECT_ROOT}/data/raw"
DATA_PROCESSED_DIR = f"{PROJECT_ROOT}/data/processed"

# Target number of articles
TARGET_ARTICLE_COUNT = 500






