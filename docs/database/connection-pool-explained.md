# Database Connection Pool Explained

## What is Pool Size?

**No, pool size of 3 does NOT mean only 3 people can use your app at a time.**

The connection pool is about **database connections**, not user connections. Here's how it works:

## Connection Pool vs Users

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User 1       │     │                  │     │                 │
│   User 2       │────▶│  Your FastAPI    │────▶│  Database Pool  │
│   User 3       │     │  Application     │     │  (3 connections)│
│   User 4       │     │                  │     │                 │
│   User 5       │     │                  │     │                 │
│   ...           │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## How It Actually Works

1. **FastAPI handles many concurrent users** (hundreds or thousands)
2. **Database connections are borrowed from the pool** only when needed
3. **Connections are returned to the pool** immediately after the query completes
4. **Same connection can serve many users** over time

## Example Timeline

```
Time 0.0s: User 1 requests data → Borrows Connection #1
Time 0.1s: User 2 requests data → Borrows Connection #2  
Time 0.2s: User 3 requests data → Borrows Connection #3
Time 0.3s: User 1's query completes → Returns Connection #1 to pool
Time 0.3s: User 4 requests data → Borrows Connection #1 (now available)
Time 0.4s: User 2's query completes → Returns Connection #2 to pool
Time 0.4s: User 5 requests data → Borrows Connection #2 (now available)
```

## Why Small Pool Size Works

- **Database queries are fast** (typically 10-100ms)
- **Connections are reused quickly**
- **Most of the time, connections are idle**

## When Pool Size Matters

The pool size becomes limiting when:
1. **Many long-running queries** execute simultaneously
2. **Database is slow** to respond
3. **Transactions are held open** for extended periods

## Overflow Connections

With our configuration:
```env
DB_POOL_SIZE=3        # Base connections always maintained
DB_MAX_OVERFLOW=2      # Additional connections under load
```

- **Normal load**: Up to 3 connections
- **High load**: Up to 5 connections (3 + 2 overflow)
- **Beyond 5**: Requests wait for a connection to be available

## Supabase Session Mode Limits

Supabase's Session Mode has specific limits:
- **Free tier**: 60 connections
- **Pro tier**: 90 connections
- **Team/Enterprise**: Higher limits

Our pool size of 3-5 is **very conservative** compared to these limits.

## Monitoring Your Pool

Check pool usage at: `http://localhost:8000/health/db-pool`

```json
{
  "status": "healthy",
  "pool": {
    "pool_size": 3,
    "checked_in": 3,
    "checked_out": 0,
    "overflow": 0,
    "invalid": 0
  }
}
```

## When to Increase Pool Size

Increase if you consistently see:
- `checked_out` close to `pool_size + max_overflow`
- Users experiencing delays
- Pool timeout errors in logs

## Recommended Settings by Load

```env
# Low traffic (< 100 concurrent users)
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=2

# Medium traffic (100-500 concurrent users)  
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=5

# High traffic (500+ concurrent users)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=10
```

## Summary

- **Pool size ≠ User limit**
- **3 connections can serve hundreds of users**
- **Connections are reused rapidly**
- **Monitor and adjust based on actual usage**