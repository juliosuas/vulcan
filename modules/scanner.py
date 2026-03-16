"""Vulnerability scanning module — Nuclei, CVE checks, SSL/TLS, headers, CORS."""

from __future__ import annotations

import json
import re

from core.executor import Executor


class ScannerModule:
    """Vulnerability scanning using nuclei, SSL checks, header analysis, and CORS testing."""

    def __init__(self, executor: Executor):
        self.executor = executor

    async def nuclei_scan(self, target: str, templates: str = "", severity: str = "") -> dict:
        """Run nuclei template scanning against the target."""
        if not self.executor.tool_available("nuclei"):
            return {"error": "nuclei not installed", "findings": []}

        url = target if target.startswith("http") else f"https://{target}"
        cmd = f"nuclei -u {url} -silent -jsonl"
        if templates:
            cmd += f" -t {templates}"
        if severity:
            cmd += f" -severity {severity}"

        result = await self.executor.run(cmd, tool="nuclei", timeout=300)

        if not result.success:
            return {"error": result.stderr, "findings": []}

        findings = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                findings.append({
                    "title": entry.get("info", {}).get("name", "Unknown"),
                    "severity": entry.get("info", {}).get("severity", "info"),
                    "description": entry.get("info", {}).get("description", ""),
                    "evidence": entry.get("matched-at", ""),
                    "template": entry.get("template-id", ""),
                })
            except json.JSONDecodeError:
                continue

        return {"findings": findings, "count": len(findings)}

    async def ssl_analysis(self, target: str) -> dict:
        """Analyze SSL/TLS configuration."""
        cmd = f"echo | openssl s_client -connect {target}:443 -servername {target} 2>/dev/null"
        result = await self.executor.run(cmd, tool="openssl")

        findings = []
        info = {"protocol": "", "cipher": "", "certificate": {}}

        if result.success:
            output = result.stdout

            # Extract protocol
            proto_match = re.search(r"Protocol\s*:\s*(\S+)", output)
            if proto_match:
                info["protocol"] = proto_match.group(1)

            # Extract cipher
            cipher_match = re.search(r"Cipher\s*:\s*(\S+)", output)
            if cipher_match:
                info["cipher"] = cipher_match.group(1)

            # Check for weak protocols
            if "TLSv1.0" in output or "TLSv1.1" in output or "SSLv3" in output:
                findings.append({
                    "title": "Weak TLS/SSL Protocol Supported",
                    "severity": "medium",
                    "description": "The server supports outdated TLS/SSL protocols that are vulnerable to known attacks.",
                    "evidence": f"Protocol: {info['protocol']}",
                    "remediation": "Disable TLSv1.0, TLSv1.1, and SSLv3. Only allow TLSv1.2 and TLSv1.3.",
                })

            # Check certificate expiry
            cert_cmd = f"echo | openssl s_client -connect {target}:443 -servername {target} 2>/dev/null | openssl x509 -noout -dates 2>/dev/null"
            cert_result = await self.executor.run(cert_cmd, tool="openssl")
            if cert_result.success:
                info["certificate"]["dates"] = cert_result.stdout.strip()

        return {"ssl_info": info, "findings": findings}

    async def header_security(self, target: str) -> dict:
        """Check HTTP security headers."""
        url = target if target.startswith("http") else f"https://{target}"
        cmd = f"curl -sI -L --max-time 10 {url}"
        result = await self.executor.run(cmd, tool="curl")

        if not result.success:
            return {"error": result.stderr, "findings": []}

        headers = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                headers[key.strip().lower()] = val.strip()

        findings = []
        required_headers = {
            "strict-transport-security": {
                "title": "Missing HSTS Header",
                "severity": "medium",
                "description": "HTTP Strict Transport Security header is not set.",
                "remediation": "Add Strict-Transport-Security header with appropriate max-age.",
            },
            "x-content-type-options": {
                "title": "Missing X-Content-Type-Options Header",
                "severity": "low",
                "description": "X-Content-Type-Options header is not set to 'nosniff'.",
                "remediation": "Add 'X-Content-Type-Options: nosniff' header.",
            },
            "x-frame-options": {
                "title": "Missing X-Frame-Options Header",
                "severity": "medium",
                "description": "X-Frame-Options header is not set, potentially allowing clickjacking.",
                "remediation": "Add 'X-Frame-Options: DENY' or 'SAMEORIGIN' header.",
            },
            "content-security-policy": {
                "title": "Missing Content-Security-Policy Header",
                "severity": "medium",
                "description": "No Content-Security-Policy header found.",
                "remediation": "Implement a Content-Security-Policy header to prevent XSS and data injection.",
            },
            "x-xss-protection": {
                "title": "Missing X-XSS-Protection Header",
                "severity": "low",
                "description": "X-XSS-Protection header is not set.",
                "remediation": "Add 'X-XSS-Protection: 1; mode=block' header.",
            },
        }

        for header, info in required_headers.items():
            if header not in headers:
                findings.append({**info, "evidence": f"Header '{header}' not found in response"})

        # Check for information disclosure
        if "server" in headers:
            findings.append({
                "title": "Server Version Disclosure",
                "severity": "info",
                "description": f"Server header reveals: {headers['server']}",
                "evidence": f"Server: {headers['server']}",
                "remediation": "Remove or obfuscate the Server header.",
            })

        return {"headers": headers, "findings": findings}

    async def cors_check(self, target: str) -> dict:
        """Check for CORS misconfiguration."""
        url = target if target.startswith("http") else f"https://{target}"
        cmd = f'curl -sI -H "Origin: https://evil.com" --max-time 10 {url}'
        result = await self.executor.run(cmd, tool="curl")

        findings = []
        if result.success:
            headers = {}
            for line in result.stdout.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    headers[key.strip().lower()] = val.strip()

            acao = headers.get("access-control-allow-origin", "")
            if acao == "*":
                findings.append({
                    "title": "CORS Wildcard Origin",
                    "severity": "medium",
                    "description": "Access-Control-Allow-Origin is set to '*', allowing any origin.",
                    "evidence": f"Access-Control-Allow-Origin: {acao}",
                    "remediation": "Restrict CORS to specific trusted origins.",
                })
            elif "evil.com" in acao:
                findings.append({
                    "title": "CORS Origin Reflection",
                    "severity": "high",
                    "description": "The server reflects the Origin header in Access-Control-Allow-Origin.",
                    "evidence": f"Reflected origin: {acao}",
                    "remediation": "Validate Origin header against a whitelist of trusted domains.",
                })

            acac = headers.get("access-control-allow-credentials", "")
            if acac.lower() == "true" and (acao == "*" or "evil.com" in acao):
                findings.append({
                    "title": "CORS Credentials with Permissive Origin",
                    "severity": "high",
                    "description": "Credentials are allowed with a permissive or reflected origin.",
                    "evidence": f"Allow-Credentials: {acac}, Allow-Origin: {acao}",
                    "remediation": "Do not allow credentials with wildcard or reflected origins.",
                })

        return {"findings": findings}

    async def cve_check(self, target: str, services: list[dict] | None = None) -> dict:
        """Check for common CVEs based on detected services."""
        if not services:
            return {"findings": [], "note": "No services provided for CVE check"}

        findings = []
        for svc in services:
            service = svc.get("service", "")
            version = svc.get("version", "")
            port = svc.get("port", "")

            if not version:
                continue

            # Use nuclei with CVE templates if available
            if self.executor.tool_available("nuclei"):
                url = f"{target}:{port}"
                cmd = f"nuclei -u {url} -t cves/ -severity critical,high -silent -jsonl"
                result = await self.executor.run(cmd, tool="nuclei", timeout=120)
                if result.success:
                    for line in result.stdout.splitlines():
                        try:
                            entry = json.loads(line.strip())
                            findings.append({
                                "title": entry.get("info", {}).get("name", ""),
                                "severity": entry.get("info", {}).get("severity", "info"),
                                "description": entry.get("info", {}).get("description", ""),
                                "evidence": entry.get("matched-at", ""),
                                "cve": entry.get("template-id", ""),
                            })
                        except json.JSONDecodeError:
                            continue

        return {"findings": findings, "services_checked": len(services or [])}
