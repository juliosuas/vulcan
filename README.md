<p align="center">
  <img src="docs/logo.png" alt="Vulcan Logo" width="400"/>
</p>

<h1 align="center">VULCAN</h1>
<p align="center"><b>AI-Powered Autonomous Penetration Testing Agent</b></p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#disclaimer">Disclaimer</a>
</p>

---

Vulcan is an autonomous penetration testing framework that leverages Large Language Models (Claude, GPT-4) to plan, execute, and report on security assessments. It uses a ReAct (Reason → Act → Observe) loop to intelligently drive the pentest pipeline — from reconnaissance through exploitation to professional report generation.

## Features

- **AI-Driven Planning** — LLM-powered attack planning that adapts based on discovered information
- **Full Pentest Pipeline** — Reconnaissance, scanning, exploitation, and reporting in one tool
- **Multi-LLM Support** — Works with Anthropic Claude and OpenAI GPT-4
- **Professional Reports** — Generates HTML/PDF pentest reports with findings, severity ratings, and remediation guidance
- **Tool Integration** — Wraps industry-standard tools (Nmap, Nuclei, SQLMap, Gobuster, and more)
- **Rich CLI** — Beautiful terminal interface with progress bars, tables, and live scan updates
- **Web Dashboard** — Single-file HTML dashboard for monitoring scan progress and findings
- **Safe Execution** — Subprocess isolation with timeouts and output capture
- **Modular Architecture** — Easy to extend with new modules and tool wrappers
- **Docker Support** — Run in an isolated container environment

## Installation

### Prerequisites

- Python 3.10+
- External tools (optional, gracefully handled if missing):
  - [Nmap](https://nmap.org/)
  - [Nuclei](https://github.com/projectdiscovery/nuclei)
  - [SQLMap](https://sqlmap.org/)
  - [Gobuster](https://github.com/OJ/gobuster)
  - [Subfinder](https://github.com/projectdiscovery/subfinder)

### From Source

```bash
git clone https://github.com/yourorg/vulcan.git
cd vulcan
pip install -e .
```

### Docker

```bash
docker-compose up --build
```

### Configuration

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and/or OPENAI_API_KEY
```

## Usage

### Quick Scan

```bash
vulcan scan --target example.com
```

### Full Assessment

```bash
vulcan scan --target example.com --mode full --llm claude --report html
```

### Recon Only

```bash
vulcan recon --target example.com --modules subdomains,ports,tech
```

### CLI Options

```
Usage: vulcan [OPTIONS] COMMAND [ARGS]

Commands:
  scan     Run a full penetration test
  recon    Run reconnaissance only
  report   Generate report from scan data

Options:
  --target, -t    Target domain or IP
  --mode, -m      Scan mode: quick, standard, full (default: standard)
  --llm           LLM provider: claude, openai (default: claude)
  --report        Report format: html, pdf, json (default: html)
  --output, -o    Output directory (default: ./vulcan_output)
  --config, -c    Path to config file
  --verbose, -v   Verbose output
  --help          Show this help message
```

## Architecture

```
┌─────────────────────────────────────────────┐
│                 VulcanAgent                 │
│            (ReAct Orchestrator)             │
├─────────────┬───────────────┬───────────────┤
│   Planner   │   Executor    │   Reporter    │
│  (LLM-based │  (Subprocess  │  (HTML/PDF    │
│   planning) │   isolation)  │   reports)    │
├─────────────┴───────────────┴───────────────┤
│                  Modules                     │
│  ┌───────┐ ┌─────────┐ ┌─────────┐         │
│  │ Recon │ │ Scanner │ │ Exploit │         │
│  └───────┘ └─────────┘ └─────────┘         │
│  ┌───────┐ ┌─────────┐                     │
│  │  Web  │ │ Network │                     │
│  └───────┘ └─────────┘                     │
├──────────────────────────────────────────────┤
│              Tool Wrappers                   │
│  Nmap · Nuclei · SQLMap · Gobuster · ...    │
└──────────────────────────────────────────────┘
```

## Screenshots

> *Screenshots coming soon — run `vulcan scan --target` to see the Rich CLI in action.*

## Disclaimer

**Vulcan is intended for authorized security testing only.** Always obtain explicit written permission before testing any systems you do not own. Unauthorized access to computer systems is illegal. The authors assume no liability for misuse of this tool.

## License

MIT License — see [LICENSE](LICENSE) for details.
