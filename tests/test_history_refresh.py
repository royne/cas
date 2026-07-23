import sqlite3
import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.history_refresh import refresh_guide_history
from dropi_cas_automation.storage import initialize_database


class FakeReader:
    def read(self, guide, *, allow_external_read):
        self.guide = guide
        self.allow_external_read = allow_external_read
        return """ORDEN PARA:
Orden #123
Número de Guía: 034000000001
Compañia de envío: carrier-a
Estatus: EN TRANSPORTE
Historial de estados:
1\t02/01/2026 03:15 PM\tEN TRANSPORTE\toperator\tSalida
Historial de Cartera
"""


class HistoryRefreshTests(unittest.TestCase):
    def test_refreshes_requested_guide_and_persists_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "automation.sqlite3"
            initialize_database(database)
            with sqlite3.connect(database) as connection:
                connection.execute("INSERT INTO orders(order_id, guide, status, carrier, raw_json) VALUES(?, ?, ?, ?, ?)", ("123", "034000000001", "EN TRANSPORTE", "carrier-a", "{}"))
            reader = FakeReader()
            result = refresh_guide_history(database, reader, "034000000001", allow_external_read=True)
            self.assertEqual(reader.guide, "034000000001")
            self.assertEqual(result["movements_saved"], 1)
            self.assertEqual(result["last_movement_at"], "2026-01-02 15:15:00")
