from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS evaluation_runs (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    input_path TEXT NOT NULL,
    evaluated_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS evaluation_results (
    id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES evaluation_runs(id),
    order_id TEXT NOT NULL,
    guide TEXT,
    decision_status TEXT NOT NULL,
    reason TEXT NOT NULL,
    hours_without_movement REAL
);
CREATE TABLE IF NOT EXISTS import_runs (
    id INTEGER PRIMARY KEY,
    source_path TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rows_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    guide TEXT,
    status TEXT,
    carrier TEXT,
    last_movement_at TEXT,
    raw_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_snapshots (
    id INTEGER PRIMARY KEY,
    import_run_id INTEGER NOT NULL REFERENCES import_runs(id),
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    status TEXT,
    guide TEXT,
    carrier TEXT,
    last_movement_at TEXT,
    raw_json TEXT NOT NULL,
    UNIQUE(import_run_id, order_id)
);
CREATE TABLE IF NOT EXISTS order_movements (
    id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    movement_id TEXT NOT NULL,
    movement_at TEXT,
    status TEXT NOT NULL,
    user_name TEXT,
    comment TEXT,
    extracted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(order_id, movement_id)
);
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL REFERENCES orders(order_id),
    guide TEXT NOT NULL,
    chat_id TEXT NOT NULL UNIQUE,
    evidence_path TEXT NOT NULL,
    message TEXT NOT NULL,
    opened_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at TEXT
);
CREATE TABLE IF NOT EXISTS followups (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id),
    chat_id TEXT NOT NULL,
    due_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    sent_at TEXT,
    message TEXT
);
"""


def initialize_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.executescript(SCHEMA)
