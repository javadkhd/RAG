from typing import Any

from app.agent.context import AgentContext
from app.agent.memory import AgentMemory
from app.providers.llm.base import LLMProvider
from app.retrieval.pipeline import RetrievalPipeline


class AgentExecutor:
    def __init__(
        self,
        llm: LLMProvider,
        retriever: RetrievalPipeline,
        memory: AgentMemory,
    ) -> None:
        self.llm = llm
        self.retriever = retriever
        self.memory = memory

    async def execute(self, context: AgentContext, steps: list[dict[str, Any]]) -> str:
        tool_map = {tool.name: tool for tool in context.tools}
        final_answer = ""

        for step in steps:
            step_type = step.get("type")

            if step_type == "retrieve":
                query = step.get("query", "")
                filters = {"workspace_id": str(context.workspace_id)}
                if context.dataset_id:
                    filters["dataset_id"] = str(context.dataset_id)
                results = await self.retriever.retrieve(query=query, filters=filters)
                self.memory.add_retrieved(results)

            elif step_type == "tool":
                tool_name = step.get("name")
                tool_input = step.get("input", {})
                tool = tool_map.get(tool_name)
                if tool:
                    result = await tool.run(**tool_input)
                    self.memory.add_tool_result(tool_name, result)

            elif step_type == "generate":
                prompt = step.get("prompt", "")
                context_text = self.memory.build_prompt_context()
                full_prompt = f"Context:\n{context_text}\n\nQuestion: {prompt}\nAnswer:"
                final_answer = await self.llm.generate(full_prompt)
                self.memory.add_message("assistant", final_answer)

        return final_answer or "No answer generated."
