# Production Deployment Guide

## Overview

This guide covers deploying the MNFST-RAG Backend to production environments. We'll cover various deployment strategies, security considerations, monitoring, and best practices for running a scalable, reliable production system.

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Load Balancer/CDN]
    end
    
    subgraph "Application Layer"
        APP1[App Instance 1]
        APP2[App Instance 2]
        APP3[App Instance N]
    end
    
    subgraph "Services"
        REDIS[Redis Cache]
        WORKER[Background Workers]
        MONITOR[Monitoring]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL Primary)]
        DB_REPLICA[(PostgreSQL Replica)]
        VECTOR[(Vector DB)]
    end
    
    subgraph "Storage"
        R2[Cloudflare R2]
        BACKUP[Backup Storage]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    
    APP1 --> DB_REPLICA
    APP2 --> DB_REPLICA
    APP3 --> DB_REPLICA
    
    APP1 --> VECTOR
    APP2 --> VECTOR
    APP3 --> VECTOR
    
    APP1 --> R2
    APP2 --> R2
    APP3 --> R2
    
    WORKER --> DB
    WORKER --> VECTOR
    WORKER --> R2
    
    DB --> BACKUP
    VECTOR --> BACKUP
```

## Deployment Options

### 1. Docker Container Deployment

#### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DEBUG=False
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  worker:
    build: .
    restart: unless-stopped
    command: uv run celery -A app.worker worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs

volumes:
  redis_data:
```

### 2. Kubernetes Deployment

#### Deployment Manifest

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mnfst-rag-backend
  labels:
    app: mnfst-rag-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mnfst-rag-backend
  template:
    metadata:
      labels:
        app: mnfst-rag-backend
    spec:
      containers:
      - name: app
        image: mnfst-rag/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mnfst-rag-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: mnfst-rag-secrets
              key: jwt-secret
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: mnfst-rag-config
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: mnfst-rag-backend-service
spec:
  selector:
    app: mnfst-rag-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mnfst-rag-backend-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.mnfst-rag.com
    secretName: mnfst-rag-tls
  rules:
  - host: api.mnfst-rag.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mnfst-rag-backend-service
            port:
              number: 80
```

### 3. Cloud Platform Deployment

#### AWS ECS

```json
{
  "family": "mnfst-rag-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "mnfst-rag-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/mnfst-rag-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mnfst-rag/db-url"
        },
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mnfst-rag/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mnfst-rag-backend",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mnfst-rag-backend', '.']
  
  # Push the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mnfst-rag-backend']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'mnfst-rag-backend'
    - '--image=gcr.io/$PROJECT_ID/mnfst-rag-backend'
    - '--region=us-central1'
    - '--platform=managed'
    - '--allow-unauthenticated'
    - '--memory=1Gi'
    - '--cpu=1'
    - '--max-instances=10'
    - '--set-env-vars=ENVIRONMENT=production'
    - '--set-secrets=DATABASE_URL=mnfst-rag-db-url:latest,JWT_SECRET_KEY=mnfst-rag-jwt-secret:latest'

images:
  - 'gcr.io/$PROJECT_ID/mnfst-rag-backend'
```

## Environment Configuration

### Production Environment Variables

```env
# .env.production
# Application
APP_NAME=MNFST-RAG API
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/mnfst_rag
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

# Security
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-32-chars-min
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
ALLOWED_ORIGINS=["https://app.mnfst-rag.com", "https://admin.mnfst-rag.com"]

# Storage
R2_ACCOUNT_ID=your-r2-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret-key
R2_BUCKET_NAME=mnfst-rag-prod-documents
R2_PUBLIC_URL=https://prod-docs.mnfst-rag.com

# AI Services
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Cache
REDIS_URL=redis://prod-redis:6379/0
REDIS_PASSWORD=your-redis-password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production
SENTRY_SAMPLE_RATE=0.5

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
```

## Security Configuration

### 1. SSL/TLS Setup

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/mnfst-rag-api
server {
    listen 443 ssl http2;
    server_name api.mnfst-rag.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/mnfst-rag-api.crt;
    ssl_certificate_key /etc/ssl/private/mnfst-rag-api.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name api.mnfst-rag.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Firewall Configuration

```bash
# UFW Configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application port (only from load balancer)
sudo ufw allow from 10.0.0.0/8 to any port 8000

# Enable firewall
sudo ufw enable
```

### 3. Secret Management

#### HashiCorp Vault

```python
# app/services/vault_client.py
import hvac
from app.config import settings

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=settings.vault_url,
            token=settings.vault_token
        )
    
    def get_secret(self, path: str) -> dict:
        """Get secret from Vault"""
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response['data']['data']
    
    def get_database_url(self) -> str:
        """Get database URL from Vault"""
        secret = self.get_secret('database')
        return secret['url']
    
    def get_jwt_secret(self) -> str:
        """Get JWT secret from Vault"""
        secret = self.get_secret('jwt')
        return secret['secret_key']
```

## Database Setup

### 1. PostgreSQL Production Configuration

```postgresql
# postgresql.conf
# Memory Settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection Settings
max_connections = 200
listen_addresses = '*'

# Performance Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_min_duration_statement = 1000
```

### 2. Database Migration

```bash
# Run migrations
uv run alembic upgrade head

# Create backup before migration
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify migration
uv run python -c "from app.database import engine; print('Database OK')"
```

### 3. Replication Setup

```bash
# Primary server configuration
# postgresql.conf
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'

# Create replication user
CREATE USER replicator REPLICATION LOGIN CONNECTION LIMIT 3 ENCRYPTED PASSWORD 'replicator_password';

# Replica server configuration
# postgresql.conf
standby_mode = on
primary_conninfo = 'host=primary-db port=5432 user=replicator'
restore_command = 'cp /var/lib/postgresql/archive/%f %p'
```

## Monitoring and Logging

### 1. Application Monitoring

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mnfst-rag-backend'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

#### Custom Metrics

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request, Response
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() start_time)
    
    return response
```

### 2. Logging Configuration

```python
# app/utils/production_logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Configure production logging
def setup_production_logging():
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        '/var/log/mnfst-rag/app.log',
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler]
    )
```

### 3. Error Tracking

```python
# app/utils/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        sample_rate=settings.sentry_sample_rate,
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=False
    )
```

## Performance Optimization

### 1. Application Performance

#### Connection Pooling

```python
# app/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

#### Caching Strategy

```python
# app/services/cache.py
import redis
from functools import wraps

redis_client = redis.Redis.from_url(settings.redis_url)

def cache_result(ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

### 2. Database Performance

#### Query Optimization

```python
# app/services/optimized_queries.py
from sqlalchemy import text

class OptimizedQueries:
    @staticmethod
    async def get_tenant_documents(tenant_id: UUID, limit: int = 50):
        """Optimized query for tenant documents with pagination"""
        
        query = text("""
            SELECT d.id, d.filename, d.original_name, d.created_at
            FROM documents d
            WHERE d.tenant_id = :tenant_id
            ORDER BY d.created_at DESC
            LIMIT :limit
        """)
        
        return await db.execute(query, {
            "tenant_id": tenant_id,
            "limit": limit
        })
    
    @staticmethod
    async def search_documents_vector(tenant_id: UUID, query_embedding: list):
        """Optimized vector search"""
        
        query = text("""
            SELECT d.id, d.content, d.metadata,
                   1 - (d.embedding <=> :query_embedding) as similarity
            FROM document_vectors d
            WHERE d.tenant_id = :tenant_id
            AND 1 - (d.embedding <=> :query_embedding) > 0.7
            ORDER BY similarity DESC
            LIMIT 10
        """)
        
        return await db.execute(query, {
            "tenant_id": tenant_id,
            "query_embedding": query_embedding
        })
```

## Backup and Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup.sh

# Configuration
DB_URL=$DATABASE_URL
BACKUP_DIR="/var/backups/mnfst-rag"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump $DB_URL > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Upload to cloud storage
aws s3 cp $BACKUP_FILE.gz s3://mnfst-rag-backups/database/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

### 2. File Backup

```bash
#!/bin/bash
# backup_files.sh

R2_BUCKET="mnfst-rag-documents"
BACKUP_BUCKET="mnfst-rag-backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Sync documents to backup bucket
aws s3 sync s3://$R2_BUCKET/ s3://$BACKUP_BUCKET/documents/$DATE/

echo "File backup completed: $DATE"
```

### 3. Recovery Procedures

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_URL=$DATABASE_URL

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Download backup from S3
aws s3 cp s3://mnfst-rag-backups/database/$BACKUP_FILE ./

# Decompress backup
gunzip $BACKUP_FILE

# Restore database
psql $DB_URL < ${BACKUP_FILE%.gz}

echo "Database restored from: $BACKUP_FILE"
```

## Scaling Strategies

### 1. Horizontal Scaling

#### Load Balancer Configuration

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app

  app:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      replicas: 5
    depends_on:
      - redis
      - db

  redis:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=mnfst_rag
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 2. Database Scaling

#### Read Replicas

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Primary database for writes
primary_engine = create_engine(settings.database_url)

# Replica database for reads
replica_engine = create_engine(settings.database_replica_url)

# Session factories
PrimarySession = sessionmaker(bind=primary_engine)
ReplicaSession = sessionmaker(bind=replica_engine)

def get_read_session():
    """Get session for read operations"""
    return ReplicaSession()

def get_write_session():
    """Get session for write operations"""
    return PrimarySession()
```

## Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database migrations tested
- [ ] Backup procedures verified
- [ ] Monitoring configured
- [ ] Security scanning completed
- [ ] Load testing performed
- [ ] Documentation updated

### Post-Deployment

- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Log collection working
- [ ] Performance benchmarks met
- [ ] Security headers verified
- [ ] DNS propagation complete
- [ ] SSL certificate valid
- [ ] Backup schedule active

## Troubleshooting

### Common Production Issues

1. **Database Connection Errors**
   ```bash
   # Check database connectivity
   psql $DATABASE_URL -c "SELECT 1;"
   
   # Check connection pool
   uv run python -c "from app.database import engine; print(engine.pool.status())"
   ```

2. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Check for memory leaks
   uv run python -m memory_profiler app/main.py
   ```

3. **Slow Response Times**
   ```bash
   # Check database queries
   uv run python -c "from app.utils.query_profiler import profile_queries; profile_queries()"
   
   # Analyze slow queries
   SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;
   ```

This comprehensive deployment guide should help you successfully deploy the MNFST-RAG Backend to production with proper security, monitoring, and scalability considerations.