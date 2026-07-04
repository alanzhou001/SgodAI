from __future__ import annotations

import hashlib

from app.models import PositionState, PositionWindowState, Signal


class PositionWindowEngine:
    rule_version = "position.rules.v0"

    def detect(
        self,
        asset_id: str,
        signals: list[Signal],
        previous_state: PositionState = PositionState.WATCH,
    ) -> PositionWindowState:
        if not signals:
            current = PositionState.IGNORED
            support_factors = ["暂无有效信号"]
            risk_factors = []
        else:
            avg_impact = self._avg(signal.impact_score for signal in signals)
            avg_trend = self._avg(signal.trend_score for signal in signals)
            avg_sentiment = self._avg(signal.sentiment_score for signal in signals)
            max_risk = max(signal.risk_score for signal in signals)

            if max_risk >= 72:
                current = PositionState.RISK_ALERT
            elif avg_trend >= 68 and avg_impact >= 64 and avg_sentiment >= 52:
                current = PositionState.RIGHT_ADD_WATCH
            elif avg_impact >= 58 and max_risk < 62:
                current = PositionState.LEFT_ACCUMULATION_WATCH
            elif avg_trend < 42 or avg_sentiment < 38:
                current = PositionState.REDUCE_WATCH
            else:
                current = PositionState.WATCH

            support_factors = [
                f"Impact 平均分 {avg_impact:.0f}",
                f"Trend 平均分 {avg_trend:.0f}",
                f"Sentiment 平均分 {avg_sentiment:.0f}",
            ]
            risk_factors = [f"Risk 最高分 {max_risk:.0f}"]

        signal_ids = [signal.id for signal in signals]
        event_ids = [signal.event_id for signal in signals]
        digest = hashlib.sha1(f"{asset_id}:{','.join(signal_ids)}".encode("utf-8")).hexdigest()[:10]
        return PositionWindowState(
            id=f"pws_{digest}",
            asset_id=asset_id,
            previous_state=previous_state,
            current_state=current,
            support_factors=support_factors,
            risk_factors=risk_factors,
            watch_variables=["财报订单", "行业景气指标", "成交量结构", "风险事件变化"],
            triggered_by_event_ids=event_ids,
            triggered_by_signal_ids=signal_ids,
            rule_version=self.rule_version,
            confidence=0.74 if signals else 0.35,
        )

    @staticmethod
    def _avg(values: object) -> float:
        items = list(values)
        return sum(items) / len(items) if items else 0.0

