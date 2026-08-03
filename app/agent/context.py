from typing import Any
from uuid import UUID

from app.models.base import Workspace, Dataset, Conversation, Message


class AgentContext:
    def __init__(
        self,
        workspace_id: UUID,
        dataset_id: UUID | None = None,
        conversation_id: UUID | None = None,
        tools: list[Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.workspace_id = workspace_id
        self.dataset_id = dataset_id
        self.conversation_id = conversation_id
        self.tools = tools or []
        self.metadata = metadata or {}
