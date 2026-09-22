#!/usr/bin/env bash
# Ejecuta una corrida operacional de CAS en ESTA instalación.
# Requiere que la persona haya iniciado sesión en Dropi desde su navegador.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${DROPI_CAS_CONFIG:-$ROOT/config.toml}"
PYTHON="${DROPI_CAS_PYTHON:-$ROOT/.venv/bin/python}"
MODE="${1:---execute}"

if [[ "$MODE" != "--execute" && "$MODE" != "--dry-run" ]]; then
  echo "Uso: ./ejecutar-cas.sh [--execute|--dry-run]"
  exit 2
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "No encuentro la instalación local. Ejecuta primero: ./scripts/install.sh"
  exit 2
fi
if [[ ! -f "$CONFIG" ]]; then
  echo "No encuentro config.toml. Ejecuta primero: ./scripts/install.sh"
  exit 2
fi

exec "$PYTHON" -m dropi_cas_automation.cli operate \
  --config "$CONFIG" \
  "$MODE"
