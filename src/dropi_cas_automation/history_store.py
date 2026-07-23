from __future__ import annotations

import sqlite3
from pathlib import Path

from .history import OrderHistory


def save_order_history(database_path: Path, history: OrderHistory) -> int:
    if not history.order_id:
        raise ValueError("Cannot persist an order history without an order ID.")
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        order = connection.execute("SELECT 1 FROM orders WHERE order_id=?", (history.order_id,)).fetchone()
        if not order:
            connection.execute(
                "INSERT INTO orders(order_id, guide, status, carrier, raw_json) VALUES(?, ?, ?, ?, ?)",
                (history.order_id, history.guide, history.current_status, history.carrier, "{}"),
            )
        saved = 0
        for movement in history.movements:
            cursor = connection.execute(
                """INSERT INTO order_movements(order_id, movement_id, movement_at, status, user_name, comment)
                   VALUES(?, ?, ?, ?, ?, ?)
                   ON CONFLICT(order_id, movement_id) DO UPDATE SET movement_at=excluded.movement_at,
                   status=excluded.status, user_name=excluded.user_name, comment=excluded.comment""",
                (history.order_id, movement.movement_id, movement.movement_at, movement.status, movement.user, movement.comment),
            )
            saved += cursor.rowcount
        connection.execute(
            "UPDATE orders SET guide=?, status=?, carrier=?, last_movement_at=?, updated_at=CURRENT_TIMESTAMP WHERE order_id=?",
            (history.guide, history.current_status, history.carrier, history.last_movement.movement_at, history.order_id),
        )
    return saved
