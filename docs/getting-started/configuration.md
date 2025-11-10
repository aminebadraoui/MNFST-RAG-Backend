# Configuration

## Overview

The MNFST-RAG Backend uses a comprehensive configuration system based on Pydantic Settings. Configuration is managed through environment variables, with support for different environments (development, staging, production) and sensible defaults.

## Configuration Files

### Primary Configuration

- **Main Config**: [`app/config.py`](../../app/config.py) - Core application settings
- **Environment**: `.env` - Environment-specific variables
- **Environment Template**: `.env.example` - Template with all available options

### Configuration Hierarchy

1. **Environment Variables** (highest priority)
2. **.env file**
3. **Default values** in code (lowest priority)

## Environment Variables

### Core Application Settings

```env
# Application Identity
APP_NAME=MNFST-RAG API
APP_VERSION=1.0.0
APP_DESCRIPTION=Multi-tenant RAG application API

# Debug Mode
DEBUG=False
LOG_LEVEL=INFO
```

### Database Configuration

```env
# Primary Database
DATABASE_URL=postgresql://user:password@host:port/database

# Database Pool Settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Database SSL (for production)
DB_SSL_MODE=require
DB_SSL_CERT_PATH=/path/to/cert.pem
```

### CORS Configuration

```env
# Allowed Origins (comma-separated)
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# CORS Settings
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
```

### Authentication & Security

```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Password Security
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_NUMBERS=True
PASSWORD_REQUIRE_SYMBOLS=True
```

### File Storage Configuration

```env
# Cloudflare R2 Storage
R2_ACCOUNT_ID=your-r2-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=mnfst-rag-documents
R2_PUBLIC_URL=https://your-bucket.r2.cloudflarestorage.com

# File Upload Limits
MAX_FILE_SIZE_MB=50
MAX_FILES_PER_TENANT=1000
MAX_STORAGE_PER_TENANT_GB=10
```

### AI/LLM Configuration

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Alternative LLM Providers
ANTHROPIC_API_KEY=your-anthropic-api-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Hugging Face Configuration
HUGGINGFACE_API_KEY=your-huggingface-api-key
HUGGINGFACE_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Vector Database Configuration

```env
# Vector Database (pgvector)
VECTOR_DB_URL=postgresql://user:password@host:port/vector_db
VECTOR_DIMENSION=1536
VECTOR_INDEX_TYPE=ivfflat
VECTOR_INDEX_LISTS=100

# Vector Search Settings
VECTOR_SEARCH_LIMIT=5
VECTOR_SIMILARITY_THRESHOLD=0.7
```

### Cache Configuration

```env
# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your-redis-password
REDIS_DB=0
REDIS_MAX_CONNECTIONS=20

# Cache TTL Settings
CACHE_TTL_SECONDS=3600
EMBEDDING_CACHE_TTL_SECONDS=86400
SESSION_CACHE_TTL_SECONDS=1800
```

### Monitoring & Logging

```env
# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE_PATH=/var/log/mnfst-rag/app.log
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=5

# Metrics Collection
METRICS_ENABLED=True
METRICS_PORT=9090
METRICS_PATH=/metrics

# Error Tracking
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production
SENTRY_SAMPLE_RATE=1.0
```

### Email Configuration

```env
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True

# Email Templates
EMAIL_FROM=noreply@mnfst-rag.com
EMAIL_REPLY_TO=support@mnfst-rag.com
```

### Rate Limiting

```env
# Rate Limiting Settings
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
RATE_LIMIT_BURST_SIZE=100

# Per-Endpoint Limits
RATE_LIMIT_AUTH_ENDPOINTS=10
RATE_LIMIT_UPLOAD_ENDPOINTS=20
RATE_LIMIT_CHAT_ENDPOINTS=60
```

## Environment-Specific Configuration

### Development Environment

```env
# .env.development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:password@localhost:5432/mnfst_rag_dev
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
REDIS_URL=redis://localhost:6379/0
```

### Staging Environment

```env
# .env.staging
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@staging-db:5432/mnfst_rag_staging
ALLOWED_ORIGINS=["https://staging.mnfst-rag.com"]
REDIS_URL=redis://staging-redis:6379/0
SENTRY_ENVIRONMENT=staging
```

### Production Environment

```env
# .env.production
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:password@prod-db:5432/mnfst_rag_prod
ALLOWED_ORIGINS=["https://app.mnfst-rag.com"]
REDIS_URL=redis://prod-redis:6379/0
SENTRY_ENVIRONMENT=production
SENTRY_SAMPLE_RATE=0.5
```

## Configuration Classes

### Base Settings Class

```python
# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    app_name: str = Field(default="MNFST-RAG API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/mnfst_rag",
        description="Database connection URL"
    )
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### Environment-Specific Settings

```python
# app/config.py
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "postgresql://postgres:password@localhost:5432/mnfst_rag_dev"

class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    log_level: str = "WARNING"
    database_url: str = Field(..., description="Production database URL required")

def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "staging":
        return StagingSettings()
    else:
        return DevelopmentSettings()
```

## Configuration Validation

### Custom Validators

```python
# app/config.py
from pydantic import validator

class Settings(BaseSettings):
    # ... other fields
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith(('postgresql://', 'sqlite:///')):
            raise ValueError('Database URL must be PostgreSQL or SQLite')
        return v
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        """Validate JWT secret key strength"""
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters')
        return v
    
    @validator('allowed_origins')
    def validate_origins(cls, v):
        """Validate CORS origins"""
        for origin in v:
            if not origin.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid origin format: {origin}')
        return v
```

## Runtime Configuration

### Dynamic Configuration

```python
# app/services/config_service.py
class ConfigService:
    """Service for dynamic configuration management"""
    
    def __init__(self):
        self.redis = Redis(settings.redis_url)
        self.config_cache = {}
    
    async def get_tenant_config(self, tenant_id: str) -> dict:
        """Get tenant-specific configuration"""
        cache_key = f"tenant_config:{tenant_id}"
        
        # Try cache first
        config = await self.redis.get(cache_key)
        if config:
            return json.loads(config)
        
        # Load from database
        config = await self.load_tenant_config_from_db(tenant_id)
        
        # Cache for 1 hour
        await self.redis.setex(cache_key, 3600, json.dumps(config))
        
        return config
    
    async def update_tenant_config(self, tenant_id: str, config: dict) -> None:
        """Update tenant-specific configuration"""
        # Update database
        await self.save_tenant_config_to_db(tenant_id, config)
        
        # Update cache
        cache_key = f"tenant_config:{tenant_id}"
        await self.redis.setex(cache_key, 3600, json.dumps(config))
```

## Configuration Management

### Environment Loading

```python
# app/config.py
import os
from pathlib import Path

def load_environment():
    """Load environment variables from appropriate file"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    env_file = Path(f".env.{env}")
    
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv(".env")  # Fallback to default .env

# Load environment at startup
load_environment()
```

### Configuration Hot Reload

```python
# app/services/config_watcher.py
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigWatcher(FileSystemEventHandler):
    """Watch for configuration file changes"""
    
    def __init__(self, config_service):
        self.config_service = config_service
    
    def on_modified(self, event):
        if event.src_path.endswith('.env'):
            asyncio.create_task(self.reload_config())
    
    async def reload_config(self):
        """Reload configuration from file"""
        logger.info("Configuration file changed, reloading...")
        await self.config_service.reload_settings()
```

## Security Considerations

### Sensitive Data Protection

```python
# app/config.py
from cryptography.fernet import Fernet

class SecureSettings:
    """Settings with encrypted sensitive values"""
    
    def __init__(self):
        self.cipher = Fernet(self.get_encryption_key())
    
    def get_encryption_key(self) -> str:
        """Get or create encryption key"""
        key_file = Path(".encryption_key")
        if key_file.exists():
            return key_file.read_text()
        
        key = Fernet.generate_key()
        key_file.write_text(key.decode())
        key_file.chmod(0o600)  # Restrict permissions
        return key
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt sensitive configuration value"""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt sensitive configuration value"""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
```

### Environment Variable Validation

```python
# app/config.py
import re

def validate_email_config():
    """Validate email configuration"""
    if not settings.smtp_host:
        raise ValueError("SMTP host is required")
    
    if not settings.smtp_username:
        raise ValueError("SMTP username is required")
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, settings.smtp_username):
        raise ValueError("Invalid SMTP username format")

def validate_database_config():
    """Validate database configuration"""
    try:
        # Test database connection
        engine = create_engine(settings.database_url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
    except Exception as e:
        raise ValueError(f"Database connection failed: {e}")
```

## Configuration Best Practices

### 1. Environment Separation

- Use separate `.env` files for each environment
- Never commit `.env` files to version control
- Use `.env.example` as a template

### 2. Secret Management

```bash
# Use environment-specific secrets
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export DB_PASSWORD=$(openssl rand -base64 32)

# Or use secret management services
export JWT_SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id jwt-key --query SecretString --output text)
```

### 3. Configuration Validation

```python
# app/main.py
@app.on_event("startup")
async def validate_configuration():
    """Validate configuration on startup"""
    try:
        validate_database_config()
        validate_email_config()
        validate_jwt_config()
        logger.info("Configuration validation passed")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
```

### 4. Configuration Documentation

- Document all configuration options
- Provide examples for common use cases
- Include security considerations
- Specify required vs optional settings

## Troubleshooting Configuration

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Test database connection
   psql $DATABASE_URL -c "SELECT 1;"
   ```

2. **CORS Issues**
   ```bash
   # Check allowed origins
   echo $ALLOWED_ORIGINS
   ```

3. **JWT Token Issues**
   ```bash
   # Generate new secret key
   openssl rand -hex 32
   ```

4. **File Upload Issues**
   ```bash
   # Test R2 connection
   aws s3 ls --endpoint-url $R2_ENDPOINT_URL
   ```

### Debug Mode

Enable debug mode for detailed configuration information:

```env
DEBUG=True
LOG_LEVEL=DEBUG
```

This will log:
- Configuration loading
- Validation results
- Connection attempts
- Environment variable resolution