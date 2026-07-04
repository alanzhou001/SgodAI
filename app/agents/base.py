from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentCommand:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    requested_by: str = "local_user"


class AgentProvider(ABC):
    provider_id: str

    @abstractmethod
    def healthcheck(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def query_stock_intelligence(self, asset_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_sector_brief(self, sector_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_asset_report(self, asset_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def explain_position_window(self, state_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def query_risk_events(self, scope: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def trigger_fetch(self, scope: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def trigger_report(self, report_type: str) -> dict[str, Any]:
        raise NotImplementedError

