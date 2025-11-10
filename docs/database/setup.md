# Database Setup Guide

Complete guide for setting up, initializing, and maintaining the MNFST-RAG database.

## 🚀 Overview

The MNFST-RAG database setup system provides:
- **Idempotent initialization** - Safe to run multiple times
- **Concurrent safety** - Handles multiple deployment instances
- **Migration management** - Version-controlled schema changes
- **Data seeding** - Initial data setup
- **Backup and recovery** - Data protection procedures

## 📋 Prerequisites

### Required Software

- **PostgreSQL 15+** with pgvector extension
- **Python 3.11+** with required packages
- **Environment variables** configured

### Database Options

1. **Supabase** (Recommended)
   - Managed PostgreSQL service
   - Built-in connection pooling
   - Automatic backups
   - pgvector extension included

2. **Self-hosted PostgreSQL**
   - Full control over configuration
   - Requires manual setup and maintenance
   - Need to install pgvector extension

## 🔧 Environment Configuration

### Required Environment Variables

```env
# Database Connection (Required)
DATABASE_URL=postgresql://user:password@host:port/database

# Optional: Database Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Optional: SSL Settings
DB_SSL_MODE=require
DB_SSL_CERT_PATH=/path/to/cert.pem
```

### Supabase Configuration

```env
# Direct Connection (Development)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Pooler Connection (Production)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres

# Session Pooler (High Concurrency)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.co:6543/postgres
```

### Self-hosted PostgreSQL

```env
# Local Development
DATABASE_URL=postgresql://postgres:password@localhost:5432/mnfst_rag

# Production
DATABASE_URL=postgresql://mnfst_user:secure_password@db.example.com:5432/mnfst_prod
```

## 🏗️ Setup Process

### Option 1: Automatic Setup (Recommended)

The database initializes automatically when you start the application:

```bash
# 1. Set environment variables
export DATABASE_URL="your_database_url_here"

# 2. Start application
uvicorn app.main:app --reload
```

The application will:
1. Wait for database to be available
2. Check if already initialized
3. Acquire database lock (prevent concurrent initialization)
4. Run migrations if needed
5. Seed initial data
6. Release lock and continue startup

### Option 2: Manual Setup

Use the provided scripts for manual control:

```bash
# Make script executable
chmod +x scripts/db.sh

# Setup database (migrations + seeding)
./scripts/db.sh setup

# Verify setup
./scripts/db.sh status
```

### Option 3: Python Script

For programmatic control:

```bash
# Setup database
python scripts/setup_database.py setup

# Force re-initialization (development only)
python scripts/setup_database.py setup --force

# Run migrations only
python scripts/setup_database.py migrate

# Seed data only
python scripts/setup_database.py seed

# Check status
python scripts/setup_database.py status
```

## 📊 Database Initialization Architecture

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

## 🔄 Migration System

### Migration Files

Migrations are stored in `migrations/versions/` directory:

```
migrations/
├── versions/
│   ├── 001_initial_migration.py
│   ├── 002_add_rls_policies.py
│   └── 003_add_indexes.py
├── env.py
├── script.py.mako
└── README
```

### Creating New Migrations

```bash
# Using shell script
./scripts/db.sh migration "Add new field to users table"

# Using Alembic directly
alembic revision --autogenerate -m "Add new field to users table"
```

### Running Migrations

```bash
# Apply all pending migrations
./scripts/db.sh migrate

# Apply specific migration
./scripts/db.sh upgrade head

# Rollback to previous migration
./scripts/db.sh downgrade previous

# Rollback to specific revision
./scripts/db.sh downgrade 001_initial_migration
```

### Migration Best Practices

1. **Always backup before migrations**
2. **Test migrations in staging first**
3. **Use descriptive migration messages**
4. **Review generated migrations before applying**
5. **Keep migrations reversible when possible**

## 🌱 Data Seeding

### Default Seed Data

The system creates initial data for development:

```python
# Default Superadmin
email: admin@mnfst-rag.com
password: admin123
role: superadmin

# Default Tenant
name: Default Tenant
slug: default

# Default Tenant Admin
email: tenant-admin@example.com
password: tenant123
role: tenant_admin
tenant: Default Tenant
```

### Seeding Process

1. **Check if users exist** - Only seeds if no users found
2. **Create default tenant** - Creates "Default Tenant" if none exists
3. **Create superadmin user** - System-wide administrator
4. **Create tenant admin** - Admin for default tenant
5. **Verify creation** - Confirm all entities created successfully

### Custom Seeding

For custom seed data, modify `app/services/seeding.py`:

```python
async def seed_custom_data():
    """Seed custom data for your application"""
    
    # Create custom tenant
    tenant = Tenant(name="Custom Company", slug="custom-company")
    db.add(tenant)
    db.flush()
    
    # Create custom users
    user = User(
        email="user@custom.com",
        name="Custom User",
        role="user",
        tenant_id=tenant.id
    )
    db.add(user)
    
    db.commit()
```

## 🔒 Security Setup

### Database User Permissions

#### Supabase

Supabase handles user permissions automatically:
- Application user with limited privileges
- Row Level Security for data isolation
- Connection pooling for performance

#### Self-hosted

Create dedicated database user:

```sql
-- Create application user
CREATE USER mnfst_app WITH PASSWORD 'secure_password';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE mnfst_rag TO mnfst_app;
GRANT USAGE ON SCHEMA public TO mnfst_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO mnfst_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO mnfst_app;

-- Enable RLS for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
-- ... enable for all tenant-specific tables
```

### SSL Configuration

#### Enforce SSL Connections

```env
# Require SSL for all connections
DB_SSL_MODE=require

# Verify SSL certificate
DB_SSL_MODE=verify-ca

# Full SSL verification
DB_SSL_MODE=verify-full
```

#### Certificate Configuration

```env
# Custom certificate path
DB_SSL_CERT_PATH=/path/to/client-cert.pem
DB_SSL_KEY_PATH=/path/to/client-key.pem
DB_SSL_CA_PATH=/path/to/ca-cert.pem
```

## 📈 Performance Setup

### Connection Pooling

#### Application Level

```python
# SQLAlchemy connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain
    max_overflow=30,       # Additional connections under load
    pool_timeout=30,       # Timeout for getting connection
    pool_recycle=3600,     # Recycle connections every hour
    pool_pre_ping=True      # Validate connections before use
)
```

#### Database Level

```sql
-- PostgreSQL configuration (postgresql.conf)
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Index Optimization

```sql
-- Create performance indexes
CREATE INDEX CONCURRENTLY idx_users_email_tenant ON users(email, tenant_id);
CREATE INDEX CONCURRENTLY idx_documents_tenant_status ON documents(tenant_id, status);
CREATE INDEX CONCURRENTLY idx_sessions_user_updated ON sessions(user_id, updated_at DESC);

-- Analyze table statistics
ANALYZE users;
ANALYZE documents;
ANALYZE sessions;
```

## 🔧 Maintenance Procedures

### Regular Maintenance

#### Daily Tasks

```bash
# Update table statistics
./scripts/db.sh maintenance analyze

# Check database health
./scripts/db.sh health-check
```

#### Weekly Tasks

```bash
# Create backup
./scripts/db.sh backup "weekly_backup_$(date +%Y%m%d)"

# Clean up old sessions (optional)
./scripts/db.sh cleanup sessions --older-than 30d
```

#### Monthly Tasks

```bash
# Full database vacuum
./scripts/db.sh maintenance vacuum

# Rebuild indexes if needed
./scripts/db.sh maintenance reindex
```

### Backup Strategy

#### Automated Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/var/backups/mnfst-rag"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Upload to cloud storage (optional)
aws s3 cp $BACKUP_FILE.gz s3://mnfst-rag-backups/database/

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
```

#### Point-in-Time Recovery

```bash
# Enable WAL archiving
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'

# Restore to specific time
pg_basebackup -h localhost -D /var/lib/postgresql/restore -U replication -v -P -W
```

## 🚨 Troubleshooting Setup Issues

### Connection Problems

#### Symptom: "Could not connect to database"

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check network connectivity
ping db.example.com

# Verify credentials
psql -h host -p port -U user -d database -c "SELECT 1;"
```

#### Symptom: "Connection timeout"

```bash
# Check database is running
pg_isready -h host -p port

# Increase timeout
export DB_POOL_TIMEOUT=60

# Check connection count
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
```

### Migration Issues

#### Symptom: "Migration failed"

```bash
# Check current migration status
./scripts/db.sh status

# Identify failed migration
alembic current

# Rollback and retry
./scripts/db.sh downgrade previous
./scripts/db.sh migrate

# Force re-initialization (development only)
./scripts/db.sh setup --force
```

#### Symptom: "Can't locate revision"

```bash
# Reset to base (WARNING: Deletes data)
./scripts/db.sh downgrade base

# Re-apply migrations
./scripts/db.sh migrate
```

### Permission Issues

#### Symptom: "Permission denied"

```bash
# Check user permissions
psql $DATABASE_URL -c "\du"

# Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mnfst_app;

# Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'users';
```

## 📋 Setup Checklist

### Pre-Setup Checklist

- [ ] PostgreSQL 15+ installed and running
- [ ] pgvector extension enabled
- [ ] Database created
- [ ] Environment variables configured
- [ ] Network connectivity verified
- [ ] SSL certificates (if required)

### Post-Setup Checklist

- [ ] Database tables created
- [ ] Indexes created
- [ ] RLS policies enabled
- [ ] Seed data created
- [ ] Default users created
- [ ] Application connects successfully
- [ ] Basic functionality tested

### Production Checklist

- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] SSL/TLS enabled
- [ ] Connection pooling configured
- [ ] Performance tuning applied
- [ ] Security policies enforced
- [ ] Disaster recovery plan tested

## 📚 Additional Resources

### Documentation

- [Database Schema](./schema.md) - Complete schema documentation
- [Configuration Guide](./configuration.md) - Database configuration details
- [Troubleshooting Guide](./troubleshooting.md) - Common issues and solutions
- [Migration Guide](./migrations.md) - Advanced migration management

### External Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

**Related Scripts**:
- [`scripts/db.sh`](../../scripts/db.sh) - Database management CLI
- [`scripts/setup_database.py`](../../scripts/setup_database.py) - Python setup utility
- [`test_db_connection.py`](../../test_db_connection.py) - Connection testing

**Service Files**:
- [`app/services/database.py`](../../app/services/database.py) - Database service
- [`app/services/seeding.py`](../../app/services/seeding.py) - Data seeding