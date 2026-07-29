import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.config import AppConfig, initialize_workspace, load_config


class ConfigTests(unittest.TestCase):
    def test_loads_relative_paths_inside_config_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.toml"
            config_path.write_text(
                """[workspace]
root = "runtime"

[rules]
minimum_hours_without_movement = 30
""",
                encoding="utf-8",
            )

            config = load_config(config_path)

            self.assertEqual(config.workspace_root, root / "runtime")
            self.assertEqual(config.minimum_hours_without_movement, 30)
            self.assertEqual(config.orders_source, "excel")

    def test_loads_mcp_source_configuration_without_credentials(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.toml"
            config_path.write_text(
                """[workspace]
root = "runtime"

[orders_source]
provider = "mcp"
mcp_config_path = "./private-hermes-config.yaml"
mcp_window_days = 20
""",
                encoding="utf-8",
            )

            config = load_config(config_path)

            self.assertEqual(config.orders_source, "mcp")
            self.assertEqual(config.mcp_config_path, root / "private-hermes-config.yaml")
            self.assertEqual(config.mcp_window_days, 20)

    def test_initialization_creates_only_configured_workspace_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "isolated"
            config = AppConfig(workspace_root=root)

            initialize_workspace(config)

            self.assertTrue((root / "data").is_dir())
            self.assertTrue((root / "evidence").is_dir())
            self.assertTrue((root / "reports").is_dir())
