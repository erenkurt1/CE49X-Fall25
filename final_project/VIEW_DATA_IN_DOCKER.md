# How to View Data in Docker/PostgreSQL

## ✅ Data is in the Database!

Your database contains **1,004 articles**. Here are multiple ways to view them:

---

## Method 1: pgAdmin (Web GUI) - Easiest

### Setup:
1. **Start pgAdmin container:**
   ```bash
   docker-compose up -d pgadmin
   ```

2. **Access pgAdmin:**
   - Open browser: http://localhost:5050
   - Login:
     - Email: `admin@ce49x.com`
     - Password: `admin`

3. **Connect to Database:**
   - Right-click "Servers" → "Register" → "Server"
   - **General Tab:**
     - Name: `CE49X Database`
   - **Connection Tab:**
     - Host: `postgres` (container name)
     - Port: `5432`
     - Database: `ce49x_articles`
     - Username: `ce49x_user`
     - Password: `ce49x_password`
   - Click "Save"

4. **View Articles:**
   - Navigate: Servers → CE49X Database → Databases → ce49x_articles → Schemas → public → Tables → articles
   - Right-click "articles" → "View/Edit Data" → "All Rows"

---

## Method 2: Web Viewer (Simple Interface)

### Run Web Viewer:
```bash
python scripts/view_articles_web.py
```

This will:
- Start a web server at http://localhost:8000
- Open browser automatically
- Show all articles in a nice interface
- Allow searching and filtering
- Export to CSV

---

## Method 3: Command Line (Python Script)

### View Articles:
```bash
# View last 10 articles
python scripts/view_articles.py

# View more articles
python scripts/view_articles.py --limit 50

# View statistics
python scripts/view_articles.py --stats

# Export to CSV
python scripts/view_articles.py --export data/raw/articles_export.csv
```

---

## Method 4: Direct SQL Queries

### Using Docker:
```bash
# Connect to PostgreSQL
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles

# Then run SQL queries:
SELECT COUNT(*) FROM articles;
SELECT * FROM articles LIMIT 10;
SELECT title, source, publication_date FROM articles ORDER BY id LIMIT 20;
```

### Using Python:
```python
from scripts.database import DatabaseManager
import pandas as pd

db = DatabaseManager()
db.connect()

# Query articles
df = pd.read_sql_query("SELECT * FROM articles LIMIT 100", db.conn)
print(df)

db.disconnect()
```

---

## Method 5: Export to CSV

### Export All Articles:
```bash
python scripts/view_articles.py --export data/raw/articles_from_database.csv
```

Then open the CSV file in Excel or any spreadsheet application.

---

## Quick Verification

### Check if data exists:
```bash
# Method 1: Python script
python scripts/check_database.py

# Method 2: Docker command
docker exec ce49x_postgres psql -U ce49x_user -d ce49x_articles -c "SELECT COUNT(*) FROM articles;"
```

---

## Recommended: Use pgAdmin

**pgAdmin is the easiest way to view and explore your data:**
1. Visual interface
2. Easy query building
3. Data export options
4. Table browsing
5. SQL query editor

**Access:** http://localhost:5050

---

## Troubleshooting

### Problem: Can't connect to pgAdmin
- **Solution:** Make sure container is running: `docker ps`
- **Solution:** Check if port 5050 is available

### Problem: Can't see articles in pgAdmin
- **Solution:** Make sure you're connected to the correct database: `ce49x_articles`
- **Solution:** Check you're looking at the `articles` table in the `public` schema

### Problem: Web viewer doesn't work
- **Solution:** Make sure database is running: `docker-compose ps`
- **Solution:** Check database connection: `python scripts/check_database.py`

---

## Current Database Status

- **Total Articles:** 1,004
- **Container:** `ce49x_postgres` (running)
- **Database:** `ce49x_articles`
- **Port:** 5432 (PostgreSQL), 5050 (pgAdmin)

---

**Try pgAdmin first - it's the easiest way to view your data!**





