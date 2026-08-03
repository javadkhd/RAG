from typing import Any

from app.tools.base import BaseTool


class PostgresTool:
    name = "postgres"
    description = "Execute read-only SQL queries against PostgreSQL."

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    async def run(self, query: str, **kwargs: Any) -> str:
        import asyncpg

        conn = await asyncpg.connect(self.connection_string)
        try:
            rows = await conn.fetch(query)
            return "\n".join(str(dict(row)) for row in rows)
        finally:
            await conn.close()
