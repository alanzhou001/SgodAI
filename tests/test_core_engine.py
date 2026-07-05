from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from app.db import SQLiteSignalStore
from app.models import Event, PositionState
from app.reports import ReportComposer
from app.scoring import ScoringEngine
from app.services import AssetIntelligenceService, ConfigAssistService, PositionWindowEngine


class FakeMarketProvider:
    provider_id = "fake_market"

    def fetch_ohlcv(self, ticker, since=None, until=None):  # noqa: ANN001
        return [
            {
                "ticker": ticker,
                "trade_date": "2026-07-01",
                "open": 10,
                "high": 11,
                "low": 9.8,
                "close": 10,
                "volume": 100,
            },
            {
                "ticker": ticker,
                "trade_date": "2026-07-05",
                "open": 11,
                "high": 13,
                "low": 10.8,
                "close": 12.5,
                "volume": 260,
            },
        ]


class EmptyNewsProvider:
    provider_id = "empty_news"

    def fetch_news(self, query, since=None, until=None):  # noqa: ANN001
        return []


class EmptyDisclosureProvider:
    provider_id = "empty_disclosure"

    def fetch_announcements(self, assets, since=None, until=None):  # noqa: ANN001
        return []

    def fetch_reports(self, assets, since=None, until=None):  # noqa: ANN001
        return []


class FakeLLMProvider:
    def run_structured_task(self, task, payload, **kwargs):  # noqa: ANN001
        from app.llm import GroundedAIOutput

        return GroundedAIOutput(
            result={
                "horizon": "long",
                "driver": "三电系统、智能化和补能网络共同驱动",
                "risks": "价格竞争；需求波动",
                "indicators": ["销量", "电池成本"],
                "upstream": ["锂电材料", "功率半导体"],
                "downstream": ["整车", "充电网络"],
                "related_assets": [{"name": "比亚迪", "ticker": "002594.SZ", "market": "A-share"}],
                "confidence": 0.8,
                "risk_notes": ["unit"],
                "disclaimer": "不构成投资建议，不提供确定性买卖指令。",
            },
            evidence_refs=["unit"],
            confidence=0.8,
            risk_notes=["unit"],
            provider="deepseek",
            model="unit",
        )


class FakeAssetSearchProvider:
    last_errors = []

    def search_assets(self, query, limit=20, markets=None):  # noqa: ANN001
        if query in {"比亚迪", "002594.SZ"}:
            return [
                {
                    "ticker": "002594.SZ",
                    "name": "比亚迪",
                    "market": "A-share",
                    "exchange": "SZ",
                    "source": "unit",
                    "score": 1.0,
                }
            ]
        return []


class CoreEngineTest(TestCase):
    def test_scoring_generates_traceable_signal(self) -> None:
        event = Event(
            id="evt_test",
            title="政策催化带动行业景气改善",
            event_type="policy",
            source="unit",
            asset_ids=["asset_001"],
            sector_ids=["sector_001"],
        )

        signal = ScoringEngine().score_event(event)

        self.assertEqual(signal.event_id, event.id)
        self.assertEqual(signal.asset_id, "asset_001")
        self.assertGreaterEqual(signal.impact_score, 57)
        self.assertEqual(signal.evidence["event_id"], "evt_test")

    def test_position_window_is_auditable(self) -> None:
        event = Event(
            id="evt_test_position",
            title="订单改善并出现政策催化",
            event_type="industry",
            source="unit",
            asset_ids=["asset_001"],
            sector_ids=["sector_001"],
        )
        signal = ScoringEngine().score_event(event)

        state = PositionWindowEngine().detect(
            asset_id="asset_001",
            signals=[signal],
            previous_state=PositionState.WATCH,
        )

        self.assertIn(signal.id, state.triggered_by_signal_ids)
        self.assertIn(event.id, state.triggered_by_event_ids)
        self.assertTrue(state.rule_version)
        self.assertIn("不构成投资建议", state.disclaimer)

    def test_report_is_grounded(self) -> None:
        event = Event(
            id="evt_report",
            title="海外映射公司资本开支上调",
            event_type="overseas",
            source="unit",
            asset_ids=["asset_002"],
            sector_ids=["sector_002"],
        )
        signal = ScoringEngine().score_event(event)
        state = PositionWindowEngine().detect("asset_002", [signal])
        now = datetime.now(timezone.utc)

        report = ReportComposer().compose_daily_report(
            events=[event],
            signals=[signal],
            position_states=[state],
            period_start=now,
            period_end=now,
        )

        self.assertTrue(report.grounded)
        self.assertEqual(report.event_ids, [event.id])
        self.assertEqual(report.signal_ids, [signal.id])

    def test_market_event_scoring_uses_real_price_evidence(self) -> None:
        event = Event(
            id="evt_market",
            title="测试标的区间价格上涨",
            event_type="market_data",
            source="unit_market",
            asset_ids=["asset_001"],
            evidence={
                "price_change_pct": 12.5,
                "volume_ratio": 2.4,
                "drawdown_pct": -1.5,
                "range_pct": 16.0,
            },
        )

        signal = ScoringEngine().score_event(event)

        self.assertGreater(signal.impact_score, 60)
        self.assertGreater(signal.trend_score, 60)
        self.assertEqual(signal.evidence["rule"], "rules.realdata.v1")

    def test_asset_intelligence_builds_event_signal_position_loop(self) -> None:
        from app.models import Asset

        service = AssetIntelligenceService(
            market_provider=FakeMarketProvider(),
            news_provider=EmptyNewsProvider(),
            disclosure_provider=EmptyDisclosureProvider(),
        )
        asset = Asset(
            id="asset_600519_SH",
            ticker="600519.SH",
            name="贵州茅台",
            market="A-share",
            asset_type="stock",
        )

        snapshot = service.build_asset_snapshot(asset, include_news=True, include_disclosures=True)

        self.assertEqual(snapshot["source_status"]["market_data"], "fake_market")
        self.assertEqual(len(snapshot["events"]), 1)
        self.assertEqual(len(snapshot["signals"]), 1)
        self.assertIn(snapshot["signals"][0].id, snapshot["position_state"].triggered_by_signal_ids)
        self.assertGreater(snapshot["scores"]["impact"], 50)

    def test_asset_intelligence_persists_traceable_outputs(self) -> None:
        from app.models import Asset

        with TemporaryDirectory() as tmpdir:
            store = SQLiteSignalStore(Path(tmpdir) / "signals.sqlite")
            service = AssetIntelligenceService(
                market_provider=FakeMarketProvider(),
                news_provider=EmptyNewsProvider(),
                disclosure_provider=EmptyDisclosureProvider(),
                signal_store=store,
            )
            asset = Asset(
                id="asset_600519_SH",
                ticker="600519.SH",
                name="贵州茅台",
                market="A-share",
                asset_type="stock",
            )

            snapshot = service.build_asset_snapshot(asset, include_news=True, include_disclosures=True)

            self.assertTrue(snapshot["persistence"]["enabled"])
            self.assertEqual(store.counts()["events"], 1)
            self.assertEqual(store.counts()["signals"], 1)
            self.assertEqual(store.counts()["position_window_states"], 1)
            self.assertEqual(store.recent_events()[0]["asset_ids"], ["asset_600519_SH"])

    def test_config_assist_validates_llm_candidate_assets(self) -> None:
        service = ConfigAssistService(
            llm_provider=FakeLLMProvider(),
            asset_search_provider=FakeAssetSearchProvider(),
        )

        result = service.assist_sector("新能源汽车")

        self.assertEqual(result["provider"], "deepseek")
        self.assertEqual(result["relatedTickers"], ["002594.SZ"])
        self.assertEqual(result["validatedAssets"][0]["name"], "比亚迪")
