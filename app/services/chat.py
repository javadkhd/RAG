from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.base import Conversation, Message
from app.providers.llm.base import LLMProvider
from app.retrieval.base import Reranker, Retriever
from app.retrieval.pipeline import RetrievalPipeline


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        llm_provider: LLMProvider,
        retriever: Retriever,
        reranker: Reranker | None = None,
    ) -> None:
        self.session = session
        self.llm_provider = llm_provider
        self.pipeline = RetrievalPipeline(
            retriever=retriever,
            reranker=reranker,
            top_k=settings.retrieval.top_k,
            rerank_top_k=settings.retrieval.rerank_top_k,
            similarity_threshold=settings.retrieval.similarity_threshold,
        )

    async def chat(self, payload: Any) -> Any:
        from app.api.schemas.chat import ChatRequest, ChatResponse

        if isinstance(payload, dict):
            request = ChatRequest(**payload)
        else:
            request = payload

        conversation = await self._get_or_create_conversation(
            conversation_id=request.conversation_id,
            workspace_id=request.workspace_id,
        )

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )
        self.session.add(user_message)
        await self.session.flush()

        results = await self.pipeline.retrieve(
            query=request.message,
            filters={
                "workspace_id": str(request.workspace_id),
                "dataset_id": str(request.dataset_id),
            },
        )

        context = self._build_context(results)
        prompt = self._build_prompt(request.message, context)

        answer = await self.llm_provider.generate(prompt)

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            sources={
                "sources": [
                    {
                        "chunk_id": r["chunk_id"],
                        "text": r["text"][:200],
                        "score": r["score"],
                    }
                    for r in results[:5]
                ]
            },
        )
        self.session.add(assistant_message)
        await self.session.commit()
        await self.session.refresh(assistant_message)

        sources = (
            assistant_message.sources.get("sources", [])
            if assistant_message.sources
            else []
        )

        return ChatResponse(
            answer=answer,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            sources=sources,
        )

    async def _get_or_create_conversation(
        self,
        conversation_id: UUID | None,
        workspace_id: UUID,
    ) -> Conversation:
        if conversation_id:
            result = await self.session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        conversation = Conversation(
            workspace_id=workspace_id,
            title=None,
        )
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    @staticmethod
    def _build_context(results: list[dict[str, Any]]) -> str:
        if not results:
            return "No relevant context found."
        parts = []
        for i, r in enumerate(results, start=1):
            parts.append(f"[{i}] {r['text']}")
        return "\n\n".join(parts)

    @staticmethod
    def _build_prompt(query: str, context: str) -> str:
        prompt = (
            """
You are a retrieval-augmented question answering assistant.

Answer the user's question using ONLY the information in the provided context.

Rules:
- Do not use outside knowledge.
- If the answer is not present in the context, say "I don't know based on the provided context."
- Do not guess.
- Give a concise answer.

"""
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
        return prompt
