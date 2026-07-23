from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path


def build_report(database_path: Path) -> dict[str, int | str]:
    with sqlite3.connect(database_path) as connection:
        orders = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        cases_open = connection.execute("SELECT COUNT(*) FROM cases WHERE closed_at IS NULL").fetchone()[0]
        followups_pending = connection.execute("SELECT COUNT(*) FROM followups WHERE status='pending'").fetchone()[0]
        followups_due = connection.execute("SELECT COUNT(*) FROM followups WHERE status='pending' AND due_at <= ?", (datetime.now().replace(microsecond=0).isoformat(sep=" "),)).fetchone()[0]
    return {"generated_at": datetime.now().replace(microsecond=0).isoformat(sep=" "), "orders": orders, "cases_open": cases_open, "followups_pending": followups_pending, "followups_due": followups_due}
