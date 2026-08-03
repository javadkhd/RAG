from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Retriever(Protocol):
    async def search(self, query: str, top_k: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...


@runtime_checkable
class Reranker(Protocol):
    async def rerank(self, query: str, results: list[dict[str, Any]], top_k: int = 10) -> list[dict[str, Any]]: ...
