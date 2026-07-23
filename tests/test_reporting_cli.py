import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dropi_cas_automation.cli import main


class ReportingCliTests(unittest.TestCase):
    def test_report_command_reads_configured_local_database(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.toml"
            config.write_text('[workspace]\nroot = "runtime"\n', encoding="utf-8")
            stream = io.StringIO()
            with redirect_stdout(stream):
                exit_code = main(["report", "--config", str(config)])
            payload = json.loads(stream.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["orders"], 0)
