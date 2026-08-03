from typing import Any

from app.agent.context import AgentContext
from app.agent.executor import AgentExecutor
from app.agent.memory import AgentMemory
from app.agent.planner import AgentPlanner
from app.providers.llm.base import LLMProvider
from app.retrieval.pipeline import RetrievalPipeline


class AgentOrchestrator:
    def __init__(
        self,
        llm: LLMProvider,
        retriever: RetrievalPipeline,
        tools: list[Any] | None = None,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.planner = AgentPlanner(llm)
        self.tools = tools or []

    async def run(self, context: AgentContext, query: str) -> str:
        context.tools = self.tools
        memory = AgentMemory(context)
        memory.add_message("user", query)

        steps = await self.planner.plan(context, query)
        executor = AgentExecutor(self.llm, self.retriever, memory)
        answer = await executor.execute(context, steps)

        return answer
