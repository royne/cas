import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dropi_cas_automation.report_download import OrdersReportDownloader


class FakeRunner:
    def __init__(self):
        self.calls = []

    def execute_json(self, code, timeout_seconds):
        self.calls.append(code)
        if "report_name" in code:
            return {
                "ok": True,
                "report": {
                    "storage_type": "s3",
                    "file_path": "reports/",
                    "file_name": "orders.xlsx",
                    "display_name": "orders.xlsx",
                },
            }
        return {"ok": True}


class DownloadTests(unittest.TestCase):
    def test_download_requires_read_permission(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = OrdersReportDownloader(FakeRunner(), Path(temp_dir))
            with self.assertRaises(PermissionError):
                downloader.download(allow_external_read=False)

    def test_download_uses_browser_to_request_then_downloads_to_own_workspace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir)
            runner = FakeRunner()
            downloader = OrdersReportDownloader(runner, output)

            def fake_retrieve(url, target):
                Path(target).write_bytes(b"xlsx")
                return target, None

            with patch("urllib.request.urlretrieve", fake_retrieve):
                path = downloader.download(allow_external_read=True)

            self.assertEqual(path, output / "orders.xlsx")
            self.assertEqual(path.read_bytes(), b"xlsx")
            self.assertIn("Órdenes (Una orden por fila)", runner.calls[0])
