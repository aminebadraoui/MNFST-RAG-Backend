# Database Documentation

Complete documentation for the MNFST-RAG database system, including schema, setup, configuration, and troubleshooting.

## 📚 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Database Architecture](#database-architecture)
- [Multi-Tenancy](#multi-tenancy)
- [Tools and Scripts](#tools-and-scripts)

## Overview

The MNFST-RAG system uses PostgreSQL as its primary database with the following key characteristics:

- **Database Engine**: PostgreSQL 15+ with pgvector extension
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Migration System**: Alembic
- **Multi-Tenancy**: Row-Level Security (RLS) with tenant isolation
- **Hosting**: Supabase (recommended) or self-hosted PostgreSQL

## Quick Start

### 1. Set Database URL

```bash
# Development
export DATABASE_URL="postgresql://postgres:password@localhost:5432/mnfst_rag"

# Production (Supabase)
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres"
```

### 2. Initialize Database

```bash
# Using the setup script (recommended)
./scripts/db.sh setup

# Or using Python directly
python scripts/setup_database.py setup
```

### 3. Start Application

```bash
uvicorn app.main:app --reload
```

The database will be automatically initialized with the required tables and seed data.

## Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| [Database Schema](./schema.md) | Complete database schema, tables, and relationships |
| [Setup Guide](./setup.md) | Database initialization, migration, and seeding |
| [Configuration](./configuration.md) | Database configuration, connection pooling, and environment setup |
| [Troubleshooting](./troubleshooting.md) | Common issues and solutions |
| [Migrations](./migrations.md) | Database migration management with Alembic |

### Related Documentation

| Document | Location |
|----------|----------|
| [System Architecture](../architecture/system-architecture.md) | Overall system architecture |
| [Multi-Tenant Design](../architecture/multi-tenant-design.md) | Multi-tenancy implementation details |
| [Production Deployment](../deployment/production.md) | Production deployment guide |
| [API Documentation](../api/overview.md) | API endpoints and usage |

## Database Architecture

### Multi-Tenant Design

The database implements a shared database, shared schema approach with tenant isolation through:

1. **Tenant Scoping**: All tenant-specific tables include `tenant_id`
2. **Row-Level Security**: PostgreSQL RLS policies enforce data isolation
3. **Application Context**: Tenant context set per request
4. **Role-Based Access**: Three-tier role system (superadmin, tenant_admin, user)

### Core Tables

```mermaid
erDiagram
    tenants ||--o{ users : "has"
    tenants ||--o{ documents : "owns"
    tenants ||--o{ social_links : "has"
    users ||--o{ documents : "uploads"
    users ||--o{ sessions : "creates"
    sessions ||--o{ messages : "contains"
    
    tenants {
        uuid id PK
        string name
        string slug
        timestamp created_at
        timestamp updated_at
    }
    
    users {
        uuid id PK
        string email
        string name
        enum role
        uuid tenant_id FK
        timestamp last_login
        timestamp created_at
        timestamp updated_at
    }
    
    documents {
        uuid id PK
        string filename
        string original_name
        int size
        string mime_type
        enum status
        timestamp processed_at
        string error
        uuid tenant_id FK
        uuid user_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    social_links {
        uuid id PK
        string url
        enum platform
        uuid tenant_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    sessions {
        uuid id PK
        string title
        uuid user_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    messages {
        uuid id PK
        uuid session_id FK
        string content
        enum role
        timestamp timestamp
        timestamp created_at
        timestamp updated_at
    }
```

## Multi-Tenancy

### Data Isolation Strategy

The system ensures complete data isolation between tenants through:

1. **Database Level**: PostgreSQL RLS policies
2. **Application Level**: Tenant context filtering
3. **API Level**: JWT-based tenant identification

### Row-Level Security

```sql
-- Example RLS policy for documents
CREATE POLICY tenant_isolation_documents ON documents
    FOR ALL TO authenticated
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### Tenant Context

Each request sets the tenant context in the database session:

```python
# Set tenant context for RLS
await set_database_context('app.current_tenant_id', tenant_id)
```

## Tools and Scripts

### Database Management Scripts

| Script | Purpose |
|--------|---------|
| `scripts/db.sh` | All-in-one database management CLI |
| `scripts/setup_database.py` | Python database setup utility |
| `test_db_connection.py` | Database connection testing |
| `debug_env.py` | Environment variable debugging |

### Common Commands

```bash
# Setup database (migrations + seeding)
./scripts/db.sh setup

# Run migrations only
./scripts/db.sh migrate

# Seed data only
./scripts/db.sh seed

# Check status
./scripts/db.sh status

# Create backup
./scripts/db.sh backup my_backup.sql

# Create new migration
./scripts/db.sh migration "Add new field to users table"
```

## Environment Variables

### Required Variables

```env
# Database Connection
DATABASE_URL=postgresql://user:password@host:port/database

# Optional: Database Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### Supabase Configuration

```env
# Supabase Direct Connection
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Supabase Pooler (Production)
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.co:5432/postgres
```

## Performance Considerations

### Indexing Strategy

- Primary key indexes on all tables
- Foreign key indexes for joins
- Tenant-based indexes for multi-tenancy
- Unique constraints for data integrity

### Connection Pooling

- Application-level connection pooling
- Configurable pool sizes
- Connection timeout management
- Health check implementation

### Query Optimization

- Tenant-scoped queries
- Pagination for large result sets
- Efficient join strategies
- Query plan analysis

## Security Considerations

### Data Protection

- Row-Level Security for tenant isolation
- Role-based access control
- Encrypted connections (SSL/TLS)
- Password hashing with bcrypt

### Access Control

- JWT-based authentication
- Three-tier role system
- API endpoint protection
- Database user permissions

## Monitoring and Maintenance

### Health Checks

```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check connection count
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor slow queries
psql $DATABASE_URL -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Backup Strategy

- Regular automated backups
- Point-in-time recovery
- Migration backups
- Disaster recovery planning

## Getting Help

### Common Issues

1. **Connection Problems**: Check [Troubleshooting Guide](./troubleshooting.md)
2. **Migration Failures**: Review [Migration Guide](./migrations.md)
3. **Performance Issues**: See [Configuration Guide](./configuration.md)

### Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Supabase Documentation](https://supabase.com/docs)

---

**Last Updated**: 2025-11-08  
**Version**: 1.0.0  
**Maintainer**: MNFST-RAG Team