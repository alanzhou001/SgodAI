from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PositionState(StrEnum):
    IGNORED = "不关注"
    WATCH = "观察"
    LEFT_ACCUMULATION_WATCH = "左侧建仓观察"
    RIGHT_ADD_WATCH = "右侧增持观察"
    HOLD_TRACKING = "持有跟踪"
    REDUCE_WATCH = "减持观察"
    RISK_ALERT = "风险预警"


@dataclass(slots=True)
class Sector:
    id: str
    name: str
    cycle_horizon: str
    focus_level: str = "medium"
    drivers: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    indicators: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Asset:
    id: str
    ticker: str
    name: str
    market: str
    asset_type: str
    sector_id: str | None = None
    currency: str | None = None
    exchange: str | None = None
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Watchlist:
    id: str
    name: str
    asset_ids: list[str] = field(default_factory=list)
    sector_ids: list[str] = field(default_factory=list)
    description: str | None = None
    enabled: bool = True
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Event:
    id: str
    title: str
    event_type: str
    source: str
    source_url: str | None = None
    source_published_at: datetime | None = None
    received_at: datetime = field(default_factory=utc_now)
    raw_content_ref: str | None = None
    summary: str | None = None
    asset_ids: list[str] = field(default_factory=list)
    sector_ids: list[str] = field(default_factory=list)
    knowledge_node_ids: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    dedup_key: str | None = None
    confidence: float = 0.0
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Signal:
    id: str
    event_id: str
    asset_id: str | None = None
    sector_id: str | None = None
    impact_score: int = 0
    trend_score: int = 0
    sentiment_score: int = 0
    risk_score: int = 0
    scoring_version: str = "rules.v0"
    evidence: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class PositionWindowState:
    id: str
    asset_id: str
    previous_state: PositionState
    current_state: PositionState
    support_factors: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    watch_variables: list[str] = field(default_factory=list)
    triggered_by_event_ids: list[str] = field(default_factory=list)
    triggered_by_signal_ids: list[str] = field(default_factory=list)
    rule_version: str = "position.rules.v0"
    confidence: float = 0.0
    disclaimer: str = (
        "仅作为研究线索和仓位观察参考，不构成投资建议，不提供自动交易指令。"
    )
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Report:
    id: str
    report_type: str
    title: str
    period_start: datetime
    period_end: datetime
    sections: dict[str, Any] = field(default_factory=dict)
    event_ids: list[str] = field(default_factory=list)
    signal_ids: list[str] = field(default_factory=list)
    position_state_ids: list[str] = field(default_factory=list)
    generated_by: str = "core_engine"
    llm_provider_id: str | None = None
    grounded: bool = True
    disclaimer: str = (
        "本报告不构成投资建议，不提供确定性买卖指令，不承诺收益。"
    )
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True, kw_only=True)
class NotificationTarget:
    id: str
    channel: str
    name: str
    address_or_endpoint: str
    enabled: bool = True
    report_types: list[str] = field(default_factory=list)
    sectors: list[str] = field(default_factory=list)
    tickers: list[str] = field(default_factory=list)
    frequency: str = "daily"
    alert_threshold: dict[str, int] = field(default_factory=dict)
    last_send_status: str | None = None
    last_sent_at: datetime | None = None


@dataclass(slots=True, kw_only=True)
class EmailTarget(NotificationTarget):
    channel: str = "email"


@dataclass(slots=True)
class DeliveryLog:
    id: str
    target_id: str
    channel: str
    status: str
    report_id: str | None = None
    alert_id: str | None = None
    retry_count: int = 0
    error_message: str | None = None
    sent_at: datetime | None = None


@dataclass(slots=True)
class DataSource:
    id: str
    source_type: str
    provider: str
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ModelProvider:
    id: str
    provider_type: str
    model: str
    enabled: bool = True
    base_url: str | None = None
    api_key_env: str | None = None
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AgentProvider:
    id: str
    agent_type: str
    mode: str
    enabled: bool = True
    endpoint: str | None = None
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KnowledgeGraphNode:
    id: str
    node_type: str
    name: str
    aliases: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KnowledgeGraphEdge:
    id: str
    source_node_id: str
    target_node_id: str
    relation_type: str
    confidence: float = 1.0
    evidence_event_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
