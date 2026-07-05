from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any

from app.providers.akshare_provider import AkShareMarketDataProvider
from app.providers.base import AssetSearchProvider


class AssetSearchError(RuntimeError):
    pass


HKEX_QUERY_ALIASES: dict[str, tuple[str, ...]] = {
    "腾讯": ("TENCENT",),
    "騰訊": ("TENCENT",),
    "阿里": ("BABA", "ALIBABA"),
    "阿里巴巴": ("BABA", "ALIBABA"),
    "美团": ("MEITUAN",),
    "美團": ("MEITUAN",),
    "小米": ("XIAOMI",),
    "京东": ("JD",),
    "京東": ("JD",),
    "快手": ("KUAISHOU",),
    "药明": ("WUXI",),
    "藥明": ("WUXI",),
}


@dataclass(slots=True)
class AssetSearchResult:
    ticker: str
    name: str
    market: str
    exchange: str
    asset_type: str = "stock"
    source: str = "unknown"
    score: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PublicAssetSearchProvider(AssetSearchProvider):
    provider_id = "public_asset_search"

    def __init__(
        self,
        *,
        hkex_prefix_endpoint: str = "https://www1.hkexnews.hk/search/prefix.do",
        timeout_seconds: int = 12,
        enable_akshare_hk_search: bool = False,
    ) -> None:
        self.hkex_prefix_endpoint = hkex_prefix_endpoint
        self.timeout_seconds = timeout_seconds
        self.enable_akshare_hk_search = enable_akshare_hk_search
        self.last_errors: list[dict[str, str]] = []

    def healthcheck(self) -> bool:
        return True

    def search_assets(
        self,
        query: str,
        *,
        limit: int = 20,
        markets: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        q = query.strip()
        if not q:
            self.last_errors = []
            return []

        normalized_markets = self._normalize_markets(markets)
        self.last_errors = []
        results: list[AssetSearchResult] = []
        if "A-share" in normalized_markets:
            results.extend(self._safe("akshare_a_share", self._search_a_share, q, limit))
        if "HK" in normalized_markets and not self._looks_like_a_share_code(q):
            results.extend(self._safe("hkex_prefix", self._search_hkex_prefix, q, limit))
            if self.enable_akshare_hk_search:
                results.extend(self._safe("akshare_hk", self._search_hk_akshare, q, limit))

        if "A-share" in normalized_markets and self._looks_like_a_share_code(q):
            results.append(
                AssetSearchResult(
                    ticker=f"{q.zfill(6)}.{a_share_exchange(q) or 'SH'}",
                    name=q.zfill(6),
                    market="A-share",
                    exchange=a_share_exchange(q) or "unknown",
                    source="a_share_code_candidate",
                    score=0.48,
                    raw={"query": q, "note": "exact_code_fallback"},
                )
            )

        unique = self._deduplicate(results)
        unique.sort(key=lambda item: item.score, reverse=True)
        return [item.to_dict() for item in unique[: max(1, min(limit, 50))]]

    def _safe(
        self,
        source: str,
        fn: Any,
        query: str,
        limit: int,
    ) -> list[AssetSearchResult]:
        try:
            return fn(query, limit)
        except Exception as exc:  # noqa: BLE001 - provider should degrade by source.
            self.last_errors.append({"source": source, "error": str(exc)})
            return []

    def _search_a_share(self, query: str, limit: int) -> list[AssetSearchResult]:
        ak = AkShareMarketDataProvider._require_akshare()
        if not hasattr(ak, "stock_info_a_code_name"):
            raise AssetSearchError("Current AkShare build does not expose stock_info_a_code_name.")
        frame = ak.stock_info_a_code_name()
        records = frame.to_dict("records")
        results: list[AssetSearchResult] = []
        for row in records:
            code = _first(row, "code", "代码", "股票代码", "证券代码", "A股代码")
            name = _first(row, "name", "名称", "股票简称", "证券简称", "A股简称")
            result = self._a_share_row_to_result(query, code=code, name=name, raw=row)
            if result:
                results.append(result)
        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

    def _search_hk_akshare(self, query: str, limit: int) -> list[AssetSearchResult]:
        ak = AkShareMarketDataProvider._require_akshare()
        fn = None
        for name in ("stock_hk_spot_em", "stock_hk_main_board_spot_em", "stock_hk_spot"):
            if hasattr(ak, name):
                fn = getattr(ak, name)
                break
        if fn is None:
            raise AssetSearchError("Current AkShare build does not expose HK spot search data.")
        frame = fn()
        results: list[AssetSearchResult] = []
        for row in frame.to_dict("records"):
            code = _first(row, "代码", "code", "symbol", "证券代码")
            name = _first(row, "名称", "name", "中文名称", "证券简称")
            result = self._hk_row_to_result(query, code=code, name=name, raw=row, source="akshare_hk")
            if result:
                results.append(result)
        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

    def _search_hkex_prefix(self, query: str, limit: int) -> list[AssetSearchResult]:
        results: list[AssetSearchResult] = []
        for query_term in hkex_query_terms(query):
            for lang in ("EN", "ZH"):
                results.extend(self._search_hkex_prefix_once(query, query_term, lang))
        return sorted(self._deduplicate(results), key=lambda item: item.score, reverse=True)[:limit]

    def _search_hkex_prefix_once(
        self,
        original_query: str,
        query_term: str,
        lang: str,
    ) -> list[AssetSearchResult]:
        params = urllib.parse.urlencode(
            {
                "callback": "callback",
                "type": "A",
                "name": query_term,
                "market": "SEHK",
                "lang": lang,
            }
        )
        request = urllib.request.Request(
            f"{self.hkex_prefix_endpoint}?{params}",
            headers={
                "Accept": "application/javascript, application/json, */*",
                "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=EN",
                "User-Agent": "SgodAI-Market-Radar/0.1",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = self._parse_jsonp(response.read().decode("utf-8", errors="replace"))
        results: list[AssetSearchResult] = []
        for row in payload.get("stockInfo") or []:
            code = _first(row, "code", "stockCode", "ticker")
            name = _first(row, "name", "stockName", "shortName")
            result = self._hk_row_to_result(
                original_query if query_term == original_query else query_term,
                code=code,
                name=name,
                raw=row,
                source="hkex_prefix",
            )
            if result:
                results.append(result)
        return results

    @staticmethod
    def _a_share_row_to_result(
        query: str,
        *,
        code: Any,
        name: Any,
        raw: dict[str, Any],
    ) -> AssetSearchResult | None:
        symbol = re.sub(r"\D", "", str(code or ""))
        if len(symbol) != 6:
            return None
        exchange = a_share_exchange(symbol)
        if not exchange:
            return None
        display_name = str(name or symbol).strip()
        score = match_score(query, symbol, display_name)
        if score <= 0:
            return None
        return AssetSearchResult(
            ticker=f"{symbol}.{exchange}",
            name=display_name,
            market="A-share",
            exchange=exchange,
            source="akshare_a_share",
            score=score,
            raw=raw,
        )

    @staticmethod
    def _hk_row_to_result(
        query: str,
        *,
        code: Any,
        name: Any,
        raw: dict[str, Any],
        source: str,
    ) -> AssetSearchResult | None:
        symbol = re.sub(r"\D", "", str(code or ""))
        if not symbol:
            return None
        display_name = str(name or symbol).strip()
        score = match_score(query, symbol, display_name)
        if score <= 0:
            return None
        return AssetSearchResult(
            ticker=f"{int(symbol)}.HK",
            name=display_name,
            market="HK",
            exchange="HK",
            source=source,
            score=score,
            raw=raw,
        )

    @staticmethod
    def _normalize_markets(markets: list[str] | None) -> set[str]:
        if not markets:
            return {"A-share", "HK"}
        normalized: set[str] = set()
        for market in markets:
            value = market.strip().lower()
            if value in {"a", "a-share", "ashare", "cn", "china", "沪深", "a股"}:
                normalized.add("A-share")
            if value in {"hk", "h-share", "hongkong", "港股"}:
                normalized.add("HK")
        return normalized or {"A-share", "HK"}

    @staticmethod
    def _looks_like_a_share_code(query: str) -> bool:
        return bool(re.fullmatch(r"\d{6}", query.strip()))

    @staticmethod
    def _parse_jsonp(value: str) -> dict[str, Any]:
        match = re.search(r"^[^(]*\((.*)\);?\s*$", value, flags=re.DOTALL)
        if not match:
            return json.loads(value)
        return json.loads(match.group(1))

    @staticmethod
    def _deduplicate(items: list[AssetSearchResult]) -> list[AssetSearchResult]:
        by_ticker: dict[str, AssetSearchResult] = {}
        for item in items:
            existing = by_ticker.get(item.ticker)
            if existing is None or item.score > existing.score:
                by_ticker[item.ticker] = item
        return list(by_ticker.values())


def _first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return ""


def hkex_query_terms(query: str) -> list[str]:
    terms = [query.strip()]
    normalized = query.strip().lower()
    for alias, expansions in HKEX_QUERY_ALIASES.items():
        alias_normalized = alias.lower()
        if normalized and (normalized in alias_normalized or alias_normalized in normalized):
            terms.extend(expansions)
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        if not term or term in seen:
            continue
        seen.add(term)
        unique.append(term)
    return unique


def a_share_exchange(code: str) -> str | None:
    symbol = re.sub(r"\D", "", str(code or "")).zfill(6)
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return "SH"
    if symbol.startswith(("000", "001", "002", "003", "200", "300", "301")):
        return "SZ"
    if symbol.startswith(("430", "830", "831", "832", "833", "834", "835", "836", "837", "838", "839", "870", "871", "872", "873", "920")):
        return "BJ"
    if symbol.startswith(("4", "8")):
        return "BJ"
    return None


def match_score(query: str, code: str, name: str) -> float:
    q = query.strip().lower()
    if not q:
        return 0.0
    normalized_code = re.sub(r"\D", "", str(code or ""))
    normalized_name = str(name or "").strip().lower()
    if q == normalized_code or q == normalized_code.lstrip("0"):
        return 1.0
    if normalized_code.startswith(q) or normalized_code.lstrip("0").startswith(q):
        return 0.86
    if q == normalized_name:
        return 0.94
    if normalized_name.startswith(q):
        return 0.82
    if q in normalized_name:
        return 0.72
    if normalized_name and normalized_name in q:
        return 0.65
    return 0.0
