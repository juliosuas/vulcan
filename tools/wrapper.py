"""Base class for tool wrappers with unified output format."""

from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from core.executor import Executor, ExecutionResult


@dataclass
class ToolOutput:
    """Unified output format for all tool wrappers."""

    tool: str
    success: bool
    raw_output: str = ""
    parsed: dict = field(default_factory=dict)
    findings: list[dict] = field(default_factory=list)
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "success": self.success,
            "parsed": self.parsed,
            "findings": self.findings,
            "error": self.error,
        }


class ToolWrapper(ABC):
    """Base class for all tool wrappers."""

    tool_name: str = ""
    binary_name: str = ""

    def __init__(self, executor: Executor):
        self.executor = executor

    @property
    def available(self) -> bool:
        """Check if the wrapped tool is installed."""
        return shutil.which(self.binary_name) is not None

    def check_available(self) -> ToolOutput:
        """Return an error ToolOutput if the tool is not available."""
        if not self.available:
            return ToolOutput(
                tool=self.tool_name,
                success=False,
                error=f"{self.binary_name} is not installed. Install it to use {self.tool_name} features.",
            )
        return None

    @abstractmethod
    async def run(self, target: str, **kwargs) -> ToolOutput:
        """Run the tool against a target. Must be implemented by subclasses."""
        ...

    def _build_output(self, result: ExecutionResult, parsed: dict | None = None, findings: list[dict] | None = None) -> ToolOutput:
        """Build a ToolOutput from an ExecutionResult."""
        return ToolOutput(
            tool=self.tool_name,
            success=result.success,
            raw_output=result.output,
            parsed=parsed or {},
            findings=findings or [],
            error=result.stderr if not result.success else "",
        )
