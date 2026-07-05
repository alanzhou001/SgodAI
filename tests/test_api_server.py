from unittest import TestCase

from app.api import server
from app.providers import provider_registry


class ApiServerTest(TestCase):
    def test_public_directory_is_available(self) -> None:
        self.assertTrue((server._public_dir() / "index.html").exists())

    def test_public_mount_keeps_api_routes_available(self) -> None:
        if server.FastAPI is None:
            self.skipTest("FastAPI is not installed")

        app = server.create_app()
        paths = [getattr(route, "path", None) for route in app.routes]

        self.assertIn("/api/health", paths)
        self.assertIn("/api/assets/search", paths)
        self.assertIn("/api/assets/{ticker}/quote", paths)
        self.assertIn("/api/assets/{ticker}/intelligence", paths)
        self.assertIn("/api/providers/registry", paths)
        self.assertIn("/api/db/status", paths)
        self.assertIn("/api/db/recent", paths)
        self.assertIn("/api/llm/config-assist", paths)
        self.assertIn("", paths)

    def test_provider_registry_keeps_institutional_reserved_sources(self) -> None:
        registry = provider_registry()
        market_ids = {provider["id"] for provider in registry["market_data"]}
        information_ids = {provider["id"] for provider in registry["information"]}

        self.assertIn("polygon_market_data", market_ids)
        self.assertIn("intrinio_market_data", market_ids)
        self.assertIn("wind_terminal_data", market_ids)
        self.assertIn("choice_terminal_data", market_ids)
        self.assertIn("ifind_terminal_data", market_ids)
        self.assertIn("tushare_market_data", market_ids)
        self.assertIn("duckdb_local_market_store", market_ids)
        self.assertIn("postgres_market_store", market_ids)
        self.assertIn("alpha_vantage_market_data", market_ids)
        self.assertIn("fmp_market_data", market_ids)
        self.assertIn("yfinance_market_data", market_ids)
        self.assertIn("finnhub_news", information_ids)
        self.assertIn("fmp_news", information_ids)
        self.assertIn("chinese_finance_scraper", information_ids)
