"""Professional pentest report generation (HTML/PDF)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

from jinja2 import Environment, FileSystemLoader, select_autoescape


@dataclass
class Finding:
    """A single vulnerability finding."""

    title: str
    severity: str  # critical, high, medium, low, info
    description: str
    evidence: str = ""
    remediation: str = ""
    cvss: float = 0.0
    cve: str = ""
    module: str = ""
    target: str = ""

    @property
    def severity_color(self) -> str:
        colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#ca8a04",
            "low": "#2563eb",
            "info": "#6b7280",
        }
        return colors.get(self.severity.lower(), "#6b7280")


@dataclass
class ScanSummary:
    """Summary of the overall scan."""

    target: str
    start_time: datetime
    end_time: datetime | None = None
    scan_mode: str = "standard"
    modules_run: list[str] = field(default_factory=list)
    commands_executed: int = 0
    total_findings: int = 0


class Reporter:
    """Generates professional HTML/PDF pentest reports."""

    def __init__(self, output_dir: str = "./vulcan_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.findings: list[Finding] = []
        self.scan_summary: ScanSummary | None = None
        self.raw_outputs: dict[str, str] = {}

        templates_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html"]),
        )

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def set_summary(self, summary: ScanSummary) -> None:
        self.scan_summary = summary
        self.scan_summary.total_findings = len(self.findings)

    def add_raw_output(self, module: str, output: str) -> None:
        self.raw_outputs[module] = output

    def _severity_sort_key(self, finding: Finding) -> int:
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        return order.get(finding.severity.lower(), 5)

    def generate_html(self, filename: str | None = None) -> Path:
        """Generate an HTML report."""
        self.findings.sort(key=self._severity_sort_key)

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in self.findings:
            key = f.severity.lower()
            if key in severity_counts:
                severity_counts[key] += 1

        template = self.env.get_template("report.html")
        html = template.render(
            findings=self.findings,
            summary=self.scan_summary,
            severity_counts=severity_counts,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            raw_outputs=self.raw_outputs,
        )

        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_slug = (self.scan_summary.target if self.scan_summary else "scan").replace(".", "_")
            filename = f"vulcan_{target_slug}_{ts}.report.html"

        path = self.output_dir / filename
        path.write_text(html, encoding="utf-8")
        return path

    def generate_pdf(self, filename: str | None = None) -> Path:
        """Generate a PDF report (requires weasyprint)."""
        html_path = self.generate_html()
        pdf_path = html_path.with_suffix(".pdf")
        if filename:
            pdf_path = self.output_dir / filename

        try:
            from weasyprint import HTML
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        except ImportError:
            raise RuntimeError(
                "PDF generation requires weasyprint. Install with: pip install weasyprint"
            )

        return pdf_path

    def generate_json(self, filename: str | None = None) -> Path:
        """Export findings as JSON."""
        if not filename:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vulcan_findings_{ts}.json"

        data = {
            "summary": {
                "target": self.scan_summary.target if self.scan_summary else "",
                "start_time": str(self.scan_summary.start_time) if self.scan_summary else "",
                "end_time": str(self.scan_summary.end_time) if self.scan_summary else "",
                "total_findings": len(self.findings),
            },
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity,
                    "description": f.description,
                    "evidence": f.evidence,
                    "remediation": f.remediation,
                    "cvss": f.cvss,
                    "cve": f.cve,
                }
                for f in self.findings
            ],
        }

        path = self.output_dir / filename
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path
