"""Gobuster integration for directory/file bruteforcing."""

from __future__ import annotations

import re

from tools.wrapper import ToolWrapper, ToolOutput


class GobusterWrapper(ToolWrapper):
    """Wrapper for gobuster directory bruteforce tool."""

    tool_name = "gobuster"
    binary_name = "gobuster"

    async def run(
        self,
        target: str,
        mode: str = "dir",
        wordlist: str = "/usr/share/wordlists/dirb/common.txt",
        extensions: str = "",
        threads: int = 20,
        status_codes: str = "200,204,301,302,307,401,403",
    ) -> ToolOutput:
        check = self.check_available()
        if check:
            return check

        url = target if target.startswith("http") else f"https://{target}"
        cmd = (
            f"gobuster {mode} -u {url} -w {wordlist} "
            f"-t {threads} -s {status_codes} -q --no-color"
        )

        if extensions:
            cmd += f" -x {extensions}"

        result = await self.executor.run(cmd, tool="gobuster", timeout=180)

        if not result.success:
            return self._build_output(result)

        entries = self._parse_output(result.stdout)
        parsed = {
            "total": len(entries),
            "by_status": {},
        }
        for e in entries:
            status = e.get("status", "")
            parsed["by_status"][status] = parsed["by_status"].get(status, 0) + 1

        findings = []
        # Flag interesting discoveries
        sensitive_patterns = [
            "admin", "backup", "config", ".env", ".git", "debug",
            "phpinfo", "server-status", "wp-admin", ".htaccess",
        ]
        for e in entries:
            path = e.get("path", "").lower()
            if any(p in path for p in sensitive_patterns):
                findings.append({
                    "title": f"Sensitive Path Discovered: {e['path']}",
                    "severity": "medium",
                    "description": f"Potentially sensitive path found at {e['path']} (Status: {e.get('status', 'unknown')})",
                    "evidence": f"URL: {url}{e['path']}",
                    "remediation": "Review and restrict access to sensitive paths. Remove unnecessary files.",
                })

        return self._build_output(result, parsed=parsed, findings=findings)

    @staticmethod
    def _parse_output(output: str) -> list[dict]:
        """Parse gobuster output."""
        entries = []
        for line in output.splitlines():
            line = line.strip()
            if not line or line.startswith("="):
                continue

            # Gobuster outputs like: /path (Status: 200) [Size: 1234]
            match = re.match(r"(\S+)\s+\(Status:\s*(\d+)\)(?:\s+\[Size:\s*(\d+)\])?", line)
            if match:
                entries.append({
                    "path": match.group(1),
                    "status": match.group(2),
                    "size": match.group(3) or "",
                })
            elif line.startswith("/"):
                entries.append({"path": line.split()[0], "status": "", "size": ""})

        return entries
