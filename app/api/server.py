from __future__ import annotations

import os
from datetime import datetime
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
except ImportError:  # pragma: no cover - exercised only before optional deps are installed
    FastAPI = None  # type: ignore
    HTTPException = RuntimeError  # type: ignore

from app.llm.openai_compatible import OpenAICompatibleLLMProvider
from app.models import Asset, Event
from app.providers.akshare_provider import AkShareMarketDataProvider


def create_app() -> Any:
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Run `pip install -e .[realdata]`.")

    app = FastAPI(title="SgodAI Market Radar API", version="0.1.0")

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "market_data": "akshare",
            "llm": "deepseek",
            "disclaimer": "不构成投资建议，不提供自动交易或确定性买卖指令。",
        }

    @app.get("/api/assets/{ticker}/ohlcv")
    def asset_ohlcv(ticker: str, start: str | None = None, end: str | None = None) -> dict[str, Any]:
        provider = AkShareMarketDataProvider()
        try:
            rows = provider.fetch_ohlcv(
                ticker,
                since=datetime.fromisoformat(start) if start else None,
                until=datetime.fromisoformat(end) if end else None,
            )
        except Exception as exc:  # noqa: BLE001 - API should surface adapter failure clearly.
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return {"ticker": ticker, "rows": rows, "source": provider.provider_id}

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

    return app


def _deepseek_provider() -> OpenAICompatibleLLMProvider:
    return OpenAICompatibleLLMProvider(
        provider_id="deepseek",
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key_env="DEEPSEEK_API_KEY",
    )


app = create_app() if FastAPI is not None else None
