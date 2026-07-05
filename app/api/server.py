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

from app import __version__
from app.db import SQLiteSignalStore
from app.llm.openai_compatible import OpenAICompatibleLLMProvider
from app.models import Asset, EmailTarget, Event, PositionState, PositionWindowState, Report, Signal
from app.notifications import EmailNotificationProvider
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
from app.reports import ReportComposer
from app.services import AssetIntelligenceService, ConfigAssistService

if load_dotenv is not None:
    env_file = os.getenv("SGODAI_ENV_FILE")
    load_dotenv(env_file) if env_file else load_dotenv()


def create_app() -> Any:
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Run `pip install -e .[realdata]`.")

    app = FastAPI(title="SgodAI Market Radar API", version=__version__)
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

    @app.get("/api/config")
    def get_config() -> dict[str, Any]:
        store = SQLiteSignalStore()
        saved = store.get_app_config()
        return {
            "configured": saved is not None,
            "config": saved["payload"] if saved else None,
            "updated_at": saved["updated_at"] if saved else None,
            "storage": {
                "backend": "sqlite",
                "path": str(store.path),
                "local_first": True,
            },
        }

    @app.post("/api/config")
    def save_config(payload: dict[str, Any]) -> dict[str, Any]:
        store = SQLiteSignalStore()
        saved = store.save_app_config(payload)
        return {
            "success": True,
            "updated_at": saved["updated_at"],
            "storage": {
                "backend": "sqlite",
                "path": str(store.path),
                "local_first": True,
            },
        }

    @app.get("/api/system/health-check")
    def system_health_check() -> dict[str, Any]:
        store = SQLiteSignalStore()
        email_status = _email_config_summary()
        llm_status = _llm_config_summary()
        registry = provider_registry()
        return {
            "status": "ok",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "components": {
                "api": {"status": "ok", "version": __version__},
                "database": {
                    "status": "ok",
                    "path": str(store.path),
                    "counts": store.counts(),
                    "config_persisted": store.get_app_config() is not None,
                },
                "llm": llm_status,
                "email": email_status,
                "providers": {
                    "status": "ok",
                    "market_data": _provider_summary(registry.get("market_data", [])),
                    "information": _provider_summary(registry.get("information", [])),
                },
            },
            "actions": {
                "manual_daily_report": "/api/reports/daily",
                "manual_weekly_report": "/api/reports/weekly",
                "test_email": "/api/notifications/email/test",
                "provider_registry": "/api/providers/registry",
            },
            "disclaimer": "不构成投资建议，不提供自动交易或确定性买卖指令。",
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
            "tables": ["events", "signals", "position_window_states", "reports", "delivery_logs", "app_config"],
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

    @app.post("/api/reports/daily")
    def generate_daily_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return _generate_report("daily", payload or {}, default_days=1)

    @app.post("/api/reports/weekly")
    def generate_weekly_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return _generate_report("weekly", payload or {}, default_days=7)

    @app.get("/api/reports/recent")
    def recent_reports(limit: int = 20) -> dict[str, Any]:
        store = SQLiteSignalStore()
        return {
            "reports": store.recent_reports(limit),
            "path": str(store.path),
        }

    @app.get("/api/notifications/email/config")
    def email_config_status() -> dict[str, Any]:
        return _email_config_summary()

    @app.post("/api/notifications/email/test")
    def send_test_email(payload: dict[str, Any]) -> dict[str, Any]:
        target = _email_target_from_payload(payload)
        provider = EmailNotificationProvider()
        store = SQLiteSignalStore()
        log = store.save_delivery_log(provider.send_test(target))
        return {
            "target": _to_json(target),
            "delivery_log": _to_json(log),
            "success": log.status == "success",
        }

    @app.get("/api/notifications/delivery-logs")
    def delivery_logs(limit: int = 50) -> dict[str, Any]:
        store = SQLiteSignalStore()
        return {
            "logs": store.recent_delivery_logs(limit),
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


def _compose_report_from_store(
    store: SQLiteSignalStore,
    *,
    period_start: datetime,
    period_end: datetime,
) -> Report:
    events = [_event_from_row(row) for row in store.recent_events(200)]
    signals = [_signal_from_row(row) for row in store.recent_signals(200)]
    states = [_position_state_from_row(row) for row in store.recent_position_states(200)]
    return ReportComposer().compose_daily_report(
        events=events,
        signals=signals,
        position_states=states,
        period_start=period_start,
        period_end=period_end,
    )


def _generate_report(report_type: str, payload: dict[str, Any], *, default_days: int) -> dict[str, Any]:
    store = SQLiteSignalStore()
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=int(payload.get("days") or default_days))
    report = _compose_report_from_store(store, period_start=period_start, period_end=now)
    if report_type == "weekly":
        report.report_type = "weekly"
        report.title = "SgodAI Market Radar Weekly"
        report.id = report.id.replace("rpt_", "rpt_weekly_", 1)
    store.save_report(report)
    delivery_logs = []
    if payload.get("send_email"):
        provider = EmailNotificationProvider()
        for target_payload in payload.get("email_targets") or []:
            target = _email_target_from_payload(target_payload)
            if not target.enabled:
                continue
            delivery_logs.append(store.save_delivery_log(provider.send_report(target, report)))
    return {
        "success": True,
        "report": _to_json(report),
        "delivery_logs": [_to_json(log) for log in delivery_logs],
        "storage": {"backend": "sqlite", "path": str(store.path)},
    }


def _event_from_row(row: dict[str, Any]) -> Event:
    return Event(
        id=str(row["id"]),
        title=str(row["title"]),
        event_type=str(row["event_type"]),
        source=str(row["source"]),
        source_url=row.get("source_url"),
        source_published_at=_parse_optional_datetime(row.get("source_published_at")),
        received_at=_parse_optional_datetime(row.get("received_at")) or datetime.now(timezone.utc),
        raw_content_ref=row.get("raw_content_ref"),
        summary=row.get("summary"),
        asset_ids=[str(item) for item in row.get("asset_ids") or []],
        sector_ids=[str(item) for item in row.get("sector_ids") or []],
        knowledge_node_ids=[str(item) for item in row.get("knowledge_node_ids") or []],
        evidence=dict(row.get("evidence") or {}),
        dedup_key=row.get("dedup_key"),
        confidence=float(row.get("confidence") or 0),
        created_at=_parse_optional_datetime(row.get("created_at")) or datetime.now(timezone.utc),
    )


def _signal_from_row(row: dict[str, Any]) -> Signal:
    return Signal(
        id=str(row["id"]),
        event_id=str(row["event_id"]),
        asset_id=row.get("asset_id"),
        sector_id=row.get("sector_id"),
        impact_score=int(row.get("impact_score") or 0),
        trend_score=int(row.get("trend_score") or 0),
        sentiment_score=int(row.get("sentiment_score") or 0),
        risk_score=int(row.get("risk_score") or 0),
        scoring_version=str(row.get("scoring_version") or "rules.v0"),
        evidence=dict(row.get("evidence") or {}),
        created_at=_parse_optional_datetime(row.get("created_at")) or datetime.now(timezone.utc),
    )


def _position_state_from_row(row: dict[str, Any]) -> PositionWindowState:
    return PositionWindowState(
        id=str(row["id"]),
        asset_id=str(row["asset_id"]),
        previous_state=PositionState(str(row.get("previous_state") or PositionState.WATCH.value)),
        current_state=PositionState(str(row.get("current_state") or PositionState.WATCH.value)),
        support_factors=[str(item) for item in row.get("support_factors") or []],
        risk_factors=[str(item) for item in row.get("risk_factors") or []],
        watch_variables=[str(item) for item in row.get("watch_variables") or []],
        triggered_by_event_ids=[str(item) for item in row.get("triggered_by_event_ids") or []],
        triggered_by_signal_ids=[str(item) for item in row.get("triggered_by_signal_ids") or []],
        rule_version=str(row.get("rule_version") or "position.rules.v0"),
        confidence=float(row.get("confidence") or 0),
        disclaimer=str(row.get("disclaimer") or "不构成投资建议。"),
        created_at=_parse_optional_datetime(row.get("created_at")) or datetime.now(timezone.utc),
    )


def _email_config_summary() -> dict[str, Any]:
    provider = EmailNotificationProvider()
    missing = [
        key
        for key, value in {
            "SMTP_HOST": provider.host,
            "SMTP_USERNAME": provider.username,
            "SMTP_PASSWORD": provider.password,
            "SMTP_FROM": provider.sender,
        }.items()
        if not value
    ]
    return {
        "provider": provider.provider_id,
        "status": "ok" if not missing else "needs_config",
        "host": provider.host,
        "port": provider.port,
        "use_ssl": provider.use_ssl,
        "from": provider.sender,
        "configured": not missing,
        "missing": missing,
    }


def _llm_config_summary() -> dict[str, Any]:
    provider = _deepseek_provider()
    configured = bool(os.getenv(provider.api_key_env or ""))
    return {
        "provider": provider.provider_id,
        "status": "ok" if configured else "needs_config",
        "base_url": provider.base_url,
        "model": provider.model,
        "api_key_env": provider.api_key_env,
        "configured": configured,
    }


def _provider_summary(providers: list[dict[str, Any]]) -> dict[str, Any]:
    active = [item for item in providers if str(item.get("status", "")).startswith("active")]
    reserved = [item for item in providers if item.get("status") == "reserved"]
    return {
        "total": len(providers),
        "active": len(active),
        "reserved": len(reserved),
        "items": providers,
    }


def _market_provider_chain() -> list[Any]:
    return [
        AkShareMarketDataProvider(),
        SinaAShareMarketDataProvider(),
        YahooChartMarketDataProvider(),
    ]


def _public_dir() -> Path:
    configured = os.getenv("SGODAI_PUBLIC_DIR")
    if configured:
        return Path(configured)
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


def _email_target_from_payload(payload: dict[str, Any]) -> EmailTarget:
    address = str(payload.get("address") or payload.get("address_or_endpoint") or "").strip()
    name = str(payload.get("name") or "Email Target").strip()
    if not address:
        raise HTTPException(status_code=400, detail="address is required")
    return EmailTarget(
        id=str(payload.get("id") or f"email_{_slug(address)}"),
        name=name,
        address_or_endpoint=address,
        enabled=bool(payload.get("enabled", True)),
        report_types=[str(item) for item in payload.get("reportTypes") or payload.get("report_types") or []],
        sectors=[str(item) for item in payload.get("sectors") or []],
        tickers=[str(item) for item in payload.get("tickers") or []],
        frequency=str(payload.get("frequency") or "manual"),
        alert_threshold={
            "impact_score": int(payload.get("impactThreshold") or 70),
            "risk_score": int(payload.get("riskThreshold") or 60),
        },
    )


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _parse_optional_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


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
    config_path = Path(os.getenv("SGODAI_CONFIG_DIR", Path("configs"))) / "sources.yaml"
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
