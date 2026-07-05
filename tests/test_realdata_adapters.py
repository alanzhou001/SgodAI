from datetime import datetime, timezone
from unittest import TestCase

from app.llm import OpenAICompatibleLLMProvider
from app.models import Asset, Event
from app.providers import (
    PublicAssetSearchProvider,
    CninfoDisclosureProvider,
    CombinedDisclosureProvider,
    HKEXNewsDisclosureProvider,
    RSSNewsProvider,
    RSSSource,
    SinaAShareMarketDataProvider,
    a_share_exchange,
    hkex_query_terms,
    match_score,
    SinaFinanceNewsProvider,
    YahooChartMarketDataProvider,
    normalize_market_ticker,
)


class RealDataAdapterTest(TestCase):
    def test_ticker_normalization_for_a_h_markets(self) -> None:
        self.assertEqual(normalize_market_ticker("688525.SH"), ("A-share", "688525"))
        self.assertEqual(normalize_market_ticker("700.HK"), ("HK", "00700"))

    def test_yahoo_chart_provider_maps_hk_us_and_a_share_symbols(self) -> None:
        self.assertEqual(YahooChartMarketDataProvider.yahoo_symbol("700.HK"), "0700.HK")
        self.assertEqual(YahooChartMarketDataProvider.yahoo_symbol("NVDA.US"), "NVDA")
        self.assertEqual(YahooChartMarketDataProvider.yahoo_symbol("600519.SH"), "600519.SS")
        self.assertEqual(YahooChartMarketDataProvider.yahoo_symbol("300750.SZ"), "300750.SZ")

    def test_asset_search_maps_a_share_exchange_suffixes(self) -> None:
        self.assertEqual(a_share_exchange("688525"), "SH")
        self.assertEqual(a_share_exchange("300750"), "SZ")
        self.assertEqual(a_share_exchange("920001"), "BJ")

    def test_asset_search_builds_a_share_result_from_akshare_row(self) -> None:
        provider = PublicAssetSearchProvider()
        result = provider._a_share_row_to_result(  # type: ignore[attr-defined]
            "佰维",
            code="688525",
            name="佰维存储",
            raw={"code": "688525", "name": "佰维存储"},
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "688525.SH")
        self.assertEqual(result.market, "A-share")

    def test_asset_search_builds_hk_result_without_leading_zero(self) -> None:
        provider = PublicAssetSearchProvider()
        result = provider._hk_row_to_result(  # type: ignore[attr-defined]
            "腾讯",
            code="00700",
            name="腾讯控股",
            raw={"code": "00700", "name": "腾讯控股"},
            source="unit",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.ticker, "700.HK")
        self.assertEqual(result.market, "HK")

    def test_asset_search_score_prefers_exact_code(self) -> None:
        self.assertGreater(match_score("688525", "688525", "佰维存储"), 0.99)
        self.assertGreater(match_score("佰维", "688525", "佰维存储"), 0.7)

    def test_hkex_query_terms_expand_common_chinese_names(self) -> None:
        terms = hkex_query_terms("腾讯")

        self.assertIn("腾讯", terms)
        self.assertIn("TENCENT", terms)

    def test_rss_provider_parses_grounded_news_events(self) -> None:
        provider = RSSNewsProvider([RSSSource(name="unit", url="https://example.test/rss")])
        payload = """
        <rss><channel>
          <item>
            <title>半导体设备订单改善</title>
            <link>https://example.test/news/1</link>
            <description>行业景气出现改善迹象</description>
            <pubDate>Sun, 05 Jul 2026 09:00:00 GMT</pubDate>
          </item>
        </channel></rss>
        """.encode("utf-8")
        events = provider.parse_feed(
            provider.sources[0],
            payload,
            query="半导体",
            since=datetime(2026, 7, 5, tzinfo=timezone.utc),
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "news")
        self.assertEqual(events[0].source_url, "https://example.test/news/1")
        self.assertIn("rss_url", events[0].evidence)

    def test_rss_provider_records_source_errors_without_raising(self) -> None:
        provider = RSSNewsProvider(
            [RSSSource(name="bad", url="https://127.0.0.1:1/rss")],
            timeout_seconds=1,
        )

        events = provider.fetch_news("")

        self.assertEqual(events, [])
        self.assertEqual(provider.last_errors[0]["source"], "bad")

    def test_sina_finance_provider_parses_rollnews_payload(self) -> None:
        provider = SinaFinanceNewsProvider(lids=["2671"])
        payload = {
            "result": {
                "data": [
                    {
                        "title": "半导体板块午后走强",
                        "intro": "存储、设备方向活跃。",
                        "url": "http://finance.sina.com.cn/stock/test.shtml",
                        "intime": "1783267200",
                        "media_name": "新浪财经",
                    }
                ]
            }
        }

        events = provider.parse_payload(payload, lid="2671", query="半导体")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "news")
        self.assertEqual(events[0].source, "sina_finance_rollnews")
        self.assertEqual(events[0].source_url, "https://finance.sina.com.cn/stock/test.shtml")

    def test_sina_market_provider_parses_a_share_jsonp(self) -> None:
        provider = SinaAShareMarketDataProvider()
        payload = """
        /*<script>location.href='//sina.com';</script>*/
        var data=([
          {"day":"2026-07-01","open":"10.0","high":"11.0","low":"9.5","close":"10.5","volume":"100"},
          {"day":"2026-07-02","open":"10.5","high":"12.0","low":"10.2","close":"11.8","volume":"200"}
        ]);
        """

        rows = provider.parse_payload("600519.SH", payload)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["trade_date"], "2026-07-01")
        self.assertEqual(rows[1]["close"], 11.8)
        self.assertEqual(rows[1]["source"], "sina")

    def test_yahoo_chart_provider_parses_ohlcv_payload(self) -> None:
        payload = {
            "chart": {
                "result": [
                    {
                        "timestamp": [1783267200, 1783353600],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [100.0, 102.0],
                                    "high": [103.0, 105.0],
                                    "low": [99.0, 101.0],
                                    "close": [102.0, 104.0],
                                    "volume": [1000, 1200],
                                }
                            ]
                        },
                    }
                ],
                "error": None,
            }
        }

        rows = YahooChartMarketDataProvider.parse_payload("NVDA.US", payload)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["ticker"], "NVDA.US")
        self.assertEqual(rows[0]["trade_date"], "2026-07-05")
        self.assertEqual(rows[1]["close"], 104.0)
        self.assertEqual(rows[1]["source"], "yahoo_chart_market_data")

    def test_openai_compatible_provider_wraps_structured_output(self) -> None:
        provider = OpenAICompatibleLLMProvider(
            provider_id="deepseek",
            base_url="https://api.deepseek.com",
            model="deepseek-v4-flash",
            api_key="unit",
        )
        provider._request_structured_result = lambda task, payload: {  # type: ignore[method-assign]
            "summary": f"{task}:{payload['event']['title']}",
            "confidence": 0.81,
            "risk_notes": ["unit risk"],
        }
        event = Event(
            id="evt_unit",
            title="公告显示订单改善",
            event_type="announcement",
            source="unit",
        )

        output = provider.summarize_event(event)

        self.assertEqual(output.provider, "deepseek")
        self.assertEqual(output.model, "deepseek-v4-flash")
        self.assertEqual(output.evidence_refs, ["evt_unit"])
        self.assertAlmostEqual(output.confidence, 0.81)

    def test_cninfo_provider_parses_a_share_announcement_payload(self) -> None:
        asset = Asset(
            id="asset_688525_SH",
            ticker="688525.SH",
            name="佰维存储",
            market="A-share",
            asset_type="stock",
        )
        provider = CninfoDisclosureProvider()
        payload = {
            "announcements": [
                {
                    "announcementTitle": "<em>佰维存储</em>：2026年半年度报告",
                    "announcementTime": 1783267200000,
                    "announcementId": "1219999999",
                    "adjunctUrl": "finalpage/2026-07-05/1219999999.PDF",
                    "secCode": "688525",
                    "secName": "佰维存储",
                }
            ]
        }

        events = provider.parse_payload(
            asset,
            payload,
            event_type="financial_report",
            category="category_bndbg_szsh",
            report_kind="semiannual",
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "financial_report")
        self.assertEqual(events[0].asset_ids, ["asset_688525_SH"])
        self.assertIn("static.cninfo.com.cn", events[0].source_url or "")
        self.assertEqual(events[0].evidence["announcement_id"], "1219999999")

    def test_hkex_provider_parses_report_search_html(self) -> None:
        asset = Asset(
            id="asset_00700_HK",
            ticker="700.HK",
            name="腾讯控股",
            market="HK",
            asset_type="stock",
        )
        provider = HKEXNewsDisclosureProvider()
        html = """
        <table>
          <tr>
            <td>05/07/2026</td>
            <td><a href="/listedco/listconews/sehk/2026/0705/202607050001.pdf">
              ANNUAL REPORT 2026
            </a></td>
          </tr>
          <tr>
            <td>05/07/2026</td>
            <td><a href="/listedco/listconews/sehk/2026/0705/202607050002.pdf">
              CHANGE OF ADDRESS
            </a></td>
          </tr>
        </table>
        """

        events = provider.parse_search_html(
            asset,
            html,
            event_type="financial_report",
            keywords=provider.report_keywords,
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, "financial_report")
        self.assertEqual(events[0].asset_ids, ["asset_00700_HK"])
        self.assertIn("hkexnews.hk/listedco/listconews", events[0].source_url or "")

    def test_hkex_provider_parses_title_search_json_payload(self) -> None:
        asset = Asset(
            id="asset_00700_HK",
            ticker="700.HK",
            name="腾讯控股",
            market="HK",
            asset_type="stock",
        )
        provider = HKEXNewsDisclosureProvider()
        payload = {
            "result": """
            [{
              "NEWS_ID": "12232076",
              "LONG_TEXT": "ANNUAL REPORT 2026",
              "TITLE": "Annual Report",
              "DATE_TIME": "05/07/2026 17:49",
              "FILE_LINK": "/listedco/listconews/sehk/2026/0705/202607050001.pdf",
              "STOCK_CODE": "00700",
              "STOCK_NAME": "TENCENT"
            }]
            """
        }

        events = provider.parse_json_payload(
            asset,
            payload,
            event_type="financial_report",
            keywords=provider.report_keywords,
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].source, "hkexnews_disclosure")
        self.assertEqual(events[0].source_published_at.year, 2026)

    def test_combined_disclosure_provider_routes_a_and_h_assets(self) -> None:
        provider = CombinedDisclosureProvider()
        a_share = Asset(
            id="asset_a",
            ticker="688525.SH",
            name="佰维存储",
            market="A-share",
            asset_type="stock",
        )
        hk = Asset(
            id="asset_hk",
            ticker="700.HK",
            name="腾讯控股",
            market="HK",
            asset_type="stock",
        )

        a_share_assets, hk_assets = provider._split_assets([a_share, hk])

        self.assertEqual(a_share_assets, [a_share])
        self.assertEqual(hk_assets, [hk])
