from collections.abc import AsyncIterator, Sequence
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    async def generate(self, prompt: str, **kwargs) -> str: ...
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncIterator[str]: ...
