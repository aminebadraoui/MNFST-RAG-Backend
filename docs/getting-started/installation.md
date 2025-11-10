# Installation

## Prerequisites

Before installing the MNFST-RAG Backend, ensure you have the following prerequisites:

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.11 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: Minimum 1GB free disk space

### Required Software

1. **Python 3.11+**
   ```bash
   # Check Python version
   python --version
   
   # Install Python (if not installed)
   # Ubuntu/Debian:
   sudo apt update && sudo apt install python3.11 python3.11-venv
   
   # macOS (using Homebrew):
   brew install python@3.11
   
   # Windows: Download from python.org
   ```

2. **uv Package Manager**
   ```bash
   # Install uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or using pip:
   pip install uv
   ```

3. **PostgreSQL Database**
   ```bash
   # Option 1: Local PostgreSQL
   # Ubuntu/Debian:
   sudo apt install postgresql postgresql-contrib
   
   # macOS (using Homebrew):
   brew install postgresql
   
   # Option 2: Supabase (recommended for development)
   # Sign up at https://supabase.com
   ```

4. **Git**
   ```bash
   # Ubuntu/Debian:
   sudo apt install git
   
   # macOS (using Homebrew):
   brew install git
   
   # Windows: Download from git-scm.com
   ```

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/mnfst-rag.git

# Navigate to the backend directory
cd mnfst-rag/mnfst-rag-backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment using uv
uv venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install dependencies using uv
uv sync

# Or install development dependencies
uv sync --dev
```

### 4. Set Up Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit the environment file
nano .env  # or use your preferred editor
```

### 5. Configure Database

#### Option A: Local PostgreSQL

```bash
# Create database
sudo -u postgres createdb mnfst_rag

# Create user (optional)
sudo -u postgres createuser --interactive
```

#### Option B: Supabase

1. Sign up at [Supabase](https://supabase.com)
2. Create a new project
3. Get your database URL from the project settings
4. Update your `.env` file with the Supabase credentials

### 6. Run Database Migrations

```bash
# Create database tables
uv run python -m app.database

# Or using Alembic (when implemented)
uv run alembic upgrade head
```

### 7. Verify Installation

```bash
# Check if the application starts
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Application Configuration
APP_NAME=MNFST-RAG API
APP_VERSION=1.0.0
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Supabase Configuration (if using Supabase)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# JWT Configuration (when implemented)
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# File Storage Configuration (when implemented)
R2_ACCOUNT_ID=your-r2-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=your-bucket-name
R2_PUBLIC_URL=https://your-bucket.r2.cloudflarestorage.com

# AI/LLM Configuration (when implemented)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Redis Configuration (when implemented)
REDIS_URL=redis://localhost:6379

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Database URL Formats

#### PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

#### Supabase
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

## Docker Installation (Alternative)

### Using Docker Compose

1. Create a `docker-compose.yml` file:

```yaml
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
```

2. Run the application:

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Using Dockerfile

1. Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. Build and run:

```bash
# Build image
docker build -t mnfst-rag-backend .

# Run container
docker run -p 8000:8000 --env-file .env mnfst-rag-backend
```

## Verification

### Health Check

After installation, verify the application is running correctly:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}
```

### API Documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Test Authentication

```bash
# Test login endpoint
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test-password"
  }'
```

## Troubleshooting

### Common Issues

#### 1. Python Version Incompatibility

**Error**: `Python 3.11+ is required`

**Solution**:
```bash
# Check your Python version
python --version

# Install Python 3.11+ using pyenv
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

#### 2. Database Connection Errors

**Error**: `Could not connect to database`

**Solution**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Verify database exists
psql -h localhost -U postgres -l
```

#### 3. Port Already in Use

**Error**: `Port 8000 is already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uv run uvicorn app.main:app --port 8001
```

#### 4. Permission Errors

**Error**: `Permission denied`

**Solution**:
```bash
# Fix file permissions
chmod +x scripts/*.sh

# Use virtual environment
source .venv/bin/activate
```

#### 5. Dependency Installation Issues

**Error**: `Failed to install dependencies`

**Solution**:
```bash
# Clear uv cache
uv cache clean

# Reinstall dependencies
uv sync --refresh

# Or install manually
pip install -r requirements.txt
```

### Getting Help

If you encounter issues during installation:

1. **Check the logs**: Look for detailed error messages
2. **Search existing issues**: Check GitHub Issues for similar problems
3. **Create an issue**: Provide detailed information about your environment
4. **Join our community**: Get help from other developers

### Log Files

Check the following log files for debugging:

- Application logs: `logs/app.log`
- Database logs: PostgreSQL logs in `/var/log/postgresql/`
- System logs: `/var/log/syslog` (Linux) or Console.app (macOS)

## Next Steps

After successful installation:

1. [Configure](configuration.md) your environment
2. [Run the quick start](quick-start.md) guide
3. [Read the API documentation](../api/overview.md)
4. [Set up development environment](../implementation/development-setup.md)

## Production Deployment

For production deployment, see the [Deployment Guide](../deployment/production.md).

Production considerations:

- Use HTTPS
- Configure proper CORS
- Set up monitoring
- Use environment-specific configurations
- Implement backup strategies
- Set up load balancing