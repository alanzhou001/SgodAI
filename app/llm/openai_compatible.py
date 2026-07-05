from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from app.llm.base import GroundedAIOutput, LLMProvider
from app.models import Event, PositionWindowState, Report


class OpenAICompatibleLLMProvider(LLMProvider):
    """OpenAI-compatible adapter for DeepSeek, Qwen, Moonshot, vLLM, LM Studio, etc."""

    def __init__(
        self,
        *,
        provider_id: str,
        base_url: str,
        model: str,
        api_key_env: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        self.provider_id = provider_id
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key_env = api_key_env
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def summarize_event(self, event: Event) -> GroundedAIOutput:
        return self._run_task("summarize_event", {"event": self._payload(event)}, [event.id], [event.id])

    def classify_event(self, event: Event) -> GroundedAIOutput:
        return self._run_task("classify_event", {"event": self._payload(event)}, [event.id], [event.id])

    def score_event(self, event: Event) -> GroundedAIOutput:
        return self._run_task("score_event", {"event": self._payload(event)}, [event.id], [event.id])

    def extract_entities(self, event: Event) -> GroundedAIOutput:
        return self._run_task("extract_entities", {"event": self._payload(event)}, [event.id], [event.id])

    def extract_risks(self, event: Event) -> GroundedAIOutput:
        return self._run_task("extract_risks", {"event": self._payload(event)}, [event.id], [event.id])

    def analyze_policy(self, event: Event) -> GroundedAIOutput:
        return self._run_task("analyze_policy", {"event": self._payload(event)}, [event.id], [event.id])

    def analyze_financial_report(self, event: Event) -> GroundedAIOutput:
        return self._run_task(
            "analyze_financial_report",
            {"event": self._payload(event)},
            [event.id],
            [event.id],
        )

    def generate_stock_brief(self, asset_id: str, events: list[Event]) -> GroundedAIOutput:
        return self._run_task(
            "generate_stock_brief",
            {"asset_id": asset_id, "events": [self._payload(event) for event in events]},
            [event.id for event in events],
            [event.id for event in events],
        )

    def generate_sector_brief(self, sector_id: str, events: list[Event]) -> GroundedAIOutput:
        return self._run_task(
            "generate_sector_brief",
            {"sector_id": sector_id, "events": [self._payload(event) for event in events]},
            [event.id for event in events],
            [event.id for event in events],
        )

    def generate_daily_report(self, report: Report) -> GroundedAIOutput:
        return self._run_task(
            "generate_daily_report",
            {"report": self._payload(report)},
            report.event_ids + report.signal_ids,
            report.event_ids,
        )

    def generate_weekly_report(self, report: Report) -> GroundedAIOutput:
        return self._run_task(
            "generate_weekly_report",
            {"report": self._payload(report)},
            report.event_ids + report.signal_ids,
            report.event_ids,
        )

    def explain_position_window(
        self,
        state: PositionWindowState,
        events: list[Event],
    ) -> GroundedAIOutput:
        return self._run_task(
            "explain_position_window",
            {
                "position_state": self._payload(state),
                "events": [self._payload(event) for event in events],
            },
            state.triggered_by_event_ids + state.triggered_by_signal_ids,
            [event.id for event in events],
        )

    def analyze_supply_chain_impact(self, event: Event) -> GroundedAIOutput:
        return self._run_task(
            "analyze_supply_chain_impact",
            {"event": self._payload(event)},
            [event.id],
            [event.id],
        )

    def deduplicate_semantic_events(self, events: list[Event]) -> GroundedAIOutput:
        return self._run_task(
            "deduplicate_semantic_events",
            {"events": [self._payload(event) for event in events]},
            [event.id for event in events],
            [event.id for event in events],
        )

    def run_structured_task(
        self,
        task: str,
        payload: dict[str, Any],
        *,
        evidence_refs: list[str] | None = None,
        input_event_ids: list[str] | None = None,
        required_output: dict[str, Any] | None = None,
    ) -> GroundedAIOutput:
        result = self._request_structured_result(
            task,
            payload,
            required_output=required_output,
        )
        return GroundedAIOutput(
            result=result,
            evidence_refs=evidence_refs or [],
            confidence=float(result.get("confidence", 0.5)),
            risk_notes=list(result.get("risk_notes", [])),
            input_event_ids=input_event_ids or [],
            provider=self.provider_id,
            model=self.model,
        )

    def _run_task(
        self,
        task: str,
        payload: dict[str, Any],
        evidence_refs: list[str],
        input_event_ids: list[str],
    ) -> GroundedAIOutput:
        result = self._request_structured_result(task, payload)
        return GroundedAIOutput(
            result=result,
            evidence_refs=evidence_refs,
            confidence=float(result.get("confidence", 0.5)),
            risk_notes=list(result.get("risk_notes", [])),
            input_event_ids=input_event_ids,
            provider=self.provider_id,
            model=self.model,
        )

    def _request_structured_result(
        self,
        task: str,
        payload: dict[str, Any],
        *,
        required_output: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        output_schema = required_output or {
            "summary": "string",
            "key_points": ["string"],
            "risks": ["string"],
            "confidence": 0.0,
            "risk_notes": ["string"],
            "disclaimer": "不构成投资建议，不提供确定性买卖指令。",
        }
        body = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是 SgodAI Market Radar 的投研辅助模型。只输出 JSON。"
                        "所有结论必须基于输入事件和证据字段，必须包含 confidence、risk_notes、"
                        "disclaimer。不得输出确定性买入/卖出指令，不得承诺收益。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "task": task,
                            "payload": payload,
                            "required_output": output_schema,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key()}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM provider {self.provider_id} HTTP {exc.code}: {detail}") from exc
        content = response_data["choices"][0]["message"]["content"]
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {"summary": content, "confidence": 0.4, "risk_notes": ["模型未返回严格 JSON。"]}
        parsed.setdefault("disclaimer", "不构成投资建议，不提供确定性买卖指令。")
        parsed.setdefault("risk_notes", [])
        parsed.setdefault("confidence", 0.5)
        return parsed

    def _api_key(self) -> str:
        key = self.api_key or (os.getenv(self.api_key_env) if self.api_key_env else None)
        if not key:
            env = self.api_key_env or "<direct api_key>"
            raise RuntimeError(f"Missing API key for {self.provider_id}; expected {env}.")
        return key

    @staticmethod
    def _payload(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.value
        if is_dataclass(value):
            return {
                key: OpenAICompatibleLLMProvider._payload(item)
                for key, item in asdict(value).items()
            }
        if isinstance(value, list):
            return [OpenAICompatibleLLMProvider._payload(item) for item in value]
        if isinstance(value, dict):
            return {
                str(key): OpenAICompatibleLLMProvider._payload(item)
                for key, item in value.items()
            }
        return value
