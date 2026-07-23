import sqlite3
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook

from dropi_cas_automation.orders_import import import_orders_xlsx
from dropi_cas_automation.storage import initialize_database


class OrdersImportTests(unittest.TestCase):
    def test_import_preserves_text_guide_and_records_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            xlsx = root / "orders.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.append(["ID", "NÚMERO GUIA", "ESTATUS", "TRANSPORTADORA", "FECHA DE ÚLTIMO MOVIMIENTO", "HORA DE ÚLTIMO MOVIMIENTO"])
            sheet.append(["order-1", "034000000001", "EN TRANSPORTE", "carrier-a", "2026-01-01", "10:30"])
            workbook.save(xlsx)

            database = root / "data" / "automation.sqlite3"
            initialize_database(database)
            result = import_orders_xlsx(database, xlsx)

            self.assertEqual(result["rows"], 1)
            with sqlite3.connect(database) as connection:
                order = connection.execute("SELECT guide, status, carrier FROM orders WHERE order_id='order-1'").fetchone()
                snapshots = connection.execute("SELECT COUNT(*) FROM order_snapshots WHERE order_id='order-1'").fetchone()[0]
            self.assertEqual(order, ("034000000001", "EN TRANSPORTE", "carrier-a"))
            self.assertEqual(snapshots, 1)
