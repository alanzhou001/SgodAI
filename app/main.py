from __future__ import annotations

from datetime import datetime, timezone

from app.models import Event, PositionState
from app.reports import ReportComposer
from app.scoring import ScoringEngine
from app.services import PositionWindowEngine


def build_demo_report() -> str:
    events = [
        Event(
            id="evt_demo_001",
            title="AI 算力产业链订单改善，海外映射公司上调资本开支",
            event_type="industry",
            source="demo",
            summary="订单改善与资本开支上调共同强化算力链景气线索。",
            asset_ids=["asset_688525"],
            sector_ids=["sector_ai_compute"],
            confidence=0.82,
        ),
        Event(
            id="evt_demo_002",
            title="存储芯片价格继续上升，部分下游客户提前锁单",
            event_type="price",
            source="demo",
            summary="价格上升与锁单行为可能改善行业趋势评分。",
            asset_ids=["asset_603986"],
            sector_ids=["sector_memory"],
            confidence=0.79,
        ),
    ]

    scoring = ScoringEngine()
    signals = [scoring.score_event(event) for event in events]

    position_engine = PositionWindowEngine()
    state = position_engine.detect(
        "asset_688525",
        [signals[0]],
        previous_state=PositionState.WATCH,
    )

    now = datetime.now(timezone.utc)
    report = ReportComposer().compose_daily_report(
        events=events,
        signals=signals,
        position_states=[state],
        period_start=now,
        period_end=now,
    )
    return f"{report.title}: {len(report.event_ids)} events, {len(report.signal_ids)} signals"


if __name__ == "__main__":
    print(build_demo_report())

