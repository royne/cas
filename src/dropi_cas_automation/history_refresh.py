from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .history import parse_order_history
from .history_store import save_order_history


class HistoryReader(Protocol):
    def read(self, guide: str, *, allow_external_read: bool) -> str:
        ...


def refresh_guide_history(database_path: Path, reader: HistoryReader, guide: str, *, allow_external_read: bool) -> dict[str, object]:
    text = reader.read(guide, allow_external_read=allow_external_read)
    history = parse_order_history(text)
    if history.guide and history.guide != guide:
        raise ValueError(f"The opened order guide ({history.guide}) does not match the requested guide ({guide}).")
    saved = save_order_history(database_path, history)
    return {
        "order_id": history.order_id,
        "guide": history.guide,
        "movements_saved": saved,
        "last_movement_at": history.last_movement.movement_at,
        "last_movement_status": history.last_movement.status,
    }
