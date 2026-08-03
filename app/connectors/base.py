from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
from uuid import UUID


class BaseConnector(ABC):
    @abstractmethod
    async def load(self, path: str, dataset_id: UUID, workspace_id: UUID) -> list[dict[str, Any]]:
        """Load documents from the given path.

        Returns a list of document dicts with at least:
        - text: str
        - source: str
        - filename: str
        - metadata: dict
        """
