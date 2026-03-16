"""Reconnaissance module — subdomain enum, port scanning, tech detection, dir bruteforce, DNS."""

from __future__ import annotations

import re

from rich.console import Console

from core.executor import Executor

console = Console()


class ReconModule:
    """Reconnaissance module wrapping common recon tools."""

    def __init__(self, executor: Executor):
        self.executor = executor

    async def port_scan(self, target: str, ports: str = "-", scan_type: str = "default") -> dict:
        """Run an nmap port scan against the target.

        Args:
            target: Target IP or hostname.
            ports: Port range (default "-" for all ports in quick mode, or top 1000).
            scan_type: "quick", "default", or "full".
        """
        if not self.executor.tool_available("nmap"):
            return {"error": "nmap not installed", "ports": []}

        flags = {
            "quick": "-sV -T4 --top-ports 100",
            "default": "-sV -sC -T4",
            "full": "-sV -sC -A -T4 -p-",
        }
        nmap_flags = flags.get(scan_type, flags["default"])
        cmd = f"nmap {nmap_flags} -oX - {target}"
        result = await self.executor.run(cmd, tool="nmap")

        if not result.success:
            return {"error": result.stderr, "ports": []}

        return self._parse_nmap_xml(result.stdout)

    async def subdomain_enum(self, target: str) -> dict:
        """Enumerate subdomains using subfinder."""
        if not self.executor.tool_available("subfinder"):
            return {"error": "subfinder not installed", "subdomains": []}

        cmd = f"subfinder -d {target} -silent"
        result = await self.executor.run(cmd, tool="subfinder")

        if not result.success:
            return {"error": result.stderr, "subdomains": []}

        subs = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return {"subdomains": subs, "count": len(subs)}

    async def tech_detect(self, target: str) -> dict:
        """Detect technologies using curl header analysis (fallback if whatweb unavailable)."""
        if self.executor.tool_available("whatweb"):
            cmd = f"whatweb -q --color=never {target}"
            result = await self.executor.run(cmd, tool="whatweb")
            if result.success:
                return {"technologies": result.stdout.strip(), "tool": "whatweb"}

        # Fallback: inspect HTTP headers
        cmd = f"curl -sI -L --max-time 10 https://{target}"
        result = await self.executor.run(cmd, tool="curl")

        if not result.success:
            cmd = f"curl -sI -L --max-time 10 http://{target}"
            result = await self.executor.run(cmd, tool="curl")

        headers = {}
        techs = []
        if result.success:
            for line in result.stdout.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    headers[key.strip().lower()] = val.strip()

            if "server" in headers:
                techs.append(headers["server"])
            if "x-powered-by" in headers:
                techs.append(headers["x-powered-by"])

        return {"technologies": techs, "headers": headers, "tool": "curl"}

    async def dir_bruteforce(self, target: str, wordlist: str | None = None) -> dict:
        """Run directory bruteforce using gobuster."""
        if not self.executor.tool_available("gobuster"):
            return {"error": "gobuster not installed", "directories": []}

        wl = wordlist or "/usr/share/wordlists/dirb/common.txt"
        url = target if target.startswith("http") else f"https://{target}"
        cmd = f"gobuster dir -u {url} -w {wl} -q --no-color -t 20"
        result = await self.executor.run(cmd, tool="gobuster", timeout=120)

        if not result.success:
            return {"error": result.stderr, "directories": []}

        dirs = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("="):
                dirs.append(line)

        return {"directories": dirs, "count": len(dirs)}

    async def dns_enum(self, target: str) -> dict:
        """Enumerate DNS records for the target."""
        records = {}
        for rtype in ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"):
            cmd = f"dig +short {target} {rtype}"
            result = await self.executor.run(cmd, tool="dig")
            if result.success and result.stdout.strip():
                records[rtype] = [l.strip() for l in result.stdout.splitlines() if l.strip()]

        return {"dns_records": records}

    @staticmethod
    def _parse_nmap_xml(xml_output: str) -> dict:
        """Parse nmap XML output into structured data."""
        try:
            import xmltodict
            data = xmltodict.parse(xml_output)
        except Exception:
            # Fallback regex parsing
            ports = []
            for match in re.finditer(
                r'portid="(\d+)".*?protocol="(\w+)".*?state="(\w+)".*?name="([^"]*)"',
                xml_output,
                re.DOTALL,
            ):
                ports.append({
                    "port": int(match.group(1)),
                    "protocol": match.group(2),
                    "state": match.group(3),
                    "service": match.group(4),
                })
            return {"ports": ports, "count": len(ports)}

        ports = []
        try:
            host = data.get("nmaprun", {}).get("host", {})
            port_data = host.get("ports", {}).get("port", [])
            if isinstance(port_data, dict):
                port_data = [port_data]
            for p in port_data:
                ports.append({
                    "port": int(p.get("@portid", 0)),
                    "protocol": p.get("@protocol", ""),
                    "state": p.get("state", {}).get("@state", ""),
                    "service": p.get("service", {}).get("@name", ""),
                    "version": p.get("service", {}).get("@version", ""),
                })
        except (KeyError, TypeError):
            pass

        return {"ports": ports, "count": len(ports)}
