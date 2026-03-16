"""Web application testing — auth, sessions, API discovery, parameter fuzzing."""

from __future__ import annotations

import json
import re
import urllib.parse

from core.executor import Executor


class WebModule:
    """Web application security testing module."""

    def __init__(self, executor: Executor):
        self.executor = executor

    async def auth_test(self, target: str, login_url: str = "") -> dict:
        """Test authentication mechanisms for common weaknesses."""
        base_url = target if target.startswith("http") else f"https://{target}"
        findings = []

        # Discover login pages
        login_paths = ["/login", "/signin", "/auth", "/admin", "/wp-login.php", "/user/login"]
        found_login = login_url

        if not found_login:
            for path in login_paths:
                url = f"{base_url}{path}"
                cmd = f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 10 '{url}'"
                result = await self.executor.run(cmd, tool="curl")
                if result.success and result.stdout.strip() in ("200", "301", "302"):
                    found_login = url
                    break

        if not found_login:
            return {"findings": [], "note": "No login page found"}

        # Test default credentials
        default_creds = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", "123456"),
            ("root", "root"),
            ("test", "test"),
        ]

        for user, passwd in default_creds:
            cmd = (
                f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 10 "
                f"-X POST -d 'username={user}&password={passwd}' '{found_login}'"
            )
            result = await self.executor.run(cmd, tool="curl")

            if result.success and result.stdout.strip() in ("302", "303"):
                findings.append({
                    "title": "Default Credentials Accepted",
                    "severity": "critical",
                    "description": f"Login accepted default credentials ({user}:{passwd})",
                    "evidence": f"URL: {found_login}, Creds: {user}:{passwd}",
                    "remediation": "Change default credentials. Enforce strong password policies.",
                })

        # Check for username enumeration
        cmd = (
            f"curl -sL --max-time 10 -X POST "
            f"-d 'username=definitely_not_a_real_user_xyzzy&password=wrong' '{found_login}'"
        )
        result1 = await self.executor.run(cmd, tool="curl")

        cmd = (
            f"curl -sL --max-time 10 -X POST "
            f"-d 'username=admin&password=wrong' '{found_login}'"
        )
        result2 = await self.executor.run(cmd, tool="curl")

        if result1.success and result2.success and len(result1.stdout) != len(result2.stdout):
            findings.append({
                "title": "Username Enumeration",
                "severity": "low",
                "description": "Login page returns different responses for valid vs invalid usernames.",
                "evidence": f"Response lengths differ: {len(result1.stdout)} vs {len(result2.stdout)}",
                "remediation": "Use generic error messages like 'Invalid credentials' for all login failures.",
            })

        return {"findings": findings, "login_url": found_login}

    async def session_test(self, target: str) -> dict:
        """Test session management security."""
        base_url = target if target.startswith("http") else f"https://{target}"
        findings = []

        cmd = f"curl -sI -c - --max-time 10 '{base_url}'"
        result = await self.executor.run(cmd, tool="curl")

        if result.success:
            cookies_raw = result.stdout
            # Check cookie flags
            if "Set-Cookie:" in cookies_raw:
                if "Secure" not in cookies_raw and base_url.startswith("https"):
                    findings.append({
                        "title": "Session Cookie Missing Secure Flag",
                        "severity": "medium",
                        "description": "Session cookie is not marked as Secure.",
                        "evidence": "Secure flag not found in Set-Cookie header",
                        "remediation": "Add the Secure flag to all session cookies.",
                    })
                if "HttpOnly" not in cookies_raw:
                    findings.append({
                        "title": "Session Cookie Missing HttpOnly Flag",
                        "severity": "medium",
                        "description": "Session cookie is not marked as HttpOnly, making it accessible to JavaScript.",
                        "evidence": "HttpOnly flag not found in Set-Cookie header",
                        "remediation": "Add the HttpOnly flag to all session cookies.",
                    })
                if "SameSite" not in cookies_raw:
                    findings.append({
                        "title": "Session Cookie Missing SameSite Attribute",
                        "severity": "low",
                        "description": "Session cookie does not have a SameSite attribute.",
                        "evidence": "SameSite attribute not found in Set-Cookie header",
                        "remediation": "Add SameSite=Strict or SameSite=Lax to session cookies.",
                    })

        return {"findings": findings}

    async def api_discovery(self, target: str) -> dict:
        """Discover API endpoints and documentation."""
        base_url = target if target.startswith("http") else f"https://{target}"
        discovered = []

        api_paths = [
            "/api", "/api/v1", "/api/v2", "/api/docs", "/api/swagger",
            "/swagger.json", "/openapi.json", "/swagger-ui.html",
            "/graphql", "/graphiql", "/.well-known/openapi.json",
            "/api-docs", "/docs", "/redoc",
        ]

        for path in api_paths:
            url = f"{base_url}{path}"
            cmd = f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 10 '{url}'"
            result = await self.executor.run(cmd, tool="curl")

            if result.success and result.stdout.strip() in ("200", "301", "302"):
                discovered.append({"path": path, "status": result.stdout.strip()})

        findings = []
        if any(p["path"] in ("/swagger.json", "/openapi.json", "/api-docs", "/graphiql") for p in discovered):
            findings.append({
                "title": "API Documentation Publicly Accessible",
                "severity": "low",
                "description": "API documentation endpoints are accessible without authentication.",
                "evidence": f"Accessible endpoints: {[p['path'] for p in discovered]}",
                "remediation": "Restrict access to API documentation in production environments.",
            })

        return {"endpoints": discovered, "findings": findings}

    async def param_fuzz(self, target: str, url: str = "", wordlist: str | None = None) -> dict:
        """Fuzz URL parameters to discover hidden parameters."""
        test_url = url or (target if target.startswith("http") else f"https://{target}")
        discovered = []

        common_params = [
            "id", "user", "name", "page", "file", "path", "url", "redirect",
            "next", "callback", "cmd", "exec", "query", "search", "lang",
            "debug", "test", "admin", "token", "key", "api_key", "secret",
            "action", "type", "format", "view", "template", "include",
        ]

        for param in common_params:
            test = f"{test_url}{'&' if '?' in test_url else '?'}{param}=vulcan_test_value"
            cmd = f"curl -sL -o /dev/null -w '%{{http_code}} %{{size_download}}' --max-time 10 '{test}'"
            result = await self.executor.run(cmd, tool="curl")

            if result.success:
                parts = result.stdout.strip().split()
                if len(parts) == 2:
                    status, size = parts
                    if status == "200":
                        discovered.append({"param": param, "status": status, "size": size})

        return {"discovered_params": discovered, "count": len(discovered)}
