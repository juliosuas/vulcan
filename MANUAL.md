# Vulcan — Manual de Usuario

> Manual práctico para operar Vulcan en sus tres modos (cloud, híbrido, bestia).

---

## 1. ¿Qué es Vulcan?

Vulcan es un **agente autónomo de pentesting** basado en un loop ReAct (Reason → Act → Observe).

Dado un target, ejecuta cuatro fases:

1. **Reconnaissance** — port scan, subdomain enum, tech detect, dir bruteforce, DNS enum
2. **Attack Planning** — el LLM genera un plan priorizado a partir de la data de recon
3. **Execution** — loop ReAct: el LLM decide la siguiente acción, se ejecuta, se observa el resultado
4. **Reporting** — reporte HTML con findings, comandos ejecutados y cronología

## 2. Los tres modos

| Modo | Cerebro (razonamiento) | Manos (ejecución) | API key |
|---|---|---|---|
| **cloud** | Claude/OpenAI | Subprocess local | Sí (`ANTHROPIC_API_KEY` u `OPENAI_API_KEY`) |
| **híbrido** | Claude/OpenAI | HexStrike server (:8888) | Sí |
| **bestia** (`--local`) | smart-llm → Ollama local | HexStrike server | **No — zero egress** |

## 3. Instalación / arranque rápido

```bash
# Desde ~/Desktop/cybersec/99-mis-proyectos/vulcan/
source venv/bin/activate
pip install -r requirements.txt   # la primera vez
```

### Modo bestia (el que más vale — full local)

```bash
./run-beast.sh scanme.nmap.org quick
```

Este script:
1. Verifica que el servidor HexStrike esté vivo en `:8888`; si no, lo arranca
2. Hace `smart-llm --warmup` (evita cold-start de 30s en la primera iteración)
3. Corre `python -m ui.cli scan --target <x> --local --mode <modo>`
4. Abre el reporte HTML al terminar

### Modo cloud (clásico)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python -m ui.cli scan --target example.com --llm claude --mode standard
```

### Modo híbrido (Claude razona, HexStrike ejecuta las 117 tools)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Arranca HexStrike en otra terminal:
~/Desktop/cybersec/08-exploitation-tools/hexstrike-ai/start-server.sh

python -m ui.cli scan --target example.com --llm claude --hexstrike --mode full
```

## 4. Flags de la CLI

| Flag | Default | Notas |
|---|---|---|
| `--target <host>` | (requerido) | Host o IP objetivo |
| `--mode {quick,standard,full}` | `standard` | `quick`: solo ports. `full`: agrega dir bruteforce + DNS enum |
| `--llm {claude,openai,smartllm}` | `claude` | Quién razona |
| `--local` | off | Shortcut de `--llm smartllm --hexstrike` |
| `--hexstrike/--no-hexstrike` | off | Rutea los comandos al API de HexStrike en lugar de subprocess |
| `--hexstrike-url <url>` | `http://127.0.0.1:8888` | Server HexStrike (útil para pivotear a otro host) |
| `--max-iterations <n>` | `50` | Tope del loop ReAct |
| `--output-dir <path>` | `vulcan_output/` | Donde se escribe el HTML |

## 5. Variables de entorno

```bash
export VULCAN_LLM_PROVIDER=smartllm     # equivalente a --local (sin --hexstrike)
export VULCAN_USE_HEXSTRIKE=1           # equivalente a --hexstrike
export VULCAN_HEXSTRIKE_SERVER=http://127.0.0.1:8888
export VULCAN_SMARTLLM_BIN=/ruta/absoluta/a/smart-llm
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
```

## 6. Cómo agregar un wrapper de tool nuevo

Hoy Vulcan tiene cinco módulos (`recon`, `scanner`, `exploit`, `web`, `network`) que usan el `Executor` para lanzar comandos.

Para agregar una tool nueva (ej. `amass`):

1. Añade un método en el módulo que corresponda (ej. `modules/recon.py`):

   ```python
   async def amass_enum(self, target: str) -> dict:
       result = await self.executor.run(f"amass enum -d {target}", tool="amass")
       return {"output": result.stdout, "findings": []}
   ```

2. Actualiza `REACT_SYSTEM_PROMPT` en `core/agent.py` listando la nueva firma. **Esto es importante:** el LLM sólo llama funciones que aparecen en ese prompt.

3. Si la tool está en el catálogo de HexStrike (`/api/tools/<tool>`), el `HexStrikeExecutor` la rutea automáticamente; si no, cae a subprocess local.

## 7. Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `smart-llm: command not found` | `~/.local/bin` no está en PATH | `export VULCAN_SMARTLLM_BIN=$(which smart-llm)` o absoluto |
| `HexStrike request failed` | Server down o en `initializing` | `curl http://127.0.0.1:8888/health`; esperar 10-15s tras arrancarlo |
| `openai.AuthenticationError: 401` | Olvidaste `export OPENAI_API_KEY` o `--llm smartllm` | Usa `--local` si no quieres keys |
| `return_code=-1` en todos los tool calls | HexStrike en estado `initializing` | Espera y reintenta |
| Cold start de ~30s en primera iteración | smart-llm está cargando qwen3:32b | Normal, garantizado con `smart-llm --warmup` que hace `run-beast.sh` |
| El LLM llama funciones inexistentes | `REACT_SYSTEM_PROMPT` desactualizado | Agrega la firma correcta en ese prompt |

Logs útiles:
- `/tmp/hexstrike-beast.log` — salida del server HexStrike
- `vulcan_output/vulcan_<target>_<timestamp>.report.html` — reporte final
- `vulcan_output/` — también guarda JSON con la cronología completa

## 8. Flujo recomendado por escenario

### CTF web (scope = 1 host, rápido)
```bash
./run-beast.sh ctf-target.htb quick
```

### Pentest autorizado contra externo (scope amplio)
```bash
export ANTHROPIC_API_KEY=...
python -m ui.cli scan --target cliente.com --llm claude --hexstrike --mode full
```

### Lab en casa (sin internet, total offline)
```bash
./run-beast.sh 192.168.56.10 standard
```

## 9. Seguridad y uso autorizado

**Importante:** todas las tools invocadas por Vulcan son de doble uso. Solo ejecuta scans contra:
- Sistemas propios o de lab
- Pentesting con contrato y scope escrito
- CTFs y challenges autorizados
- Hosts públicos de test como `scanme.nmap.org`

Ejecutar contra un host sin autorización = probable delito, dependiendo de jurisdicción.

---

Ver también:
- `INTEGRATION.md` — detalle técnico de la integración Vulcan × HexStrike × smart-llm
- `README.md` — overview del proyecto
- `~/Desktop/cybersec/EXTERNAL-LINKS.md` — cómo encaja Vulcan en el workspace completo
