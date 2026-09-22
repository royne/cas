#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${1:-$ROOT/.venv}"
CONFIG="$ROOT/config.toml"

if ! command -v python3 >/dev/null 2>&1; then
  echo "No encuentro Python 3. Instálalo y vuelve a ejecutar este archivo."
  exit 1
fi

if command -v uv >/dev/null 2>&1; then
  uv venv "$VENV"
  uv pip install --python "$VENV/bin/python" "$ROOT"
else
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install "$ROOT"
fi

if ! command -v browser-harness >/dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then
    echo "Instalando browser-harness..."
    uv tool install browser-harness
  else
    echo "No encuentro browser-harness ni uv para instalarlo automáticamente."
    echo "Instala uv y vuelve a ejecutar este instalador."
    exit 1
  fi
fi

if [[ ! -f "$CONFIG" ]]; then
  cp "$ROOT/config.example.toml" "$CONFIG"
fi
"$VENV/bin/dropi-cas" init --config "$CONFIG" >/dev/null
chmod +x "$ROOT/ejecutar-cas.sh"

printf '\nInstalación lista.\n'
printf '1. Abre Dropi en tu navegador e inicia sesión.\n'
printf '2. Ejecuta: %s\n' "$ROOT/ejecutar-cas.sh"
printf '   Para revisar sin crear ni enviar nada: %s --dry-run\n' "$ROOT/ejecutar-cas.sh"
printf 'Los reportes quedarán en: %s/runtime/reports/\n' "$ROOT"
