from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class OrderSnapshot:
    order_id: str
    guide: str
    carrier: str
    current_status: str
    last_movement_at: Optional[datetime]


@dataclass(frozen=True)
class EligibilityDecision:
    status: str
    reason: str
    hours_without_movement: Optional[float]
