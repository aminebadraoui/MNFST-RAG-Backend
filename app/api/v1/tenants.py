"""
Tenant management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends, Response
from typing import Any, List

from app.schemas.tenant import (
    TenantRead,
    TenantCreate,
    TenantUpdate,
    TenantReadWithAdmin
)
from app.schemas.response import DataResponse
from app.services.tenant import TenantService, tenant_service
from app.services.tenant_creation import tenant_creation_service
from app.database import get_session
from app.dependencies.auth import require_superadmin

router = APIRouter()


@router.get("", response_model=DataResponse[List[TenantReadWithAdmin]])
async def get_tenants(
    current_user = Depends(require_superadmin)
) -> Any:
    """
    Get all tenants
    Retrieve all tenants in the system (superadmin only)
    """
    try:
        tenants = tenant_service.get_all_tenants()
        
        # Get stats for each tenant
        tenants_with_stats = []
        for tenant in tenants:
            stats = tenant_service.get_tenant_stats(str(tenant.id))
            # Get admin user for this tenant
            from app.models.user import User, UserRole
            from sqlmodel import select
            
            admin_statement = select(User).where(
                User.tenant_id == tenant.id,
                User.role == UserRole.TENANT_ADMIN
            )
            admin_user = tenant_service.session.exec(admin_statement).first()
            
            tenant_read = TenantReadWithAdmin(
                id=tenant.id,
                name=tenant.name,
                slug=tenant.slug,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
                user_count=stats["user_count"],
                document_count=stats["document_count"],
                admin_user={
                    "id": str(admin_user.id) if admin_user else None,
                    "email": admin_user.email if admin_user else None,
                    "name": admin_user.name if admin_user else None,
                    "role": admin_user.role.value if admin_user else None
                } if admin_user else None
            )
            tenants_with_stats.append(tenant_read)
        
        return DataResponse(
            data=tenants_with_stats,
            message="Tenants retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tenants: {str(e)}"
        )


@router.post("", response_model=DataResponse[TenantReadWithAdmin], status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user = Depends(require_superadmin)
) -> Any:
    """
    Create tenant
    Create a new tenant with admin user (superadmin only)
    """
    try:
        tenant, admin_user = tenant_creation_service.create_tenant_with_admin(tenant_data)
        
        tenant_response = TenantReadWithAdmin(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
            user_count=1,
            document_count=0,
            admin_user={
                "id": str(admin_user.id),
                "email": admin_user.email,
                "name": admin_user.name,
                "role": admin_user.role.value
            }
        )
        
        return DataResponse(
            data=tenant_response,
            message="Tenant created successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}"
        )


@router.get("/{tenantId}", response_model=DataResponse[TenantRead])
async def get_tenant(
    tenantId: str,
    current_user = Depends(require_superadmin)
) -> Any:
    """
    Get tenant by ID
    Retrieve specific tenant information (superadmin only)
    """
    try:
        tenant = tenant_service.get_tenant_by_id(tenantId)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        stats = tenant_service.get_tenant_stats(tenantId)
        
        tenant_response = TenantRead(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
            user_count=stats["user_count"],
            document_count=stats["document_count"]
        )
        
        return DataResponse(
            data=tenant_response,
            message="Tenant retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tenant: {str(e)}"
        )


@router.put("/{tenantId}", response_model=DataResponse[TenantRead])
async def update_tenant(
    tenantId: str,
    tenant_data: TenantUpdate,
    current_user = Depends(require_superadmin)
) -> Any:
    """
    Update tenant
    Update tenant information (superadmin only)
    """
    try:
        tenant = tenant_service.update_tenant(tenantId, tenant_data)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        stats = tenant_service.get_tenant_stats(tenantId)
        
        tenant_response = TenantRead(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
            user_count=stats["user_count"],
            document_count=stats["document_count"]
        )
        
        return DataResponse(
            data=tenant_response,
            message="Tenant updated successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update tenant: {str(e)}"
        )


@router.delete("/{tenantId}")
async def delete_tenant(
    tenantId: str,
    current_user = Depends(require_superadmin)
) -> Any:
    """
    Delete tenant
    Delete a tenant and all associated data (superadmin only)
    """
    try:
        deleted = tenant_service.delete_tenant_cascade(tenantId)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}"
        )