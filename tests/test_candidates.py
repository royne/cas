import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from dropi_cas_automation.candidates import load_candidates
from dropi_cas_automation.storage import initialize_database


class CandidateTests(unittest.TestCase):
    def test_loads_only_orders_eligible_by_real_movement(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "automation.sqlite3"
            initialize_database(database)
            old = (datetime.now() - timedelta(hours=30)).replace(microsecond=0).isoformat(sep=" ")
            with sqlite3.connect(database) as connection:
                connection.execute("INSERT INTO orders(order_id, guide, status, carrier, last_movement_at, raw_json) VALUES(?, ?, ?, ?, ?, ?)", ("123", "034000000001", "EN TRANSPORTE", "carrier-a", old, "{}"))
            candidates = load_candidates(database, minimum_hours_without_movement=24)
            self.assertEqual([item.order_id for item in candidates], ["123"])
