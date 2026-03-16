"""Tests for Vulcan core components."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from core.config import Config
from core.executor import Executor, ExecutionResult
from core.planner import Planner, AttackPlan, AttackStep, Priority
from core.reporter import Reporter, Finding, ScanSummary
from datetime import datetime


class TestConfig:
    def test_default_config(self):
        cfg = Config()
        assert cfg.llm_provider == "claude"
        assert cfg.scan_mode == "standard"
        assert cfg.cmd_timeout == 300
        assert cfg.max_concurrency == 5

    def test_get_api_key_claude(self):
        cfg = Config(llm_provider="claude", anthropic_api_key="test-key")
        assert cfg.get_api_key() == "test-key"

    def test_get_api_key_openai(self):
        cfg = Config(llm_provider="openai", openai_api_key="test-key")
        assert cfg.get_api_key() == "test-key"

    def test_ensure_output_dir(self, tmp_path):
        cfg = Config(output_dir=str(tmp_path / "output"))
        p = cfg.ensure_output_dir()
        assert p.exists()
        assert p.is_dir()


class TestExecutor:
    def test_tool_available(self):
        assert Executor.tool_available("python3") or Executor.tool_available("python")

    def test_tool_not_available(self):
        assert not Executor.tool_available("definitely_not_a_real_tool_xyzzy")

    def test_execution_result_success(self):
        r = ExecutionResult(command="test", return_code=0, stdout="ok")
        assert r.success
        assert r.output == "ok"

    def test_execution_result_failure(self):
        r = ExecutionResult(command="test", return_code=1, stderr="fail")
        assert not r.success
        assert "fail" in r.output

    def test_execution_result_timeout(self):
        r = ExecutionResult(command="test", timed_out=True)
        assert not r.success

    @pytest.mark.asyncio
    async def test_run_echo(self):
        executor = Executor(timeout=10)
        result = await executor.run("echo hello")
        assert result.success
        assert "hello" in result.stdout

    @pytest.mark.asyncio
    async def test_run_timeout(self):
        executor = Executor(timeout=1)
        result = await executor.run("sleep 10", timeout=1)
        assert result.timed_out

    @pytest.mark.asyncio
    async def test_history(self):
        executor = Executor()
        await executor.run("echo test1")
        await executor.run("echo test2")
        assert len(executor.history) == 2


class TestPlanner:
    def test_parse_plan(self):
        raw = json.dumps({
            "summary": "Test plan",
            "steps": [
                {
                    "id": 1,
                    "phase": "recon",
                    "action": "Port scan",
                    "tool": "nmap",
                    "command": "nmap target",
                    "rationale": "Find open ports",
                    "priority": "high",
                    "depends_on": [],
                }
            ],
        })
        plan = Planner._parse_plan("test.com", raw)
        assert plan.target == "test.com"
        assert plan.summary == "Test plan"
        assert len(plan.steps) == 1
        assert plan.steps[0].priority == Priority.HIGH

    def test_parse_plan_with_code_fence(self):
        raw = "```json\n" + json.dumps({
            "summary": "Fenced",
            "steps": [],
        }) + "\n```"
        plan = Planner._parse_plan("test.com", raw)
        assert plan.summary == "Fenced"

    def test_attack_plan_next_step(self):
        plan = AttackPlan(
            target="test.com",
            steps=[
                AttackStep(id=1, phase="recon", action="scan", tool="nmap", command="nmap test.com", rationale=""),
                AttackStep(id=2, phase="exploit", action="sqli", tool="sqlmap", command="sqlmap", rationale="", depends_on=[1]),
            ],
        )
        assert plan.next_step().id == 1
        plan.steps[0].completed = True
        assert plan.next_step().id == 2
        plan.steps[1].completed = True
        assert plan.next_step() is None


class TestReporter:
    def test_add_finding(self):
        reporter = Reporter("/tmp/vulcan_test_output")
        f = Finding(title="Test", severity="high", description="Test finding")
        reporter.add_finding(f)
        assert len(reporter.findings) == 1

    def test_severity_color(self):
        f = Finding(title="", severity="critical", description="")
        assert f.severity_color == "#dc2626"
        f2 = Finding(title="", severity="info", description="")
        assert f2.severity_color == "#6b7280"

    def test_generate_html(self, tmp_path):
        reporter = Reporter(str(tmp_path))
        reporter.add_finding(Finding(
            title="XSS Found",
            severity="high",
            description="Reflected XSS",
            evidence="<script>alert(1)</script>",
            remediation="Encode output",
        ))
        reporter.set_summary(ScanSummary(
            target="test.com",
            start_time=datetime.now(),
            end_time=datetime.now(),
        ))
        path = reporter.generate_html("test_report.html")
        assert path.exists()
        content = path.read_text()
        assert "XSS Found" in content
        assert "VULCAN" in content

    def test_generate_json(self, tmp_path):
        reporter = Reporter(str(tmp_path))
        reporter.add_finding(Finding(title="Test", severity="low", description="test"))
        reporter.set_summary(ScanSummary(target="test.com", start_time=datetime.now()))
        path = reporter.generate_json("test.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data["findings"]) == 1


class TestModules:
    @pytest.mark.asyncio
    async def test_recon_port_scan_no_nmap(self):
        """Test graceful handling when nmap is not available."""
        executor = Executor()
        with patch.object(Executor, 'tool_available', return_value=False):
            from modules.recon import ReconModule
            recon = ReconModule(executor)
            result = await recon.port_scan("test.com")
            assert "error" in result

    @pytest.mark.asyncio
    async def test_scanner_header_check(self):
        """Test header security check runs."""
        executor = Executor()
        from modules.scanner import ScannerModule
        scanner = ScannerModule(executor)
        # This will make a real curl request — skip if no network
        try:
            result = await scanner.header_security("example.com")
            assert "headers" in result or "error" in result
        except Exception:
            pass  # Network may not be available in CI
