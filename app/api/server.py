from __future__ import annotations

import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in realdata profile
    load_dotenv = None  # type: ignore

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - exercised only before optional deps are installed
    FastAPI = None  # type: ignore
    HTTPException = RuntimeError  # type: ignore
    CORSMiddleware = None  # type: ignore
    StaticFiles = None  # type: ignore

from app.db import SQLiteSignalStore
from app.llm.openai_compatible import OpenAICompatibleLLMProvider
from app.models import Asset, Event
from app.providers import (
    PublicAssetSearchProvider,
    RSSNewsProvider,
    RSSSource,
    SinaAShareMarketDataProvider,
    SinaFinanceNewsProvider,
    YahooChartMarketDataProvider,
    normalize_market_ticker,
    provider_registry,
)
from app.providers.akshare_provider import AkShareMarketDataProvider
from app.providers.disclosure_provider import CombinedDisclosureProvider
from app.services import AssetIntelligenceService, ConfigAssistService

if load_dotenv is not None:
    load_dotenv()


def create_app() -> Any:
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Run `pip install -e .[realdata]`.")

    app = FastAPI(title="SgodAI Market Radar API", version="0.1.0")
    if CORSMiddleware is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "market_data": {
                "primary": "akshare_market_data",
                "fallback": "sina_a_share_market_data + yahoo_chart_market_data",
                "status": "primary_with_multi_fallback",
                "note": (
                    "AkShare may fail when EastMoney endpoints are blocked by the current network; "
                    "A-share can fall back to Sina, and HK/US OHLCV can fall back to Yahoo Chart."
                ),
            },
            "llm": "deepseek",
            "disclaimer": (
                "不构成投资建议，不提供自动交易或确定性买卖指令。"
            ),
        }

    @app.get("/api/assets/search")
    def asset_search(
        q: str,
        limit: int = 20,
        markets: str = "A-share,HK",
    ) -> dict[str, Any]:
        provider = PublicAssetSearchProvider()
        results = provider.search_assets(
            q,
            limit=limit,
            markets=[item.strip() for item in markets.split(",") if item.strip()],
        )
        return {
            "query": q,
            "results": results,
            "source": provider.provider_id,
            "errors": provider.last_errors,
        }

    @app.get("/api/providers/registry")
    def providers_registry() -> dict[str, Any]:
        return {
            "providers": provider_registry(),
            "principle": "Core Engine provider interfaces are swappable; paid or licensed providers stay disabled until configured.",
        }

    @app.get("/api/assets/{ticker}/quote")
    def asset_quote(ticker: str) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        for provider in _market_provider_chain():
            try:
                quote = provider.fetch_latest_quote(ticker)
                return {
                    "ticker": ticker,
                    "quote": quote,
                    "source": getattr(provider, "provider_id", "market_data"),
                    "errors": errors,
                }
            except Exception as exc:  # noqa: BLE001
                errors.append({"source": getattr(provider, "provider_id", "market_data"), "error": str(exc)})
        raise HTTPException(status_code=502, detail={"errors": errors})

    @app.get("/api/assets/{ticker}/ohlcv")
    def asset_ohlcv(
        ticker: str,
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        since = datetime.fromisoformat(start) if start else None
        until = datetime.fromisoformat(end) if end else None
        errors: list[dict[str, str]] = []
        for provider in _market_provider_chain():
            source = getattr(provider, "provider_id", "market_data")
            try:
                rows = provider.fetch_ohlcv(ticker, since=since, until=until)
                if not rows:
                    errors.append({"source": source, "error": "empty OHLCV result"})
                    continue
                return {
                    "ticker": ticker,
                    "rows": rows,
                    "source": source,
                    "errors": errors,
                }
            except Exception as exc:  # noqa: BLE001
                errors.append({"source": source, "error": str(exc)})
        raise HTTPException(status_code=502, detail={"errors": errors})

    @app.get("/api/news/rss")
    def rss_news(
        query: str = "",
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        provider = RSSNewsProvider(_rss_sources_from_config())
        try:
            events = provider.fetch_news(
                query,
                since=_parse_date(start),
                until=_parse_date(end),
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "source": provider.provider_id,
            "events": [_to_json(event) for event in events],
            "errors": provider.last_errors,
        }

    @app.get("/api/news")
    def news(
        query: str = "",
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        since = _parse_date(start)
        until = _parse_date(end)
        rss_provider = RSSNewsProvider(_rss_sources_from_config())
        sina_provider = _sina_provider_from_config()
        events: list[Event] = []
        errors: list[dict[str, str]] = []

        events.extend(rss_provider.fetch_news(query, since=since, until=until))
        errors.extend(rss_provider.last_errors)
        try:
            events.extend(sina_provider.fetch_news(query, since=since, until=until))
        except Exception as exc:  # noqa: BLE001
            errors.append({"source": sina_provider.provider_id, "error": str(exc)})

        return {
            "sources": [rss_provider.provider_id, sina_provider.provider_id],
            "events": [_to_json(event) for event in _dedupe_events(events)],
            "errors": errors,
        }

    @app.get("/api/disclosures/announcements")
    def disclosure_announcements(
        ticker: str,
        name: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        provider = CombinedDisclosureProvider()
        asset = _asset_from_ticker(ticker, name=name)
        try:
            events = provider.fetch_announcements(
                [asset],
                since=_parse_date(start),
                until=_parse_date(end),
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "source": provider.provider_id,
            "ticker": ticker,
            "events": [_to_json(event) for event in events],
        }

    @app.get("/api/disclosures/reports")
    def disclosure_reports(
        ticker: str,
        name: str | None = None,
        start: str | None = None,
        end: str | None = None,
    ) -> dict[str, Any]:
        provider = CombinedDisclosureProvider()
        asset = _asset_from_ticker(ticker, name=name)
        try:
            events = provider.fetch_reports(
                [asset],
                since=_parse_date(start),
                until=_parse_date(end),
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "source": provider.provider_id,
            "ticker": ticker,
            "events": [_to_json(event) for event in events],
        }

    @app.post("/api/llm/config-assist")
    def config_assist(payload: dict[str, Any]) -> dict[str, Any]:
        kind = str(payload.get("kind") or "sector")
        name = str(payload.get("name") or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="name is required")
        service = ConfigAssistService(llm_provider=_deepseek_provider())
        try:
            if kind == "sector":
                result = service.assist_sector(
                    name,
                    market_scope=[str(item) for item in payload.get("market_scope") or ["A-share", "HK"]],
                )
            elif kind == "asset":
                result = service.assist_asset(name, payload)
            else:
                raise HTTPException(status_code=400, detail=f"unsupported assist kind: {kind}")
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "kind": kind,
            "name": name,
            "result": result,
            "provider": result.get("provider"),
            "model": result.get("model"),
            "disclaimer": result.get("disclaimer", "不构成投资建议，不提供确定性买卖指令。"),
        }

    @app.get("/api/assets/{ticker}/intelligence")
    def asset_intelligence(
        ticker: str,
        name: str | None = None,
        sector: str | None = None,
        days: int = 90,
        include_news: bool = True,
        include_disclosures: bool = True,
    ) -> dict[str, Any]:
        asset = _asset_from_ticker(ticker, name=name, sector=sector)
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=max(7, min(days, 365)))
        try:
            store = SQLiteSignalStore()
            snapshot = AssetIntelligenceService(signal_store=store).build_asset_snapshot(
                asset,
                since=start,
                until=end,
                include_news=include_news,
                include_disclosures=include_disclosures,
            )
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return _to_json(snapshot)

    @app.get("/api/db/status")
    def db_status() -> dict[str, Any]:
        store = SQLiteSignalStore()
        return {
            "path": str(store.path),
            "counts": store.counts(),
            "local_first": True,
            "tables": ["events", "signals", "position_window_states"],
        }

    @app.get("/api/db/recent")
    def db_recent(limit: int = 50) -> dict[str, Any]:
        store = SQLiteSignalStore()
        safe_limit = max(1, min(limit, 500))
        return {
            "path": str(store.path),
            "events": store.recent_events(safe_limit),
            "signals": store.recent_signals(safe_limit),
            "position_window_states": store.recent_position_states(safe_limit),
        }

    @app.post("/api/llm/event-summary")
    def event_summary(payload: dict[str, Any]) -> dict[str, Any]:
        provider = _deepseek_provider()
        event = Event(
            id=str(payload.get("id") or "evt_manual"),
            title=str(payload.get("title") or ""),
            event_type=str(payload.get("event_type") or "manual"),
            source=str(payload.get("source") or "api"),
            summary=payload.get("summary"),
            evidence=dict(payload.get("evidence") or {}),
            confidence=float(payload.get("confidence") or 0.5),
        )
        try:
            output = provider.summarize_event(event)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {
            "result": output.result,
            "evidence_refs": output.evidence_refs,
            "confidence": output.confidence,
            "risk_notes": output.risk_notes,
            "disclaimer": output.disclaimer,
            "provider": output.provider,
            "model": output.model,
        }

    public_dir = _public_dir()
    if StaticFiles is not None and public_dir.exists():
        app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")

    return app


def _deepseek_provider() -> OpenAICompatibleLLMProvider:
    return OpenAICompatibleLLMProvider(
        provider_id="deepseek",
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        api_key_env="DEEPSEEK_API_KEY",
    )


def _market_provider_chain() -> list[Any]:
    return [
        AkShareMarketDataProvider(),
        SinaAShareMarketDataProvider(),
        YahooChartMarketDataProvider(),
    ]


def _public_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "public"


def _asset_from_ticker(
    ticker: str,
    *,
    name: str | None = None,
    sector: str | None = None,
) -> Asset:
    market, symbol = normalize_market_ticker(ticker)
    return Asset(
        id=f"asset_{ticker.upper().replace('.', '_')}",
        ticker=ticker.upper(),
        name=name or symbol,
        market=market,
        asset_type="stock",
        sector_id=f"sector_{_slug(sector)}" if sector else None,
        exchange=ticker.upper().split(".")[-1] if "." in ticker else None,
        metadata={"sector": sector} if sector else {},
    )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _slug(value: str | None) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in str(value or "").lower()).strip("_")


def _rss_sources_from_config() -> list[RSSSource]:
    news_config = _news_config()
    source_configs = news_config.get("sources") or []
    sources: list[RSSSource] = []
    for source in source_configs:
        url = str(source.get("url") or "").strip()
        if not url:
            continue
        sources.append(
            RSSSource(
                name=str(source.get("name") or url),
                url=url,
                weight=float(source.get("weight") or 1.0),
            )
        )
    return sources


def _sina_provider_from_config() -> SinaFinanceNewsProvider:
    news_config = _news_config()
    fallback_sources = news_config.get("fallback_sources") or []
    for source in fallback_sources:
        if source.get("provider") != "sina_finance_rollnews" or not source.get("enabled", True):
            continue
        lids = [str(lid) for lid in source.get("lids") or []]
        return SinaFinanceNewsProvider(lids=lids or None)
    return SinaFinanceNewsProvider()


def _news_config() -> dict[str, Any]:
    config_path = Path("configs/sources.yaml")
    try:
        import yaml
    except ImportError:
        return {}
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    return (config.get("data_sources") or {}).get("news") or {}


def _to_json(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _to_json(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [_to_json(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_json(item) for key, item in value.items()}
    return value


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


app = create_app() if FastAPI is not None else None
