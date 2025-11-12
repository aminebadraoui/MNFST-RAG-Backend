# Tenant Creation Refactor: Cleaner Architecture

## Overview

This document describes the refactoring of the tenant creation process to address tight coupling and transaction management issues.

## Problem Statement

The original implementation had several issues:

1. **Tight Coupling**: `TenantService.create_tenant_with_admin()` directly called `auth_service.create_user_with_password()`
2. **Split Transaction Management**: Tenant service didn't commit because auth service handled its own commit
3. **Mixed Responsibilities**: Tenant creation logic was spread across two services
4. **Potential Data Inconsistency**: If user creation failed after tenant creation, there was no automatic cleanup

## Solution: Unit of Work Pattern

We implemented a Unit of Work pattern with a dedicated coordinator service that manages the entire transaction.

### New Architecture Components

#### 1. BaseService (`app/services/base.py`)
```python
class BaseService(ABC):
    """Base service with session management"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or next(get_session())
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
```

#### 2. UserService (`app/services/user.py`)
Extracted user creation logic from auth service:
- `create_user()`: Creates user without transaction management
- `get_user_by_id()`: Retrieves user by ID
- `get_user_by_email()`: Retrieves user by email

#### 3. Refactored TenantService (`app/services/tenant.py`)
Removed transaction management and coupling:
- `create_tenant()`: Creates tenant without transaction management
- Other methods updated to use instance methods instead of static methods

#### 4. TenantCreationService (`app/services/tenant_creation.py`)
New coordinator service that manages the entire transaction:
```python
@staticmethod
def create_tenant_with_admin(tenant_data: TenantCreate) -> Tuple[Tenant, User]:
    """Create a new tenant with an admin user in a single transaction"""
    session = next(get_session())
    
    try:
        # Create tenant
        with TenantService(session) as tenant_service:
            tenant = tenant_service.create_tenant(
                name=tenant_data.name,
                slug=tenant_data.slug
            )
            
            # Create admin user using the same session
            user_service = UserService(session)
            admin_user = user_service.create_user(
                email=tenant_data.admin_email,
                password=tenant_data.admin_password,
                name=tenant_data.admin_name,
                role=UserRole.TENANT_ADMIN,
                tenant_id=str(tenant.id)
            )
            
            return tenant, admin_user
            
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
```

## Benefits

### Immediate Benefits
1. **Single Transaction Management**: Eliminates split transactions between services
2. **Reduced Coupling**: Tenant service no longer directly depends on auth service
3. **Improved Error Handling**: Centralized error handling with proper rollback
4. **Cleaner Code Organization**: Each service has a single responsibility

### Long-term Benefits
1. **Scalability**: Easy to add more operations to the tenant creation flow
2. **Testability**: Each service can be unit tested in isolation
3. **Maintainability**: Changes to user creation don't affect tenant service
4. **Flexibility**: Can easily switch to different transaction management strategies

## Usage Examples

### Creating a Tenant with Admin
```python
from app.services.tenant_creation import tenant_creation_service
from app.schemas.tenant import TenantCreate

tenant_data = TenantCreate(
    name="My Company",
    slug="my-company",
    admin_email="admin@mycompany.com",
    admin_name="Admin User",
    admin_password="SecurePassword123"
)

tenant, admin_user = tenant_creation_service.create_tenant_with_admin(tenant_data)
```

### Using Individual Services
```python
from app.services.tenant import tenant_service
from app.services.user import user_service

# Using context managers for automatic transaction management
with tenant_service as ts:
    tenant = ts.create_tenant(name="Test", slug="test")
    
with user_service as us:
    user = us.create_user(
        email="user@test.com",
        password="password123",
        name="Test User",
        role=UserRole.USER,
        tenant_id=str(tenant.id)
    )
```

## Migration Strategy

The refactoring was done in phases:

1. **Phase 1**: Created new services alongside existing ones
2. **Phase 2**: Updated API endpoints to use new services
3. **Phase 3**: Refactored existing services to use new patterns
4. **Phase 4**: Added comprehensive tests

## Testing

Run the test script to verify the implementation:

```bash
cd mnfst-rag-backend
python test_tenant_creation.py
```

## Key Implementation Details

### Transaction Management
- The `TenantCreationService` handles the entire transaction manually
- Individual services (`TenantService`, `UserService`) use `flush()` instead of `commit()`
- The coordinator service manages `commit()` and `rollback()`

### Backward Compatibility
- Global service instances (`tenant_service`) use static methods internally
- Existing API endpoints continue to work without changes
- Static methods handle their own session management

### Error Handling
- All database operations are wrapped in try-catch blocks
- Automatic rollback on any exception
- Proper session cleanup in `finally` blocks

## Future Enhancements

This architecture sets up the foundation for:

1. **Event-Driven Architecture**: Can easily emit events after successful tenant creation
2. **Domain-Driven Design**: Can evolve to full DDD with aggregate roots
3. **Repository Pattern**: Can add repository layer for more complex queries
4. **Caching**: Can add caching at the service level
5. **Async Processing**: Can easily make operations asynchronous

## Backward Compatibility

The refactoring maintains backward compatibility by:
- Keeping the same API endpoints
- Preserving the same response formats
- Maintaining the same error handling behavior
- Keeping the global service instances for existing code

## Conclusion

This refactoring provides a cleaner, more maintainable architecture that addresses the original coupling and transaction management issues while setting up a foundation for future enhancements.