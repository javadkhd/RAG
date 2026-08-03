import re
from pathlib import Path
from typing import Any, Optional
from uuid import UUID

from app.connectors.base import BaseConnector


class MarkdownConnector(BaseConnector):
    async def load(self, path: str, dataset_id: UUID, workspace_id: UUID) -> list[dict[str, Any]]:
        root = Path(path)
        if not root.exists():
            raise FileNotFoundError(f"Markdown path does not exist: {path}")

        documents = []
        for file_path in sorted(root.rglob("*.md")):
            raw = file_path.read_text(encoding="utf-8")
            frontmatter, body = self._parse_frontmatter(raw)
            rel_path = file_path.relative_to(root).as_posix()

            documents.append({
                "text": body.strip(),
                "source": str(file_path.resolve()),
                "filename": file_path.name,
                "metadata": {
                    "path": rel_path,
                    "directory": str(file_path.parent.relative_to(root).as_posix()),
                    "size_bytes": file_path.stat().st_size,
                    **({"frontmatter": frontmatter} if frontmatter else {}),
                },
                "dataset_id": dataset_id,
                "workspace_id": workspace_id,
            })

        return documents

    @staticmethod
    def _parse_frontmatter(text: str) -> tuple[Optional[dict[str, Any]], str]:
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
        if not match:
            return None, text

        frontmatter_text, body = match.group(1), match.group(2)
        frontmatter: dict[str, Any] = {}
        for line in frontmatter_text.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter, body
