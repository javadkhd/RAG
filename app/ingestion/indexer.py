from collections.abc import Sequence
from typing import Any

from app.models.base import Chunk, Document, Embedding
from app.providers.embeddings.base import EmbeddingProvider


class Indexer:
    def __init__(self, session, provider: EmbeddingProvider | None = None) -> None:
        self.session = session
        self.provider = provider

    async def index(self, documents: list[dict[str, Any]], dataset_id, workspace_id) -> None:
        from app.ingestion.splitter import split
        from app.ingestion.cleaner import clean

        chunk_size = 512
        overlap = 50

        for doc in documents:
            document = Document(
                dataset_id=doc["dataset_id"],
                workspace_id=doc["workspace_id"],
                source=doc["source"],
                filename=doc.get("filename"),
                content_type="text/markdown",
                size_bytes=len(doc["text"].encode("utf-8")),
                extra_metadata=doc.get("metadata"),
                status="processing",
            )
            self.session.add(document)
            await self.session.flush()

            chunks = split(doc["text"], chunk_size=chunk_size, overlap=overlap)
            for idx, chunk_text in enumerate(chunks):
                chunk = Chunk(
                    document_id=document.id,
                    dataset_id=dataset_id,
                    workspace_id=workspace_id,
                    chunk_index=idx,
                    text=chunk_text,
                    token_count=len(chunk_text.split()),
                )
                self.session.add(chunk)
                await self.session.flush()

                if self.provider is not None:
                    vectors = await self.provider.embed([chunk_text])
                    embedding = Embedding(
                        chunk_id=chunk.id,
                        workspace_id=workspace_id,
                        dataset_id=dataset_id,
                        model="placeholder",
                        dimensions=len(vectors[0]) if vectors else 0,
                        vector=vectors[0] if vectors else None,
                    )
                    self.session.add(embedding)

            document.status = "completed"
            await self.session.flush()
