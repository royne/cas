import tempfile
import unittest
from pathlib import Path

from dropi_cas_automation.evidence import EvidenceCapture


class FakeRunner:
    def __init__(self, source):
        self.source = source

    def execute_json(self, code, timeout_seconds):
        return {"ok": True, "screenshot": str(self.source)}


class EvidenceTests(unittest.TestCase):
    def test_capture_requires_read_permission(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(PermissionError):
                EvidenceCapture(FakeRunner(Path(temp_dir) / "x.png"), Path(temp_dir)).capture("guide", allow_external_read=False)

    def test_capture_copies_screenshot_to_isolated_evidence_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.png"
            source.write_bytes(b"image")
            target = EvidenceCapture(FakeRunner(source), root / "evidence").capture("034000000001", allow_external_read=True)
            self.assertEqual(target.read_bytes(), b"image")
            self.assertIn("034000000001", target.name)
