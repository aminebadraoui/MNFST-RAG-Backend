# Database Reset Guide (SQLModel)

This guide provides step-by-step instructions for completely resetting your database and recreating it through Alembic terminal commands using SQLModel.

## Overview

The process involves:
1. Dropping all existing database tables
2. Removing the existing migration file
3. Creating a new migration through Alembic terminal
4. Applying the new migration to recreate tables

## SQLModel-Specific Notes

This guide is tailored for SQLModel users:
- Uses SQLModel's metadata for autogeneration
- Handles SQLModel's enum types correctly
- Preserves SQLModel's relationship definitions

## Step 1: Drop All Database Tables

### Option A: Using Alembic Downgrade (Recommended)

If your migration is already applied, you can use Alembic to downgrade:

```bash
cd mnfst-rag-backend
alembic downgrade base
```

This will run the downgrade function in your migration, which drops all tables in reverse order.

### Option B: Manual SQL Drop

If Alembic downgrade doesn't work or you prefer manual approach:

```bash
# Connect to your PostgreSQL database
psql postgresql://user:password@localhost:5432/mnfst_rag

# Drop all tables in correct order (respecting foreign key constraints)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS social_links CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;

# Drop enum types if they exist
DROP TYPE IF EXISTS messagerole;
DROP TYPE IF EXISTS socialplatform;
DROP TYPE IF EXISTS documentstatus;
DROP TYPE IF EXISTS userrole;
```

## Step 2: Remove the Existing Migration File

Delete the current migration file:

```bash
rm mnfst-rag-backend/migrations/versions/001_initial_migration.py
```

## Step 3: Reset Alembic Version Table

Clear the Alembic version tracking:

```bash
# Connect to your database
psql postgresql://user:password@localhost:5432/mnfst_rag

# Delete the alembic version record
DELETE FROM alembic_version;
```

## Step 4: Create a New Migration Through Alembic Terminal

Now you can create a fresh migration using Alembic's autogenerate feature:

```bash
cd mnfst-rag-backend

# Generate a new migration based on your models
alembic revision --autogenerate -m "Initial migration"
```

This will:
1. Examine your SQLAlchemy models in `app/models/`
2. Compare with the current database state (empty)
3. Generate a new migration file in `migrations/versions/`

## Step 5: Apply the New Migration

Apply the newly created migration to create all tables:

```bash
alembic upgrade head
```

## Step 6: Verify the Database

Check that all tables were created correctly:

```bash
# Connect to your database
psql postgresql://user:password@localhost:5432/mnfst_rag

# List all tables
\dt

# Check the alembic version
SELECT * FROM alembic_version;
```

## Expected Tables

After successful migration, you should have these tables:

1. `tenants` - Tenant information
2. `users` - User accounts with roles
3. `documents` - Document metadata
4. `social_links` - Social media links
5. `sessions` - Chat sessions
6. `messages` - Chat messages

## Troubleshooting

### Migration Fails with Foreign Key Errors

Ensure tables are dropped in the correct order (child tables before parent tables).

### Alembic Cannot Detect Models

Make sure all model files are imported in `migrations/env.py`. The current file already imports:
- `Tenant`
- `User`
- `Document`
- `SocialLink`
- `Session`
- `Message`

### Database Connection Issues

Verify your database URL is correctly set in:
1. `.env` file (if using environment variables)
2. `alembic.ini` file (line 60)

## Alternative: Using the Setup Script

If you prefer using the project's setup script instead of direct Alembic commands:

```bash
cd mnfst-rag-backend

# Run the setup script (this will handle migrations)
python scripts/setup_database.py setup --force
```

## Notes

- This process is destructive and will delete all data in your database
- Always backup your database before performing these operations
- The models in `app/models/` define the schema that Alembic will use to generate migrations
- After this process, you can continue using Alembic normally for future schema changes