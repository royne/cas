from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol


class BrowserRunner(Protocol):
    def execute_json(self, code: str, timeout_seconds: int) -> dict[str, Any]:
        ...


class EvidenceCapture:
    def __init__(self, runner: BrowserRunner, output_dir: Path):
        self.runner = runner
        self.output_dir = output_dir

    def capture(self, guide: str, *, allow_external_read: bool) -> Path:
        if not allow_external_read:
            raise PermissionError("External reads are disabled. Explicit read authorization is required to capture evidence.")
        result = self.runner.execute_json(self._script(guide), timeout_seconds=120)
        source = Path(str(result.get("screenshot") or ""))
        if not result.get("ok") or not source.is_file():
            raise RuntimeError("Dropi did not return a usable evidence screenshot.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        target = self.output_dir / f"guide_{guide}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        shutil.copyfile(source, target)
        return target

    @staticmethod
    def _script(guide: str) -> str:
        return r'''
import json
GUIDE = __GUIDE__
text = js("document.body.innerText || ''")
if GUIDE not in text or 'Historial de estados' not in text:
    print('__JSON__' + json.dumps({'ok':False, 'error':'expected_order_detail_not_visible'}))
else:
    print('__JSON__' + json.dumps({'ok':True, 'screenshot':capture_screenshot()}, ensure_ascii=False))
'''.replace("__GUIDE__", json.dumps(guide))
