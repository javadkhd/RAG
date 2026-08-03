from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class DatasetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    connector_type: Optional[str] = Field(None, max_length=100)
    connector_config: Optional[dict[str, Any]] = None
    extra_metadata: Optional[dict[str, Any]] = None


class DatasetCreate(DatasetBase):
    workspace_id: UUID


class DatasetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    connector_type: Optional[str] = Field(None, max_length=100)
    connector_config: Optional[dict[str, Any]] = None
    extra_metadata: Optional[dict[str, Any]] = None


class DatasetResponse(DatasetBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime


class DatasetList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    name: str
    description: Optional[str] = None
    connector_type: Optional[str] = None
    created_at: datetime
