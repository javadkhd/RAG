import httpx
from typing import Any

from app.tools.base import BaseTool


class SearchTool:
    name = "search"
    description = "Search the web for information."

    def __init__(self, api_key: str, engine_id: str) -> None:
        self.api_key = api_key
        self.engine_id = engine_id

    async def run(self, query: str, **kwargs: Any) -> str:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.engine_id,
            "q": query,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        items = data.get("items", [])
        results = []
        for item in items[:5]:
            results.append(f"- {item.get('title')}: {item.get('snippet')}")
        return "\n".join(results) if results else "No results found."
