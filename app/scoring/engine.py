from __future__ import annotations

import hashlib

from app.models import Event, Signal


class ScoringEngine:
    scoring_version = "rules.realdata.v1"

    def score_event(self, event: Event) -> Signal:
        text = f"{event.title} {event.summary or ''} {event.event_type}".lower()
        impact = self._score_keywords(
            text,
            ["订单", "政策", "财报", "业绩", "并购", "突破", "回购", "涨停", "放量"],
            base=45,
        )
        trend = self._score_keywords(
            text,
            ["改善", "增长", "上升", "景气", "催化", "创新高", "放量", "修复"],
            base=42,
        )
        sentiment = self._score_keywords(
            text,
            ["利好", "改善", "回购", "增长", "预增", "上修", "中标"],
            base=45,
        )
        risk = self._score_keywords(
            text,
            ["减持", "监管", "下滑", "风险", "解禁", "亏损", "问询", "处罚", "退市"],
            base=30,
        )
        if event.event_type == "market_data":
            market_scores = self._market_scores(event.evidence)
            impact = max(impact, market_scores["impact"])
            trend = max(trend, market_scores["trend"])
            sentiment = market_scores["sentiment"]
            risk = max(risk, market_scores["risk"])

        digest = hashlib.sha1(event.id.encode("utf-8")).hexdigest()[:10]
        return Signal(
            id=f"sig_{digest}",
            event_id=event.id,
            asset_id=event.asset_ids[0] if event.asset_ids else None,
            sector_id=event.sector_ids[0] if event.sector_ids else None,
            impact_score=min(100, impact),
            trend_score=min(100, trend),
            sentiment_score=min(100, sentiment),
            risk_score=min(100, risk),
            scoring_version=self.scoring_version,
            evidence={
                "event_id": event.id,
                "source": event.source,
                "rule": self.scoring_version,
                "event_type": event.event_type,
                "market_evidence": event.evidence if event.event_type == "market_data" else None,
            },
        )

    @staticmethod
    def _score_keywords(text: str, keywords: list[str], base: int) -> int:
        hits = sum(1 for keyword in keywords if keyword in text)
        return base + hits * 12

    @staticmethod
    def _market_scores(evidence: dict[str, object]) -> dict[str, int]:
        change = _float(evidence.get("price_change_pct"))
        abs_change = abs(change)
        volume_ratio = max(0.0, _float(evidence.get("volume_ratio"), default=1.0))
        drawdown = abs(min(0.0, _float(evidence.get("drawdown_pct"))))
        volatility = abs(_float(evidence.get("range_pct")))

        impact = 44 + min(28, int(abs_change * 2.1)) + min(12, int(max(0, volume_ratio - 1) * 8))
        trend = 50 + int(change * 2.2)
        sentiment = 50 + int(change * 2.4)
        risk = 34 + min(34, int(drawdown * 2.4)) + min(16, int(volatility * 1.1))
        if change < -4:
            risk += min(18, int(abs_change * 1.4))
        if volume_ratio >= 2 and change < 0:
            risk += 8
        return {
            "impact": _clamp(impact),
            "trend": _clamp(trend),
            "sentiment": _clamp(sentiment),
            "risk": _clamp(risk),
        }


def _float(value: object, *, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))
