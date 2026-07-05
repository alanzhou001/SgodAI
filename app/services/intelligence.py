from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from app.db import SQLiteSignalStore
from app.models import Asset, Event, PositionState, Signal
from app.providers import (
    CombinedDisclosureProvider,
    RSSNewsProvider,
    RSSSource,
    SinaAShareMarketDataProvider,
    SinaFinanceNewsProvider,
    YahooChartMarketDataProvider,
    normalize_market_ticker,
)
from app.providers.akshare_provider import AkShareMarketDataProvider
from app.scoring import ScoringEngine
from app.services.position_window import PositionWindowEngine


class AssetIntelligenceService:
    def __init__(
        self,
        *,
        market_provider: Any | None = None,
        market_fallback_provider: Any | None = None,
        news_provider: Any | None = None,
        disclosure_provider: Any | None = None,
        scoring_engine: ScoringEngine | None = None,
        position_engine: PositionWindowEngine | None = None,
        signal_store: SQLiteSignalStore | None = None,
    ) -> None:
        self.market_provider = market_provider or AkShareMarketDataProvider()
        self.market_fallback_providers = (
            [market_fallback_provider]
            if market_fallback_provider is not None
            else [SinaAShareMarketDataProvider(), YahooChartMarketDataProvider()]
        )
        self.news_provider = news_provider
        self.disclosure_provider = disclosure_provider or CombinedDisclosureProvider()
        self.scoring_engine = scoring_engine or ScoringEngine()
        self.position_engine = position_engine or PositionWindowEngine()
        self.signal_store = signal_store

    def build_asset_snapshot(
        self,
        asset: Asset,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        include_news: bool = True,
        include_disclosures: bool = True,
    ) -> dict[str, Any]:
        end = until or datetime.now(timezone.utc)
        start = since or (end - timedelta(days=90))
        errors: list[dict[str, str]] = []
        events: list[Event] = []

        rows, market_source = self._fetch_ohlcv(asset.ticker, since=start, until=end, errors=errors)
        if rows:
            events.extend(self.market_events(asset, rows, source=market_source))

        if include_news:
            events.extend(self._safe_news(asset, start, end, errors))

        if include_disclosures:
            events.extend(self._safe_disclosures(asset, start, end, errors))

        events = self._dedupe_events(self._ground_events(asset, events))[:24]
        signals = [self.scoring_engine.score_event(event) for event in events]
        position_state = self.position_engine.detect(
            asset.id,
            signals,
            previous_state=PositionState.WATCH,
        )
        persistence = self._persist(events, signals, position_state)
        return {
            "asset": asset,
            "events": events,
            "signals": signals,
            "scores": aggregate_scores(signals),
            "position_state": position_state,
            "score_source": self.scoring_engine.scoring_version,
            "source_status": {
                "market_data": market_source,
                "event_count": len(events),
                "signal_count": len(signals),
                "errors": errors,
            },
            "persistence": persistence,
            "generated_at": datetime.now(timezone.utc),
            "disclaimer": "仅作为研究线索、信息整理和风险提示，不构成投资建议或买卖指令。",
        }

    def _persist(
        self,
        events: list[Event],
        signals: list[Signal],
        position_state: Any,
    ) -> dict[str, Any]:
        if self.signal_store is None:
            return {"enabled": False}
        counts = self.signal_store.save_snapshot(events, signals, [position_state])
        return {
            "enabled": True,
            "store": str(self.signal_store.path),
            "counts": counts,
        }

    def _fetch_ohlcv(
        self,
        ticker: str,
        *,
        since: datetime,
        until: datetime,
        errors: list[dict[str, str]],
    ) -> tuple[list[dict[str, Any]], str]:
        providers = [self.market_provider, *self.market_fallback_providers]
        for provider in providers:
            source = getattr(provider, "provider_id", "market_data")
            try:
                rows = provider.fetch_ohlcv(ticker, since=since, until=until)
                if rows:
                    return rows, source
                errors.append({"source": source, "error": "empty OHLCV result"})
            except Exception as exc:  # noqa: BLE001
                errors.append({"source": source, "error": str(exc)})
        return [], "unavailable"

    def _safe_news(
        self,
        asset: Asset,
        since: datetime,
        until: datetime,
        errors: list[dict[str, str]],
    ) -> list[Event]:
        provider = self.news_provider or SinaFinanceNewsProvider()
        try:
            return provider.fetch_news(asset.name or asset.ticker, since=since, until=until)
        except Exception as exc:  # noqa: BLE001
            errors.append({"source": getattr(provider, "provider_id", "news"), "error": str(exc)})
            return []

    def _safe_disclosures(
        self,
        asset: Asset,
        since: datetime,
        until: datetime,
        errors: list[dict[str, str]],
    ) -> list[Event]:
        try:
            return self.disclosure_provider.fetch_announcements(
                [asset],
                since=since,
                until=until,
            ) + self.disclosure_provider.fetch_reports([asset], since=since, until=until)
        except Exception as exc:  # noqa: BLE001
            errors.append({"source": getattr(self.disclosure_provider, "provider_id", "disclosure"), "error": str(exc)})
            return []

    @staticmethod
    def market_events(asset: Asset, rows: list[dict[str, Any]], *, source: str) -> list[Event]:
        ordered = sorted(rows, key=lambda row: str(row.get("trade_date") or row.get("date") or ""))
        if len(ordered) < 2:
            return []
        first = ordered[0]
        last = ordered[-1]
        first_close = _float(first.get("close"))
        last_close = _float(last.get("close"))
        if first_close <= 0 or last_close <= 0:
            return []
        highs = [_float(row.get("high")) for row in ordered if _float(row.get("high")) > 0]
        lows = [_float(row.get("low")) for row in ordered if _float(row.get("low")) > 0]
        volumes = [_float(row.get("volume")) for row in ordered if _float(row.get("volume")) > 0]
        change_pct = (last_close / first_close - 1) * 100
        high = max(highs) if highs else last_close
        low = min(lows) if lows else last_close
        range_pct = (high / low - 1) * 100 if low else 0.0
        drawdown_pct = (last_close / high - 1) * 100 if high else 0.0
        avg_volume = sum(volumes[:-1]) / len(volumes[:-1]) if len(volumes) > 1 else volumes[-1]
        volume_ratio = volumes[-1] / avg_volume if avg_volume else 1.0
        digest = hashlib.sha1(
            f"{asset.ticker}:{first.get('trade_date')}:{last.get('trade_date')}:{last_close}".encode("utf-8")
        ).hexdigest()[:12]
        direction = "上涨" if change_pct >= 0 else "下跌"
        return [
            Event(
                id=f"evt_mkt_{digest}",
                title=f"{asset.name} 区间价格{direction} {change_pct:.2f}%，量能比 {volume_ratio:.2f}",
                event_type="market_data",
                source=source,
                source_published_at=_date(last.get("trade_date")),
                summary=(
                    f"{asset.ticker} 从 {first.get('trade_date')} 到 {last.get('trade_date')} "
                    f"收盘价变动 {change_pct:.2f}%，区间振幅 {range_pct:.2f}%。"
                ),
                asset_ids=[asset.id],
                sector_ids=[asset.sector_id] if asset.sector_id else [],
                evidence={
                    "ticker": asset.ticker,
                    "first_trade_date": first.get("trade_date"),
                    "last_trade_date": last.get("trade_date"),
                    "first_close": first_close,
                    "last_close": last_close,
                    "price_change_pct": round(change_pct, 4),
                    "range_pct": round(range_pct, 4),
                    "drawdown_pct": round(drawdown_pct, 4),
                    "volume_ratio": round(volume_ratio, 4),
                    "rows": len(ordered),
                },
                confidence=0.9,
            )
        ]

    @staticmethod
    def _ground_events(asset: Asset, events: list[Event]) -> list[Event]:
        for event in events:
            if not event.asset_ids:
                event.asset_ids.append(asset.id)
            if asset.sector_id and not event.sector_ids:
                event.sector_ids.append(asset.sector_id)
        return events

    @staticmethod
    def _dedupe_events(events: list[Event]) -> list[Event]:
        seen: set[str] = set()
        unique: list[Event] = []
        for event in events:
            key = event.dedup_key or event.id
            if key in seen:
                continue
            seen.add(key)
            unique.append(event)
        return unique


def aggregate_scores(signals: list[Signal]) -> dict[str, int]:
    if not signals:
        return {"impact": 50, "trend": 50, "sentiment": 50, "risk": 45}
    return {
        "impact": _blend_avg_max([signal.impact_score for signal in signals]),
        "trend": _avg([signal.trend_score for signal in signals]),
        "sentiment": _avg([signal.sentiment_score for signal in signals]),
        "risk": max(signal.risk_score for signal in signals),
    }


def _blend_avg_max(values: list[int]) -> int:
    return min(100, round((_avg(values) * 0.65) + (max(values) * 0.35)))


def _avg(values: list[int]) -> int:
    return round(sum(values) / len(values)) if values else 0


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _date(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value)).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
