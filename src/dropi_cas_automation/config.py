from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    workspace_root: Path
    minimum_hours_without_movement: float = 24.0

    @property
    def database_path(self) -> Path:
        return self.workspace_root / "data" / "automation.sqlite3"

    @property
    def evidence_dir(self) -> Path:
        return self.workspace_root / "evidence"

    @property
    def reports_dir(self) -> Path:
        return self.workspace_root / "reports"


def _parse_minimal_toml(text: str) -> dict[str, dict[str, Any]]:
    section = ""
    data: dict[str, dict[str, Any]] = {}
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            data.setdefault(section, {})
            continue
        if "=" not in line or not section:
            raise ValueError(f"Unsupported configuration line: {raw_line}")
        key, raw_value = (part.strip() for part in line.split("=", 1))
        if raw_value.startswith('"') and raw_value.endswith('"'):
            value: Any = raw_value[1:-1]
        else:
            value = float(raw_value) if "." in raw_value else int(raw_value)
        data[section][key] = value
    return data


def load_config(path: Path) -> AppConfig:
    path = path.expanduser().resolve()
    data = _parse_minimal_toml(path.read_text(encoding="utf-8"))
    workspace = data.get("workspace", {}).get("root")
    if not isinstance(workspace, str) or not workspace.strip():
        raise ValueError("[workspace].root must be a non-empty string.")
    workspace_root = Path(workspace).expanduser()
    if not workspace_root.is_absolute():
        workspace_root = path.parent / workspace_root
    threshold = data.get("rules", {}).get("minimum_hours_without_movement", 24)
    if not isinstance(threshold, (int, float)) or threshold <= 0:
        raise ValueError("[rules].minimum_hours_without_movement must be greater than zero.")
    return AppConfig(workspace_root=workspace_root.resolve(), minimum_hours_without_movement=float(threshold))


def initialize_workspace(config: AppConfig) -> None:
    for directory in (config.workspace_root / "data", config.evidence_dir, config.reports_dir):
        directory.mkdir(parents=True, exist_ok=True)
