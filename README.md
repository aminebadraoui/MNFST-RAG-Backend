# MNFST-RAG Backend

FastAPI backend for the MNFST-RAG application with multi-tenant support and role-based access control.

## Features

- **Multi-tenant architecture** with tenant isolation
- **Role-based access control** (superadmin, tenant_admin, user)
- **Document management** with RAG processing
- **Social media links** management
- **Chat functionality** with sessions and messages
- **JWT authentication** (placeholder implementation)
- **SQLModel** for database models
- **Supabase** PostgreSQL integration
- **CORS** support for frontend integration
- **OpenAPI** documentation with FastAPI

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQLAlchemy + Pydantic for database models
- **PostgreSQL** - Database (via Supabase)
- **Pydantic** - Data validation and serialization
- **uv** - Python package manager
- **Python 3.11+** - Latest Python version

## Project Structure

```
mnfst-rag-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection setup
│   ├── models/                 # SQLModel data models
│   │   ├── base.py            # Base model class
│   │   ├── user.py            # User model
│   │   ├── tenant.py          # Tenant model
│   │   ├── document.py        # Document model
│   │   ├── social.py          # Social link model
│   │   └── chat.py            # Chat session and message models
│   ├── schemas/                # Pydantic models for API
│   │   ├── auth.py            # Auth request/response schemas
│   │   ├── user.py            # User schemas
│   │   ├── tenant.py          # Tenant schemas
│   │   ├── document.py        # Document schemas
│   │   ├── social.py          # Social link schemas
│   │   └── chat.py            # Chat schemas
│   ├── api/                    # API routers
│   │   └── v1/
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── tenants.py     # Tenant management endpoints
│   │       ├── users.py       # User management endpoints
│   │       ├── documents.py   # Document management endpoints
│   │       ├── social.py      # Social links endpoints
│   │       └── chat.py        # Chat endpoints
│   └── utils/                  # Utility functions
│       ├── mock_data.py       # Mock data generator
│       ├── logger.py          # Logging configuration
│       └── exceptions.py      # Custom exceptions
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore file
├── pyproject.toml           # Project configuration and dependencies
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.11 or higher
- uv package manager
- PostgreSQL database (Supabase recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mnfst-rag-backend
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Copy environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` file with your configuration:
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
```

### Running the Application

1. Start the development server:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Access the API:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

### Tenants (Superadmin only)
- `GET /api/v1/tenants` - Get all tenants
- `POST /api/v1/tenants` - Create tenant
- `GET /api/v1/tenants/{tenant_id}` - Get tenant by ID
- `PUT /api/v1/tenants/{tenant_id}` - Update tenant
- `DELETE /api/v1/tenants/{tenant_id}` - Delete tenant

### Users (Tenant admin only)
- `GET /api/v1/users` - Get users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Documents (Tenant admin only)
- `GET /api/v1/documents` - Get documents
- `POST /api/v1/documents/presigned-url` - Get presigned upload URL
- `POST /api/v1/documents/register-upload` - Register uploaded document
- `GET /api/v1/documents/upload/{upload_id}/status` - Get upload status
- `DELETE /api/v1/documents/{document_id}` - Delete document

### Social Links (Tenant admin only)
- `GET /api/v1/social-links` - Get social links
- `POST /api/v1/social-links` - Add social link
- `DELETE /api/v1/social-links/{link_id}` - Delete social link

### Chat (Authenticated users)
- `GET /api/v1/sessions` - Get chat sessions
- `POST /api/v1/sessions` - Create chat session
- `DELETE /api/v1/sessions/{session_id}` - Delete chat session
- `GET /api/v1/sessions/{session_id}/messages` - Get chat messages
- `POST /api/v1/sessions/{session_id}/messages` - Send message
- `POST /api/v1/sessions/{session_id}/messages/stream` - Send message with streaming

## Development

### Mock Data

The application includes a mock data generator for testing and development:

```python
from app.utils.mock_data import MockDataGenerator

# Generate mock users
users = MockDataGenerator.generate_users(count=5, role="user")

# Generate mock documents
documents = MockDataGenerator.generate_documents(count=10)

# Generate mock chat sessions
sessions = MockDataGenerator.generate_sessions(count=3)
```

### Logging

The application uses structured logging with configurable levels:

```python
from app.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(level="DEBUG")

# Get logger
logger = get_logger(__name__)
logger.info("Application started")
```

## Current Status

This is a **scaffold** implementation with:

- ✅ Complete project structure
- ✅ All API endpoints with placeholder implementations
- ✅ Data models based on OpenAPI specification
- ✅ Mock data generation
- ✅ Basic error handling
- ✅ Logging configuration
- ✅ CORS middleware
- ⏳ Placeholder authentication (no real JWT logic)
- ⏳ Placeholder database operations (no real persistence)
- ⏳ No real RAG processing
- ⏳ No real file upload handling

## Next Steps

To complete the implementation:

1. **Implement real authentication** with JWT tokens
2. **Add database operations** with SQLModel
3. **Implement file upload** with Cloudflare R2
4. **Add RAG processing** for documents
5. **Implement streaming** for chat responses
6. **Add comprehensive tests**
7. **Add input validation**
8. **Implement rate limiting**
9. **Add monitoring and metrics**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.