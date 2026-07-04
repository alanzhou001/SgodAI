from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.models import Event, PositionWindowState, Report


@dataclass(slots=True)
class GroundedAIOutput:
    result: dict[str, Any]
    evidence_refs: list[str]
    confidence: float
    risk_notes: list[str] = field(default_factory=list)
    disclaimer: str = "不构成投资建议，不提供确定性买卖指令。"
    input_event_ids: list[str] = field(default_factory=list)
    provider: str | None = None
    model: str | None = None


class LLMProvider(ABC):
    provider_id: str

    @abstractmethod
    def summarize_event(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def classify_event(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def score_event(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def extract_entities(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def extract_risks(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def analyze_policy(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def analyze_financial_report(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def generate_stock_brief(self, asset_id: str, events: list[Event]) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def generate_sector_brief(self, sector_id: str, events: list[Event]) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def generate_daily_report(self, report: Report) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def generate_weekly_report(self, report: Report) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def explain_position_window(
        self,
        state: PositionWindowState,
        events: list[Event],
    ) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def analyze_supply_chain_impact(self, event: Event) -> GroundedAIOutput:
        raise NotImplementedError

    @abstractmethod
    def deduplicate_semantic_events(self, events: list[Event]) -> GroundedAIOutput:
        raise NotImplementedError

