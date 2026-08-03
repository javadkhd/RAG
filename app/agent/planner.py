import json
from typing import Any

from app.agent.context import AgentContext
from app.agent.prompts import PLANNER_PROMPT
from app.providers.llm.base import LLMProvider


class AgentPlanner:
    def __init__(self, llm: LLMProvider) -> None:
        self.llm = llm

    async def plan(self, context: AgentContext, query: str) -> list[dict[str, Any]]:
        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" for tool in context.tools
        )
        prompt = PLANNER_PROMPT.format(tools=tool_descriptions, query=query)
        response = await self.llm.generate(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"type": "generate", "prompt": query}]
