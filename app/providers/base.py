from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from app.models import Asset, Event, Sector


class DataProvider(ABC):
    provider_id: str

    @abstractmethod
    def healthcheck(self) -> bool:
        raise NotImplementedError


class MarketDataProvider(DataProvider):
    @abstractmethod
    def fetch_quotes(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class AssetSearchProvider(DataProvider):
    @abstractmethod
    def search_assets(
        self,
        query: str,
        *,
        limit: int = 20,
        markets: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class AnnouncementProvider(DataProvider):
    @abstractmethod
    def fetch_announcements(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        raise NotImplementedError


class NewsProvider(DataProvider):
    @abstractmethod
    def fetch_news(
        self,
        query: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        raise NotImplementedError


class FinancialReportProvider(DataProvider):
    @abstractmethod
    def fetch_reports(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        raise NotImplementedError


class PolicyProvider(DataProvider):
    @abstractmethod
    def fetch_policy_events(
        self,
        keywords: list[str],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        raise NotImplementedError


class IndustryDataProvider(DataProvider):
    @abstractmethod
    def fetch_indicators(
        self,
        sectors: list[Sector],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class CommodityPriceProvider(DataProvider):
    @abstractmethod
    def fetch_prices(
        self,
        symbols: list[str],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class OverseasMarketProvider(DataProvider):
    @abstractmethod
    def fetch_mapping_events(
        self,
        assets: list[Asset],
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        raise NotImplementedError


class SentimentProvider(DataProvider):
    @abstractmethod
    def fetch_sentiment(
        self,
        scope: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class ResearchReportProvider(DataProvider):
    @abstractmethod
    def fetch_research_reports(
        self,
        scope: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[Event]:
        raise NotImplementedError


class CalendarProvider(DataProvider):
    @abstractmethod
    def fetch_calendar(
        self,
        scope: str,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError
