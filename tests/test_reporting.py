import sqlite3
import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.reporting import build_report
from dropi_cas_automation.storage import initialize_database


class ReportingTests(unittest.TestCase):
    def test_report_counts_orders_cases_and_pending_followups(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "automation.sqlite3"
            initialize_database(database)
            with sqlite3.connect(database) as connection:
                connection.execute("INSERT INTO orders(order_id, guide, status, carrier, raw_json) VALUES(?, ?, ?, ?, ?)", ("123", "034000000001", "EN TRANSPORTE", "carrier-a", "{}"))
                connection.execute("INSERT INTO cases(order_id, guide, chat_id, evidence_path, message) VALUES(?, ?, ?, ?, ?)", ("123", "034000000001", "chat-1", "/tmp/evidence.png", "message"))
                case_id = connection.execute("SELECT id FROM cases WHERE chat_id='chat-1'").fetchone()[0]
                connection.execute("INSERT INTO followups(case_id, chat_id, due_at) VALUES(?, ?, ?)", (case_id, "chat-1", "2020-01-01 00:00:00"))
            report = build_report(database)
            self.assertEqual(report["orders"], 1)
            self.assertEqual(report["cases_open"], 1)
            self.assertEqual(report["followups_pending"], 1)
