import os
from typing import Any

from app.tools.base import BaseTool


class FilesystemTool:
    name = "filesystem"
    description = "Read, write, or list files on the local filesystem."

    async def run(self, action: str, path: str, content: str | None = None, **kwargs: Any) -> str:
        if action == "read":
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        elif action == "write":
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
            return f"Wrote {path}"
        elif action == "list":
            entries = os.listdir(path)
            return "\n".join(entries)
        else:
            raise ValueError(f"Unknown filesystem action: {action}")
