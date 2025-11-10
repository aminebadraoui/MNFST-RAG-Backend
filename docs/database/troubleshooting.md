# Database Troubleshooting

Comprehensive guide to diagnosing and resolving common database issues in MNFST-RAG.

## 🔍 Overview

This guide covers:
- **Connection problems** and solutions
- **Migration issues** and recovery
- **Performance bottlenecks** and optimization
- **Security issues** and fixes
- **Data corruption** and recovery procedures

## 🚨 Quick Diagnosis

### Health Check Commands

```bash
# Basic connectivity test
psql $DATABASE_URL -c "SELECT 1;"

# Check database status
./scripts/db.sh status

# Application health check
curl -s http://localhost:8000/health | jq

# Check connection count
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
```

### Common Error Patterns

| Error | Likely Cause | Quick Fix |
|--------|--------------|-----------|
| `FATAL: database "..." does not exist` | Database not created | Create database |
| `FATAL: password authentication failed` | Wrong credentials | Check password |
| `Connection refused` | Database not running | Start PostgreSQL |
| `Connection timeout` | Network issues | Check connectivity |
| `Too many connections` | Connection limit reached | Increase pool size |
| `Tenant or user not found` | Wrong URL format | Fix Supabase URL |

## 🔌 Connection Issues

### Problem: Cannot Connect to Database

#### Symptoms
- Application fails to start
- "Connection refused" errors
- Timeout errors
- Authentication failures

#### Diagnosis Steps

```bash
# 1. Test basic connectivity
ping db.example.com

# 2. Test database connection
psql $DATABASE_URL -c "SELECT 1;"

# 3. Check database is running
pg_isready -h host -p port

# 4. Verify credentials
psql -h host -p port -U user -d database -c "SELECT version();"

# 5. Check environment variables
echo $DATABASE_URL
```

#### Solutions

**Wrong Database URL Format**

```bash
# Check current format
echo $DATABASE_URL

# Fix Supabase URL format
# Wrong: postgresql://user@db.project.supabase.co:5432/db
# Correct: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Network Connectivity Issues**

```bash
# Check DNS resolution
nslookup db.example.com

# Check port accessibility
telnet db.example.com 5432

# Check firewall rules
sudo ufw status
iptables -L
```

**Database Not Running**

```bash
# Start PostgreSQL (Ubuntu/Debian)
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Start PostgreSQL (macOS with Homebrew)
brew services start postgresql

# Check status
sudo systemctl status postgresql
```

### Problem: Connection Pool Exhaustion

#### Symptoms
- "Too many connections" errors
- Application hangs under load
- Slow response times

#### Diagnosis

```sql
-- Check current connections
SELECT 
    state,
    count(*) as connection_count,
    max(now() - query_start) as max_query_time
FROM pg_stat_activity 
WHERE datname = current_database()
GROUP BY state;

-- Check connection limits
SELECT 
    setting as max_connections,
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections
FROM pg_settings 
WHERE name = 'max_connections';
```

#### Solutions

**Increase Connection Pool Size**

```python
# app/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=30,              # Increase from 20
    max_overflow=50,           # Increase from 30
    pool_timeout=60,           # Increase timeout
    pool_recycle=1800          # Recycle more frequently
)
```

**Optimize Application Connections**

```python
# Use connection pooling properly
def get_db_session():
    """Get database session with proper cleanup"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()  # Always close connection
```

**Database-Level Configuration**

```sql
-- Increase max connections
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();

-- Configure connection limits per user
ALTER USER mnfst_app CONNECTION LIMIT 50;
```

## 🔄 Migration Issues

### Problem: Migration Fails

#### Symptoms
- Migration script errors
- Schema mismatch errors
- "Can't locate revision" errors
- Constraint violations

#### Diagnosis

```bash
# Check current migration status
./scripts/db.sh status

# Check Alembic history
alembic history

# Check current revision
alembic current

# Check for failed migrations
alembic show head
```

#### Solutions

**Migration Conflicts**

```bash
# 1. Backup current database
./scripts/db.sh backup pre_migration_fix.sql

# 2. Identify conflicting migration
alembic heads

# 3. Mark migration as applied (if manually fixed)
alembic stamp head

# 4. Or rollback to previous version
alembic downgrade previous

# 5. Re-run migration
./scripts/db.sh migrate
```

**Schema Mismatch**

```bash
# 1. Check what Alembic thinks exists
alembic upgrade head --sql

# 2. Check what actually exists
psql $DATABASE_URL -c "\dt"

# 3. Manually fix schema if needed
psql $DATABASE_URL -c "ALTER TABLE users ADD COLUMN IF NOT EXISTS new_column VARCHAR(255);"

# 4. Mark migration as complete
alembic stamp head
```

**Constraint Violations**

```sql
-- Identify constraint violations
SELECT 
    conname as constraint_name,
    conrelid::regclass as table_name,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE convalidated = false;

-- Fix data issues
UPDATE users SET email = 'temp_' || id WHERE email IS NULL;
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
```

### Problem: Lost Migration History

#### Symptoms
- Alembic thinks database is at wrong revision
- Can't apply new migrations
- "Can't locate revision" errors

#### Solutions

**Rebuild Migration History**

```bash
# 1. Backup database
./scripts/db.sh backup before_history_rebuild.sql

# 2. Drop Alembic version table
psql $DATABASE_URL -c "DROP TABLE IF EXISTS alembic_version;"

# 3. Mark current state as head
alembic stamp head

# 4. Verify status
./scripts/db.sh status
```

**Manual Revision Marking**

```bash
# Mark specific revision as current
alembic stamp <revision_id>

# Mark as base (no migrations)
alembic stamp base
```

## ⚡ Performance Issues

### Problem: Slow Queries

#### Symptoms
- API response times > 5 seconds
- Database CPU usage high
- Timeouts during peak load

#### Diagnosis

```sql
-- Enable query statistics if not already
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE mean_time > 1000  -- queries taking more than 1 second
ORDER BY mean_time DESC
LIMIT 10;

-- Check for missing indexes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
  AND n_distinct > 100
  AND tablename NOT IN (
    SELECT DISTINCT tablename 
    FROM pg_indexes 
    WHERE schemaname = 'public'
);
```

#### Solutions

**Add Missing Indexes**

```sql
-- Index for tenant-specific queries
CREATE INDEX CONCURRENTLY idx_users_tenant_email ON users(tenant_id, email);
CREATE INDEX CONCURRENTLY idx_documents_tenant_status ON documents(tenant_id, status);

-- Index for foreign keys
CREATE INDEX CONCURRENTLY idx_documents_user_id ON documents(user_id);
CREATE INDEX CONCURRENTLY idx_messages_session_id ON messages(session_id);

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_documents_tenant_user_created ON documents(tenant_id, user_id, created_at DESC);
```

**Optimize Query Patterns**

```python
# Bad: N+1 query problem
def get_users_with_documents_bad(tenant_id: UUID, db: Session):
    users = db.exec(select(User).where(User.tenant_id == tenant_id)).all()
    for user in users:
        user.documents = db.exec(select(Document).where(Document.user_id == user.id)).all()
    return users

# Good: Use joins
def get_users_with_documents_good(tenant_id: UUID, db: Session):
    return db.exec(
        select(User, Document)
        .join(Document)
        .where(User.tenant_id == tenant_id)
        .order_by(User.created_at.desc())
    ).all()
```

**Database Configuration Tuning**

```sql
-- Memory settings for performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

-- Query planning
ALTER SYSTEM SET random_page_cost = 1.1;  -- For SSD
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Apply changes
SELECT pg_reload_conf();
```

### Problem: High Memory Usage

#### Symptoms
- Database server memory exhaustion
- Out-of-memory errors
- System swapping

#### Diagnosis

```sql
-- Check memory usage by query
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    temp_blks_read + temp_blks_written as temp_blocks
FROM pg_stat_statements
WHERE temp_blocks > 0
ORDER BY temp_blocks DESC;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Solutions

**Reduce Memory Usage**

```sql
-- Lower work_mem for concurrent queries
ALTER SYSTEM SET work_mem = '2MB';

-- Enable memory-efficient sorting
ALTER SYSTEM SET enable_sort = on;
ALTER SYSTEM SET enable_hashagg = on;

-- Configure memory for specific operations
SET LOCAL work_mem = '8MB';  -- For specific session
```

**Optimize Large Tables**

```sql
-- Partition large tables (example for messages)
CREATE TABLE messages_partitioned (
    LIKE messages INCLUDING ALL
) PARTITION BY RANGE (created_at);

CREATE TABLE messages_2024_01 PARTITION OF messages_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## 🔒 Security Issues

### Problem: Authentication Failures

#### Symptoms
- "Password authentication failed" errors
- "Tenant or user not found" (Supabase)
- SSL certificate errors

#### Solutions

**Fix Supabase Connection**

```bash
# 1. Get correct connection string from Supabase dashboard
# Settings > Database > Connection string > URI

# 2. Update .env file with correct format
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# 3. Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**Fix SSL Certificate Issues**

```bash
# 1. Download CA certificate
wget https://storage.googleapis.com/supabase-certs/prod-ca-2021.crt

# 2. Configure SSL
export DB_SSL_MODE=verify-ca
export DB_SSL_CA_PATH=/path/to/prod-ca-2021.crt

# 3. Test with SSL
psql "postgresql://user:pass@host:5432/db?sslmode=verify-ca&sslrootcert=/path/to/ca.crt"
```

**Reset Database User**

```sql
-- Reset password for database user
ALTER USER mnfst_app WITH PASSWORD 'new_secure_password';

-- Grant necessary permissions
GRANT CONNECT ON DATABASE mnfst_rag TO mnfst_app;
GRANT USAGE ON SCHEMA public TO mnfst_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO mnfst_app;
```

### Problem: Row Level Security Issues

#### Symptoms
- Users can't see their data
- "Permission denied" errors
- Data leakage between tenants

#### Diagnosis

```sql
-- Check RLS policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies 
WHERE schemaname = 'public';

-- Check if RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public';
```

#### Solutions

**Enable RLS on Tables**

```sql
-- Enable RLS on tenant-specific tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
```

**Fix RLS Policies**

```sql
-- Drop existing policies
DROP POLICY IF EXISTS tenant_isolation_users ON users;
DROP POLICY IF EXISTS tenant_isolation_documents ON documents;

-- Create correct policies
CREATE POLICY tenant_isolation_users ON users
    FOR ALL TO authenticated
    USING (
        tenant_id = current_setting('app.current_tenant_id')::uuid 
        OR current_setting('app.user_role') = 'superadmin'
    );

CREATE POLICY tenant_isolation_documents ON documents
    FOR ALL TO authenticated
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

**Set Application Context**

```python
# Ensure context is set for each request
async def set_database_context(tenant_id: UUID, user_id: UUID, role: str):
    """Set database context for RLS"""
    await db.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)}
    )
    await db.execute(
        text("SELECT set_config('app.current_user_id', :user_id, true)"),
        {"user_id": str(user_id)}
    )
    await db.execute(
        text("SELECT set_config('app.user_role', :role, true)"),
        {"role": role}
    )
```

## 💾 Data Corruption Issues

### Problem: Data Inconsistency

#### Symptoms
- Foreign key constraint violations
- Duplicate data
- Missing related records

#### Diagnosis

```sql
-- Check for orphaned records
SELECT 'documents with missing users' as issue, count(*) as count
FROM documents d 
LEFT JOIN users u ON d.user_id = u.id 
WHERE u.id IS NULL

UNION ALL

SELECT 'documents with missing tenants' as issue, count(*) as count
FROM documents d 
LEFT JOIN tenants t ON d.tenant_id = t.id 
WHERE t.id IS NULL;

-- Check for duplicates
SELECT email, count(*) as duplicate_count
FROM users 
GROUP BY email 
HAVING count(*) > 1;
```

#### Solutions

**Fix Orphaned Records**

```sql
-- Delete orphaned documents
DELETE FROM documents 
WHERE user_id NOT IN (SELECT id FROM users)
   OR tenant_id NOT IN (SELECT id FROM tenants);

-- Fix duplicate emails
DELETE FROM users 
WHERE id NOT IN (
    SELECT min(id) 
    FROM users 
    GROUP BY email, tenant_id
);
```

**Restore from Backup**

```bash
# 1. Stop application
sudo systemctl stop mnfst-rag

# 2. Create backup of current state
./scripts/db.sh backup before_restore.sql

# 3. Restore from backup
./scripts/db.sh restore backup_20241108_120000.sql

# 4. Run migrations to catch up
./scripts/db.sh migrate

# 5. Start application
sudo systemctl start mnfst-rag
```

## 🔧 Recovery Procedures

### Complete Database Recovery

```bash
# 1. Assess damage
./scripts/db.sh status
./scripts/db.sh backup emergency_backup.sql

# 2. Stop all applications
sudo systemctl stop mnfst-rag

# 3. Restore from latest good backup
./scripts/db.sh restore latest_good_backup.sql

# 4. Verify data integrity
./scripts/db.sh verify

# 5. Apply any missing migrations
./scripts/db.sh migrate

# 6. Restart applications
sudo systemctl start mnfst-rag
```

### Point-in-Time Recovery

```bash
# 1. Identify corruption time
grep "ERROR" /var/log/postgresql/postgresql.log | tail -20

# 2. Restore to point before corruption
pg_basebackup -h localhost -D /var/lib/postgresql/restore -U replication -v -P -W

# 3. Configure recovery
echo "restore_command = 'cp /var/lib/postgresql/archive/%f %p'" >> /var/lib/postgresql/restore/recovery.conf
echo "recovery_target_time = '2024-11-08 12:00:00'" >> /var/lib/postgresql/restore/recovery.conf

# 4. Start recovery
pg_ctl -D /var/lib/postgresql/restore start
```

## 📊 Monitoring and Alerting

### Set Up Monitoring

```bash
# 1. Install monitoring tools
pip install prometheus-client

# 2. Add database metrics to application
# app/metrics.py
from prometheus_client import Counter, Histogram, Gauge

db_connections = Gauge('db_connections_active', 'Active database connections')
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration')
db_errors = Counter('db_errors_total', 'Total database errors')
```

### Alert on Issues

```yaml
# alerts.yml
groups:
  - name: database
    rules:
      - alert: DatabaseDown
        expr: up{job="database"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
          
      - alert: TooManyConnections
        expr: db_connections_active > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Too many database connections"
```

## 📋 Troubleshooting Checklist

### Initial Diagnosis

- [ ] Check application logs
- [ ] Check database logs
- [ ] Test basic connectivity
- [ ] Verify environment variables
- [ ] Check system resources (CPU, memory, disk)

### Connection Issues

- [ ] Database URL format correct
- [ ] Network connectivity verified
- [ ] Database service running
- [ ] Credentials valid
- [ ] SSL certificates valid
- [ ] Connection pool configured

### Performance Issues

- [ ] Slow queries identified
- [ ] Missing indexes added
- [ ] Query patterns optimized
- [ ] Database configuration tuned
- [ ] Memory usage optimized

### Security Issues

- [ ] Authentication working
- [ ] RLS policies enabled
- [ ] SSL/TLS configured
- [ ] User permissions correct
- [ ] Data isolation verified

### Data Issues

- [ ] Backup created before fixes
- [ ] Data integrity verified
- [ ] Orphaned records cleaned
- [ ] Duplicates removed
- [ ] Constraints enforced

---

**Related Documentation**:
- [Database Schema](./schema.md) - Complete schema documentation
- [Setup Guide](./setup.md) - Database initialization and setup
- [Configuration](./configuration.md) - Database configuration details

**Troubleshooting Tools**:
- [`scripts/db.sh`](../../scripts/db.sh) - Database management CLI
- [`test_db_connection.py`](../../test_db_connection.py) - Connection testing
- [`debug_env.py`](../../debug_env.py) - Environment debugging