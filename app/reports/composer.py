from __future__ import annotations

import hashlib
from datetime import datetime

from app.models import Event, PositionWindowState, Report, Signal


class ReportComposer:
    def compose_daily_report(
        self,
        events: list[Event],
        signals: list[Signal],
        position_states: list[PositionWindowState],
        period_start: datetime,
        period_end: datetime,
    ) -> Report:
        digest = hashlib.sha1(
            f"{period_start.isoformat()}:{period_end.isoformat()}:{len(events)}".encode("utf-8")
        ).hexdigest()[:10]
        high_impact = [signal for signal in signals if signal.impact_score >= 65]
        high_risk = [signal for signal in signals if signal.risk_score >= 60]

        sections = {
            "market_overview": {
                "event_count": len(events),
                "signal_count": len(signals),
                "position_state_count": len(position_states),
            },
            "sector_focus": self._group_by_sector(events),
            "asset_focus": self._group_by_asset(events),
            "key_announcements": [event.title for event in events if event.event_type == "announcement"],
            "abnormal_signals": [signal.id for signal in high_impact],
            "risk_notes": [signal.id for signal in high_risk],
            "next_watchlist": [
                {
                    "asset_id": state.asset_id,
                    "state": state.current_state.value,
                    "watch_variables": state.watch_variables,
                }
                for state in position_states
            ],
        }

        return Report(
            id=f"rpt_{digest}",
            report_type="daily",
            title="SgodAI Market Radar Daily",
            period_start=period_start,
            period_end=period_end,
            sections=sections,
            event_ids=[event.id for event in events],
            signal_ids=[signal.id for signal in signals],
            position_state_ids=[state.id for state in position_states],
            generated_by="core_engine",
            grounded=True,
        )

    @staticmethod
    def _group_by_sector(events: list[Event]) -> dict[str, int]:
        result: dict[str, int] = {}
        for event in events:
            for sector_id in event.sector_ids:
                result[sector_id] = result.get(sector_id, 0) + 1
        return result

    @staticmethod
    def _group_by_asset(events: list[Event]) -> dict[str, int]:
        result: dict[str, int] = {}
        for event in events:
            for asset_id in event.asset_ids:
                result[asset_id] = result.get(asset_id, 0) + 1
        return result

