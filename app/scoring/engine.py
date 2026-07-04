from __future__ import annotations

import hashlib

from app.models import Event, Signal


class ScoringEngine:
    scoring_version = "rules.v0"

    def score_event(self, event: Event) -> Signal:
        text = f"{event.title} {event.summary or ''} {event.event_type}".lower()
        impact = self._score_keywords(text, ["订单", "政策", "财报", "并购", "突破"], base=45)
        trend = self._score_keywords(text, ["改善", "增长", "上升", "景气", "催化"], base=42)
        sentiment = self._score_keywords(text, ["利好", "改善", "回购", "增长"], base=45)
        risk = self._score_keywords(text, ["减持", "监管", "下滑", "风险", "解禁"], base=30)

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
                "rule": "keyword_weighted_demo",
            },
        )

    @staticmethod
    def _score_keywords(text: str, keywords: list[str], base: int) -> int:
        hits = sum(1 for keyword in keywords if keyword in text)
        return base + hits * 12

