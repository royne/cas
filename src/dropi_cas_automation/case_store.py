from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def record_created_case(database_path: Path, order_id: str, guide: str, chat_id: str, evidence_path: str, message: str, *, followup_hours: float) -> dict[str, str]:
    opened_at = datetime.now().replace(microsecond=0)
    due_at = opened_at + timedelta(hours=followup_hours)
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        cursor = connection.execute(
            """INSERT INTO cases(order_id, guide, chat_id, evidence_path, message, opened_at)
               VALUES(?, ?, ?, ?, ?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET evidence_path=excluded.evidence_path, message=excluded.message""",
            (order_id, guide, chat_id, evidence_path, message, opened_at.isoformat(sep=" ")),
        )
        case = connection.execute("SELECT id FROM cases WHERE chat_id=?", (chat_id,)).fetchone()
        connection.execute(
            "INSERT INTO followups(case_id, chat_id, due_at) VALUES(?, ?, ?)",
            (case[0], chat_id, due_at.isoformat(sep=" ")),
        )
    return {"chat_id": chat_id, "next_followup_at": due_at.isoformat(sep=" ")}
