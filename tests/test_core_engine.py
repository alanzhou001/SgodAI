from datetime import datetime, timezone
from unittest import TestCase

from app.models import Event, PositionState
from app.reports import ReportComposer
from app.scoring import ScoringEngine
from app.services import PositionWindowEngine


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

