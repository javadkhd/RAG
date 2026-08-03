from unittest.mock import AsyncMock

import pytest

from app.agent.context import AgentContext
from app.agent.executor import AgentExecutor
from app.agent.memory import AgentMemory
from app.agent.orchestrator import AgentOrchestrator
from app.agent.planner import AgentPlanner
from app.tools.base import BaseTool
from app.tools.filesystem import FilesystemTool
from app.tools.shell import ShellTool


class DummyTool:
    name = "dummy"
    description = "Dummy tool for testing"

    async def run(self, **kwargs):
        return "dummy result"


class TestBaseToolProtocol:
    def test_filesystem_satisfies_protocol(self):
        tool = FilesystemTool()
        assert isinstance(tool, BaseTool)

    def test_shell_satisfies_protocol(self):
        tool = ShellTool()
        assert isinstance(tool, BaseTool)

    def test_dummy_satisfies_protocol(self):
        tool = DummyTool()
        assert isinstance(tool, BaseTool)


class TestAgentMemory:
    def test_add_message(self):
        ctx = AgentContext(workspace_id="wid")
        memory = AgentMemory(ctx)
        memory.add_message("user", "hello")
        assert len(memory.history) == 1
        assert memory.history[0]["role"] == "user"

    def test_build_prompt_context_empty(self):
        ctx = AgentContext(workspace_id="wid")
        memory = AgentMemory(ctx)
        assert memory.build_prompt_context() == "No additional context."

    def test_build_prompt_context_with_chunks(self):
        ctx = AgentContext(workspace_id="wid")
        memory = AgentMemory(ctx)
        memory.add_retrieved([{"text": "chunk one"}])
        context = memory.build_prompt_context()
        assert "Retrieved knowledge:" in context
        assert "chunk one" in context


class TestAgentPlanner:
    @pytest.mark.asyncio
    async def test_plan_returns_steps(self):
        llm = AsyncMock()
        llm.generate.return_value = '[{"type": "retrieve", "query": "test"}]'
        planner = AgentPlanner(llm)
        ctx = AgentContext(workspace_id="wid", tools=[DummyTool()])
        steps = await planner.plan(ctx, "test query")
        assert isinstance(steps, list)
        assert steps[0]["type"] == "retrieve"

    @pytest.mark.asyncio
    async def test_plan_fallback_on_bad_json(self):
        llm = AsyncMock()
        llm.generate.return_value = "not json"
        planner = AgentPlanner(llm)
        ctx = AgentContext(workspace_id="wid", tools=[DummyTool()])
        steps = await planner.plan(ctx, "test query")
        assert steps == [{"type": "generate", "prompt": "test query"}]


class TestAgentExecutor:
    @pytest.mark.asyncio
    async def test_execute_retrieve_step(self):
        llm = AsyncMock()
        llm.generate.return_value = "final answer"
        retriever = AsyncMock()
        retriever.retrieve.return_value = [{"text": "chunk"}]
        ctx = AgentContext(workspace_id="wid")
        memory = AgentMemory(ctx)
        executor = AgentExecutor(llm, retriever, memory)

        steps = [
            {"type": "retrieve", "query": "test"},
            {"type": "generate", "prompt": "test"},
        ]
        answer = await executor.execute(ctx, steps)
        assert answer == "final answer"
        assert len(memory.retrieved_chunks) == 1

    @pytest.mark.asyncio
    async def test_execute_tool_step(self):
        llm = AsyncMock()
        llm.generate.return_value = "final answer"
        retriever = AsyncMock()
        retriever.retrieve.return_value = []
        tool = DummyTool()
        ctx = AgentContext(workspace_id="wid", tools=[tool])
        memory = AgentMemory(ctx)
        executor = AgentExecutor(llm, retriever, memory)

        steps = [
            {"type": "tool", "name": "dummy", "input": {}},
            {"type": "generate", "prompt": "test"},
        ]
        answer = await executor.execute(ctx, steps)
        assert answer == "final answer"
        assert memory.tool_results[0]["tool"] == "dummy"


class TestAgentOrchestrator:
    @pytest.mark.asyncio
    async def test_run_end_to_end(self):
        llm = AsyncMock()
        llm.generate.side_effect = [
            '[{"type": "retrieve", "query": "test"}, {"type": "generate", "prompt": "What is RAG?"}]',
            "final answer",
        ]
        retriever = AsyncMock()
        retriever.retrieve.return_value = [{"text": "chunk"}]
        tool = DummyTool()
        orchestrator = AgentOrchestrator(llm, retriever, tools=[tool])
        ctx = AgentContext(workspace_id="wid")

        answer = await orchestrator.run(ctx, "What is RAG?")
        assert answer == "final answer"
        assert len(ctx.tools) == 1
