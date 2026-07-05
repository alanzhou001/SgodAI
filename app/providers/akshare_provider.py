from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from app.models import Asset, Event
from app.providers.base import AnnouncementProvider, FinancialReportProvider, MarketDataProvider


class ProviderDependencyError(RuntimeError):
    pass


def normalize_market_ticker(ticker: str) -> tuple[str, str]:
    raw = ticker.strip().upper()
    if raw.endswith(".SH") or raw.endswith(".SZ") or raw.endswith(".BJ"):
        return "A-share", raw.split(".")[0]
    if raw.endswith(".HK"):
        return "HK", raw.split(".")[0].zfill(5)
    return "unknown", raw


class AkShareMarketDataProvider(MarketDataProvider):
    provider_id = "akshare_market_data"

    def __init__(self, *, adjust: str = "qfq") -> None:
        self.adjust = adjust

    def healthcheck(self) -> bool:
        return self._akshare() is not None

    def fetch_quotes(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for asset in assets:
            rows.extend(self.fetch_ohlcv(asset.ticker, since=since, until=until))
        return rows

    def fetch_ohlcv(
        self,
        ticker: str,
        since: datetime | None = None,
        until: datetime | None = None,
        period: str = "daily",
    ) -> list[dict[str, Any]]:
        ak = self._require_akshare()
        market, symbol = normalize_market_ticker(ticker)
        start_date = (since or datetime(2020, 1, 1)).strftime("%Y%m%d")
        end_date = (until or datetime.now()).strftime("%Y%m%d")

        if market == "A-share":
            frame = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=self.adjust,
            )
        elif market == "HK":
            frame = ak.stock_hk_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=self.adjust,
            )
        else:
            raise ValueError(f"Unsupported ticker market for AkShare: {ticker}")

        return [self._row_to_ohlcv(ticker, row) for row in frame.to_dict("records")]

    @staticmethod
    def _row_to_ohlcv(ticker: str, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "ticker": ticker,
            "trade_date": str(row.get("日期") or row.get("date") or ""),
            "open": float(row.get("开盘", 0) or 0),
            "high": float(row.get("最高", 0) or 0),
            "low": float(row.get("最低", 0) or 0),
            "close": float(row.get("收盘", 0) or 0),
            "volume": float(row.get("成交量", 0) or 0),
            "amount": float(row.get("成交额", 0) or 0),
            "source": "akshare",
        }

    @staticmethod
    def _akshare() -> Any | None:
        try:
            import akshare as ak  # type: ignore
        except ImportError:
            return None
        return ak

    @classmethod
    def _require_akshare(cls) -> Any:
        ak = cls._akshare()
        if ak is None:
            raise ProviderDependencyError(
                "AkShare is not installed. Run `pip install akshare pandas` in your venv."
            )
        return ak


class AkShareDisclosureProvider(AnnouncementProvider, FinancialReportProvider):
    provider_id = "akshare_disclosure"

    def healthcheck(self) -> bool:
        return AkShareMarketDataProvider._akshare() is not None

    def fetch_announcements(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        ak = AkShareMarketDataProvider._require_akshare()
        if not hasattr(ak, "stock_notice_report"):
            raise ProviderDependencyError("Current AkShare build does not expose stock_notice_report.")
        query_date = (until or datetime.now()).strftime("%Y%m%d")
        frame = ak.stock_notice_report(symbol="全部", date=query_date)
        records = frame.to_dict("records")
        return self._records_to_events(records, assets, event_type="announcement", source="akshare_notice")

    def fetch_reports(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        ak = AkShareMarketDataProvider._require_akshare()
        events: list[Event] = []
        for asset in assets:
            market, symbol = normalize_market_ticker(asset.ticker)
            if market != "A-share":
                continue
            if hasattr(ak, "stock_financial_abstract"):
                frame = ak.stock_financial_abstract(symbol=symbol)
                title = f"{asset.name} 财务摘要更新"
                events.append(
                    self._event(
                        title=title,
                        source="akshare_financial_abstract",
                        event_type="financial_report",
                        asset=asset,
                        evidence={"rows": frame.head(5).to_dict("records")},
                    )
                )
        return events

    def _records_to_events(
        self,
        records: list[dict[str, Any]],
        assets: list[Asset],
        *,
        event_type: str,
        source: str,
    ) -> list[Event]:
        events: list[Event] = []
        for record in records:
            title = str(record.get("公告标题") or record.get("title") or "")
            code = str(record.get("代码") or record.get("证券代码") or "")
            name = str(record.get("名称") or record.get("证券简称") or "")
            asset = self._match_asset(assets, code, name, title)
            if not asset:
                continue
            events.append(
                self._event(
                    title=title or f"{asset.name} 公告",
                    source=source,
                    event_type=event_type,
                    asset=asset,
                    source_url=str(record.get("公告链接") or record.get("url") or "") or None,
                    evidence=record,
                )
            )
        return events

    @staticmethod
    def _match_asset(
        assets: list[Asset],
        code: str,
        name: str,
        title: str,
    ) -> Asset | None:
        normalized_code = code.strip().zfill(6) if code.strip().isdigit() else code.strip()
        for asset in assets:
            _, symbol = normalize_market_ticker(asset.ticker)
            if normalized_code and normalized_code == symbol:
                return asset
            if asset.name and (asset.name in name or asset.name in title):
                return asset
        return None

    @staticmethod
    def _event(
        *,
        title: str,
        source: str,
        event_type: str,
        asset: Asset,
        evidence: dict[str, Any],
        source_url: str | None = None,
    ) -> Event:
        digest = hashlib.sha1(f"{source}:{asset.id}:{title}".encode("utf-8")).hexdigest()[:12]
        return Event(
            id=f"evt_{digest}",
            title=title,
            event_type=event_type,
            source=source,
            source_url=source_url,
            asset_ids=[asset.id],
            sector_ids=[asset.sector_id] if asset.sector_id else [],
            evidence=evidence,
            confidence=0.72,
        )
