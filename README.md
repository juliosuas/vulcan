```
 ██╗   ██╗██╗   ██╗██╗      ██████╗ █████╗ ███╗   ██╗
 ██║   ██║██║   ██║██║     ██╔════╝██╔══██╗████╗  ██║
 ██║   ██║██║   ██║██║     ██║     ███████║██╔██╗ ██║
 ╚██╗ ██╔╝██║   ██║██║     ██║     ██╔══██║██║╚██╗██║
  ╚████╔╝ ╚██████╔╝███████╗╚██████╗██║  ██║██║ ╚████║
   ╚═══╝   ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
```

<h1 align="center">🌋 VULCAN</h1>
<p align="center"><b>AI-Powered Autonomous Penetration Testing Agent</b></p>
<p align="center"><i>Let the AI think. Let the tools execute. Get the report.</i></p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT"></a>
  <a href="https://github.com/juliosuas/vulcan/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build"></a>
  <a href="https://github.com/juliosuas/vulcan/issues"><img src="https://img.shields.io/github/issues/juliosuas/vulcan?style=flat-square" alt="Issues"></a>
  <a href="https://github.com/juliosuas/vulcan/stargazers"><img src="https://img.shields.io/github/stars/juliosuas/vulcan?style=flat-square" alt="Stars"></a>
  <img src="https://img.shields.io/badge/security-pentest-critical?style=flat-square&logo=hackthebox&logoColor=white" alt="Security">
  <img src="https://img.shields.io/badge/AI-Claude%20%7C%20GPT--4-purple?style=flat-square&logo=openai&logoColor=white" alt="AI Powered">
</p>

<p align="center">
  <a href="#-how-it-works">How it Works</a> •
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-comparison">Comparison</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-roadmap">Roadmap</a> •
  <a href="#-contributing">Contributing</a> •
  <a href="#%EF%B8%8F-disclaimer">Disclaimer</a>
</p>

---

## What is Vulcan?

**Vulcan** is an autonomous penetration testing framework that leverages Large Language Models (Claude, GPT-4) to **plan, execute, and report** on security assessments — without constant human intervention.

It uses a **ReAct (Reason → Act → Observe)** loop to intelligently drive the entire pentest pipeline: from reconnaissance through exploitation to professional report generation. Think of it as an AI pentester that wraps industry-standard tools and makes intelligent decisions about what to run next.

> **One command. Full assessment. Professional report.**

---

## 🔄 How it Works

Vulcan operates on a **ReAct loop** — the same reasoning pattern used by autonomous AI agents:

```
                    ┌─────────────────────┐
                    │     🎯 TARGET       │
                    │   example.com       │
                    └─────────┬───────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │         🧠 REASON            │
               │   LLM analyzes current state  │
               │   Plans next action            │
               │   Prioritizes attack surface   │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │          ⚡ ACT              │
               │   Execute selected tool       │
               │   (Nmap, Nuclei, SQLMap...)   │
               │   Subprocess isolation        │
               └──────────────┬───────────────┘
                              │
                              ▼
               ┌──────────────────────────────┐
               │        👁️ OBSERVE            │
               │   Parse tool output           │
               │   Update knowledge base       │
               │   Identify new vectors        │
               └──────────────┬───────────────┘
                              │
                     ┌────────┴────────┐
                     │  More to test?  │
                     └────────┬────────┘
                        Yes ↙     ↘ No
                  (loop back       ▼
                   to REASON)  ┌────────┐
                               │ REPORT │
                               │ 📋     │
                               └────────┘
```

Each iteration refines the attack plan based on discovered information. The LLM decides when to pivot, what to investigate deeper, and when the assessment is complete.

---

## ✨ Features

| Feature | Description | Status |
|---------|-------------|--------|
| 🧠 AI-Driven Planning | LLM-powered attack planning that adapts in real-time | ✅ |
| 🔄 ReAct Loop | Autonomous Reason → Act → Observe cycle | ✅ |
| 📡 Full Recon Pipeline | Subdomains, ports, tech stack, directories | ✅ |
| 🔍 Vulnerability Scanning | Automated vuln discovery with Nuclei + custom checks | ✅ |
| 💉 Exploitation | SQLi, XSS, command injection via integrated tools | ✅ |
| 📊 Professional Reports | HTML/PDF reports with severity ratings & remediation | ✅ |
| 🤖 Multi-LLM Support | Anthropic Claude & OpenAI GPT-4 | ✅ |
| 🖥️ Rich CLI | Beautiful terminal UI with progress bars & tables | ✅ |
| 🌐 Web Dashboard | Single-file HTML dashboard for monitoring | ✅ |
| 🐳 Docker Support | Isolated container environment | ✅ |
| 🔒 Safe Execution | Subprocess isolation with timeouts | ✅ |
| 🧩 Modular Architecture | Easy to extend with new modules | ✅ |

---

## 📦 Installation

### Option 1: pip (Recommended)

```bash
pip install vulcan-pentest
```

### Option 2: From Source

```bash
git clone https://github.com/juliosuas/vulcan.git
cd vulcan
pip install -e .
```

### Option 3: Docker

```bash
git clone https://github.com/juliosuas/vulcan.git
cd vulcan
docker-compose up --build
```

### Configuration

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### External Tools (Optional)

Vulcan gracefully degrades if tools are missing, but for full coverage install:

| Tool | Purpose | Install |
|------|---------|---------|
| [Nmap](https://nmap.org/) | Port scanning & service detection | `apt install nmap` |
| [Nuclei](https://github.com/projectdiscovery/nuclei) | Vulnerability scanning | `go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| [SQLMap](https://sqlmap.org/) | SQL injection testing | `pip install sqlmap` |
| [Gobuster](https://github.com/OJ/gobuster) | Directory & DNS brute-forcing | `go install github.com/OJ/gobuster/v3@latest` |
| [Subfinder](https://github.com/projectdiscovery/subfinder) | Subdomain enumeration | `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |

---

## 🚀 Quick Start

### 1. Quick Scan (fastest)

```bash
vulcan scan --target example.com
```

### 2. Full Assessment with Claude

```bash
vulcan scan --target example.com --mode full --llm claude --report html
```

### 3. Recon Only

```bash
vulcan recon --target example.com --modules subdomains,ports,tech
```

### 4. Generate Report from Existing Data

```bash
vulcan report --input ./vulcan_output/example.com --format pdf
```

### CLI Reference

```
Usage: vulcan [OPTIONS] COMMAND [ARGS]

Commands:
  scan     Run a full penetration test
  recon    Run reconnaissance only
  report   Generate report from scan data

Options:
  --target, -t    Target domain or IP
  --mode, -m      Scan mode: quick | standard | full (default: standard)
  --llm           LLM provider: claude | openai (default: claude)
  --report        Report format: html | pdf | json (default: html)
  --output, -o    Output directory (default: ./vulcan_output)
  --config, -c    Path to config file
  --verbose, -v   Verbose output
  --help          Show this help message
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│                  VulcanAgent                      │
│             (ReAct Orchestrator)                  │
├────────────────┬──────────────┬──────────────────┤
│    Planner     │   Executor   │    Reporter      │
│  (LLM-based   │ (Subprocess  │  (HTML/PDF       │
│   reasoning)   │  isolation)  │   generation)    │
├────────────────┴──────────────┴──────────────────┤
│                   Modules                         │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Recon  │ │ Scanner  │ │ Exploit  │          │
│  └─────────┘ └──────────┘ └──────────┘          │
│  ┌─────────┐ ┌──────────┐                        │
│  │   Web   │ │ Network  │                        │
│  └─────────┘ └──────────┘                        │
├──────────────────────────────────────────────────┤
│               Tool Wrappers                       │
│  Nmap · Nuclei · SQLMap · Gobuster · Subfinder   │
└──────────────────────────────────────────────────┘
```

---

## 📊 Comparison

How does Vulcan compare to existing tools?

| Capability | Vulcan | Metasploit | Burp Suite | Nuclei |
|-----------|--------|------------|------------|--------|
| AI-driven planning | ✅ | ❌ | ❌ | ❌ |
| Autonomous execution | ✅ | ❌ | ❌ | ⚠️ Partial |
| ReAct reasoning loop | ✅ | ❌ | ❌ | ❌ |
| Recon → Exploit → Report | ✅ Full pipeline | ⚠️ Manual | ⚠️ Manual | ❌ Scan only |
| Auto-generated reports | ✅ HTML/PDF | ⚠️ Basic | ✅ | ⚠️ JSON |
| Multi-tool orchestration | ✅ | ❌ Single | ❌ Single | ❌ Single |
| Natural language control | ✅ | ❌ | ❌ | ❌ |
| Open source | ✅ MIT | ✅ | ❌ Commercial | ✅ MIT |
| Docker ready | ✅ | ✅ | ❌ | ✅ |

> **Vulcan doesn't replace these tools — it orchestrates them.** It uses Nmap, Nuclei, SQLMap, and others under the hood, guided by AI decision-making.

---

## 📸 Screenshots

<details>
<summary><b>🖥️ Rich CLI Interface</b></summary>
<br>
<p align="center">
  <i>Screenshot: Terminal output showing scan progress with Rich tables and progress bars</i>
</p>

> Run `vulcan scan --target example.com --verbose` to see it in action.
</details>

<details>
<summary><b>📊 HTML Report</b></summary>
<br>
<p align="center">
  <i>Screenshot: Professional HTML report with findings, severity ratings, and remediation guidance</i>
</p>
</details>

<details>
<summary><b>🌐 Web Dashboard</b></summary>
<br>
<p align="center">
  <i>Screenshot: Real-time web dashboard showing scan progress and discovered findings</i>
</p>
</details>

---

## ✅ Pentest Verification Checklists

Every Vulcan assessment phase includes built-in verification steps to ensure completeness and quality. These checklists are inspired by industry best practices for structured security testing.

### Reconnaissance Verification

| Check | Criteria | How to Confirm |
|-------|----------|----------------|
| Subdomain Coverage | All passive + active sources queried | Compare subfinder, amass, and DNS brute results |
| Port Scan Completeness | Top 1000 ports minimum on all live hosts | Verify nmap scan parameters in output |
| Service Identification | Version strings extracted for all open ports | Check `-sV` results for "unknown" entries |
| Technology Stack | Web technologies fingerprinted | Confirm tech detection ran against all HTTP services |
| Scope Validation | No out-of-scope targets scanned | Cross-reference all scanned IPs/domains against scope document |

### Vulnerability Scanning Verification

| Check | Criteria | How to Confirm |
|-------|----------|----------------|
| Template Coverage | Critical + High severity templates executed | Verify nuclei template count in scan output |
| False Positive Review | Each critical/high finding manually validated | Evidence screenshots or request/response pairs saved |
| CVE Mapping | Findings mapped to CVE identifiers where applicable | CVE column populated in report findings table |
| CVSS Scoring | All findings have CVSS v3.1 scores | No "unscored" entries in final report |
| Remediation Guidance | Each finding has specific fix recommendations | Review report remediation section completeness |

### Exploitation Verification

| Check | Criteria | How to Confirm |
|-------|----------|----------------|
| Authorization Check | Exploitation only on explicitly authorized targets | Scope document reviewed before each exploit attempt |
| Evidence Capture | Proof of exploitation documented | Screenshots, command output, or data samples saved |
| Impact Assessment | Business impact described for each exploit | Impact field populated in findings |
| Cleanup | All test artifacts removed from target | Post-exploitation cleanup checklist completed |
| Chain Documentation | Multi-step exploits documented step-by-step | Attack narrative includes each pivot point |

### Report Quality Verification

| Check | Criteria | How to Confirm |
|-------|----------|----------------|
| Executive Summary | Non-technical overview present | Readable by C-suite without security background |
| Finding Accuracy | No duplicate or contradictory findings | Peer review or AI cross-check completed |
| Severity Distribution | Ratings align with CVSS + business context | No medium finding with critical business impact |
| Remediation Priority | Fixes ordered by risk, not just CVSS | Priority considers exploitability and asset value |
| Evidence Completeness | Each finding has supporting evidence | Every finding links to scan output or screenshots |

---

## 🖥️ Platform Compatibility

| Platform | Architecture | Status | Notes |
|----------|-------------|--------|-------|
| Ubuntu 22.04+ | x86_64, ARM64 | ✅ Full | Recommended — all tools available via apt |
| Debian 12+ | x86_64, ARM64 | ✅ Full | Fully tested |
| Kali Linux | x86_64 | ✅ Full | Most dependencies pre-installed |
| Parrot OS | x86_64 | ✅ Full | Security-focused distribution |
| macOS 13+ | ARM64, x86_64 | ⚠️ Partial | Some tools require Homebrew; nmap works natively |
| Windows 11 | x86_64 (WSL2) | ⚠️ Partial | Run inside WSL2 Ubuntu for best results |
| Docker | Any | ✅ Full | `docker-compose up --build` — isolated and portable |
| Arch Linux | x86_64 | ✅ Full | Community packages available |

### LLM Provider Compatibility

| Provider | Models | Status |
|----------|--------|--------|
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | ✅ Recommended |
| OpenAI | GPT-4, GPT-4 Turbo | ✅ Fully supported |
| Local LLMs | Ollama (Llama 3, Mixtral) | ⚠️ Experimental |

### Tool Compatibility

| Tool | Min Version | Required | Purpose |
|------|------------|----------|---------|
| Python | 3.10+ | ✅ | Core runtime |
| Nmap | 7.80+ | Recommended | Port scanning & service detection |
| Nuclei | 3.0+ | Recommended | Vulnerability scanning |
| SQLMap | 1.7+ | Optional | SQL injection testing |
| Gobuster | 3.5+ | Optional | Directory brute-forcing |
| Subfinder | 2.6+ | Optional | Subdomain enumeration |

---

## 🖥️ Platform Compatibility

| Platform | Architecture | Status | Notes |
|----------|-------------|--------|-------|
| Ubuntu 22.04+ | x86_64, ARM64 | ✅ Full | Recommended platform |
| Debian 12+ | x86_64, ARM64 | ✅ Full | Fully tested |
| Kali Linux | x86_64 | ✅ Full | Most tools pre-installed |
| Parrot OS | x86_64 | ✅ Full | Security tools included |
| macOS 13+ | ARM64 (Apple Silicon) | ✅ Full | Homebrew for tool deps |
| macOS 13+ | x86_64 (Intel) | ✅ Full | Homebrew for tool deps |
| Windows 11 | x86_64 (WSL2) | ⚠️ Partial | WSL2 with Ubuntu recommended |
| Arch Linux | x86_64 | ✅ Full | Community tested |
| Docker | Any | ✅ Full | `docker-compose up` — isolated environment |

### AI Provider Compatibility

| Provider | Models | Status |
|----------|--------|--------|
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | ✅ Recommended |
| OpenAI | GPT-4, GPT-4 Turbo | ✅ Fully tested |
| Local (Ollama) | Llama 3, Mixtral | ⚠️ Experimental |

---

## ✅ Verification & Quality Assurance

Every Vulcan assessment includes built-in verification to ensure finding accuracy and report quality. Use the comprehensive verification checklist to validate results:

📋 **[Full Verification Checklist](docs/verification-checklist.md)** — 35+ checks across 7 categories

### Quick Verification

After any assessment, confirm these critical checks:

| Check | How to Verify | Expected Result |
|-------|--------------|-----------------|
| ReAct loop execution | Review Vulcan logs | Reason → Act → Observe cycle visible |
| Tool execution | Check output for tool results | Tools ran and produced parseable output |
| Finding accuracy | Manually confirm top 3 findings | ≥80% true positive rate |
| Report generation | Open generated report | Structured with exec summary + findings |
| Evidence chain | Follow a finding from detection to proof | Clear, reproducible evidence |
| Scope compliance | Review all tested targets | No out-of-scope systems contacted |
| Cleanup | Check for leftover artifacts on target | Clean target post-assessment |

### Confidence Scoring

| Score | Rating | Action |
|-------|--------|--------|
| 90-100% verified checks | ✅ High Confidence | Report ready for delivery |
| 70-89% verified checks | ⚠️ Moderate | Investigate failures before delivery |
| <70% verified checks | ❌ Low | Re-run affected phases |

---

## 🗺️ Roadmap

- [x] Core ReAct loop with Claude/GPT-4
- [x] Nmap, Nuclei, SQLMap, Gobuster integration
- [x] HTML/PDF report generation
- [x] Rich CLI interface
- [x] Docker support
- [x] Web dashboard
- [ ] 🔜 Plugin system for custom tool integration
- [ ] 🔜 Multi-target campaign mode
- [ ] 🔜 API server mode (REST + WebSocket)
- [ ] 🔜 Collaborative mode (multiple agents)
- [ ] OWASP ZAP integration
- [ ] Custom wordlist management
- [ ] Scan scheduling & cron support
- [ ] Slack/Discord notifications
- [ ] Cloud deployment templates (AWS/GCP)
- [ ] CVSS scoring integration
- [ ] Evidence chain & attack path visualization

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/awesome-feature`
3. **Commit** your changes: `git commit -m 'Add awesome feature'`
4. **Push** to the branch: `git push origin feat/awesome-feature`
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/juliosuas/vulcan.git
cd vulcan
pip install -e ".[dev]"
python -m pytest tests/
```

### Guidelines

- Follow existing code style and patterns
- Add tests for new features
- Update documentation as needed
- Keep PRs focused and atomic

---

## ⚠️ Disclaimer

> **⚠️ IMPORTANT: AUTHORIZED USE ONLY**
>
> Vulcan is designed and intended **exclusively for authorized security testing and educational purposes**.
>
> - **Always** obtain **explicit written permission** before testing any system
> - **Never** use this tool against systems you do not own or have authorization to test
> - Unauthorized access to computer systems is **illegal** in most jurisdictions
> - Users are **solely responsible** for ensuring compliance with all applicable laws
> - The authors and contributors assume **no liability** for misuse of this software
>
> By using Vulcan, you agree to use it responsibly and legally. When in doubt, **don't test it**.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <b>Built with 🌋 by the Vulcan Team</b><br>
  <sub>If Vulcan helps your security work, consider giving it a ⭐</sub>
</p>

---
### 🌱 Also check out
**[AI Garden](https://github.com/juliosuas/ai-garden)** — A living world built exclusively by AI agents. Watch it grow.
