import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class DueFollowup:
    id: int
    case_id: int
    order_id: str
    guide: str
    carrier: str
    chat_id: str
    due_at: datetime


def load_due_followups(database_path: Path, *, now: datetime | None = None, limit: int | None = None) -> list[DueFollowup]:
    current = (now or datetime.now()).replace(microsecond=0).isoformat(sep=" ")
    query = """
        SELECT f.id, f.case_id, c.order_id, c.guide, o.carrier, f.chat_id, f.due_at
        FROM followups f
        JOIN cases c ON c.id = f.case_id
        JOIN orders o ON o.order_id = c.order_id
        WHERE f.status = 'pending' AND f.due_at <= ?
        ORDER BY f.due_at, f.id
    """
    if limit is not None:
        query += " LIMIT ?"
    parameters: tuple[object, ...] = (current,) if limit is None else (current, limit)
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [DueFollowup(row[0], row[1], row[2], row[3], row[4] or "", row[5], datetime.fromisoformat(row[6])) for row in rows]


def mark_followup_sent(database_path: Path, followup_id: int, message: str) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE followups SET status='sent', sent_at=?, message=? WHERE id=? AND status='pending'",
            (datetime.now().replace(microsecond=0).isoformat(sep=" "), message, followup_id),
        )


def mark_followup_skipped(database_path: Path, followup_id: int, reason: str) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute("UPDATE followups SET status='skipped', message=? WHERE id=? AND status='pending'", (reason, followup_id))
