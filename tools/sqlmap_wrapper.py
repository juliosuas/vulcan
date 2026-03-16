"""SQLMap integration for SQL injection testing."""

from __future__ import annotations

import re

from tools.wrapper import ToolWrapper, ToolOutput


class SqlmapWrapper(ToolWrapper):
    """Wrapper for sqlmap SQL injection tool."""

    tool_name = "sqlmap"
    binary_name = "sqlmap"

    async def run(
        self,
        target: str,
        params: list[str] | None = None,
        level: int = 2,
        risk: int = 1,
        technique: str = "",
        tamper: str = "",
    ) -> ToolOutput:
        check = self.check_available()
        if check:
            return check

        cmd = (
            f"sqlmap -u '{target}' --batch --random-agent "
            f"--level={level} --risk={risk} "
            f"--output-dir=/tmp/sqlmap_vulcan"
        )

        if params:
            cmd += f" -p {','.join(params)}"
        if technique:
            cmd += f" --technique={technique}"
        if tamper:
            cmd += f" --tamper={tamper}"

        result = await self.executor.run(cmd, tool="sqlmap", timeout=180)

        if not result.success:
            return self._build_output(result)

        findings = self._parse_output(result.stdout)
        parsed = {
            "vulnerable": len(findings) > 0,
            "injection_count": len(findings),
        }

        return self._build_output(result, parsed=parsed, findings=findings)

    @staticmethod
    def _parse_output(output: str) -> list[dict]:
        """Parse sqlmap output for injection findings."""
        findings = []

        for match in re.finditer(
            r"Parameter: (\S+).*?Type: ([^\n]+).*?Title: ([^\n]+)",
            output,
            re.DOTALL,
        ):
            param = match.group(1)
            inj_type = match.group(2).strip()
            title = match.group(3).strip()

            findings.append({
                "title": f"SQL Injection — {title}",
                "severity": "critical",
                "description": f"SQL injection in parameter '{param}' via {inj_type}.",
                "evidence": match.group(0)[:500],
                "remediation": "Use parameterized queries. Validate and sanitize all user input.",
            })

        # Check for database info extraction
        db_match = re.search(r"back-end DBMS: (.+)", output)
        if db_match:
            for f in findings:
                f["description"] += f" Backend DBMS: {db_match.group(1).strip()}"

        return findings
