from __future__ import annotations

import hashlib
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from app.models import Event
from app.providers.base import NewsProvider


@dataclass(frozen=True, slots=True)
class RSSSource:
    name: str
    url: str
    weight: float = 1.0


class RSSNewsProvider(NewsProvider):
    provider_id = "rss_news"

    def __init__(self, sources: list[RSSSource], *, timeout_seconds: int = 20) -> None:
        self.sources = sources
        self.timeout_seconds = timeout_seconds
        self.last_errors: list[dict[str, str]] = []

    def healthcheck(self) -> bool:
        return bool(self.sources)

    def fetch_news(
        self,
        query: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        events: list[Event] = []
        self.last_errors = []
        for source in self.sources:
            request = urllib.request.Request(
                source.url,
                headers={
                    "Accept": (
                        "application/rss+xml, application/atom+xml, "
                        "application/xml, text/xml, */*"
                    ),
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                        "Version/17.0 Safari/605.1.15 SgodAI-Market-Radar/0.1"
                    ),
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                    payload = response.read()
                events.extend(
                    self.parse_feed(
                        source,
                        payload,
                        query=query,
                        since=since,
                        until=until,
                    )
                )
            except Exception as exc:  # noqa: BLE001 - RSS should degrade per source.
                self.last_errors.append(
                    {"source": source.name, "url": source.url, "error": str(exc)}
                )
        return events

    def parse_feed(
        self,
        source: RSSSource,
        payload: bytes | str,
        *,
        query: str = "",
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        root = ET.fromstring(payload)
        items = root.findall(".//item")
        if not items:
            items = root.findall("{http://www.w3.org/2005/Atom}entry")
        events: list[Event] = []
        for item in items:
            title = self._text(item, "title")
            link = self._text(item, "link") or self._link_href(item)
            summary = self._text(item, "description") or self._text(item, "summary")
            published = self._published_at(item)
            if query and query.lower() not in f"{title} {summary}".lower():
                continue
            if since and published and published < self._aware(since):
                continue
            if until and published and published > self._aware(until):
                continue
            digest = hashlib.sha1(f"{source.name}:{title}:{link}".encode("utf-8")).hexdigest()[:12]
            events.append(
                Event(
                    id=f"evt_{digest}",
                    title=title,
                    event_type="news",
                    source=source.name,
                    source_url=link or None,
                    source_published_at=published,
                    summary=summary or None,
                    evidence={"source_weight": source.weight, "rss_url": source.url},
                    confidence=min(0.95, 0.55 + source.weight * 0.35),
                )
            )
        return events

    @staticmethod
    def _text(item: ET.Element, tag: str) -> str:
        found = item.find(tag)
        if found is None:
            found = item.find(f"{{http://www.w3.org/2005/Atom}}{tag}")
        return "".join(found.itertext()).strip() if found is not None else ""

    @staticmethod
    def _link_href(item: ET.Element) -> str:
        found = item.find("link")
        if found is None:
            found = item.find("{http://www.w3.org/2005/Atom}link")
        if found is None:
            return ""
        return found.attrib.get("href", "")

    @classmethod
    def _published_at(cls, item: ET.Element) -> datetime | None:
        raw = (
            cls._text(item, "pubDate")
            or cls._text(item, "published")
            or cls._text(item, "updated")
            or cls._text(item, "dc:date")
        )
        if not raw:
            return None
        try:
            return cls._aware(parsedate_to_datetime(raw))
        except (TypeError, ValueError):
            try:
                return cls._aware(datetime.fromisoformat(raw.replace("Z", "+00:00")))
            except ValueError:
                return None

    @staticmethod
    def _aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
