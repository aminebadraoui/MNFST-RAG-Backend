# Database Initialization Guide

This guide explains how database creation and initialization works in the MNFST-RAG backend application, ensuring it's not triggered multiple times and follows best practices for Supabase.

## Overview

The application uses a robust database initialization system that combines:
- **Alembic migrations** for schema version control
- **Idempotent initialization** to prevent multiple executions
- **Database locking** to handle concurrent deployments
- **Seeding system** for initial data setup

## Architecture

```mermaid
graph TD
    A[Application Startup] --> B[Database Service]
    B --> C{Database Available?}
    C -->|No| D[Wait & Retry]
    C -->|Yes| E{Already Initialized?}
    E -->|No| F[Acquire Lock]
    E -->|Yes| G{Needs Migration?}
    F --> H[Run Migrations]
    H --> I[Seed Data]
    G -->|Yes| H
    G -->|No| J[Continue Startup]
    I --> J
    D --> C
    H --> K[Release Lock]
    K --> J
```

## Components

### 1. Database Service (`app/services/database.py`)

Handles database initialization and migration management:

**Key Features:**
- **Idempotent Operations**: Checks if already initialized before running
- **Database Locking**: Uses PostgreSQL advisory locks to prevent concurrent initializations
- **Connection Waiting**: Retries database connection with exponential backoff
- **Migration Status**: Tracks current vs. latest migration versions

**Key Methods:**
- `initialize_database()`: Main initialization method
- `is_database_initialized()`: Checks if tables exist
- `needs_migration()`: Compares current vs. latest migration
- `wait_for_database()`: Waits for database to be available

### 2. Database Seeder (`app/services/seeding.py`)

Handles initial data creation:

**Key Features:**
- **Conditional Seeding**: Only seeds if no users exist
- **Order-Dependent**: Creates data in correct dependency order
- **Idempotent**: Checks for existing data before creating

**Default Data Created:**
- Superadmin user (`admin@mnfst-rag.com` / `admin123`)
- Default tenant (`Default Tenant` / `default`)
- Tenant admin user (`tenant-admin@example.com` / `tenant123`)

### 3. Migration System (`migrations/`)

Alembic-based migration system:

**Files:**
- `alembic.ini`: Alembic configuration
- `migrations/env.py`: Migration environment setup
- `migrations/versions/`: Migration files
- `migrations/script.py.mako`: Migration template

**Initial Migration:**
- `001_initial_migration.py`: Creates all tables with proper indexes

## Usage

### Application Startup

Database initialization happens automatically during application startup in [`app/main.py`](../app/main.py):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MNFST-RAG Backend API")
    
    # Initialize database with migrations
    if not initialize_database_on_startup():
        logger.error("Database initialization failed")
        raise RuntimeError("Failed to initialize database")
    
    # Seed initial data if needed
    if not seed_database_on_startup():
        logger.error("Database seeding failed")
        raise RuntimeError("Failed to seed database")
    
    yield
    logger.info("Application shutdown")
```

### Manual Database Management

#### Python Script

```bash
# Setup database (migrations + seeding)
python scripts/setup_database.py setup

# Setup database (force re-initialization)
python scripts/setup_database.py setup --force

# Run migrations only
python scripts/setup_database.py migrate

# Seed data only
python scripts/setup_database.py seed

# Check status
python scripts/setup_database.py status
```

#### Shell Script (Recommended)

```bash
# Make script executable
chmod +x scripts/db.sh

# Setup database
./scripts/db.sh setup

# Force re-initialization
./scripts/db.sh setup --force

# Run migrations only
./scripts/db.sh migrate

# Seed data only
./scripts/db.sh seed

# Check status
./scripts/db.sh status

# Create new migration
./scripts/db.sh migration "Add new field to users table"

# Upgrade to specific revision
./scripts/db.sh upgrade head

# Create backup
./scripts/db.sh backup my_backup.sql
```

## Deployment Scenarios

### 1. New Deployment

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@your-project.supabase.co:5432/postgres"

# Run initial setup
./scripts/db.sh setup
```

### 2. Application Update

```bash
# Deploy new code
# Application will automatically run migrations on startup

# Or run manually before deployment
./scripts/db.sh migrate
```

### 3. Multiple Instance Deployment

The system handles multiple instances safely:

1. **First Instance**: Acquires database lock, runs migrations
2. **Other Instances**: Wait for lock release, check if migrations completed
3. **All Instances**: Continue startup once migrations are done

## Best Practices

### 1. Environment Configuration

Always set `DATABASE_URL` environment variable:

```bash
# Development
export DATABASE_URL="postgresql://postgres:password@localhost:5432/mnfst_rag"

# Production (Supabase)
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres"
```

### 2. Migration Management

```bash
# Before schema changes
./scripts/db.sh backup pre_migration_backup.sql

# Create migration
./scripts/db.sh migration "Describe your changes"

# Apply migration
./scripts/db.sh migrate

# Verify application works
# If not, rollback: ./scripts/db.sh downgrade previous_revision
```

### 3. Production Deployment

```bash
# 1. Backup current database
./scripts/db.sh backup pre_deployment_backup.sql

# 2. Deploy new code
# 3. Application will auto-migrate on startup

# 4. Verify deployment
./scripts/db.sh status
```

## Troubleshooting

### Migration Conflicts

**Problem**: Migration fails with "Can't locate revision identified by 'head'"

```bash
# Check current status
./scripts/db.sh status

# Reset to base (WARNING: Deletes data)
./scripts/db.sh downgrade base

# Re-apply migrations
./scripts/db.sh migrate
```

### Lock Timeouts

**Problem**: Database lock timeout during deployment

```bash
# Check for stuck locks
psql $DATABASE_URL -c "SELECT * FROM pg_locks WHERE pid NOT IN (SELECT pid FROM pg_stat_activity);"

# Clear stuck locks if needed
# Usually resolves automatically when process dies
```

### Connection Issues

**Problem**: Can't connect to Supabase

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check network connectivity
ping db.your-project.supabase.co

# Verify credentials in Supabase dashboard
```

## Security Considerations

### 1. Password Management

- Change default passwords in production
- Use environment variables for sensitive data
- Consider using Supabase's connection pooling

### 2. Database Access

- Use read-only users for application access where possible
- Implement proper connection limits
- Monitor connection pool usage

### 3. Migration Safety

- Always backup before migrations
- Test migrations in staging first
- Use transactional migrations when possible

## Monitoring

### 1. Migration Status

```bash
# Regular status checks
./scripts/db.sh status

# Monitor migration logs
tail -f logs/application.log | grep migration
```

### 2. Database Health

```bash
# Check connection count
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor slow queries
psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Backup database
        run: |
          ./scripts/db.sh backup "pre_deploy_${{ github.sha }}.sql"
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          
      - name: Deploy application
        # Your deployment steps here
        
      - name: Verify deployment
        run: |
          ./scripts/db.sh status
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Summary

This database initialization system provides:

✅ **Idempotent Operations**: Safe to run multiple times  
✅ **Concurrent Safety**: Handles multiple deployment instances  
✅ **Migration Tracking**: Full version control with Alembic  
✅ **Error Handling**: Comprehensive error recovery  
✅ **Production Ready**: Backup and rollback procedures  
✅ **Easy Management**: Simple CLI tools for operations  

The system ensures your Supabase database is properly initialized without the risk of multiple triggers or data corruption.