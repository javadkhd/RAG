from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.connectors.base import BaseConnector


@dataclass
class PostgresInspector:
    engine: Any

    async def get_tables(self, schema: str = "public") -> list[str]:
        query = text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = :schema AND table_type = 'BASE TABLE'"
        )
        async with self.engine.connect() as conn:
            result = await conn.execute(query, {"schema": schema})
            rows = await result.fetchall()
            return [row[0] for row in rows]

    async def get_columns(self, table: str, schema: str = "public") -> list[str]:
        query = text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table ORDER BY ordinal_position"
        )
        async with self.engine.connect() as conn:
            result = await conn.execute(query, {"schema": schema, "table": table})
            rows = await result.fetchall()
            return [row[0] for row in rows]


class PostgresConnector(BaseConnector):
    def __init__(self, schema: str = "public", tables: list[str] | None = None) -> None:
        self.schema = schema
        self.tables = tables
        self.inspector: PostgresInspector | None = None

    async def load(self, path: str, dataset_id: UUID, workspace_id: UUID) -> list[dict[str, Any]]:
        engine = create_async_engine(path)
        self.inspector = PostgresInspector(engine=engine)

        target_tables = self.tables or await self.inspector.get_tables(self.schema)
        documents: list[dict[str, Any]] = []

        for table in target_tables:
            columns = await self.inspector.get_columns(table, self.schema)
            rows = await self._fetch_rows(engine, table, columns)
            for idx, row in enumerate(rows):
                text_content = self._row_to_text(table, columns, row)
                documents.append(
                    {
                        "text": text_content,
                        "source": f"postgres://{table}",
                        "filename": f"{table}.txt",
                        "metadata": {
                            "table": table,
                            "schema": self.schema,
                            "row_index": idx,
                            "columns": columns,
                        },
                        "dataset_id": dataset_id,
                        "workspace_id": workspace_id,
                    }
                )

        await engine.dispose()
        return documents

    @staticmethod
    async def _fetch_rows(engine, table: str, columns: list[str]) -> list[tuple]:
        col_list = ", ".join(columns)
        query = text(f"SELECT {col_list} FROM {table}")
        async with engine.connect() as conn:
            result = await conn.execute(query)
            rows = await result.fetchall()
            return [tuple(row) for row in rows]

    @staticmethod
    def _row_to_text(table: str, columns: list[str], row: tuple) -> str:
        lines = [f"Table: {table}"]
        for column, value in zip(columns, row):
            lines.append(f"- {column}: {value}")
        return "\n".join(lines)
