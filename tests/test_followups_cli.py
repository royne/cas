import io
import json
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path

from dropi_cas_automation.cli import main
from dropi_cas_automation.storage import initialize_database


class FollowupsCliTests(unittest.TestCase):
    def test_dry_run_lists_due_followup_without_browser_access(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.toml"
            config.write_text('[workspace]\nroot = "./runtime"\n[rules]\nminimum_hours_without_movement = 24\n', encoding="utf-8")
            database = root / "runtime" / "data" / "automation.sqlite3"
            initialize_database(database)
            with sqlite3.connect(database) as con:
                con.execute("INSERT INTO orders(order_id,guide,status,carrier,last_movement_at,raw_json) VALUES('order-1','034','EN REPARTO','carrier','2026-01-01 00:00:00','{}')")
                con.execute("INSERT INTO cases(order_id,guide,chat_id,evidence_path,message) VALUES('order-1','034','chat-1','e.png','initial')")
                con.execute("INSERT INTO followups(case_id,chat_id,due_at) VALUES(1,'chat-1',?)", ((datetime.now()-timedelta(hours=1)).replace(microsecond=0).isoformat(sep=" "),))
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = main(["followups", "--config", str(config), "--dry-run"])
            payload = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["due_count"], 1)
            self.assertEqual(payload["followups"][0]["chat_id"], "chat-1")
