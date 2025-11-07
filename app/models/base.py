"""
Base SQLModel class
"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4


class BaseSQLModel(SQLModel):
    """Base model with common fields"""
    
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Last update timestamp"
    )