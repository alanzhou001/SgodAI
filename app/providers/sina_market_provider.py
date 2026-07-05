from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any

from app.models import Asset
from app.providers.akshare_provider import normalize_market_ticker
from app.providers.base import MarketDataProvider


class SinaMarketDataError(RuntimeError):
    pass


class SinaAShareMarketDataProvider(MarketDataProvider):
    provider_id = "sina_a_share_market_data"

    def __init__(
        self,
        *,
        endpoint: str = "https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20data=/CN_MarketDataService.getKLineData",
        timeout_seconds: int = 12,
        datalen: int = 1023,
    ) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.datalen = datalen

    def healthcheck(self) -> bool:
        return True

    def fetch_quotes(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for asset in assets:
            latest = self.fetch_latest_quote(asset.ticker)
            rows.append(latest)
        return rows

    def fetch_latest_quote(self, ticker: str) -> dict[str, Any]:
        rows = self.fetch_ohlcv(ticker, since=datetime.now() - timedelta(days=30))
        if not rows:
            raise SinaMarketDataError(f"Sina returned no quote rows for {ticker}")
        latest = rows[-1]
        previous = rows[-2] if len(rows) > 1 else None
        change = None
        change_pct = None
        if previous and previous["close"]:
            change = latest["close"] - previous["close"]
            change_pct = change / previous["close"] * 100
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
            "amount": latest["amount"],
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
            raise SinaMarketDataError("Sina fallback currently supports daily OHLCV only.")
        market, symbol = normalize_market_ticker(ticker)
        if market != "A-share":
            raise SinaMarketDataError(f"Sina fallback supports A-share only: {ticker}")
        sina_symbol = self._sina_symbol(ticker, symbol)
        params = urllib.parse.urlencode(
            {
                "symbol": sina_symbol,
                "scale": 240,
                "ma": "no",
                "datalen": self.datalen,
            }
        )
        request = urllib.request.Request(
            f"{self.endpoint}?{params}",
            headers={
                "Accept": "application/javascript, application/json, */*",
                "Referer": "https://finance.sina.com.cn/",
                "User-Agent": "SgodAI-Market-Radar/0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            raise SinaMarketDataError(f"Sina A-share OHLCV request failed for {ticker}: {exc}") from exc
        return self.parse_payload(ticker, payload, since=since, until=until)

    def parse_payload(
        self,
        ticker: str,
        payload: str,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        records = self._extract_records(payload)
        rows = [self._row_to_ohlcv(ticker, row) for row in records if isinstance(row, dict)]
        rows.sort(key=lambda row: row["trade_date"])
        return [
            row
            for row in rows
            if self._in_range(row["trade_date"], since=since, until=until)
        ]

    @staticmethod
    def _extract_records(payload: str) -> list[dict[str, Any]]:
        match = re.search(
            r"var\s+data\s*=\s*\(?(?P<json>\[.*\]|\{.*\})\)?\s*;",
            payload,
            re.DOTALL,
        )
        if not match:
            raise SinaMarketDataError("Sina response did not contain JSONP data.")
        data = json.loads(match.group("json"))
        if isinstance(data, dict) and data.get("__ERROR"):
            raise SinaMarketDataError(str(data.get("__ERRORMSG") or data.get("__ERROR")))
        if not isinstance(data, list):
            raise SinaMarketDataError("Sina response did not contain an OHLCV list.")
        return data

    @staticmethod
    def _row_to_ohlcv(ticker: str, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "ticker": ticker,
            "trade_date": str(row.get("day") or row.get("date") or ""),
            "open": float(row.get("open") or 0),
            "high": float(row.get("high") or 0),
            "low": float(row.get("low") or 0),
            "close": float(row.get("close") or 0),
            "volume": float(row.get("volume") or 0),
            "amount": float(row.get("amount") or 0),
            "source": "sina",
        }

    @staticmethod
    def _sina_symbol(ticker: str, symbol: str) -> str:
        upper = ticker.upper()
        if upper.endswith(".SH"):
            return f"sh{symbol}"
        if upper.endswith(".SZ"):
            return f"sz{symbol}"
        if upper.endswith(".BJ"):
            return f"bj{symbol}"
        raise SinaMarketDataError(f"Unsupported A-share exchange for Sina: {ticker}")

    @staticmethod
    def _in_range(
        trade_date: str,
        *,
        since: datetime | None,
        until: datetime | None,
    ) -> bool:
        if not trade_date:
            return False
        value = datetime.fromisoformat(trade_date)
        if since and value.date() < since.date():
            return False
        if until and value.date() > until.date():
            return False
        return True
