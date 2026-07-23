from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class CaseCreationResult:
    status: str
    chat_id: str | None
    url: str | None
    raw: dict[str, Any]


class BrowserRunner(Protocol):
    def execute_json(self, code: str, timeout_seconds: int) -> dict[str, Any]:
        ...


class DropiCaseCreator:
    """UI wizard writer. This method is intentionally unavailable by default."""

    def __init__(self, runner: BrowserRunner):
        self.runner = runner

    def create(self, order_id: str, guide: str, message: str, evidence_path: Path, *, allow_external_writes: bool) -> CaseCreationResult:
        if not allow_external_writes:
            raise PermissionError("External writes are disabled. Explicit write authorization is required to create a case.")
        if not evidence_path.is_file():
            raise FileNotFoundError(f"Evidence does not exist: {evidence_path}")
        result = self.runner.execute_json(self._script(order_id, guide, message, evidence_path), timeout_seconds=300)
        if result.get("status") == "existing_case":
            return CaseCreationResult("existing_case", result.get("chat_id"), result.get("url"), result)
        if not result.get("ok") or result.get("status") != "created":
            raise RuntimeError(str(result.get("error") or "Dropi did not confirm case creation."))
        return CaseCreationResult("created", result.get("chat_id"), result.get("url"), result)

    @staticmethod
    def _script(order_id: str, guide: str, message: str, evidence_path: Path) -> str:
        return r'''
import json, re, time
ORDER_ID = __ORDER_ID__
GUIDE = __GUIDE__
MESSAGE = __MESSAGE__
EVIDENCE = __EVIDENCE__

def body(): return js("document.body.innerText || ''")
def click_text(text):
    return js(f"""(() => {{
      const target = {json.dumps(text)};
      const items = [...document.querySelectorAll('button,a,label,[role=button],div,span')]
        .filter(e => {{ const r=e.getBoundingClientRect(); return r.width>0 && r.height>0 && (e.innerText||e.textContent||'').trim().includes(target); }})
        .sort((a,b) => (a.innerText||'').length - (b.innerText||'').length);
      if (!items.length) return false;
      const element = items[0].closest('button,a,label,[role=button]') || items[0];
      element.scrollIntoView({{block:'center'}}); element.click(); return true;
    }})()""")
if '/dashboard/orders' not in (page_info().get('url') or ''):
    new_tab('https://app.dropi.co/dashboard/orders'); wait_for_load(25); time.sleep(3)
if not js("!!document.querySelector('textarea')"):
    js("document.querySelector('button[title=\"Mostrar Filtros\"]')?.click()"); time.sleep(1)
js("document.querySelector('#radio_shipping_guide')?.click()")
js(f"""(() => {{ const field=document.querySelector('textarea'); if(!field)return false; const setter=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set; setter.call(field,{json.dumps(GUIDE)}); field.dispatchEvent(new Event('input',{{bubbles:true}})); field.dispatchEvent(new Event('change',{{bubbles:true}})); return true; }})()""")
click_text('Ok'); time.sleep(4); wait_for_load()
opened = js(f"""(() => {{ const row=[...document.querySelectorAll('table tbody tr')].find(item=>item.innerText.includes({json.dumps(GUIDE)})); const link=row?.querySelector('a[title="Nueva consulta"]'); if(!link)return false; link.click(); return true; }})()""")
if not opened:
    print('__JSON__'+json.dumps({'ok':False,'error':'new_case_action_not_found'})); raise SystemExit
time.sleep(1); wait_for_load()
if 'Orden ya tiene un caso' in body():
    print('__JSON__'+json.dumps({'ok':True,'status':'existing_case','url':page_info().get('url') or ''}, ensure_ascii=False)); raise SystemExit
for _ in range(20):
    time.sleep(.5); wait_for_load()
    if 'Transportadora' in body(): break
else:
    print('__JSON__'+json.dumps({'ok':False,'error':'wizard_not_loaded'})); raise SystemExit
click_text('Transportadora'); click_text('Siguiente'); time.sleep(2); wait_for_load()
click_text('Ordenes sin movimiento'); click_text('Siguiente'); time.sleep(2); wait_for_load()
filled = js(f"""(() => {{ const field=document.querySelector('textarea'); if(!field)return false; const setter=Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set; setter.call(field,{json.dumps(MESSAGE)}); field.dispatchEvent(new Event('input',{{bubbles:true}})); field.dispatchEvent(new Event('change',{{bubbles:true}})); return true; }})()""")
if not filled:
    print('__JSON__'+json.dumps({'ok':False,'error':'message_field_not_found'})); raise SystemExit
upload_file('input[type="file"]', EVIDENCE); time.sleep(4); wait_for_load()
click_text('Iniciar conversación'); time.sleep(4); wait_for_load()
url = page_info().get('url') or ''
match = re.search(r'cas_chat_id=([^&]+)', url)
if '/dashboard/cas/' not in url:
    print('__JSON__'+json.dumps({'ok':False,'error':'case_not_confirmed','url':url})); raise SystemExit
print('__JSON__'+json.dumps({'ok':True,'status':'created','chat_id':match.group(1) if match else None,'url':url}, ensure_ascii=False))
'''.replace("__ORDER_ID__", json.dumps(order_id)).replace("__GUIDE__", json.dumps(guide)).replace("__MESSAGE__", json.dumps(message)).replace("__EVIDENCE__", json.dumps(str(evidence_path)))
