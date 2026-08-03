import asyncio
from typing import Any

from app.tools.base import BaseTool


class ShellTool:
    name = "shell"
    description = "Run safe shell commands."

    async def run(self, command: str, **kwargs: Any) -> str:
        allowed = {"ls", "cat", "pwd", "echo", "date"}
        subcmd = command.strip().split()[0]
        if subcmd not in allowed:
            raise ValueError(f"Shell command not allowed: {subcmd}")
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            return stderr.decode()
        return stdout.decode()
