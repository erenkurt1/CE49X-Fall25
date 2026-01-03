# Connecting PostgreSQL to pgAdmin

## Current Setup

Your Docker containers are running:
- **PostgreSQL**: `ce49x_postgres` on port `5432`
- **pgAdmin**: `ce49x_pgadmin` on port `5050`

## Database Connection Details

**PostgreSQL Server:**
- **Host**: `postgres` (use this when connecting from pgAdmin container) OR `host.docker.internal` (if connecting from outside Docker)
- **Port**: `5432`
- **Database**: `ce49x_articles`
- **Username**: `ce49x_user`
- **Password**: `ce49x_password`

**pgAdmin Login:**
- **URL**: http://localhost:5050/browser/
- **Email**: `admin@ce49x.com`
- **Password**: `admin`

## Steps to Connect

1. **Open pgAdmin**
   - Go to: http://localhost:5050/browser/
   - Login with:
     - Email: `admin@ce49x.com`
     - Password: `admin`

2. **Add New Server**
   - Right-click on "Servers" in the left panel
   - Select "Register" → "Server..."

3. **General Tab**
   - **Name**: `CE49X Articles Database` (or any name you prefer)

4. **Connection Tab**
   - **Host name/address**: `postgres` (this is the Docker service name - try this first)
     - **Alternatives** (if `postgres` doesn't work):
       - `ce49x_postgres` (container name)
       - `172.18.0.2` (container IP address)
       - `host.docker.internal` (Docker host)
   - **Port**: `5432`
   - **Maintenance database**: `ce49x_articles`
   - **Username**: `ce49x_user`
   - **Password**: `ce49x_password`
   - ✅ **Save password** (check this box)

5. **Click "Save"**

## Troubleshooting

### If connection fails with "postgres" as hostname:

Try these alternatives in order:

1. **Use container name**: `ce49x_postgres`
2. **Use Docker host**: `host.docker.internal`
3. **Use localhost**: `localhost` (if pgAdmin is accessing from host)
4. **Find container IP**:
   ```bash
   docker inspect ce49x_postgres | grep IPAddress
   ```
   Use the IP address shown

### Verify Connection

After connecting, you should see:
- Database: `ce49x_articles`
- Tables: `articles`
- You can browse and query your article data

## Quick Test Query

Once connected, try this query:
```sql
SELECT COUNT(*) as total_articles FROM articles;
```

This should return the total number of articles in your database.

