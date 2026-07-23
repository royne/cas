from __future__ import annotations

import json
from typing import Any, Protocol


class BrowserRunner(Protocol):
    def execute_json(self, code: str, timeout_seconds: int) -> dict[str, Any]: ...


def followup_message() -> str:
    return "Buen día. La guía continúa sin movimiento; agradezco validar y gestionar avance prioritario. Gracias."


class DropiFollowupSender:
    def __init__(self, runner: BrowserRunner): self.runner = runner

    def send(self, chat_id: str, message: str, *, allow_external_writes: bool) -> dict[str, Any]:
        if not allow_external_writes:
            raise PermissionError("External writes are disabled. Explicit write authorization is required to send a follow-up.")
        result = self.runner.execute_json(self._script(chat_id, message), timeout_seconds=120)
        if not result.get("ok"):
            raise RuntimeError(str(result.get("error") or "Dropi did not confirm the follow-up."))
        return result

    @staticmethod
    def _script(chat_id: str, message: str) -> str:
        return r'''
import json
CHAT_ID = __CHAT_ID__
MESSAGE = __MESSAGE__
script = f"""(async () => {{
  const CHAT_ID = {json.dumps(CHAT_ID)};
  const MESSAGE = {json.dumps(MESSAGE)};
  const token = JSON.parse(localStorage.getItem('casToken') || 'null');
  const user = JSON.parse(localStorage.getItem('casUser') || 'null');
  if (!token || !user) return {{ok:false,error:'session_missing'}};
  const response = await fetch('https://api-v2.dropi.co/cas/api/v1/caschat/interaction/create/massive', {{
    method:'POST', headers:{{Authorization:'Bearer '+token,'Content-Type':'application/json'}},
    body:JSON.stringify({{interactionType:'MESSAGE', casChats:[{{_id:CHAT_ID}}], objectIntegrationType:{{message:MESSAGE}}, user}})
  }});
  return {{ok:response.ok,status:response.status}};
}})()"""
print('__JSON__' + json.dumps(js(script), ensure_ascii=False))
'''.replace("__CHAT_ID__", json.dumps(chat_id)).replace("__MESSAGE__", json.dumps(message))
