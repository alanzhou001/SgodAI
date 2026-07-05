from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from app.models import Asset
from app.providers.base import MarketDataProvider


class YahooChartMarketDataError(RuntimeError):
    pass


class YahooChartMarketDataProvider(MarketDataProvider):
    provider_id = "yahoo_chart_market_data"

    def __init__(
        self,
        *,
        endpoint: str = "https://query1.finance.yahoo.com/v8/finance/chart",
        timeout_seconds: int = 12,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> bool:
        return True

    def fetch_quotes(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        return [self.fetch_latest_quote(asset.ticker) for asset in assets]

    def fetch_latest_quote(self, ticker: str) -> dict[str, Any]:
        rows = self.fetch_ohlcv(ticker)
        if not rows:
            raise YahooChartMarketDataError(f"Yahoo Chart returned no rows for {ticker}")
        latest = rows[-1]
        previous = rows[-2] if len(rows) > 1 else None
        change = latest["close"] - previous["close"] if previous else None
        change_pct = change / previous["close"] * 100 if previous and previous["close"] else None
        return {
            "ticker": ticker,
            "name": "",
            "price": latest["close"],
            "change": change,
            "change_pct": change_pct,
            "open": latest["open"],
            "high": latest["high"],
            "low": latest["low"],
            "prev_close": previous["close"] if previous else None,
            "volume": latest["volume"],
            "amount": latest.get("amount"),
            "source": self.provider_id,
        }

    def fetch_ohlcv(
        self,
        ticker: str,
        since: datetime | None = None,
        until: datetime | None = None,
        period: str = "daily",
    ) -> list[dict[str, Any]]:
        if period != "daily":
            raise YahooChartMarketDataError("Yahoo Chart fallback currently supports daily OHLCV only.")
        yahoo_symbol = self.yahoo_symbol(ticker)
        params = urllib.parse.urlencode(
            {
                "period1": int((since or datetime(2020, 1, 1, tzinfo=timezone.utc)).timestamp()),
                "period2": int((until or datetime.now(timezone.utc)).timestamp()),
                "interval": "1d",
                "events": "history",
                "includeAdjustedClose": "true",
            }
        )
        request = urllib.request.Request(
            f"{self.endpoint}/{urllib.parse.quote(yahoo_symbol)}?{params}",
            headers={
                "Accept": "application/json",
                "User-Agent": "SgodAI-Market-Radar/0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception as exc:  # noqa: BLE001
            raise YahooChartMarketDataError(f"Yahoo Chart request failed for {ticker}: {exc}") from exc
        return self.parse_payload(ticker, payload)

    @staticmethod
    def yahoo_symbol(ticker: str) -> str:
        raw = ticker.strip().upper()
        if raw.endswith(".HK"):
            return f"{raw.split('.')[0].zfill(4)}.HK"
        if raw.endswith(".US"):
            return raw.removesuffix(".US")
        if raw.endswith(".SH"):
            return f"{raw.split('.')[0]}.SS"
        if raw.endswith(".SZ"):
            return f"{raw.split('.')[0]}.SZ"
        return raw

    @classmethod
    def parse_payload(cls, ticker: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        chart = payload.get("chart") or {}
        error = chart.get("error")
        if error:
            raise YahooChartMarketDataError(str(error))
        results = chart.get("result") or []
        if not results:
            raise YahooChartMarketDataError("Yahoo Chart response did not contain result data.")
        result = results[0]
        timestamps = result.get("timestamp") or []
        quote = ((result.get("indicators") or {}).get("quote") or [{}])[0]
        rows: list[dict[str, Any]] = []
        for index, timestamp in enumerate(timestamps):
            row = {
                "ticker": ticker,
                "trade_date": datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat(),
                "open": _float_at(quote.get("open"), index),
                "high": _float_at(quote.get("high"), index),
                "low": _float_at(quote.get("low"), index),
                "close": _float_at(quote.get("close"), index),
                "volume": _float_at(quote.get("volume"), index),
                "amount": 0.0,
                "source": cls.provider_id,
            }
            if all(row[key] is not None for key in ("open", "high", "low", "close")):
                rows.append(row)
        return rows


def _float_at(values: Any, index: int) -> float | None:
    try:
        value = values[index]
    except (TypeError, IndexError):
        return None
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
