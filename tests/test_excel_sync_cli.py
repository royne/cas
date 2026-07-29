import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from dropi_cas_automation.cli import main


class ExcelSyncCliTests(unittest.TestCase):
    def test_sync_defaults_to_excel_when_toml_has_no_orders_source_section(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.toml"
            config.write_text('[workspace]\nroot = "runtime"\n', encoding="utf-8")
            report = root / "orders.xlsx"
            report.write_bytes(b"xlsx")
            with patch("dropi_cas_automation.cli.OrdersReportDownloader.download", return_value=report), patch(
                "dropi_cas_automation.cli.import_orders_xlsx", return_value={"rows": 1, "created": 1, "updated": 0}
            ) as importer:
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(["sync", "--config", str(config), "--allow-external-read"]), 0)

            self.assertEqual(json.loads(output.getvalue())["source"], "excel")
            importer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
