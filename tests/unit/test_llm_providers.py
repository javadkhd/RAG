import asyncio
import json
import sys
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.providers.llm.base import LLMProvider
from app.providers.llm.ollama import OllamaLLMProvider

if "openai" not in sys.modules:
    sys.modules["openai"] = MagicMock()
if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = MagicMock()
if "google" not in sys.modules:
    sys.modules["google"] = MagicMock()
if "google.generativeai" not in sys.modules:
    sys.modules["google.generativeai"] = MagicMock()

from app.providers.llm.openai import OpenAILLMProvider  # noqa: E402
from app.providers.llm.anthropic import AnthropicLLMProvider  # noqa: E402
from app.providers.llm.gemini import GeminiLLMProvider  # noqa: E402
from app.providers.llm import get_llm_provider  # noqa: E402


class TestOllamaLLMProvider:
    @pytest.mark.asyncio
    async def test_generate(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello from Ollama"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response

        with patch("app.providers.llm.ollama.httpx.AsyncClient", return_value=mock_client):
            provider = OllamaLLMProvider(model="qwen2.5:0.5b")
            result = await provider.generate("Hi")

        assert result == "Hello from Ollama"
        mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_stream(self):
        mock_client = MagicMock()

        async def make_aiter_lines():
            for chunk in ["first", "second", "third"]:
                yield json.dumps({"response": chunk})

        mock_stream = MagicMock()
        mock_stream.aiter_lines = MagicMock(return_value=make_aiter_lines())
        mock_stream.raise_for_status = MagicMock()

        class MockStreamContext:
            async def __aenter__(self):
                return mock_stream

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        mock_client.stream.return_value = MockStreamContext()

        class MockClientContext:
            async def __aenter__(self):
                return mock_client

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        with patch("app.providers.llm.ollama.httpx.AsyncClient", return_value=MockClientContext()):
            provider = OllamaLLMProvider(model="qwen2.5:0.5b")
            chunks = []
            async for chunk in provider.generate_stream("Hi"):
                chunks.append(chunk)

        assert chunks == ["first", "second", "third"]


class TestOpenAILLMProvider:
    @pytest.mark.asyncio
    async def test_generate(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from OpenAI"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(sys.modules["openai"], "AsyncOpenAI", return_value=mock_client):
            provider = OpenAILLMProvider(model="gpt-4o", api_key="test-key")
            result = await provider.generate("Hi")

        assert result == "Hello from OpenAI"
        mock_client.chat.completions.create.assert_called_once()


class TestAnthropicLLMProvider:
    @pytest.mark.asyncio
    async def test_generate(self):
        mock_text_block = MagicMock()
        mock_text_block.text = "Hello from Anthropic"

        mock_response = MagicMock()
        mock_response.content = [mock_text_block]

        mock_client = AsyncMock()
        mock_client.messages.create.return_value = mock_response

        with patch.object(sys.modules["anthropic"], "AsyncAnthropic", return_value=mock_client):
            provider = AnthropicLLMProvider(model="claude-3-5-sonnet-20241022", api_key="test-key")
            result = await provider.generate("Hi")

        assert result == "Hello from Anthropic"
        mock_client.messages.create.assert_called_once()


class TestGeminiLLMProvider:
    @pytest.mark.asyncio
    async def test_generate(self):
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = MagicMock()

        with patch.dict(sys.modules, {"google.generativeai": mock_genai}):
            provider = GeminiLLMProvider(model="gemini-pro", api_key="test-key")
            with patch.object(provider, "generate", return_value="Hello from Gemini"):
                result = await provider.generate("Hi")

        assert result == "Hello from Gemini"


class TestLLMProviderProtocol:
    def test_ollama_satisfies_protocol(self):
        provider = OllamaLLMProvider(model="qwen2.5:0.5b")
        assert isinstance(provider, LLMProvider)

    def test_openai_satisfies_protocol(self):
        with patch.object(sys.modules["openai"], "AsyncOpenAI", return_value=AsyncMock()):
            provider = OpenAILLMProvider(model="gpt-4o", api_key="test")
        assert isinstance(provider, LLMProvider)


class TestGetLLMProvider:
    def test_get_ollama_provider(self):
        with patch("app.providers.llm.settings.llm.provider", "ollama"):
            provider = get_llm_provider()
        assert isinstance(provider, OllamaLLMProvider)

    def test_get_unknown_provider(self):
        with patch("app.providers.llm.settings.llm.provider", "unknown"):
            with pytest.raises(ValueError):
                get_llm_provider()
