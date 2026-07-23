import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dropi_cas_automation.cli import main


class CliTests(unittest.TestCase):
    def test_evaluate_writes_only_local_decisions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.toml"
            config.write_text('[workspace]\nroot = "runtime"\n', encoding="utf-8")
            orders = root / "orders.json"
            orders.write_text(
                json.dumps(
                    [
                        {
                            "order_id": "order-1",
                            "guide": "G-1",
                            "carrier": "carrier-a",
                            "current_status": "EN TRANSPORTE",
                            "last_movement_at": "2026-01-01T00:00:00+00:00",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["evaluate", "--config", str(config), "--input", str(orders)])

            payload = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["summary"]["eligible"], 1)
            self.assertTrue((root / "runtime" / "data" / "automation.sqlite3").exists())
