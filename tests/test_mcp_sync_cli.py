import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from dropi_cas_automation.cli import main


class McpSyncCliTests(unittest.TestCase):
    def test_sync_uses_mcp_when_toml_selects_mcp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.toml"
            private_mcp_config = root / "mcp.yaml"
            private_mcp_config.write_text("private", encoding="utf-8")
            config.write_text(
                """[workspace]
root = "runtime"

[orders_source]
provider = "mcp"
mcp_config_path = "./mcp.yaml"
mcp_window_days = 20
""",
                encoding="utf-8",
            )
            with patch("dropi_cas_automation.cli.fetch_mcp_orders", return_value=([{"id": "order-1"}], {"truncated": False})) as fetch, patch(
                "dropi_cas_automation.cli.import_mcp_orders", return_value={"rows": 1, "created": 1, "updated": 0}
            ) as importer:
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(["sync", "--config", str(config), "--allow-external-read"]), 0)

            self.assertEqual(json.loads(output.getvalue())["source"], "mcp")
            fetch.assert_called_once_with(private_mcp_config, window_days=20)
            importer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
