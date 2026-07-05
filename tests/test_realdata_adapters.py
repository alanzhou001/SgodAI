from datetime import datetime, timezone
from unittest import TestCase

from app.llm import OpenAICompatibleLLMProvider
from app.models import Event
from app.providers import RSSNewsProvider, RSSSource, normalize_market_ticker


class RealDataAdapterTest(TestCase):
    def test_ticker_normalization_for_a_h_markets(self) -> None:
        self.assertEqual(normalize_market_ticker("688525.SH"), ("A-share", "688525"))
        self.assertEqual(normalize_market_ticker("700.HK"), ("HK", "00700"))

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

    def test_openai_compatible_provider_wraps_structured_output(self) -> None:
        provider = OpenAICompatibleLLMProvider(
            provider_id="deepseek",
            base_url="https://api.deepseek.com/v1",
            model="deepseek-chat",
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
        self.assertEqual(output.model, "deepseek-chat")
        self.assertEqual(output.evidence_refs, ["evt_unit"])
        self.assertAlmostEqual(output.confidence, 0.81)
