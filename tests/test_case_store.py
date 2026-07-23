import sqlite3
import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.case_store import record_created_case
from dropi_cas_automation.storage import initialize_database


class CaseStoreTests(unittest.TestCase):
    def test_records_confirmed_case_and_followup_due_date(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "automation.sqlite3"
            initialize_database(database)
            with sqlite3.connect(database) as connection:
                connection.execute("INSERT INTO orders(order_id, guide, status, carrier, raw_json) VALUES(?, ?, ?, ?, ?)", ("123", "034000000001", "EN TRANSPORTE", "carrier-a", "{}"))
            result = record_created_case(database, "123", "034000000001", "chat-1", "/tmp/evidence.png", "message", followup_hours=48)
            self.assertEqual(result["chat_id"], "chat-1")
            with sqlite3.connect(database) as connection:
                case_count = connection.execute("SELECT COUNT(*) FROM cases WHERE chat_id='chat-1'").fetchone()[0]
                followup_count = connection.execute("SELECT COUNT(*) FROM followups WHERE chat_id='chat-1'").fetchone()[0]
            self.assertEqual(case_count, 1)
            self.assertEqual(followup_count, 1)
