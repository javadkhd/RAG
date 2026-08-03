from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BaseTool(Protocol):
    name: str
    description: str

    async def run(self, **kwargs: Any) -> str:
        ...
