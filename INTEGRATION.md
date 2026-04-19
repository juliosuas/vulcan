# Vulcan × HexStrike × smart-llm — Integration Guide

> "Bestia en IA" — full-local autonomous pentest pipeline.

Vulcan ahora tiene dos ejes independientes combinables:

| Eje | Flag | Qué hace |
|---|---|---|
| **LLM provider** | `--llm {claude,openai,smartllm}` | Quién razona (el "cerebro") |
| **Tool execution** | `--hexstrike` / `--no-hexstrike` | Dónde se ejecutan las tools (local o API HexStrike) |
| **Shortcut** | `--local` | Equivalente a `--llm smartllm --hexstrike` (full-local, sin API keys) |

## Modos

### 1. Modo clásico (cloud)
```bash
export ANTHROPIC_API_KEY=...
python3 -m ui.cli scan --target example.com --llm claude
```
Todo local excepto el LLM. Requiere API key.

### 2. Modo híbrido
```bash
export ANTHROPIC_API_KEY=...
python3 -m ui.cli scan --target example.com --llm claude --hexstrike
```
Claude razona, HexStrike ejecuta las tools (útil cuando el host tiene 127 tools instaladas vs el laptop local).

### 3. Modo local (la "bestia")
```bash
./run-beast.sh example.com
```
Equivalente a `--local`: smart-llm razona (modelos Ollama en VRAM), HexStrike ejecuta. **Cero API keys, cero egress.**

## Requisitos por modo

| Modo | API key | smart-llm | HexStrike server :8888 | Tools locales |
|---|:---:|:---:|:---:|:---:|
| claude | ✅ | — | — | ✅ |
| openai | ✅ | — | — | ✅ |
| claude + hexstrike | ✅ | — | ✅ | — |
| smartllm | — | ✅ | — | ✅ |
| **bestia (`--local`)** | — | ✅ | ✅ | — |

## Env vars disponibles
- `VULCAN_LLM_PROVIDER=claude|openai|smartllm`
- `VULCAN_USE_HEXSTRIKE=1`
- `VULCAN_HEXSTRIKE_SERVER=http://127.0.0.1:8888`
- `VULCAN_SMARTLLM_BIN=smart-llm` (o path absoluto)
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`

## Archivos añadidos/modificados
- `core/hexstrike_executor.py` — nuevo, `HexStrikeExecutor(Executor)` que routea comandos al `/api/tools/<x>` del server
- `core/config.py` — flags `use_hexstrike`, `hexstrike_server`, `smartllm_binary` + provider `smartllm` acepta sin API key
- `core/agent.py` — swap condicional del executor + método `_call_smartllm()` vía subprocess
- `ui/cli.py` — flags `--local`, `--hexstrike/--no-hexstrike`, `--hexstrike-url`
- `run-beast.sh` — pipeline wrapper (arranca server, warm models, corre scan, abre reporte)

## Verificación rápida

```bash
# Sintaxis
python3 -c "import ast; [ast.parse(open(f).read()) for f in ['core/config.py','core/agent.py','core/hexstrike_executor.py','ui/cli.py']]"

# CLI help muestra nuevos flags
source venv/bin/activate && python3 -m ui.cli scan --help | grep -E "local|hexstrike"

# Health del HexStrike server
curl -s http://127.0.0.1:8888/health | head -c 200

# Smart-llm responde
smart-llm "say hi"

# End-to-end (target legal)
./run-beast.sh scanme.nmap.org quick
```

## Troubleshooting
- **`smart-llm: command not found`** → asegúrate `~/.local/bin` está en PATH, o define `VULCAN_SMARTLLM_BIN=/ruta/absoluta`.
- **`HexStrike request failed`** → fallback automático a subprocess local activo (ver `core/hexstrike_executor.py:HexStrikeExecutor(fallback_local=True)`). Revisa `/tmp/hexstrike-beast.log`.
- **`return_code=-1` en todos los tool calls** → probablemente el server está en `initializing`; espera 10-15s tras arrancarlo.
- **Cold start de ~30s en primera iteración ReAct** → normal, smart-llm carga qwen3:32b en VRAM. Warm garantizado por `run-beast.sh`.
