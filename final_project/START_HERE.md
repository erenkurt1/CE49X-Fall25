# CE49X Final Project - Quick Start Guide

## 🚀 Getting Started with Task 1: Data Collection

This project uses **Docker with PostgreSQL** for data storage.

### Step 1: Install Prerequisites

1. **Install Docker Desktop**
   - Download: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Verify: Open terminal and run `docker --version`

2. **Python Environment**
   - Python 3.8+ required
   - Create virtual environment:
     ```bash
     cd final_project
     python -m venv venv
     venv\Scripts\activate  # Windows
     # or: source venv/bin/activate  # Mac/Linux
     ```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up PostgreSQL Database

1. **Start Docker container:**
   ```bash
   docker-compose up -d
   ```

2. **Verify it's running:**
   ```bash
   docker ps
   ```
   You should see `ce49x_postgres` container.

3. **Test database connection:**
   ```bash
   python scripts/database.py
   ```

### Step 4: Configure API Keys

1. **Get NewsAPI Key:**
   - Sign up at: https://newsapi.org
   - Free tier: 100 requests/day, 1 month history
   - Copy your API key

2. **Create `.env` file** in `final_project/` directory:
   ```env
   # Database (already configured in docker-compose.yml)
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ce49x_articles
   DB_USER=ce49x_user
   DB_PASSWORD=ce49x_password

   # NewsAPI
   NEWSAPI_KEY=your_newsapi_key_here
   ```

### Step 5: Start Data Collection

**Option A: CSV First (Recommended - Review before upload)**
```bash
python scripts/newsapi_collector_csv.py
```
This saves to CSV first so you can review the data.

**Option B: Direct to Database**
```bash
python scripts/newsapi_collector.py
```
This saves directly to PostgreSQL.

### Step 6: Review and Upload (If using CSV approach)

1. **Review CSV file:**
   - Location: `data/raw/articles_collected_*.csv`
   - Open in Excel or any CSV viewer

2. **Upload to database:**
   ```bash
   python scripts/upload_csv_to_db.py
   ```

### Step 6: Monitor Progress

**Check article count:**
```bash
python -c "from scripts.database import DatabaseManager; db = DatabaseManager(); db.connect(); print(f'Total articles: {db.get_article_count()}')"
```

**View in PostgreSQL:**
```bash
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles -c "SELECT COUNT(*) FROM articles;"
```

**View statistics:**
```bash
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles -c "SELECT * FROM article_stats;"
```

## 📊 Project Structure

```
final_project/
├── docker-compose.yml          # Docker configuration
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables (create this)
├── scripts/
│   ├── database.py             # Database connection & operations
│   ├── newsapi_collector.py    # Main data collection script
│   ├── init_db.sql             # Database schema
│   └── ...
├── data/
│   └── raw/                    # (Data stored in PostgreSQL)
└── docs/
    └── data_description_template.md
```

## 🎯 Task 1 Requirements Checklist

- [ ] PostgreSQL database running in Docker
- [ ] Database connection tested successfully
- [ ] NewsAPI key configured in `.env`
- [ ] Data collection script run successfully
- [ ] **≥ 500 articles collected** in database
- [ ] Each article has: Title, Date, Source, Content, URL
- [ ] Data Description document completed

## 📝 Important Notes

### API Rate Limits
- NewsAPI free tier: **100 requests/day**
- If you hit the limit, wait 24 hours or upgrade to paid tier
- The script includes delays to be respectful

### Data Collection Strategy
- Start with NewsAPI (easiest)
- May need to run over multiple days due to rate limits
- Can combine with web scraping for more sources
- Target: **500+ unique articles**

### Database Management
- Data persists in Docker volume
- To reset: `docker-compose down -v` then `docker-compose up -d`
- To backup: See `DOCKER_SETUP.md`

## 🆘 Troubleshooting

**Problem:** Docker container won't start
- **Solution:** Make sure Docker Desktop is running
- Check port 5432 is not in use

**Problem:** Can't connect to database
- **Solution:** Verify container is running: `docker ps`
- Check `.env` file has correct credentials

**Problem:** NewsAPI rate limit
- **Solution:** Wait 24 hours or run collection over multiple days
- Consider adding web scraping as additional source

**Problem:** Not enough articles
- **Solution:** 
  - Increase date range (modify `DAYS_BACK` in script)
  - Add more keyword combinations
  - Use multiple data sources

## 📚 Documentation

- **Detailed Pathway:** `../Task1_Data_Collection_Pathway.md`
- **Quick Checklist:** `../Task1_Quick_Start_Checklist.md`
- **Docker Setup:** `DOCKER_SETUP.md`
- **Data Description Template:** `docs/data_description_template.md`

## ✅ Next Steps After Task 1

Once you have 500+ articles:
1. Complete Data Description document
2. Export data if needed: `db.export_to_csv('data/raw/articles_backup.csv')`
3. Proceed to **Task 2: Text Preprocessing & NLP**

---

**Need Help?** Check the detailed pathway document or Docker setup guide for more information.

