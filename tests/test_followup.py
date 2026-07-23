import unittest

from dropi_cas_automation.followup import DropiFollowupSender, followup_message


class FakeRunner:
    def __init__(self): self.calls = 0
    def execute_json(self, code, timeout_seconds):
        self.calls += 1
        return {"ok": True, "status": 201}


class FollowupTests(unittest.TestCase):
    def test_message_is_short_and_usable(self):
        self.assertLessEqual(len(followup_message()), 200)

    def test_sender_requires_explicit_write_permission(self):
        runner = FakeRunner()
        with self.assertRaises(PermissionError):
            DropiFollowupSender(runner).send("chat-1", "message", allow_external_writes=False)
        self.assertEqual(runner.calls, 0)

    def test_sender_returns_confirmed_result(self):
        result = DropiFollowupSender(FakeRunner()).send("chat-1", "message", allow_external_writes=True)
        self.assertTrue(result["ok"])
