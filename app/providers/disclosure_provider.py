from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models import Asset, Event
from app.providers.akshare_provider import normalize_market_ticker
from app.providers.base import AnnouncementProvider, FinancialReportProvider


class DisclosureFetchError(RuntimeError):
    pass


CNINFO_REPORT_CATEGORIES: dict[str, str] = {
    "annual": "category_ndbg_szsh",
    "semiannual": "category_bndbg_szsh",
    "q1": "category_yjdbg_szsh",
    "q3": "category_sjdbg_szsh",
}


class CninfoDisclosureProvider(AnnouncementProvider, FinancialReportProvider):
    provider_id = "cninfo_disclosure"

    def __init__(
        self,
        *,
        endpoint: str = "https://www.cninfo.com.cn/new/hisAnnouncement/query",
        static_base_url: str = "https://static.cninfo.com.cn/",
        page_size: int = 30,
        timeout_seconds: int = 20,
    ) -> None:
        self.endpoint = endpoint
        self.static_base_url = static_base_url
        self.page_size = page_size
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> bool:
        return True

    def fetch_announcements(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        for asset in assets:
            if not self._supports(asset):
                continue
            events.extend(
                self._query_asset(
                    asset,
                    since=since,
                    until=until,
                    event_type="announcement",
                )
            )
        return events

    def fetch_reports(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        for asset in assets:
            if not self._supports(asset):
                continue
            for report_kind, category in CNINFO_REPORT_CATEGORIES.items():
                events.extend(
                    self._query_asset(
                        asset,
                        since=since,
                        until=until,
                        event_type="financial_report",
                        category=category,
                        report_kind=report_kind,
                    )
                )
        return self._deduplicate(events)

    def parse_payload(
        self,
        asset: Asset,
        payload: dict[str, Any],
        *,
        event_type: str,
        category: str | None = None,
        report_kind: str | None = None,
    ) -> list[Event]:
        records = payload.get("announcements") or []
        if not isinstance(records, list):
            return []
        return [
            self._record_to_event(
                asset,
                record,
                event_type=event_type,
                category=category,
                report_kind=report_kind,
            )
            for record in records
            if isinstance(record, dict)
        ]

    def _query_asset(
        self,
        asset: Asset,
        *,
        since: datetime | None,
        until: datetime | None,
        event_type: str,
        category: str | None = None,
        report_kind: str | None = None,
    ) -> list[Event]:
        market, symbol = normalize_market_ticker(asset.ticker)
        if market != "A-share":
            return []
        body = urllib.parse.urlencode(
            {
                "pageNum": 1,
                "pageSize": self.page_size,
                "column": "sse" if asset.ticker.upper().endswith(".SH") else "szse",
                "tabName": "fulltext",
                "plate": "",
                "stock": "",
                "searchkey": symbol,
                "secid": "",
                "category": category or "",
                "trade": "",
                "seDate": self._date_range(since, until),
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://www.cninfo.com.cn",
                "Referer": (
                    "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch"
                    "?url=disclosure/list/search"
                ),
                "User-Agent": "SgodAI-Market-Radar/0.1",
                "X-Requested-With": "XMLHttpRequest",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - provider errors should be surfaced clearly.
            raise DisclosureFetchError(
                f"CNINFO disclosure request failed for {asset.ticker}: {exc}"
            ) from exc
        return self.parse_payload(
            asset,
            payload,
            event_type=event_type,
            category=category,
            report_kind=report_kind,
        )

    def _record_to_event(
        self,
        asset: Asset,
        record: dict[str, Any],
        *,
        event_type: str,
        category: str | None,
        report_kind: str | None,
    ) -> Event:
        raw_title = str(record.get("announcementTitle") or record.get("title") or "")
        title = self._strip_html(raw_title) or f"{asset.name} 公告"
        announcement_id = str(record.get("announcementId") or "")
        source_url = self._source_url(str(record.get("adjunctUrl") or ""))
        published_at = self._published_at(record.get("announcementTime"))
        digest = hashlib.sha1(
            f"cninfo:{asset.ticker}:{announcement_id}:{title}:{source_url}".encode("utf-8")
        ).hexdigest()[:12]
        return Event(
            id=f"evt_{digest}",
            title=title,
            event_type=event_type,
            source=self.provider_id,
            source_url=source_url,
            source_published_at=published_at,
            summary=None,
            asset_ids=[asset.id],
            sector_ids=[asset.sector_id] if asset.sector_id else [],
            evidence={
                "provider": self.provider_id,
                "market": "A-share",
                "ticker": asset.ticker,
                "sec_code": record.get("secCode"),
                "sec_name": record.get("secName"),
                "announcement_id": announcement_id,
                "category": category,
                "report_kind": report_kind,
                "raw": record,
            },
            dedup_key=f"cninfo:{announcement_id or source_url or title}",
            confidence=0.86,
        )

    def _source_url(self, adjunct_url: str) -> str | None:
        if not adjunct_url:
            return None
        return urllib.parse.urljoin(self.static_base_url, adjunct_url)

    @staticmethod
    def _supports(asset: Asset) -> bool:
        market, _ = normalize_market_ticker(asset.ticker)
        return market == "A-share"

    @staticmethod
    def _date_range(since: datetime | None, until: datetime | None) -> str:
        if not since and not until:
            return ""
        end = until or datetime.now()
        start = since or (end - timedelta(days=30))
        return f"{start:%Y-%m-%d}~{end:%Y-%m-%d}"

    @staticmethod
    def _published_at(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        try:
            timestamp = float(value) / 1000
            return datetime.fromtimestamp(timestamp, timezone.utc)
        except (TypeError, ValueError, OSError):
            return None

    @staticmethod
    def _strip_html(value: str) -> str:
        text = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text).replace("&nbsp;", " ")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _deduplicate(events: list[Event]) -> list[Event]:
        seen: set[str] = set()
        unique: list[Event] = []
        for event in events:
            key = event.dedup_key or event.id
            if key in seen:
                continue
            seen.add(key)
            unique.append(event)
        return unique


class HKEXNewsDisclosureProvider(AnnouncementProvider, FinancialReportProvider):
    provider_id = "hkexnews_disclosure"

    report_keywords = (
        "annual report",
        "interim report",
        "quarterly report",
        "environmental, social and governance report",
        "financial statements",
        "年度报告",
        "中期报告",
        "季度报告",
        "财务报表",
        "環境、社會及管治報告",
    )

    def __init__(
        self,
        *,
        endpoint: str = "https://www1.hkexnews.hk/search/titleSearchServlet.do",
        stock_prefix_endpoint: str = "https://www1.hkexnews.hk/search/prefix.do",
        timeout_seconds: int = 20,
    ) -> None:
        self.endpoint = endpoint
        self.stock_prefix_endpoint = stock_prefix_endpoint
        self.timeout_seconds = timeout_seconds
        self._stock_id_cache: dict[str, str] = {}

    def healthcheck(self) -> bool:
        return True

    def fetch_announcements(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        for asset in assets:
            if not self._supports(asset):
                continue
            events.extend(
                self._query_asset(
                    asset,
                    since=since,
                    until=until,
                    event_type="announcement",
                )
            )
        return events

    def fetch_reports(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        for asset in assets:
            if not self._supports(asset):
                continue
            events.extend(
                self._query_asset(
                    asset,
                    since=since,
                    until=until,
                    event_type="financial_report",
                    keywords=self.report_keywords,
                )
            )
        return events

    def parse_search_html(
        self,
        asset: Asset,
        html: str,
        *,
        event_type: str,
        keywords: tuple[str, ...] | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        link_pattern = (
            r"<a[^>]+href=[\"'](?P<href>[^\"']*listedco/listconews/[^\"']+)[\"']"
            r"[^>]*>(?P<title>.*?)</a>"
        )
        for match in re.finditer(
            link_pattern,
            html,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            href = match.group("href")
            title = self._strip_html(match.group("title"))
            if keywords and not self._matches_keywords(title, keywords):
                continue
            row_html = self._row_html(html, match.start(), match.end())
            published_at = self._published_at(row_html)
            events.append(
                self._event(
                    asset,
                    title=title,
                    href=href,
                    event_type=event_type,
                    published_at=published_at,
                    raw=row_html,
                )
            )
        return self._deduplicate(events)

    def parse_json_payload(
        self,
        asset: Asset,
        payload: dict[str, Any],
        *,
        event_type: str,
        keywords: tuple[str, ...] | None = None,
    ) -> list[Event]:
        result = payload.get("result") or []
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = []
        events: list[Event] = []
        for row in result:
            if not isinstance(row, dict):
                continue
            title = self._strip_html(
                str(row.get("LONG_TEXT") or row.get("TITLE") or row.get("SHORT_TEXT") or "")
            )
            if keywords and not self._matches_keywords(title, keywords):
                continue
            events.append(
                self._event(
                    asset,
                    title=title or f"{asset.name} HKEX announcement",
                    href=str(row.get("FILE_LINK") or ""),
                    event_type=event_type,
                    published_at=self._published_at(str(row.get("DATE_TIME") or "")),
                    raw=row,
                )
            )
        return self._deduplicate(events)

    def _query_asset(
        self,
        asset: Asset,
        *,
        since: datetime | None,
        until: datetime | None,
        event_type: str,
        keywords: tuple[str, ...] | None = None,
    ) -> list[Event]:
        _, symbol = normalize_market_ticker(asset.ticker)
        stock_id = self._lookup_stock_id(symbol)
        end = until or datetime.now()
        start = since or (end - timedelta(days=30))
        params = urllib.parse.urlencode(
            {
                "sortDir": "0",
                "sortByOptions": "DateTime",
                "category": "0",
                "market": "SEHK",
                "stockId": stock_id,
                "documentType": -1,
                "fromDate": f"{start:%Y%m%d}",
                "toDate": f"{end:%Y%m%d}",
                "title": "",
                "searchType": 1,
                "t1code": -2,
                "t2Gcode": -2,
                "t2code": -2,
                "rowRange": 100,
                "lang": "E",
            }
        )
        request = urllib.request.Request(
            f"{self.endpoint}?{params}",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=EN",
                "User-Agent": "SgodAI-Market-Radar/0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception as exc:  # noqa: BLE001
            raise DisclosureFetchError(
                f"HKEXnews request failed for {asset.ticker}: {exc}"
            ) from exc
        return self.parse_json_payload(asset, payload, event_type=event_type, keywords=keywords)

    def _lookup_stock_id(self, symbol: str) -> str:
        if symbol in self._stock_id_cache:
            return self._stock_id_cache[symbol]
        params = urllib.parse.urlencode(
            {
                "callback": "callback",
                "type": "A",
                "name": symbol,
                "market": "SEHK",
                "lang": "EN",
            }
        )
        request = urllib.request.Request(
            f"{self.stock_prefix_endpoint}?{params}",
            headers={
                "Accept": "application/javascript, application/json, */*",
                "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=EN",
                "User-Agent": "SgodAI-Market-Radar/0.1",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = self._parse_jsonp(response.read().decode("utf-8", errors="replace"))
        except Exception as exc:  # noqa: BLE001
            raise DisclosureFetchError(f"HKEX stock lookup failed for {symbol}: {exc}") from exc
        rows = payload.get("stockInfo") or []
        for row in rows:
            if str(row.get("code") or "").zfill(5) == symbol:
                stock_id = str(row.get("stockId"))
                self._stock_id_cache[symbol] = stock_id
                return stock_id
        if rows:
            stock_id = str(rows[0].get("stockId"))
            self._stock_id_cache[symbol] = stock_id
            return stock_id
        raise DisclosureFetchError(f"HKEX stock lookup returned no match for {symbol}.")

    def _event(
        self,
        asset: Asset,
        *,
        title: str,
        href: str,
        event_type: str,
        published_at: datetime | None,
        raw: Any,
    ) -> Event:
        source_url = urllib.parse.urljoin("https://www1.hkexnews.hk", href)
        digest = hashlib.sha1(
            f"hkex:{asset.ticker}:{title}:{source_url}".encode("utf-8")
        ).hexdigest()[:12]
        return Event(
            id=f"evt_{digest}",
            title=title,
            event_type=event_type,
            source=self.provider_id,
            source_url=source_url,
            source_published_at=published_at,
            asset_ids=[asset.id],
            sector_ids=[asset.sector_id] if asset.sector_id else [],
            evidence={
                "provider": self.provider_id,
                "market": "HK",
                "ticker": asset.ticker,
                "raw": self._clean_raw(raw),
            },
            dedup_key=f"hkex:{source_url}",
            confidence=0.84,
        )

    @staticmethod
    def _supports(asset: Asset) -> bool:
        market, _ = normalize_market_ticker(asset.ticker)
        return market == "HK"

    @staticmethod
    def _row_html(html: str, start: int, end: int) -> str:
        row_start = html.rfind("<tr", 0, start)
        row_end = html.find("</tr>", end)
        if row_start == -1 or row_end == -1:
            return html[start:end]
        return html[row_start : row_end + len("</tr>")]

    @staticmethod
    def _published_at(value: str) -> datetime | None:
        text = HKEXNewsDisclosureProvider._strip_html(value)
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        match = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
        if match:
            day, month, year = (int(part) for part in match.groups())
            return datetime(year, month, day, tzinfo=timezone.utc)
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
        if match:
            year, month, day = (int(part) for part in match.groups())
            return datetime(year, month, day, tzinfo=timezone.utc)
        return None

    @staticmethod
    def _parse_jsonp(value: str) -> dict[str, Any]:
        match = re.search(r"^[^(]*\((.*)\);?\s*$", value, flags=re.DOTALL)
        if not match:
            return json.loads(value)
        return json.loads(match.group(1))

    @staticmethod
    def _matches_keywords(title: str, keywords: tuple[str, ...]) -> bool:
        lower = title.lower()
        return any(keyword.lower() in lower for keyword in keywords)

    @staticmethod
    def _strip_html(value: str) -> str:
        text = value.replace("\\u003cbr/\\u003e", " ")
        text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text).replace("&nbsp;", " ")
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def _clean_raw(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls._strip_html(value)
        if isinstance(value, dict):
            return {str(key): cls._clean_raw(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._clean_raw(item) for item in value]
        return value

    @staticmethod
    def _deduplicate(events: list[Event]) -> list[Event]:
        seen: set[str] = set()
        unique: list[Event] = []
        for event in events:
            key = event.dedup_key or event.id
            if key in seen:
                continue
            seen.add(key)
            unique.append(event)
        return unique


class CombinedDisclosureProvider(AnnouncementProvider, FinancialReportProvider):
    provider_id = "combined_disclosure"

    def __init__(
        self,
        *,
        cninfo: CninfoDisclosureProvider | None = None,
        hkexnews: HKEXNewsDisclosureProvider | None = None,
    ) -> None:
        self.cninfo = cninfo or CninfoDisclosureProvider()
        self.hkexnews = hkexnews or HKEXNewsDisclosureProvider()

    def healthcheck(self) -> bool:
        return self.cninfo.healthcheck() and self.hkexnews.healthcheck()

    def fetch_announcements(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        a_share_assets, hk_assets = self._split_assets(assets)
        return self.cninfo.fetch_announcements(
            a_share_assets,
            since=since,
            until=until,
        ) + self.hkexnews.fetch_announcements(hk_assets, since=since, until=until)

    def fetch_reports(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        a_share_assets, hk_assets = self._split_assets(assets)
        return self.cninfo.fetch_reports(
            a_share_assets,
            since=since,
            until=until,
        ) + self.hkexnews.fetch_reports(hk_assets, since=since, until=until)

    @staticmethod
    def _split_assets(assets: list[Asset]) -> tuple[list[Asset], list[Asset]]:
        a_share_assets: list[Asset] = []
        hk_assets: list[Asset] = []
        for asset in assets:
            market, _ = normalize_market_ticker(asset.ticker)
            if market == "A-share":
                a_share_assets.append(asset)
            elif market == "HK":
                hk_assets.append(asset)
        return a_share_assets, hk_assets
