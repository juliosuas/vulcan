"""Nmap integration with XML parsing."""

from __future__ import annotations

import re

from tools.wrapper import ToolWrapper, ToolOutput


class NmapWrapper(ToolWrapper):
    """Wrapper for nmap port scanner with XML output parsing."""

    tool_name = "nmap"
    binary_name = "nmap"

    async def run(self, target: str, ports: str = "", scan_type: str = "default", scripts: str = "") -> ToolOutput:
        check = self.check_available()
        if check:
            return check

        flags_map = {
            "quick": "-sV -T4 --top-ports 100",
            "default": "-sV -sC -T4",
            "full": "-sV -sC -A -T4 -p-",
            "udp": "-sU -T4 --top-ports 50",
            "stealth": "-sS -T2",
        }
        flags = flags_map.get(scan_type, flags_map["default"])

        if ports:
            flags += f" -p {ports}"
        if scripts:
            flags += f" --script={scripts}"

        cmd = f"nmap {flags} -oX - {target}"
        result = await self.executor.run(cmd, tool="nmap", timeout=300)

        if not result.success:
            return self._build_output(result)

        parsed = self._parse_xml(result.stdout)
        return self._build_output(result, parsed=parsed)

    @staticmethod
    def _parse_xml(xml_output: str) -> dict:
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
            return {"hosts": [], "ports": ports}

        hosts = []
        try:
            nmaprun = data.get("nmaprun", {})
            host_data = nmaprun.get("host", {})
            if isinstance(host_data, dict):
                host_data = [host_data]

            for host in host_data:
                addr = host.get("address", {})
                if isinstance(addr, list):
                    ip = addr[0].get("@addr", "")
                else:
                    ip = addr.get("@addr", "")

                ports = []
                port_data = host.get("ports", {}).get("port", [])
                if isinstance(port_data, dict):
                    port_data = [port_data]

                for p in port_data:
                    ports.append({
                        "port": int(p.get("@portid", 0)),
                        "protocol": p.get("@protocol", ""),
                        "state": p.get("state", {}).get("@state", ""),
                        "service": p.get("service", {}).get("@name", ""),
                        "product": p.get("service", {}).get("@product", ""),
                        "version": p.get("service", {}).get("@version", ""),
                    })

                os_info = host.get("os", {}).get("osmatch", {})
                if isinstance(os_info, list):
                    os_info = os_info[0] if os_info else {}

                hosts.append({
                    "ip": ip,
                    "ports": ports,
                    "os": os_info.get("@name", ""),
                    "os_accuracy": os_info.get("@accuracy", ""),
                })
        except (KeyError, TypeError, IndexError):
            pass

        return {"hosts": hosts}
