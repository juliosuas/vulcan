"""Safe command execution with subprocess isolation, timeouts, and output capture."""

from __future__ import annotations

import asyncio
import shlex
import shutil
import time
from dataclasses import dataclass, field


@dataclass
class ExecutionResult:
    """Result of a command execution."""

    command: str
    stdout: str = ""
    stderr: str = ""
    return_code: int = -1
    timed_out: bool = False
    duration: float = 0.0
    tool: str = ""

    @property
    def success(self) -> bool:
        return self.return_code == 0 and not self.timed_out

    @property
    def output(self) -> str:
        """Combined stdout and stderr."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)


class Executor:
    """Executes shell commands safely in subprocesses with timeout and output capture."""

    def __init__(self, timeout: int = 300, max_concurrency: int = 5):
        self.timeout = timeout
        self.max_concurrency = max_concurrency
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self.history: list[ExecutionResult] = []

    @staticmethod
    def tool_available(tool_name: str) -> bool:
        """Check if a tool is available on the system PATH."""
        return shutil.which(tool_name) is not None

    async def run(
        self,
        command: str,
        timeout: int | None = None,
        tool: str = "",
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Execute a command asynchronously with timeout and output capture."""
        timeout = timeout or self.timeout
        result = ExecutionResult(command=command, tool=tool)
        start = time.monotonic()

        async with self._semaphore:
            try:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                )
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=timeout
                    )
                    result.stdout = stdout.decode("utf-8", errors="replace")
                    result.stderr = stderr.decode("utf-8", errors="replace")
                    result.return_code = proc.returncode or 0
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
                    result.timed_out = True
                    result.stderr = f"Command timed out after {timeout}s"
            except Exception as e:
                result.stderr = str(e)
                result.return_code = -1

        result.duration = time.monotonic() - start
        self.history.append(result)
        return result

    def run_sync(
        self,
        command: str,
        timeout: int | None = None,
        tool: str = "",
        cwd: str | None = None,
    ) -> ExecutionResult:
        """Synchronous wrapper around async run."""
        return asyncio.get_event_loop().run_until_complete(
            self.run(command, timeout=timeout, tool=tool, cwd=cwd)
        )
