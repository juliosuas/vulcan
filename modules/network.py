"""Network testing — service enumeration, default credentials, SMB/FTP/SSH testing."""

from __future__ import annotations

import re

from core.executor import Executor


class NetworkModule:
    """Network-level security testing module."""

    def __init__(self, executor: Executor):
        self.executor = executor

    async def service_enum(self, target: str, ports: list[int] | None = None) -> dict:
        """Enumerate services on discovered ports with version detection."""
        if not self.executor.tool_available("nmap"):
            return {"error": "nmap not installed", "services": []}

        port_spec = ",".join(str(p) for p in ports) if ports else "21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5432,5900,8080,8443"
        cmd = f"nmap -sV -sC -p {port_spec} {target} -oX -"
        result = await self.executor.run(cmd, tool="nmap", timeout=120)

        if not result.success:
            return {"error": result.stderr, "services": []}

        services = []
        try:
            import xmltodict
            data = xmltodict.parse(result.stdout)
            host = data.get("nmaprun", {}).get("host", {})
            port_data = host.get("ports", {}).get("port", [])
            if isinstance(port_data, dict):
                port_data = [port_data]
            for p in port_data:
                state = p.get("state", {}).get("@state", "")
                if state == "open":
                    svc = p.get("service", {})
                    services.append({
                        "port": int(p.get("@portid", 0)),
                        "protocol": p.get("@protocol", ""),
                        "service": svc.get("@name", ""),
                        "version": svc.get("@version", ""),
                        "product": svc.get("@product", ""),
                        "extra_info": svc.get("@extrainfo", ""),
                    })
        except Exception:
            # Fallback regex parsing
            for match in re.finditer(
                r'portid="(\d+)".*?state="open".*?name="([^"]*)".*?product="([^"]*)".*?version="([^"]*)"',
                result.stdout,
                re.DOTALL,
            ):
                services.append({
                    "port": int(match.group(1)),
                    "service": match.group(2),
                    "product": match.group(3),
                    "version": match.group(4),
                })

        return {"services": services, "count": len(services)}

    async def default_creds_check(self, target: str, services: list[dict] | None = None) -> dict:
        """Check for default credentials on common services."""
        findings = []
        services = services or []

        for svc in services:
            service = svc.get("service", "")
            port = svc.get("port", 0)

            if service in ("ftp", "ftps") or port == 21:
                findings.extend(await self._check_ftp(target, port))
            elif service in ("ssh",) or port == 22:
                findings.extend(await self._check_ssh(target, port))
            elif service in ("mysql",) or port == 3306:
                findings.extend(await self._check_mysql(target, port))
            elif service in ("postgresql", "postgres") or port == 5432:
                findings.extend(await self._check_postgres(target, port))

        return {"findings": findings}

    async def _check_ftp(self, target: str, port: int) -> list[dict]:
        """Check FTP for anonymous login."""
        findings = []
        cmd = f"curl -s --max-time 10 ftp://{target}:{port}/ --user anonymous:anonymous"
        result = await self.executor.run(cmd, tool="curl")

        if result.success and result.return_code == 0:
            findings.append({
                "title": "FTP Anonymous Login Allowed",
                "severity": "high",
                "description": f"FTP server on port {port} allows anonymous login.",
                "evidence": f"Anonymous access to ftp://{target}:{port}/",
                "remediation": "Disable anonymous FTP access unless explicitly required.",
            })

        return findings

    async def _check_ssh(self, target: str, port: int) -> list[dict]:
        """Check SSH for password authentication and weak configs."""
        findings = []

        # Check if password auth is enabled (via SSH banner / config)
        cmd = f"ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=no -p {port} nobody@{target} 2>&1 || true"
        result = await self.executor.run(cmd, tool="ssh", timeout=15)

        if result.output:
            if "Permission denied (publickey)" in result.output:
                pass  # Good — password auth disabled
            elif "password" in result.output.lower():
                findings.append({
                    "title": "SSH Password Authentication Enabled",
                    "severity": "low",
                    "description": f"SSH on port {port} accepts password authentication.",
                    "evidence": "SSH responds to password authentication attempts",
                    "remediation": "Disable password authentication. Use key-based authentication only.",
                })

        return findings

    async def _check_mysql(self, target: str, port: int) -> list[dict]:
        """Check MySQL for default credentials."""
        findings = []
        default_creds = [("root", ""), ("root", "root"), ("root", "password")]

        for user, passwd in default_creds:
            cmd = f"mysql -h {target} -P {port} -u {user} -p'{passwd}' -e 'SELECT 1' 2>&1 || true"
            result = await self.executor.run(cmd, tool="mysql", timeout=10)

            if result.success and "1" in result.stdout and "ERROR" not in result.output:
                findings.append({
                    "title": "MySQL Default Credentials",
                    "severity": "critical",
                    "description": f"MySQL on port {port} accepts default credentials ({user}).",
                    "evidence": f"Successful login with {user}:{passwd or '(empty)'}",
                    "remediation": "Change default MySQL credentials immediately. Restrict remote access.",
                })
                break

        return findings

    async def _check_postgres(self, target: str, port: int) -> list[dict]:
        """Check PostgreSQL for default credentials."""
        findings = []
        default_creds = [("postgres", "postgres"), ("postgres", "password")]

        for user, passwd in default_creds:
            cmd = f"PGPASSWORD='{passwd}' psql -h {target} -p {port} -U {user} -c 'SELECT 1' 2>&1 || true"
            result = await self.executor.run(cmd, tool="psql", timeout=10)

            if result.success and "1" in result.stdout and "FATAL" not in result.output:
                findings.append({
                    "title": "PostgreSQL Default Credentials",
                    "severity": "critical",
                    "description": f"PostgreSQL on port {port} accepts default credentials ({user}).",
                    "evidence": f"Successful login with {user}:{passwd}",
                    "remediation": "Change default PostgreSQL credentials. Restrict remote access via pg_hba.conf.",
                })
                break

        return findings

    async def smb_test(self, target: str) -> dict:
        """Test SMB for null sessions and common misconfigurations."""
        findings = []

        if not self.executor.tool_available("smbclient"):
            return {"error": "smbclient not installed", "findings": []}

        # Test null session
        cmd = f"smbclient -L //{target} -N 2>&1 || true"
        result = await self.executor.run(cmd, tool="smbclient", timeout=15)

        if result.success and "Sharename" in result.output:
            shares = []
            for line in result.output.splitlines():
                line = line.strip()
                if line and not line.startswith("Sharename") and not line.startswith("---") and "\t" in line:
                    shares.append(line.split()[0] if line.split() else line)

            findings.append({
                "title": "SMB Null Session Allowed",
                "severity": "high",
                "description": "SMB server allows null session enumeration of shares.",
                "evidence": f"Shares found: {shares}",
                "remediation": "Disable null sessions. Restrict anonymous access to SMB shares.",
            })

        return {"findings": findings}
