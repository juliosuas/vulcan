```
 ██╗   ██╗██╗   ██╗██╗      ██████╗ █████╗ ███╗   ██╗
 ██║   ██║██║   ██║██║     ██╔════╝██╔══██╗████╗  ██║
 ██║   ██║██║   ██║██║     ██║     ███████║██╔██╗ ██║
 ╚██╗ ██╔╝██║   ██║██║     ██║     ██╔══██║██║╚██╗██║
  ╚████╔╝ ╚██████╔╝███████╗╚██████╗██║  ██║██║ ╚████║
   ╚═══╝   ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
```

<h1 align="center">🌋 VULCAN</h1>
<p align="center"><b>The Sovereign AI Pentester</b></p>
<p align="center"><i>Full-local. Zero API keys. 117 tools. One command.</i></p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/v2.0-BESTIA_MODE-red?style=for-the-badge" alt="v2.0 Bestia Mode">
  <img src="https://img.shields.io/badge/tools-117+-orange?style=for-the-badge&logo=hackthebox&logoColor=white" alt="117 Tools">
  <img src="https://img.shields.io/badge/AI-local_%7C_cloud_%7C_hybrid-purple?style=for-the-badge&logo=openai&logoColor=white" alt="Multi LLM">
  <img src="https://img.shields.io/badge/data-sovereign-black?style=for-the-badge&logo=tor&logoColor=white" alt="Data Sovereign">
</p>

<p align="center">
  <a href="#-why-vulcan">Why Vulcan</a> •
  <a href="#-60-second-quick-start">60-Second Quick Start</a> •
  <a href="#-three-modes-one-binary">Three Modes</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-how-vulcan-fits-the-landscape">Landscape</a> •
  <a href="#-roadmap">Roadmap</a> •
  <a href="#%EF%B8%8F-disclaimer">Disclaimer</a>
</p>

---

> ### ⚡ **v2.0 — BESTIA Mode just dropped.**
> One command. Full pentest. **No API keys. No egress. No vendor lock-in.**
> 117 security tools orchestrated by a ReAct-loop AI agent running entirely on your metal.
> ```bash
> ./run-beast.sh scanme.nmap.org
> ```

---

## 🤔 Why Vulcan?

Existing pentest automation forces you to choose:

- **Cloud AI** (Burp, commercial scanners) → your target data leaves the perimeter.
- **Scriptable tools** (Metasploit, Nuclei) → powerful, but *you* still plan every step.
- **LLM wrappers** (Claude Code, Copilot) → great for ideation, useless without tool execution.

**Vulcan fuses all three.** A ReAct-loop agent plans the attack. A 127-tool API executes it. An LLM — cloud *or* local — drives decisions. Everything flows into a professional HTML/PDF report. Assessment-ready in one command.

> The AI thinks. The tools execute. You get the report.

### 🎯 Who this is for

- **Red teamers** who want a force-multiplier, not a replacement.
- **CTF players** who want autonomous recon → exploit chains on HackTheBox / TryHackMe / VulnHub boxes.
- **Bug bounty hunters** who need to cover wide scope fast.
- **Security researchers** who refuse to ship target data to third-party clouds.
- **Consultants** whose clients demand 100% on-prem tooling.

---

## ⚡ 60-Second Quick Start

```bash
# Clone
git clone https://github.com/juliosuas/vulcan.git && cd vulcan

# Install
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run — full autonomous pentest, local-only (no API keys required)
./run-beast.sh scanme.nmap.org
```

That's it. `run-beast.sh` auto-launches the HexStrike API, warms your local LLM, runs the full ReAct pipeline, and opens the HTML report in your browser.

**Want to use Claude instead?**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
vulcan scan --target example.com --llm claude --hexstrike
```

**Want classic subprocess-only mode?**
```bash
vulcan scan --target example.com --llm claude
```

---

## 🔥 Three Modes. One Binary.

Vulcan exposes two orthogonal axes — the LLM provider and the execution backend — giving you four deployment profiles:

| Mode | Command | LLM | Tools | API keys | Egress | When to use |
|------|---------|:---:|:---:|:---:|:---:|---|
| 🔴 **BESTIA** (full-local) | `./run-beast.sh <target>` | smart-llm (Ollama, local) | HexStrike API (117 tools) | ❌ none | ❌ zero | Air-gapped labs · sensitive clients · CTF grind |
| 🟡 **Hybrid** | `--llm claude --hexstrike` | Claude / GPT-4 | HexStrike API (117 tools) | ✅ LLM only | ⚠️ reasoning only | Best-of-both: heavy iron executing, frontier model thinking |
| 🟢 **Cloud classic** | `--llm claude` | Claude / GPT-4 | Local subprocess (5 tools) | ✅ LLM only | ⚠️ reasoning only | Laptop, fast iteration, full frontier reasoning |
| ⚫ **OSS-only** | `--llm openai` + Ollama base URL | Local Ollama model | Local subprocess | ❌ none | ❌ zero | Legacy hosts, minimal install |

**Why this matters:** most "AI pentest" tools lock you into one cloud LLM *and* one tool orchestration choice. Vulcan lets you mix them independently — and switch modes with a single flag.

---

## 🧠 How It Works

Vulcan runs a **ReAct (Reason → Act → Observe)** loop — the canonical autonomous-agent pattern — across four phases:

```
                    ┌─────────────────────┐
                    │     🎯 TARGET       │
                    │   example.com       │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  RECON   │   │ PLANNING │   │ EXECUTION│
        │ (auto)   │→ │  (LLM)   │→ │ (ReAct)  │
        └──────────┘   └──────────┘   └─────┬────┘
                                            │
                                            ▼
                                      ┌──────────┐
                                      │  REPORT  │
                                      │ HTML/PDF │
                                      └──────────┘
```

Inside the execution phase, every iteration:

```
🧠 REASON  ──►  LLM reads state, picks next action, emits JSON
⚡  ACT     ──►  Vulcan dispatches to module → Executor → tool
👁️  OBSERVE ──►  Parse output, extract findings, update conversation
         ↑                                                    │
         └────────────────── loop ←─────────────────────────┘
                     (up to max_iterations=50)
```

The LLM decides when to pivot, what to investigate deeper, when to drop a thread, and when the assessment is complete.

---

## ✨ Features

| Feature | Description | v1 | v2 |
|---|---|:---:|:---:|
| 🧠 AI-driven attack planning | LLM plans & re-plans in real time | ✅ | ✅ |
| 🔄 ReAct (Reason → Act → Observe) loop | Canonical autonomous-agent pattern | ✅ | ✅ |
| 📡 Full recon pipeline | Subdomains · ports · tech · dirs · DNS | ✅ | ✅ |
| 🔍 Automated vuln scanning | Nuclei + custom checks | ✅ | ✅ |
| 💉 Exploitation modules | SQLi · XSS · SSRF · CMD injection | ✅ | ✅ |
| 📊 Professional reports | HTML (validated) + PDF via weasyprint (optional) | ✅ | ✅ |
| 🤖 Claude / GPT-4 support | Frontier cloud LLMs | ✅ | ✅ |
| 🖥️ Rich CLI | Beautiful terminal UI | ✅ | ✅ |
| 🐳 Docker | Isolated execution | ✅ | ✅ |
| 🔴 **BESTIA mode** | **Full-local, zero API keys** | — | ✅ |
| ⚔️ **HexStrike integration** | **5 → 127 security tools** | — | ✅ |
| 🚀 **smart-llm routing** | **Local Ollama via heuristic router** | — | ✅ |
| 🛡️ **Data sovereignty** | **Target data never leaves your host** | — | ✅ |
| 🔀 **Mix-and-match modes** | **LLM × executor independent axes** | — | ✅ |
| 🧩 **Graceful fallback** | **Auto-fallback to local subprocess if API down** | — | ✅ |

---

## 📊 How Vulcan fits the landscape

| Capability | Vulcan v2 | Metasploit | Burp Pro | Nuclei |
|---|:---:|:---:|:---:|:---:|
| AI-driven planning | ✅ | ❌ | ❌ | ❌ |
| Autonomous ReAct loop | ✅ | ❌ | ❌ | ❌ |
| Recon → Exploit → Report pipeline | ✅ | ⚠️ Manual | ⚠️ Manual | ❌ Scan only |
| Multi-tool orchestration | ✅ 117 tools | ❌ Single | ❌ Single | ❌ Single |
| Runs 100% local (no cloud) | ✅ | ✅ | ❌ | ✅ |
| **Local LLM reasoning** | ✅ | ❌ | ❌ | ❌ |
| **Zero egress mode** | ✅ | ✅ | ❌ | ✅ |
| Auto-generated reports | ✅ HTML (PDF opt.) | ⚠️ Basic | ✅ | ⚠️ JSON |
| Natural language control | ✅ | ❌ | ❌ | ❌ |
| Open source | ✅ MIT | ✅ | ❌ | ✅ MIT |
| Docker ready | ✅ | ✅ | ❌ | ✅ |

> **Vulcan doesn't replace these tools — it orchestrates them.** Nmap, Nuclei, SQLMap, Gobuster, Subfinder, Hydra, NetExec, MSFVenom, Hashcat, FFuf, WPScan, Amass, and 100+ more run underneath, guided by AI.
>
> *Other autonomous-pentest projects exist (PentestGPT, Shennina, etc.) — Vulcan's differentiator is the independently swappable LLM × executor axes and the full-local BESTIA mode.*

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VulcanAgent                               │
│                    (ReAct Orchestrator)                          │
├──────────────┬──────────────────┬──────────────┬────────────────┤
│   Planner    │      LLM         │   Executor   │   Reporter     │
│  (strategy)  │ ─────────────    │ ─────────────│ (HTML/PDF/JSON)│
│              │  • Anthropic     │  • Subproc   │                │
│              │  • OpenAI        │  • HexStrike │                │
│              │  • smart-llm ⚡  │    API :8888 │                │
├──────────────┴──────────────────┴──────────────┴────────────────┤
│                             Modules                              │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ ┌──────────┐   │
│  │  Recon  │ │ Scanner  │ │ Exploit  │ │ Web  │ │ Network  │   │
│  └─────────┘ └──────────┘ └──────────┘ └──────┘ └──────────┘   │
├──────────────────────────────────────────────────────────────────┤
│                       Execution Layer                            │
│   Local subprocess  ◄─────── OR ───────►  HexStrike API :8888   │
│   (5 tools by default)                     (117 tools, shared)   │
└──────────────────────────────────────────────────────────────────┘
```

### The key insight

Vulcan's executor is **swappable at init time**:

- `Executor` → runs `nmap -sV target` via `asyncio.create_subprocess_shell` on localhost.
- `HexStrikeExecutor` → parses the same command, POSTs to `/api/tools/nmap` on a remote HexStrike server, returns the same `ExecutionResult`.

**Modules, tool wrappers, and the ReAct loop don't change.** You swap the executor with `--hexstrike` and you're now orchestrating 117 tools instead of 5, with caching, concurrency, and graceful fallback baked in.

---

## 🚀 Installation

### Option 1: Full install (recommended)

```bash
git clone https://github.com/juliosuas/vulcan.git
cd vulcan
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Option 2: Docker

```bash
git clone https://github.com/juliosuas/vulcan.git
cd vulcan
docker compose up --build
```

### Option 3: Pip (coming soon)

```bash
pip install vulcan-pentest
```

### Config

```bash
cp .env.example .env
# Edit .env with your keys (optional — BESTIA mode needs none)
```

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
VULCAN_LLM_PROVIDER=smartllm        # claude | openai | smartllm
VULCAN_USE_HEXSTRIKE=1              # route through HexStrike :8888
VULCAN_HEXSTRIKE_SERVER=http://127.0.0.1:8888
VULCAN_SMARTLLM_BIN=smart-llm       # or absolute path
```

### Optional: local LLM stack (for BESTIA mode)

Install [Ollama](https://ollama.com), pull a model, and install [`smart-llm`](https://github.com/juliosuas/smart-llm) (the heuristic router):

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:32b        # recommended for reasoning
ollama pull qwen2.5-coder:7b # for code/payload tasks
```

### Optional: HexStrike AI (for 127-tool mode)

```bash
git clone https://github.com/0x4m4/hexstrike-ai.git
cd hexstrike-ai && python3 -m venv hexstrike-env && source hexstrike-env/bin/activate
pip install -r requirements.txt
./hexstrike_server.py   # Flask API on :8888
```

---

## 📖 Usage

### BESTIA — zero keys, full pipeline

```bash
./run-beast.sh <target> [quick|standard|full]
```

### Classic scan (cloud LLM)

```bash
vulcan scan --target example.com --llm claude --mode full
```

### Hybrid (cloud LLM + HexStrike)

```bash
vulcan scan --target example.com --llm claude --hexstrike
```

### Recon only

```bash
vulcan recon --target example.com --modules subdomains,ports,tech,dirs,dns
```

### Generate report from existing data

```bash
vulcan report --input ./vulcan_output/example.com --format html
# PDF: pip install weasyprint && vulcan report --input ./vulcan_output/example.com --format pdf
```

### All flags

```
vulcan scan --help

  --target, -t               Target domain or IP              [required]
  --mode, -m                 quick | standard | full          [standard]
  --llm                      claude | openai | smartllm       [claude]
  --local                    Shortcut: --llm smartllm --hexstrike
  --hexstrike/--no-hexstrike Route tools through HexStrike    [off]
  --hexstrike-url            HexStrike server URL             [http://127.0.0.1:8888]
  --report                   html | pdf | json                [html]
  --output, -o               Output directory                 [./vulcan_output]
  --config, -c               YAML config path
  --verbose, -v              Verbose output
```

---

## 🔬 How BESTIA Mode Works Under the Hood

```
┌─────────────────────────────────────────────────────────┐
│  ./run-beast.sh scanme.nmap.org                         │
└──────────┬──────────────────────────────────────────────┘
           │
    ┌──────▼──────────┐        ┌──────────────────────┐
    │ Preflight       │───────►│ curl :8888/health    │
    │                 │        │ if down → start      │
    └──────┬──────────┘        └──────────────────────┘
           │
    ┌──────▼──────────┐        ┌──────────────────────┐
    │ Warm smart-llm  │───────►│ Ollama models → VRAM │
    │                 │        │ (avoid cold-start)   │
    └──────┬──────────┘        └──────────────────────┘
           │
    ┌──────▼──────────┐
    │ vulcan scan     │──── ReAct loop ──► smart-llm (qwen3:32b)
    │   --local       │                         │
    │                 │                         ▼
    │                 │                    JSON action
    │                 │                         │
    │                 │         ┌───────────────┘
    │                 ▼         ▼
    │        ┌────────────────────────┐
    │        │  HexStrikeExecutor     │──POST /api/tools/nmap──►  HexStrike :8888
    │        │  (aiohttp + semaphore) │                           │
    │        │                        │◄───JSON result─────────── ↓
    │        └────────────────────────┘                      [subprocess · caching · recovery]
    │                 │
    │                 ▼
    │        Finding extracted → Reporter
    │
    └──► xdg-open vulcan_output/*.html
```

Every component degrades gracefully:
- **HexStrike down** → `HexStrikeExecutor.fallback_local=True` silently falls back to subprocess.
- **smart-llm missing** → raises with exact env var to set.
- **Model cold** → `run-beast.sh --warmup` keeps them hot in VRAM with `keep_alive=24h`.

---

## ✅ Built-in Pentest Verification

Every Vulcan run includes verification checklists inspired by industry methodology:

### Reconnaissance
| Check | Criteria | How to confirm |
|---|---|---|
| Subdomain coverage | All passive + active sources queried | Compare subfinder/amass/DNS results |
| Port scan completeness | Top 1000+ on all live hosts | Verify nmap params in output |
| Service identification | Versions extracted for all open ports | Check `-sV` for "unknown" entries |
| Scope compliance | No out-of-scope targets contacted | Cross-reference scope doc |

### Vulnerability Scanning
| Check | Criteria | How to confirm |
|---|---|---|
| Template coverage | Critical + High executed | Verify nuclei template count |
| False-positive review | Each critical/high validated | Request/response pairs saved |
| CVE mapping | Findings mapped to CVE IDs | CVE column populated in report |
| Remediation guidance | Fix rec per finding | Review report remediation section |

### Exploitation
| Check | Criteria | How to confirm |
|---|---|---|
| Authorization | Explicit written permission | Scope doc reviewed before exploit |
| Evidence capture | Proof documented | Screenshots / request-response saved |
| Impact assessment | Business impact described | Impact field populated |
| Cleanup | All test artifacts removed | Post-exploitation checklist done |

### Report Quality
| Check | Criteria | How to confirm |
|---|---|---|
| Exec summary | Non-technical overview present | Readable by C-suite |
| Finding accuracy | No dupes/contradictions | Peer review or AI cross-check |
| Severity distribution | Aligns with CVSS + business context | No Medium with Critical impact |
| Remediation priority | Ordered by risk, not CVSS alone | Considers exploitability + asset value |

---

## 🖥️ Platform Compatibility

| Platform | Status | Notes |
|---|:---:|---|
| Debian 12 | ✅ Tested | Primary dev + validation platform |
| Kali / Parrot | 🟢 Expected | Derivatives of Debian; most tools pre-installed |
| Ubuntu 22.04+ | 🟢 Expected | Debian-family; should work out of the box |
| Arch / Fedora | 🟡 Untested | Python deps portable; tool install paths differ |
| macOS 13+ (Apple Silicon) | 🟡 Untested | Homebrew for Nmap/Nuclei; Ollama native |
| Windows 11 (WSL2) | 🟡 Untested | Run inside Ubuntu for best results |
| Docker | 🟢 Expected | `docker compose up --build` (Dockerfile + compose file shipped, validation pending) |

> **Current validation status (v2.0):** end-to-end pipeline (recon → planning → ReAct → HTML report) validated against `scanme.nmap.org` on Debian 12 in both `--local` (BESTIA) and `--llm claude --hexstrike` (hybrid) modes. PDF export uses `weasyprint` (optional dep, untested this release). Other platforms expected to work but not independently verified yet — PRs confirming are welcome.

### LLM Compatibility

| Provider | Models | BESTIA? | Notes |
|---|---|:---:|---|
| Anthropic | Claude Sonnet 4 / Opus | ❌ (cloud) | Recommended for frontier reasoning |
| OpenAI | GPT-4o / GPT-4 Turbo | ❌ (cloud) | Fully supported |
| **smart-llm + Ollama** | **qwen3:32b / qwen2.5-coder:7b** | ✅ | **Default in BESTIA mode** |
| LiteLLM proxy | 100+ models | ⚠️ Experimental | Via OpenAI-compatible base URL |

---

## 🗺️ Roadmap

- [x] Core ReAct loop with Claude/GPT-4
- [x] Recon · Scanner · Exploit · Web · Network modules
- [x] HTML/PDF/JSON report generation
- [x] Rich CLI + beautiful terminal UI
- [x] Docker support
- [x] **v2.0 — HexStrike integration (117 tools)**
- [x] **v2.0 — smart-llm local-only mode**
- [x] **v2.0 — Graceful subprocess fallback**
- [x] **v2.0 — Hybrid mode (cloud LLM + local exec)**
- [ ] 🔜 Plugin system for custom tool integration
- [ ] 🔜 Multi-target campaign mode
- [ ] 🔜 API server mode (REST + WebSocket)
- [ ] 🔜 Collaborative mode (agent swarms)
- [ ] 🔜 MITRE ATT&CK mapping per finding
- [ ] 🔜 Evidence chain visualization (graph)
- [ ] 🔜 OWASP ZAP integration
- [ ] 🔜 Slack / Discord / Telegram webhooks
- [ ] 🔜 Cloud deployment templates (AWS/GCP)
- [ ] 🔜 CTF-specific heuristics (flag sniffing, well-known ports)
- [ ] 🔜 Replay mode (re-run from cached output, zero tool exec)

---

## 🤝 Contributing

PRs are welcome — especially new tool wrappers, additional LLM providers, and report templates.

1. Fork → `git checkout -b feat/your-feature`
2. `pip install -e ".[dev]"`
3. `python -m pytest tests/`
4. Open a PR with a clear description

### Guidelines
- Follow existing code style (Black, 100 char lines)
- Add tests for new features
- Keep PRs focused and atomic
- New tool wrappers must subclass `ToolWrapper` in `tools/wrapper.py`
- New LLM providers must implement `_call_llm()` in `core/agent.py`

---

## ⚠️ Disclaimer

> **⚠️ AUTHORIZED USE ONLY**
>
> Vulcan is designed **exclusively for authorized security testing and educational purposes**.
>
> - **Always** obtain **explicit written permission** before testing any system.
> - **Never** use this tool against systems you do not own or have authorization to test.
> - Unauthorized access to computer systems is **illegal** in most jurisdictions.
> - Users are **solely responsible** for ensuring compliance with all applicable laws.
> - The authors and contributors assume **no liability** for misuse.
>
> By using Vulcan, you agree to use it responsibly and legally. When in doubt, **don't run it**.

**Legal testing sandboxes to learn on:** `scanme.nmap.org` · [HackTheBox](https://hackthebox.com) · [TryHackMe](https://tryhackme.com) · [VulnHub](https://vulnhub.com) · [DVWA](https://github.com/digininja/DVWA) · [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/).

---

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  <b>Built with 🌋 by <a href="https://github.com/juliosuas">@juliosuas</a></b><br>
  <sub>If Vulcan saves you a weekend, consider dropping a ⭐</sub>
</p>

<p align="center">
  <a href="https://github.com/juliosuas/vulcan/stargazers"><img src="https://img.shields.io/github/stars/juliosuas/vulcan?style=social" alt="Stars"></a>
  <a href="https://github.com/juliosuas/vulcan/network/members"><img src="https://img.shields.io/github/forks/juliosuas/vulcan?style=social" alt="Forks"></a>
  <a href="https://github.com/juliosuas/vulcan/watchers"><img src="https://img.shields.io/github/watchers/juliosuas/vulcan?style=social" alt="Watchers"></a>
</p>

---

### 🌱 Also from @juliosuas
- **[Ghost](https://github.com/juliosuas/ghost)** — AI-powered OSINT platform
- **[Phantom](https://github.com/juliosuas/phantom)** — LLM red teaming · OWASP Top 10 for LLMs
- **[Sentinel](https://github.com/juliosuas/sentinel)** — AI-powered SOC · real-time log analysis
- **[Cerberus](https://github.com/juliosuas/cerberus)** — Security-as-a-Service for SMBs
- **[AI Garden](https://github.com/juliosuas/ai-garden)** — A pixel-art world built by AI agents. Watch it grow.

### 🙏 Built on top of
- **[HexStrike AI](https://github.com/0x4m4/hexstrike-ai)** by [@0x4m4](https://github.com/0x4m4) — the 117-tool Flask API that powers BESTIA mode's execution layer.
- **[Ollama](https://ollama.com)** — the local LLM runtime.
