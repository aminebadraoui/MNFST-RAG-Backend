# MNFST-RAG Backend Documentation

Complete documentation for the MNFST-RAG backend application.

## 📚 Table of Contents

- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Database](#database)
- [API Documentation](#api-documentation)
- [Features](#features)
- [Deployment](#deployment)
- [Development](#development)
- [Appendices](#appendices)

## Getting Started

| Document | Description |
|----------|-------------|
| [Installation Guide](./getting-started/installation.md) | Set up development environment |
| [Quick Start](./getting-started/quick-start.md) | Get running in 5 minutes |
| [Configuration](./getting-started/configuration.md) | Environment and app configuration |

## Architecture

| Document | Description |
|----------|-------------|
| [System Architecture](./architecture/system-architecture.md) | Overall system design |
| [Dependency Injection](./architecture/dependency-injection.md) | FastAPI dependency injection patterns and implementation |
| [Multi-Tenant Design](./architecture/multi-tenant-design.md) | Multi-tenancy implementation |
| [Authentication System](./architecture/auth-system.md) | Security and access control |
| [Database Schema](./architecture/database-schema.md) | Data models and relationships |

## Database

🆕 **New Consolidated Database Documentation**

We've consolidated all database-related documentation into a dedicated section:

| Document | Description |
|----------|-------------|
| [Database Overview](./database/README.md) | **Main database documentation hub** |
| [Database Schema](./database/schema.md) | Complete schema, tables, and relationships |
| [Database Setup](./database/setup.md) | Initialization, migration, and seeding |
| [Database Configuration](./database/configuration.md) | Connection pooling, performance, and security |
| [Database Troubleshooting](./database/troubleshooting.md) | Common issues and solutions |
| [Database Migrations](./database/migrations.md) | Migration management with Alembic |

### Quick Database Links

- **[Database Setup Quick Start](./database/setup.md#-quick-start)** - Get database running in minutes
- **[Connection Configuration](./database/configuration.md#-connection-configuration)** - Configure database connections
- **[Troubleshooting Guide](./database/troubleshooting.md#-quick-diagnosis)** - Fix common database issues
- **[Migration Commands](./database/migrations.md#-migration-commands)** - Database migration reference

## API Documentation

| Document | Description |
|----------|-------------|
| [API Overview](./api/overview.md) | API design and usage |
| [Authentication Endpoints](./api/auth.md) | Authentication and authorization |
| [Document Management](./api/documents.md) | Document upload and processing |
| [Chat API](./api/chat.md) | Chat functionality |
| [Social Media Integration](./api/social.md) | Social media features |
| [Tenant Management](./api/tenants.md) | Multi-tenant operations |

## Features

| Document | Description |
|----------|-------------|
| [Document Processing](./features/document-processing.md) | RAG document processing pipeline |
| [Multi-Tenancy](./features/multi-tenancy.md) | Tenant isolation and management |
| [Real-time Chat](./features/real-time-chat.md) | WebSocket-based chat system |
| [File Storage](./features/file-storage.md) | Cloud storage integration |

## Deployment

| Document | Description |
|----------|-------------|
| [Production Deployment](./deployment/production.md) | Production deployment guide |
| [Docker Deployment](./deployment/docker.md) | Container-based deployment |
| [Environment Setup](./deployment/environment-setup.md) | Environment configuration |
| [Monitoring](./deployment/monitoring.md) | Application monitoring and logging |

## Development

| Document | Description |
|----------|-------------|
| [Development Setup](./development/setup.md) | Development environment setup |
| [Testing Guide](./development/testing.md) | Testing strategies and tools |
| [Code Style](./development/code-style.md) | Coding standards and conventions |
| [Contributing](./development/contributing.md) | Contribution guidelines |

## Appendices

| Document | Description |
|----------|-------------|
| [Troubleshooting](./appendices/troubleshooting.md) | Common issues and solutions |
| [FAQ](./appendices/faq.md) | Frequently asked questions |
| [Glossary](./appendices/glossary.md) | Terms and definitions |
| [Changelog](./appendices/changelog.md) | Version history and changes |

## 🔍 Quick Navigation

### For New Developers

1. Start with [Installation Guide](./getting-started/installation.md)
2. Read [Quick Start](./getting-started/quick-start.md)
3. Understand [System Architecture](./architecture/system-architecture.md)
4. Review [Database Overview](./database/README.md)
5. Check [API Overview](./api/overview.md)

### For Database Administrators

1. Go to [Database Overview](./database/README.md)
2. Review [Database Schema](./database/schema.md)
3. Follow [Database Setup](./database/setup.md)
4. Configure [Database Connections](./database/configuration.md)
5. Bookmark [Troubleshooting Guide](./database/troubleshooting.md)

### For DevOps Engineers

1. Read [Production Deployment](./deployment/production.md)
2. Review [Database Configuration](./database/configuration.md)
3. Check [Environment Setup](./deployment/environment-setup.md)
4. Set up [Monitoring](./deployment/monitoring.md)
5. Review [Troubleshooting](./appendices/troubleshooting.md)

### For API Users

1. Start with [API Overview](./api/overview.md)
2. Review [Authentication](./api/auth.md)
3. Check relevant endpoints:
   - [Documents](./api/documents.md)
   - [Chat](./api/chat.md)
   - [Social](./api/social.md)
   - [Tenants](./api/tenants.md)

## 🛠️ Common Tasks

### Database Operations

```bash
# Setup database
./scripts/db.sh setup

# Run migrations
./scripts/db.sh migrate

# Check status
./scripts/db.sh status

# Create backup
./scripts/db.sh backup backup_name.sql
```

### Application Development

```bash
# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Check code style
black app/
flake8 app/
```

### Deployment

```bash
# Build Docker image
docker build -t mnfst-rag-backend .

# Deploy to production
./scripts/deploy.sh production
```

## 📋 Documentation Structure

```
docs/
├── README.md                    # This file
├── database/                   # 🆕 Consolidated database docs
│   ├── README.md               # Database overview and hub
│   ├── schema.md               # Complete database schema
│   ├── setup.md               # Database initialization and setup
│   ├── configuration.md        # Database configuration and connections
│   ├── troubleshooting.md      # Database troubleshooting
│   └── migrations.md          # Database migration guide
├── getting-started/            # Getting started guides
├── architecture/              # System architecture
├── api/                      # API documentation
├── features/                  # Feature documentation
├── deployment/                # Deployment guides
├── development/               # Development guides
└── appendices/               # Additional resources
```

## 🤝 Contributing to Documentation

### Adding New Documentation

1. Choose appropriate section in the structure above
2. Follow the established format and style
3. Update this README.md with links to new documents
4. Add cross-references to related documentation

### Documentation Standards

- Use clear, descriptive titles
- Include table of contents for long documents
- Add code examples with syntax highlighting
- Include diagrams and visualizations where helpful
- Provide both quick start and detailed information
- Add cross-references to related documents

### Review Process

1. Create pull request with documentation changes
2. Request review from maintainers
3. Update based on feedback
4. Ensure all links work correctly
5. Merge to main branch

## 🔗 External Resources

### Technology Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Supabase Documentation](https://supabase.com/docs)

### Development Tools

- [Python 3.11+](https://www.python.org/)
- [PostgreSQL 15+](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [GitHub Actions](https://github.com/features/actions)

## 📞 Getting Help

### Documentation Issues

- Found outdated information? [Create an issue](https://github.com/your-org/mnfst-rag/issues)
- Missing documentation? [Request documentation](https://github.com/your-org/mnfst-rag/discussions)
- Want to contribute? See [Contributing Guide](./development/contributing.md)

### Technical Support

- Check [Troubleshooting Guide](./appendices/troubleshooting.md)
- Review [FAQ](./appendices/faq.md)
- Search existing [GitHub Issues](https://github.com/your-org/mnfst-rag/issues)
- Join our [Discord Community](https://discord.gg/mnfst-rag)

---

**Last Updated**: 2025-11-08  
**Version**: 1.0.0  
**Maintainer**: MNFST-RAG Team

**Quick Links**:
- [🚀 Quick Start](./getting-started/quick-start.md)
- [🗄️ Database Hub](./database/README.md)
- [📖 API Overview](./api/overview.md)
- [🏗️ Architecture](./architecture/system-architecture.md)
- [🚀 Deployment](./deployment/production.md)