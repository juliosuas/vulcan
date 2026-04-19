"""HexStrike-backed Executor: routes commands to the HexStrike Flask API instead of local subprocess.

Drop-in replacement for core.executor.Executor. Parses `<tool> <args> <target>` commands, maps to the
corresponding /api/tools/<tool> endpoint, and packages the JSON response back into an ExecutionResult.
"""

from __future__ import annotations

import asyncio
import shlex
import time
import urllib.parse
from typing import Any

import aiohttp

from core.executor import Executor, ExecutionResult


DEFAULT_SERVER = "http://127.0.0.1:8888"


def _is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))


def _command_to_api_call(command: str) -> tuple[str, dict[str, Any]] | None:
    """Parse a shell command and map it to a (endpoint, json_body) tuple.

    Returns None if the command can't be mapped (fall back to generic /api/command).
    Each entry captures the minimum fields HexStrike endpoints require plus additional_args
    for anything past the target/url.
    """
    try:
        parts = shlex.split(command)
    except ValueError:
        return None
    if not parts:
        return None

    tool = parts[0]
    rest = parts[1:]

    if tool == "nmap":
        target = rest[-1] if rest else ""
        flags = " ".join(rest[:-1]) if len(rest) > 1 else ""
        return f"/api/tools/nmap", {
            "target": target,
            "scan_type": "",
            "additional_args": flags,
        }

    if tool == "gobuster":
        mode = rest[0] if rest else "dir"
        url = ""
        wordlist = ""
        extras: list[str] = []
        i = 1
        while i < len(rest):
            tok = rest[i]
            if tok == "-u" and i + 1 < len(rest):
                url = rest[i + 1]; i += 2; continue
            if tok == "-w" and i + 1 < len(rest):
                wordlist = rest[i + 1]; i += 2; continue
            extras.append(tok); i += 1
        return f"/api/tools/gobuster", {
            "url": url,
            "mode": mode,
            "wordlist": wordlist or "/usr/share/seclists/Discovery/Web-Content/common.txt",
            "additional_args": " ".join(extras),
        }

    if tool == "nuclei":
        target = ""
        extras: list[str] = []
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok in ("-u", "-target") and i + 1 < len(rest):
                target = rest[i + 1]; i += 2; continue
            extras.append(tok); i += 1
        return f"/api/tools/nuclei", {
            "target": target,
            "additional_args": " ".join(extras),
        }

    if tool == "ffuf":
        url = ""
        wordlist = ""
        extras: list[str] = []
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok == "-u" and i + 1 < len(rest):
                url = rest[i + 1]; i += 2; continue
            if tok == "-w" and i + 1 < len(rest):
                wordlist = rest[i + 1]; i += 2; continue
            extras.append(tok); i += 1
        return f"/api/tools/ffuf", {
            "url": url,
            "wordlist": wordlist,
            "additional_args": " ".join(extras),
        }

    if tool == "sqlmap":
        url = ""
        extras: list[str] = []
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok in ("-u", "--url") and i + 1 < len(rest):
                url = rest[i + 1]; i += 2; continue
            extras.append(tok); i += 1
        return f"/api/tools/sqlmap", {
            "url": url,
            "additional_args": " ".join(extras),
        }

    if tool == "nikto":
        target = ""
        i = 0
        while i < len(rest):
            tok = rest[i]
            if tok in ("-h", "-host") and i + 1 < len(rest):
                target = rest[i + 1]; i += 2; continue
            i += 1
        return f"/api/tools/nikto", {
            "target": target,
            "additional_args": "",
        }

    if tool == "hydra":
        # Last arg is service://target typically
        return f"/api/tools/hydra", {
            "target": rest[-1] if rest else "",
            "additional_args": " ".join(rest[:-1]) if len(rest) > 1 else "",
        }

    if tool in ("nxc", "netexec"):
        return f"/api/tools/netexec", {
            "protocol": rest[0] if rest else "smb",
            "target": rest[1] if len(rest) > 1 else "",
            "additional_args": " ".join(rest[2:]) if len(rest) > 2 else "",
        }

    if tool == "hashcat":
        return f"/api/tools/hashcat", {"additional_args": " ".join(rest)}

    if tool == "msfvenom":
        return f"/api/tools/msfvenom", {"additional_args": " ".join(rest)}

    if tool == "subfinder":
        domain = ""
        i = 0
        while i < len(rest):
            if rest[i] == "-d" and i + 1 < len(rest):
                domain = rest[i + 1]; break
            i += 1
        return f"/api/tools/subfinder", {
            "domain": domain,
            "additional_args": "",
        }

    # Unmapped: fall back to generic command executor.
    return None


class HexStrikeExecutor(Executor):
    """Executor that delegates commands to a remote HexStrike AI Flask API.

    Preserves the Executor public surface (async run, history, tool_available) so Vulcan modules
    work unchanged. Pass ``fallback_local=True`` to silently fall back to local subprocess execution
    for unmapped commands or when the server is unreachable.
    """

    def __init__(
        self,
        timeout: int = 300,
        max_concurrency: int = 5,
        server_url: str = DEFAULT_SERVER,
        fallback_local: bool = True,
    ):
        super().__init__(timeout=timeout, max_concurrency=max_concurrency)
        self.server_url = server_url.rstrip("/")
        self.fallback_local = fallback_local
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def health_check(self) -> bool:
        try:
            session = await self._get_session()
            async with session.get(f"{self.server_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return resp.status == 200
        except Exception:
            return False

    @staticmethod
    def tool_available(tool_name: str) -> bool:  # noqa: D401 - maintain Executor signature
        """Always True when routed through HexStrike — the server owns availability."""
        return True

    async def run(
        self,
        command: str,
        timeout: int | None = None,
        tool: str = "",
        cwd: str | None = None,
    ) -> ExecutionResult:
        timeout = timeout or self.timeout
        start = time.monotonic()
        result = ExecutionResult(command=command, tool=tool)

        mapping = _command_to_api_call(command)

        # Prefer structured tool endpoint when mapped; otherwise use generic /api/command.
        if mapping is None:
            endpoint, body = "/api/command", {"command": command, "use_cache": True}
        else:
            endpoint, body = mapping

        async with self._semaphore:
            try:
                session = await self._get_session()
                async with session.post(
                    f"{self.server_url}{endpoint}",
                    json=body,
                    timeout=aiohttp.ClientTimeout(total=timeout + 10),
                ) as resp:
                    data = await resp.json(content_type=None)
                result.stdout = str(data.get("stdout", data.get("output", "")) or "")
                result.stderr = str(data.get("stderr", data.get("error", "")) or "")
                result.return_code = int(data.get("return_code", 0 if data.get("success") else 1))
                result.timed_out = bool(data.get("timed_out", False))
            except Exception as e:
                if self.fallback_local:
                    result = await super().run(command, timeout=timeout, tool=tool, cwd=cwd)
                    result.stderr = (result.stderr + f"\n[hexstrike fallback: {e}]").strip()
                    return result
                result.stderr = f"HexStrike request failed: {e}"
                result.return_code = -1

        result.duration = time.monotonic() - start
        self.history.append(result)
        return result
