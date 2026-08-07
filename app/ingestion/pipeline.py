from dataclasses import dataclass, field

from app.connectors.base import BaseConnector
from app.ingestion.indexer import Indexer


@dataclass
class IngestionResult:
    documents_loaded: int = 0
    chunks_created: int = 0
    embeddings_generated: int = 0
    errors: list[str] = field(default_factory=list)


class IngestionPipeline:
    def __init__(self, session, connector: BaseConnector, embedder=None) -> None:
        self.session = session
        self.connector = connector
        self.embedder = embedder

    async def run(self, path: str, dataset_id, workspace_id) -> IngestionResult:
        result = IngestionResult()

        documents = await self.connector.load(path, dataset_id, workspace_id)
        result.documents_loaded = len(documents)

        indexer = Indexer(self.session, provider=self.embedder)
        index_result = await indexer.index(documents, dataset_id, workspace_id)

        result.chunks_created = index_result["chunks_created"]
        result.embeddings_generated = index_result["embeddings_generated"]

        return result
