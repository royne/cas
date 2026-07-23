#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${1:-$ROOT/.venv}"

if command -v uv >/dev/null 2>&1; then
  uv venv "$VENV"
  uv pip install --python "$VENV/bin/python" "$ROOT"
else
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install "$ROOT"
fi
printf 'Installed dropi-cas into %s\n' "$VENV"
printf 'Next: copy config.example.toml to a private config.toml and run %s/bin/dropi-cas doctor --config ./config.toml\n' "$VENV"
