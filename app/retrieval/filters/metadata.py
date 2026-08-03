from typing import Any

from app.models.base import Chunk


def apply_filters(query, filters: dict[str, Any] | None = None):
    if not filters:
        return query
    if "workspace_id" in filters:
        query = query.where(Chunk.workspace_id == filters["workspace_id"])
    if "dataset_id" in filters:
        query = query.where(Chunk.dataset_id == filters["dataset_id"])
    return query
