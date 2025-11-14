# API Overview

## Introduction

The MNFST-RAG Backend provides a comprehensive RESTful API for multi-tenant RAG (Retrieval-Augmented Generation) applications. The API follows REST principles and uses JSON for data exchange. All endpoints are designed to be stateless and support multi-tenancy with role-based access control.

## Base URL

```
Production: https://api.mnfst-rag.com
Development: http://localhost:8000
```

## API Versioning

The API uses URL path versioning:

```
/api/v1/ - Current version
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Types

1. **Access Token**: Short-lived (1 hour) for API requests
2. **Refresh Token**: Long-lived (30 days) for obtaining new access tokens

## Request/Response Format

### Request Headers

```http
Content-Type: application/json
Authorization: Bearer <access_token>
X-Tenant-ID: <tenant_id> (optional, for superadmin operations)
```

### Response Format

All API responses follow a consistent format:

#### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  }
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no content to return |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required or failed |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | User logout |
| GET | `/api/v1/auth/me` | Get current user info |

### Tenants (Superadmin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tenants` | List all tenants |
| POST | `/api/v1/tenants` | Create new tenant |
| GET | `/api/v1/tenants/{tenantId}` | Get tenant details |
| PUT | `/api/v1/tenants/{tenantId}` | Update tenant |
| DELETE | `/api/v1/tenants/{tenantId}` | Delete tenant |

### Users (Tenant admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List users (tenant-scoped) |
| POST | `/api/v1/users` | Create new user |
| GET | `/api/v1/users/{userId}` | Get user details |
| PUT | `/api/v1/users/{userId}` | Update user |
| DELETE | `/api/v1/users/{userId}` | Delete user |

### Documents (Tenant admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/documents` | List documents (tenant-scoped) |
| POST | `/api/v1/documents/presigned-url` | Get presigned upload URL |
| POST | `/api/v1/documents/register-upload` | Register uploaded document |
| GET | `/api/v1/documents/upload/{uploadId}/status` | Get upload status |
| DELETE | `/api/v1/documents/{documentId}` | Delete document |

### Social Links (Tenant admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/social-links` | List social links (tenant-scoped) |
| POST | `/api/v1/social-links` | Add social link |
| DELETE | `/api/v1/social-links/{linkId}` | Delete social link |

### Chat (Authenticated users)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/sessions` | List chat sessions (user-scoped) |
| POST | `/api/v1/sessions` | Create chat session |
| DELETE | `/api/v1/sessions/{sessionId}` | Delete chat session |
| GET | `/api/v1/sessions/{sessionId}/messages` | Get chat messages |
| POST | `/api/v1/sessions/{sessionId}/messages` | Send message |
| POST | `/api/v1/sessions/{sessionId}/messages/stream` | Send message with streaming |

## Multi-Tenancy

### Tenant Context

All tenant-specific operations automatically filter by the authenticated user's tenant. Superadmins can access any tenant's data by providing the `X-Tenant-ID` header.

### Example Request

```http
GET /api/v1/users
Authorization: Bearer <access_token>
X-Tenant-ID: 123e4567-e89b-12d3-a456-426614174000
```

## Role-Based Access Control

### User Roles

1. **Superadmin**: System-wide access to all resources
2. **Tenant Admin**: Tenant-wide access to users, documents, and settings
3. **User**: Personal access to documents and chat functionality

### Access Matrix

| Resource | Superadmin | Tenant Admin | User |
|----------|-------------|--------------|------|
| Tenants | CRUD | - | - |
| Users | CRUD | CRUD (tenant) | Read (self) |
| Documents | CRUD | CRUD (tenant) | CRUD (own) |
| Social Links | CRUD | CRUD (tenant) | Read |
| Chat Sessions | CRUD | Read (tenant) | CRUD (own) |

## Pagination

List endpoints support pagination using query parameters:

```
GET /api/v1/users?page=1&limit=20&sort=created_at&order=desc
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number (1-based) |
| limit | integer | 20 | Items per page (max 100) |
| sort | string | created_at | Sort field |
| order | string | desc | Sort order (asc/desc) |

### Response

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## Filtering and Search

### Filtering

Many endpoints support filtering by specific fields:

```
GET /api/v1/documents?status=processed&mime_type=application/pdf
```

### Search

Text search is available on searchable fields:

```
GET /api/v1/documents?search=report
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Anonymous requests**: 10 requests per minute
- **Authenticated requests**: 1000 requests per hour
- **Upload requests**: 10 uploads per minute

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Error Codes

| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Request validation failed |
| UNAUTHORIZED | Authentication required |
| FORBIDDEN | Insufficient permissions |
| NOT_FOUND | Resource not found |
| CONFLICT | Resource conflict |
| RATE_LIMIT_EXCEEDED | Rate limit exceeded |
| INTERNAL_ERROR | Internal server error |

### Error Response Example

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

## File Uploads

### Upload Flow

1. **Get Presigned URL**: Request a presigned URL for direct upload
2. **Upload File**: Upload file directly to storage (Cloudflare R2)
3. **Register Upload**: Register the uploaded file with the system

### Example

```bash
# 1. Get presigned URL
curl -X POST "http://localhost:8000/api/v1/documents/presigned-url" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf"
  }'

# 2. Upload file to R2 (using presigned URL)
curl -X PUT "<presigned_url>" \
  -H "Content-Type: application/pdf" \
  --data-binary @document.pdf

# 3. Register upload
curl -X POST "http://localhost:8000/api/v1/documents/register-upload" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "<document_id>",
    "file_name": "document.pdf",
    "file_key": "<file_key>",
    "public_url": "<public_url>",
    "file_size": 1024000,
    "mime_type": "application/pdf"
  }'
```

## Streaming Responses

Chat endpoints support streaming responses for real-time AI responses:

```javascript
const response = await fetch('/api/v1/sessions/session-id/messages/stream', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: 'Hello, AI!',
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  console.log(chunk); // Stream chunk
}
```

## OpenAPI Documentation

Interactive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## SDKs and Client Libraries

### Official SDKs

- **Python**: `pip install mnfst-rag-python`
- **JavaScript/TypeScript**: `npm install @mnfst-rag/js`
- **cURL**: Examples provided in documentation

### Community SDKs

- **Ruby**: Available on GitHub
- **Java**: Available on Maven Central
- **Go**: Available on Go Modules

## Webhooks (Planned)

Webhooks allow your application to receive real-time notifications about events:

### Supported Events

- `user.created` - New user created
- `document.uploaded` - Document uploaded
- `document.processed` - Document processing completed
- `chat.message.created` - New chat message

### Configuration

```bash
curl -X POST "http://localhost:8000/api/v1/webhooks" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks",
    "events": ["document.processed", "user.created"],
    "secret": "webhook-secret"
  }'
```

## API Changelog

### v1.0.0 (Current)
- Initial API release
- Authentication and authorization
- Multi-tenant support
- Document management
- Chat functionality
- Social links management

### Upcoming Features
- Webhooks support
- Advanced search capabilities
- Bulk operations
- API analytics
- Custom integrations

## Support

- **Documentation**: https://docs.mnfst-rag.com
- **API Reference**: https://api.mnfst-rag.com/docs
- **Support Email**: api-support@mnfst-rag.com
- **Status Page**: https://status.mnfst-rag.com
- **GitHub Issues**: https://github.com/mnfst-rag/backend/issues