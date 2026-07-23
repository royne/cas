import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from dropi_cas_automation.followup_store import load_due_followups, mark_followup_sent, mark_followup_skipped
from dropi_cas_automation.storage import initialize_database


class FollowupStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "automation.sqlite3"
        initialize_database(self.db)
        with sqlite3.connect(self.db) as con:
            con.execute("INSERT INTO orders(order_id,guide,status,carrier,last_movement_at,raw_json) VALUES('o-1','034','EN REPARTO','ENVIA','2026-01-01 00:00:00','{}')")
            con.execute("INSERT INTO cases(order_id,guide,chat_id,evidence_path,message) VALUES('o-1','034','chat-1','e.png','initial')")
            con.execute("INSERT INTO followups(case_id,chat_id,due_at) VALUES(1,'chat-1',?)", ((datetime.now()-timedelta(hours=1)).replace(microsecond=0).isoformat(sep=" "),))
            con.execute("INSERT INTO followups(case_id,chat_id,due_at) VALUES(1,'chat-2',?)", ((datetime.now()+timedelta(hours=1)).replace(microsecond=0).isoformat(sep=" "),))

    def tearDown(self): self.temp.cleanup()

    def test_loads_only_due_pending_followups(self):
        due = load_due_followups(self.db)
        self.assertEqual([item.chat_id for item in due], ["chat-1"])

    def test_marks_sent_or_skipped_without_touching_future_followup(self):
        due = load_due_followups(self.db)
        mark_followup_sent(self.db, due[0].id, "sent message")
        self.assertEqual(load_due_followups(self.db), [])
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute("SELECT status,message FROM followups WHERE chat_id='chat-1'").fetchone(), ('sent', 'sent message'))
            self.assertEqual(con.execute("SELECT status FROM followups WHERE chat_id='chat-2'").fetchone(), ('pending',))
        mark_followup_skipped(self.db, due[0].id, "ignored")
