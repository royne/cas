from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Movement:
    movement_id: str
    movement_at: str | None
    status: str
    user: str | None
    comment: str | None


@dataclass(frozen=True)
class OrderHistory:
    order_id: str | None
    guide: str | None
    carrier: str | None
    current_status: str | None
    movements: tuple[Movement, ...]
    last_movement: Movement


def _parse_datetime(value: str) -> str | None:
    text = value.replace("\xa0", " ").replace("a. m.", "AM").replace("p. m.", "PM").strip()
    for pattern in ("%d/%m/%Y %I:%M %p", "%d-%m-%Y %I:%M %p", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, pattern).replace(microsecond=0).isoformat(sep=" ")
        except ValueError:
            continue
    return None


def _field(text: str, label: str) -> str | None:
    found = re.search(rf"{re.escape(label)}:\s*([^\n]+)", text)
    return found.group(1).strip() if found else None


def parse_order_history(text: str) -> OrderHistory:
    if "ORDEN PARA:" not in text:
        raise ValueError("Order detail is not visible.")
    block = re.search(r"Historial de estados:\s*(.*?)\s*Historial de Cartera", text, flags=re.S)
    if not block:
        raise ValueError("Order status history is not visible.")
    movements: list[Movement] = []
    for raw in block.group(1).splitlines():
        parts = [part.strip() for part in raw.strip().split("\t")]
        if len(parts) < 3 or not re.fullmatch(r"\d+", parts[0]):
            continue
        movements.append(Movement(parts[0], _parse_datetime(parts[1]), parts[2], parts[3] if len(parts) > 3 else None, parts[4] if len(parts) > 4 else None))
    if not movements:
        raise ValueError("No movements were parsed from the order history.")
    movements.sort(key=lambda movement: movement.movement_at or "")
    order_match = re.search(r"Orden #(\d+)", text)
    return OrderHistory(
        order_id=order_match.group(1) if order_match else None,
        guide=_field(text, "Número de Guía"),
        carrier=_field(text, "Compañia de envío"),
        current_status=_field(text, "Estatus"),
        movements=tuple(movements),
        last_movement=movements[-1],
    )
