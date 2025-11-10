# Quick Start Guide

## Overview

This guide will help you get the MNFST-RAG Backend running in minutes. We'll cover the fastest path from installation to a working API with mock data.

## Prerequisites

Make sure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **uv** - Python package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git** - [Download Git](https://git-scm.com/downloads)

## 5-Minute Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/your-org/mnfst-rag.git
cd mnfst-rag/mnfst-rag-backend

# Install dependencies
uv sync

# Create environment file
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with minimal configuration:

```env
# Basic settings
APP_NAME=MNFST-RAG API
DEBUG=True

# Database (use SQLite for quick start)
DATABASE_URL=sqlite:///./mnfst_rag.db

# CORS (for local development)
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### 3. Start the Server

```bash
# Start the development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Installation

Open your browser and navigate to:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

You should see the API documentation interface and a healthy status response.

## Testing the API

### 1. Test Authentication

```bash
# Test login (using mock data)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "any-password"
  }'
```

### 2. Test Tenant Management

```bash
# Create a tenant (mock response)
curl -X POST "http://localhost:8000/api/v1/tenants" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Tenant",
    "slug": "test-tenant",
    "admin_user": {
      "email": "admin@test.com",
      "name": "Test Admin",
      "password": "password123",
      "role": "tenant_admin"
    }
  }'
```

### 3. Test Document Upload

```bash
# Get presigned URL for upload
curl -X POST "http://localhost:8000/api/v1/documents/presigned-url" \
  -H "Content-Type: application/json" \
  -d '{
    "original_name": "test-document.pdf",
    "size": 1024000,
    "mime_type": "application/pdf"
  }'
```

## Using Mock Data

The backend includes a comprehensive mock data generator for testing:

```python
# Generate mock data in Python
from app.utils.mock_data import MockDataGenerator

# Generate mock users
users = MockDataGenerator.generate_users(count=5, role="user")

# Generate mock documents
documents = MockDataGenerator.generate_documents(count=10)

# Generate mock chat sessions
sessions = MockDataGenerator.generate_sessions(count=3)
```

## Frontend Integration

### 1. Install Frontend

```bash
# Navigate to frontend directory
cd ../mnfst-rag-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

### 2. Configure Frontend

Create `.env` file in frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=MNFST-RAG
```

### 3. Test Integration

Open http://localhost:5173 in your browser and test the full application.

## Database Setup (Optional)

For production-like setup with PostgreSQL:

### 1. Using Docker

```bash
# Start PostgreSQL with Docker
docker run --name mnfst-postgres \
  -e POSTGRES_DB=mnfst_rag \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Update .env file
DATABASE_URL=postgresql://postgres:password@localhost:5432/mnfst_rag
```

### 2. Using Supabase (Recommended)

1. Create a free account at [Supabase](https://supabase.com)
2. Create a new project
3. Get the connection string from project settings
4. Update your `.env` file:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-SUPABASE-KEY]
```

## Common Development Tasks

### 1. Adding New API Endpoints

```python
# app/api/v1/example.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/example")
async def get_example():
    return {"message": "Hello, World!"}

# Add to main.py
app.include_router(router, prefix="/api/v1/example", tags=["Example"])
```

### 2. Adding New Models

```python
# app/models/example.py
from sqlmodel import SQLModel, Field
from .base import BaseSQLModel

class Example(BaseSQLModel, table=True):
    __tablename__ = "examples"
    
    name: str = Field(description="Example name")
    value: str = Field(description="Example value")
```

### 3. Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_auth.py
```

### 4. Code Formatting

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Type checking
uv run mypy app/
```

## Environment-Specific Setups

### Development Environment

```env
# .env.development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./mnfst_rag_dev.db
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Production Environment

```env
# .env.production
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:password@prod-db:5432/mnfst_rag
ALLOWED_ORIGINS=["https://your-domain.com"]
JWT_SECRET_KEY=your-super-secret-jwt-key
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   
   # Or use different port
   uv run uvicorn app.main:app --port 8001
   ```

2. **Import Errors**
   ```bash
   # Reinstall dependencies
   uv sync --refresh
   
   # Recreate virtual environment
   rm -rf .venv
   uv venv
   uv sync
   ```

3. **Database Connection Issues**
   ```bash
   # Check database URL format
   echo $DATABASE_URL
   
   # Test connection
   uv run python -c "from app.database import engine; print(engine.url)"
   ```

4. **CORS Issues**
   ```bash
   # Check allowed origins
   curl -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: X-Requested-With" \
        -X OPTIONS http://localhost:8000/api/v1/auth/login
   ```

### Getting Help

- **Check logs**: Look for error messages in the console
- **API Documentation**: Visit http://localhost:8000/docs
- **GitHub Issues**: Search for similar problems
- **Community**: Join our Discord community

## Next Steps

After successful quick start:

1. **Read Architecture**: [System Architecture](../architecture/system-architecture.md)
2. **Explore API**: [API Overview](../api/overview.md)
3. **Configure Database**: [Database Schema](../architecture/database-schema.md)
4. **Set Up Authentication**: [Auth System](../architecture/auth-system.md)
5. **Deploy to Production**: [Deployment Guide](../deployment/production.md)

## Video Tutorial

For a visual walkthrough, check out our quick start video:

[![Quick Start Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)

## One-Click Setup

For the fastest setup, use our Docker Compose:

```bash
# Create docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mnfst_rag
      - DEBUG=True
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mnfst_rag
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# Start everything
docker-compose up --build
```

This will start both the application and database with a single command!

## Performance Tips

### Development Performance

```bash
# Use SQLite for faster development
DATABASE_URL=sqlite:///./mnfst_rag.db

# Disable unnecessary features
DEBUG=False
LOG_LEVEL=ERROR

# Use faster server
uv run uvicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Memory Usage

```bash
# Monitor memory usage
uv run python -m memory_profiler app/main.py

# Use lighter dependencies
uv sync --no-dev
```

## Security Notes

⚠️ **Important**: The quick start uses insecure defaults suitable only for development:

- JWT secret key is not set
- Database has no password
- CORS allows all origins
- Debug mode is enabled

For production deployment, always:

1. Set a strong JWT secret key
2. Use a secure database connection
3. Configure proper CORS origins
4. Disable debug mode
5. Use HTTPS
6. Set up proper logging and monitoring

## Congratulations! 🎉

You now have a running MNFST-RAG Backend with:

- ✅ FastAPI server with auto-generated documentation
- ✅ Multi-tenant architecture
- ✅ Authentication endpoints
- ✅ Document management
- ✅ Chat functionality
- ✅ Mock data for testing

Ready to build something amazing? Check out our [development guides](../implementation/development-setup.md) to learn more!