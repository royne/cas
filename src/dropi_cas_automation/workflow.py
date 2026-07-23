from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any, Protocol

from .models import OrderSnapshot
from .rules import EligibilityPolicy, evaluate_order


class ExternalWriteDisabled(PermissionError):
    pass


class AutomationGateway(Protocol):
    def load_orders(self) -> list[OrderSnapshot]:
        ...

    def refresh_history(self, order: OrderSnapshot) -> OrderSnapshot:
        ...

    def validate_case(self, order: OrderSnapshot) -> str:
        ...

    def capture_evidence(self, order: OrderSnapshot) -> str:
        ...

    def create_case(self, order: OrderSnapshot, evidence_path: str) -> str:
        ...

    def send_followup(self, order: OrderSnapshot) -> None:
        ...


class AutomationPipeline:
    """Orchestrates a configured gateway without embedding account state.

    The gateway owns browser/API implementation. The pipeline owns ordering,
    eligibility decisions, audit-shaped results, and write permissions.
    """

    def __init__(self, gateway: AutomationGateway, policy: EligibilityPolicy | None = None):
        self.gateway = gateway
        self.policy = policy or EligibilityPolicy()

    def run(self, *, execute: bool = False, allow_external_writes: bool = False, limit: int | None = None) -> dict[str, Any]:
        if execute and not allow_external_writes:
            raise ExternalWriteDisabled("External writes are disabled. Use explicit write authorization before creating cases or sending follow-ups.")

        results: list[dict[str, Any]] = []
        candidates = self.gateway.load_orders()
        if limit is not None:
            candidates = candidates[:limit]
        for order in candidates:
            refreshed = self.gateway.refresh_history(order)
            decision = evaluate_order(refreshed, self.policy)
            item: dict[str, Any] = {"order": asdict(refreshed), "decision": asdict(decision), "status": decision.status}
            if decision.status != "eligible":
                results.append(item)
                continue
            remote_status = self.gateway.validate_case(refreshed)
            if remote_status != "eligible":
                item["status"] = remote_status
                results.append(item)
                continue
            if not execute:
                results.append(item)
                continue
            evidence_path = self.gateway.capture_evidence(refreshed)
            if not evidence_path or not Path(evidence_path).is_file():
                item["status"] = "evidence_missing"
                results.append(item)
                continue
            chat_id = self.gateway.create_case(refreshed, evidence_path)
            item["status"] = "created"
            item["chat_id"] = chat_id
            item["evidence_path"] = evidence_path
            results.append(item)

        summary = dict(Counter(item["status"] for item in results))
        return {"ok": True, "mode": "execute" if execute else "dry_run", "summary": summary, "results": results}
