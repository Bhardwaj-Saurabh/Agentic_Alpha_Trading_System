# Database Setup Guide

This project has been upgraded to use PostgreSQL database instead of CSV storage for production-ready data persistence.

## Prerequisites

- PostgreSQL 12 or higher
- Python packages: `psycopg2` or `psycopg2-binary`

## Quick Setup

### 1. Install PostgreSQL

**Windows:**
```bash
# Download and install from: https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Access PostgreSQL
psql -U postgres

# Create the trading database
CREATE DATABASE trading_db;

# Exit psql
\q
```

### 3. Configure Environment

Add to your `.env` file:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trading_db
```

Replace `your_password` with your PostgreSQL password.

### 4. Install Python Dependencies

```bash
pip install psycopg2-binary
```

Or if you prefer to build from source:
```bash
pip install psycopg2
```

## Database Schema

The application automatically creates the following tables on first run:

### trading_decisions
Stores all agent trading decisions
- `id`: Primary key
- `symbol`: Stock symbol
- `decision`: Trading decision text
- `confidence`: Confidence score (0-1)
- `agent_name`: Name of the agent
- `created_at`: Timestamp

### audit_trail
Stores detailed audit entries for compliance
- `id`: Primary key
- `symbol`: Stock symbol
- `decision_type`: Type of decision (SUPERVISOR, REGULATORY, etc.)
- `action`: Trading action (BUY/SELL/HOLD)
- `confidence`: Confidence score
- `rationale`: Detailed reasoning
- `compliance_status`: Compliance status
- `risk_level`: Risk assessment
- `position_size`: Position sizing info
- `blocked_trades`: Blocked trades info
- `timestamp`: Timestamp

### trading_signals
Stores trading signals
- `id`: Primary key
- `symbol`: Stock symbol
- `signal_type`: Signal type
- `strategy`: Strategy name
- `confidence`: Confidence score
- `timestamp`: Timestamp

### screened_stocks
Stores screened stock information
- `id`: Primary key
- `symbol`: Stock symbol
- `company_name`: Company name
- `current_price`: Current stock price
- `average_volume`: Average volume
- `last_updated`: Last update timestamp

## Verification

After setup, run the application:

```bash
streamlit run app/main.py --server.port 5000 --server.address 0.0.0.0
```

If the connection is successful, you'll see:
- No database connection errors in the console
- All agent decisions are saved to the database
- Audit trail is properly maintained

## Troubleshooting

### Connection Error
```
Database connection failed: ...
```

**Solutions:**
1. Verify PostgreSQL is running:
   ```bash
   # Windows
   pg_isready

   # Linux/macOS
   sudo systemctl status postgresql
   ```

2. Check your DATABASE_URL format
3. Verify database exists:
   ```bash
   psql -U postgres -l
   ```

### Permission Error
```
FATAL: role "postgres" does not exist
```

**Solution:**
Create the postgres user:
```bash
createuser -s postgres
```

### Table Creation Error

If tables aren't created automatically, you can create them manually:

```sql
-- Connect to your database
\c trading_db

-- Run the SQL commands from app/db/database.py create_tables() method
```

## Cloud Deployment

### Heroku
```bash
# Heroku automatically provides DATABASE_URL
heroku config:set DATABASE_URL=postgresql://...
```

### AWS RDS
1. Create a PostgreSQL RDS instance
2. Update .env with your RDS connection string:
   ```
   DATABASE_URL=postgresql://username:password@your-rds-endpoint.rds.amazonaws.com:5432/trading_db
   ```

### Other Cloud Providers
The application works with any PostgreSQL-compatible database including:
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases
- Supabase
- Neon

## Migration from CSV

If you have existing CSV data:

1. The old CSV files are in `data_storage/`
2. The database tables match the CSV structure
3. You can manually import CSV data or let the application create fresh data

## Benefits of Database Over CSV

✅ **ACID Compliance** - Data integrity guaranteed
✅ **Concurrent Access** - Multiple agents can write simultaneously
✅ **Query Performance** - Fast indexed lookups
✅ **Data Relationships** - Foreign keys and constraints
✅ **Scalability** - Handles millions of records
✅ **Audit Trail** - Built-in transaction logging
✅ **Production Ready** - Enterprise-grade reliability

## Support

For database-related issues:
1. Check PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-*.log`
2. Verify connection: `psql -U postgres -d trading_db`
3. Review application logs for database errors

---

**Status:** ✅ Database migration complete!
