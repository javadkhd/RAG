import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.connectors.markdown.loader import MarkdownConnector
from app.connectors.postgres.loader import PostgresConnector, PostgresInspector
from app.ingestion.cleaner import clean
from app.ingestion.splitter import split


class TestMarkdownConnector:
    @pytest.fixture
    def tmp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "doc1.md").write_text("# Hello\n\nWorld", encoding="utf-8")
            (root / "sub").mkdir()
            (root / "sub" / "doc2.md").write_text("---\ntitle: Test\n---\nBody text", encoding="utf-8")
            yield root

    @pytest.mark.asyncio
    async def test_load_markdown_files(self, tmp_dir):
        connector = MarkdownConnector()
        docs = await connector.load(str(tmp_dir), dataset_id="00000000-0000-0000-0000-000000000000", workspace_id="00000000-0000-0000-0000-000000000000")
        assert len(docs) == 2
        filenames = {d["filename"] for d in docs}
        assert filenames == {"doc1.md", "doc2.md"}

    @pytest.mark.asyncio
    async def test_frontmatter_parsing(self, tmp_dir):
        connector = MarkdownConnector()
        docs = await connector.load(str(tmp_dir), dataset_id="00000000-0000-0000-0000-000000000000", workspace_id="00000000-0000-0000-0000-000000000000")
        doc2 = next(d for d in docs if d["filename"] == "doc2.md")
        assert doc2["metadata"]["frontmatter"] == {"title": "Test"}

    @pytest.mark.asyncio
    async def test_missing_path(self):
        connector = MarkdownConnector()
        with pytest.raises(FileNotFoundError):
            await connector.load("/nonexistent/path", dataset_id="00000000-0000-0000-0000-000000000000", workspace_id="00000000-0000-0000-0000-000000000000")


class TestCleaner:
    def test_clean_whitespace(self):
        assert clean("Hello   world\n\n\n\nFoo") == "Hello world\n\nFoo"

    def test_clean_carriage_return(self):
        assert clean("Hello\r\nworld") == "Hello\nworld"


class TestSplitter:
    def test_split_basic(self):
        text = " ".join(str(i) for i in range(20))
        chunks = split(text, chunk_size=5, overlap=2)
        assert len(chunks) > 1
        assert chunks[0].count(" ") == 4

    def test_split_empty(self):
        assert split("") == []

    def test_split_short_text(self):
        assert split("hello world", chunk_size=10, overlap=2) == ["hello world"]


class TestPostgresInspector:
    @pytest.mark.asyncio
    async def test_get_tables(self):
        engine = MagicMock()
        connection = AsyncMock()
        result = AsyncMock()
        result.fetchall.return_value = [("users",), ("posts",)]
        connection.execute.return_value = result
        engine.connect.return_value.__aenter__.return_value = connection

        inspector = PostgresInspector(engine=engine)
        tables = await inspector.get_tables()
        assert tables == ["users", "posts"]

    @pytest.mark.asyncio
    async def test_get_columns(self):
        engine = MagicMock()
        connection = AsyncMock()
        result = AsyncMock()
        result.fetchall.return_value = [("id",), ("name",), ("email",)]
        connection.execute.return_value = result
        engine.connect.return_value.__aenter__.return_value = connection

        inspector = PostgresInspector(engine=engine)
        columns = await inspector.get_columns("users")
        assert columns == ["id", "name", "email"]


class TestPostgresConnector:
    @pytest.mark.asyncio
    async def test_load_documents(self):
        engine = MagicMock()
        connection = AsyncMock()
        result = AsyncMock()

        result.fetchall.side_effect = [
            [("users",)],
            [("id",), ("name",)],
            [(1, "Alice"), (2, "Bob")],
        ]
        connection.execute.return_value = result
        engine.connect.return_value.__aenter__.return_value = connection
        engine.dispose = AsyncMock()

        with patch("app.connectors.postgres.loader.create_async_engine", return_value=engine):
            connector = PostgresConnector()
            docs = await connector.load("postgresql://localhost/test", dataset_id="00000000-0000-0000-0000-000000000000", workspace_id="00000000-0000-0000-0000-000000000000")

        assert len(docs) == 2
        assert docs[0]["text"] == "Table: users\n- id: 1\n- name: Alice"
        assert docs[0]["metadata"]["table"] == "users"
        assert docs[0]["metadata"]["row_index"] == 0

    @pytest.mark.asyncio
    async def test_load_with_table_filter(self):
        engine = MagicMock()
        connection = AsyncMock()
        result = AsyncMock()
        result.fetchall.side_effect = [
            [("id",), ("name",)],
            [(1, "Alice")],
        ]
        connection.execute.return_value = result
        engine.connect.return_value.__aenter__.return_value = connection
        engine.dispose = AsyncMock()

        with patch("app.connectors.postgres.loader.create_async_engine", return_value=engine):
            connector = PostgresConnector(tables=["users"])
            docs = await connector.load("postgresql://localhost/test", dataset_id="00000000-0000-0000-0000-000000000000", workspace_id="00000000-0000-0000-0000-000000000000")

        assert len(docs) == 1
        assert docs[0]["metadata"]["table"] == "users"

    @pytest.mark.asyncio
    async def test_row_to_text(self):
        text = PostgresConnector._row_to_text("users", ["id", "name"], (1, "Alice"))
        assert text == "Table: users\n- id: 1\n- name: Alice"