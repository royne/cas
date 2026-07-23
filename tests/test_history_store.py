import sqlite3
import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.history import parse_order_history
from dropi_cas_automation.history_store import save_order_history
from dropi_cas_automation.storage import initialize_database


class HistoryStoreTests(unittest.TestCase):
    def test_saves_movements_and_updates_order_last_movement(self):
        text = """ORDEN PARA:
Orden #123
Número de Guía: 034000000001
Compañia de envío: carrier-a
Estatus: EN TRANSPORTE
Historial de estados:
1\t01/01/2026 10:30 AM\tEN BODEGA ORIGEN\toperator\tIngreso
2\t02/01/2026 03:15 PM\tEN TRANSPORTE\toperator\tSalida
Historial de Cartera
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "automation.sqlite3"
            initialize_database(database)
            with sqlite3.connect(database) as connection:
                connection.execute("INSERT INTO orders(order_id, guide, status, carrier, raw_json) VALUES(?, ?, ?, ?, ?)", ("123", "034000000001", "EN TRANSPORTE", "carrier-a", "{}"))
            saved = save_order_history(database, parse_order_history(text))
            self.assertEqual(saved, 2)
            with sqlite3.connect(database) as connection:
                last = connection.execute("SELECT last_movement_at FROM orders WHERE order_id='123'").fetchone()[0]
                movements = connection.execute("SELECT COUNT(*) FROM order_movements WHERE order_id='123'").fetchone()[0]
            self.assertEqual(last, "2026-01-02 15:15:00")
            self.assertEqual(movements, 2)
