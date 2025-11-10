# Database Migrations Guide

Comprehensive guide to managing database schema changes with Alembic in MNFST-RAG.

## 🔄 Overview

The migration system provides:
- **Version-controlled schema changes** with Alembic
- **Automatic migration detection** and application
- **Rollback capabilities** for failed changes
- **Branch support** for parallel development
- **Production-safe** deployment procedures

## 📁 Migration Structure

```
migrations/
├── versions/                    # Migration files
│   ├── 001_initial_migration.py
│   ├── 002_add_rls_policies.py
│   ├── 003_add_indexes.py
│   └── ...
├── env.py                      # Migration environment setup
├── script.py.mako              # Migration template
├── README                      # Migration instructions
└── alembic.ini                # Alembic configuration
```

### Migration Files

Each migration file contains:
- **Revision ID** - Unique identifier
- **Dependencies** - Previous revisions
- **Upgrade function** - Apply changes
- **Downgrade function** - Revert changes

```python
"""Add user preferences table

Revision ID: 004_add_user_preferences
Revises: 003_add_indexes
Create Date: 2024-11-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004_add_user_preferences'
down_revision = '003_add_indexes'
branch_labels = None
depends_on = None

def upgrade():
    """Add user preferences table"""
    op.create_table('user_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.Column('timezone', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])

def downgrade():
    """Remove user preferences table"""
    op.drop_index('idx_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences')
```

## 🛠️ Migration Commands

### Basic Operations

```bash
# Create new migration
./scripts/db.sh migration "Add new field to users table"

# Apply all pending migrations
./scripts/db.sh migrate

# Apply specific migration
./scripts/db.sh upgrade 004_add_user_preferences

# Rollback to previous migration
./scripts/db.sh downgrade

# Rollback to specific migration
./scripts/db.sh downgrade 003_add_indexes

# Check current status
./scripts/db.sh status

# Show migration history
./scripts/db.sh history
```

### Direct Alembic Commands

```bash
# Create new migration (autogenerate)
alembic revision --autogenerate -m "Add audit table"

# Create new migration (manual)
alembic revision -m "Add audit table"

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade 004_add_user_preferences

# Rollback to previous migration
alembic downgrade -1

# Rollback to specific migration
alembic downgrade 003_add_indexes

# Rollback to base (no migrations)
alembic downgrade base

# Show SQL without executing
alembic upgrade head --sql

# Show downgrade SQL
alembic downgrade 004_add_user_preferences --sql

# Dry run (show what would be done)
alembic upgrade head --dry-run

# Stamp current database version (no changes)
alembic stamp head

# Stamp specific version
alembic stamp 003_add_indexes

# Create offline migration
alembic revision --autogenerate -m "Add offline changes" --sql

# Get current revision
alembic current

# Get migration history
alembic history

# Get migration heads
alembic heads

# Show migration details
alembic show 004_add_user_preferences
```

### Script vs Direct Alembic Commands

#### Using Scripts (Recommended)
```bash
# Scripts provide additional safety features
./scripts/db.sh migration "Add new field"      # Includes backup
./scripts/db.sh migrate                         # Includes validation
./scripts/db.sh downgrade                       # Includes confirmation
```

#### Using Alembic Directly
```bash
# Direct Alembic commands for advanced usage
alembic revision --autogenerate -m "Add field"  # More control
alembic upgrade head                           # Direct execution
alembic downgrade previous                      # Direct rollback
```

## 📝 Creating Migrations

### Auto-Generated Migrations

For most schema changes, use autogenerate:

```bash
# 1. Make model changes in app/models/
# 2. Generate migration
./scripts/db.sh migration "Add user preferences table"

# 3. Review generated migration
cat migrations/versions/004_add_user_preferences.py

# 4. Apply migration
./scripts/db.sh migrate
```

### Manual Migrations

For complex changes, write migrations manually:

```python
"""Add audit trail functionality

Revision ID: 005_add_audit_trail
Revises: 004_add_user_preferences
Create Date: 2024-11-08 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    """Add audit trail tables and triggers"""
    
    # Create audit table
    op.create_table('audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('operation', sa.String(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=True),
        sa.Column('old_values', postgresql.JSONB(), nullable=True),
        sa.Column('new_values', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_audit_logs_table_timestamp', 'audit_logs', ['table_name', 'timestamp'])
    op.create_index('idx_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    
    # Create audit trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_trigger_function()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO audit_logs (
                table_name, operation, user_id, tenant_id, 
                old_values, new_values, timestamp
            ) VALUES (
                TG_TABLE_NAME, TG_OP, 
                current_setting('app.current_user_id', true)::uuid,
                current_setting('app.current_tenant_id', true)::uuid,
                CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
                CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END,
                NOW()
            );
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)
    
    # Create triggers for audited tables
    for table in ['users', 'documents', 'sessions']:
        op.execute(f"""
            CREATE TRIGGER audit_{table}_trigger
                AFTER INSERT OR UPDATE OR DELETE ON {table}
                FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
        """)

def downgrade():
    """Remove audit trail functionality"""
    
    # Drop triggers
    for table in ['users', 'documents', 'sessions']:
        op.execute(f"DROP TRIGGER IF EXISTS audit_{table}_trigger ON {table}")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS audit_trigger_function()")
    
    # Drop indexes
    op.drop_index('idx_audit_logs_user_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_logs_table_timestamp', table_name='audit_logs')
    
    # Drop table
    op.drop_table('audit_logs')
```

### Data Migrations

For migrating data, use batch operations:

```python
"""Migrate user roles to new format

Revision ID: 006_migrate_user_roles
Revises: 005_add_audit_trail
Create Date: 2024-11-08 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

def upgrade():
    """Migrate user roles to new enum format"""
    
    # Add new role column
    op.add_column('users', sa.Column('role_new', sa.Enum('superadmin', 'tenant_admin', 'user', name='user_role_new')))
    
    # Migrate data in batches
    connection = op.get_bind()
    
    # Process in batches of 1000
    offset = 0
    batch_size = 1000
    
    while True:
        result = connection.execute(text("""
            UPDATE users 
            SET role_new = CASE 
                WHEN role = 'admin' THEN 'tenant_admin'
                WHEN role = 'client' THEN 'user'
                ELSE role 
            END
            WHERE id IN (
                SELECT id FROM users 
                ORDER BY id 
                LIMIT :batch_size OFFSET :offset
            )
            AND role_new IS NULL
        """), {'batch_size': batch_size, 'offset': offset})
        
        if result.rowcount == 0:
            break
            
        offset += batch_size
        print(f"Migrated {result.rowcount} users, offset: {offset}")
    
    # Drop old column and rename new one
    op.drop_column('users', 'role')
    op.alter_column('users', 'role_new', new_column_name='role')

def downgrade():
    """Revert user role migration"""
    
    # Add old role column
    op.add_column('users', sa.Column('role_old', sa.String()))
    
    # Migrate data back
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE users 
        SET role_old = CASE 
            WHEN role = 'tenant_admin' THEN 'admin'
            WHEN role = 'user' THEN 'client'
            ELSE role 
        END
    """))
    
    # Drop new column and rename old one
    op.drop_column('users', 'role')
    op.alter_column('users', 'role_old', new_column_name='role')
```

## 🌿 Branch Migrations

### Feature Branch Development

When working on feature branches:

```bash
# 1. Create feature branch
git checkout -b feature/add-user-preferences

# 2. Make changes and create migration
./scripts/db.sh migration "Add user preferences table"

# 3. Apply migration locally
./scripts/db.sh migrate

# 4. Develop and test
# ... development work ...

# 5. Merge to main
git checkout main
git merge feature/add-user-preferences

# 6. Apply migration in main
./scripts/db.sh migrate
```

### Handling Merge Conflicts

When migrations conflict:

```bash
# 1. Identify conflicting migrations
./scripts/db.sh history

# 2. Create merge migration
alembic merge -m "merge user_preferences and audit_trail branches" \
    004_add_user_preferences 005_add_audit_trail

# 3. Review and edit merge migration
# migrations/versions/006_merge_user_preferences_audit_trail.py

# 4. Apply merge migration
./scripts/db.sh migrate
```

### Branch-Specific Migrations

For long-running branches:

```bash
# Create branch label
alembic revision -m "Start feature branch" --branch-label feature_user_preferences

# Create branch-specific migrations
./scripts/db.sh migration "Add user preferences table"

# When merging to main:
alembic merge main feature_user_preferences -m "Merge user preferences feature"
```

## 🚀 Production Deployments

### Safe Deployment Process

```bash
# 1. Backup database
./scripts/db.sh backup pre_deployment_$(date +%Y%m%d_%H%M%S).sql

# 2. Check current status
./scripts/db.sh status

# 3. Review pending migrations
./scripts/db.sh history --verbose

# 4. Test migrations in staging
# (Deploy to staging first)

# 5. Apply production migrations
./scripts/db.sh migrate

# 6. Verify deployment
./scripts/db.sh status

# 7. Run smoke tests
curl -s http://localhost:8000/health
```

### Zero-Downtime Migrations

For production systems requiring zero downtime:

```python
"""Add email verification field (zero downtime)

Revision ID: 007_add_email_verification
Revises: 006_merge_user_preferences_audit_trail
Create Date: 2024-11-08 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add email verification with zero downtime"""
    
    # Phase 1: Add nullable column
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True))
    
    # Phase 2: Backfill data in batches
    connection = op.get_bind()
    
    # Set existing users as verified
    connection.execute(text("""
        UPDATE users 
        SET email_verified = true 
        WHERE email_verified IS NULL
    """))
    
    # Phase 3: Make column non-nullable (requires downtime)
    # This step should be done during a maintenance window
    op.alter_column('users', 'email_verified', nullable=False)

def downgrade():
    """Remove email verification field"""
    op.drop_column('users', 'email_verified')
```

### Rolling Migrations

For large tables, use rolling migrations:

```python
"""Add index to large table (rolling)

Revision ID: 008_add_documents_index
Revises: 007_add_email_verification
Create Date: 2024-11-08 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add index to documents table without locking"""
    
    # Use CONCURRENTLY to avoid locking
    op.execute("""
        CREATE INDEX CONCURRENTLY idx_documents_tenant_status_created 
        ON documents(tenant_id, status, created_at DESC)
    """)

def downgrade():
    """Remove index safely"""
    op.drop_index('idx_documents_tenant_status_created', table_name='documents')
```

## 🔍 Migration Testing

### Local Testing

```bash
# 1. Create test database
createdb mnfst_rag_test

# 2. Set test environment
export DATABASE_URL="postgresql://postgres:password@localhost:5432/mnfst_rag_test"

# 3. Run migrations
./scripts/db.sh setup

# 4. Test application
pytest tests/

# 5. Clean up
dropdb mnfst_rag_test
```

### Migration Validation

```python
# tests/test_migrations.py
import pytest
from alembic.command import upgrade, downgrade
from alembic.config import Config

def test_migration_upgrade_downgrade():
    """Test that migrations can be applied and reverted"""
    
    alembic_cfg = Config("alembic.ini")
    
    # Get current head revision
    with pytest.raises(Exception):
        # Should fail if database is at latest
        upgrade(alembic_cfg, "head")
    
    # Downgrade to base
    downgrade(alembic_cfg, "base")
    
    # Upgrade to head
    upgrade(alembic_cfg, "head")
    
    # Verify database state
    # ... add verification logic ...

def test_migration_data_integrity():
    """Test that migrations preserve data integrity"""
    
    # Create test data
    # ... create test records ...
    
    # Run migration
    upgrade(alembic_cfg, "head")
    
    # Verify data integrity
    # ... check data consistency ...
```

### Performance Testing

```bash
# Test migration performance on large dataset
time ./scripts/db.sh migrate

# Monitor database during migration
watch -n 1 "psql $DATABASE_URL -c 'SELECT count(*) FROM pg_stat_activity WHERE state = \"active\";'"

# Check for long-running queries
psql $DATABASE_URL -c "SELECT query, now() - query_start as duration FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '1 second';"
```

## 🚨 Troubleshooting Migrations

### Common Issues

#### Migration Fails Mid-Execution

```bash
# 1. Identify failed migration
./scripts/db.sh status

# 2. Check error details
tail -f /var/log/postgresql/postgresql.log

# 3. Manual cleanup if needed
psql $DATABASE_URL -c "DROP TABLE IF EXISTS new_table;"

# 4. Mark migration as not applied
alembic stamp <previous_revision>

# 5. Re-run migration
./scripts/db.sh migrate
```

#### Lock Timeout Errors

```sql
-- Check for locks
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

#### Out of Memory Errors

```sql
-- Increase work_mem for migration
SET LOCAL work_mem = '256MB';

-- Run migration in smaller batches
-- Modify migration to process in chunks
```

### Recovery Procedures

#### Complete Migration Reset

```bash
# 1. Backup current database
./scripts/db.sh backup emergency_backup.sql

# 2. Reset to base (WARNING: Deletes data)
./scripts/db.sh downgrade base

# 3. Re-apply all migrations
./scripts/db.sh migrate

# 4. Restore seed data if needed
./scripts/db.sh seed
```

#### Selective Migration Rollback

```bash
# 1. Identify problematic migration
./scripts/db.sh history

# 2. Rollback to specific revision
./scripts/db.sh downgrade 005_add_audit_trail

# 3. Fix migration file
# Edit migration file to fix issues

# 4. Re-apply fixed migration
./scripts/db.sh upgrade 006_add_audit_trail
```

## 📋 Migration Checklist

### Before Creating Migration

- [ ] Model changes reviewed
- [ ] Backward compatibility considered
- [ ] Data migration plan ready
- [ ] Performance impact assessed
- [ ] Rollback strategy planned

### Before Applying Migration

- [ ] Database backed up
- [ ] Migration tested in staging
- [ ] Downtime scheduled (if needed)
- [ ] Rollback plan verified
- [ ] Team notified

### After Applying Migration

- [ ] Migration status verified
- [ ] Application functionality tested
- [ ] Performance monitored
- [ ] Data integrity checked
- [ ] Documentation updated

---

**Related Documentation**:
- [Database Schema](./schema.md) - Complete schema documentation
- [Setup Guide](./setup.md) - Database initialization and setup
- [Configuration](./configuration.md) - Database configuration details

**Migration Files**:
- [`alembic.ini`](../../alembic.ini) - Alembic configuration
- [`migrations/env.py`](../../migrations/env.py) - Migration environment
- [`migrations/versions/`](../../migrations/versions/) - Migration files