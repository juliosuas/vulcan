"""Rich CLI interface with ASCII banner, progress bars, tables, and live updates."""

from __future__ import annotations

import asyncio
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core.agent import VulcanAgent
from core.config import Config

console = Console()

BANNER = r"""
[bold red]
 ██╗   ██╗██╗   ██╗██╗      ██████╗ █████╗ ███╗   ██╗
 ██║   ██║██║   ██║██║     ██╔════╝██╔══██╗████╗  ██║
 ██║   ██║██║   ██║██║     ██║     ███████║██╔██╗ ██║
 ╚██╗ ██╔╝██║   ██║██║     ██║     ██╔══██║██║╚██╗██║
  ╚████╔╝ ╚██████╔╝███████╗╚██████╗██║  ██║██║ ╚████║
   ╚═══╝   ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
[/bold red]
[dim]AI-Powered Autonomous Penetration Testing Agent[/dim]
[dim]───────────────────────────────────────────────[/dim]
"""


def print_banner():
    console.print(BANNER)


@click.group()
@click.version_option(version="1.0.0", prog_name="Vulcan")
def main():
    """Vulcan — AI-Powered Autonomous Penetration Testing Agent."""
    pass


@main.command()
@click.option("--target", "-t", required=True, help="Target domain or IP address")
@click.option("--mode", "-m", default="standard", type=click.Choice(["quick", "standard", "full"]), help="Scan mode")
@click.option("--llm", default="claude", type=click.Choice(["claude", "openai", "smartllm"]), help="LLM provider")
@click.option("--local", "local_mode", is_flag=True, help="Shortcut for --llm smartllm --hexstrike (fully local stack)")
@click.option("--hexstrike/--no-hexstrike", default=False, help="Route tool execution through HexStrike AI :8888")
@click.option("--hexstrike-url", default="http://127.0.0.1:8888", show_default=True, help="HexStrike server URL")
@click.option("--report", default="html", type=click.Choice(["html", "pdf", "json"]), help="Report format")
@click.option("--output", "-o", default="./vulcan_output", help="Output directory")
@click.option("--config", "-c", default=None, help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def scan(target: str, mode: str, llm: str, local_mode: bool, hexstrike: bool, hexstrike_url: str,
         report: str, output: str, config: str, verbose: bool):
    """Run a full penetration test against the target."""
    print_banner()

    cfg = Config.load(config_path=config)
    cfg.target = target
    cfg.scan_mode = mode
    cfg.llm_provider = "smartllm" if local_mode else llm
    cfg.use_hexstrike = hexstrike or local_mode
    cfg.hexstrike_server = hexstrike_url
    cfg.report_format = report
    cfg.output_dir = output

    if not cfg.get_api_key():
        console.print(f"[bold red]Error:[/] No API key found for {cfg.llm_provider}. Set it in .env or environment.")
        sys.exit(1)

    console.print(Panel(
        f"[bold]Target:[/] {target}\n"
        f"[bold]Mode:[/] {mode}\n"
        f"[bold]LLM:[/] {cfg.llm_provider}\n"
        f"[bold]HexStrike:[/] {'on — ' + hexstrike_url if cfg.use_hexstrike else 'off (local subprocess)'}\n"
        f"[bold]Report:[/] {report}\n"
        f"[bold]Output:[/] {output}",
        title="[bold red]Scan Configuration[/]",
        border_style="red",
    ))

    console.print("\n[bold yellow]⚠  Ensure you have authorization to test this target.[/]\n")

    agent = VulcanAgent(cfg)
    asyncio.run(agent.run(target, mode))


@main.command()
@click.option("--target", "-t", required=True, help="Target domain or IP address")
@click.option("--modules", "-m", default="all", help="Comma-separated recon modules: subdomains,ports,tech,dirs,dns")
@click.option("--output", "-o", default="./vulcan_output", help="Output directory")
@click.option("--config", "-c", default=None, help="Path to config file")
def recon(target: str, modules: str, output: str, config: str):
    """Run reconnaissance only."""
    print_banner()

    cfg = Config.load(config_path=config)
    cfg.target = target
    cfg.output_dir = output

    from core.executor import Executor
    from modules.recon import ReconModule

    executor = Executor(timeout=cfg.cmd_timeout)
    recon_mod = ReconModule(executor)

    module_list = [m.strip() for m in modules.split(",")] if modules != "all" else ["subdomains", "ports", "tech", "dirs", "dns"]

    async def run_recon():
        results = {}

        if "ports" in module_list:
            with console.status("[bold green]Running port scan..."):
                results["ports"] = await recon_mod.port_scan(target)
                console.print(f"  [green]✓[/] Port scan complete")

        if "subdomains" in module_list:
            with console.status("[bold green]Enumerating subdomains..."):
                results["subdomains"] = await recon_mod.subdomain_enum(target)
                console.print(f"  [green]✓[/] Subdomain enumeration complete")

        if "tech" in module_list:
            with console.status("[bold green]Detecting technologies..."):
                results["tech"] = await recon_mod.tech_detect(target)
                console.print(f"  [green]✓[/] Technology detection complete")

        if "dirs" in module_list:
            with console.status("[bold green]Bruteforcing directories..."):
                results["dirs"] = await recon_mod.dir_bruteforce(target)
                console.print(f"  [green]✓[/] Directory bruteforce complete")

        if "dns" in module_list:
            with console.status("[bold green]Enumerating DNS records..."):
                results["dns"] = await recon_mod.dns_enum(target)
                console.print(f"  [green]✓[/] DNS enumeration complete")

        console.print_json(data=results)

    asyncio.run(run_recon())


@main.command()
@click.option("--input", "-i", required=True, help="Path to scan data (JSON)")
@click.option("--format", "-f", "fmt", default="html", type=click.Choice(["html", "pdf", "json"]), help="Report format")
@click.option("--output", "-o", default="./vulcan_output", help="Output directory")
def report(input: str, fmt: str, output: str):
    """Generate a report from existing scan data."""
    print_banner()

    import json
    from pathlib import Path
    from datetime import datetime
    from core.reporter import Reporter, Finding, ScanSummary

    data_path = Path(input)
    if not data_path.exists():
        console.print(f"[bold red]Error:[/] File not found: {input}")
        sys.exit(1)

    with open(data_path) as f:
        data = json.load(f)

    reporter = Reporter(output)

    for f_data in data.get("findings", []):
        reporter.add_finding(Finding(
            title=f_data.get("title", ""),
            severity=f_data.get("severity", "info"),
            description=f_data.get("description", ""),
            evidence=f_data.get("evidence", ""),
            remediation=f_data.get("remediation", ""),
        ))

    summary = data.get("summary", {})
    reporter.set_summary(ScanSummary(
        target=summary.get("target", "unknown"),
        start_time=datetime.fromisoformat(summary["start_time"]) if summary.get("start_time") else datetime.now(),
        end_time=datetime.fromisoformat(summary["end_time"]) if summary.get("end_time") else datetime.now(),
    ))

    if fmt == "html":
        path = reporter.generate_html()
    elif fmt == "pdf":
        path = reporter.generate_pdf()
    else:
        path = reporter.generate_json()

    console.print(f"[bold green]Report generated:[/] {path}")


if __name__ == "__main__":
    main()
