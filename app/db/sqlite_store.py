from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

from app.models import Event, PositionWindowState, Signal
from app.settings import settings


class SQLiteSignalStore:
    """Durable local store for auditable market intelligence outputs."""

    def __init__(self, path: str | Path | None = None) -> None:
        configured = path or os.getenv("SGODAI_DB_PATH") or settings.database_path
        self.path = Path(configured)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_url TEXT,
                    source_published_at TEXT,
                    received_at TEXT,
                    raw_content_ref TEXT,
                    summary TEXT,
                    asset_ids_json TEXT NOT NULL,
                    sector_ids_json TEXT NOT NULL,
                    knowledge_node_ids_json TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    dedup_key TEXT,
                    confidence REAL NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS signals (
                    id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    asset_id TEXT,
                    sector_id TEXT,
                    impact_score INTEGER NOT NULL,
                    trend_score INTEGER NOT NULL,
                    sentiment_score INTEGER NOT NULL,
                    risk_score INTEGER NOT NULL,
                    scoring_version TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(event_id) REFERENCES events(id)
                );

                CREATE TABLE IF NOT EXISTS position_window_states (
                    id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    previous_state TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    support_factors_json TEXT NOT NULL,
                    risk_factors_json TEXT NOT NULL,
                    watch_variables_json TEXT NOT NULL,
                    triggered_by_event_ids_json TEXT NOT NULL,
                    triggered_by_signal_ids_json TEXT NOT NULL,
                    rule_version TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    disclaimer TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_signals_created_at ON signals(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_signals_event_id ON signals(event_id);
                CREATE INDEX IF NOT EXISTS idx_pws_asset_created ON position_window_states(asset_id, created_at DESC);
                """
            )

    def save_events(self, events: Iterable[Event]) -> int:
        rows = [
            (
                event.id,
                event.title,
                event.event_type,
                event.source,
                event.source_url,
                _dt(event.source_published_at),
                _dt(event.received_at),
                event.raw_content_ref,
                event.summary,
                _json(event.asset_ids),
                _json(event.sector_ids),
                _json(event.knowledge_node_ids),
                _json(event.evidence),
                event.dedup_key,
                event.confidence,
                _dt(event.created_at),
            )
            for event in events
        ]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO events (
                    id, title, event_type, source, source_url, source_published_at,
                    received_at, raw_content_ref, summary, asset_ids_json,
                    sector_ids_json, knowledge_node_ids_json, evidence_json,
                    dedup_key, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def save_signals(self, signals: Iterable[Signal]) -> int:
        rows = [
            (
                signal.id,
                signal.event_id,
                signal.asset_id,
                signal.sector_id,
                signal.impact_score,
                signal.trend_score,
                signal.sentiment_score,
                signal.risk_score,
                signal.scoring_version,
                _json(signal.evidence),
                _dt(signal.created_at),
            )
            for signal in signals
        ]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO signals (
                    id, event_id, asset_id, sector_id, impact_score, trend_score,
                    sentiment_score, risk_score, scoring_version, evidence_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def save_position_states(self, states: Iterable[PositionWindowState]) -> int:
        rows = [
            (
                state.id,
                state.asset_id,
                state.previous_state.value,
                state.current_state.value,
                _json(state.support_factors),
                _json(state.risk_factors),
                _json(state.watch_variables),
                _json(state.triggered_by_event_ids),
                _json(state.triggered_by_signal_ids),
                state.rule_version,
                state.confidence,
                state.disclaimer,
                _dt(state.created_at),
            )
            for state in states
        ]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT OR REPLACE INTO position_window_states (
                    id, asset_id, previous_state, current_state, support_factors_json,
                    risk_factors_json, watch_variables_json, triggered_by_event_ids_json,
                    triggered_by_signal_ids_json, rule_version, confidence, disclaimer, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
        return len(rows)

    def save_snapshot(
        self,
        events: Iterable[Event],
        signals: Iterable[Signal],
        position_states: Iterable[PositionWindowState],
    ) -> dict[str, int]:
        event_items = list(events)
        signal_items = list(signals)
        state_items = list(position_states)
        return {
            "events": self.save_events(event_items),
            "signals": self.save_signals(signal_items),
            "position_window_states": self.save_position_states(state_items),
        }

    def recent_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._recent("events", limit)

    def recent_signals(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._recent("signals", limit)

    def recent_position_states(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._recent("position_window_states", limit)

    def counts(self) -> dict[str, int]:
        with self._connect() as connection:
            return {
                table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("events", "signals", "position_window_states")
            }

    def _recent(self, table: str, limit: int) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [_decode_row(dict(row)) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _json(value: Any) -> str:
    return json.dumps(_plain(value), ensure_ascii=False, sort_keys=True)


def _plain(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return _plain(asdict(value))
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _decode_row(row: dict[str, Any]) -> dict[str, Any]:
    decoded: dict[str, Any] = {}
    for key, value in row.items():
        if key.endswith("_json"):
            decoded[key.removesuffix("_json")] = json.loads(value or "null")
        else:
            decoded[key] = value
    return decoded
