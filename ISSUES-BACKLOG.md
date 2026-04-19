# Vulcan — Issues Backlog (roadmap)

> Drafts listos para crear en `github.com/juliosuas/vulcan/issues`. Listar con `gh issue list`, crear con `gh issue create -F issues/XX.md`.

---

## 🐛 #01 — `aiohttp` Unclosed client session warning al final del scan

**Labels:** `bug`, `good first issue`

**Resumen:** tras Phase 4, sale un warning `Unclosed client session: client_session: <aiohttp.client.ClientSession>`. No bloquea el reporte pero ensucia el output.

**Causa probable:** `HexStrikeExecutor` crea una `ClientSession` pero no llama `close()` al final del run.

**Reproducir:**
```bash
./run-beast.sh scanme.nmap.org quick 2>&1 | tail -5
```

**Fix propuesto:** manejar el lifecycle en `VulcanAgent.run()` (try/finally con `await self.executor.aclose()` si existe).

---

## 🐛 #02 — El LLM llama funciones con nombres inventados

**Labels:** `bug`, `reliability`

**Resumen:** observado con `--local` contra `scanme.nmap.org`: smart-llm llamó `port_scanning` en vez de `port_scan`, `nuclei_scanning` en vez de `nuclei_scan`, `service_enumeration` en vez de `service_enum`.

**Fix aplicado (parcial):** `REACT_SYSTEM_PROMPT` ahora incluye el registry explícito de las 22 firmas disponibles.

**Fix completo (pendiente):** agregar validación defensiva en `_execute_action` que sugiera la función más parecida con `difflib.get_close_matches` cuando el nombre no existe (feedback al siguiente turno del loop).

---

## ✨ #03 — Plugin system para tools externas

**Labels:** `enhancement`, `architecture`

**Resumen:** hoy las tools están hardcoded en los módulos. Para que un usuario agregue una tool nueva necesita editar Vulcan core.

**Propuesta:** discoverable plugins vía entry points (`vulcan.plugins` en `pyproject.toml`) o un directorio `~/.vulcan/plugins/` con archivos `.py` que registren wrappers.

**Beneficio:** la comunidad puede publicar plugins sin fork.

---

## ✨ #04 — REST API + WebSocket para UI real-time

**Labels:** `enhancement`, `api`

**Resumen:** Vulcan es CLI-only. Un servidor REST permitiría integrarlo con dashboards, Slack bots, o un frontend web.

**Endpoints mínimos:**
- `POST /scans` — arranca un scan, retorna `scan_id`
- `GET /scans/<id>` — estado + findings acumulados
- `WS /scans/<id>/events` — stream de eventos ReAct

---

## ✨ #05 — Campaign mode (múltiples targets con coordinación)

**Labels:** `enhancement`, `feature`

**Resumen:** hoy un scan = un target. Un pentest real suele abarcar 10-50 hosts.

**Propuesta:** `vulcan campaign --scope scope.txt --mode full` donde `scope.txt` lista hosts. El planner comparte findings entre targets (p.ej. si un host expone SMB, probarlo en todo el rango).

---

## ✨ #06 — ATT&CK tagging automático en findings

**Labels:** `enhancement`, `reporting`

**Resumen:** cada finding hoy tiene severity pero no mapeo a MITRE ATT&CK. Dado que los 774 cybersec skills ya están mapeados, el reporter podría inferir el tactic/technique a partir del tipo de finding.

**Beneficio:** reportes compatibles con SOC tooling y trend analysis.

---

## ✨ #07 — Replay mode

**Labels:** `enhancement`, `testing`

**Resumen:** grabar una sesión (prompts + observaciones) y poder reproducirla con otro LLM para comparar razonamiento.

**Uso:** útil para benchmarking (¿Claude vs smart-llm vs gpt-4o en el mismo CTF?) y regression testing cuando cambia el REACT_SYSTEM_PROMPT.

**Storage:** JSONL en `vulcan_output/<scan>.replay.jsonl`.

---

## ✨ #08 — Webhooks para findings críticos

**Labels:** `enhancement`, `integration`

**Resumen:** `--webhook-url https://hooks.slack.com/...` que dispara POST por cada finding `critical`/`high`.

**Formato payload:** compatible con Slack blocks + Discord embeds.

---

## ✨ #09 — Evidence graph

**Labels:** `enhancement`, `reporting`

**Resumen:** finding `X` puede depender de finding `Y` (ej. "SSRF en /api → pivote a metadata EC2 → acceso a secret"). Hoy los findings son una lista plana.

**Propuesta:** DAG donde edges = "este finding habilitó este otro". Renderizar como grafo en el HTML report con D3 o mermaid.

---

## ✨ #10 — CTF heuristics

**Labels:** `enhancement`, `ctf`

**Resumen:** en CTFs hay patrones: el flag suele estar en `/flag.txt`, el web challenge suele pivotear a admin, etc.

**Propuesta:** módulo `ctf_heuristics` que activa con `--mode ctf` y hace:
- Busca `flag`, `flag.txt`, `/root/flag`, `.flag` en cada host comprometido
- Regex del formato de flag (configurable: `--flag-format "FLAG{.*}"`)
- Auto-submit al scoreboard si se pasa `--scoreboard-url`

---

## ✨ #11 — Publicación a PyPI

**Labels:** `enhancement`, `packaging`

**Resumen:** `pip install vulcan-pentest` facilitaría onboarding.

**Tareas:**
- [ ] `pyproject.toml` con metadata completa
- [ ] Entry point `vulcan = vulcan.ui.cli:main`
- [ ] CI con GitHub Actions para publish en tag push
- [ ] Reservar nombre en PyPI

---

## ✨ #12 — Dockerfile + docker-compose

**Labels:** `enhancement`, `packaging`

**Resumen:** stack reproducible:
- Servicio `hexstrike` — el Flask server
- Servicio `ollama` — con los modelos pre-cargados
- Servicio `vulcan` — el agente
- Servicio `reporter` — nginx sirviendo los HTML

**Beneficio:** arranque con `docker compose up`, sin instalar nada a mano.

---

## ✨ #13 — Tests de integración con mocks de HexStrike

**Labels:** `enhancement`, `testing`

**Resumen:** hoy no hay tests automatizados del loop ReAct.

**Propuesta:** fixture con un mock Flask que simule `/api/tools/<x>` con respuestas canned. Test end-to-end sin necesidad de tener HexStrike real corriendo.

---

## 🔐 #14 — Rate limiting y killswitch

**Labels:** `security`, `safety`

**Resumen:** por seguridad operativa, Vulcan debería:
- Limitar requests/segundo contra el target
- Killswitch: si detecta 429/WAF-block, detener todo el loop
- Scope guard: validar que el target está en una lista permitida antes de correr

**Beneficio:** evitar correr contra producción por error de dedo.
