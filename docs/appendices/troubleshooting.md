# Troubleshooting Guide

## Overview

This guide covers common issues, debugging techniques, and solutions for problems you might encounter while developing, deploying, or running the MNFST-RAG Backend.

## Quick Diagnosis

### Health Check Commands

```bash
# Check application health
curl http://localhost:8000/health

# Check database connectivity
uv run python -c "from app.database import engine; print(engine.url)"

# Check Redis connectivity
uv run python -c "import redis; r=redis.Redis(); print(r.ping())"

# Check environment variables
env | grep -E "(DATABASE|REDIS|JWT|DEBUG)"
```

### Log Locations

```bash
# Application logs
tail -f logs/app.log

# Database logs
tail -f /var/log/postgresql/postgresql.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Docker logs
docker logs mnfst-rag-backend
docker logs -f mnfst-rag-backend  # Follow logs
```

## Installation Issues

### Python Version Incompatibility

**Problem**: `Python 3.11+ is required`

**Symptoms**:
```
ERROR: Package requires a different Python: 3.11.0 not in '<3.11'
```

**Solutions**:
```bash
# Check current Python version
python --version

# Install Python 3.11+ using pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0

# Or using system package manager
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.11 python3.11-venv

# macOS:
brew install python@3.11
```

### Dependency Installation Failures

**Problem**: `Failed to install dependencies`

**Symptoms**:
```
error: failed to solve: process "/bin/sh -c uv sync" did not complete successfully
```

**Solutions**:
```bash
# Clear uv cache
uv cache clean

# Reinstall dependencies
uv sync --refresh

# Update uv to latest version
pip install --upgrade uv

# Try with different index
uv sync --index-url https://pypi.org/simple/

# If using corporate proxy, configure:
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Virtual Environment Issues

**Problem**: Virtual environment not working

**Symptoms**:
```
Command not found: uvicorn
```

**Solutions**:
```bash
# Recreate virtual environment
rm -rf .venv
uv venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# Verify activation
which python
python --version
```

## Database Issues

### Connection Errors

**Problem**: `Could not connect to database`

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions**:
```bash
# Check database URL format
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL -c "SELECT 1;"

# Check if PostgreSQL is running
sudo systemctl status postgresql
sudo systemctl start postgresql

# For Docker deployment
docker ps | grep postgres
docker logs postgres-container

# Check network connectivity
telnet localhost 5432
nc -zv localhost 5432
```

### Migration Failures

**Problem**: Database migration failed

**Symptoms**:
```
alembic.util.exc.CommandError: Can't locate revision identified by 'head'
```

**Solutions**:
```bash
# Check current migration status
uv run alembic current

# Reset to initial state (WARNING: This will delete data)
uv run alembic downgrade base

# Apply migrations again
uv run alembic upgrade head

# Create new migration if needed
uv run alembic revision --autogenerate -m "Initial migration"

# Check migration history
uv run alembic history
```

### Permission Errors

**Problem**: Database permission denied

**Symptoms**:
```
psql: FATAL: permission denied for database
```

**Solutions**:
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE mnfst_rag;
CREATE USER mnfst_rag_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mnfst_rag TO mnfst_rag_user;
\q

# Update DATABASE_URL
DATABASE_URL=postgresql://mnfst_rag_user:your_password@localhost:5432/mnfst_rag
```

## Authentication Issues

### JWT Token Problems

**Problem**: Invalid or expired tokens

**Symptoms**:
```
{"detail": "Could not validate credentials"}
```

**Solutions**:
```bash
# Check JWT secret key
echo $JWT_SECRET_KEY

# Generate new secret key
openssl rand -hex 32

# Verify token format
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." | cut -d. -f2 | base64 -d

# Test token manually
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/auth/me
```

### CORS Issues

**Problem**: CORS errors in browser

**Symptoms**:
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solutions**:
```bash
# Check allowed origins
echo $ALLOWED_ORIGINS

# Test CORS preflight
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://localhost:8000/api/v1/auth/login

# Update .env file
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## File Upload Issues

### Storage Connection Errors

**Problem**: Cannot connect to Cloudflare R2

**Symptoms**:
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solutions**:
```bash
# Check R2 credentials
echo $R2_ACCESS_KEY_ID
echo $R2_SECRET_ACCESS_KEY

# Test R2 connection
aws s3 ls --endpoint-url https://your-account-id.r2.cloudflarestorage.com

# Configure AWS CLI for R2
aws configure set aws_access_key_id $R2_ACCESS_KEY_ID
aws configure set aws_secret_access_key $R2_SECRET_ACCESS_KEY
aws configure set default.region auto

# Test with curl
curl -H "X-Amz-Date: $(date -u +%Y%m%dT%H%M%SZ)" \
     -H "Authorization: AWS4-HMAC-SHA256 ..." \
     https://your-account-id.r2.cloudflarestorage.com/your-bucket
```

### File Size Limit Errors

**Problem**: File too large

**Symptoms**:
```
413 Request Entity Too Large
```

**Solutions**:
```bash
# Check current limits
grep MAX_FILE_SIZE .env

# Update limits in .env
MAX_FILE_SIZE_MB=100

# For Nginx, update client_max_body_size
# /etc/nginx/nginx.conf
client_max_body_size 100M;

# Restart Nginx
sudo systemctl restart nginx
```

## Performance Issues

### Slow Response Times

**Problem**: API responses are slow

**Diagnosis**:
```bash
# Check response time
time curl http://localhost:8000/health

# Monitor system resources
top
htop
iostat -x 1

# Check database queries
uv run python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10'))
    for row in result:
        print(row)
"
```

**Solutions**:
```bash
# Add database indexes
uv run python -c "
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('CREATE INDEX CONCURRENTLY idx_documents_tenant_id ON documents(tenant_id)'))
    conn.commit()
"

# Optimize database configuration
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Memory Leaks

**Problem**: Memory usage keeps increasing

**Diagnosis**:
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep uvicorn'

# Memory profiling
uv run python -m memory_profiler app/main.py

# Check for memory leaks
uv run python -c "
import tracemalloc
tracemalloc.start()
# Your code here
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
"
```

**Solutions**:
```python
# Fix memory leaks in code
# app/database.py
def get_session() -> Generator[Session, None, None]:
    """Get database session with proper cleanup"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()  # Ensure session is closed
```

## Docker Issues

### Container Won't Start

**Problem**: Docker container fails to start

**Symptoms**:
```
docker: Error response from daemon: Container failed to start
```

**Solutions**:
```bash
# Check container logs
docker logs mnfst-rag-backend

# Run container interactively for debugging
docker run -it --entrypoint /bin/bash mnfst-rag-backend

# Check Dockerfile
# Ensure proper base image and dependencies
# Verify working directory and permissions

# Build with no cache
docker build --no-cache -t mnfst-rag-backend .
```

### Port Conflicts

**Problem**: Port already in use

**Symptoms**:
```
docker: Error response from daemon: driver failed programming external connectivity
```

**Solutions**:
```bash
# Find process using port
lsof -i :8000
netstat -tulpn | grep :8000

# Kill the process
kill -9 <PID>

# Or use different port
docker run -p 8001:8000 mnfst-rag-backend

# Stop conflicting container
docker stop $(docker ps -q --filter "publish=8000")
```

## API Issues

### 422 Validation Errors

**Problem**: Request validation fails

**Symptoms**:
```
{"detail": [{"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}]}
```

**Solutions**:
```bash
# Check request format
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password"}' \
     -v  # Verbose output

# Check API documentation
open http://localhost:8000/docs

# Validate JSON
echo '{"email": "test@example.com"}' | python -m json.tool
```

### 404 Not Found Errors

**Problem**: API endpoints return 404

**Symptoms**:
```
{"detail": "Not Found"}
```

**Solutions**:
```bash
# Check available endpoints
curl http://localhost:8000/docs
curl http://localhost:8000/openapi.json

# Check URL path
curl http://localhost:8000/api/v1/auth/login  # Correct
curl http://localhost:8000/auth/login          # Incorrect

# Check router registration
# app/main.py
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
```

## Development Issues

### Hot Reload Not Working

**Problem**: Code changes not reflected

**Symptoms**:
```
Application doesn't restart after code changes
```

**Solutions**:
```bash
# Check uvicorn command
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ensure running in development mode
export DEBUG=True

# Check file permissions
ls -la app/

# Restart with explicit reload
uv run uvicorn app.main:app --reload-dir=app --reload
```

### Import Errors

**Problem**: Module import failures

**Symptoms**:
```
ModuleNotFoundError: No module named 'app.utils'
```

**Solutions**:
```bash
# Check Python path
uv run python -c "import sys; print(sys.path)"

# Install missing dependencies
uv sync

# Check file structure
find . -name "*.py" | head -10

# Run from correct directory
cd mnfst-rag-backend
uv run python -m app.main
```

## Production Issues

### SSL Certificate Problems

**Problem**: SSL certificate errors

**Symptoms**:
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions**:
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Check certificate chain
openssl s_client -connect api.mnfst-rag.com:443

# Renew certificate (Let's Encrypt)
sudo certbot renew

# Test certificate
curl -v https://api.mnfst-rag.com
```

### High CPU Usage

**Problem**: CPU usage consistently high

**Diagnosis**:
```bash
# Check CPU usage
top
htop

# Check process details
ps aux | grep uvicorn

# Profile application
uv run python -m cProfile -o profile.stats app/main.py
uv run python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

**Solutions**:
```bash
# Scale horizontally
docker-compose up --scale app=3

# Optimize database queries
# Add indexes, optimize joins, use pagination

# Implement caching
# Redis for frequently accessed data
```

## Debugging Techniques

### Logging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add custom logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Debug Mode

```python
# Enable debug mode in FastAPI
app = FastAPI(debug=True)

# Or via environment variable
export DEBUG=True
```

### Interactive Debugging

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use ipdb (better)
import ipdb; ipdb.set_trace()

# For async code
import asyncio
await asyncio.get_event_loop().run_in_executor(None, lambda: pdb.set_trace())
```

### Performance Profiling

```python
# Profile specific functions
import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()
        
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result
    return wrapper

@profile_function
def slow_function():
    # Your code here
    pass
```

## Getting Help

### Collecting Debug Information

```bash
# Create debug report
cat > debug_info.txt << EOF
System Information:
==================
OS: $(uname -a)
Python: $(python --version)
uv: $(uv --version)

Environment Variables:
==================
DATABASE_URL: ${DATABASE_URL:0:20}...
REDIS_URL: ${REDIS_URL:0:20}...

Application Status:
==================
Health Check: $(curl -s http://localhost:8000/health)
Database Connection: $(psql $DATABASE_URL -c "SELECT 1;" 2>&1)
Redis Connection: $(redis-cli ping 2>&1)

Recent Logs:
=============
$(tail -20 logs/app.log 2>/dev/null || echo "No log file found")
EOF

echo "Debug information saved to debug_info.txt"
```

### Community Resources

- **GitHub Issues**: [Create an issue](https://github.com/your-org/mnfst-rag/issues)
- **Discord Community**: [Join our Discord](https://discord.gg/mnfst-rag)
- **Stack Overflow**: Tag questions with `mnfst-rag`
- **Documentation**: [Full documentation](https://docs.mnfst-rag.com)

### Reporting Issues

When reporting issues, include:

1. **Environment**: OS, Python version, dependencies
2. **Error Message**: Full error traceback
3. **Steps to Reproduce**: Detailed reproduction steps
4. **Expected Behavior**: What you expected to happen
5. **Actual Behavior**: What actually happened
6. **Debug Information**: Output from debug_info.txt

## Prevention

### Regular Maintenance

```bash
# Update dependencies regularly
uv sync --upgrade

# Run security scans
uv run safety check
uv run bandit -r app/

# Monitor system health
# Set up monitoring alerts
# Regular backup verification
```

### Code Quality

```bash
# Run linting
uv run black --check app/
uv run isort --check-only app/
uv run flake8 app/
uv run mypy app/

# Run tests
uv run pytest --cov=app
```

This troubleshooting guide should help you resolve most common issues with the MNFST-RAG Backend. For additional help, don't hesitate to reach out to our community!