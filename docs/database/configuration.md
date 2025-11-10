# Database Configuration

Complete guide for configuring database connections, pooling, performance tuning, and environment settings.

## 🔧 Overview

Database configuration for MNFST-RAG includes:
- **Connection management** with pooling and timeouts
- **Performance tuning** for optimal query execution
- **Security settings** for data protection
- **Environment-specific** configurations
- **Monitoring and health checks**

## 🌐 Connection Configuration

### Database URL Formats

#### PostgreSQL Standard

```env
# Basic format
DATABASE_URL=postgresql://username:password@host:port/database

# Examples
DATABASE_URL=postgresql://postgres:password@localhost:5432/mnfst_rag
DATABASE_URL=postgresql://mnfst_user:secure_pass@db.example.com:5432/mnfst_prod
```

#### Supabase Connections

```env
# Direct Connection (Development)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Pooler Connection (Production)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres

# Session Pooler (High Concurrency)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.co:6543/postgres
```

#### Connection String Parameters

```env
# With SSL and timeout
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require&connect_timeout=10

# With connection pool settings
DATABASE_URL=postgresql://user:pass@host:5432/db?application_name=mnfst_rag&sslmode=verify-full
```

### Connection Pool Settings

#### SQLAlchemy Configuration

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,              # Number of connections to maintain
    max_overflow=30,           # Additional connections under load
    pool_timeout=30,            # Timeout for getting connection
    pool_recycle=3600,         # Recycle connections every hour
    pool_pre_ping=True,         # Validate connections before use
    echo=False                  # Log all SQL (debug only)
)
```

#### Environment Variables

```env
# Connection Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true

# Connection Timeouts
DB_CONNECT_TIMEOUT=10
DB_COMMAND_TIMEOUT=30
```

#### Async Configuration

```python
# For async operations (FastAPI)
from sqlalchemy.ext.asyncio import create_async_engine

async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

## 🔒 Security Configuration

### SSL/TLS Settings

#### SSL Modes

```env
# SSL Configuration
DB_SSL_MODE=disable          # No SSL (development only)
DB_SSL_MODE=allow           # Try SSL, allow non-SSL
DB_SSL_MODE=prefer          # Prefer SSL, allow non-SSL
DB_SSL_MODE=require         # Require SSL (production minimum)
DB_SSL_MODE=verify-ca       # Verify CA certificate
DB_SSL_MODE=verify-full     # Full verification (most secure)
```

#### Certificate Configuration

```env
# SSL Certificate Paths
DB_SSL_CERT_PATH=/path/to/client-cert.pem
DB_SSL_KEY_PATH=/path/to/client-key.pem
DB_SSL_CA_PATH=/path/to/ca-cert.pem

# Certificate Authority
DB_SSL_ROOT_CERT=/path/to/root-ca.pem
```

#### Connection String with SSL

```env
# SSL in connection string
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem
```

### Authentication Configuration

#### Password Security

```python
# Password hashing configuration
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,        # Higher rounds = more secure but slower
    bcrypt__ident="2b"        # bcrypt version
)
```

#### JWT Configuration

```env
# JWT Settings
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## ⚡ Performance Configuration

### PostgreSQL Server Settings

#### Memory Configuration

```sql
-- postgresql.conf
# Memory Settings
shared_buffers = 256MB              -- 25% of RAM
effective_cache_size = 1GB           -- 75% of RAM
work_mem = 4MB                      -- Per query memory
maintenance_work_mem = 64MB           -- Maintenance operations
checkpoint_completion_target = 0.9     -- Checkpoint tuning
```

#### Connection Settings

```sql
-- Connection Limits
max_connections = 100                 -- Maximum concurrent connections
superuser_reserved_connections = 3      -- Reserve for superusers
shared_preload_libraries = 'pg_stat_statements'  -- Load monitoring
```

#### Query Performance

```sql
-- Query Planning
random_page_cost = 1.1               -- SSD optimization
effective_io_concurrency = 200        -- Concurrent I/O operations
default_statistics_target = 100         -- Statistics accuracy
```

### Application-Level Optimization

#### Query Optimization

```python
# Efficient tenant queries
def get_tenant_documents(tenant_id: UUID, db: Session):
    """Optimized tenant document query"""
    return db.exec(
        select(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .limit(50)  # Pagination
    ).all()

# Use indexes effectively
def search_documents(tenant_id: UUID, query: str, db: Session):
    """Full-text search with indexes"""
    return db.exec(
        select(Document)
        .where(
            and_(
                Document.tenant_id == tenant_id,
                Document.original_name.ilike(f"%{query}%")
            )
        )
        .limit(20)
    ).all()
```

#### Batch Operations

```python
# Bulk insert for performance
def create_documents_bulk(documents: List[DocumentCreate], db: Session):
    """Bulk insert documents"""
    db_objects = [Document(**doc.dict()) for doc in documents]
    db.bulk_insert_mappings(Document, db_objects)
    db.commit()

# Batch updates
def update_documents_status(document_ids: List[UUID], status: str, db: Session):
    """Batch update document status"""
    db.execute(
        update(Document)
        .where(Document.id.in_(document_ids))
        .values(status=status)
    )
    db.commit()
```

### Index Strategy

#### Performance Indexes

```sql
-- Tenant-specific queries
CREATE INDEX CONCURRENTLY idx_users_tenant_email ON users(tenant_id, email);
CREATE INDEX CONCURRENTLY idx_documents_tenant_status ON documents(tenant_id, status);
CREATE INDEX CONCURRENTLY idx_sessions_user_updated ON sessions(user_id, updated_at DESC);

-- Full-text search
CREATE INDEX CONCURRENTLY idx_messages_content_fts ON messages USING gin(to_tsvector('english', content));
CREATE INDEX CONCURRENTLY idx_documents_name_fts ON documents USING gin(to_tsvector('english', original_name));

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_documents_tenant_user_created ON documents(tenant_id, user_id, created_at DESC);
```

#### Index Maintenance

```sql
-- Analyze table statistics
ANALYZE users;
ANALYZE documents;
ANALYZE sessions;
ANALYZE messages;

-- Rebuild fragmented indexes
REINDEX INDEX CONCURRENTLY idx_users_tenant_email;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## 🌍 Environment-Specific Configuration

### Development Environment

```env
# .env.development
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/mnfst_rag_dev
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Security
JWT_SECRET_KEY=dev-secret-key-not-for-production
DB_SSL_MODE=disable

# Logging
LOG_LEVEL=DEBUG
SQL_ECHO=true

# Performance
DB_POOL_RECYCLE=1800
```

### Staging Environment

```env
# .env.staging
# Database
DATABASE_URL=postgresql://mnfst_user:staging_pass@staging-db.example.com:5432/mnfst_rag_staging
DB_POOL_SIZE=15
DB_MAX_OVERFLOW=20

# Security
JWT_SECRET_KEY=staging-secret-key-change-in-production
DB_SSL_MODE=require

# Logging
LOG_LEVEL=INFO
SQL_ECHO=false

# Performance
DB_POOL_RECYCLE=3600
```

### Production Environment

```env
# .env.production
# Database
DATABASE_URL=postgresql://mnfst_user:secure_pass@prod-db.example.com:5432/mnfst_rag_prod
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Security
JWT_SECRET_KEY=${JWT_SECRET_KEY_FROM_VAULT}
DB_SSL_MODE=verify-full
DB_SSL_CA_PATH=/etc/ssl/certs/ca-cert.pem

# Logging
LOG_LEVEL=WARNING
SQL_ECHO=false

# Performance
DB_CONNECT_TIMEOUT=10
DB_COMMAND_TIMEOUT=30
```

## 🔍 Monitoring Configuration

### Health Checks

#### Database Health Endpoint

```python
# app/health.py
from sqlalchemy import text
from fastapi import HTTPException

async def check_database_health():
    """Check database connectivity and performance"""
    try:
        # Test basic connectivity
        result = await db.execute(text("SELECT 1"))
        
        # Check connection pool
        pool_status = engine.pool.status()
        
        # Check slow queries
        slow_queries = await db.execute(text("""
            SELECT count(*) 
            FROM pg_stat_statements 
            WHERE mean_time > 1000
        """))
        
        return {
            "status": "healthy",
            "connections": pool_status,
            "slow_queries": slow_queries.scalar()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unhealthy: {str(e)}")
```

#### Connection Monitoring

```sql
-- Monitor active connections
SELECT 
    state,
    count(*) as connection_count,
    max(now() - query_start) as max_query_time
FROM pg_stat_activity 
WHERE datname = current_database()
GROUP BY state;

-- Monitor connection pool usage
SELECT 
    pool_size,
    active_connections,
    idle_connections,
    waiting_connections
FROM (
    SELECT 
        (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as pool_size,
        count(*) FILTER (WHERE state = 'active') as active_connections,
        count(*) FILTER (WHERE state = 'idle') as idle_connections,
        count(*) FILTER (WHERE wait_event IS NOT NULL) as waiting_connections
    FROM pg_stat_activity
    WHERE datname = current_database()
) pool_stats;
```

### Performance Monitoring

#### Query Performance

```sql
-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Monitor slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE mean_time > 100  -- queries taking more than 100ms
ORDER BY mean_time DESC
LIMIT 10;

-- Monitor table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Application Metrics

```python
# app/middleware/database_monitoring.py
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.5:  # Log slow queries
        logger.warning(f"Slow query: {total:.3f}s - {statement[:100]}")
```

## 🛠️ Configuration Management

### Pydantic Settings

```python
# app/config.py
from pydantic import BaseSettings, Field, validator
from typing import Optional

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # Connection
    database_url: str = Field(..., description="Database connection URL")
    
    # Pool Settings
    db_pool_size: int = Field(20, description="Database pool size")
    db_max_overflow: int = Field(30, description="Maximum overflow connections")
    db_pool_timeout: int = Field(30, description="Pool timeout in seconds")
    db_pool_recycle: int = Field(3600, description="Connection recycle time")
    
    # SSL Settings
    db_ssl_mode: str = Field("require", description="SSL mode")
    db_ssl_cert_path: Optional[str] = Field(None, description="SSL certificate path")
    
    # Performance
    db_connect_timeout: int = Field(10, description="Connection timeout")
    db_command_timeout: int = Field(30, description="Command timeout")
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(('postgresql://', 'sqlite:///')):
            raise ValueError('Database URL must be PostgreSQL or SQLite')
        return v
    
    @validator('db_ssl_mode')
    def validate_ssl_mode(cls, v):
        """Validate SSL mode"""
        valid_modes = ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']
        if v not in valid_modes:
            raise ValueError(f'SSL mode must be one of: {valid_modes}')
        return v
    
    class Config:
        env_prefix = "DB_"
        case_sensitive = False

settings = DatabaseSettings()
```

### Environment-Specific Loading

```python
# app/main.py
import os
from pathlib import Path

def load_environment_config():
    """Load configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    # Load environment file
    env_file = Path(f".env.{env}")
    if env_file.exists():
        load_dotenv(env_file)
    
    # Override with production secrets
    if env == "production":
        load_production_secrets()

def load_production_secrets():
    """Load production secrets from secure source"""
    # Example: HashiCorp Vault
    import hvac
    client = hvac.Client(url=os.getenv("VAULT_URL"))
    client.auth.approle.login(
        role_id=os.getenv("VAULT_ROLE_ID"),
        secret_id=os.getenv("VAULT_SECRET_ID")
    )
    
    secrets = client.secrets.kv.v2.read_secret("database")
    os.environ["DATABASE_URL"] = secrets["data"]["data"]["url"]
    os.environ["JWT_SECRET_KEY"] = secrets["data"]["data"]["jwt_secret"]
```

## 🔧 Advanced Configuration

### Read Replicas

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Primary database for writes
primary_engine = create_engine(primary_database_url)

# Replica database for reads
replica_engine = create_engine(replica_database_url)

# Session factories
PrimarySession = sessionmaker(bind=primary_engine)
ReplicaSession = sessionmaker(bind=replica_engine)

def get_read_session():
    """Get read-only session from replica"""
    session = ReplicaSession()
    try:
        yield session
    finally:
        session.close()

def get_write_session():
    """Get write session from primary"""
    session = PrimarySession()
    try:
        yield session
    finally:
        session.close()
```

### Connection Failover

```python
# app/database_failover.py
import time
from sqlalchemy.exc import OperationalError

class DatabaseFailover:
    """Database connection with automatic failover"""
    
    def __init__(self, primary_url, replica_urls):
        self.primary_url = primary_url
        self.replica_urls = replica_urls
        self.current_engine = None
        self.is_primary = True
    
    def get_engine(self, read_only=False):
        """Get appropriate database engine"""
        if read_only and not self.is_primary:
            return self.get_replica_engine()
        return self.get_primary_engine()
    
    def get_primary_engine(self):
        """Get primary database engine with retry"""
        try:
            if not self.current_engine:
                self.current_engine = create_engine(self.primary_url)
            return self.current_engine
        except OperationalError:
            return self.failover_to_replica()
    
    def failover_to_replica(self):
        """Failover to replica database"""
        logger.error("Primary database failed, failing over to replica")
        self.is_primary = False
        return self.get_replica_engine()
    
    def get_replica_engine(self):
        """Get replica database engine"""
        for replica_url in self.replica_urls:
            try:
                return create_engine(replica_url)
            except OperationalError:
                logger.warning(f"Replica {replica_url} failed")
                continue
        raise Exception("All database connections failed")
```

## 📋 Configuration Checklist

### Development Setup

- [ ] PostgreSQL installed locally
- [ ] Development database created
- [ ] Environment variables configured
- [ ] Connection pooling configured
- [ ] SSL disabled for local development
- [ ] Debug logging enabled
- [ ] Query logging enabled

### Production Setup

- [ ] Production database provisioned
- [ ] SSL/TLS configured
- [ ] Connection pooling optimized
- [ ] Performance tuning applied
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security policies enforced
- [ ] Health checks configured

### Security Configuration

- [ ] SSL mode set to `require` or higher
- [ ] Certificate validation enabled
- [ ] Strong passwords used
- [ ] JWT secret key secure
- [ ] Database user permissions limited
- [ ] Row Level Security enabled
- [ ] Connection encryption enforced

---

**Related Documentation**:
- [Database Schema](./schema.md) - Complete schema documentation
- [Setup Guide](./setup.md) - Database initialization and setup
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

**Configuration Files**:
- [`app/config.py`](../../app/config.py) - Application configuration
- [`app/database.py`](../../app/database.py) - Database connection setup
- [`.env.example`](../../.env.example) - Environment template