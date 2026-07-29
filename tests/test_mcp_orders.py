import sqlite3
import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.mcp_orders import import_mcp_orders
from dropi_cas_automation.storage import initialize_database


class McpOrdersTests(unittest.TestCase):
    def test_imports_mcp_rows_without_losing_a_text_guide(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "automation.sqlite3"
            initialize_database(database)

            result = import_mcp_orders(
                database,
                [
                    {
                        "id": "order-1",
                        "status": "EN TRANSPORTE",
                        "shippingGuide": "034000000001",
                        "carrier": "ENVIA",
                        "lastMovementAt": "2026-07-29T08:00:00",
                    }
                ],
                source_ref="mcp:2026-07-05:2026-07-29",
            )

            with sqlite3.connect(database) as connection:
                row = connection.execute("SELECT guide,status,carrier,last_movement_at FROM orders WHERE order_id='order-1'").fetchone()
                source = connection.execute("SELECT source_path FROM import_runs").fetchone()[0]
            self.assertEqual(result["rows"], 1)
            self.assertEqual(row, ("034000000001", "EN TRANSPORTE", "ENVIA", "2026-07-29T08:00:00"))
            self.assertEqual(source, "mcp:2026-07-05:2026-07-29")


if __name__ == "__main__":
    unittest.main()
