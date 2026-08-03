from datetime import datetime
from typing import Any
from uuid import UUID

from app.agent.context import AgentContext


class AgentMemory:
    def __init__(self, context: AgentContext) -> None:
        self.context = context
        self.history: list[dict[str, Any]] = []
        self.retrieved_chunks: list[dict[str, Any]] = []
        self.tool_results: list[dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content, "at": datetime.utcnow().isoformat()})

    def add_retrieved(self, chunks: list[dict[str, Any]]) -> None:
        self.retrieved_chunks.extend(chunks)

    def add_tool_result(self, tool: str, result: str) -> None:
        self.tool_results.append({"tool": tool, "result": result, "at": datetime.utcnow().isoformat()})

    def build_prompt_context(self) -> str:
        parts: list[str] = []
        if self.retrieved_chunks:
            parts.append("Retrieved knowledge:")
            for i, chunk in enumerate(self.retrieved_chunks[:5], start=1):
                parts.append(f"[{i}] {chunk.get('text', '')}")
        if self.tool_results:
            parts.append("Tool results:")
            for item in self.tool_results[-5:]:
                parts.append(f"- {item['tool']}: {item['result']}")
        return "\n\n".join(parts) if parts else "No additional context."
