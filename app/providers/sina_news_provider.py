from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from app.models import Event
from app.providers.base import NewsProvider


SINA_FINANCE_LIDS: dict[str, str] = {
    "2519": "财经",
    "2671": "股市",
    "2672": "美股",
    "2673": "中国概念股",
    "2674": "港股",
    "2675": "研究报告",
    "2676": "全球市场",
    "2487": "外汇",
}


class SinaFinanceNewsProvider(NewsProvider):
    provider_id = "sina_finance_rollnews"

    def __init__(
        self,
        *,
        lids: list[str] | None = None,
        limit_per_lid: int = 30,
        timeout_seconds: int = 20,
    ) -> None:
        self.lids = lids or ["2671", "2674", "2675", "2676"]
        self.limit_per_lid = limit_per_lid
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> bool:
        return bool(self.lids)

    def fetch_news(
        self,
        query: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        for lid in self.lids:
            payload = self._fetch_lid(lid)
            events.extend(
                self.parse_payload(
                    payload,
                    lid=lid,
                    query=query,
                    since=since,
                    until=until,
                )
            )
        return self._deduplicate(events)

    def parse_payload(
        self,
        payload: dict[str, Any],
        *,
        lid: str,
        query: str = "",
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        rows = (((payload.get("result") or {}).get("data")) or [])
        events: list[Event] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title") or "").strip()
            summary = str(row.get("intro") or "").strip() or None
            haystack = f"{title} {summary or ''}".lower()
            if query and query.lower() not in haystack:
                continue
            published_at = self._published_at(row.get("intime"))
            if since and published_at and published_at < self._aware(since):
                continue
            if until and published_at and published_at > self._aware(until):
                continue
            events.append(
                self._row_to_event(
                    row,
                    lid=lid,
                    title=title,
                    summary=summary,
                    published_at=published_at,
                )
            )
        return events

    def _fetch_lid(self, lid: str) -> dict[str, Any]:
        params = urllib.parse.urlencode(
            {
                "pageid": "384",
                "lid": lid,
                "k": "",
                "num": self.limit_per_lid,
                "page": 1,
                "r": f"{time.time():.6f}",
                "_": int(time.time() * 1000),
            }
        )
        request = urllib.request.Request(
            f"https://feed.mix.sina.com.cn/api/roll/get?{params}",
            headers={
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://finance.sina.com.cn/roll/",
                "User-Agent": "SgodAI-Market-Radar/0.1",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def _row_to_event(
        self,
        row: dict[str, Any],
        *,
        lid: str,
        title: str,
        summary: str | None,
        published_at: datetime | None,
    ) -> Event:
        source_url = str(row.get("url") or "").replace("http://", "https://") or None
        digest = hashlib.sha1(f"sina:{lid}:{title}:{source_url}".encode("utf-8")).hexdigest()[:12]
        return Event(
            id=f"evt_{digest}",
            title=title,
            event_type="news",
            source=self.provider_id,
            source_url=source_url,
            source_published_at=published_at,
            summary=summary,
            evidence={
                "provider": self.provider_id,
                "lid": lid,
                "category": SINA_FINANCE_LIDS.get(lid, lid),
                "media_name": row.get("media_name"),
                "raw": row,
            },
            dedup_key=f"sina:{source_url or title}",
            confidence=0.72,
        )

    @staticmethod
    def _published_at(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        try:
            return datetime.fromtimestamp(float(value), timezone.utc)
        except (TypeError, ValueError, OSError):
            return None

    @staticmethod
    def _aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

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
