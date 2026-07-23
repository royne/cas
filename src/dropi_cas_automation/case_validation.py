from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class CaseValidationResult:
    status: str
    chat_id: str | None = None
    raw: dict[str, Any] | None = None


class BrowserRunner(Protocol):
    def execute_json(self, code: str, timeout_seconds: int) -> dict[str, Any]:
        ...


class DropiCaseValidator:
    """Read-only remote CAS validation. Browser tokens never leave the tab."""

    def __init__(self, runner: BrowserRunner, *, case_service_type_id: str = ""):
        self.runner = runner
        self.case_service_type_id = case_service_type_id

    def validate(self, order_id: str, carrier: str, *, allow_external_read: bool) -> CaseValidationResult:
        if not allow_external_read:
            raise PermissionError("External reads are disabled. Explicit read authorization is required to validate a remote case.")
        data = self.runner.execute_json(self._script(order_id, carrier), timeout_seconds=120)
        return CaseValidationResult(str(data.get("status") or "error"), data.get("chat_id"), data)

    def _script(self, order_id: str, carrier: str) -> str:
        return r'''
import json
ORDER_ID = __ORDER_ID__
CARRIER = __CARRIER__
SERVICE_TYPE = __SERVICE_TYPE__
script = f"""(async () => {{
  const ORDER_ID = {json.dumps(ORDER_ID)};
  const CARRIER = {json.dumps(CARRIER)};
  const SERVICE_TYPE = {json.dumps(SERVICE_TYPE)};
  const ordersToken = JSON.parse(localStorage.getItem('DROPI_token') || 'null');
  const casToken = JSON.parse(localStorage.getItem('casToken') || 'null');
  if (!ordersToken || !casToken) return {{status:'session_missing'}};
  const ordersHeaders = {{Authorization:'Bearer ' + ordersToken, 'X-Authorization':'Bearer ' + ordersToken}};
  const validation = await fetch('https://api.dropi.co/api/orders/validate-any-case-carriers?order_id=' + encodeURIComponent(ORDER_ID), {{headers:ordersHeaders}}).then(r => r.json());
  if (!validation?.objects?.ORDER_WITHOUT_MOVEMENT) return {{status:'not_eligible', validation}};
  if (!SERVICE_TYPE) return {{status:'eligible', validation}};
  const headers = {{Authorization:'Bearer ' + casToken, 'Content-Type':'application/json'}};
  const query = {{enterpriseNames:[CARRIER], serviceTypeId:SERVICE_TYPE, referenceObjects:[{{id:Number(ORDER_ID), type:'ORDER'}}], status_chat:['active','queues','postponed','to_reopen','close','closed','finalized']}};
  const search = await fetch('https://api-v2.dropi.co/cas/api/v1/chats/search', {{method:'POST',headers,body:JSON.stringify(query)}}).then(r => r.json());
  const active = (search?.data || []).find(item => !['close','closed','finalized'].includes(String(item?.casChat?.status || '').toLowerCase()));
  return active ? {{status:'existing_case', chat_id:active?.casChat?._id, search}} : {{status:'eligible', validation, search}};
}})()"""
print('__JSON__' + json.dumps(js(script), ensure_ascii=False))
'''.replace("__ORDER_ID__", json.dumps(order_id)).replace("__CARRIER__", json.dumps(carrier)).replace("__SERVICE_TYPE__", json.dumps(self.case_service_type_id))
