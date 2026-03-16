"""Nuclei scanner integration."""

from __future__ import annotations

import json

from tools.wrapper import ToolWrapper, ToolOutput


class NucleiWrapper(ToolWrapper):
    """Wrapper for ProjectDiscovery's Nuclei vulnerability scanner."""

    tool_name = "nuclei"
    binary_name = "nuclei"

    async def run(
        self,
        target: str,
        templates: str = "",
        severity: str = "",
        tags: str = "",
        rate_limit: int = 150,
    ) -> ToolOutput:
        check = self.check_available()
        if check:
            return check

        url = target if target.startswith("http") else f"https://{target}"
        cmd = f"nuclei -u {url} -silent -jsonl -rate-limit {rate_limit}"

        if templates:
            cmd += f" -t {templates}"
        if severity:
            cmd += f" -severity {severity}"
        if tags:
            cmd += f" -tags {tags}"

        result = await self.executor.run(cmd, tool="nuclei", timeout=300)

        if not result.success:
            return self._build_output(result)

        findings = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                info = entry.get("info", {})
                findings.append({
                    "title": info.get("name", "Unknown"),
                    "severity": info.get("severity", "info"),
                    "description": info.get("description", ""),
                    "evidence": entry.get("matched-at", ""),
                    "template_id": entry.get("template-id", ""),
                    "tags": info.get("tags", []),
                    "reference": info.get("reference", []),
                    "remediation": info.get("remediation", ""),
                })
            except json.JSONDecodeError:
                continue

        parsed = {"total": len(findings), "by_severity": {}}
        for f in findings:
            sev = f["severity"]
            parsed["by_severity"][sev] = parsed["by_severity"].get(sev, 0) + 1

        return self._build_output(result, parsed=parsed, findings=findings)
