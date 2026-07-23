import unittest

from dropi_cas_automation.case_validation import DropiCaseValidator


class FakeRunner:
    def __init__(self, result):
        self.result = result
        self.code = ""

    def execute_json(self, code, timeout_seconds):
        self.code = code
        return self.result


class CaseValidationTests(unittest.TestCase):
    def test_validation_requires_read_permission(self):
        with self.assertRaises(PermissionError):
            DropiCaseValidator(FakeRunner({})).validate("123", "carrier-a", allow_external_read=False)

    def test_validation_returns_existing_case_without_write(self):
        runner = FakeRunner({"ok": True, "status": "existing_case", "chat_id": "chat-1"})
        result = DropiCaseValidator(runner).validate("123", "carrier-a", allow_external_read=True)
        self.assertEqual(result.status, "existing_case")
        self.assertEqual(result.chat_id, "chat-1")
        self.assertIn("123", runner.code)
