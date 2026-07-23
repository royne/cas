from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path
from typing import Any, Protocol


class BrowserRunner(Protocol):
    def execute_json(self, code: str, timeout_seconds: int) -> dict[str, Any]:
        ...


class OrdersReportDownloader:
    """Read-only Dropi orders-report downloader.

    The browser session generates the official report and exposes its normal
    report metadata. The downloaded XLSX is written only to `output_dir`.
    Browser tokens remain inside the browser JavaScript context.
    """

    def __init__(self, runner: BrowserRunner, output_dir: Path):
        self.runner = runner
        self.output_dir = output_dir

    def download(self, *, allow_external_read: bool, timeout_seconds: int = 180) -> Path:
        if not allow_external_read:
            raise PermissionError("External reads are disabled. Explicit read authorization is required to download an orders report.")
        self._request_report()
        report = self._wait_for_report(timeout_seconds)
        return self._download_file(report)

    def _request_report(self) -> None:
        result = self.runner.execute_json(
            r'''
import json, time
orders_url = 'https://app.dropi.co/dashboard/orders'
if 'app.dropi.co' not in (page_info().get('url') or ''):
    new_tab(orders_url)
    wait_for_load(25)
    time.sleep(3)
def visible(element):
    rect = element.getBoundingClientRect()
    return rect.width > 0 and rect.height > 0

def click_text(label):
    return js(f"""(() => {{
      const target = {json.dumps(label)};
      const element = [...document.querySelectorAll('button,a,[role=button],dropi-button,li,span,div')]
        .filter(e => {{ const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && (e.innerText || e.textContent || '').trim().includes(target); }})
        .sort((a,b) => (a.innerText || '').length - (b.innerText || '').length)[0];
      if (!element) return false;
      element.scrollIntoView({{block:'center'}}); element.click(); return true;
    }})()""")
actions = js("""(() => { const toggle = document.querySelector('a.dropdown-toggle'); if (!toggle) return false; if (toggle.getAttribute('aria-expanded') !== 'true') toggle.click(); return true; })()""")
time.sleep(1)
report = js("""(() => { const item = [...document.querySelectorAll('.dropdown-menu button,.dropdown-menu a')].find(e => (e.innerText || e.textContent || '').trim() === 'Órdenes (Una orden por fila)'); if (!item) return false; item.click(); return true; })()""")
print('__JSON__' + json.dumps({'ok': bool(actions and report)}, ensure_ascii=False))
''',
            timeout_seconds=90,
        )
        if not result.get("ok"):
            raise RuntimeError("Dropi did not expose the orders report action.")

    def _wait_for_report(self, timeout_seconds: int) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            result = self.runner.execute_json(
                r'''
import json
script = """(async () => {
  const raw = localStorage.getItem('DROPI_token');
  const token = raw ? JSON.parse(raw) : null;
  if (!token) return {ok:false,error:'missing_session_token'};
  const response = await fetch('https://api.dropi.co/api/reports/index?startData=0&pageSize=30&page=1&search=&status=ALL', {
    headers: {'X-Authorization': 'Bearer ' + token}
  });
  const data = await response.json();
  const report = (data.objects || []).find(item => item.report_name === 'Reporte orderByRow' && item.ready && !item.error && item.ready_records > 0);
  return {ok: response.ok && data.isSuccess === true, report};
})()"""
print('__JSON__' + json.dumps(js(script), ensure_ascii=False))
''',
                timeout_seconds=90,
            )
            if result.get("ok") and result.get("report"):
                return dict(result["report"])
            time.sleep(5)
        raise TimeoutError("Orders report did not become ready before the configured timeout.")

    def _download_file(self, report: dict[str, Any]) -> Path:
        base = "https://d1l4mzebo786pw.cloudfront.net" if report.get("storage_type") == "s3" else "https://reports.dropi.co"
        name = Path(str(report.get("display_name") or report.get("file_name") or "orders.xlsx")).name
        if not name.lower().endswith(".xlsx"):
            name += ".xlsx"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = self.output_dir / name
        urllib.request.urlretrieve(f"{base}/{report.get('file_path', '')}{report.get('file_name', '')}", target)
        if not target.is_file() or target.stat().st_size <= 0:
            raise RuntimeError("Orders report download was empty.")
        return target
