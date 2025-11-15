# Database Connection Pool Fixes

## Problem
The application was experiencing frequent "MaxClientsInSessionMode: max clients reached" errors from Supabase, indicating that the database connection pool was being exhausted.

## Root Causes
1. **No connection pool configuration**: The database engine was created with default settings, which didn't properly limit connections
2. **Improper session management**: Services were holding onto database sessions longer than necessary
3. **Global service instance**: The chat service was instantiated globally with a single session that never closed

## Solutions Implemented

### 1. Connection Pool Configuration
Updated `app/database.py` to include proper connection pooling:
- Added `QueuePool` with configurable pool size
- Set `pool_pre_ping=True` to validate connections before use
- Added connection recycling to prevent stale connections
- Configured pool timeout and overflow settings

### 2. Environment Variables
Added new environment variables to `.env.example`:
- `DB_POOL_SIZE`: Number of connections to maintain (default: 5)
- `DB_MAX_OVERFLOW`: Additional connections beyond pool size (default: 10)
- `DB_POOL_TIMEOUT`: Seconds to wait for connection (default: 30)
- `DB_POOL_RECYCLE`: Seconds before recycling connections (default: 3600)
- `DB_ECHO`: Enable SQL logging (default: false)

### 3. Session Management Fixes
- Updated `BaseService` to properly handle session lifecycle
- Modified `get_session()` to ensure sessions are always closed
- Fixed `get_optional_current_user()` to use context manager

### 4. Service Pattern Changes
- Removed global `chat_service` instance
- Created `get_chat_service(session)` factory function
- Updated all API endpoints to inject session dependency

### 5. Monitoring
Added `/health/db-pool` endpoint to monitor:
- Current pool size
- Checked in/out connections
- Overflow connections
- Invalid connections

## Recommended Configuration for Supabase
For Supabase's Session Mode (which has connection limits):

```env
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=2
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_ECHO=false
```

This configuration:
- Maintains 3 base connections
- Allows up to 2 additional connections under load
- Recycles connections every 30 minutes
- Times out after 30 seconds if no connection is available

## Usage Guidelines

### For API Endpoints
Always inject the session dependency:
```python
async def my_endpoint(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    chat_service = get_chat_service(session)
    # Use service...
```

### For Background Tasks
Use context manager:
```python
with next(get_session()) as session:
    chat_service = get_chat_service(session)
    # Use service...
```

### Monitoring Pool Status
Check the pool health endpoint:
```bash
curl http://localhost:8000/health/db-pool
```

## Troubleshooting

### Still Getting Pool Errors?
1. Reduce `DB_POOL_SIZE` to 2-3 for Supabase
2. Check for long-running queries that hold connections
3. Monitor the `/health/db-pool` endpoint regularly
4. Ensure all database operations use proper session management

### Connection Leaks
If you suspect connection leaks:
1. Enable `DB_ECHO=true` to see SQL queries
2. Check for sessions not being closed in error paths
3. Use the pool monitoring endpoint to track usage

## Best Practices
1. Always use dependency injection for sessions in API endpoints
2. Use context managers for background tasks
3. Keep transactions short and focused
4. Monitor pool status regularly in production
5. Adjust pool settings based on your Supabase plan limits