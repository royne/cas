import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from dropi_cas_automation.cli import main
from dropi_cas_automation.config import load_config


class OperationalModeTests(unittest.TestCase):
    def test_config_uses_packaged_cas_defaults_without_prompting_for_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.toml"
            config_path.write_text('[workspace]\nroot = "runtime"\n', encoding="utf-8")

            config = load_config(config_path)

            self.assertTrue(config.case_service_type_id)
            self.assertTrue(config.case_ticket_type_id)

    def test_operate_dry_run_generates_human_reports_in_own_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.toml"
            config_path.write_text('[workspace]\nroot = "runtime"\n', encoding="utf-8")
            output = io.StringIO()
            with (
                patch("dropi_cas_automation.cli.command_sync", return_value=0) as sync,
                patch("dropi_cas_automation.cli.command_run", return_value=0) as run,
                patch("dropi_cas_automation.cli.command_followups", return_value=0) as followups,
                redirect_stdout(output),
            ):
                exit_code = main(["operate", "--config", str(config_path), "--dry-run"])

            payload = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["mode"], "dry_run")
            self.assertEqual([step["name"] for step in payload["steps"]], ["sync", "cas", "followups"])
            self.assertTrue(Path(payload["summary_report"]).is_file())
            self.assertTrue(Path(payload["detailed_report"]).is_file())
            self.assertIn("Resumen operativo CAS", Path(payload["summary_report"]).read_text(encoding="utf-8"))
            sync.assert_called_once()
            run.assert_called_once()
            followups.assert_called_once()

    def test_operate_execute_uses_configured_service_type_without_user_flag(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.toml"
            config_path.write_text('[workspace]\nroot = "runtime"\n', encoding="utf-8")
            output = io.StringIO()
            with (
                patch("dropi_cas_automation.cli.command_sync", return_value=0),
                patch("dropi_cas_automation.cli.command_run", return_value=0) as run,
                patch("dropi_cas_automation.cli.command_followups", return_value=0),
                redirect_stdout(output),
            ):
                exit_code = main(["operate", "--config", str(config_path), "--execute", "--limit", "2"])

            self.assertEqual(exit_code, 0)
            self.assertTrue(run.call_args.args[0].execute)
            self.assertEqual(run.call_args.args[0].case_service_type_id, load_config(config_path).case_service_type_id)
