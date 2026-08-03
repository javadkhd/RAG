import subprocess
from typing import Any

from app.tools.base import BaseTool


class GitTool:
    name = "git"
    description = "Run git commands in a repository."

    async def run(self, command: str, cwd: str = ".", **kwargs: Any) -> str:
        allowed = {"status", "log", "diff", "show", "branch", "tag"}
        subcmd = command.strip().split()[0]
        if subcmd not in allowed:
            raise ValueError(f"Git command not allowed: {subcmd}")
        result = subprocess.run(
            ["git"] + command.split(),
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
