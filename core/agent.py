"""Main VulcanAgent — ReAct-based orchestrator for autonomous pentesting."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from dataclasses import dataclass, field

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.config import Config
from core.executor import Executor, ExecutionResult
from core.planner import Planner, AttackPlan, AttackStep
from core.reporter import Reporter, Finding, ScanSummary
from modules.recon import ReconModule
from modules.scanner import ScannerModule
from modules.exploit import ExploitModule
from modules.web import WebModule
from modules.network import NetworkModule

console = Console()

REACT_SYSTEM_PROMPT = """You are Vulcan, an autonomous penetration testing agent.
You operate in a ReAct loop: Reason about the current state, decide an Action, then Observe the result.

You have access to these modules:
- recon: subdomain enumeration, port scanning, tech detection, directory bruteforce, DNS enum
- scanner: nuclei scanning, CVE checks, SSL/TLS analysis, header security, CORS checks
- exploit: SQL injection, XSS detection, SSRF, command injection, file inclusion
- web: auth testing, session management, API discovery, parameter fuzzing
- network: service enumeration, default credentials, SMB/FTP/SSH testing

Respond in JSON:
{
  "reasoning": "Your analysis of the current situation",
  "action": {
    "module": "module_name",
    "function": "function_name",
    "args": {"key": "value"}
  },
  "should_continue": true
}

Set should_continue to false when the assessment is complete.
Be thorough but efficient. Prioritize high-impact findings."""


@dataclass
class AgentState:
    """Tracks the agent's internal state during a scan."""

    target: str = ""
    phase: str = "init"
    recon_data: dict = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    plan: AttackPlan | None = None
    iteration: int = 0
    max_iterations: int = 50
    conversation: list[dict] = field(default_factory=list)


class VulcanAgent:
    """Autonomous pentesting agent using the ReAct pattern.

    Flow: Recon → Plan → Execute (loop) → Report
    """

    def __init__(self, config: Config):
        self.config = config
        self.executor = Executor(
            timeout=config.cmd_timeout,
            max_concurrency=config.max_concurrency,
        )
        self.planner = Planner(config)
        self.reporter = Reporter(config.output_dir)
        self.state = AgentState()
        self._llm_client = None

        # Initialize modules
        self.modules = {
            "recon": ReconModule(self.executor),
            "scanner": ScannerModule(self.executor),
            "exploit": ExploitModule(self.executor),
            "web": WebModule(self.executor),
            "network": NetworkModule(self.executor),
        }

    def _get_llm_client(self):
        if self._llm_client:
            return self._llm_client

        if self.config.llm_provider == "claude":
            import anthropic
            self._llm_client = anthropic.Anthropic(api_key=self.config.anthropic_api_key)
        else:
            import openai
            self._llm_client = openai.OpenAI(api_key=self.config.openai_api_key)
        return self._llm_client

    async def run(self, target: str, mode: str = "standard") -> None:
        """Run a full penetration test against the target."""
        self.state.target = target
        self.config.scan_mode = mode
        start_time = datetime.now()

        console.print(Panel(
            f"[bold red]Target:[/] {target}\n[bold red]Mode:[/] {mode}\n[bold red]LLM:[/] {self.config.llm_provider}",
            title="[bold]VULCAN — Autonomous Pentest[/]",
            border_style="red",
        ))

        # Phase 1: Reconnaissance
        console.print("\n[bold cyan]═══ Phase 1: Reconnaissance ═══[/]\n")
        self.state.phase = "recon"
        await self._run_recon(target, mode)

        # Phase 2: Planning
        console.print("\n[bold cyan]═══ Phase 2: Attack Planning ═══[/]\n")
        self.state.phase = "planning"
        self.state.plan = self.planner.generate_plan(target, self.state.recon_data)
        self._display_plan(self.state.plan)

        # Phase 3: Execution (ReAct loop)
        console.print("\n[bold cyan]═══ Phase 3: Execution ═══[/]\n")
        self.state.phase = "execution"
        await self._react_loop()

        # Phase 4: Reporting
        console.print("\n[bold cyan]═══ Phase 4: Report Generation ═══[/]\n")
        self.state.phase = "reporting"

        scan_summary = ScanSummary(
            target=target,
            start_time=start_time,
            end_time=datetime.now(),
            scan_mode=mode,
            modules_run=list(self.modules.keys()),
            commands_executed=len(self.executor.history),
        )
        self.reporter.set_summary(scan_summary)

        for finding in self.state.findings:
            self.reporter.add_finding(finding)

        report_path = self.reporter.generate_html()
        console.print(f"[bold green]Report saved to:[/] {report_path}")

    async def _run_recon(self, target: str, mode: str) -> None:
        """Run reconnaissance modules."""
        recon = self.modules["recon"]

        with console.status("[bold green]Running port scan..."):
            ports_result = await recon.port_scan(target)
            self.state.recon_data["ports"] = ports_result
            console.print(f"  [green]✓[/] Port scan complete — {len(ports_result.get('ports', []))} ports found")

        if mode in ("standard", "full"):
            with console.status("[bold green]Running subdomain enumeration..."):
                subs_result = await recon.subdomain_enum(target)
                self.state.recon_data["subdomains"] = subs_result
                console.print(f"  [green]✓[/] Subdomain enum complete — {len(subs_result.get('subdomains', []))} found")

            with console.status("[bold green]Detecting technologies..."):
                tech_result = await recon.tech_detect(target)
                self.state.recon_data["technologies"] = tech_result
                console.print(f"  [green]✓[/] Technology detection complete")

        if mode == "full":
            with console.status("[bold green]Running directory bruteforce..."):
                dirs_result = await recon.dir_bruteforce(target)
                self.state.recon_data["directories"] = dirs_result
                console.print(f"  [green]✓[/] Directory bruteforce complete")

            with console.status("[bold green]Running DNS enumeration..."):
                dns_result = await recon.dns_enum(target)
                self.state.recon_data["dns"] = dns_result
                console.print(f"  [green]✓[/] DNS enumeration complete")

    async def _react_loop(self) -> None:
        """Run the ReAct (Reason → Act → Observe) loop."""
        while self.state.iteration < self.state.max_iterations:
            self.state.iteration += 1
            console.print(f"\n[bold yellow]── Iteration {self.state.iteration} ──[/]")

            # Reason: Ask LLM what to do next
            action = self._reason()
            if not action or not action.get("should_continue", True):
                console.print("[bold green]Agent decided assessment is complete.[/]")
                break

            # Act: Execute the chosen action
            reasoning = action.get("reasoning", "")
            console.print(f"  [dim]Reasoning:[/] {reasoning}")

            act = action.get("action", {})
            module_name = act.get("module", "")
            func_name = act.get("function", "")
            args = act.get("args", {})

            console.print(f"  [cyan]Action:[/] {module_name}.{func_name}({args})")

            result = await self._execute_action(module_name, func_name, args)

            # Observe: Feed result back to the conversation
            self.state.conversation.append({
                "role": "assistant",
                "content": json.dumps(action),
            })
            self.state.conversation.append({
                "role": "user",
                "content": f"Observation:\n{json.dumps(result, indent=2, default=str)}",
            })

            # Extract any findings
            self._extract_findings(result, module_name)

    def _reason(self) -> dict | None:
        """Ask the LLM to reason about the next action."""
        context = (
            f"Target: {self.state.target}\n"
            f"Phase: {self.state.phase}\n"
            f"Iteration: {self.state.iteration}\n"
            f"Findings so far: {len(self.state.findings)}\n"
            f"Recon data summary: {json.dumps({k: type(v).__name__ for k, v in self.state.recon_data.items()})}\n"
        )

        messages = [{"role": "user", "content": context}] + self.state.conversation
        if not self.state.conversation:
            messages = [{"role": "user", "content": context + "\nBegin the assessment. What should we do first?"}]

        try:
            raw = self._call_llm(REACT_SYSTEM_PROMPT, messages)
            text = raw.strip()
            if "```" in text:
                start = text.index("```") + 3
                if text[start:].startswith("json"):
                    start += 4
                end = text.index("```", start)
                text = text[start:end].strip()
            return json.loads(text)
        except Exception as e:
            console.print(f"  [red]LLM error:[/] {e}")
            return None

    def _call_llm(self, system: str, messages: list[dict]) -> str:
        client = self._get_llm_client()

        if self.config.llm_provider == "claude":
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system,
                messages=messages,
            )
            return resp.content[0].text
        else:
            resp = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=4096,
                messages=[{"role": "system", "content": system}] + messages,
            )
            return resp.choices[0].message.content

    async def _execute_action(self, module_name: str, func_name: str, args: dict) -> dict:
        """Execute an action on a module."""
        module = self.modules.get(module_name)
        if not module:
            return {"error": f"Unknown module: {module_name}"}

        func = getattr(module, func_name, None)
        if not func:
            return {"error": f"Unknown function: {module_name}.{func_name}"}

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(**args)
            else:
                result = func(**args)
            return result if isinstance(result, dict) else {"output": str(result)}
        except Exception as e:
            return {"error": str(e)}

    def _extract_findings(self, result: dict, module: str) -> None:
        """Extract vulnerability findings from module results."""
        if "findings" in result:
            for f in result["findings"]:
                finding = Finding(
                    title=f.get("title", "Unknown"),
                    severity=f.get("severity", "info"),
                    description=f.get("description", ""),
                    evidence=f.get("evidence", ""),
                    remediation=f.get("remediation", ""),
                    module=module,
                    target=self.state.target,
                )
                self.state.findings.append(finding)
                self.reporter.add_finding(finding)
                console.print(f"  [bold red]Finding:[/] [{finding.severity_color}]{finding.severity.upper()}[/] — {finding.title}")

    def _display_plan(self, plan: AttackPlan) -> None:
        """Display the attack plan in a rich table."""
        console.print(f"[bold]Strategy:[/] {plan.summary}\n")
        table = Table(title="Attack Plan", show_lines=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Phase", style="cyan")
        table.add_column("Action", style="white")
        table.add_column("Tool", style="green")
        table.add_column("Priority", style="bold")

        for step in plan.steps:
            priority_style = {
                "critical": "bold red",
                "high": "bold yellow",
                "medium": "bold blue",
                "low": "dim",
            }.get(step.priority.value, "dim")

            table.add_row(
                str(step.id),
                step.phase,
                step.action,
                step.tool,
                f"[{priority_style}]{step.priority.value.upper()}[/{priority_style}]",
            )

        console.print(table)
