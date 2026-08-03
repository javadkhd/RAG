from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    workspace_id: UUID
    dataset_id: UUID
    message: str = Field(..., min_length=1)
    conversation_id: Optional[UUID] = None
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    answer: str
    conversation_id: UUID
    message_id: UUID
    sources: list[dict[str, Any]] = []


class ChatStreamEvent(BaseModel):
    event: str
    data: str


class ConversationCreate(BaseModel):
    workspace_id: UUID
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: Optional[dict] = None
    created_at: datetime
