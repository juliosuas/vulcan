#!/usr/bin/env bash
# run-beast.sh — full-local Vulcan + HexStrike + smart-llm pipeline.
#
# Usage: ./run-beast.sh <target> [mode]
#   mode: quick | standard (default) | full
#
# Steps:
#   1. Ensure HexStrike API server is up (arranca si no).
#   2. Warm smart-llm (carga modelos en VRAM — evita cold start de 20-30s).
#   3. Ejecuta `vulcan scan --local` contra el target.
#   4. Abre el reporte HTML al terminar.

set -euo pipefail

TARGET="${1:-}"
MODE="${2:-standard}"
VULCAN_DIR="$(cd "$(dirname "$0")" && pwd)"
HEXSTRIKE_DIR="$HOME/Desktop/cybersec/08-exploitation-tools/hexstrike-ai"
HEXSTRIKE_URL="http://127.0.0.1:8888"
OUTPUT_DIR="${VULCAN_OUTPUT_DIR:-$VULCAN_DIR/vulcan_output}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <target> [quick|standard|full]"
  echo "Ejemplo: $0 scanme.nmap.org standard"
  exit 1
fi

echo "🔴 BESTIA pipeline — target=$TARGET mode=$MODE"

# --- Step 1: HexStrike ---
if curl -sf "$HEXSTRIKE_URL/health" >/dev/null 2>&1; then
  echo "  ✅ HexStrike ya corriendo en $HEXSTRIKE_URL"
else
  echo "  🚀 Arrancando HexStrike server..."
  if [[ ! -x "$HEXSTRIKE_DIR/start-server.sh" ]]; then
    echo "  ❌ No se encontró $HEXSTRIKE_DIR/start-server.sh — abortando."
    exit 1
  fi
  nohup "$HEXSTRIKE_DIR/start-server.sh" > /tmp/hexstrike-beast.log 2>&1 &
  for i in {1..20}; do
    sleep 1
    curl -sf "$HEXSTRIKE_URL/health" >/dev/null 2>&1 && { echo "  ✅ HexStrike arriba."; break; }
  done
  if ! curl -sf "$HEXSTRIKE_URL/health" >/dev/null 2>&1; then
    echo "  ❌ HexStrike no arrancó en 20s — revisa /tmp/hexstrike-beast.log"
    exit 1
  fi
fi

# --- Step 2: warm smart-llm ---
if command -v smart-llm >/dev/null 2>&1; then
  echo "  🔥 Warming smart-llm (modelos → VRAM)..."
  smart-llm --warmup --keep-alive 24h >/dev/null 2>&1 || echo "  ⚠️  smart-llm --warmup falló (no crítico)."
else
  echo "  ⚠️  smart-llm no encontrado en PATH — Vulcan fallará si usas --local."
fi

# --- Step 3: Vulcan ---
cd "$VULCAN_DIR"
if [[ -d "$VULCAN_DIR/venv" ]]; then
  # shellcheck disable=SC1091
  source "$VULCAN_DIR/venv/bin/activate"
fi
echo "  ⚔️  Lanzando Vulcan (--local --hexstrike)..."
python3 -m ui.cli scan --target "$TARGET" --mode "$MODE" --local --output "$OUTPUT_DIR"

# --- Step 4: abrir reporte ---
latest_report="$(ls -t "$OUTPUT_DIR"/*.html 2>/dev/null | head -1 || true)"
if [[ -n "$latest_report" ]]; then
  echo "  📄 Reporte: $latest_report"
  command -v xdg-open >/dev/null && xdg-open "$latest_report" &
else
  echo "  ⚠️  No se encontró reporte HTML en $OUTPUT_DIR."
fi
