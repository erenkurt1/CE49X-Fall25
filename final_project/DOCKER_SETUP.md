# Docker & PostgreSQL Setup Guide

This guide will help you set up PostgreSQL using Docker for the CE49X Final Project.

## Prerequisites

- Docker Desktop installed and running
  - Download from: https://www.docker.com/products/docker-desktop
  - Verify installation: `docker --version`

## Quick Start

### 1. Start PostgreSQL Container

Navigate to the project directory and start the Docker container:

```bash
cd final_project
docker-compose up -d
```

This will:
- Download PostgreSQL 15 image (if not already downloaded)
- Create a container named `ce49x_postgres`
- Initialize the database with the schema
- Expose PostgreSQL on port 5432

### 2. Verify Container is Running

```bash
docker ps
```

You should see `ce49x_postgres` in the list.

### 3. Check Database Connection

Test the database connection:

```bash
python scripts/database.py
```

Or from Python:
```python
from scripts.database import test_connection
test_connection()
```

### 4. View Database Logs (Optional)

```bash
docker-compose logs postgres
```

## Database Configuration

The database is configured with these default settings (defined in `docker-compose.yml`):

- **Host:** localhost
- **Port:** 5432
- **Database:** ce49x_articles
- **Username:** ce49x_user
- **Password:** ce49x_password

### Environment Variables

Create a `.env` file in the `final_project/` directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ce49x_articles
DB_USER=ce49x_user
DB_PASSWORD=ce49x_password

# NewsAPI Configuration
NEWSAPI_KEY=your_newsapi_key_here
```

**Note:** The `.env` file is already in `.gitignore` to keep your credentials safe.

## Common Commands

### Start Container
```bash
docker-compose up -d
```

### Stop Container
```bash
docker-compose stop
```

### Stop and Remove Container (keeps data)
```bash
docker-compose down
```

### Stop and Remove Container + Data Volume
```bash
docker-compose down -v
```

### View Container Status
```bash
docker-compose ps
```

### Access PostgreSQL CLI
```bash
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles
```

### Run SQL Query from Command Line
```bash
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles -c "SELECT COUNT(*) FROM articles;"
```

## Database Schema

The database is automatically initialized with:

- **articles table** - Stores all collected articles
- **Indexes** - For fast queries on URL, date, source, keywords
- **article_stats view** - Pre-built statistics view
- **Triggers** - Auto-update timestamps

See `scripts/init_db.sql` for the complete schema.

## Data Persistence

Data is stored in a Docker volume named `postgres_data`. This means:
- Data persists even if you stop/remove the container
- Data is stored on your local machine
- To completely remove data, use: `docker-compose down -v`

## Troubleshooting

### Container won't start
```bash
# Check if port 5432 is already in use
netstat -an | findstr 5432  # Windows
lsof -i :5432  # Mac/Linux

# View error logs
docker-compose logs postgres
```

### Can't connect to database
1. Verify container is running: `docker ps`
2. Check if port is correct: `docker-compose ps`
3. Verify credentials in `.env` file match `docker-compose.yml`

### Reset database
```bash
# Stop and remove container + data
docker-compose down -v

# Start fresh
docker-compose up -d
```

### View database size
```bash
docker exec -it ce49x_postgres psql -U ce49x_user -d ce49x_articles -c "SELECT pg_size_pretty(pg_database_size('ce49x_articles'));"
```

### Backup database
```bash
docker exec ce49x_postgres pg_dump -U ce49x_user ce49x_articles > backup_$(date +%Y%m%d).sql
```

### Restore database
```bash
docker exec -i ce49x_postgres psql -U ce49x_user ce49x_articles < backup_20241201.sql
```

## Next Steps

Once the database is running:

1. **Test connection:**
   ```bash
   python scripts/database.py
   ```

2. **Start collecting data:**
   ```bash
   python scripts/newsapi_collector.py
   ```

3. **Check article count:**
   ```bash
   python -c "from scripts.database import DatabaseManager; db = DatabaseManager(); db.connect(); print(f'Articles: {db.get_article_count()}')"
   ```

## Using pgAdmin (Optional GUI)

If you prefer a GUI to view your database:

1. Add to `docker-compose.yml`:
```yaml
  pgadmin:
    image: dpage/pgadmin4
    container_name: ce49x_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres
```

2. Access at: http://localhost:5050
3. Add server:
   - Host: postgres (container name)
   - Port: 5432
   - Database: ce49x_articles
   - Username: ce49x_user
   - Password: ce49x_password


