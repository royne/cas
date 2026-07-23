import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from dropi_cas_automation.cli import main


class DropiCliSafetyTests(unittest.TestCase):
    def test_diagnose_command_requires_explicit_external_read_opt_in(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "config.toml"
            config.write_text('[workspace]\nroot = "./runtime"\n', encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["diagnose-dropi", "--config", str(config)])

            self.assertEqual(exit_code, 2)
            self.assertIn("External browser access is disabled", stdout.getvalue())
